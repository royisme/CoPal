# CoPal

**Agent Harness Configuration & State Management Tool**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[简体中文](./README_CN.md) | English

## Overview

CoPal is a **passive Agent Harness tool**—providing standardized configuration and state management interfaces for AI Coding Agents (like **Claude Code**, **Codex CLI**, **Gemini CLI**).

> **CoPal is NOT an Agent and does NOT actively control any workflow.**  
> The real actors are Coding Agents like Claude Code. They read CoPal-generated config files (`AGENTS.md`, `SKILL.md`) and call `copal` CLI commands to manage task state.

### How It Works

```
┌───────────────────────────────────────────────────────────────┐
│  User → Claude Code (Actor) → Calls copal CLI → Updates State │
└───────────────────────────────────────────────────────────────┘
```

1. **Init-time**: CoPal generates configuration files (`AGENTS.md`, `SKILL.md`, workflows) once
2. **Run-time**: Agents like Claude Code read these configs and call `copal` commands during execution
3. **CoPal is always passive**: It only responds to Agent command calls, never initiates

### Design Inspiration

Inspired by [Anthropic's research on long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)—when Agents work across multiple context windows, they need mechanisms to:

- Save session summaries (Session Memory)
- Manage task state (todo.json)
- Validate environment state (Pre-task validation)

CoPal implements these mechanisms as a CLI **for Agents to call**.

## Key Features

| Feature                    | What CoPal Provides                           | How Agents Use It                                              |
| -------------------------- | --------------------------------------------- | -------------------------------------------------------------- |
| **Session Memory**         | Interface to store/retrieve session summaries | Agent calls `copal done` to save, `copal next` to read history |
| **Task State**             | `todo.json` and state management commands     | Agent calls `copal next` / `copal done` to update state        |
| **Environment Validation** | Pre-task check command                        | Agent calls `copal validate --pre-task` to verify environment  |
| **Worktree Management**    | Git worktree wrapper                          | Agent calls `copal next --worktree` for isolation              |
| **Config Export**          | Generate tool-specific configs                | User runs `copal export claude` to generate `.claude/` config  |

## Quick Start

### 1. Install

```bash
# Using uv (recommended)
uv tool install copal-cli

# Or pip
pip install copal-cli
```

### 2. Initialize Project

```bash
copal init
```

This generates:

- `AGENTS.md` - Entry guide for Agents
- `.copal/packs/engineering_loop/skill/SKILL.md` - Claude Code Skill definition
- `.copal/manifest.yaml` - Project configuration

### 3. Export to Agent Tool

```bash
# Export for Claude Code
copal export claude
# Generates .claude/skills/copal-engineering_loop/SKILL.md
```

### 4. Use with Agent

Now when you start Claude Code:

1. **Claude Code reads `AGENTS.md`** to understand project rules
2. **Claude Code loads `SKILL.md`** to learn how to use CoPal
3. **User gives task**: "Implement user login feature"
4. **Claude Code executes**:
   ```bash
   # Claude Code calls these commands
   copal status              # Check status
   copal next                # Claim task, view historical context
   copal validate --pre-task # Verify environment
   # ... implement code ...
   copal done 1              # Complete task, save session summary
   ```

## Commands for Agents

These commands are designed for Coding Agents to call during execution:

### Task Lifecycle

```bash
# Check project status
copal status

# Claim next task (shows recent session history)
copal next

# Claim task and create isolated worktree
copal next --worktree

# Complete task (auto-saves session summary to Memory)
copal done <task_id>
```

### Environment Validation

```bash
# Pre-task validation: Check Git status + run tests
copal validate --pre-task

# Validate configuration
copal validate

# Validate Agent-generated artifacts
copal validate --artifacts
```

### Memory Management

```bash
# Search historical memories
copal memory search --query "authentication"

# Add memory
copal memory add --type decision --content "Use JWT for auth"

# List all memories
copal memory list
```

### Worktree Management

```bash
# Create new worktree
copal worktree new feature-login

# List worktrees
copal worktree list

# Remove worktree
copal worktree remove feature-login
```

## Commands for Users

These commands are primarily for users (not Agents):

```bash
# Initialize project
copal init

# Export to Agent tool
copal export claude|codex|gemini
```

## Directory Structure

```
Project/
├── AGENTS.md                    # Entry guide for Agents
├── .copal/
│   ├── manifest.yaml            # CoPal configuration
│   ├── artifacts/
│   │   └── todo.json            # Task list (updated via Agent commands)
│   ├── memory/                  # Memory storage (read/written via Agent commands)
│   └── packs/
│       └── engineering_loop/
│           └── skill/SKILL.md   # Claude Code Skill (read by Agent)
```

## Design Principles

1. **CoPal is Passive** - Only responds to Agent command calls, never controls flow
2. **Agent is the Actor** - Claude Code etc. makes decisions and executes
3. **Filesystem as Communication** - State and config passed through `.copal/` directory
4. **Incremental Progress** - Each session completes small tasks, saves summary for next session

## License

MIT License
