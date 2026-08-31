# SkillMCP (Skill Management System)

A containerized, horizontally scalable Model Context Protocol (MCP) server for distributing and managing AI agent skills.

## Overview & Motivation

AI agents rely on domain-specific skills (instructions, metadata, schemas, and reference assets) to perform complex engineering and analytical tasks. However, managing skills across diverse teams and agent fleets often introduces critical operational challenges:

- **Fragmented & Outdated Skills**: Skills stored across scattered individual repositories or copied manually quickly fall out of sync, leaving agents executing obsolete or incompatible workflows.
- **Distribution & Update Bottlenecks**: Distributing skill updates across distributed agent instances requires manual synchronization or fragile file-copy steps.
- **Lack of Versioning & Diagnostics Friction**: When skills are edited without immutable versioning, diagnosing regressions or agent behavior shifts becomes nearly impossible.
- **Single-Host Scalability Limits**: Traditional stdio-based MCP servers are tied to single local host processes, blocking horizontal scaling and high availability.

**SkillMCP** solves these challenges by providing a **centralized, containerized, and horizontally scalable Skill Management System** powered by **Stateless Streamable HTTP**.

---

## Key Capabilities & Features

### 1. Centralized & Versioned Skill Packaging
- **Immutable Container Releases**: Skills (`SKILL.md`, `references/`, and `examples/`) are packaged directly inside Docker images tagged with explicit semver (`v1.2.0`), ensuring 100% reproducible environments and auditability.
- **Unified Skill Repository**: Eliminates fragmented multi-repo drift by managing, validating, and bundling all domain skills in a single maintainable repository.
- **Fast Troubleshooting & Traceability**: Versioned container tags make it straightforward to diagnose agent issues, reproduce historical behavior, and roll back changes instantly.

### 2. Stateless MCP over Streamable HTTP (Horizontal Scalability & HPA Ready)
- **True Stateless Request/Response Architecture**: Streamable HTTP uses standard HTTP POST requests where backend instances do not maintain long-lived in-memory socket state between client calls.
- **Seamless Horizontal Pod Autoscaling (HPA)**: Without sticky sessions or persistent TCP stream locking, backend replicas can scale up/down dynamically and handle requests evenly across any load balancer.
- **Short-Lived Streaming**: Responses requiring streaming are upgraded to `text/event-stream` only for the duration of that specific payload and close immediately once the JSON-RPC response finishes.
- **Nginx Ingress Load Balancing**: Configured with `least_conn` routing, keepalive connection pooling, and dedicated `/healthz` health checks for zero-downtime rolling updates.

### 3. Developer & Agent Tooling
- **Built-in Skill Validator CLI**: `skillmcp validate ./skills` automatically verifies directory structures, YAML frontmatter, and asset links before packaging.
- **Dynamic Discovery & Search**: 
  - MCP Tools: `list_skills`, `get_skill`, `search_skills`, `read_skill_reference`, `read_skill_example`.
  - MCP Resources: `skill://{name}` for direct markdown document inspection.
- **Dual Compose Environments**: `docker-compose.local.yml` for instant local development with volume-mounted hot reloading, and `docker-compose.yml` for production deployments.
- **TREM Python Standard**: Built strictly following Testable, Readable, Extensible, and Maintainable (TREM) principles with `uv`, `pydantic-settings`, standard library `logging`, and `pytest`.
- **Automated CI/CD Publishing**: GitHub Actions pipeline that validates tests and pushes immutable semver releases to Docker Hub on version tags (`v*.*.*`).

---

## Quickstart

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- Docker & Docker Compose

### Local Installation

```bash
# Sync dependencies
uv sync

# Run tests
uv run pytest -v

# Validate skills
uv run skillmcp validate ./skills

# List discovered skills
uv run skillmcp list --skills-path ./skills
```

### Running the Server Locally

```bash
# Start MCP server directly (Streamable HTTP on port 8000)
uv run skillmcp serve --host 0.0.0.0 --port 8000
```

---

## Container Usage & Deployment

### 1. Run Standalone Docker Container

Pull and run the pre-built image directly from Docker Hub:

```bash
# Run standalone container with bundled skills
docker run -d \
  --name skillmcp \
  -p 8000:8000 \
  docker.io/clivechung/skillmcp:latest

# Or mount your own custom skills directory
docker run -d \
  --name skillmcp \
  -p 8000:8000 \
  -v $(pwd)/skills:/app/skills:ro \
  docker.io/clivechung/skillmcp:latest
```

Verify the server is running:
```bash
curl http://localhost:8000/healthz
# {"status":"healthy","service":"skillmcp","version":"0.1.0"}
```

---

### 2. Run with Docker Compose (Production Topology)

Runs 2 backend `skillmcp` replicas behind an Nginx load balancer:

```bash
docker compose up -d
```

- **MCP Endpoint**: `http://localhost:8080/mcp`
- **Ingress Health Check**: `http://localhost:8080/healthz`

---

### 3. Local Development (Live Reload & Volume Mounts)

```bash
docker compose -f docker-compose.local.yml up -d --build
```

- **Nginx Ingress**: `http://localhost:8080/mcp`
- **Backend App (Direct)**: `http://localhost:8000/mcp`

---

## Client Integration Guide

SkillMCP exposes a stateless Model Context Protocol (MCP) server over Streamable HTTP at `/mcp`. Configure your favorite AI coding assistant or agent CLI using the examples below.

### 1. Google Antigravity (AGY)

Add SkillMCP to your Antigravity configuration (either workspace-level `.agents/mcp_config.json` or global `~/.gemini/config/mcp_config.json`):

```json
{
  "mcpServers": {
    "skillmcp": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

> **Note**: If connecting directly to the standalone container without Nginx, use `http://localhost:8000/mcp`.

---

### 2. OpenAI Codex (Visio IDE)

For projects developed in Visio / VS Code IDE with OpenAI Codex, add the server to your project's `.vscode/mcp.json` or workspace settings:

```json
{
  "mcpServers": {
    "skillmcp": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

If your IDE environment or extension utilizes a stdio bridge for remote HTTP endpoints, configure `mcp-remote`:

```json
{
  "mcpServers": {
    "skillmcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8080/mcp"]
    }
  }
}
```

---

### 3. Claude CLI (Visio IDE & Terminal)

#### Direct Registration via Claude CLI:
In your Visio IDE integrated terminal or command line:
```bash
# Add the streamable HTTP MCP server to Claude CLI
claude mcp add --transport http skillmcp http://localhost:8080/mcp
```

#### Via Visio / Claude MCP Configuration (`~/.claude.json` or `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "skillmcp": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

Or using `mcp-remote` for stdio-only bridge clients:
```json
{
  "mcpServers": {
    "skillmcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:8080/mcp"]
    }
  }
}
```

---

### Available MCP Tools & Resources

Once connected, your agents will have immediate access to the following tools:

| Tool / Resource | Description |
|---|---|
| `list_skills` | List all discovered skills with metadata, descriptions, references, and examples. |
| `get_skill(name)` | Retrieve full markdown instructions and frontmatter for a specific skill. |
| `search_skills(query)` | Search available skills by keyword or domain phrase. |
| `read_skill_reference(name, ref_path)` | Read auxiliary reference documents bundled with a skill. |
| `read_skill_example(name, example_path)` | Read practical code and workflow examples for a skill. |
| `skill://{name}` *(Resource)* | Read the raw markdown skill file as an MCP resource. |

---

## Testing Seams

- **Seam 1: Domain Service**: `tests/test_domain_service.py` (Validates scanner, parser, traversal safety, and query engine)
- **Seam 2: MCP Protocol & Tools**: `tests/test_mcp_server.py` & `tests/test_mcp_http.py` (Validates FastMCP tools, resources, and ASGI transport routes)
- **Seam 3: CLI & Integration**: `tests/test_cli.py` (Validates CLI validator, list, and serve commands)

---

## License & Attribution

- **Core Project**: Released under the [MIT License](LICENSE) (c) 2026 clivechung.
- **Skills & Attributions**: Declarations, licenses, and provenance for all bundled server skills and agent development skills are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).


