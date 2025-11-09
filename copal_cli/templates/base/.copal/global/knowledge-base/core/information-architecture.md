---
id: core-information-architecture
origin: copal
type: information-architecture
owner: knowledge-team
updated: 2025-11-03
---

# CoPal Information Architecture Blueprint

## 0. Goals

- Provide a reusable collaboration framework for tools like Codex, Claude Code, and Copilot CLI.
- Separate shared templates from project-specific guidance so teams can extend CoPal after `copal init`.
- Use front matter metadata to make documents discoverable by LLMs and scripts.

## 1. Directory Layout

```
.copal/
├── global/                # Default templates (this directory)
│   └── knowledge-base/    # Roles, workflows, toolsets, principles
└── hooks/                 # MCP routing rules and injected guidance
UserAgents.md              # Entry point for project-specific notes
```

Projects can override any document by recreating the same path in their repository and linking it from `UserAgents.md`.

## 2. Module Overview

- `core/` – Global principles, environment guidance, and maintenance notes
- `roles/` – Playbooks covering responsibilities, kick-off steps, deliverables, and checklists
- `workflows/` – Cross-role processes (plan-to-implement, implementation loop, review-release, skill lifecycle)
- `toolsets/cli/` – CLI usage guides
- `toolsets/project/` – Platform-neutral discovery and documentation helpers
- `toolsets/agent/` – Guardrail and helper scripts
- `logs/`, `retrospectives/` – Reserved for guardrail output and improvement logs

## 3. Override Strategy

- After running `copal init`, list custom docs in `UserAgents.md`.
- Override any default by creating a file with the same path (e.g., `docs/agents/roles/implementer.md`) and linking it from `UserAgents.md`.
- Agents should load docs in order: `AGENTS.md` → `.copal/global/...` → `UserAgents.md` and its references.

## 4. Recommended Structure

| Document type | Suggested content |
| ------------- | ----------------- |
| `AGENTS.md` (project root) | 1. Summary of constraints<br>2. Keyword → module mapping<br>3. Getting-started flow<br>4. Link to `UserAgents.md` |
| `UserAgents.md` | Project overview, role extensions, commands, safety policies, linked docs |
| `roles/*.md` | Front matter + required reading + kick-off steps + guidance + deliverables + checklist |
| `workflows/*.md` | Goal, inputs, steps, outputs, quality checks |
| `toolsets/cli/*.md` | Installation/login, core commands, safety configuration, common issues |

## 5. Init Workflow

1. Run `copal init` in the target repository.
2. Templates are copied to `.copal/global/`, and `AGENTS.md` plus `UserAgents.md` are created.
3. Project maintainers extend `UserAgents.md` and create additional documents as needed.
4. Future updates to shared templates come from the CoPal repository; project-specific docs remain under the project's control.

## 6. Maintenance Tips

- Keep shared templates generic; avoid hard-coding project-specific technologies.
- When introducing new workflows or CLI guides, update this blueprint first and then extend supporting docs.
- Use validation scripts (e.g., `copal validate`) to ensure front matter metadata stays consistent.
