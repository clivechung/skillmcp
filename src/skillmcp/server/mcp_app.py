"""FastMCP application and HTTP transport assembly for SkillMCP."""

import logging
from typing import Any
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount

from skillmcp import __version__
from skillmcp.config import Settings, get_settings
from skillmcp.domain.scanner import SkillScanner
from skillmcp.domain.service import SkillService
from skillmcp.server.tools import create_mcp_tools

logger = logging.getLogger(__name__)


def create_mcp_server(service: SkillService, name: str = "SkillMCP") -> FastMCP:
    """Create and configure FastMCP server with tools and resources.
    
    Args:
        service: The domain SkillService providing data access.
        name: The name of the MCP server.
        
    Returns:
        Configured FastMCP server instance.
    """
    mcp = FastMCP(name)
    tools = create_mcp_tools(service=service)

    @mcp.tool(name="list_skills", description="List all available skills with metadata, references, and examples.")
    async def list_skills() -> list[dict[str, Any]]:
        return await tools.list_skills()

    @mcp.tool(name="get_skill", description="Get full instructions and content for a specific skill.")
    async def get_skill(name: str) -> str:
        content = await tools.get_skill(name)
        if content is None:
            raise ValueError(f"Skill '{name}' not found.")
        return content

    @mcp.tool(name="search_skills", description="Search available skills by query keyword.")
    async def search_skills(query: str) -> list[dict[str, Any]]:
        return await tools.search_skills(query)

    @mcp.tool(name="read_skill_reference", description="Read a bundled reference document for a given skill.")
    async def read_skill_reference(name: str, ref_path: str) -> str:
        content = await tools.read_skill_reference(name, ref_path)
        if content is None:
            raise ValueError(f"Reference '{ref_path}' not found in skill '{name}'.")
        return content

    @mcp.tool(name="read_skill_example", description="Read a bundled example document for a given skill.")
    async def read_skill_example(name: str, example_path: str) -> str:
        content = await tools.read_skill_example(name, example_path)
        if content is None:
            raise ValueError(f"Example '{example_path}' not found in skill '{name}'.")
        return content

    @mcp.resource("skill://{name}", name="Skill Document", description="Full markdown document for a skill")
    async def skill_resource(name: str) -> str:
        skill = await service.get_skill(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found.")
        return skill.content

    return mcp


async def healthz_endpoint(request: Any) -> JSONResponse:
    """Health check endpoint for orchestrators and load balancers."""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "skillmcp",
            "version": __version__,
        }
    )


def create_app(service: SkillService | None = None, settings: Settings | None = None) -> Starlette:
    """Create ASGI HTTP/SSE application with health check and MCP transport."""
    if settings is None:
        settings = get_settings()

    if service is None:
        scanner = SkillScanner(skills_root=settings.skills_dir)
        service = SkillService(scanner=scanner)

    mcp_server = create_mcp_server(service=service, name=settings.app_name)
    app = mcp_server.http_app(transport=settings.transport)

    # If streamable-http transport is active, register route alias for /sse so clients pointing to /sse work seamlessly
    streamable_route = None
    for r in app.routes:
        if getattr(r, "path", None) == "/mcp":
            streamable_route = r
            break

    if streamable_route:
        app.routes.append(
            Route(
                "/sse",
                endpoint=streamable_route.endpoint,
                methods=["POST", "GET", "OPTIONS", "HEAD"],
            )
        )

    app.add_route("/healthz", healthz_endpoint, methods=["GET"])
    return app

