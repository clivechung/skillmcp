"""Domain models for SkillMCP."""

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    """Metadata extracted from a skill's YAML frontmatter."""

    name: str = Field(..., description="Unique skill identifier name.")
    description: str = Field(..., description="High-level description of the skill capability.")
    category: str | None = Field(default=None, description="Optional categorization.")
    tags: list[str] = Field(default_factory=list, description="Descriptive tags for search/filtering.")
    extra: dict[str, Any] = Field(default_factory=dict, description="Additional custom frontmatter fields.")


class SkillDocument(BaseModel):
    """Full representation of a skill, including markdown body and bundled assets."""

    name: str = Field(..., description="Unique skill identifier name.")
    description: str = Field(..., description="High-level description of the skill capability.")
    content: str = Field(..., description="Full raw markdown instructions.")
    path: Path = Field(..., description="Filesystem directory path of the skill.")
    category: str | None = Field(default=None, description="Optional categorization.")
    tags: list[str] = Field(default_factory=list, description="Descriptive tags for search/filtering.")
    references: list[str] = Field(
        default_factory=list,
        description="Relative filenames of reference documents in references/ directory.",
    )
    examples: list[str] = Field(
        default_factory=list,
        description="Relative filenames of example documents in examples/ directory.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw frontmatter metadata mapping.",
    )


class SkillResource(BaseModel):
    """MCP Resource definition representation."""

    uri: str = Field(..., description="Resource URI, e.g. skill://{name}")
    name: str = Field(..., description="Display name for the resource.")
    description: str | None = Field(default=None, description="Resource description.")
    mime_type: str = Field(default="text/markdown", description="MIME type of resource content.")
