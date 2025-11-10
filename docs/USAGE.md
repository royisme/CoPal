# CoPal Usage Guide

This guide provides detailed instructions on how to install, configure, and use CoPal to manage AI coding assistant workflows.

## Table of Contents

- [Installation](#installation)
- [Initialization](#initialization)
- [Customizing Your Project](#customizing-your-project)
- [Agent Loading Order](#agent-loading-order)
- [Workflow Commands](#workflow-commands)
- [Skill Management](#skill-management)
- [Memory Management](#memory-management)
- [MCP Configuration](#mcp-configuration)
- [Updating Templates](#updating-templates)
- [Best Practices](#best-practices)

## Installation

The CLI currently ships as a source package. Install it locally with editable mode so updates are reflected immediately:

```bash
# Clone from GitHub
git clone https://github.com/royisme/CoPal.git
cd CoPal

# Basic installation
pip install -e .

# Or install with development dependencies (includes testing tools)
pip install -e ".[dev]"
```

CoPal requires Python 3.9 or newer.

### Verify Installation

```bash
# Check if CLI is available
copal --help

# View version information
copal --version
```

## Initialization

Run the init command from the root of the target repository:

```bash
copal init --target .
```

### Options

- `--target` – Destination directory (default: current working directory)
- `--force` – Overwrite existing files if they already exist
- `--dry-run` – Show which files would be created without writing to disk
- `--verbose` – Enable verbose logging output

### What Gets Created

The command creates:
- `AGENTS.md` – Root navigation guide providing entry point for AI assistants
- `UserAgents.md` – Placeholder for project-specific guidance
- `.copal/` – Directory containing:
  - `global/knowledge-base/` – Shared knowledge base templates
  - `hooks/` – MCP hook configurations
  - `mcp-available.json` – Available MCP tools declaration
  - `runtime/` – Runtime-generated prompts (created automatically)
  - `artifacts/` – Workflow artifact storage (created automatically)

### Important Notes

Treat `.copal/` as read-only unless you deliberately extend the templates. Re-run `copal init --force` to sync updates from CoPal.

## Customizing Your Project

### 1. Edit Root Navigation

Edit `AGENTS.md` so the "Project Customisation" section points to real documents:

```markdown
## Project Customization

Please read the following project-specific documents:

- [Project Overview](./docs/overview.md)
- [Architecture Design](./docs/architecture.md)
- [Coding Standards](./docs/coding-standards.md)
```

### 2. Populate Project-Specific Guidance

Populate `UserAgents.md` with project-specific norms and conventions:

```markdown
# User Agent Guidance

## Project Structure

This project uses a modular architecture...

## Development Workflow

1. Create feature branch from main
2. Implement feature and add tests
3. Run linters and test suite
4. Submit PR for review

## Tech Stack

- Backend: Python 3.9+ with FastAPI
- Database: PostgreSQL 14+
- Testing: pytest + pytest-cov
```

And link to any additional docs in the repo.

### 3. Override Knowledge Base Templates (Optional)

To override shared templates:

1. Create mirror path, e.g., `docs/agents/knowledge-base/roles/`
2. Copy and modify the templates you need to customize
3. Link to these documents from `UserAgents.md`

For example, to override the implementer role:

```bash
mkdir -p docs/agents/knowledge-base/roles
cp .copal/global/knowledge-base/roles/implementer.md \
   docs/agents/knowledge-base/roles/implementer.md
# Edit docs/agents/knowledge-base/roles/implementer.md
```

Then add to `UserAgents.md`:

```markdown
## Custom Roles

- [Implementer Role](./docs/agents/knowledge-base/roles/implementer.md)
```

### 4. Store Reusable Prompts

Store reusable prompts or playbooks anywhere in the repo:

```
docs/
├── agents/
│   ├── prompts/
│   │   ├── code-review.md
│   │   └── testing-strategy.md
│   └── workflows/
│       └── feature-development.md
```

Link them from `UserAgents.md`:

```markdown
## Workflow Guides

- [Feature Development Process](./docs/agents/workflows/feature-development.md)
- [Code Review Standards](./docs/agents/prompts/code-review.md)
- [Testing Strategy](./docs/agents/prompts/testing-strategy.md)
```

## Agent Loading Order

When an assistant starts working on the repo it should read, in order:

1. **Root `AGENTS.md`** - Provides overall navigation and structure
2. **`.copal/global/knowledge-base` templates** - Loads shared roles and workflows
3. **`UserAgents.md`** - Loads project-specific guidance and overrides
4. **Any docs linked from `UserAgents.md`** - Detailed project documentation

This ensures shared templates load first, followed by project-specific overrides.

## Workflow Commands

CoPal provides six main workflow stages. Each stage generates prompts and expects specific artifacts.

### 1. Analyze Stage

Understand the task and gather context.

```bash
copal analyze --title "Add user authentication" \
               --goals "Implement JWT-based authentication system" \
               --constraints "Must be compatible with existing user database"
```

**Output:**
- `.copal/runtime/analysis.prompt.md` – Analysis prompt
- Expected artifact: `.copal/artifacts/analysis.md` – Analysis results

**Prompt includes:**
- Task metadata (title, goals, constraints)
- Analyst role guidance
- MCP tool usage hints (if context7 configured)

### 2. Spec Stage

Write a formal task specification.

```bash
copal spec
```

**Output:**
- `.copal/runtime/spec.prompt.md` – Specification prompt
- Expected artifact: `.copal/artifacts/spec.md` – Task specification

**Prompt includes:**
- Specifier role guidance
- Previous analysis results
- Specification writing best practices

### 3. Plan Stage

Produce an executable implementation plan.

```bash
copal plan
```

**Output:**
- `.copal/runtime/plan.prompt.md` – Planning prompt
- Expected artifact: `.copal/artifacts/plan.md` – Implementation plan

**Prompt includes:**
- Planner role guidance
- Specification and analysis results
- MCP tool usage hints (if context7 configured)
- Plan writing templates

### 4. Implement Stage

Execute the plan and record changes.

```bash
copal implement
```

**Output:**
- `.copal/runtime/implement.prompt.md` – Implementation prompt
- Expected artifact: `.copal/artifacts/patch-notes.md` – Change descriptions

**Prompt includes:**
- Implementer role guidance
- Detailed implementation plan
- MCP tool usage hints (if active-file and file-tree configured)
- Code change guidance

### 5. Review Stage

Assess quality and draft PR notes.

```bash
copal review
```

**Output:**
- `.copal/runtime/review.prompt.md` – Review prompt
- Expected artifact: `.copal/artifacts/review.md` – Review results

**Prompt includes:**
- Reviewer role guidance
- Implemented change descriptions
- Quality checklist
- PR preparation guidance

### 6. Commit Stage

Record workflow metadata.

```bash
copal commit
```

**Output:**
- `.copal/runtime/commit.prompt.md` – Commit prompt
- Expected artifact: `.copal/artifacts/commit-metadata.json` – Workflow metadata

**Prompt includes:**
- Commit guidance
- Workflow completion checklist
- Metadata collection templates

### Status and Resume

```bash
# Check workflow status
copal status

# Resume interrupted workflow (shows most recent prompt)
copal resume
```

## Skill Management

Skills are reusable automation modules stored in `.copal/skills/` (or a custom root).

### Create Skill Scaffold

```bash
# Create Python skill
copal skill scaffold my-skill \
  --skills-root .copal/skills \
  --lang python \
  --description "Automated unit test generation"

# Create Bash skill
copal skill scaffold deploy-script \
  --lang bash \
  --description "Automated deployment script"
```

**Creates:**
```
.copal/skills/my-skill/
├── skill.json           # Metadata (ID, language, description, etc.)
├── prelude.md          # Usage instructions and requirements
├── entrypoint.log      # Execution log
├── scripts/            # Scripts directory
├── tests/              # Tests directory
└── examples/           # Examples directory
```

### Build Skill Registry

Scan skills and generate registry:

```bash
copal skill registry build --skills-root .copal/skills
```

Generates `.copal/skills/registry.json` with an index of all skills.

### List Skills

```bash
# List all skills
copal skill registry list --skills-root .copal/skills

# Filter by language
copal skill registry list --skills-root .copal/skills --lang python
```

### Search Skills

```bash
# Fuzzy search
copal skill search --skills-root .copal/skills --query "testing"

# Search by language
copal skill search --skills-root .copal/skills \
  --query "deployment" \
  --lang bash
```

### Execute Skills

```bash
# Execute skill
copal skill exec --skills-root .copal/skills --skill my-skill

# Execute in sandbox (if skill requires)
copal skill exec --skills-root .copal/skills \
  --skill my-skill \
  --sandbox
```

### Skill Lifecycle

1. **Create** - Use `copal skill scaffold` to create scaffold
2. **Develop** - Implement scripts, tests, and documentation
3. **Register** - Run `copal skill registry build`
4. **Discover** - Team members use `copal skill search` to find
5. **Execute** - Run with `copal skill exec`
6. **Share** - Commit to version control for team reuse

### Python API Usage

For richer template support, use the Python API:

```python
from copal_cli.skills import scaffold_skill

scaffold_skill(
    name="advanced-skill",
    skills_root=".copal/skills",
    lang="python",
    description="Advanced automation skill",
    force=False
)
```

## Memory Management

The memory layer persists decisions, experiences, and notes across workflow runs.

### Memory Types

- `decision` - Technical decisions and choices
- `preference` - Team preferences and conventions
- `experience` - Lessons learned and insights
- `plan` - Plans and strategies
- `note` - General notes and observations

### Add Memory

```bash
# Record a decision
copal memory add \
  --type decision \
  --content "Use PostgreSQL as primary database" \
  --metadata reason="High performance and reliability" \
  --metadata impact="high"

# Record a preference
copal memory add \
  --type preference \
  --content "Use Black for Python code formatting" \
  --metadata scope="project-wide"

# Record an experience
copal memory add \
  --type experience \
  --content "Redis connection pool size should match worker processes" \
  --metadata severity="important"
```

### Search Memory

```bash
# Keyword search
copal memory search --query "database"

# Search by type
copal memory search --query "authentication" --type decision

# Search preferences
copal memory search --type preference
```

### View Memory Details

```bash
# View full record
copal memory show <memory-id>
```

Output includes:
- Content and metadata
- Created and updated timestamps
- Relationships (if any)

### Update Memory

```bash
# Update content
copal memory update <memory-id> \
  --content "Use PostgreSQL 14+ as primary database"

# Update metadata
copal memory update <memory-id> \
  --metadata version="14.5" \
  --metadata updated_reason="Version upgrade"
```

### Supersede Memory

Create new memory with SUPERSEDES relationship to old one:

```bash
copal memory supersede <old-memory-id> \
  --type decision \
  --content "Migrate to MongoDB for better flexibility" \
  --metadata reason="Need more flexible schema"
```

### Delete Memory

```bash
# Delete memory and all its relationships
copal memory delete <memory-id>
```

### List Memories

```bash
# List all memories
copal memory list

# List by type
copal memory list --type decision
```

### Memory Statistics

```bash
# View memory statistics
copal memory summary
```

Output includes:
- Count of memories by type
- Total memory count
- Relationship statistics

### Configure Memory Layer

Configure in `.copal/memory-config.json`:

```json
{
  "backend": "networkx",
  "auto_capture": true,
  "scope_strategy": "workflow_run"
}
```

**Configuration options:**
- `backend` - Storage backend (currently supports `networkx`)
- `auto_capture` - Whether to automatically capture memory for each stage
- `scope_strategy` - Memory scope strategy:
  - `workflow_run` - Independent scope per workflow run
  - `global` - Global scope

## MCP Configuration

The Model Context Protocol (MCP) hook system injects tool-specific guidance into stage prompts.

### Declare Available Tools

Declare in `.copal/mcp-available.json`:

```json
["context7", "active-file", "file-tree"]
```

### View Available Tools

```bash
copal mcp ls
```

### Configure Hook Rules

Configure hook rules in `.copal/hooks/hooks.yaml`:

```yaml
# context7 usage guidance for analysis stage
- id: context7-analysis
  stage: analysis
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.analysis.md

# context7 usage guidance for plan stage
- id: context7-plan
  stage: plan
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.plan.md

# active-file and file-tree usage guidance for implement stage
- id: active-file-implement
  stage: implement
  all_mcp: ["active-file", "file-tree"]
  inject:
    - mcp/active-file/usage.implement.md
```

### Rule Syntax

**Basic structure:**

```yaml
- id: unique-rule-id       # Unique rule ID
  stage: stage-name        # analysis/spec/plan/implement/review/commit
  any_mcp: [list]          # OR logic; triggers if any MCP present
  all_mcp: [list]          # AND logic; triggers only if all MCPs present
  inject:                  # List of hook blocks to inject
    - path/to/block.md
```

**Conditional logic:**
- `any_mcp` - Fires when at least one tool in the list is available
- `all_mcp` - Fires only when every tool in the list is available

### Create Custom Hooks

1. **Declare the MCP** - Add to `.copal/mcp-available.json`
2. **Create a hook block** - Create Markdown file under `.copal/hooks/mcp/<tool>/usage.<stage>.md`
3. **Add routing rule** - Reference the block from `.copal/hooks/hooks.yaml`
4. **Test** - Run the relevant stage command and verify the prompt includes new guidance

### Built-in Hook Examples

**context7 - Analysis stage:**
- Path: `.copal/hooks/mcp/context7/usage.analysis.md`
- When: Analysis stage and context7 is available
- Content: How to research libraries, gather background knowledge, capture findings in analysis artifact

**context7 - Plan stage:**
- Path: `.copal/hooks/mcp/context7/usage.plan.md`
- When: Plan stage and context7 is available
- Content: Confirm APIs, design solutions, document dependencies and versions

**active-file + file-tree - Implement stage:**
- Path: `.copal/hooks/mcp/active-file/usage.implement.md`
- When: Both active-file and file-tree are available during implement stage
- Content: Locate files, apply changes, write tests, capture patch notes

## Updating Templates

### Sync Latest Templates

```bash
# Pull latest CoPal repository
cd /path/to/CoPal
git pull origin main

# Reinstall
pip install -e .

# Refresh templates in your project
cd /path/to/your-project
copal init --force
```

### Important Notes

- Keep shared templates generic; store project-specific details in your own docs
- Maintain a changelog for any custom knowledge base updates so teammates know what changed
- Backup custom content before updating

## Best Practices

### 1. Workflow Management

- **Execute stages in order** - Follow analyze → spec → plan → implement → review → commit sequence
- **Capture artifacts** - Each stage creates artifacts in `.copal/artifacts/`
- **Use status commands** - Regularly run `copal status` to check progress
- **Resume interrupted work** - Use `copal resume` to continue

### 2. Knowledge Base Management

- **Minimize overrides** - Only override templates that truly need customization
- **Version control** - Commit custom knowledge base files to version control
- **Document links** - Clearly link all custom docs from `UserAgents.md`
- **Sync regularly** - Periodically sync latest shared templates from CoPal

### 3. Skill Development

- **Document requirements** - Detail runtime requirements in `prelude.md`
- **Include tests** - Add tests for skills to ensure reliability
- **Use sandbox** - Mark `requires_sandbox: true` for sensitive operations
- **Version skills** - Include version information in `skill.json`
- **Share registry** - Commit `registry.json` for team discovery

### 4. Memory Usage

- **Record promptly** - Record decisions as they're made
- **Add context** - Use metadata to provide additional context
- **Review regularly** - Periodically review and update memories
- **Use types** - Use appropriate memory types for different information
- **Build relationships** - Use supersede to create chains of decision evolution

### 5. MCP Integration

- **Declare tools** - Declare all available tools in `.copal/mcp-available.json`
- **Stage-specific guidance** - Create specific usage guidance for different stages
- **Test hooks** - Verify hooks trigger at the correct stages
- **Keep concise** - Hook content should be concise and to the point

### 6. Team Collaboration

- **Share configuration** - Commit `.copal/` configuration to version control
- **Unify conventions** - Document team conventions in `UserAgents.md`
- **Share skills** - Share and reuse team skills
- **Share memory** - Use global scope for important shared decisions

## Validation

Use `copal validate` to ensure knowledge base files have correct front matter:

```bash
# Validate default knowledge base
copal validate --target .copal/global

# Validate custom knowledge base
copal validate --target docs/agents/knowledge-base

# Use custom pattern
copal validate --target .copal/global --pattern "**/*.md"
```

## Troubleshooting

### Issue: init command fails

**Solution:**
- Check that target directory exists and is writable
- Use `--verbose` to see detailed error information
- Use `--dry-run` to preview actions

### Issue: MCP tools not found

**Solution:**
- Check `.copal/mcp-available.json` exists
- Verify JSON format is correct
- Use `copal mcp ls` to verify configuration

### Issue: Memory search returns no results

**Solution:**
- Check memories are in current scope
- Try different search keywords
- Use `copal memory list` to see all memories

### Issue: Skill execution fails

**Solution:**
- Check `skill.json` format is correct
- Verify requirements in `prelude.md` are met
- Use `--sandbox` if skill marked as requiring sandbox
- Check log files for error details

## Getting Help

- **Command help** - Use `copal <command> --help` for command help
- **Documentation** - See other documentation in [docs/](../docs/) directory
- **Issues** - Submit issues at [GitHub Issues](https://github.com/royisme/CoPal/issues)
- **Examples** - See examples in [examples/](../examples/) directory

## Next Steps

- Read [HOOKS.md](./HOOKS.md) for MCP hook system details
- Read [DEVELOPMENT.md](./DEVELOPMENT.md) for development and contribution guide
- See [CHANGELOG.md](./CHANGELOG.md) for latest updates
- `copal memory list` / `copal memory summary` – list or summarise memories for the current project scope.

Memories are scoped per repository by default. Configuration lives in `.copal/config.json` under the `memory` key:

```json
{
  "memory": {
    "backend": "networkx",
    "database": ".copal/memory.db",
    "auto_capture": true,
    "scope": {"default": "my-project"}
  }
}
```

- `backend` – currently only `networkx` is supported and stores data locally with SQLite persistence.
- `database` – relative or absolute path for the SQLite file.
- `auto_capture` – when `true`, each workflow stage automatically logs a lightweight note about prompt generation.
- `scope.default` – overrides the default scope identifier when working across multiple projects.

The auto-capture hook records a short note every time `copal analyze/spec/plan/implement/review/commit` runs. Agents can expand on these entries (for example, replace the placeholder content with artefact summaries) using `copal memory update`.

## 7. Skill Lifecycle Tips

1. Scaffold new skills under a dedicated directory (for example `.copal/skills/internal/`).
2. Record ownership, tags, and sandbox requirements in `skill.json`.
3. Capture the intended usage in `prelude.md` so downstream agents know how to reuse the skill.
4. Build the registry and commit both `registry.json` and the skill directory so other contributors can discover it.
5. When executing, respect the declared sandbox requirement; rerun with `--sandbox` if the skill is marked as sensitive.

## 8. Future Enhancements

Planned improvements include:
- Publishing the package to PyPI
- Additional maintenance commands (e.g., `copal update`, `copal doctor`)
- Schema validation for knowledge base files
- Integrations with additional AI CLIs as they become available
