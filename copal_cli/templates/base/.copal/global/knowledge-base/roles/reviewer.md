---
id: role-reviewer
origin: copal
type: role
owner: qa-guild
updated: 2025-11-03
---

# Reviewer Playbook

## Required Reading

- `../core/principles.md`
- `../core/environment.md`
- Corresponding CLI guides (based on the tooling used during implementation)
- `.copal/artifacts/analysis.md`, `.copal/artifacts/task_spec.md`, `.copal/artifacts/plan.md`, `.copal/artifacts/patch_notes.md`

## Kick-off Steps

1. Check `retrospectives/` for outstanding risks or follow-up actions.
2. Gather implementation logs (Copilot `/usage`, Codex `logs`, Claude Code `/logs`, etc.).
3. Prepare to re-run critical commands (tests, lint, builds) to validate results.

## Guidance

- Compare the delivered work against the Definition of Done and the planner's requirements.
- Verify that CLI sessions respected approval and sandbox policies.
- Aggregate findings from code, docs, and logs into actionable feedback.
- Update project guidance (e.g., `UserAgents.md`) when policies need adjustment.

## Deliverable

- Review report or issue list saved to `.copal/artifacts/review_report.md`.
- Updated test or validation results.
- Release prerequisites or rollback strategies when applicable.
- Updated task status (approved, needs changes, blocked) and PR draft in `.copal/artifacts/pr_draft.md`.

## Checklist

- [ ] Critical validation commands re-run and passing.
- [ ] Issues logged with owners and next steps.
- [ ] Project guidance updated if new policies are required.
- [ ] Logs and approval records archived.
