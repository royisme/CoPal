---
id: knowledge-base
origin: copal
type: index
updated: 2025-10-31
---

# CoPal Shared Knowledge Base

This directory provides the default knowledge skeleton for terminal-based AI coding assistants. It aims to:

- Offer unified role, workflow, and tooling guidance for Codex, Claude Code, Copilot CLI, and similar tools.
- Use YAML front matter so LLMs or scripts can quickly locate the right document.
- Layer cleanly with project overrides—projects can supply files with the same path to replace the defaults.

## Directory Overview

- `core/` – Global principles and environment constraints
- `roles/` – Role playbooks for Analyst, Specifier, Planner, Implementer, Reviewer, etc.
- `workflows/` – Cross-role processes such as planning-to-implementation, implementation loops, skill lifecycle, and review-release
- `toolsets/cli/` – Quick-start guides for common CLIs
- `toolsets/project/` – Tool discovery and documentation lookup aids
- `toolsets/agent/` – Guardrail and helper script examples shipped with CoPal
- `logs/`, `retrospectives/` – Reserved directories for guardrail output and follow-up actions (projects may override or extend)

After initialisation, list project-specific documents in `UserAgents.md` or create overrides in your repository. Link them from `AGENTS.md` so agents know where to look first.
