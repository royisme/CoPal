"""Commit stage command implementation."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from ..memory.integration import maybe_record_stage_memory
from ..memory.models import MemoryType
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
        logger.error(f"Target path does not exist: {target_root}")
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

    print(f"\n✓ Commit stage completed: {commit_file}\n")
    print("Workflow metadata:")
    print(f"  Task ID: {commit_data['task_id']}")
    print(f"  Timestamp: {commit_data['timestamp']}")
    print(f"  Artifact count: {len(artifact_files)}")
    if artifact_files:
        print("\n  Artifact list:")
        for artifact in sorted(artifact_files):
            print(f"    - {artifact}")
    print("\nWorkflow complete! Run 'copal analyze' to start a new task.\n")

    maybe_record_stage_memory(
        target_root=target_root,
        memory_type=MemoryType.NOTE,
        content=(
            "Commit stage completed with task {task} and {count} artifacts.".format(
                task=commit_data["task_id"],
                count=len(artifact_files),
            )
        ),
        metadata={
            "stage": "commit",
            "task_id": commit_data["task_id"],
            "artifacts": artifact_files,
            "commit_file": str(commit_file.relative_to(target_root)),
        },
        importance=0.5,
    )

    return 0
