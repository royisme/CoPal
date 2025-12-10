"""Skill scaffold management for CoPal."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

logger = logging.getLogger(__name__)
console = Console()

SKILL_SCAFFOLD_DIR = Path(__file__).parent.parent / "templates" / "skill-scaffold"


def skill_create_command(
    name: str,
    target: str = ".",
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    interactive: bool = True,
) -> int:
    """
    Create a new skill from the scaffold template.
    
    Args:
        name: Skill name (will be converted to skill_id)
        target: Target directory (default: current directory)
        description: Skill description
        tags: List of tags for the skill
        interactive: Whether to prompt for missing values
    
    Returns:
        0 on success, 1 on failure
    """
    target_path = Path(target).resolve()
    skills_dir = target_path / ".copal" / "skills"
    
    # Validate .copal exists
    if not (target_path / ".copal").exists():
        console.print("[red]✗ No .copal directory found. Run 'copal init' first.[/red]")
        return 1
    
    # Convert name to skill_id (lowercase, underscores)
    skill_id = name.lower().replace("-", "_").replace(" ", "_")
    skill_dir = skills_dir / skill_id
    
    if skill_dir.exists():
        console.print(f"[red]✗ Skill '{skill_id}' already exists at {skill_dir}[/red]")
        return 1
    
    # Interactive prompts for missing values
    if interactive:
        if not description:
            description = Prompt.ask(
                "Skill description",
                default=f"A skill for {name}"
            )
        if not tags:
            tags_input = Prompt.ask(
                "Tags (comma-separated)",
                default="utility"
            )
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
    
    # Defaults
    description = description or f"A skill for {name}"
    tags = tags or ["utility"]
    
    # Template variables
    created_at = datetime.now().isoformat()
    tags_block = "\n".join(f"  - {tag}" for tag in tags)
    
    template_vars = {
        "skill_id": skill_id,
        "title": name,
        "description": description,
        "tags_block": tags_block,
        "created_at": created_at,
    }
    
    console.print(Panel.fit(
        f"[bold blue]Creating Skill:[/bold blue] {name}",
        subtitle=f"ID: {skill_id}"
    ))
    
    try:
        # Create skill directory
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Process all template files
        files_created = []
        for template_file in SKILL_SCAFFOLD_DIR.rglob("*.jinja"):
            rel_path = template_file.relative_to(SKILL_SCAFFOLD_DIR)
            # Remove .jinja extension
            target_file = skill_dir / str(rel_path).replace(".jinja", "")
            
            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Read and render template
            template_content = template_file.read_text(encoding="utf-8")
            rendered = Template(template_content).safe_substitute(template_vars)
            
            target_file.write_text(rendered, encoding="utf-8")
            files_created.append(target_file.relative_to(target_path))
            logger.debug(f"Created {target_file}")
        
        # Success output
        console.print(f"\n[green]✓ Skill '{skill_id}' created successfully![/green]")
        console.print("\n[bold]Files created:[/bold]")
        for f in files_created:
            console.print(f"  • {f}")
        
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  1. Edit [cyan]{skill_dir / 'SKILL.md'}[/cyan] to define skill behavior")
        console.print(f"  2. Add implementation in [cyan]{skill_dir / 'scripts/run.py'}[/cyan]")
        console.print(f"  3. Run [bold]copal export claude[/bold] to sync to Claude skills")
        
        return 0
        
    except Exception as e:
        console.print(f"[red]✗ Failed to create skill: {e}[/red]")
        logger.exception("Skill creation failed")
        return 1


def skill_list_command(target: str = ".") -> int:
    """List all skills in the project."""
    target_path = Path(target).resolve()
    skills_dir = target_path / ".copal" / "skills"
    
    if not skills_dir.exists():
        console.print("[yellow]No skills directory found.[/yellow]")
        return 0
    
    skills = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    
    if not skills:
        console.print("[dim]No skills found. Create one with 'copal skill create <name>'[/dim]")
        return 0
    
    console.print(Panel.fit("[bold]Project Skills[/bold]"))
    
    for skill_dir in sorted(skills):
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            # Try to extract description from frontmatter
            content = skill_md.read_text(encoding="utf-8")
            desc = _extract_frontmatter_field(content, "description") or "[dim]No description[/dim]"
        else:
            desc = "[dim]Missing SKILL.md[/dim]"
        
        console.print(f"  • [cyan]{skill_dir.name}[/cyan]: {desc}")
    
    return 0


def _extract_frontmatter_field(content: str, field: str) -> Optional[str]:
    """Extract a field from YAML frontmatter."""
    lines = content.split("\n")
    in_frontmatter = False
    
    for line in lines:
        if line.strip() == "---":
            if in_frontmatter:
                break
            in_frontmatter = True
            continue
        
        if in_frontmatter and line.startswith(f"{field}:"):
            value = line.split(":", 1)[1].strip()
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            return value
    
    return None
