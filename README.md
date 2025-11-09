# CoPal

**Command-line Orchestration Playbook for AI Coders**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Overview

CoPal provides a reusable workflow, knowledge base, and skill management toolkit for teams working with terminal-based AI coding assistants such as OpenAI Codex CLI, Anthropic Claude Code, GitHub Copilot CLI, and similar tools. The project bundles:

- **Six-stage workflow orchestration** (Analyze → Spec → Plan → Implement → Review → Commit)
- **Prompt generation** with stage-specific headers, task metadata injection, and optional MCP guidance
- **Knowledge base templates** for roles, workflows, toolsets, and global policies (YAML front matter for fast retrieval)
- **Project initialisation** via `copal init` to copy AGENTS, UserAgents, and shared knowledge base assets
- **Skill lifecycle tooling** (registry build/list/search, scaffold generation, sandbox-aware execution)
- **Utility commands** for MCP discovery, workflow status, and resume hints

The CLI is implemented with the Python standard library and ships with pytest-based tests. All documentation and templates are now fully in English so they can be reused across international teams.

## Quick Start

```bash
# Clone and install locally
pip install -e .

# Initialise CoPal assets in the current repository
copal init --target .

# Optional: declare available MCP tools
cat <<'JSON' > .copal/mcp-available.json
["context7", "active-file", "file-tree"]
JSON

# Run the workflow (each command emits a prompt in .copal/runtime/)
copal analyze --title "Add login" --goals "Implement JWT auth"
copal spec
copal plan
copal implement
copal review
copal commit

# Inspect overall progress
copal status
```

After initialisation, edit `UserAgents.md` with project-specific guidelines and link to any additional documentation. Agents should read `AGENTS.md`, the shared `.copal/global/` knowledge base, and then `UserAgents.md` before starting work.

## CLI Reference

### Core Commands

| Command | Purpose |
| ------- | ------- |
| `copal init [--force] [--dry-run]` | Copy templates (AGENTS, UserAgents, `.copal/`) into a repository |
| `copal validate --target <path>` | Validate knowledge base files for required front matter |
| `copal analyze|spec|plan|implement|review|commit` | Generate prompts and capture artifacts for each workflow stage |
| `copal mcp ls` | List MCP tools declared in `.copal/mcp-available.json` |
| `copal status` | Summarise prompts, artifacts, and the suggested next stage |
| `copal resume` | Show the most recent prompt for workflow recovery |

### Skill Commands

| Command | Purpose |
| ------- | ------- |
| `copal skill registry build --skills-root <dir>` | Scan skills and write `registry.json` |
| `copal skill registry list --skills-root <dir> [--lang <lang>]` | List registered skills, optionally filtered by language |
| `copal skill search --skills-root <dir> --query <text> [--lang <lang>]` | Fuzzy search skill metadata |
| `copal skill scaffold <name> [--skills-root <dir>] [--lang <lang>] [--description <text>]` | Create a minimal skill skeleton (`skill.json`, `prelude.md`, entrypoint log) |
| `copal skill exec --skills-root <dir> --skill <name> [--sandbox]` | Stream a skill's entrypoint log to stdout, enforcing sandbox requirements |

Use the Python API (`copal_cli.skills.scaffold_skill`) when you need the richer Jinja-based templates from `copal_cli/templates/skills/` and automatic `skills.json` manifest updates.

## Knowledge Base

The shared knowledge base lives under `copal_cli/templates/base/.copal/global/knowledge-base/` and includes:

- **core/** – Global principles, environment guardrails, and information architecture
- **roles/** – Playbooks for Analyst, Specifier, Planner, Implementer, and Reviewer
- **workflows/** – Step-by-step guides for planning-to-implementation, implementation loops, review and release, and skill lifecycle
- **toolsets/** – Quick-reference guides for common CLIs plus project tooling and guardrail scripts

Projects can override any template by recreating the same path in their repository and linking it from `UserAgents.md`.

## Skill Lifecycle

Skills are reusable automation modules stored under `.copal/skills/` (or a custom root). Each skill contains `skill.json`, `prelude.md`, scripts/tests, and optional logs. Typical lifecycle:

1. Scaffold a new skill with `copal skill scaffold` or the Python API.
2. Implement scripts, prompts, guardrails, and tests. Document runtime requirements in `prelude.md`.
3. Build the registry (`copal skill registry build`) so teammates can discover the skill via `copal skill search`.
4. Execute with `copal skill exec`, passing `--sandbox` if the skill metadata marks it as sensitive.
5. Commit the skill directory, `registry.json`, and relevant logs so others can reuse it safely.

A higher-level sandbox executor is available via `copal_cli.skills.SkillExecutor`, which runs bash-prefixed commands inside the `LocalSandbox` with output redaction and resource limits.

## Architecture Overview

```
CoPal/
├── copal_cli/
│   ├── cli.py                 # CLI entry point
│   ├── init.py                # Template installer
│   ├── stages/                # Stage command implementations
│   ├── system/                # Prompt builder, MCP helpers, status/resume utilities
│   ├── skills/                # Registry, selector, scaffolder, executor
│   └── templates/             # Base templates and skill scaffolds
├── docs/                      # Usage guides and design notes
├── examples/                  # Sample customisation layout
├── tests/                     # Pytest suites covering CLI, stages, skills, and integrations
└── pyproject.toml             # Package metadata
```

The prompt builder composes runtime headers with role templates and optional MCP hook injections defined in `.copal/hooks/hooks.yaml`. Hooks can target specific stages and MCP combinations (e.g., `context7` guidance during analysis and planning, `active-file` plus `file-tree` during implementation).

## Development

- Python 3.9+ is required (the codebase uses `from __future__ import annotations` to support newer typing syntax).
- Install dev dependencies with `pip install -e .[dev]`.
- Run the test suite with `pytest`.
- Use `copal validate` to ensure template front matter stays consistent.

## Contributing

Contributions are welcome! Please open an issue to discuss significant changes, fork the repository, create a feature branch, add tests, and submit a pull request under the MIT license.
