from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from .fs import read_text, write_text
from .hooks import select_injection_blocks

logger = logging.getLogger(__name__)


def render_stage_prompt(
    stage: str,
    role_template_path: Path,
    hooks_yaml_path: Path,
    templates_root: Path,
    runtime_dir: Path,
    mcp_available: list[str],
    task_meta: dict | None = None,
) -> Path:
    """Render a stage prompt by combining role template with injection blocks."""

    try:
        role_content = read_text(role_template_path)
    except FileNotFoundError:
        logger.error("Role template not found: %s", role_template_path)
        raise

    injection_blocks = select_injection_blocks(stage, mcp_available, hooks_yaml_path)

    injection_content = ""
    if injection_blocks:
        hooks_dir = hooks_yaml_path.parent
        for block_path in injection_blocks:
            full_block_path = hooks_dir / block_path
            try:
                block_content = read_text(full_block_path)
                injection_content += f"\n\n{block_content}"
                logger.debug("Injected block: %s", block_path)
            except FileNotFoundError:
                logger.warning("Injection block not found: %s", full_block_path)
                continue

    header = _build_runtime_header(stage, task_meta)

    full_prompt = f"{header}\n\n{role_content}{injection_content}"

    output_path = runtime_dir / f"{stage}.prompt.md"
    write_text(output_path, full_prompt)

    logger.info("Generated prompt: %s", output_path)
    return output_path


def _build_runtime_header(stage: str, task_meta: dict | None = None) -> str:
    """Build the runtime header for the generated prompt."""

    stage_info = {
        "analysis": {
            "role": "Analyst",
            "output": ".copal/artifacts/analysis.md",
            "description": "Analyse the task and capture open questions, context, and research targets.",
        },
        "spec": {
            "role": "Specifier",
            "output": ".copal/artifacts/task_spec.md",
            "description": "Produce an actionable specification with scope, interfaces, and acceptance criteria.",
        },
        "plan": {
            "role": "Planner",
            "output": ".copal/artifacts/plan.md",
            "description": "Break down the work into executable steps, files, risks, and validation notes.",
        },
        "implement": {
            "role": "Implementer",
            "output": ".copal/artifacts/patch_notes.md",
            "description": "Document code changes, impacted files, tests, and follow-up actions.",
        },
        "review": {
            "role": "Reviewer",
            "output": ".copal/artifacts/review_report.md, .copal/artifacts/pr_draft.md",
            "description": "Validate quality, risk, and release readiness, then draft the PR summary.",
        },
    }

    info = stage_info.get(
        stage,
        {
            "role": stage.capitalize(),
            "output": f".copal/artifacts/{stage}.md",
            "description": f"Expected output for the {stage} stage.",
        },
    )

    header_lines = [
        "---",
        f"# CoPal Runtime Prompt - {stage.capitalize()} Stage",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "---",
        "",
        f"# Role: {info['role']}",
        "",
        f"**Current stage**: {stage}",
        f"**Expected artifact**: `{info['output']}`",
        f"**Stage goal**: {info['description']}",
    ]

    if task_meta:
        header_lines.append("\n## Task metadata")
        if "title" in task_meta:
            header_lines.append(f"**Title**: {task_meta['title']}")
        if "goals" in task_meta:
            header_lines.append(f"**Goals**: {task_meta['goals']}")
        if "constraints" in task_meta:
            header_lines.append(f"**Constraints**: {task_meta['constraints']}")

    header_lines.append("\n---")
    return "\n".join(header_lines)
