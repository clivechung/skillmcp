import pytest
from pathlib import Path
from typing import Any

# Seam 1: Domain Skill Service Tests
# Tests public behavior of scanning, parsing, and retrieving skills from disk.

def create_sample_skill(base_dir: Path, skill_name: str, name_in_meta: str, desc: str, body: str) -> Path:
    """Helper fixture to create a valid skill directory structure."""
    skill_dir = base_dir / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file = skill_dir / "SKILL.md"
    content = f"""---
name: {name_in_meta}
description: {desc}
---

# {name_in_meta.title()}

{body}
"""
    skill_file.write_text(content, encoding="utf-8")
    return skill_dir


@pytest.mark.asyncio
async def test_scanner_loads_valid_skills(tmp_path: Path):
    """Verifies that the skill scanner discovers and parses valid skill definitions."""
    # Arrange: Create two sample skills in temporary directory
    create_sample_skill(
        base_dir=tmp_path,
        skill_name="code-reviewer",
        name_in_meta="code-reviewer",
        desc="Reviews code against quality standards.",
        body="## Workflows\n1. Analyze AST\n2. Report findings.",
    )
    create_sample_skill(
        base_dir=tmp_path,
        skill_name="tdd-guide",
        name_in_meta="tdd-guide",
        desc="Guides red-green-refactor loop.",
        body="## Rules\n1. Red before green.",
    )

    # Import from domain package (Red phase: module to be implemented)
    from skill_mcp.domain.scanner import SkillScanner

    # Act
    scanner = SkillScanner(skills_root=tmp_path)
    skills = await scanner.scan_all()

    # Assert
    assert len(skills) == 2
    skill_names = {s.name for s in skills}
    assert skill_names == {"code-reviewer", "tdd-guide"}
    
    reviewer = next(s for s in skills if s.name == "code-reviewer")
    assert reviewer.description == "Reviews code against quality standards."
    assert "Analyze AST" in reviewer.content


@pytest.mark.asyncio
async def test_get_skill_by_name(tmp_path: Path):
    """Verifies that a specific skill can be retrieved by name."""
    create_sample_skill(
        base_dir=tmp_path,
        skill_name="python-dev",
        name_in_meta="python-dev",
        desc="Python developer assistant.",
        body="Useful for Python coding.",
    )

    from skill_mcp.domain.service import SkillService
    from skill_mcp.domain.scanner import SkillScanner

    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)

    skill = await service.get_skill("python-dev")
    assert skill is not None
    assert skill.name == "python-dev"
    assert skill.description == "Python developer assistant."


@pytest.mark.asyncio
async def test_get_nonexistent_skill_returns_none(tmp_path: Path):
    """Verifies that querying a missing skill returns None or raises domain error."""
    from skill_mcp.domain.service import SkillService
    from skill_mcp.domain.scanner import SkillScanner

    scanner = SkillScanner(skills_root=tmp_path)
    service = SkillService(scanner=scanner)

    skill = await service.get_skill("non-existent-skill")
    assert skill is None
