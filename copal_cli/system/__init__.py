"""System utilities for CoPal CLI."""

from .fs import ensure_runtime_dirs, read_text, write_text
from .mcp import read_mcp_available, print_mcp_available
from .hooks import select_injection_blocks
from .prompt_builder import render_stage_prompt

__all__ = [
    'ensure_runtime_dirs',
    'read_text',
    'write_text',
    'read_mcp_available',
    'print_mcp_available',
    'select_injection_blocks',
    'render_stage_prompt',
]
