"""Resume functionality for CoPal CLI."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def print_resume_info(target_root: Path) -> None:
    """Print information about resuming from current state.

    Args:
        target_root: Root directory of the target repository.
    """
    runtime_dir = target_root / ".copal" / "runtime"

    if not runtime_dir.exists():
        print("\n未找到运行时目录 (.copal/runtime/)")
        print("请先运行 copal analyze 开始新任务\n")
        return

    # Find the most recent prompt
    prompts = sorted(runtime_dir.glob("*.prompt.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not prompts:
        print("\n运行时目录中没有找到 Prompt 文件")
        print("请运行以下命令之一开始工作流：")
        print("  copal analyze")
        print()
        return

    latest_prompt = prompts[0]
    stage_name = latest_prompt.stem.replace('.prompt', '')

    print(f"\n=== 恢复工作流 ===\n")
    print(f"最近的阶段: {stage_name}")
    print(f"Prompt 文件: {latest_prompt}")
    print()
    print("继续工作流:")
    print(f"  1. 让 Codex 读取: {latest_prompt}")
    print(f"  2. 完成任务后，产物应保存到相应的 .copal/artifacts/ 目录")
    print()

    # Show expected output
    expected_outputs = {
        'analysis': '.copal/artifacts/analysis.md',
        'spec': '.copal/artifacts/task_spec.md',
        'plan': '.copal/artifacts/plan.md',
        'implement': '.copal/artifacts/patch_notes.md',
        'review': '.copal/artifacts/review_report.md, .copal/artifacts/pr_draft.md'
    }

    if stage_name in expected_outputs:
        print(f"期望产物: {expected_outputs[stage_name]}")
        print()

    # Check if artifact exists
    artifacts_dir = target_root / ".copal" / "artifacts"
    if artifacts_dir.exists():
        artifact_file = artifacts_dir / f"{stage_name}.md"
        if artifact_file.exists():
            print(f"注意: 产物文件 {artifact_file.name} 已存在")
            print()
