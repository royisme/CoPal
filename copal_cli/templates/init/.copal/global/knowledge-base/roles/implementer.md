---
id: role-implementer
origin: copal
type: role
owner: delivery-guild
updated: 2025-11-03
---

# Implementer Playbook

## Required Reading

- `../core/principles.md`
- `../core/environment.md`
- `.copal/artifacts/task_spec.md`
- `.copal/artifacts/plan.md`
- `../workflows/implementation-loop.md`

## Kick-off Steps

1. Review the plan and confirm scope, assumptions, and risks.
2. Ensure required tools and sandboxes are available.
3. Collect references (analysis, spec, plan) before editing code.

## Guidance

- Follow the plan, updating it if reality diverges—record deltas in `update_plan`.
- Work in small increments; keep commit-ready changesets.
- Record changes per file, including rationale and side effects.
- Write or update tests alongside code changes.
- Capture manual validation steps, logs, and follow-up actions.

## Deliverable

- Patch notes saved to `.copal/artifacts/patch_notes.md` covering:
  - Files modified and summary of changes
  - Tests executed and results
  - Follow-up tasks or TODOs
  - Risks or mitigations discovered during implementation

## Checklist

- [ ] Plan deviations recorded and approved if necessary.
- [ ] Code changes, tests, and documentation updates are summarised.
- [ ] Tests are executed or queued with clear instructions.
- [ ] Patch notes saved to `.copal/artifacts/patch_notes.md`.
