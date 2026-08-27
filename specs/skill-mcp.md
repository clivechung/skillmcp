# Specification: Skill MCP (SkillMCP)

## 1. Problem Statement

AI agents require access to specialized, domain-specific skills (instructions, metadata, schemas, and supporting assets) to execute complex engineering and operational workflows. Currently, distributing and managing these skills across teams and agent instances is fragmented:
1. **Local Coupling**: Skills are frequently tied to local file trees or manually duplicated across heterogeneous environments.
2. **Single-Host Limitation**: Serving skills over standard stdio MCP interfaces restricts agents to local single-host processes, inhibiting horizontal scalability, central management, and high availability.
3. **Operational Overhead**: Teams lack a standardized containerized deployment pipeline with reverse proxy routing, local iteration workflows, health monitoring, and automated CI/CD container publishing.

---

## 2. Solution Overview

The **Skill Management System (`skillmcp`)** is a containerized, horizontally scalable Model Context Protocol (MCP) server that standardizes skill distribution, discovery, and execution for AI agents:
1. **Containerized Skill & Server Package**: Skill definitions (`SKILL.md`, `references/`, and `examples/`) and the FastMCP application are built and packaged into an optimized, secure container image.
2. **Horizontal Scalability (Stateless MCP over Streamable HTTP)**: Implements Streamable HTTP MCP transport where stateless backend replicas handle independent request/response cycles without sticky sessions or long-lived server-held sockets, alongside backward-compatible SSE support.
3. **Nginx Ingress Reverse Proxy**: Provides load balancing (`least_conn`), request routing, SSE stream buffer management (`proxy_buffering off`), and orchestrator health checks.
4. **Dual Compose Environments**:
   - `docker-compose.yml`: Production-ready multi-replica deployment pulling images from `docker.io`.
   - `docker-compose.local.yml`: Developer environment enabling source builds, volume-mounted hot reloading of skill files, and full stack ingress testing.
5. **Rich CLI Utility**: Embedded Typer/Rich CLI for running servers (`skillmcp serve`), validating skill directory structures (`skillmcp validate`), and inspecting available skills (`skillmcp list`).
6. **Automated CI/CD Pipeline**: GitHub Actions workflow executing automated testing and skill validation on pull requests and pushes, and building/pushing immutable semver release images to Docker Hub on version tag releases (`v*.*.*`).

---

## 3. User Stories

### AI Agent Experience
1. **Skill Discovery**: As an AI agent, I want to discover available skills through `list_skills` and `search_skills` MCP tools, so that I can dynamically identify relevant skills for my current task.
2. **Instruction Retrieval**: As an AI agent, I want to fetch full skill instructions (`SKILL.md`) and frontmatter metadata via `get_skill` or the `skill://{name}` MCP resource, so that I can follow prescribed domain workflows.
3. **Deep Reference Inspection**: As an AI agent, I want to read bundled reference documents (`read_skill_reference`) and examples (`read_skill_example`), so that I can access deeper technical specifications on demand without bloating the initial prompt.

### Developer Experience
4. **Local Iteration**: As a developer, I want a `docker-compose.local.yml` configuration with live volume mounts (`./skills:/app/skills:ro`), so that changes to skill documentation reflect immediately without container rebuilds.
5. **Skill Validation**: As a skill author, I want a CLI command (`skillmcp validate`) to verify YAML frontmatter, required metadata, markdown content, and asset integrity before publishing.
6. **CLI Inspection**: As a developer, I want to list available skills directly in the terminal (`skillmcp list`), so that I can quickly verify local skill discovery.

### DevOps & Platform Engineering
7. **Stateless Scalability**: As a platform engineer, I want stateless MCP application instances scaled horizontally behind Nginx, so that the service handles concurrent agent traffic seamlessly.
8. **Health Probing**: As a cluster orchestrator (Kubernetes/Compose), I want standardized `/healthz` endpoints on both Nginx and the MCP application, so that unhealthy instances are automatically detected and recycled.
9. **Automated Container Delivery**: As a release manager, I want automated CI/CD publishing to Docker Hub (`clivechung/skillmcp`) triggered exclusively on version tag releases (`v*.*.*`), so that production deployments receive stable, verified container builds.
10. **Code Quality & TREM Standards**: As an engineer, I want the codebase to adhere to TREM principles (Testable, Readable, Extensible, Maintainable) using `uv`, `pydantic-settings`, `typer`, `fastmcp`, and `pytest`.

---

## 4. Architecture & Component Design

```
                     +---------------------------------------+
                     |         AI Agent / MCP Client         |
                     +---------------------------------------+
                                         |
                                         | HTTP / SSE Stream
                                         v
                     +---------------------------------------+
                     |         Nginx Ingress (Port 80)       |
                     |   - Least-Conn Load Balancing         |
                     |   - Ingress Healthcheck (/healthz)    |
                     |   - SSE Buffering & Timeout Handling  |
                     +---------------------------------------+
                               /                   \
         Upstream Proxy (HTTP) /                     \ Upstream Proxy (HTTP)
                             v                       v
               +---------------------------+   +---------------------------+
               |  SkillMCP Replica 1       |   |  SkillMCP Replica 2       |
               |  (FastMCP / Starlette)    |   |  (FastMCP / Starlette)    |
               |  - /healthz               |   |  - /healthz               |
               |  - /mcp & /sse            |   |  - /mcp & /sse            |
               |  - Tools & Resources      |   |  - Tools & Resources      |
               +---------------------------+   +---------------------------+
                             |                               |
                             +---------------+---------------+
                                             |
                                             v
                             +-------------------------------+
                             |    Domain Layer (Filesystem)  |
                             |    - SkillScanner             |
                             |    - SkillService (Cache)     |
                             |    - SkillDocument & Models   |
                             +-------------------------------+
                                             |
                                             v
                             +-------------------------------+
                             |     Mounted Skills Root       |
                             |     ./skills/<skill_name>/    |
                             |       ├── SKILL.md            |
                             |       ├── references/         |
                             |       └── examples/           |
                             +-------------------------------+
```

### 4.1 Layer Responsibilities

1. **CLI Layer (`src/skillmcp/cli.py`)**:
   - Built with `typer` and `rich`.
   - Commands:
     - `skillmcp serve`: Starts ASGI server via `uvicorn` with configurable host, port, skills directory, and log level.
     - `skillmcp validate [path]`: Parses and checks skills for frontmatter errors, missing fields, and broken structure.
     - `skillmcp list [--skills-path]`: Displays tabular summary of discovered skills.

2. **Configuration Layer (`src/skillmcp/config.py`)**:
   - Powered by `pydantic-settings.BaseSettings` with `SKILLMCP_` environment prefix.
   - Settings:
     - `SKILLMCP_HOST` (default: `"0.0.0.0"`)
     - `SKILLMCP_PORT` (default: `8000`)
     - `SKILLMCP_SKILLS_DIR` (default: `Path("skills")`)
     - `SKILLMCP_LOG_LEVEL` (default: `"INFO"`)
     - `SKILLMCP_APP_NAME` (default: `"SkillMCP Server"`)
     - `SKILLMCP_TRANSPORT` (default: `"streamable-http"`)

3. **Domain Layer (`src/skillmcp/domain/`)**:
   - `models.py`:
     - `SkillMetadata`: Validated YAML frontmatter (`name`, `description`, `category`, `tags`, `extra`).
     - `SkillDocument`: Full skill representation including body, absolute filesystem path, references, and examples.
     - `SkillResource`: MCP resource definition (`uri`, `name`, `description`, `mime_type`).
   - `scanner.py`:
     - `SkillScanner`: Discovers skill directories containing `SKILL.md`, parses YAML frontmatter using `pyyaml`, and catalogs `references/` and `examples/` subdirectories.
   - `service.py`:
     - `SkillService`: Business logic layer managing caching, indexing, case-insensitive keyword search across content/metadata, and directory traversal-safe file readers for references and examples.

4. **Server & MCP Layer (`src/skillmcp/server/`)**:
   - `tools.py`: Encapsulates MCP tool invocations delegating to `SkillService`.
   - `mcp_app.py`:
     - Configures FastMCP instance with 5 tools and 1 resource template.
     - Wraps FastMCP HTTP ASGI app within Starlette.
     - Registers `/healthz` Starlette JSON endpoint.
     - Implements route aliasing: routes both `/mcp` and `/sse` to the streamable HTTP transport endpoint.

---

## 5. Skill Directory Specification

Every skill package residing within the configured `skills_dir` follows this directory convention:

```
skills/<skill_name>/
├── SKILL.md              # Required: Primary instruction document with YAML frontmatter
├── references/           # Optional: Deep architectural specs, API references, cheat-sheets
│   ├── api-spec.md
│   └── schema.json
└── examples/             # Optional: Concrete implementation examples and code snippets
    ├── sample_agent.py
    └── usage_flow.md
```

### `SKILL.md` Structure
```markdown
---
name: sample-skill
description: Comprehensive workflow for deploying cloud workloads.
category: cloud
tags:
  - aws
  - devops
  - deployment
---

# Sample Skill Title

Detailed instructions, steps, constraints, and guidelines for the AI agent...
```

---

## 6. MCP Protocol Interface Specification

### 6.1 MCP Tools

| Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- |
| `list_skills` | *(none)* | `list[dict]` | Returns a list of all available skills with name, description, category, tags, and lists of reference/example file names. |
| `get_skill` | `name: str` | `str` | Returns the complete markdown document of the requested skill, prefixed with its YAML frontmatter header. Raises error if not found. |
| `search_skills` | `query: str` | `list[dict]` | Searches across skill names, descriptions, tags, and full markdown body for the given query string (case-insensitive). |
| `read_skill_reference` | `name: str`<br>`ref_path: str` | `str` | Reads and returns the content of a specific reference document in the skill's `references/` directory. |
| `read_skill_example` | `name: str`<br>`example_path: str` | `str` | Reads and returns the content of a specific example document in the skill's `examples/` directory. |

### 6.2 MCP Resources

| URI Pattern | Name | MIME Type | Description |
| :--- | :--- | :--- | :--- |
| `skill://{name}` | Skill Document | `text/markdown` | Exposes the raw markdown instructions for the skill identified by `{name}`. |

### 6.3 HTTP Endpoints

| Path | Method | Purpose | Response |
| :--- | :--- | :--- | :--- |
| `/healthz` | `GET` | Application health monitoring | `{"status": "healthy", "service": "skillmcp", "version": "0.1.0"}` |
| `/mcp` | `GET`, `POST` | Primary FastMCP streamable-http endpoint | MCP transport stream / message exchange |
| `/sse` | `GET`, `POST` | Backward-compatible SSE route alias | Proxied to MCP transport endpoint |

### 6.4 Transport Modes & Scalability Implications

> [!WARNING]
> **Transport Selection & Load Balancing Constraints**:
> - **Streamable HTTP (`SKILLMCP_TRANSPORT=streamable-http`, Default)**: Each JSON-RPC invocation is a discrete HTTP POST request. Backend instances hold no persistent socket session state between client requests, enabling full horizontal auto-scaling and stateless load balancing across arbitrary replicas without session affinity.
> - **Native SSE (`SKILLMCP_TRANSPORT=sse`)**: Stateful transport. The initial `GET /sse` handshake opens a long-lived persistent TCP connection held in server memory on that specific replica instance. Subsequent `POST /messages/?session_id=...` calls routed by a round-robin or least-conn load balancer to a different replica will fail with 404/session mismatch errors. Deploying in Native SSE mode requires either a single replica or sticky session ingress routing (e.g. Nginx `ip_hash` or cookie affinity).

---

## 7. Containerization & Deployment

### 7.1 Multi-Stage Dockerfile (`Dockerfile`)
- **Stage 1 (Builder)**: Uses `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` to compile bytecode and synchronize dependencies (`uv sync --frozen --no-dev`) into `/app/.venv`.
- **Stage 2 (Runtime)**:
  - Base: `python:3.12-slim-bookworm`.
  - Non-root user: `skillmcp:skillmcp` (UID/GID `10001`).
  - Default environment: `SKILLMCP_HOST=0.0.0.0`, `SKILLMCP_PORT=8000`, `SKILLMCP_SKILLS_DIR=/app/skills`.
  - Health check: Polls `http://127.0.0.1:8000/healthz` using Python standard library `urllib.request`.
  - Entrypoint: `CMD ["skillmcp", "serve"]`.

### 7.2 Nginx Ingress Configuration (`nginx/nginx.conf`)
- **Upstream Pool**: `upstream skillmcp_backend` utilizing `least_conn` and `keepalive 32`.
- **Ingress Healthcheck**: Dedicated `/healthz` endpoint returning `{"status":"healthy","ingress":"nginx"}`.
- **Streaming Optimizations**:
  - `proxy_buffering off;` & `proxy_cache off;` (preserves real-time SSE chunk delivery).
  - `chunked_transfer_encoding off;`
  - `proxy_read_timeout 3600s;` & `proxy_send_timeout 3600s;` (prevents premature closure of long-lived MCP agent sessions).

### 7.3 Production Topology (`docker-compose.yml`)
- Services:
  - `nginx`: Ingress mapping `8080:80`.
  - `skillmcp-app`: Multi-replica service (`replicas: 2`) pulling `docker.io/clivechung/skillmcp:latest`.

### 7.4 Local Development Topology (`docker-compose.local.yml`)
- Services:
  - `nginx`: Ingress mapping `8080:80`.
  - `skillmcp-app`: Builds locally from `Dockerfile`, mounts `./skills:/app/skills:ro` and `./src:/app/src:ro`, debug logging enabled.

---

## 8. CI/CD GitHub Actions Workflow

File: `.github/workflows/docker-publish.yml`

```
 [Trigger: push to main, PRs, tags v*.*.*]
                        |
                        v
        +-------------------------------+
        |  Job: test                    |
        |  1. Install uv & Python 3.12  |
        |  2. uv sync --frozen          |
        |  3. uv run pytest -v          |
        |  4. uv run skillmcp validate  |
        +-------------------------------+
                        |
                        v (if tag release v*.*.* & test passed)
        +-------------------------------+
        |  Job: build-and-push (Release)|
        |  1. Docker Buildx setup       |
        |  2. Docker Hub Login          |
        |  3. Semver Metadata & Tagging |
        |     - {{version}} (e.g. 0.1.0)|
        |     - {{major}}.{{minor}}     |
        |     - latest                  |
        |  4. Build & Push via GHA cache|
        +-------------------------------+
```

### Required GitHub Secrets
- `DOCKERHUB_USERNAME`: Docker Hub user identifier.
- `DOCKERHUB_TOKEN`: Personal Access Token with Read & Write scope.

---

## 9. Testing Decisions & Seams

The test architecture avoids brittle end-to-end couplings by exercising four explicit testing seams:

1. **Seam 1: Domain Service & Scanner (`tests/test_domain_service.py`)**
   - Direct unit testing of `SkillScanner` and `SkillService`.
   - Verifies YAML parsing, missing metadata rejection, caching mechanisms, keyword search relevance, directory traversal protection, and reference/example readers against mock filesystems.
2. **Seam 2: MCP Server & Tool Bindings (`tests/test_mcp_server.py`)**
   - Verifies tool registrations (`list_skills`, `get_skill`, `search_skills`, `read_skill_reference`, `read_skill_example`) and resource decorators on the FastMCP instance.
3. **Seam 3: HTTP Transport, Routing & Ingress (`tests/test_mcp_http.py`)**
   - Exercises the Starlette ASGI application via `httpx.AsyncClient`.
   - Tests `/healthz` JSON contract, `/sse` and `/mcp` route resolution, and simulated proxy headers.
4. **Seam 4: CLI Interface (`tests/test_cli.py`)**
   - Tests `skillmcp validate`, `skillmcp list`, and `skillmcp serve` CLI commands using Typer's `CliRunner`.

---

## 10. Out of Scope

- Dynamic remote skill modification/mutations via MCP (skills remain filesystem/git-backed and immutable during runtime).
- Distributed database persistence layers (in-memory caching over filesystem is optimal for sub-second latency and zero external dependencies).
- User authentication / API gateway tokens (handled upstream at the API gateway / perimeter ingress).
