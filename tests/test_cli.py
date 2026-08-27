import pytest
from pathlib import Path
from typer.testing import CliRunner

from skillmcp.cli import app

runner = CliRunner()


def create_sample_skill(base_dir: Path, skill_name: str, desc: str, body: str) -> Path:
    skill_dir = base_dir / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: {desc}\n---\n\n# {skill_name}\n\n{body}\n",
        encoding="utf-8",
    )
    return skill_dir


def test_cli_validate_success(tmp_path: Path):
    """Verifies that skillmcp validate succeeds on valid skill directories."""
    create_sample_skill(tmp_path, "skill-one", "Valid skill 1", "Instructions for skill 1")
    create_sample_skill(tmp_path, "skill-two", "Valid skill 2", "Instructions for skill 2")

    result = runner.invoke(app, ["validate", str(tmp_path)])
    assert result.exit_code == 0
    assert "Validation passed" in result.output


def test_cli_validate_failure_on_invalid_frontmatter(tmp_path: Path):
    """Verifies that skillmcp validate flags malformed frontmatter."""
    invalid_dir = tmp_path / "broken-skill"
    invalid_dir.mkdir()
    (invalid_dir / "SKILL.md").write_text("No frontmatter here\nJust text", encoding="utf-8")

    result = runner.invoke(app, ["validate", str(tmp_path)])
    assert result.exit_code == 1
    assert "INVALID" in result.output


def test_cli_list_command(tmp_path: Path):
    """Verifies that skillmcp list displays table of discovered skills."""
    create_sample_skill(tmp_path, "code-bot", "AI coding helper", "Code instructions")

    result = runner.invoke(app, ["list", "--skills-path", str(tmp_path)])
    assert result.exit_code == 0
    assert "code-bot" in result.output
