# Review Phase Workflow

> **Adopt Persona**: [Reviewer Agent](../prompts/reviewer.md) - Read this file to understand your role.

## Objective

Ensure code quality and alignment with the plan.

## Steps

1. **Review Code**: Check correctness, quality, security, performance.
2. **Verify Alignment**: Audit against `plan.json`.
3. **Generate Findings**: Create `.copal/artifacts/findings.json`.
4. **Create Todos**: Create `.copal/artifacts/todo.json` for any fixes.
5. **Decision**:
   - **Approved**: Proceed to Codify.
   - **Needs Changes**: Back to Work phase.
   - **Rejected**: Back to Plan phase.
