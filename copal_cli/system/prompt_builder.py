"""Prompt builder for CoPal CLI."""

from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime

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
    task_meta: dict | None = None
) -> Path:
    """Render a stage prompt by combining role template with injection blocks.

    Args:
        stage: Stage name (e.g., 'analysis', 'spec', 'plan', 'implement', 'review').
        role_template_path: Path to the role template markdown file.
        hooks_yaml_path: Path to hooks.yaml file.
        templates_root: Root directory of templates (e.g., templates/base/.copal/global).
        runtime_dir: Directory to write the rendered prompt.
        mcp_available: List of available MCP names.
        task_meta: Optional dictionary with task metadata (title, goals, constraints, etc.).

    Returns:
        Path: Path to the rendered prompt file (.copal/runtime/<stage>.prompt.md).
    """
    # Read role template
    try:
        role_content = read_text(role_template_path)
    except FileNotFoundError:
        logger.error(f"Role template not found: {role_template_path}")
        raise

    # Select injection blocks based on hooks
    injection_blocks = select_injection_blocks(stage, mcp_available, hooks_yaml_path)

    # Read and concatenate injection blocks
    injection_content = ""
    if injection_blocks:
        hooks_dir = hooks_yaml_path.parent
        for block_path in injection_blocks:
            full_block_path = hooks_dir / block_path
            try:
                block_content = read_text(full_block_path)
                injection_content += f"\n\n{block_content}"
                logger.debug(f"Injected block: {block_path}")
            except FileNotFoundError:
                logger.warning(f"Injection block not found: {full_block_path}")
                continue

    # Build runtime header
    header = _build_runtime_header(stage, task_meta)

    # Combine all parts
    full_prompt = f"{header}\n\n{role_content}{injection_content}"

    # Write to runtime directory
    output_path = runtime_dir / f"{stage}.prompt.md"
    write_text(output_path, full_prompt)

    logger.info(f"Generated prompt: {output_path}")
    return output_path


def _build_runtime_header(stage: str, task_meta: dict | None = None) -> str:
    """Build runtime header for the prompt.

    Args:
        stage: Stage name.
        task_meta: Optional task metadata.

    Returns:
        str: Runtime header content.
    """
    # Map stage to role and expected output
    stage_info = {
        'analysis': {
            'role': 'Analyst',
            'output': '.copal/artifacts/analysis.md',
            'description': '分析任务并产出问题理解与信息收集点'
        },
        'spec': {
            'role': 'Specifier',
            'output': '.copal/artifacts/task_spec.md',
            'description': '形成任务说明书（范围、接口、验收标准）'
        },
        'plan': {
            'role': 'Planner',
            'output': '.copal/artifacts/plan.md',
            'description': '形成可执行计划（步骤、文件、风险）'
        },
        'implement': {
            'role': 'Implementer',
            'output': '.copal/artifacts/patch_notes.md',
            'description': '输出补丁建议/修改清单/测试建议'
        },
        'review': {
            'role': 'Reviewer',
            'output': '.copal/artifacts/review_report.md, .copal/artifacts/pr_draft.md',
            'description': '一致性/覆盖率/风险评估，生成 PR 描述'
        }
    }

    info = stage_info.get(stage, {
        'role': stage.capitalize(),
        'output': f'.copal/artifacts/{stage}.md',
        'description': f'{stage} stage output'
    })

    header = f"""---
# CoPal Runtime Prompt - {stage.capitalize()} Stage
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
---

# 角色: {info['role']}

**当前阶段**: {stage}  
**期望产物**: `{info['output']}`  
**阶段目标**: {info['description']}
"""

    if task_meta:
        header += "\n## 任务信息\n"
        if 'title' in task_meta:
            header += f"**任务标题**: {task_meta['title']}\n"
        if 'goals' in task_meta:
            header += f"**目标**: {task_meta['goals']}\n"
        if 'constraints' in task_meta:
            header += f"**约束条件**: {task_meta['constraints']}\n"

    header += "\n---\n"
    return header
