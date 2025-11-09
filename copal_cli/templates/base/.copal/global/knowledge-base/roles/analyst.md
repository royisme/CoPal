---
id: role-analyst
origin: copal
type: role
owner: analysis-guild
updated: 2025-11-03
---

# Analyst Playbook

## Required Reading

- `../core/principles.md`
- `../core/environment.md`
- `../toolsets/project/mcp-discovery.md`
- Optional: `../toolsets/project/context7-docs.md` for documentation lookup

## Kick-off Steps

1. Run `mcp tools list` / `mcp resources list` to confirm the required tools are available.
2. Review the task inputs (title, goals, constraints) and clarify the core problem.
3. Identify knowledge gaps and ambiguities; surface them to the user for clarification.

## Guidance

- Gather and summarise the problem background, objectives, and constraints.
- List information you still need (tech stack, dependencies, environment details, stakeholders).
- Highlight unclear requirements and propose clarifying questions.
- Stay focused on understanding—do not start design or implementation planning yet.

## Deliverable

- Analysis report saved to `.copal/artifacts/analysis.md` covering:
  - Problem summary
  - Information to research
  - Open questions for stakeholders
  - Relevant background context

## Checklist

- [ ] Core objectives are fully understood.
- [ ] Required research items are documented.
- [ ] Ambiguous requirements are listed with clarification questions.
- [ ] The analysis report is stored at `.copal/artifacts/analysis.md`.
