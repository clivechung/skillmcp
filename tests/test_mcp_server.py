import pytest
from pathlib import Path

# Seam 2: MCP Server Tools Interface Tests
# Tests public MCP tool contracts (list_skills, get_skill, search_skills)

def create_sample_skill(base_dir: Path, skill_name: str, desc: str, body: str) -> None:
    skill_dir = base_dir / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: {desc}\n---\n\n# {skill_name}\n\n{body}\n",
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_mcp_tool_list_skills(tmp_path: Path):
    """Verifies that the MCP list_skills tool returns formatted metadata for all loaded skills."""
    create_sample_skill(tmp_path, "skill-a", "First skill description", "Body of A")
    create_sample_skill(tmp_path, "skill-b", "Second skill description", "Body of B")

    from skillmcp.domain.scanner import SkillScanner
    from skillmcp.domain.service import SkillService
    from skillmcp.server.tools import create_mcp_tools

    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)
    tools = create_mcp_tools(service=service)

    result = await tools.list_skills()
    assert len(result) == 2
    names = [s["name"] for s in result]
    assert "skill-a" in names
    assert "skill-b" in names


@pytest.mark.asyncio
async def test_mcp_tool_get_skill_content(tmp_path: Path):
    """Verifies that the MCP get_skill tool retrieves full markdown instructions and references."""
    create_sample_skill(tmp_path, "code-analyzer", "Performs static analysis.", "## Steps\n1. Run linter")

    from skillmcp.domain.scanner import SkillScanner
    from skillmcp.domain.service import SkillService
    from skillmcp.server.tools import create_mcp_tools

    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)
    tools = create_mcp_tools(service=service)

    content = await tools.get_skill("code-analyzer")
    assert content is not None
    assert "Performs static analysis." in content
    assert "Run linter" in content
