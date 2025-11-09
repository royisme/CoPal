---
id: claude-code-cli
origin: copal
type: cli-guide
owner: integration-team
updated: 2025-11-03
---

# Claude Code CLI Guide

## Installation and Login

```bash
pipx install anthropic-cli  # or pip install anthropic-cli
anthropic login             # Authenticate with your API key
```

## Launch Modes

```bash
anthropic code               # Start interactive Claude Code session
anthropic code --resume      # Resume the last session
anthropic code --import <file>  # Seed a session with context
```

## Safety Controls

- Enable approval prompts via configuration: `anthropic config set approvals.required true`
- Restrict file access with `anthropic config set sandbox.mode read-only`
- Allow specific tools with `anthropic config allow-tool shell("pytest *")`

## MCP Integration

```bash
anthropic mcp list
anthropic mcp install context7
anthropic mcp info context7
anthropic mcp remove context7
```

## Usage Tips

- Start sessions from the repository root to give Claude full context.
- Use `/plan` or `update_plan` style prompts to keep large tasks organised.
- Capture session logs with `/logs` and attach key excerpts to reviews or retrospectives.
- Switch to stricter approval settings before executing destructive commands.

## Troubleshooting

- **Authentication errors** – Re-run `anthropic login` and ensure the API key has Claude Code access.
- **Session drops** – Use `anthropic code --resume` to reopen the previous session state.
- **Tool execution blocked** – Check sandbox configuration and update `allow-tool` rules if needed.
