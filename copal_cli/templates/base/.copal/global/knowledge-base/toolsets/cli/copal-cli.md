---
id: copal-cli
origin: copal
type: cli-guide
owner: automation-guild
enforcement: baseline
updated: 2025-11-03
---

# CoPal CLI Guide

## Core Commands

```bash
copal init --target .                    # Install templates
copal validate --target .copal/global    # Validate front matter metadata
copal analyze|spec|plan|implement|review|commit   # Run workflow stages
copal mcp ls                             # List available MCP tools
copal status                             # Summarise prompts and artifacts
copal resume                             # Show the latest generated prompt
```

## Skill Commands

```bash
copal skill registry build --skills-root .copal/skills
copal skill registry list --skills-root .copal/skills [--lang python]
copal skill search --skills-root .copal/skills --query lint [--lang python]
copal skill scaffold example/hello-world --skills-root .copal/skills
copal skill exec --skills-root .copal/skills --skill example/hello-world [--sandbox]
```

- `--skills-root <dir>` – Directory containing skill folders (`skill.json`, `prelude.md`, entrypoints).
- `--sandbox` – Required when executing a skill that declares `"requires_sandbox": true`.

## Prelude Expectations

`prelude.md` should include:

1. Task background and skill identifier.
2. Inputs, environment variables, and external resources.
3. Expected outputs (files, logs, artifact paths).
4. Execution notes from the last run and owner.
5. Reproduction command, including `--sandbox` and any `--args` passed to the skill.

Commit `prelude.md` alongside the skill so future users can safely reuse it.

## Sandbox Recommendations

| Mode    | Description                        | Typical usage                    |
| ------- | ---------------------------------- | -------------------------------- |
| `replay`| Read-only, no writes               | Dry-runs, auditing skill steps   |
| `reuse` | Reuse an isolated environment      | Iterative execution (default)    |
| `fresh` | New environment each invocation    | Sensitive or side-effect-heavy tasks |

Always execute a skill with a sandbox mode equal to or stricter than the one documented in its metadata.

## Auditing and Logs

- CoPal can store execution logs under `.copal/logs/`; include relevant snippets in reviews or PRs.
- Ensure the Git workspace is clean before scaffolding or executing skills to avoid committing temporary files.
- Archive important outputs (under `usage/` or similar) when handing off to reviewers.

## Troubleshooting

- **Registry missing** – Run `copal skill registry build` to regenerate `registry.json`.
- **Sandbox mismatch** – Re-run the skill with `--sandbox` if the metadata requires it.
- **Prelude incomplete** – Regenerate using `copal skill scaffold ... --skills-root <dir> --force` and fill in project-specific details.
