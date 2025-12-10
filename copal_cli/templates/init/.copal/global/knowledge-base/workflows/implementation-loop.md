---
id: workflow-implementation-loop
origin: copal
type: workflow
owner: delivery-guild
updated: 2025-11-03
---

# Workflow: Implementation Loop

## Goal

Execute a single implementation iteration with tight feedback between coding, testing, and documentation.

## Inputs

- `.copal/artifacts/plan.md`
- Source files referenced in the plan
- Existing tests and documentation

## Steps

1. **Select a task** – Choose the next plan item and confirm acceptance criteria.
2. **Prepare context** – Open relevant files, tests, and documentation.
3. **Implement** – Apply changes in small commits; document rationale per file.
4. **Test** – Run automated tests and record results. Add or update tests as needed.
5. **Validate** – Perform manual checks or sanity testing when automation is insufficient.
6. **Document** – Update patch notes, READMEs, or user guides affected by the change.
7. **Review progress** – Update `update_plan` status and flag blockers or follow-ups.

## Outputs

- Updated code and tests
- Patch notes entry for the iteration
- Validation results attached to the task

## Quality Checks

- [ ] Acceptance criteria for the task are met.
- [ ] Tests covering the change pass (or failures are documented with a plan).
- [ ] Documentation reflects new behaviour.
- [ ] Risks, follow-ups, and TODOs are captured in the plan or patch notes.
