"""Analysis stage command implementation."""

from __future__ import annotations

import logging
from pathlib import Path

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
        logger.error(f"目标路径不存在: {target_root}")
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
        print(f"\n✓ 分析阶段 Prompt 已生成: {prompt_path}\n")
        print("请让 Codex 执行以下操作:")
        print(f"  1. 读取 Prompt 文件: {prompt_path}")
        print(f"  2. 完成分析后，将产物保存到: {artifacts_dir / 'analysis.md'}\n")
        print("完成后执行下一步:")
        print("  copal spec\n")

        return 0

    except Exception as e:
        logger.error(f"生成 Prompt 失败: {e}")
        return 1
