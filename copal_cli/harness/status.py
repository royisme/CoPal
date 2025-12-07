from __future__ import annotations

import logging
from pathlib import Path
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from copal_cli.config.manifest import Manifest
from copal_cli.config.pack import Pack

logger = logging.getLogger(__name__)
console = Console()

def status_command(target: str = ".") -> int:
    """
    Display current Copal project status including artifacts.
    """
    target_path = Path(target).resolve()
    manifest_path = target_path / ".copal" / "manifest.yaml"
    
    if not manifest_path.exists():
        console.print(f"[red]✗ Manifest not found at {manifest_path}[/red]")
        return 2

    try:
        manifest = Manifest.load(manifest_path)
    except Exception as e:
        console.print(f"[red]✗ Manifest invalid: {e}[/red]")
        return 2

    # Display Project Info
    console.print(Panel(
        f"[bold]{manifest.project.name}[/bold]\n{manifest.project.description}",
        title="Project Info",
        expand=False
    ))
    
    # Pack Status
    table = Table(title="Installed Packs")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    
    active_pack = None

    for pack_ref in manifest.packs:
        path_str = None
        name = "unknown"
        
        if isinstance(pack_ref, str):
            name = pack_ref
            path_str = f".copal/packs/{pack_ref}" # Assumption based on init logic
        elif isinstance(pack_ref, dict):
            path_str = pack_ref.get("path")
            name = pack_ref.get("name", "unknown")
            
        status = "[red]Missing[/red]"
        version = "?"
        
        if path_str:
            pack_path = target_path / path_str
            try:
                pack = Pack.load(pack_path)
                status = f"[green]Active (v{pack.version})[/green]"
                if name == manifest.default_pack:
                    active_pack = pack
            except Exception:
                status = "[red]Invalid[/red]"
        
        table.add_row(name, status)
    console.print(table)
    
    # Agent Manager Summary (Todo)
    from .agent_manager import AgentManager
    console.print()
    try:
        mgr = AgentManager(target_path)
        mgr.summary()
    except Exception:
        # Fallback if no todo found or error
        console.print("[dim]No active engineering loop found.[/dim]")

    return 0
