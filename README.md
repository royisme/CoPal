# CoPal

**Command-line Orchestration Playbook for AI Coders**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[English](#english) | [中文](#中文)

---

## English

### Overview

CoPal (Command-line Orchestration Playbook for AI coders) is a universal collaboration framework designed for terminal-based AI coding assistants such as OpenAI Codex CLI, Anthropic Claude Code, GitHub Copilot CLI, and similar tools.

**Key Features:**

- **Universal Knowledge Framework**: Standardized templates for roles, workflows, and tool guidance with YAML front matter for fast LLM retrieval
- **CLI Initialization Tool**: `copal init` command to bootstrap projects with standard templates
- **Customization Overlay**: Projects maintain their specific requirements through `UserAgents.md` and related documentation
- **MCP/Plugin Integration**: Built-in support for Model Context Protocol and CLI plugin discovery
- **Zero Dependencies**: Pure Python standard library implementation

> **Current Status**: This repository is in prototype phase, focusing on directory design and initialization workflow. It can be extended to a full Python package or npm tool as needed.

### Why CoPal?

When working with AI coding assistants, teams often face challenges:

- **Inconsistent Workflows**: Different team members use different prompts and processes
- **Knowledge Fragmentation**: Best practices scattered across chat histories and docs
- **Tool Discovery**: Hard to know what MCP tools or CLI plugins are available
- **Role Confusion**: Unclear when to plan vs. implement vs. review
- **Context Loss**: AI assistants restart without project-specific guidance

CoPal solves these by providing:

1. **Standardized Templates**: Battle-tested patterns that work across multiple AI tools
2. **Clear Role Separation**: Distinct playbooks for Planner, Implementer, and Reviewer roles
3. **Discoverable Tools**: Structured guidance for CLI tools and MCP integration
4. **Safety First**: Built-in guardrails and approval process requirements
5. **Project Customization**: Easy override mechanism for project-specific needs

### Architecture

#### Directory Structure

```
CoPal/
├── README.md                       # This file
├── LICENSE                         # MIT License
├── docs/
│   └── USAGE.md                    # Detailed usage guide
├── examples/
│   └── project-customization/      # Customization examples
├── pyproject.toml                  # Package configuration
└── copal_cli/                      # Main package
    ├── __init__.py
    ├── cli.py                      # CLI entry point
    ├── init.py                     # Init command implementation
    └── templates/base/             # Template resources
        ├── AGENTS.md               # Root index template
        ├── UserAgents.md           # Project customization placeholder
        └── .copal/global/          # Universal knowledge base
            └── knowledge-base/
                ├── core/           # Global principles & environment
                ├── roles/          # Planner, Implementer, Reviewer playbooks
                ├── workflows/      # Cross-role processes
                └── toolsets/       # CLI guides and tool discovery
```

#### Knowledge Base Organization

The `.copal/global/knowledge-base/` provides reusable templates:

**Core Modules** (`core/`)
- `principles.md` - 5 fundamental principles for AI collaboration
- `environment.md` - Environment constraints and requirements
- `information-architecture.md` - Metadata structure and organization

**Role Playbooks** (`roles/`)
- `planner.md` - Requirements analysis, task breakdown, risk assessment
- `implementer.md` - Code execution, testing, and validation
- `reviewer.md` - Quality assurance and release preparation

**Workflows** (`workflows/`)
- `plan-to-implement.md` - Convert requirements to executable tasks
- `implementation-loop.md` - Single development iteration cycle
- `review-release.md` - QA and deployment process

**Toolsets** (`toolsets/`)
- `cli/` - CLI-specific guides (Codex CLI, Claude Code, Copilot CLI)
- `project/` - MCP discovery and documentation tools
- `agent/` - Example utilities (guardrail scripts)

### Installation

#### Development Installation

1. Clone or add as submodule:
   ```bash
   git clone https://github.com/yourusername/CoPal.git
   # or
   git submodule add https://github.com/yourusername/CoPal.git
   ```

2. Install in development mode:
   ```bash
   pip install -e ./CoPal
   ```

#### Usage

**Initialize a project**:
```bash
cd /path/to/your/project
copal init --target .
```

**Preview changes without writing files (dry-run)**:
```bash
copal init --target . --dry-run
```

**Force overwrite existing files**:
```bash
copal init --target . --force
```

**Validate YAML front matter in knowledge base**:
```bash
copal validate --target .copal/global
```

**Show detailed logging**:
```bash
copal init --target . --verbose
copal validate --target .copal/global --verbose
```

#### What Gets Installed

Running `copal init` creates:

- `AGENTS.md` - Navigation index for AI assistants
- `UserAgents.md` - Project-specific customization template
- `.copal/global/` - Universal knowledge base directory

### Quick Start Guide

1. **Install CoPal** in your development environment
2. **Run initialization** in your project root
3. **Customize** `UserAgents.md` with project-specific information:
   - Project structure and tech stack
   - Role-specific requirements
   - Common commands (build, test, deploy)
   - Security policies
4. **Guide AI assistants** to read `.copal/global/` templates first, then `UserAgents.md`

> **Tip**: The `.copal/` directory is maintained by CoPal and rarely needs manual editing. Keep project-specific content in `UserAgents.md` and files it references.

### Customization

Projects can customize by:

1. **Editing UserAgents.md**: Add project-specific sections
2. **Creating project docs**: Link from UserAgents.md to detailed guides
3. **Extending knowledge base**: Add files that override global templates
4. **Defining prompts**: Create reusable prompt templates

See `examples/project-customization/` for detailed examples.

### Integration

CoPal integrates with:

- **OpenSpec**: Spec-driven development workflows
- **MCP (Model Context Protocol)**: Tool and resource discovery
- **Claude Code**: Plugin management and Git workflows
- **Other AI CLIs**: Codex CLI, Copilot CLI with dedicated guides
- **Version Control**: Git commit, PR, and review processes

### Design Principles

1. **Template-First**: Provide proven patterns before custom solutions
2. **Overlay Pattern**: Customize by addition, not modification
3. **Documentation as Code**: Version-controlled, searchable guidance
4. **Agent-Friendly**: YAML metadata enables fast LLM navigation
5. **Safety-Conscious**: Built-in approval and audit requirements

### Roadmap

Completed features:
- ✅ `copal init` command with template installation
- ✅ `--dry-run` option for previewing changes
- ✅ `--verbose` flag for detailed logging
- ✅ `copal validate` command for YAML front matter validation
- ✅ Comprehensive test suite with pytest
- ✅ Full docstring documentation

Future enhancements planned:
- [ ] Publish to PyPI (`pip install copal-cli`)
- [ ] Add `copal update` command to sync templates
- [ ] Add `copal doctor` health check command
- [ ] Support more CLI tools (Cursor CLI, Gemini CLI)
- [ ] Multi-language documentation support
- [ ] Add YAML library support for complex structures

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

For major changes, please open an issue first to discuss proposed changes.

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Support

- **Documentation**: See [docs/USAGE.md](docs/USAGE.md)
- **Examples**: Check `examples/` directory
- **Issues**: Report bugs or request features via GitHub Issues

### Acknowledgments

CoPal is designed to work seamlessly with:
- [Anthropic Claude Code](https://claude.ai/code)
- [OpenAI Codex](https://openai.com/blog/openai-codex)
- [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.org)

---

## 中文

### 概述

CoPal（Command-line Orchestration Playbook for AI coders）是一套面向终端型 AI 编码工具（如 OpenAI Codex CLI、Anthropic Claude Code、GitHub Copilot CLI 等）的通用协作指引框架。

**核心特性：**

- **通用知识骨架**：角色、工作流、工具指引的统一模板，使用 YAML front matter 便于 LLM 快速检索
- **CLI 初始化工具**：`copal init` 命令将模板复制到目标仓库，快速启动项目
- **自定义覆盖机制**：项目通过 `UserAgents.md` 及相关文档维护专属需求
- **MCP/插件整合**：内置对模型上下文协议（MCP）和 CLI 插件发现的支持
- **零依赖设计**：纯 Python 标准库实现，无外部依赖

> **当前状态**：本仓库处于原型阶段，核心是目录设计与初始化流程。可根据需要扩展为完整的 Python 包或 npm 工具。

### 为什么选择 CoPal？

使用 AI 编码助手时，团队常面临以下挑战：

- **工作流不一致**：不同成员使用不同的提示词和流程
- **知识碎片化**：最佳实践散落在聊天记录和文档中
- **工具发现困难**：难以了解可用的 MCP 工具或 CLI 插件
- **角色混淆**：不清楚何时规划、实施或审查
- **上下文丢失**：AI 助手重启后缺少项目特定指引

CoPal 通过以下方式解决这些问题：

1. **标准化模板**：经过实战检验的模式，适用于多种 AI 工具
2. **清晰的角色分离**：为规划者、实施者和审查者提供不同的操作手册
3. **可发现的工具**：为 CLI 工具和 MCP 集成提供结构化指引
4. **安全优先**：内置防护机制和审批流程要求
5. **项目定制化**：轻松覆盖项目特定需求

### 架构设计

#### 目录结构

```
CoPal/
├── README.md                       # 本文件
├── LICENSE                         # MIT 许可证
├── docs/
│   └── USAGE.md                    # 详细使用说明
├── examples/
│   └── project-customization/      # 自定义示例
├── pyproject.toml                  # 包配置
└── copal_cli/                      # 主包
    ├── __init__.py
    ├── cli.py                      # CLI 入口
    ├── init.py                     # 初始化命令实现
    └── templates/base/             # 模板资源
        ├── AGENTS.md               # 根索引模板
        ├── UserAgents.md           # 项目自定义占位
        └── .copal/global/          # 通用知识库
            └── knowledge-base/
                ├── core/           # 全局原则与环境
                ├── roles/          # 规划者、实施者、审查者手册
                ├── workflows/      # 跨角色流程
                └── toolsets/       # CLI 指南和工具发现
```

#### 知识库组织

`.copal/global/knowledge-base/` 提供可复用模板：

**核心模块** (`core/`)
- `principles.md` - AI 协作的 5 个基本原则
- `environment.md` - 环境约束和要求
- `information-architecture.md` - 元数据结构和组织

**角色手册** (`roles/`)
- `planner.md` - 需求分析、任务拆解、风险评估
- `implementer.md` - 代码执行、测试和验证
- `reviewer.md` - 质量保证和发布准备

**工作流** (`workflows/`)
- `plan-to-implement.md` - 将需求转换为可执行任务
- `implementation-loop.md` - 单次开发迭代循环
- `review-release.md` - QA 和部署流程

**工具集** (`toolsets/`)
- `cli/` - CLI 专用指南（Codex CLI、Claude Code、Copilot CLI）
- `project/` - MCP 发现和文档工具
- `agent/` - 示例实用程序（防护脚本）

### 安装

#### 开发安装

1. 克隆或添加为子模块：
   ```bash
   git clone https://github.com/yourusername/CoPal.git
   # 或
   git submodule add https://github.com/yourusername/CoPal.git
   ```

2. 以开发模式安装：
   ```bash
   pip install -e ./CoPal
   ```

#### 使用方法

**初始化项目**：
```bash
cd /path/to/your/project
copal init --target .
```

**预览变更而不实际写入文件（试运行）**：
```bash
copal init --target . --dry-run
```

**强制覆盖现有文件**：
```bash
copal init --target . --force
```

**验证知识库中的 YAML front matter**：
```bash
copal validate --target .copal/global
```

**显示详细日志**：
```bash
copal init --target . --verbose
copal validate --target .copal/global --verbose
```

#### 安装内容

运行 `copal init` 会创建：

- `AGENTS.md` - AI 助手的导航索引
- `UserAgents.md` - 项目专用自定义模板
- `.copal/global/` - 通用知识库目录

### 快速入门指南

1. **安装 CoPal** 到开发环境
2. **运行初始化** 在项目根目录
3. **自定义** `UserAgents.md` 添加项目特定信息：
   - 项目结构和技术栈
   - 角色特定要求
   - 常用命令（构建、测试、部署）
   - 安全策略
4. **引导 AI 助手** 先读取 `.copal/global/` 模板，然后读取 `UserAgents.md`

> **提示**：`.copal/` 目录由 CoPal 维护，很少需要手动编辑。将项目专属内容保存在 `UserAgents.md` 及其引用的文件中。

### 自定义

项目可通过以下方式自定义：

1. **编辑 UserAgents.md**：添加项目专属章节
2. **创建项目文档**：从 UserAgents.md 链接到详细指南
3. **扩展知识库**：添加覆盖全局模板的文件
4. **定义提示词**：创建可复用的提示词模板

详细示例请参见 `examples/project-customization/`。

### 集成

CoPal 可集成：

- **OpenSpec**：规范驱动的开发工作流
- **MCP（模型上下文协议）**：工具和资源发现
- **Claude Code**：插件管理和 Git 工作流
- **其他 AI CLI**：Codex CLI、Copilot CLI 及专用指南
- **版本控制**：Git 提交、PR 和审查流程

### 设计原则

1. **模板优先**：提供经过验证的模式，再进行定制
2. **覆盖模式**：通过添加而非修改来定制
3. **文档即代码**：版本控制、可搜索的指引
4. **AI 友好**：YAML 元数据支持 LLM 快速导航
5. **注重安全**：内置审批和审计要求

### 路线图

已完成功能：
- ✅ `copal init` 命令与模板安装
- ✅ `--dry-run` 选项用于预览变更
- ✅ `--verbose` 标志用于详细日志
- ✅ `copal validate` 命令用于 YAML front matter 验证
- ✅ 使用 pytest 的全面测试套件
- ✅ 完整的 docstring 文档

计划的未来增强：
- [ ] 发布到 PyPI (`pip install copal-cli`)
- [ ] 添加 `copal update` 命令同步模板
- [ ] 添加 `copal doctor` 健康检查命令
- [ ] 支持更多 CLI 工具（Cursor CLI、Gemini CLI）
- [ ] 多语言文档支持
- [ ] 添加 YAML 库支持复杂结构

### 贡献

欢迎贡献！请：

1. Fork 仓库
2. 创建功能分支
3. 进行更改并添加测试
4. 提交 pull request

对于重大更改，请先开 issue 讨论建议的更改。

### 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

### 支持

- **文档**：参见 [docs/USAGE.md](docs/USAGE.md)
- **示例**：查看 `examples/` 目录
- **问题**：通过 GitHub Issues 报告 bug 或请求功能

### 致谢

CoPal 设计为无缝配合以下工具：
- [Anthropic Claude Code](https://claude.ai/code)
- [OpenAI Codex](https://openai.com/blog/openai-codex)
- [GitHub Copilot CLI](https://githubnext.com/projects/copilot-cli)
- [模型上下文协议（MCP）](https://modelcontextprotocol.org)
