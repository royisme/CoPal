"""Review stage command implementation."""

from __future__ import annotations

import logging
from pathlib import Path

from ..system.fs import ensure_runtime_dirs
from ..system.mcp import read_mcp_available
from ..system.prompt_builder import render_stage_prompt

logger = logging.getLogger(__name__)

PACKAGE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PACKAGE_DIR / "templates" / "base"


def review_command(target: str) -> int:
    """Execute the review stage.

    Args:
        target: Target repository path.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    target_root = Path(target).resolve()

    if not target_root.exists():
        logger.error(f"Target path does not exist: {target_root}")
        return 1

    runtime_dir, artifacts_dir = ensure_runtime_dirs(target_root)
    mcp_available = read_mcp_available(target_root)

    templates_root = TEMPLATE_DIR / ".copal" / "global"
    role_template = templates_root / "knowledge-base" / "roles" / "reviewer.md"
    hooks_yaml = target_root / ".copal" / "hooks" / "hooks.yaml"

    try:
        prompt_path = render_stage_prompt(
            stage='review',
            role_template_path=role_template,
            hooks_yaml_path=hooks_yaml,
            templates_root=templates_root,
            runtime_dir=runtime_dir,
            mcp_available=mcp_available
        )

        print(f"\n✓ Review stage prompt generated: {prompt_path}\n")
        print("Please have Codex perform the following:")
        print(f"  1. Read the prompt file: {prompt_path}")
        print(f"  2. After completing review, save artifacts to:")
        print(f"     - {artifacts_dir / 'review_report.md'}")
        print(f"     - {artifacts_dir / 'pr_draft.md'}\n")
        print("Next step:")
        print("  copal commit\n")

        return 0

    except Exception as e:
        logger.error(f"Failed to generate prompt: {e}")
        return 1
