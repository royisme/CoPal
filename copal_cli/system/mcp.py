"""MCP (Model Context Protocol) utilities for CoPal CLI."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


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
        print("\n.copal/mcp-available.json not found or empty")
        print("\nYou can create this file and add available MCP tool names, for example:")
        print('  ["context7", "active-file", "file-tree"]')
        print("\nSupported MCP examples:")
        print("  - context7: Context documentation query tool")
        print("  - active-file: Active file tool")
        print("  - file-tree: File tree navigation tool")
        return

    print(f"\nAvailable MCP tools ({len(mcp_names)}):")
    for name in mcp_names:
        print(f"  - {name}")
    print()
