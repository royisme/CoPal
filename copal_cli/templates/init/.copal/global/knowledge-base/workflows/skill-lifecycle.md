---
id: workflow-skill-lifecycle
origin: copal
type: workflow
owner: automation-guild
updated: 2025-11-03
---

# Workflow: Skill Lifecycle

## Goal

Create, register, and reuse automation skills so teams can share repeatable workflows.

## Inputs

- Skill idea with description and expected value
- Access to `.copal/skills/` or project skill directory
- Registry configuration (`skills.json` or `registry.json`)

## Steps

1. **Discover demand** – Confirm the skill solves a recurring problem and aligns with project policy.
2. **Scaffold** – Use `copal skill scaffold <name>` or `scaffold_skill()` to generate boilerplate.
3. **Implement** – Fill in scripts, prompts, tests, and guardrails. Document usage in `prelude.md`.
4. **Validate** – Run automated and manual tests in the declared sandbox mode.
5. **Register** – Update `skills.json` or run `copal skill registry build` to publish metadata.
6. **Share** – Commit the skill directory, registry, and usage logs. Link it from `UserAgents.md` if relevant.
7. **Iterate** – Track feedback, update versions, and maintain change logs in `CHANGELOG.md`.

## Outputs

- Skill directory with scripts, tests, and documentation
- Registry entry discoverable via `copal skill search`
- Usage notes (prelude, logs) for downstream teams

## Quality Checks

- [ ] Skill metadata includes owner, tags, sandbox mode, and clear description.
- [ ] Prelude explains inputs, outputs, dependencies, and safety requirements.
- [ ] Tests cover critical behaviour or guard against misuse.
- [ ] Registry index rebuilt and committed.
