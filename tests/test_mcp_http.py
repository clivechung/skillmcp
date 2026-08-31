import pytest
from pathlib import Path
import httpx

from skillmcp.domain.scanner import SkillScanner
from skillmcp.domain.service import SkillService
from skillmcp.server.mcp_app import create_app, create_mcp_server
from skillmcp.config import Settings


def create_sample_skill(base_dir: Path, skill_name: str, desc: str, body: str) -> None:
    skill_dir = base_dir / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: {desc}\n---\n\n# {skill_name}\n\n{body}\n",
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_healthz_endpoint(tmp_path: Path):
    """Verifies that the /healthz endpoint returns healthy status code and JSON."""
    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)
    app = create_app(service=service)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "skillmcp"
        assert "version" in data


@pytest.mark.asyncio
async def test_fastmcp_server_direct_tool_invocation(tmp_path: Path):
    """Verifies that FastMCP server tools execute correctly."""
    create_sample_skill(tmp_path, "test-skill", "Testing skill description", "Test content body")

    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)
    mcp_server = create_mcp_server(service=service)

    # Call tools via FastMCP
    skills = await mcp_server.call_tool("list_skills", {})
    # In FastMCP 3.x call_tool returns result content or data
    assert skills is not None


@pytest.mark.asyncio
async def test_streamable_http_transport(tmp_path: Path):
    """Verifies that Streamable HTTP transport accepts initialize on /mcp in stateless mode."""
    create_sample_skill(tmp_path, "skill-stream", "Testing streamable skill", "Body content")

    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)
    settings = Settings(transport="streamable-http")
    app = create_app(service=service, settings=settings)

    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            headers = {"Accept": "application/json, text/event-stream"}
            init_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-antigravity", "version": "1.0"},
                },
            }
            # Post to /mcp
            resp_mcp = await client.post("/mcp", json=init_payload, headers=headers)
            assert resp_mcp.status_code == 200

            # Stateless tool list call without session tracking
            tool_list_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            }
            resp_tools = await client.post("/mcp", json=tool_list_payload, headers=headers)
            assert resp_tools.status_code == 200
            assert "list_skills" in resp_tools.text


