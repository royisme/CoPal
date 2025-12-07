# AGENTS.md - Agent Harness Entry Point

> **System**: This file is the primary entry point for AI Agents (Claude Code, Codex, Gemini).
> **Role**: Passive Execution Harness.

## 1. Core Directives

1. **Passive Execution**: Do not invent your own process. Follow the "Harness" instructions.
2. **Context Loading**: Your context is minimal by design. Read only what is linked here.
3. **Memory**: Check `.copal/memory/index.json` for persistent project state.

## 2. Active Pack & Workflows

**👉 [READ THIS FIRST: Engineering Loop Guide](.copal/packs/engineering_loop/PACK.md)**

Follow the link above to find:

- **Workflows** (Plan, Work, Review)
- **Roles** (Prompts)
- **References** (Conventions, Tech Stack)

## 3. Global Commands

- **Verify**: Run the project verification script.
  - Command: `sh .copal/packs/engineering_loop/scripts/verify.sh` (or see manifest)
- **Memory**:
  - `copal memory add`
  - `copal memory search`
