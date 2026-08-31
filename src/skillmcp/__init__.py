"""Skill Management System (SkillMCP)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("skillmcp")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"

