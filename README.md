# SkillMCP (Skill Management System)

A containerized, horizontally scalable Model Context Protocol (MCP) server for distributing and managing AI agent skills.

## Overview & Motivation

AI agents rely on domain-specific skills (instructions, metadata, schemas, and reference assets) to perform complex engineering and analytical tasks. However, managing skills across diverse teams and agent fleets often introduces critical operational challenges:

- **Fragmented & Outdated Skills**: Skills stored across scattered individual repositories or copied manually quickly fall out of sync, leaving agents executing obsolete or incompatible workflows.
- **Distribution & Update Bottlenecks**: Distributing skill updates across distributed agent instances requires manual synchronization or fragile file-copy steps.
- **Lack of Versioning & Diagnostics Friction**: When skills are edited without immutable versioning, diagnosing regressions or agent behavior shifts becomes nearly impossible.
- **Single-Host Scalability Limits**: Traditional stdio-based MCP servers are tied to single local host processes, blocking horizontal scaling and high availability.

**SkillMCP** solves these challenges by providing a **centralized, containerized, and horizontally scalable Skill Management System** powered by **Stateless Streamable HTTP** (with backward-compatible SSE support).

---

## Key Capabilities & Features

### 1. Centralized & Versioned Skill Packaging
- **Immutable Container Releases**: Skills (`SKILL.md`, `references/`, and `examples/`) are packaged directly inside Docker images tagged with explicit semver (`v1.2.0`), ensuring 100% reproducible environments and auditability.
- **Unified Skill Repository**: Eliminates fragmented multi-repo drift by managing, validating, and bundling all domain skills in a single maintainable repository.
- **Fast Troubleshooting & Traceability**: Versioned container tags make it straightforward to diagnose agent issues, reproduce historical behavior, and roll back changes instantly.

### 2. Stateless MCP over Streamable HTTP (Horizontal Scalability)
- **True Stateless Request/Response Architecture**: Streamable HTTP uses standard HTTP POST requests where backend instances do not maintain long-lived in-memory socket state between client calls.
- **Session Decoupling & Horizontal Scaling**: Individual requests can be routed to any backend container replica behind an Nginx reverse proxy or load balancer without requiring sticky sessions.
- **Short-Lived Streaming**: Responses requiring streaming are upgraded to `text/event-stream` only for the duration of that specific payload and close immediately once the JSON-RPC response finishes.
- **Legacy SSE Compatibility**: Supports legacy Server-Sent Events (`/sse`) with configured proxy buffer bypass (`proxy_buffering off`) and extended read timeouts for clients requiring persistent channels.
- **Nginx Ingress Load Balancing**: Configured with `least_conn` routing, keepalive connection pooling, and dedicated `/healthz` health checks for zero-downtime rolling updates.

> [!WARNING]
> **Transport & Horizontal Scalability**:
> - **Streamable HTTP (`default`, recommended)**: Truly stateless. Allows horizontal auto-scaling and arbitrary load-balancing across replicas without session affinity.
> - **Native SSE (`SKILLMCP_TRANSPORT=sse`)**: Stateful due to persistent TCP stream binding. In native SSE mode, horizontal scaling behind standard round-robin/least-connections load balancers will cause `POST /messages` routing errors unless sticky sessions (e.g. Nginx `ip_hash` or cookie affinity) or a single-replica deployment is used.

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

- **Seam 1: Domain Service**: `tests/test_domain_service.py` (Validates scanner, parser, traversal safety, and query engine)
- **Seam 2: MCP Protocol & Tools**: `tests/test_mcp_server.py` & `tests/test_mcp_http.py` (Validates FastMCP tools, resources, and ASGI transport routes)
- **Seam 3: CLI & Integration**: `tests/test_cli.py` (Validates CLI validator, list, and serve commands)

---

## License & Attribution

- **Core Project**: Released under the [MIT License](LICENSE) (c) 2026 clivechung.
- **Skills & Attributions**: Declarations, licenses, and provenance for all bundled server skills and agent development skills are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

