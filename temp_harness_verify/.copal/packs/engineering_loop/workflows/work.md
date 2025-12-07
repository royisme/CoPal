# Work Phase Workflow

## Objective

Implement the confirmed plan with high quality.

## Steps

1. **Gate Check**: Verify plan status is `confirmed`.
2. **Implement**: Execute steps in `.copal/artifacts/plan.json`.
   - Update code files.
   - Create new files.
3. **Verify**: Run `scripts/verify.sh` and fix issues.
4. **Document**: Generate `.copal/artifacts/test_plan.md` with results.
5. **Update Status**: precise `plan.json` as `completed`.
6. **Handoff**: Proceed to Review phase.
