---
id: role-specifier
origin: copal
type: role
owner: specification-guild
updated: 2025-11-03
---

# Specifier Playbook

## Required Reading

- `../core/principles.md`
- `../core/environment.md`
- `.copal/artifacts/analysis.md`
- `../toolsets/project/mcp-discovery.md`
- Optional: `../toolsets/project/context7-docs.md`

## Kick-off Steps

1. Review the analysis report to understand context and research items.
2. Run `mcp tools list` to ensure supporting tools are available.
3. Perform additional technical investigation as needed.

## Guidance

- Convert ambiguous requests into clear, verifiable specifications.
- Define scope and explicitly list what is out of scope.
- Document interfaces, data structures, and workflow expectations.
- Capture acceptance criteria and success metrics.
- Avoid implementation details—leave planning to the next stage.

## Deliverable

- Specification saved to `.copal/artifacts/task_spec.md` including:
  - Scope
  - Out-of-scope items
  - Interface/data definitions
  - Acceptance criteria
  - Success metrics and constraints

## Checklist

- [ ] Scope and boundaries are clearly defined.
- [ ] Acceptance criteria are testable and measurable.
- [ ] Interfaces and data contracts are documented.
- [ ] Out-of-scope items are listed to prevent scope creep.
- [ ] Specification is saved to `.copal/artifacts/task_spec.md`.
