---
id: codex-cli
origin: copal
type: cli-guide
owner: integration-team
enforcement: recommended
updated: 2025-11-03
---

# Codex CLI Guide

## Installation and Verification

```bash
npm install -g @openai/codex
codex --version
```

Homebrew users can run `brew install codex`.

## Launch Modes

```bash
codex                          # Interactive TUI
codex "fix lint errors"         # Start a session with an initial prompt
codex exec "explain utils.ts"  # Headless automation mode
```

## Safety Settings

- Approval policy: `codex --ask-for-approval suggest | on-request | on-failure | never`
- Sandbox modes:
  - `codex --sandbox read-only`
  - `codex --sandbox workspace-write`
  - `codex --sandbox danger-full-access`

## MCP Management

```bash
codex mcp list
codex mcp add docs -- npx -y mcp-server-docs
codex mcp get docs --json
codex mcp remove docs
codex mcp login <server>
```

## Usage Tips

- Start in the repository root so Git status and context are accurate.
- Break large tasks into smaller prompts and track progress with `update_plan`.
- Audit history with `codex logs --tail` or by inspecting `~/.config/codex/logs/`.
- Tighten approval policies before running risky commands or deploying changes.

## Troubleshooting

- **Authentication failure** – Confirm you are logged into your OpenAI account and API key is configured.
- **MCP startup issues** – Validate the command following `--` is executable by running it manually.
- **Timeouts** – Split requests or provide more detailed instructions to reduce execution time.
