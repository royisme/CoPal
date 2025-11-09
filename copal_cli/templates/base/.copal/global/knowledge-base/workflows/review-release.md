---
id: workflow-review-release
origin: copal
type: workflow
owner: qa-guild
updated: 2025-11-03
---

# Workflow: Review and Release

## Goal

Verify that implementation results meet quality standards and prepare the change for release.

## Inputs

- `.copal/artifacts/patch_notes.md`
- `.copal/artifacts/plan.md`
- Test reports, logs, and validation artefacts
- Deployment or release checklists

## Steps

1. **Audit deliverables** – Compare patch notes against the plan and specification.
2. **Re-run validation** – Execute critical tests, lint, or build commands to confirm repeatability.
3. **Assess risk** – Evaluate failure impact, rollback strategies, and monitoring requirements.
4. **Document feedback** – Capture issues, blockers, or follow-up tasks; assign owners.
5. **Prepare release notes** – Summarise changes, risks, and testing outcomes for stakeholders.
6. **Decide status** – Approve, request changes, or block release pending further work.

## Outputs

- Review report with findings and decisions
- Updated PR draft or release notes
- Validated test results and logs archived for auditing

## Quality Checks

- [ ] All blocking issues resolved or documented with owners.
- [ ] Tests and validation steps have been re-run or acknowledged.
- [ ] Rollback plan and monitoring steps are identified if required.
- [ ] Release documentation is complete and shared.
