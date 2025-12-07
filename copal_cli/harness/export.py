from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console

from copal_cli.config.manifest import Manifest
from copal_cli.config.pack import Pack
from copal_cli.adapters.claude import ClaudeAdapter
from copal_cli.adapters.gemini import GeminiAdapter
from copal_cli.adapters.codex import CodexAdapter

logger = logging.getLogger(__name__)
console = Console()

def export_command(tool: str, target: str = ".") -> int:
    """
    Export Copal packs to agent tools.
    
    Args:
        tool: Target tool name (e.g. 'claude', 'gemini', 'codex').
        target: Target repository path.
        
    Returns:
        0 success, 1 error, 2 config error.
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

    # Instantiate adapter
    adapter = None
    if tool == "claude":
        adapter = ClaudeAdapter(manifest, target_path)
    elif tool == "gemini":
        adapter = GeminiAdapter(manifest, target_path)
    elif tool == "codex":
        adapter = CodexAdapter(manifest, target_path)
    else:
        console.print(f"[red]Unknown tool: {tool}[/red]")
        return 1
        
    # Export each pack
    exported_count = 0
    
    # Handle both list of strings and list of dicts for packs
    packs_list = manifest.packs
    
    for pack_ref in packs_list:
        pack_path = None
        
        if isinstance(pack_ref, str):
            # Assumes pack is installed in .copal/packs/<name>
            pack_path = target_path / ".copal" / "packs" / pack_ref
        elif isinstance(pack_ref, dict):
            path_str = pack_ref.get("path")
            if path_str:
                pack_path = target_path / path_str
        
        if not pack_path:
            console.print(f"[red]Could not resolve path for pack ref: {pack_ref}[/red]")
            return 1
            
        try:
            pack = Pack.load(pack_path)
            adapter.export(pack)
            exported_count += 1
            console.print(f"[green]✓ Exported pack '{pack.name}' to {tool}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to export pack at {pack_path}: {e}[/red]")
            return 1
            
    if exported_count == 0:
        console.print("[yellow]No packs exported.[/yellow]")
        
    return 0
