"""Status display utilities for CoPal CLI."""

from __future__ import annotations

import logging
from pathlib import Path

from .mcp import read_mcp_available

logger = logging.getLogger(__name__)


def print_status(target_root: Path) -> None:
    """Print current CoPal status including available MCPs and artifacts.

    Args:
        target_root: Root directory of the target repository.
    """
    print("\n=== CoPal Status ===\n")

    # Show available MCPs
    mcp_names = read_mcp_available(target_root)
    if mcp_names:
        print(f"Available MCP tools ({len(mcp_names)}):")
        for name in mcp_names:
            print(f"  ✓ {name}")
    else:
        print("Available MCP tools: None (.copal/mcp-available.json not found or empty)")

    # Show runtime prompts
    runtime_dir = target_root / ".copal" / "runtime"
    print(f"\nRuntime prompts (.copal/runtime/):")
    if runtime_dir.exists():
        prompts = sorted(runtime_dir.glob("*.prompt.md"))
        if prompts:
            for prompt in prompts:
                print(f"  ✓ {prompt.name}")
        else:
            print("  None")
    else:
        print("  Directory not found")

    # Show artifacts
    artifacts_dir = target_root / ".copal" / "artifacts"
    print(f"\nArtifacts (.copal/artifacts/):")
    if artifacts_dir.exists():
        artifacts = sorted(artifacts_dir.glob("*.md")) + sorted(artifacts_dir.glob("*.json"))
        if artifacts:
            for artifact in artifacts:
                print(f"  ✓ {artifact.name}")
        else:
            print("  None")
    else:
        print("  Directory not found")

    # Suggest next command
    stages = ['analysis', 'spec', 'plan', 'implement', 'review', 'commit']
    expected_artifacts = {
        'analysis': 'analysis.md',
        'spec': 'task_spec.md',
        'plan': 'plan.md',
        'implement': 'patch_notes.md',
        'review': 'review_report.md',
        'commit': 'commit.json'
    }

    next_stage = None
    if artifacts_dir.exists():
        for stage in stages:
            artifact_file = artifacts_dir / expected_artifacts[stage]
            if not artifact_file.exists():
                next_stage = stage
                break

    print("\nSuggested next step:")
    if next_stage:
        print(f"  copal {next_stage}")
    else:
        print("  All stages complete, run 'copal analyze' to start a new task")

    print()
