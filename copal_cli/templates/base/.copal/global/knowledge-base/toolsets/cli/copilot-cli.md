---
id: toolset-cli-copilot
origin: copal
type: cli-guide
owner: enablement-team
updated: 2025-11-03
---

# GitHub Copilot CLI Guide

## Installation and Login

```bash
npm install -g @github/copilot   # Requires Node.js 22+ and npm 10+
```

Run `/login` during the first session to authenticate with GitHub.

## Session Management

```bash
copilot                 # Interactive session
copilot --banner        # Show startup banner
copilot --continue      # Resume the most recent session
copilot --resume        # Browse past conversations
```

Common in-session commands: `/login`, `/exit`, `/clear`, `/usage`, `/help`.

## Safety Controls

- `copilot -p` – Approve file access interactively.
- `copilot --allow-all-paths` – Trust all paths (use with caution).
- `copilot --allow-tool "shell(git *)"` – Allow specific commands.
- `copilot --deny-tool "shell(rm -rf *)"` – Deny dangerous commands.
- `/usage` – Review premium usage, token consumption, and change summaries.

## Non-interactive Mode

```bash
copilot "Generate docs"           # Write to stdout
copilot "Fix lint" --stdio        # Stream responses through STDIO
copilot "Refactor file" --output docs/refactor.md
```

Combine with shell commands, e.g. `copilot "Generate docs" && cat docs/api.md`.

## File Referencing

- Use `@` inside prompts to reference files or images with fuzzy search.
- Reference multiple files at once for better context.

## Troubleshooting

- **Authentication issues** – Ensure your subscription is active; run `/logout` then `/login` if necessary.
- **Session loss** – Inspect `~/.copilot/session-state` and use `--resume` to restore history.
- **Insufficient permissions** – Adjust `--allow-tool`, `--allow-all-paths`, or approve commands interactively when prompted.
