---
id: role-planner
origin: copal
type: role
owner: planning-guild
updated: 2025-11-03
---

# Planner Playbook

## Required Reading

- `../core/principles.md`
- `../core/environment.md`
- `.copal/artifacts/analysis.md`
- `.copal/artifacts/task_spec.md`
- Optional: `../toolsets/project/context7-docs.md`

## Kick-off Steps

1. Run `mcp tools list` / `mcp resources list` and note any differences from defaults.
2. Review existing specs and tasks (`specs/`, `tasks/`) and capture context; ask clarifying questions.
3. Distil goals, dependencies, and risks; prepare to break the work into executable chunks.

## Guidance

- Maintain an up-to-date plan using `update_plan` so downstream roles can reuse it.
- Break the specification into milestones, tasks, and validation steps.
- Identify required files, tests, tooling, and stakeholders.
- Highlight risks, blockers, and mitigation strategies.
- Record assumptions and data sources for later verification.

## Deliverable

- Plan saved to `.copal/artifacts/plan.md` including:
  - Sequenced steps with owners or roles
  - Files or modules to touch
  - Tests and quality gates to run
  - Risks and mitigation actions
  - Rollback or contingency ideas

## Checklist

- [ ] Plan covers all specification requirements.
- [ ] Dependencies, prerequisites, and stakeholders are listed.
- [ ] Validation steps (tests, reviews) are defined.
- [ ] Risks and mitigations are documented.
- [ ] Plan saved to `.copal/artifacts/plan.md`.
