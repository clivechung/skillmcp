"""Filesystem scanner and parser for skill packages."""

import logging
from pathlib import Path
from typing import Any
import yaml

from skill_mcp.domain.models import SkillDocument

logger = logging.getLogger(__name__)


class SkillScanner:
    """Discovers and parses skill directories containing SKILL.md."""

    def __init__(self, skills_root: Path) -> None:
        self.skills_root = Path(skills_root)

    async def scan_all(self) -> list[SkillDocument]:
        """Scan skills_root and return all discovered and valid SkillDocuments."""
        skills: list[SkillDocument] = []
        if not self.skills_root.exists() or not self.skills_root.is_dir():
            logger.warning("Skills root directory does not exist: %s", self.skills_root)
            return skills

        # Check subdirectories for SKILL.md
        for path in sorted(self.skills_root.iterdir()):
            if path.is_dir():
                skill_file = path / "SKILL.md"
                if skill_file.exists() and skill_file.is_file():
                    skill = self._parse_skill_dir(path, skill_file)
                    if skill:
                        skills.append(skill)
            elif path.name == "SKILL.md":
                skill = self._parse_skill_dir(self.skills_root, path)
                if skill:
                    skills.append(skill)

        return skills

    def _parse_skill_dir(self, skill_dir: Path, skill_file: Path) -> SkillDocument | None:
        """Parse SKILL.md and directory structure into a SkillDocument."""
        try:
            raw_text = skill_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error("Failed to read skill file %s: %s", skill_file, e)
            return None

        metadata, body = self._parse_frontmatter(raw_text)
        if not metadata:
            logger.warning("Skill file missing valid frontmatter: %s", skill_file)
            return None

        name = metadata.get("name") or skill_dir.name
        description = metadata.get("description", "")
        category = metadata.get("category")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        # Collect references
        references: list[str] = []
        refs_dir = skill_dir / "references"
        if refs_dir.exists() and refs_dir.is_dir():
            references = [
                f.name for f in sorted(refs_dir.iterdir()) if f.is_file() and not f.name.startswith(".")
            ]

        # Collect examples
        examples: list[str] = []
        examples_dir = skill_dir / "examples"
        if examples_dir.exists() and examples_dir.is_dir():
            examples = [
                f.name for f in sorted(examples_dir.iterdir()) if f.is_file() and not f.name.startswith(".")
            ]

        return SkillDocument(
            name=name,
            description=description,
            content=body.strip(),
            path=skill_dir,
            category=category,
            tags=tags,
            references=references,
            examples=examples,
            metadata=metadata,
        )

    def _parse_frontmatter(self, text: str) -> tuple[dict[str, Any] | None, str]:
        """Extract YAML frontmatter and markdown body from text."""
        trimmed = text.lstrip()
        if not trimmed.startswith("---"):
            return None, text

        # Find closing delimiter
        closing_idx = trimmed.find("\n---", 3)
        if closing_idx == -1:
            return None, text

        frontmatter_str = trimmed[3:closing_idx]
        body = trimmed[closing_idx + 4 :]

        try:
            parsed = yaml.safe_load(frontmatter_str)
            if isinstance(parsed, dict):
                return parsed, body
            return None, text
        except yaml.YAMLError as e:
            logger.warning("YAML parsing error: %s", e)
            return None, text
