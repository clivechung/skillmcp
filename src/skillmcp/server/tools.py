"""MCP tools interface definitions and handlers."""

import logging
from typing import Any
from skillmcp.domain.service import SkillService

logger = logging.getLogger(__name__)


class SkillMCPTools:
    """Encapsulates MCP tool functions delegating to the domain SkillService."""

    def __init__(self, service: SkillService) -> None:
        self.service = service

    async def list_skills(self) -> list[dict[str, Any]]:
        """List all available skills with their metadata, available references, and examples.
        
        Returns:
            List of skill metadata dictionaries.
        """
        skills = await self.service.list_skills()
        return [
            {
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "tags": s.tags,
                "references": s.references,
                "examples": s.examples,
            }
            for s in skills
        ]

    async def get_skill(self, name: str) -> str | None:
        """Get full instructions and content for a given skill.
        
        Args:
            name: The unique identifier name of the skill.
            
        Returns:
            The complete skill markdown content or None if not found.
        """
        skill = await self.service.get_skill(name)
        if not skill:
            return None

        # Format full skill document with frontmatter header and body
        doc_parts = [
            "---",
            f"name: {skill.name}",
            f"description: {skill.description}",
        ]
        if skill.category:
            doc_parts.append(f"category: {skill.category}")
        if skill.tags:
            doc_parts.append(f"tags: {', '.join(skill.tags)}")
        doc_parts.append("---")
        doc_parts.append("")
        doc_parts.append(skill.content)

        return "\n".join(doc_parts)

    async def search_skills(self, query: str) -> list[dict[str, Any]]:
        """Search available skills by query string across name, description, tags, and content.
        
        Args:
            query: Keyword or phrase to search for.
            
        Returns:
            List of matching skill metadata dictionaries.
        """
        skills = await self.service.search_skills(query)
        return [
            {
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "tags": s.tags,
                "references": s.references,
                "examples": s.examples,
            }
            for s in skills
        ]

    async def read_skill_reference(self, name: str, ref_path: str) -> str | None:
        """Read a bundled reference document for a given skill.
        
        Args:
            name: The unique name of the skill.
            ref_path: Filename of the reference document.
            
        Returns:
            The reference document text content or None if not found.
        """
        return await self.service.read_skill_reference(name, ref_path)

    async def read_skill_example(self, name: str, example_path: str) -> str | None:
        """Read a bundled example document for a given skill.
        
        Args:
            name: The unique name of the skill.
            example_path: Filename of the example document.
            
        Returns:
            The example document text content or None if not found.
        """
        return await self.service.read_skill_example(name, example_path)


def create_mcp_tools(service: SkillService) -> SkillMCPTools:
    """Factory helper to create SkillMCPTools instance."""
    return SkillMCPTools(service=service)
