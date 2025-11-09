<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or major performance/security work
- Appears ambiguous and you need the authoritative specification before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Specification format and conventions
- Project structure and guidelines

Keep this managed block so `openspec update` can refresh the instructions.

<!-- OPENSPEC:END -->

# CoPal Workflow – Agent Handbook

> This document walks AI coding agents through the CoPal workflow so that every stage is executed in the correct order.

## Workflow Overview

CoPal splits the lifecycle into six stages. Each stage is triggered by a CLI command that generates a prompt file for the assistant to follow:

1. **Analyze** – Understand the task and gather context
2. **Spec** – Draft a precise task specification
3. **Plan** – Produce an actionable implementation plan
4. **Implement** – Generate patch notes and change summaries
5. **Review** – Evaluate quality and prepare PR content
6. **Commit** – Record workflow metadata and close the loop

## Detailed Stages

### 1. Analyze

**Command**
```bash
copal analyze --title "<title>" --goals "<goals>" --constraints "<constraints>"
```

**Agent duties**
1. Read `.copal/runtime/analysis.prompt.md`.
2. Follow the prompt to understand the task and highlight unknowns.
3. Save the report to `.copal/artifacts/analysis.md`.

**Deliverable**
- Summary of the problem
- Information gaps to investigate
- Questions to clarify with stakeholders
- Relevant background context

**Next step**: `copal spec`

---

### 2. Spec

**Command**
```bash
copal spec
```

**Agent duties**
1. Read `.copal/runtime/spec.prompt.md`.
2. Convert the analysis into a formal specification.
3. Save the spec to `.copal/artifacts/task_spec.md`.

**Deliverable**
- Scope
- Out-of-scope items
- Interfaces/data contracts
- Acceptance criteria and success metrics

**Next step**: `copal plan`

---

### 3. Plan

**Command**
```bash
copal plan
```

**Agent duties**
1. Read `.copal/runtime/plan.prompt.md`.
2. Break the specification into executable steps.
3. Save the plan to `.copal/artifacts/plan.md`.

**Deliverable**
- Ordered implementation steps
- File and dependency list
- Risk assessment and mitigations
- Rollback ideas if something fails

**MCP enhancement**
- When the `context7` MCP is available the prompt adds documentation discovery guidance.

**Next step**: `copal implement`

---

### 4. Implement

**Command**
```bash
copal implement
```

**Agent duties**
1. Read `.copal/runtime/implement.prompt.md`.
2. Produce patch notes and testing guidance based on the plan.
3. Save notes to `.copal/artifacts/patch_notes.md`.

**Deliverable**
- Files touched and rationale
- Summary of code changes
- Recommended tests and coverage notes
- Documentation follow-ups

---

### 5. Review

**Command**
```bash
copal review
```

**Agent duties**
1. Read `.copal/runtime/review.prompt.md`.
2. Audit the patch, risks, and compliance.
3. Save the review to `.copal/artifacts/review_report.md` and draft PR copy to `.copal/artifacts/pr_draft.md`.

**Deliverable**
- Quality findings and blockers
- Test results or retest recommendations
- PR summary draft
- Release or rollback considerations

**Next step**: `copal commit`

---

### 6. Commit

**Command**
```bash
copal commit [--task-id <task-id>]
```

**Deliverable**
- `.copal/artifacts/commit.json` containing task metadata, timestamps, and generated artifacts.

**Outcome**
- Workflow is complete. Start a new task with `copal analyze`.

---

## System Commands

### MCP tooling

```bash
copal mcp ls
```

Shows the contents of `.copal/mcp-available.json` so you know which Model Context Protocol tools are ready to use.

### Status snapshot

```bash
copal status
```

Displays:
- Available MCP tools
- Generated prompt files in `.copal/runtime/`
- Artifacts collected in `.copal/artifacts/`
- Suggested next command based on missing artifacts

### Resume workflow

```bash
copal resume
```

Lists the latest stage prompt so that the agent can pick up where the workflow stopped.

---

## MCP Integration

CoPal supports Model Context Protocol hooks that conditionally inject tool guidance into prompts.

### Configure MCP

Create `.copal/mcp-available.json` in the project root:

```json
["context7", "active-file", "file-tree"]
```

### Built-in behavior

- **context7** – Adds documentation lookup tips to the Analyze and Plan stages.
- **active-file + file-tree** – Adds navigation guidance to the Implement stage.

---

## Quick Start Example

```bash
# 1. Initialise CoPal (once per repository)
copal init

# 2. Optional: declare MCP tools
echo '["context7", "active-file", "file-tree"]' > .copal/mcp-available.json

# 3. Start a new task
copal analyze --title "Add user authentication" --goals "Implement JWT login" --constraints "Zero new runtime deps"

# 4. Have the agent read .copal/runtime/analysis.prompt.md and produce analysis.md

# 5. Continue the remaining stages
copal spec
copal plan
copal implement
copal review
copal commit

# 6. Inspect status at any time
copal status
```

---

## Global Guardrails

1. **Consistent language** – Follow the user's requested language. Default to English when not specified.
2. **Plan first** – Use `update_plan` to track multi-step work before implementing.
3. **Command safety** – Respect the approval and sandbox policies of the active CLI.
4. **Traceable logs** – Capture command output or reference CLI usage logs for audit trails.
5. **Knowledge upkeep** – When guidance is missing, update `UserAgents.md` or related project docs.

---

## Project Customisation

After initialisation, populate `UserAgents.md` with project-specific guidance:
- Code structure and tech stack
- Key commands (build, test, deploy)
- Security policies and approval flows
- Links to additional documentation

> Keep shared templates in the CoPal repository. Maintain project-specific guidance in your project repo.
