"""Analysis stage command implementation."""

from __future__ import annotations

import logging
from pathlib import Path

from ..memory.integration import maybe_record_stage_memory
from ..memory.models import MemoryType
from ..system.fs import ensure_runtime_dirs
from ..system.mcp import read_mcp_available
from ..system.prompt_builder import render_stage_prompt

logger = logging.getLogger(__name__)

# Package directory
PACKAGE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PACKAGE_DIR / "templates" / "base"


def analyze_command(
    target: str,
    title: str | None = None,
    goals: str | None = None,
    constraints: str | None = None
) -> int:
    """Execute the analysis stage.

    Args:
        target: Target repository path.
        title: Optional task title.
        goals: Optional task goals.
        constraints: Optional task constraints.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    target_root = Path(target).resolve()

    if not target_root.exists():
        logger.error(f"Target path does not exist: {target_root}")
        return 1

    # Ensure runtime and artifacts directories exist
    runtime_dir, artifacts_dir = ensure_runtime_dirs(target_root)

    # Read available MCPs
    mcp_available = read_mcp_available(target_root)

    # Build task metadata
    task_meta = {}
    if title:
        task_meta['title'] = title
    if goals:
        task_meta['goals'] = goals
    if constraints:
        task_meta['constraints'] = constraints

    # Paths
    templates_root = TEMPLATE_DIR / ".copal" / "global"
    role_template = templates_root / "knowledge-base" / "roles" / "analyst.md"
    hooks_yaml = target_root / ".copal" / "hooks" / "hooks.yaml"

    try:
        # Render the prompt
        prompt_path = render_stage_prompt(
            stage='analysis',
            role_template_path=role_template,
            hooks_yaml_path=hooks_yaml,
            templates_root=templates_root,
            runtime_dir=runtime_dir,
            mcp_available=mcp_available,
            task_meta=task_meta if task_meta else None
        )

        # Print instructions
        print(f"\n✓ Analysis stage prompt generated: {prompt_path}\n")
        print("Please have Codex perform the following:")
        print(f"  1. Read the prompt file: {prompt_path}")
        print(f"  2. After completing analysis, save artifacts to: {artifacts_dir / 'analysis.md'}\n")
        print("Next step:")
        print("  copal spec\n")

        maybe_record_stage_memory(
            target_root=target_root,
            memory_type=MemoryType.NOTE,
            content=f"Analysis stage prompt generated at {prompt_path}",
            metadata={
                "stage": "analysis",
                "prompt_path": str(prompt_path),
            },
            importance=0.3,
        )

        return 0

    except Exception as e:
        logger.error(f"Failed to generate prompt: {e}")
        return 1
