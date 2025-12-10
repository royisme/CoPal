import argparse
import logging
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from .git_utils import worktree_add, worktree_list, worktree_remove, get_repo_root
from .sync import sync_assets

logger = logging.getLogger(__name__)
console = Console()

def handle_new(args: argparse.Namespace) -> int:
    """Handle 'copal worktree new' command."""
    cwd = Path(os.getcwd())
    repo_root = get_repo_root(cwd)
    
    if not repo_root:
        console.print("[red]✗ Not inside a git repository.[/red]")
        return 1
        
    name = args.name
    branch = args.branch or name
    base = args.base
    
    # Strategy: Create worktrees in a sibling directory "../{repo_name}.wt/{name}"
    # This keeps the main repo clean and avoids nesting issues.
    repo_name = repo_root.name
    wt_root = repo_root.parent / f"{repo_name}.wt"
    target_path = wt_root / name
    
    if target_path.exists():
        console.print(f"[red]✗ Worktree path already exists:[/red] {target_path}")
        return 1
        
    # 1. Create Worktree
    console.print(f"[dim]Creating worktree '{name}' at {target_path}...[/dim]")
    if not worktree_add(repo_root, target_path, branch, base):
        return 1
        
    # 2. Sync Assets
    console.print("[dim]Syncing CoPal assets...[/dim]")
    if not sync_assets(repo_root, target_path):
        console.print("[yellow]Warning: Failed to sync some assets. You may need to run 'copal init' manually in the new worktree.[/yellow]")
        
    console.print(f"[green]✓ Successfully created worktree '{name}'![/green]")
    console.print(f"\nTo switch to it: [cyan]cd {target_path}[/cyan]")
    
    return 0

def handle_list(args: argparse.Namespace) -> int:
    """Handle 'copal worktree list' command."""
    cwd = Path(os.getcwd())
    worktrees = worktree_list(cwd)
    
    if not worktrees:
        console.print("[dim]No worktrees found.[/dim]")
        return 0
    
    table = Table(title="Git Worktrees")
    table.add_column("Path", style="cyan")
    table.add_column("Branch", style="green")
    table.add_column("HEAD", style="dim")
    
    for path, head, branch in worktrees:
        table.add_row(path, branch, head[:7])
    
    console.print(table)
    return 0

def handle_remove(args: argparse.Namespace) -> int:
    """Handle 'copal worktree remove' command."""
    cwd = Path(os.getcwd())
    repo_root = get_repo_root(cwd)
    
    if not repo_root:
        console.print("[red]✗ Not inside a git repository.[/red]")
        return 1
        
    name = args.name
    force = args.force
    
    # Try to find the worktree path
    # 1. Check if name is a full path
    target_path = Path(name)
    if not target_path.is_absolute():
        # 2. Check default location
        repo_name = repo_root.name
        wt_root = repo_root.parent / f"{repo_name}.wt"
        target_path = wt_root / name
    
    if not target_path.exists():
        console.print(f"[red]✗ Worktree path not found:[/red] {target_path}")
        # Fallback: try to find by branch name matching the directory name?
        # For now, strict path matching based on our convention.
        return 1
        
    if not worktree_remove(repo_root, target_path, force):
        return 1
        
    console.print(f"[green]✓ Removed worktree '{name}'[/green]")
    return 0
