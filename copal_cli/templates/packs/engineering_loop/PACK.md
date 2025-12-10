# Engineering Loop Pack

> **Router**: This is the central hub for the Engineering Loop workflow.

## 1. Principles

- **Phase-Driven**: Work in distinct phases (Plan -> Work -> Review).
- **Artifact-Centric**: Every phase produces verifiable artifacts (JSON/Markdown).
- **Progressive**: Read only what you need for the current phase.

## 2. Modes & Workflows

Choose the workflow that matches your current goal:

| Goal                   | Workflow                      | Output Artifact                  |
| :--------------------- | :---------------------------- | :------------------------------- |
| **New Task / Feature** | [Plan](workflows/plan.md)     | `.copal/artifacts/plan.json`     |
| **Active Development** | [Work](workflows/work.md)     | `.copal/artifacts/test_plan.md`  |
| **Code Review**        | [Review](workflows/review.md) | `.copal/artifacts/findings.json` |
| **Wrap Up**            | [Codify](workflows/codify.md) | Documentation updates            |

## 3. Reference Material

- [Conventions](references/conventions.md)
- [Tech Stack](references/tech_stack.md)
