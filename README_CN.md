# CoPal

**Agent Harness 配置与状态管理工具**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[English](./README.md) | 简体中文

## 概述

CoPal 是一个**被动的 Agent Harness 工具**——它为 AI Coding Agents（如 **Claude Code**、**Codex CLI**、**Gemini CLI**）提供标准化的配置和状态管理接口。

> **CoPal 不是 Agent，也不主动控制任何流程。**  
> 真正的主体是 Claude Code 等 Coding Agent。它们在工作时会读取 CoPal 生成的配置文件（`AGENTS.md`、`SKILL.md`），并在需要时调用 `copal` CLI 命令来管理任务状态。

### 工作模式

```
┌─────────────────────────────────────────────────────────────┐
│  用户 → Claude Code (主体) → 调用 copal CLI → 读取/更新状态  │
└─────────────────────────────────────────────────────────────┘
```

1. **Init-time**: CoPal 一次性生成配置文件（`AGENTS.md`、`SKILL.md`、workflows）
2. **Run-time**: Claude Code 等 Agent 读取这些配置，并在执行过程中调用 `copal` 命令
3. **CoPal 始终是被动的**：它只响应 Agent 的命令调用，不主动介入

### 设计灵感

设计灵感源自 [Anthropic 的长时运行 Agent 研究](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)——当 Agent 需要跨多个上下文窗口工作时，需要一个机制来：

- 保存会话摘要（Session Memory）
- 管理任务状态（todo.json）
- 验证环境状态（Pre-task validation）

CoPal 就是这个机制的 CLI 实现，**供 Agent 调用**。

## 核心功能

| 功能              | CoPal 提供了什么           | Agent 如何使用                                          |
| ----------------- | -------------------------- | ------------------------------------------------------- |
| **会话记忆**      | 存储/检索会话摘要的接口    | Agent 调用 `copal done` 保存摘要，`copal next` 读取历史 |
| **任务状态**      | `todo.json` 及状态管理命令 | Agent 调用 `copal next` / `copal done` 更新状态         |
| **环境验证**      | Pre-task 检查命令          | Agent 调用 `copal validate --pre-task` 确认环境         |
| **Worktree 管理** | Git worktree 封装          | Agent 调用 `copal next --worktree` 创建隔离环境         |
| **配置导出**      | 生成各工具格式的配置       | 用户运行 `copal export claude` 生成 `.claude/` 配置     |

## 快速开始

### 1. 安装

```bash
# 使用 uv (推荐)
uv tool install copal-cli

# 或 pip
pip install copal-cli
```

### 2. 初始化项目

```bash
copal init
```

这会生成：

- `AGENTS.md` - Agent 的入口指南
- `.copal/packs/engineering_loop/skill/SKILL.md` - Claude Code Skill 定义
- `.copal/manifest.yaml` - 项目配置

### 3. 导出到 Agent 工具

```bash
# 为 Claude Code 导出
copal export claude
# 生成 .claude/skills/copal-engineering_loop/SKILL.md
```

### 4. 使用 Agent

现在当你启动 Claude Code 时：

1. **Claude Code 读取 `AGENTS.md`** 了解项目规则
2. **Claude Code 加载 `SKILL.md`** 了解如何使用 CoPal
3. **用户下达任务**: "实现用户登录功能"
4. **Claude Code 执行**:
   ```bash
   # Claude Code 调用这些命令
   copal status              # 查看状态
   copal next                # 领取任务，查看历史上下文
   copal validate --pre-task # 验证环境
   # ... 实现代码 ...
   copal done 1              # 完成任务，保存会话摘要
   ```

## Agent 可调用的命令

以下命令设计供 Coding Agent 在执行过程中调用：

### 任务生命周期

```bash
# 查看项目状态
copal status

# 领取下一个任务 (显示最近会话历史)
copal next

# 领取任务并创建隔离 worktree
copal next --worktree

# 完成任务 (自动保存会话摘要到 Memory)
copal done <task_id>
```

### 环境验证

```bash
# Pre-task 验证: 检查 Git 状态 + 运行测试
copal validate --pre-task

# 验证配置
copal validate

# 验证 Agent 生成的工件
copal validate --artifacts
```

### 记忆管理

```bash
# 搜索历史记忆
copal memory search --query "authentication"

# 添加记忆
copal memory add --type decision --content "使用 JWT 进行认证"

# 列出所有记忆
copal memory list
```

### Worktree 管理

```bash
# 创建新 worktree
copal worktree new feature-login

# 列出 worktrees
copal worktree list

# 删除 worktree
copal worktree remove feature-login
```

## 用户命令

以下命令主要供用户（而非 Agent）使用：

```bash
# 初始化项目
copal init

# 导出到 Agent 工具
copal export claude|codex|gemini
```

## 目录结构

```
Project/
├── AGENTS.md                    # Agent 入口指南
├── .copal/
│   ├── manifest.yaml            # CoPal 配置
│   ├── artifacts/
│   │   └── todo.json            # 任务列表 (Agent 调用命令更新)
│   ├── memory/                  # Memory 存储 (Agent 调用命令读写)
│   └── packs/
│       └── engineering_loop/
│           └── skill/SKILL.md   # Claude Code Skill (Agent 读取)
```

## 设计原则

1. **CoPal 是被动的** - 只响应 Agent 的命令调用，不主动控制流程
2. **Agent 是主体** - Claude Code 等 Agent 负责决策和执行
3. **文件系统是通信媒介** - 通过 `.copal/` 目录传递状态和配置
4. **增量进展** - 每个会话完成小任务，保存摘要供下个会话使用

## 许可证

MIT License
