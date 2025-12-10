"""MCP (Model Context Protocol) utilities for CoPal CLI."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()


def read_mcp_available(target_root: Path) -> list[str]:
    """Read available MCP names from .copal/mcp-available.json.

    Args:
        target_root: Root directory of the target repository.

    Returns:
        list[str]: List of available MCP names. Empty list if file doesn't exist.
    """
    mcp_file = target_root / ".copal" / "mcp-available.json"

    if not mcp_file.exists():
        logger.debug(f"MCP file not found: {mcp_file}")
        return []

    try:
        with open(mcp_file, encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.warning(f"Invalid MCP file format (expected list): {mcp_file}")
            return []

        return data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse MCP file: {e}")
        return []
    except Exception as e:
        logger.error(f"Error reading MCP file: {e}")
        return []


def print_mcp_available(target_root: Path) -> None:
    """Print available MCP names from .copal/mcp-available.json.

    Args:
        target_root: Root directory of the target repository.
    """
    mcp_names = read_mcp_available(target_root)

    if not mcp_names:
        console.print("[yellow].copal/mcp-available.json not found or empty[/yellow]")
        console.print("\n[dim]You can create this file and add available MCP tool names, for example:[/dim]")
        console.print('  [cyan]["context7", "active-file", "file-tree"][/cyan]')
        console.print("\n[bold]Supported MCP examples:[/bold]")
        console.print("  • [cyan]context7[/cyan]: Context documentation query tool")
        console.print("  • [cyan]active-file[/cyan]: Active file tool")
        console.print("  • [cyan]file-tree[/cyan]: File tree navigation tool")
        return

    table = Table(title=f"Available MCP Tools ({len(mcp_names)})")
    table.add_column("Name", style="cyan")
    
    for name in mcp_names:
        table.add_row(name)
    
    console.print(table)
