# CoPal Usage Guide

## 1. Installation

The CLI currently ships as a source package. Install it locally with editable mode so updates are reflected immediately:

```bash
pip install -e ./CoPal
# or if CoPal lives as a submodule
pip install -e tools/copal
```

CoPal requires Python 3.9 or newer.

## 2. Initialisation

Run the init command from the root of the target repository:

```bash
copal init --target .
```

Options:
- `--target` – Destination directory (default: current working directory)
- `--force` – Overwrite existing files if they already exist
- `--dry-run` – Show which files would be created without writing to disk

The command creates:
- `AGENTS.md` – Root navigation guide
- `UserAgents.md` – Placeholder for project-specific guidance
- `.copal/` – Shared knowledge base, hooks, and MCP metadata

Treat `.copal/` as read-only unless you deliberately extend the templates. Re-run `copal init --force` to sync updates from CoPal.

## 3. Customising the Project

1. Edit `AGENTS.md` so the "Project Customisation" section points to real documents.
2. Populate `UserAgents.md` with project-specific norms and link to any additional docs in the repo.
3. (Optional) Mirror `.copal/global/knowledge-base/` to override selected templates with project content.
4. Store reusable prompts or playbooks anywhere in the repo and link them from `UserAgents.md`.

## 4. Agent Loading Order

When an assistant starts working on the repo it should read, in order:

1. Root `AGENTS.md`
2. `.copal/global/knowledge-base` templates
3. `UserAgents.md`
4. Any docs linked from `UserAgents.md`

This ensures shared templates load first, followed by project-specific overrides.

## 5. Updating Templates

- Pull the latest CoPal repository (or update the submodule) and rerun `copal init --force` to refresh shared templates.
- Keep shared templates generic; store project-specific details in your own docs.
- Maintain a changelog for any custom knowledge base updates so teammates know what changed.

## 6. CLI Reference

### Validation

```bash
copal validate --target .copal/global --pattern "**/*.md"
```

Validates the YAML front matter metadata in knowledge base files.

### Workflow Commands

Run the six-stage loop (`analyze`, `spec`, `plan`, `implement`, `review`, `commit`) to generate prompts and capture artifacts. Each command writes `.copal/runtime/<stage>.prompt.md` for the agent to follow and expects artifacts in `.copal/artifacts/`.

### Status Utilities

- `copal mcp ls` – Print available MCP tools declared in `.copal/mcp-available.json`
- `copal status` – Summarise prompts, artifacts, and suggested next command
- `copal resume` – Show the most recent prompt so the workflow can continue

### Skill Management

The `copal skill` namespace manages reusable automation skills stored in `.copal/skills/` (or a custom directory):

- `copal skill registry build --skills-root <dir>` – Scan skills and write `registry.json`
- `copal skill registry list --skills-root <dir> [--lang python]` – List registered skills
- `copal skill search --skills-root <dir> --query <text> [--lang python]` – Fuzzy search skill metadata
- `copal skill scaffold <name> [--skills-root <dir>] [--lang python] [--description text]` – Create a lightweight scaffold with `skill.json`, `prelude.md`, and an entrypoint log file
- `copal skill exec --skills-root <dir> --skill <name> [--sandbox]` – Stream the skill's entrypoint log to stdout (honours `requires_sandbox` in metadata)

For richer scaffolds, use the Python API `copal_cli.skills.scaffold_skill` which renders Jinja templates and updates `skills.json` manifests.

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
