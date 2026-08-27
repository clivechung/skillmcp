"""Configuration management for SkillMCP using Pydantic Settings."""

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable overrides."""

    model_config = SettingsConfigDict(
        env_prefix="SKILLMCP_",
        env_file=".env",
        extra="ignore",
    )

    skills_dir: Path = Field(
        default=Path("skills"),
        description="Path to directory containing skills to load and serve.",
    )
    host: str = Field(
        default="0.0.0.0",
        description="Host interface to bind the MCP HTTP server to.",
    )
    port: int = Field(
        default=8000,
        description="Port to bind the MCP HTTP server to.",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    )
    app_name: str = Field(
        default="SkillMCP Server",
        description="Name of the MCP application.",
    )
    transport: str = Field(
        default="streamable-http",
        description="MCP transport type ('streamable-http', 'http', or 'sse').",
    )


def get_settings() -> Settings:
    """Return a fresh or default instance of Settings."""
    return Settings()

