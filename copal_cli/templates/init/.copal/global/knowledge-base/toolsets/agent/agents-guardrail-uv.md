---
id: agent-guardrail-uv
origin: copal
type: agent-script
owner: automation-guild
updated: 2025-11-03
---

# Guardrail: Enforce `uv` for Python Commands

## Purpose

Prevent accidental use of bare `python` or `pip` commands by wrapping them with `uv`. This helps standardise dependency management and execution environments.

## Setup

1. Copy `scripts/guardrails/check_shell.py` into your project or reference it directly from `.copal/global/`.
2. Configure your CLI to execute the guardrail before running shell commands (e.g., via pre-command hooks or wrapper scripts).
3. Store audit logs under `.copal/global/logs/` or a project-specific path.

## Usage

```bash
python scripts/guardrails/check_shell.py --command "python script.py"
python scripts/guardrails/check_shell.py --command "pip install requests"
python scripts/guardrails/check_shell.py --snapshot --limit 10
```

- Returns exit code `0` when the command passes validation.
- Returns exit code `1` when the guardrail blocks the command and records an audit entry.
- Use `--snapshot` to inspect recent violations stored in `logs/guardrail-history.jsonl`.

## Customisation Ideas

- Extend the script to cover language-specific commands (e.g., `npm`, `composer`).
- Integrate with project logging or incident tracking.
- Add allowlists per repository or task to balance flexibility and enforcement.
