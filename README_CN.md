# CoPal

**Agent Harness Configuration Tool (AI Agents 配置与编排工具)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[English](./README.md) | 简体中文

## 概述

CoPal 是一个**Agent Harness 配置生成器与校验器**。它的核心定位是为 AI 编程助手（如 **Anthropic Claude Code**、**OpenAI Codex CLI**、**Cursor** 等）提供标准化的工作环境配置（Harness）。

**CoPal 不是一个代理（Agent），而是一个为代理准备环境的工具。**

它通过 Init-time（初始化时）生成静态配置文件（`AGENTS.md`、Workflows、Prompts），让运行时（Run-time）的通用 AI Agent 能够遵循能够复用、确定性的工程流程。

## 核心功能

- **Init-time Configuration**：一次性生成标准化的 `AGENTS.md` 和 workflow 指令，避免每次对话重复 prompt。
- **Passive Orchestration**：通过文件系统（`.copal/`）向 Agent 传递上下文和约束，而非主动劫持控制流。
- **Worktree Isolation**：内置 Git Worktree 管理，为每个 AI 任务创建隔离的开发环境，保护主分支。
- **Persistent Memory**：跨会话管理项目特定的知识和状态（Memory），防止上下文丢失。
- **Artifact Validation**：提供 `copal validate` 命令，事后校验 Agent 生成的工件（JSON Plan、Todo List 等）是否符合 Schema。
- **Universal Export**：同一套配置可导出为 Claude Code 命令、Cursor Rules 或 Codex Prompts。

## 快速开始

### 1. 安装

### 1. 安装

**推荐：使用 uv**（快速、环境隔离）

```bash
# 直接从 PyPI 安装（待发布后）
uv tool install copal-cli

# 或者从源码安装
git clone https://github.com/royisme/CoPal.git
cd CoPal
uv tool install .
```

**替代方案：pip**

```bash
pip install -e .
```

### 2. 初始化项目 (Init)

在任意项目根目录下运行，生成 Harness 配置：

```bash
copal init
```

这将创建：

- `AGENTS.md`：AI Agent 的入口指南。
- `.copal/manifest.yaml`：项目配置清单。
- `.copal/packs/`：安装默认的工作流包（如 `engineering_loop`）。

### 3. 创建隔离工作区 (Worktree)

为新任务创建一个隔离的 Git Worktree，避免污染当前开发环境：

```bash
# 创建一个名为 "feature-login" 的新功能分支工作区
copal worktree new feature-login
```

### 4. 导出指令 (Export)

将配置导出为你使用的 Agent 工具可识别的格式：

```bash
# 为 Claude Code 导出指令
copal export claude
# 生成文件位于 .claude/commands/copal/*.md
```

### 5. 运行 Agent

启动你的 AI Agent（例如 Claude Code），它会自动读取 `AGENTS.md` 和导出的指令。

> **User**: "Claude, please start the task: Add generic export support to Copal CLI."

Agent 会遵循指南：

1. **Plan**: 生成计划并写入 `.copal/artifacts/plan.json`
2. **Research**: 调用工具调研代码库
3. **Work**: 实施代码变更

### 6. 管理记忆 (Memory)

**注意：此功能主要供 Agent 在运行时通过 Tool 调用，而非用户手动操作。**
Agent 可以利用 Copal 提供的记忆库来跨会话存储关键决策或上下文：

```bash
# Agent 调用此命令添加一条新的记忆
copal memory add --type concept --content "The export module uses a plugin architecture."

# Agent 调用此命令搜索记忆
copal memory search --query "export module"
```

### 7. 校验状态 (Validate)

在 Agent 工作过程中或完成后，校验工件是否符合规范：

```bash
# 校验配置和 Agent 生成的工件格式是否正确
copal validate --artifacts
```

## CLI 命令参考

| 命令                  | 用途                                                                 |
| --------------------- | -------------------------------------------------------------------- |
| `copal init`          | 初始化项目，生成 `AGENTS.md` 和 `.copal/` 目录                       |
| `copal validate`      | 校验 Manifest 和 Pack 配置。使用 `--artifacts` 校验生成产物          |
| `copal export <tool>` | 将指令导出为指定工具格式（支持 `claude`, `codex`, `gemini`）         |
| `copal status`        | 查看当前项目的 Harness 状态和 Artifacts 摘要                         |
| `copal worktree`      | 管理 Git Worktrees (`new`, `list`, `remove`)，实现任务隔离           |
| `copal memory`        | 管理项目记忆库 (`add`, `search`, `list`, `show`, `update`, `delete`) |
| `copal mcp`           | 查看 Model Context Protocol 工具配置状态                             |

## 目录结构规范

CoPal 初始化的标准结构：

```
Project/
├── AGENTS.md                # Agent 入口指南（只包含核心原则和索引）
├── .copal/
│   ├── manifest.yaml        # Copal 配置
│   ├── artifacts/           # Agent 运行时的产出物 (plan.json, findings.json...)
│   ├── memory/              # Memory 存储 (sqlite/json)
│   ├── packs/               # 安装的工作流包
│   │   └── engineering_loop/
│   │       ├── workflows/   # 具体的步骤说明 (md)
│   │       ├── prompts/     # 角色 Prompt 模板
│   │       └── schemas/     # 工件 JSON Schema
│   └── mcp-available.json   # MCP 工具注册表
```

## 贡献

欢迎贡献新的 Workflow Packs 或 Tool Adapters！

1. Fork 本仓库
2. 创建功能分支
3. 提交更改
4. 开启 Pull Request

## 许可证

MIT License
