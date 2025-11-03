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
        print("\nRuntime directory not found (.copal/runtime/)")
        print("Please run 'copal analyze' to start a new task\n")
        return

    # Find the most recent prompt
    prompts = sorted(runtime_dir.glob("*.prompt.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not prompts:
        print("\nNo prompt files found in runtime directory")
        print("Please run one of the following commands to start the workflow:")
        print("  copal analyze")
        print()
        return

    latest_prompt = prompts[0]
    stage_name = latest_prompt.stem.replace('.prompt', '')

    print(f"\n=== Resume Workflow ===\n")
    print(f"Latest stage: {stage_name}")
    print(f"Prompt file: {latest_prompt}")
    print()
    print("To continue workflow:")
    print(f"  1. Have Codex read: {latest_prompt}")
    print(f"  2. After completion, save artifacts to .copal/artifacts/")
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
        print(f"Expected output: {expected_outputs[stage_name]}")
        print()

    # Check if artifact exists
    artifacts_dir = target_root / ".copal" / "artifacts"
    if artifacts_dir.exists():
        artifact_file = artifacts_dir / f"{stage_name}.md"
        if artifact_file.exists():
            print(f"Note: Artifact file {artifact_file.name} already exists")
            print()
