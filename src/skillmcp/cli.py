"""CLI interface for SkillMCP using Typer."""

import asyncio
from pathlib import Path
import sys
from typing import Annotated, Optional

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from skillmcp.config import Settings
from skillmcp.domain.scanner import SkillScanner
from skillmcp.domain.service import SkillService
from skillmcp.logging import setup_logging

app = typer.Typer(
    name="skillmcp",
    help="SkillMCP CLI and server runner.",
    add_completion=False,
)
console = Console()


@app.command()
def serve(
    host: Annotated[Optional[str], typer.Option(help="Host to bind server to")] = None,
    port: Annotated[Optional[int], typer.Option(help="Port to bind server to")] = None,
    skills_dir: Annotated[Optional[Path], typer.Option(help="Directory containing skills")] = None,
    log_level: Annotated[Optional[str], typer.Option(help="Logging level (DEBUG, INFO, etc.)")] = None,
) -> None:
    """Start the SkillMCP MCP HTTP server."""
    settings = Settings()
    if host:
        settings.host = host
    if port:
        settings.port = port
    if skills_dir:
        settings.skills_dir = skills_dir
    if log_level:
        settings.log_level = log_level

    setup_logging(settings.log_level)
    console.print(f"[bold green]Starting SkillMCP server on {settings.host}:{settings.port}[/bold green]")
    console.print(f"[blue]Serving skills from: {settings.skills_dir.resolve()}[/blue]")

    from skillmcp.server.mcp_app import create_app

    server_app = create_app(settings=settings)
    uvicorn.run(
        server_app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


@app.command()
def validate(
    skills_path: Annotated[
        Path,
        typer.Argument(help="Path to skills directory or specific skill directory"),
    ] = Path("skills"),
) -> None:
    """Validate skill structure, YAML frontmatter, and assets."""
    target = skills_path.resolve()
    if not target.exists():
        console.print(f"[bold red]Error: Path '{target}' does not exist.[/bold red]")
        raise typer.Exit(code=1)

    scanner = SkillScanner(skills_root=target if target.is_dir() else target.parent)
    
    # Identify target dirs
    skill_dirs: list[Path] = []
    if (target / "SKILL.md").exists():
        skill_dirs = [target]
    elif target.is_dir():
        skill_dirs = [p for p in target.iterdir() if p.is_dir() and (p / "SKILL.md").exists()]

    if not skill_dirs:
        console.print(f"[yellow]No skill directories containing SKILL.md found in '{target}'.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title="Skill Validation Report")
    table.add_column("Skill Directory", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Issues / Notes", style="yellow")

    all_valid = True

    for s_dir in skill_dirs:
        skill_file = s_dir / "SKILL.md"
        skill_doc = scanner._parse_skill_dir(s_dir, skill_file)
        
        issues = []
        if not skill_doc:
            issues.append("Failed to parse SKILL.md or invalid YAML frontmatter")
            status = "[red]INVALID[/red]"
            all_valid = False
            table.add_row(s_dir.name, "-", "-", status, "; ".join(issues))
            continue

        if not skill_doc.name:
            issues.append("Missing required 'name' in metadata")
        if not skill_doc.description:
            issues.append("Missing required 'description' in metadata")
        if not skill_doc.content:
            issues.append("Skill body content is empty")

        if issues:
            all_valid = False
            status = "[red]INVALID[/red]"
        else:
            status = "[green]VALID[/green]"
            issues.append(f"{len(skill_doc.references)} refs, {len(skill_doc.examples)} examples")

        table.add_row(
            s_dir.name,
            skill_doc.name,
            (skill_doc.description[:40] + "...") if len(skill_doc.description) > 40 else skill_doc.description,
            status,
            "; ".join(issues),
        )

    console.print(table)
    if not all_valid:
        console.print("[bold red]Validation failed: One or more skills contain errors.[/bold red]")
        raise typer.Exit(code=1)
    
    console.print(f"[bold green]Validation passed: {len(skill_dirs)} skills are valid.[/bold green]")


@app.command(name="list")
def list_command(
    skills_path: Annotated[
        Path,
        typer.Option(help="Path to skills directory"),
    ] = Path("skills"),
) -> None:
    """List available skills from a directory."""
    target = skills_path.resolve()
    scanner = SkillScanner(skills_root=target)
    service = SkillService(scanner=scanner)
    skills = asyncio.run(service.list_skills())

    if not skills:
        console.print(f"[yellow]No skills found in '{target}'.[/yellow]")
        return

    table = Table(title=f"Skills in {target}")
    table.add_column("Name", style="magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Tags", style="blue")
    table.add_column("Description", style="white")

    for s in skills:
        table.add_row(
            s.name,
            s.category or "-",
            ", ".join(s.tags) if s.tags else "-",
            s.description,
        )

    console.print(table)


if __name__ == "__main__":
    app()
