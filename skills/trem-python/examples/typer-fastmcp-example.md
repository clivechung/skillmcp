# Example: Typer CLI + FastMCP Server with Shared Domain

This example demonstrates how to build both a CLI tool (`typer`) and an AI Model Context Protocol server (`fastmcp`) sharing the same testable domain services.

---

## 📁 Architecture Overview

```text
src/skillms/
├── config.py         # Pydantic Settings
├── domain/
│   ├── models.py     # Pydantic domain models
│   └── service.py    # Core business logic (Protocol-driven)
├── cli.py            # Typer CLI entrypoint
├── mcp_server.py     # FastMCP server entrypoint
└── logging_config.py # Standard logging setup
```

---

## 1. Shared Domain Service (`src/skillms/domain/service.py`)

```python
import logging
from typing import Protocol
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class SkillItem(BaseModel):
    name: str
    category: str
    description: str

class SkillStorageProtocol(Protocol):
    async def list_all(self) -> list[SkillItem]: ...
    async def add(self, item: SkillItem) -> None: ...

class SkillManagerService:
    def __init__(self, storage: SkillStorageProtocol) -> None:
        self._storage = storage

    async def list_skills(self, category: str | None = None) -> list[SkillItem]:
        logger.info("Listing skills (filter category=%s)", category)
        items = await self._storage.list_all()
        if category:
            items = [i for i in items if i.category.lower() == category.lower()]
        return items

    async def register(self, name: str, category: str, description: str) -> SkillItem:
        item = SkillItem(name=name, category=category, description=description)
        await self._storage.add(item)
        logger.info("Registered skill '%s' in category '%s'", name, category)
        return item
```

---

## 2. Typer CLI Interface (`src/skillms/cli.py`)

```python
import asyncio
import typer
from rich.console import Console
from rich.table import Table
from skillms.domain.service import SkillManagerService
from skillms.adapters.filesystem import FileSystemStorage

app = typer.Typer(name="skillms", help="Skill Management System CLI", no_args_is_help=True)
console = Console()

def get_service() -> SkillManagerService:
    return SkillManagerService(storage=FileSystemStorage())

@app.command("list")
def list_skills(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
) -> None:
    """List all available skills."""
    service = get_service()
    skills = asyncio.run(service.list_skills(category=category))

    if not skills:
        console.print("[yellow]No skills found.[/yellow]")
        return

    table = Table(title="Available Skills")
    table.add_column("Name", style="cyan bold")
    table.add_column("Category", style="green")
    table.add_column("Description")

    for s in skills:
        table.add_row(s.name, s.category, s.description)

    console.print(table)

@app.command("add")
def add_skill(
    name: str = typer.Argument(..., help="Name of the skill"),
    category: str = typer.Option("general", "--category", "-c", help="Skill category"),
    desc: str = typer.Option("", "--desc", "-d", help="Skill description"),
) -> None:
    """Add a new skill to the registry."""
    service = get_service()
    asyncio.run(service.register(name=name, category=category, description=desc))
    console.print(f"[bold green]✓[/bold green] Added skill: [cyan]{name}[/cyan]")

if __name__ == "__main__":
    app()
```

---

## 3. FastMCP Server Interface (`src/skillms/mcp_server.py`)

```python
from fastmcp import FastMCP
from skillms.domain.service import SkillManagerService
from skillms.adapters.filesystem import FileSystemStorage

mcp = FastMCP("SkillMS MCP Server")
service = SkillManagerService(storage=FileSystemStorage())

@mcp.tool()
async def search_available_skills(category: str | None = None) -> list[dict]:
    """Retrieve skills registered in SkillMS, optionally filtered by category."""
    skills = await service.list_skills(category=category)
    return [skill.model_dump() for skill in skills]

@mcp.tool()
async def register_new_skill(name: str, category: str, description: str) -> str:
    """Register a new skill into the repository."""
    created = await service.register(name=name, category=category, description=description)
    return f"Successfully registered {created.name} in category {created.category}."

if __name__ == "__main__":
    mcp.run()
```

---

## 4. CLI Unit Testing with `CliRunner` (`tests/test_cli.py`)

```python
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock
from skillms.cli import app
from skillms.domain.service import SkillItem

runner = CliRunner()

def test_cli_list_command():
    with patch("skillms.cli.get_service") as mock_get_svc:
        mock_svc = AsyncMock()
        mock_svc.list_skills.return_value = [
            SkillItem(name="trem-python", category="software", description="Python TREM guidelines")
        ]
        mock_get_svc.return_value = mock_svc

        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "trem-python" in result.stdout
```
