"""Commit stage command implementation."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from datetime import datetime

from ..system.fs import ensure_runtime_dirs, write_text

logger = logging.getLogger(__name__)


def commit_command(target: str, task_id: str | None = None) -> int:
    """Execute the commit stage.

    This stage creates a metadata file recording the completion of the workflow.

    Args:
        target: Target repository path.
        task_id: Optional task identifier.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    target_root = Path(target).resolve()

    if not target_root.exists():
        logger.error(f"目标路径不存在: {target_root}")
        return 1

    runtime_dir, artifacts_dir = ensure_runtime_dirs(target_root)

    # Collect artifacts
    artifact_files = []
    for artifact in artifacts_dir.glob("*.md"):
        artifact_files.append(str(artifact.relative_to(target_root)))
    for artifact in artifacts_dir.glob("*.json"):
        if artifact.name != "commit.json":  # Don't include the commit file itself
            artifact_files.append(str(artifact.relative_to(target_root)))

    # Build commit metadata
    commit_data = {
        "task_id": task_id or f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "artifacts": sorted(artifact_files),
        "workflow_completed": True
    }

    # Write commit metadata
    commit_file = artifacts_dir / "commit.json"
    write_text(commit_file, json.dumps(commit_data, indent=2, ensure_ascii=False))

    print(f"\n✓ 提交阶段已完成: {commit_file}\n")
    print("工作流元数据:")
    print(f"  任务 ID: {commit_data['task_id']}")
    print(f"  时间戳: {commit_data['timestamp']}")
    print(f"  产物数量: {len(artifact_files)}")
    if artifact_files:
        print("\n  产物列表:")
        for artifact in sorted(artifact_files):
            print(f"    - {artifact}")
    print("\n工作流已完成！可以执行 'copal analyze' 开始新任务。\n")

    return 0
