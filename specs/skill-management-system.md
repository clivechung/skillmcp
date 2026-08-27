# Specification: Skill Management System (SkillMCP)

## Problem Statement

AI agents require access to specialized, domain-specific skills (instructions, metadata, schemas, and supporting assets) to execute complex workflows. Currently, distributing and managing these skills across teams and agent instances is fragmented:
1. Skills are often tightly coupled to local file trees or manually copied across environments.
2. Serving skills over standard stdio MCP interfaces restricts agents to local single-host processes and prevents horizontal scaling and high availability.
3. Teams lack a standardized containerized deployment pipeline with reverse proxy routing, local iteration workflows, and automated CI/CD container publishing.

## Solution

The **Skill Management System (`skillmcp`)** provides a containerized, horizontally scalable Model Context Protocol (MCP) server that bundles skill management and distribution:
1. **Containerized Skill & Server Package**: Skill definitions (`SKILL.md`, references, and examples) and the FastMCP application are built and packaged into a single container image.
2. **Horizontal Scalability (MCP over Streamable HTTP/SSE)**: Implements Streamable HTTP/SSE MCP transport so multiple stateless backend replicas can run concurrently behind a load balancer.
3. **Nginx Ingress**: Provides reverse proxying, request routing, header buffer management for SSE streaming, and load balancing across backend instances.
4. **Dual Compose Environments**:
   - `docker-compose.yml`: Production-ready deployment pulling versioned images from `docker.io`.
   - `docker-compose.local.yml`: Developer environment enabling local image builds, volume-mounted hot reloading of skill files, and full stack ingress testing.
5. **Automated CI/CD Pipeline**: GitHub Actions workflow supporting dual-channel publishing: snapshot images on development branch pushes and immutable semver releases on tag releases.

---

## User Stories

1. As an AI agent, I want to discover available skills through an MCP tools/resources endpoint over HTTP, so that I can dynamically identify relevant skills for my current task.
2. As an AI agent, I want to fetch full skill instructions (`SKILL.md`) and frontmatter metadata via an MCP resource read, so that I can follow prescribed domain workflows.
3. As an AI agent, I want to read skill reference documents and examples via MCP tools or resource links, so that I can access deeper technical specifications on demand.
4. As an MCP client, I want to connect to the skill server using standard HTTP/SSE transport, so that my connection does not require a local stdio subprocess.
5. As a DevOps engineer, I want the MCP server instances to be stateless, so that I can scale them horizontally behind an Nginx reverse proxy to handle traffic spikes.
6. As a DevOps engineer, I want Nginx to act as an ingress controller, so that client traffic is load-balanced and SSE stream buffers are properly managed.
7. As a DevOps engineer, I want health check endpoints on both Nginx (`/healthz`) and the MCP application, so that container orchestrators can detect and replace unhealthy instances.
8. As a developer, I want a `docker-compose.local.yml` file that builds the image from source, so that I can test my changes locally before pushing code.
9. As a developer, I want to mount local `./skills` directories into the local development container, so that skill content changes reflect immediately without image rebuilds.
10. As a developer, I want a CLI command or automated script to validate skill structure and YAML frontmatter, so that malformed skills are caught before packaging.
11. As a CI/CD system, I want to automatically build a snapshot Docker image on push to `main`, so that the latest development build is immediately testable.
12. As a CI/CD system, I want to tag snapshot images with `:snapshot` and the commit SHA, so that builds are traceable.
13. As a CI/CD system, I want to build and push release images when a version tag (`v*.*.*`) is created, so that production deployments receive stable, immutable versions.
14. As a release manager, I want images published to `docker.io` (Docker Hub) using secure GitHub Action secrets, so that public or authorized consumers can pull the container.
15. As a software engineer, I want the codebase to strictly adhere to TREM Python standards (`uv`, `pydantic-settings`, `logging`, `pytest`), so that the system is testable, readable, extensible, and maintainable.

---

## Implementation Decisions

### 1. Architecture & Layering
- **Domain Layer (`src/skillmcp/domain/`)**:
  - `models.py`: Pydantic models for `SkillMetadata`, `SkillDocument`, `SkillResource`.
  - `scanner.py` & `service.py`: Skill repository scanning filesystem directories, parsing YAML frontmatter, and extracting markdown sections.
- **Server / MCP Layer (`src/skillmcp/server/`)**:
  - `mcp_app.py`: FastMCP server exposing tools (`list_skills`, `get_skill`, `read_skill_reference`, `search_skills`) and resources (`skill://{name}`).
  - `http_transport.py`: ASGI/HTTP SSE transport runner allowing stateless request-response scaling.
- **Configuration & Infrastructure (`src/skillmcp/config.py`)**:
  - `Settings`: Pydantic `BaseSettings` reading `SKILLMCP_HOST`, `SKILLMCP_PORT`, `SKILLMCP_SKILLS_DIR`, `SKILLMCP_LOG_LEVEL`.
  - Standard library `logging` configured across all modules.

### 2. Packaging & Containerization
- **Multi-Stage Dockerfile (`Dockerfile`)**:
  - Build stage: Uses `ghcr.io/astral-sh/uv` to install dependencies into a virtual environment with `--frozen`.
  - Runtime stage: Minimal Python 3.11/3.12 slim image copying only the venv, application code, and default packaged `skills/` directory.
  - Non-root user execution for security hardening.
- **Ingress (`nginx/nginx.conf`)**:
  - Configures `upstream skillmcp_backend` load-balancing multiple app containers.
  - Configures `proxy_buffering off`, `proxy_cache off`, and `proxy_read_timeout 3600s` for uninterrupted HTTP/SSE MCP streams.

### 3. Docker Compose Topologies
- **Production Topology (`docker-compose.yml`)**:
  - Services: `nginx` (port `8080:80`) and `skillmcp-app` (scalable via `deploy.replicas` or compose replicas).
  - Uses published image `docker.io/<repo>/skillmcp:latest`.
- **Local Development Topology (`docker-compose.local.yml`)**:
  - Services: `nginx` (port `8080:80`) and `skillmcp-app` (`build: .`).
  - Volume mount: `./skills:/app/skills:ro` and `./src:/app/src:ro`.
  - Environment variable overrides for live reload and debug logging.

### 4. CI/CD GitHub Actions (`.github/workflows/docker-publish.yml`)
- Workflow triggered on `push` to `main` / `develop` and on tags matching `v*.*.*`.
- Uses `docker/setup-buildx-action` and `docker/login-action`.
- Automatically computes tags via `docker/metadata-action`:
  - Branch push → `type=raw,value=snapshot`, `type=sha,prefix=sha-`
  - Release tag → `type=semver,pattern={{version}}`, `type=raw,value=latest`

---

## Testing Decisions & Seams

### The Seams Under Test
To prevent brittle, implementation-coupled tests, we establish three explicit testing seams:

1. **Seam 1: Domain Skill Service (`SkillService` public API)**
   - **Interface**: `list_skills()`, `get_skill(name)`, `search_skills(query)`.
   - **Verification**: Injects file storage protocols or virtual temporary directories with sample skill files; verifies extracted frontmatter, markdown sections, and missing skill error handling without starting HTTP servers.
2. **Seam 2: MCP Protocol & HTTP SSE Endpoint (`TestClient` / `AsyncClient`)**
   - **Interface**: MCP protocol tool call requests and resource queries over HTTP transport (`/sse`, `/messages`, `/healthz`).
   - **Verification**: Verifies that MCP tool invocations return compliant tool responses, correct schemas, and appropriate HTTP status codes.
3. **Seam 3: Docker & Ingress Integration Seam**
   - **Interface**: Nginx configuration validation (`nginx -t`) and compose health check endpoints.
   - **Verification**: Ensures Nginx proxies requests to backend upstreams, handles SSE headers properly, and passes health checks.

### Testing Principles
- Only test external behavior through the pre-agreed seams.
- No tautological assertions; test inputs map to known fixture outputs.
- Test suites run via `uv run pytest` with `pytest-asyncio`.

---

## Out of Scope
- Dynamic skill authoring/editing via the MCP API (skills are packaged and treated as immutable or mounted files in this phase).
- User authentication / OAuth2 integration (can be added as an API gateway layer in future revisions).
- Distributed database persistence (skills are filesystem/git-backed within the image).

---

## Further Notes
- Skill format follows the standard `SKILL.md` specification (YAML frontmatter + markdown body).
- The system is architected for zero-downtime rolling updates when deployed to container orchestrators (Kubernetes, Docker Swarm, AWS ECS).
