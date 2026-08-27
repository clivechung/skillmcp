"""Structured logging configuration for SkillMCP adhering to TREM principles."""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure standardized standard-library logging for the application.
    
    Args:
        level: Logging level string (e.g. 'DEBUG', 'INFO', 'WARNING', 'ERROR').
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
