---
name: Copal Engineering Loop
description: Use when implementing features with structured TDD workflow, task tracking via todo.json, and engineering best practices.
---

# Copal Engineering Loop Skill

This skill integrates with the **Copal CLI** to provide structured, state-driven development workflows.

## When to Use This Skill

Activate this skill when:

- User asks to implement a feature or fix a bug
- User wants structured development workflow (Plan → Research → Work → Review)
- Project has `.copal/` directory with `todo.json`

## Available Commands

### Task Management

```bash
# Get and start the next pending task
copal next [--worktree]

# Mark a task as completed
copal done <task_id>

# Show project status, task summary, and recent session history
copal status

# Validate project state before starting work
copal validate --pre-task

# Search project memory
copal memory search --query "search term"
```

## Workflow

### 1. Session Initialization (Get Bearings)

- Run `copal status` to see active tasks.
- Run `copal next` to get context and see **recent session history**.
- If you need more context, use `copal memory search`.
- Run `copal validate --pre-task` to ensure:
  - Git working directory is clean
  - Baseline tests are passing

### 2. Execution Loop

- Run `copal next` (or `copal next --worktree` for isolation) to claim a task.
- **Worktree**: If using worktree, `cd` into the new directory.
- **TDD**: Write tests -> Fail -> Implement -> Pass.
- **Commit**: Make atomic commits for the task.

### 3. Completion & Handover

- Run `copal done <id>`. This will:
  - Mark task as done in `todo.json`
  - **Save a session summary** to memory automatically
- If using worktree, merge changes back to main branch.

## Task States

| Status        | Meaning                   |
| ------------- | ------------------------- |
| `todo`        | Not started               |
| `in_progress` | Currently being worked on |
| `done`        | Completed                 |
| `blocked`     | Cannot proceed            |

## Best Practices

1.  **Trust the Harness**: Rely on `copal validate` and memory chains.
2.  **One Feature, One Branch**: Use `copal next --worktree` for complex tasks.
3.  **Validation Gates**: Never start a task on a dirty or broken state.
4.  **Self-Correction**: If `copal done` fails, fix the issue and retry.

## File Locations

- Task list: `.copal/artifacts/todo.json`
- Memories: `.copal/memory.sqlite` (managed via CLI)
