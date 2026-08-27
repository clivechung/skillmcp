"""Domain service orchestrating skill retrieval and search operations."""

import logging
from skillmcp.domain.models import SkillDocument
from skillmcp.domain.scanner import SkillScanner

logger = logging.getLogger(__name__)


class SkillService:
    """Core domain service for skill operations."""

    def __init__(self, scanner: SkillScanner) -> None:
        self.scanner = scanner
        self._cache: dict[str, SkillDocument] | None = None

    async def reload(self) -> list[SkillDocument]:
        """Scan skills from disk and update internal lookup cache."""
        skills = await self.scanner.scan_all()
        self._cache = {s.name: s for s in skills}
        logger.info("Loaded %d skills from %s", len(skills), self.scanner.skills_root)
        return skills

    async def list_skills(self, force_reload: bool = False) -> list[SkillDocument]:
        """List all available skills."""
        if self._cache is None or force_reload:
            await self.reload()
        assert self._cache is not None
        return list(self._cache.values())

    async def get_skill(self, name: str, force_reload: bool = False) -> SkillDocument | None:
        """Get a specific skill by name."""
        if self._cache is None or force_reload:
            await self.reload()
        assert self._cache is not None
        return self._cache.get(name)

    async def search_skills(self, query: str) -> list[SkillDocument]:
        """Search skills matching name, description, tags, or content."""
        all_skills = await self.list_skills()
        q = query.lower()
        results: list[SkillDocument] = []
        for skill in all_skills:
            if (
                q in skill.name.lower()
                or q in skill.description.lower()
                or any(q in tag.lower() for tag in skill.tags)
                or q in skill.content.lower()
            ):
                results.append(skill)
        return results

    async def read_skill_reference(self, skill_name: str, reference_name: str) -> str | None:
        """Read the content of a specific reference document in a skill."""
        skill = await self.get_skill(skill_name)
        if not skill:
            return None

        # Prevent directory traversal
        clean_ref_name = Path(reference_name).name
        ref_file = skill.path / "references" / clean_ref_name
        if ref_file.exists() and ref_file.is_file():
            try:
                return ref_file.read_text(encoding="utf-8")
            except Exception as e:
                logger.error("Failed to read reference file %s: %s", ref_file, e)
                return None
        return None

    async def read_skill_example(self, skill_name: str, example_name: str) -> str | None:
        """Read the content of a specific example document in a skill."""
        skill = await self.get_skill(skill_name)
        if not skill:
            return None

        clean_example_name = Path(example_name).name
        example_file = skill.path / "examples" / clean_example_name
        if example_file.exists() and example_file.is_file():
            try:
                return example_file.read_text(encoding="utf-8")
            except Exception as e:
                logger.error("Failed to read example file %s: %s", example_file, e)
                return None
        return None
