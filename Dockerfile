# ==========================================
# Stage 1: Build virtual environment with uv
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first (layer caching)
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy source code and install project package
COPY src ./src
RUN uv sync --frozen --no-dev

# ==========================================
# Stage 2: Minimal runtime image
# ==========================================
FROM python:3.12-slim-bookworm AS runtime

# Security hardening: create non-root user
RUN groupadd -r -g 10001 skillmcp && \
    useradd -r -u 10001 -g skillmcp -d /app -s /sbin/nologin skillmcp

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=skillmcp:skillmcp /app/.venv /app/.venv

# Copy source code and default skills
COPY --chown=skillmcp:skillmcp src ./src
COPY --chown=skillmcp:skillmcp skills ./skills

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    SKILL_MCP_HOST="0.0.0.0" \
    SKILL_MCP_PORT=8000 \
    SKILL_MCP_SKILLS_DIR="/app/skills"

# Switch to non-root user
USER skillmcp

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz')" || exit 1

CMD ["skill-mcp", "serve"]
