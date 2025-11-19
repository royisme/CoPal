# CoPal

**Command-line Orchestration Playbook for AI Coders**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

English | [简体中文](./README_CN.md)

## Overview

CoPal provides a reusable workflow, knowledge base, and skill management toolkit for teams working with terminal-based AI coding assistants such as OpenAI Codex CLI, Anthropic Claude Code, GitHub Copilot CLI, and similar tools. The project bundles:

- **Six-stage workflow orchestration** (Analyze → Spec → Plan → Implement → Review → Commit)
- **Prompt generation** with stage-specific headers, task metadata injection, and optional MCP guidance
- **Knowledge base templates** for roles, workflows, toolsets, and global policies (YAML front matter for fast retrieval)
- **Project initialisation** via `copal init` to copy AGENTS, UserAgents, and shared knowledge base assets
- **Skill lifecycle tooling** (registry build/list/search, scaffold generation, sandbox-aware execution)
- **Memory layer** that persists decisions, notes, and experiences across workflow runs
- **Utility commands** for MCP discovery, workflow status, and resume hints

The CLI is implemented with the Python standard library and ships with pytest-based tests. All documentation and templates are available in both English and Chinese for international teams.

## Core Features

### 🔄 Six-Stage Workflow
CoPal provides a structured software development workflow:
1. **Analyze** - Understand the task and gather context
2. **Spec** - Write a formal task specification
3. **Plan** - Produce an executable implementation plan
4. **Implement** - Execute the plan and capture changes
5. **Review** - Assess quality and draft PR notes
6. **Commit** - Record workflow metadata

### 📚 Knowledge Base Management
- Built-in role templates (Analyst, Specifier, Planner, Implementer, Reviewer)
- Workflow guides and best practices
- Customizable project-specific knowledge bases
- YAML front matter for fast retrieval

### 🛠️ Skill System
- Reusable automation modules
- Skill registry and search functionality
- Scaffold generation tools
- Sandbox execution environment
- Skill versioning and sharing

### 🧠 Memory Layer
- Persist decisions and experiences across workflow runs
- Graph-based knowledge storage (using NetworkX)
- Support for decisions, preferences, experiences, plans, and notes
- Memory relationships and querying

### 🔌 MCP Integration
- Model Context Protocol hook system
- Tool-specific guidance injection
- Flexible hook configuration
- Support for context7, active-file, file-tree, and more

## Quick Start

### Installation

#### Recommended: run via `uvx` (no global install)

If you already have `uv` installed, you can run CoPal without installing it globally:

```bash
uvx copal-cli --help
uvx copal-cli init --target .
```

This will download the latest released `copal-cli` package, create an isolated environment for it, and run the `copal` CLI inside your current project directory.

#### Alternative: install the CLI as a tool

If you prefer a persistent CLI installation, you can use `uv tool` or `pipx`:

```bash
# Using uv tool
uv tool install copal-cli
copal --help

# Or with pipx
pipx install copal-cli
copal --help

# Or with plain pip (inside a virtualenv)
python -m pip install copal-cli
copal --help
```

Use whichever tool you are most comfortable with. We recommend `uv` or `pipx` to avoid polluting your global Python environment.

#### Development (from source, for contributors)

If you want to hack on CoPal itself or contribute changes:

```bash
git clone https://github.com/royisme/CoPal.git
cd CoPal

# Option A: using uv to manage the virtualenv
uv sync

# Option B: using pip directly
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Now you can run the CLI from this environment:
uv run copal --help   # if using uv
# or simply:
copal --help
```

### Initialize CoPal in your project

Once the `copal` CLI is available (either via `uvx`, `uv tool`, `pipx`, or a local install), you should initialize CoPal **in the root directory of the project that you want to instrument with CoPal**.

```bash
cd /path/to/your/project

# Initialize CoPal assets into the current repository
copal init --target .

# Preview what would be created (dry-run)
copal init --dry-run

# Force overwrite existing CoPal assets (be careful)
copal init --force
```

Important:

* Do **not** run `copal init --target .` in the CoPal source repository itself, unless you know exactly what you are doing.
* The intent is to initialize CoPal's `.copal` folder, templates, and agent guides inside **your own application or service repository**.

### Configure MCP Tools (Optional)

Declare available MCP tools:

```bash
cat <<'JSON' > .copal/mcp-available.json
["context7", "active-file", "file-tree"]
JSON
```

### Run the Workflow

Execute the six-stage workflow (each command generates prompts in `.copal/runtime/`):

```bash
# 1. Analysis stage - understand the task
copal analyze --title "Add user login" --goals "Implement JWT authentication"

# 2. Specification stage - write specifications
copal spec

# 3. Planning stage - create plan
copal plan

# 4. Implementation stage - execute implementation
copal implement

# 5. Review stage - code review
copal review

# 6. Commit stage - commit changes
copal commit

# Check overall progress
copal status

# Resume interrupted workflow
copal resume
```

## CLI Reference

### Core Commands

| Command | Purpose |
| ------- | ------- |
| `copal init [--force] [--dry-run]` | Copy templates (AGENTS, UserAgents, `.copal/`) into a repository |
| `copal validate --target <path>` | Validate knowledge base files for required front matter |
| `copal analyze\|spec\|plan\|implement\|review\|commit` | Generate prompts and capture artifacts for each workflow stage |
| `copal mcp ls` | List MCP tools declared in `.copal/mcp-available.json` |
| `copal status` | Summarise prompts, artifacts, and the suggested next stage |
| `copal resume` | Show the most recent prompt for workflow recovery |

### Skill Commands

| Command | Purpose |
| ------- | ------- |
| `copal skill registry build --skills-root <dir>` | Scan skills and write `registry.json` |
| `copal skill registry list --skills-root <dir> [--lang <lang>]` | List registered skills, optionally filtered by language |
| `copal skill search --skills-root <dir> --query <text> [--lang <lang>]` | Fuzzy search skill metadata |
| `copal skill scaffold <name> [--skills-root <dir>] [--lang <lang>]` | Create a minimal skill skeleton (`skill.json`, `prelude.md`, entrypoint log) |
| `copal skill exec --skills-root <dir> --skill <name> [--sandbox]` | Stream a skill's entrypoint log to stdout, enforcing sandbox requirements |

### Memory Commands

| Command | Purpose |
| ------- | ------- |
| `copal memory add --type <type> --content "..."` | Create a memory entry |
| `copal memory search --query <text> [--type <type>]` | Search within the active scope |
| `copal memory show <id>` | Inspect the full record |
| `copal memory update <id> --content "..."` | Update stored content or metadata |
| `copal memory delete <id>` | Remove a memory and its relationships |
| `copal memory supersede <id> --type <type> --content "..."` | Add a follow-up memory with SUPERSEDES relationship |
| `copal memory list [--type <type>]` | List all memories in the active scope |
| `copal memory summary` | Show memory statistics |

Memory types include: `decision`, `preference`, `experience`, `plan`, `note`

## Knowledge Base

The shared knowledge base lives under `copal_cli/templates/base/.copal/global/knowledge-base/` and includes:

- **core/** – Global principles, environment guardrails, and information architecture
- **roles/** – Playbooks for Analyst, Specifier, Planner, Implementer, and Reviewer
- **workflows/** – Step-by-step guides for planning-to-implementation, implementation loops, review and release, and skill lifecycle
- **toolsets/** – Quick-reference guides for common CLIs plus project tooling and guardrail scripts

Projects can override any template by recreating the same path in their repository and linking it from `UserAgents.md`.

## Skill Lifecycle

Skills are reusable automation modules stored under `.copal/skills/` (or a custom root). Each skill contains `skill.json`, `prelude.md`, scripts/tests, and optional logs. Typical lifecycle:

1. Scaffold a new skill with `copal skill scaffold` or the Python API
2. Implement scripts, prompts, guardrails, and tests. Document runtime requirements in `prelude.md`
3. Build the registry (`copal skill registry build`) so teammates can discover the skill via `copal skill search`
4. Execute with `copal skill exec`, passing `--sandbox` if the skill metadata marks it as sensitive
5. Commit the skill directory, `registry.json`, and relevant logs so others can reuse it safely

A higher-level sandbox executor is available via `copal_cli.skills.SkillExecutor`, which runs bash-prefixed commands inside the `LocalSandbox` with output redaction and resource limits.

## Memory Layer Usage

The memory layer allows you to persist important information across workflow runs:

```bash
# Record a decision
copal memory add --type decision --content "Use JWT for authentication" \
  --metadata reason="Secure and scalable"

# Search for related decisions
copal memory search --query "authentication" --type decision

# Update a decision
copal memory update <id> --content "Use JWT and OAuth2"

# Create a follow-up decision (supersedes old one)
copal memory supersede <id> --type decision --content "Switch to OAuth2"

# View all decisions
copal memory list --type decision

# View memory statistics
copal memory summary
```

## MCP Hook System

The MCP hook system injects tool-specific guidance into stage prompts based on the tools declared in `.copal/mcp-available.json`.

### Configuration Example

`.copal/hooks/hooks.yaml`:

```yaml
- id: context7-analysis
  stage: analysis
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.analysis.md

- id: active-file-implement
  stage: implement
  all_mcp: ["active-file", "file-tree"]
  inject:
    - mcp/active-file/usage.implement.md
```

Hook blocks are located under `.copal/hooks/mcp/` and contain stage-specific usage instructions.

## Customizing Your Project

After initialization, customize your project:

1. Edit `AGENTS.md` so the "Project Customisation" section points to real documents
2. Populate `UserAgents.md` with project-specific norms and link to any additional docs in the repo
3. (Optional) Mirror `.copal/global/knowledge-base/` to override selected templates with project content
4. Store reusable prompts or playbooks anywhere in the repo and link them from `UserAgents.md`

### Agent Loading Order

When an assistant starts working on the repo it should read, in order:

1. Root `AGENTS.md`
2. `.copal/global/knowledge-base` templates
3. `UserAgents.md`
4. Any docs linked from `UserAgents.md`

This ensures shared templates load first, followed by project-specific overrides.

## Project Structure

```
CoPal/
├── copal_cli/              # CLI main code
│   ├── cli.py              # CLI entry point
│   ├── init.py             # Template installer
│   ├── stages/             # Stage command implementations
│   │   ├── analyze.py
│   │   ├── spec.py
│   │   ├── plan.py
│   │   ├── implement.py
│   │   ├── review.py
│   │   └── commit.py
│   ├── system/             # System utilities
│   │   ├── prompt_builder.py  # Prompt generator
│   │   ├── mcp.py             # MCP helpers
│   │   ├── status.py          # Status utilities
│   │   └── resume.py          # Resume utilities
│   ├── skills/             # Skill management
│   │   ├── registry.py        # Skill registry
│   │   ├── scaffold.py        # Scaffold generation
│   │   ├── executor.py        # Skill executor
│   │   └── sandbox/           # Sandbox environment
│   ├── memory/             # Memory layer
│   │   ├── models.py          # Data models
│   │   ├── networkx_store.py  # Storage backend
│   │   └── cli_commands.py    # CLI commands
│   └── templates/          # Base templates and skill scaffolds
├── docs/                   # Usage guides and design notes
│   ├── USAGE.md           # English usage guide
│   ├── USAGE_CN.md        # Chinese usage guide
│   ├── HOOKS.md           # MCP hooks documentation
│   ├── DEVELOPMENT.md     # Development guide
│   └── CHANGELOG.md       # Changelog
├── examples/               # Sample customisation layout
├── tests/                  # Pytest test suites
└── pyproject.toml          # Package metadata
```

## Development

### Prerequisites

- Python 3.9 or higher
- pip or another Python package manager

### Development Setup

```bash
# Clone the repository
git clone https://github.com/royisme/CoPal.git
cd CoPal

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage report
pytest --cov=copal_cli --cov-report=html

# Validate knowledge base files
copal validate --target .copal/global
```

### Code Quality

- Use type hints with Python 3.9+
- Follow existing code style
- Add tests to cover new features
- Run the test suite with `pytest`
- Use `copal validate` to ensure template front matter stays consistent

## Configuration Options

### Memory Layer Configuration

Configure the memory layer in `.copal/memory-config.json`:

```json
{
  "backend": "networkx",
  "auto_capture": true,
  "scope_strategy": "workflow_run"
}
```

- `backend`: Storage backend (currently supports `networkx`)
- `auto_capture`: Whether to automatically capture memory for each stage
- `scope_strategy`: Memory scope strategy (`workflow_run` or `global`)

## FAQ

### How do I update templates?

Pull the latest CoPal repository and rerun `copal init --force` to refresh shared templates.

### How do I add custom roles?

Create a `docs/agents/knowledge-base/roles/` directory in your project, add your role documents, and link from `UserAgents.md`.

### How do I share skills?

1. Create the skill and commit to version control
2. Run `copal skill registry build` to generate registry
3. Team members can discover via `copal skill search` and execute with `copal skill exec`

### Where is memory data stored?

By default, memory is stored in SQLite database and graph files under `.copal/memory/` directory.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please open an issue to discuss significant changes before submitting, and ensure all tests pass.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Memory layer design inspired by [mem-layer](https://github.com/codebasehq/mem-layer) project
- Thanks to all contributors and users for their support

## Contact

- Issue Tracker: [GitHub Issues](https://github.com/royisme/CoPal/issues)
- Documentation: [docs/](./docs/)

## Additional Resources

- [English Usage Guide](./docs/USAGE.md)
- [Chinese Usage Guide](./docs/USAGE_CN.md)
- [MCP Hooks Documentation](./docs/HOOKS.md)
- [Development Guide](./docs/DEVELOPMENT.md)
- [Changelog](./docs/CHANGELOG.md)
