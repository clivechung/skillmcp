# SkillMCP (Skill Management System)

A containerized, horizontally scalable Model Context Protocol (MCP) server for distributing and managing AI agent skills.

## Overview & Motivation

AI agents rely on domain-specific skills (instructions, metadata, schemas, and reference assets) to perform complex engineering and analytical tasks. However, managing skills across diverse teams and agent fleets often introduces critical operational challenges:

- **Fragmented & Outdated Skills**: Skills stored across scattered individual repositories or copied manually quickly fall out of sync, leaving agents executing obsolete or incompatible workflows.
- **Distribution & Update Bottlenecks**: Distributing skill updates across distributed agent instances requires manual synchronization or fragile file-copy steps.
- **Lack of Versioning & Diagnostics Friction**: When skills are edited without immutable versioning, diagnosing regressions or agent behavior shifts becomes nearly impossible.
- **Single-Host Scalability Limits**: Traditional stdio-based MCP servers are tied to single local host processes, blocking horizontal scaling and high availability.

**SkillMCP** solves these challenges by providing a **centralized, containerized, and horizontally scalable Skill Management System** powered by stateless **MCP over Streamable HTTP and SSE**.

---

## Key Capabilities & Features

### 1. Centralized & Versioned Skill Packaging
- **Immutable Container Releases**: Skills (`SKILL.md`, references, and examples) are packaged directly inside Docker images tagged with explicit semver (`v1.2.0`) or snapshot commit SHAs (`:snapshot-sha`), ensuring 100% reproducible environments and auditability.
- **Unified Skill Repository**: Eliminates fragmented multi-repo drift by managing, validating, and bundling all domain skills in a single maintainable repository.
- **Fast Troubleshooting & Traceability**: Versioned container tags make it straightforward to diagnose agent issues, reproduce historical behavior, and roll back changes instantly.

### 2. Stateless MCP over Streamable HTTP/SSE (Horizontal Scalability)
- **Stateless MCP Architecture**: By using stateless HTTP/SSE transport, backend instances don't rely on local stdio pipes or sticky process sessions.
- **Horizontal Auto-Scaling**: Multiple backend application replicas can run concurrently behind reverse proxies and load balancers to absorb traffic spikes without state divergence.
- **Nginx Ingress Load Balancing**: Configured with `least_conn` routing, stream buffer management (`proxy_buffering off`), and dedicated `/healthz` health checks for zero-downtime rolling updates.

### 3. Developer & Agent Tooling
- **Built-in Skill Validator CLI**: `skill-mcp validate ./skills` automatically verifies directory structures, YAML frontmatter, and asset links before packaging.
- **Dynamic Discovery & Search**: MCP tools (`list_skills`, `get_skill`, `search_skills`, `read_skill_reference`) and resources (`skill://{name}`) allow agents to dynamically query and inspect skills at runtime.
- **Dual Compose Environments**: `docker-compose.local.yml` for instant local development with volume-mounted hot reloading, and `docker-compose.yml` for production deployments.
- **TREM Python Standard**: Built strictly following Testable, Readable, Extensible, and Maintainable (TREM) principles with `uv`, `pydantic-settings`, standard library `logging`, and `pytest`.
- **Automated CI/CD Publishing**: Automated GitHub Actions pipeline building snapshot images on branch pushes and immutable semver releases on git tags.

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
uv run skill-mcp validate ./skills

# List discovered skills
uv run skill-mcp list --skills-path ./skills
```

### Running the Server Locally

```bash
# Start MCP server directly
uv run skill-mcp serve --host 0.0.0.0 --port 8000
```

---

## Docker Topologies

### Local Development (Live Reload & Ingress)

```bash
docker compose -f docker-compose.local.yml up -d --build
```
- Nginx Ingress: `http://localhost:8080` (`/healthz` health check)
- Backend App: `http://localhost:8000` (`/healthz` health check)

### Production Deployment

```bash
docker compose up -d
```

---

## Testing Seams

- **Seam 1: Domain Service**: `tests/test_domain_service.py` (Validates scanner, parser, and query engine)
- **Seam 2: MCP Protocol & Tools**: `tests/test_mcp_server.py` & `tests/test_mcp_http.py` (Validates MCP tool execution and HTTP/SSE transport)
- **Seam 3: CLI & Integration**: `tests/test_cli.py` (Validates CLI validator and commands)
