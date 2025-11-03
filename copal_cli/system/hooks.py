"""Hook system for CoPal CLI."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def select_injection_blocks(
    stage: str,
    mcp_names: list[str],
    hooks_yaml_path: Path
) -> list[str]:
    """Select injection blocks based on stage and available MCPs.

    This function parses hooks.yaml and returns a list of injection block paths
    that should be injected for the given stage and available MCPs.

    Args:
        stage: Current stage name (e.g., 'analysis', 'spec', 'plan', 'implement', 'review').
        mcp_names: List of available MCP names from mcp-available.json.
        hooks_yaml_path: Path to hooks.yaml file.

    Returns:
        list[str]: List of relative paths to injection blocks (relative to hooks directory).
                   Returns empty list if hooks.yaml doesn't exist or no rules match.
    """
    if not hooks_yaml_path.exists():
        logger.debug(f"Hooks file not found: {hooks_yaml_path}")
        return []

    try:
        # Parse YAML manually (zero dependencies requirement)
        content = hooks_yaml_path.read_text(encoding='utf-8')

        # Simple YAML parser for the expected structure
        rules = _parse_hooks_yaml(content)

        # Filter rules by stage and MCP availability
        injection_blocks = []
        for rule in rules:
            if rule.get('stage') != stage:
                continue

            # Check MCP conditions
            any_mcp = rule.get('any_mcp', [])
            all_mcp = rule.get('all_mcp', [])

            # Check if any_mcp condition is met
            if any_mcp:
                if not any(mcp in mcp_names for mcp in any_mcp):
                    continue

            # Check if all_mcp condition is met
            if all_mcp:
                if not all(mcp in mcp_names for mcp in all_mcp):
                    continue

            # Add injection blocks from this rule
            inject = rule.get('inject', [])
            injection_blocks.extend(inject)

        logger.debug(f"Selected {len(injection_blocks)} injection blocks for stage '{stage}'")
        return injection_blocks

    except Exception as e:
        logger.error(f"Error parsing hooks file: {e}")
        return []


def _parse_hooks_yaml(content: str) -> list[dict[str, Any]]:
    """Simple YAML parser for hooks.yaml structure.

    This is a minimal parser that handles the specific structure of hooks.yaml
    without requiring external dependencies.

    Args:
        content: YAML content as string.

    Returns:
        list[dict]: List of rule dictionaries.
    """
    rules = []
    current_rule: dict[str, Any] | None = None
    in_inject = False
    indent_level = 0

    for line in content.split('\n'):
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith('#'):
            continue

        # Detect rule start
        if stripped.startswith('- id:'):
            if current_rule:
                rules.append(current_rule)
            current_rule = {'id': stripped.split(':', 1)[1].strip()}
            in_inject = False
            continue

        if current_rule is None:
            continue

        # Parse rule fields
        if stripped.startswith('stage:'):
            current_rule['stage'] = stripped.split(':', 1)[1].strip()
        elif stripped.startswith('any_mcp:'):
            # Parse list inline or multiline
            value = stripped.split(':', 1)[1].strip()
            if value.startswith('['):
                # Inline list: [item1, item2]
                value_inner = value.strip('[]').strip()
                if value_inner:
                    items = value_inner.split(',')
                    current_rule['any_mcp'] = [item.strip().strip('"\'') for item in items if item.strip()]
                else:
                    current_rule['any_mcp'] = []
            else:
                current_rule['any_mcp'] = []
                in_inject = False
        elif stripped.startswith('all_mcp:'):
            value = stripped.split(':', 1)[1].strip()
            if value.startswith('['):
                # Inline list: [item1, item2]
                value_inner = value.strip('[]').strip()
                if value_inner:
                    items = value_inner.split(',')
                    current_rule['all_mcp'] = [item.strip().strip('"\'') for item in items if item.strip()]
                else:
                    current_rule['all_mcp'] = []
            else:
                current_rule['all_mcp'] = []
                in_inject = False
        elif stripped.startswith('inject:'):
            current_rule['inject'] = []
            in_inject = True
        elif in_inject and stripped.startswith('-'):
            # Injection block item
            block_path = stripped[1:].strip().strip('"\'')
            current_rule['inject'].append(block_path)
        elif stripped.startswith('- ') and 'any_mcp' in current_rule and len(current_rule.get('any_mcp', [])) == 0 and not in_inject:
            # List item for any_mcp (multiline format)
            current_rule['any_mcp'].append(stripped[1:].strip().strip('"\''))
        elif stripped.startswith('- ') and 'all_mcp' in current_rule and len(current_rule.get('all_mcp', [])) == 0 and not in_inject:
            # List item for all_mcp (multiline format)
            current_rule['all_mcp'].append(stripped[1:].strip().strip('"\''))

    # Add last rule
    if current_rule:
        rules.append(current_rule)

    return rules
