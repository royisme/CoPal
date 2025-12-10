"""Resume functionality for CoPal CLI."""

from __future__ import annotations

import logging
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

logger = logging.getLogger(__name__)
console = Console()


def print_resume_info(target_root: Path) -> None:
    """Print information about resuming from current state.

    Args:
        target_root: Root directory of the target repository.
    """
    runtime_dir = target_root / ".copal" / "runtime"

    if not runtime_dir.exists():
        console.print("[yellow]Runtime directory not found (.copal/runtime/)[/yellow]")
        console.print("[dim]Please run 'copal analyze' to start a new task[/dim]")
        return

    # Find the most recent prompt
    prompts = sorted(runtime_dir.glob("*.prompt.md"), key=lambda p: p.stat().st_mtime, reverse=True)

    if not prompts:
        console.print("[yellow]No prompt files found in runtime directory[/yellow]")
        console.print("[dim]Please run one of the following commands to start the workflow:[/dim]")
        console.print("  [cyan]copal analyze[/cyan]")
        return

    latest_prompt = prompts[0]
    stage_name = latest_prompt.stem.replace('.prompt', '')

    console.print(Panel.fit(
        f"[bold]Latest stage:[/bold] {stage_name}\n"
        f"[bold]Prompt file:[/bold] {latest_prompt}",
        title="[bold blue]Resume Workflow[/bold blue]"
    ))

    console.print("\n[bold]To continue workflow:[/bold]")
    console.print(f"  1. Have Codex read: [cyan]{latest_prompt}[/cyan]")
    console.print(f"  2. After completion, save artifacts to [cyan].copal/artifacts/[/cyan]")

    # Show expected output
    expected_outputs = {
        'analysis': '.copal/artifacts/analysis.md',
        'spec': '.copal/artifacts/task_spec.md',
        'plan': '.copal/artifacts/plan.md',
        'implement': '.copal/artifacts/patch_notes.md',
        'review': '.copal/artifacts/review_report.md, .copal/artifacts/pr_draft.md'
    }

    if stage_name in expected_outputs:
        console.print(f"\n[bold]Expected output:[/bold] [cyan]{expected_outputs[stage_name]}[/cyan]")

    # Check if artifact exists
    artifacts_dir = target_root / ".copal" / "artifacts"
    if artifacts_dir.exists():
        artifact_file = artifacts_dir / f"{stage_name}.md"
        if artifact_file.exists():
            console.print(f"\n[yellow]Note: Artifact file {artifact_file.name} already exists[/yellow]")
