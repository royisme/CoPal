---
id: core-environment
origin: copal
type: environment
owner: governance-team
updated: 2025-11-03
---

# Terminal Agent Environment Constraints

- **Working directory** – Assume commands run from the repository root. Specify `--cwd` or absolute paths if you need to operate elsewhere.
- **Approval policies** –
  - Codex: choose the appropriate `--ask-for-approval` mode (`on-request`, `suggest`, `never`).
  - Claude Code: enable approval prompts via configuration or launch flags.
  - Copilot CLI: manage permissions with `-p`, `--allow-tool`, and `--deny-tool`.
- **Sandboxing** – Prefer restricted execution (`--sandbox workspace-write`, etc.) and only escalate when a fully privileged environment is required.
- **Command guardrails** –
  - See `toolsets/agent/agents-guardrail-uv.md` for a simple shell guard example.
  - Projects can add language-specific rules (e.g., disallow bare `python` or `pip`).
- **MCP / plugin discovery** – Before each task run `mcp tools list` and `mcp resources list` to confirm available tools and docs.
- **Logging and auditability** –
  - Codex: check `~/.config/codex/logs/` or `codex logs --tail`.
  - Claude Code: use `/logs` or inspect the default log directory.
  - Copilot CLI: capture `/usage` output for request statistics and code changes.
  Summarise critical logs in the task report or store them under `logs/`.
