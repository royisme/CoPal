---
id: toolset-agent-index
origin: copal
type: toolset-index
owner: automation-guild
updated: 2025-11-03
---

# Agent Toolset Index

This directory contains optional guardrails and helper scripts that projects can adopt or extend.

## Contents

- `agents-guardrail-uv.md` – Example guardrail for enforcing `uv` when running Python or pip commands
- `scripts/guardrails/check_shell.py` – Reference implementation of the guardrail script (extend as needed)
- `logs/` – Recommended location for guardrail audit logs
- `retrospectives/` – Space for documenting gaps, incidents, or improvements identified by the guardrails

Projects can replace these examples with their own enforcement scripts and update references in `UserAgents.md`.
