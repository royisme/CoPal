# CoPal

**Command-line Orchestration Playbook for AI Coders（AI编程助手的命令行编排工作流）**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

[English](./README.md) | 简体中文

## 概述

CoPal 是一个为使用终端型 AI 编程助手（如 OpenAI Codex CLI、Anthropic Claude Code、GitHub Copilot CLI 等）的团队提供的可重用工作流、知识库和技能管理工具包。本项目包含：

- **六阶段工作流编排**（分析 → 规范 → 计划 → 实现 → 审查 → 提交）
- **提示词生成**，包含阶段特定的标题、任务元数据注入和可选的 MCP 指导
- **知识库模板**，涵盖角色、工作流、工具集和全局策略（使用 YAML 前置元数据以便快速检索）
- **项目初始化**，通过 `copal init` 命令复制 AGENTS、UserAgents 和共享知识库资源
- **技能生命周期工具**（注册表构建/列表/搜索、脚手架生成、沙箱感知执行）
- **实用命令**，用于 MCP 发现、工作流状态和恢复提示
- **记忆层**，在工作流运行之间持久化决策、笔记和经验

CoPal CLI 使用 Python 标准库实现，并附带基于 pytest 的测试。所有文档和模板均提供中英文版本，方便国际团队使用。

## 核心特性

### 🔄 六阶段工作流
CoPal 提供结构化的软件开发工作流：
1. **分析（Analyze）** - 理解任务并收集上下文
2. **规范（Spec）** - 编写正式的任务规范
3. **计划（Plan）** - 制定可执行的实施计划
4. **实现（Implement）** - 执行计划并记录更改
5. **审查（Review）** - 评估质量并起草 PR 说明
6. **提交（Commit）** - 记录工作流元数据

### 📚 知识库管理
- 内置角色模板（分析师、规范员、计划员、实现者、审查者）
- 工作流指南和最佳实践
- 可自定义的项目特定知识库
- YAML 前置元数据支持快速检索

### 🛠️ 技能系统
- 可重用的自动化模块
- 技能注册表和搜索功能
- 脚手架生成工具
- 沙箱执行环境
- 技能版本控制和共享

### 🧠 记忆层
- 跨工作流运行持久化决策和经验
- 基于图的知识存储（使用 NetworkX）
- 支持决策、偏好、经验、计划和笔记
- 记忆关系和查询功能

### 🔌 MCP 集成
- 模型上下文协议（Model Context Protocol）钩子系统
- 工具特定的指导注入
- 灵活的钩子配置
- 支持 context7、active-file、file-tree 等工具

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/royisme/CoPal.git
cd CoPal

# 本地安装（开发模式）
pip install -e .

# 或安装开发依赖
pip install -e ".[dev]"
```

### 初始化项目

在您的项目根目录中初始化 CoPal：

```bash
# 在当前目录初始化 CoPal 资源
copal init --target .

# 查看将要创建的文件（不实际创建）
copal init --dry-run

# 强制覆盖现有文件
copal init --force
```

初始化后会创建以下文件和目录：
- `AGENTS.md` - 根导航指南
- `UserAgents.md` - 项目特定指导的占位符
- `.copal/` - 共享知识库、钩子和 MCP 元数据

### 配置 MCP 工具（可选）

声明可用的 MCP 工具：

```bash
cat <<'JSON' > .copal/mcp-available.json
["context7", "active-file", "file-tree"]
JSON
```

### 运行工作流

执行六阶段工作流（每个命令在 `.copal/runtime/` 中生成提示词）：

```bash
# 1. 分析阶段 - 理解任务
copal analyze --title "添加用户登录" --goals "实现 JWT 认证"

# 2. 规范阶段 - 编写规范
copal spec

# 3. 计划阶段 - 制定计划
copal plan

# 4. 实现阶段 - 执行实现
copal implement

# 5. 审查阶段 - 代码审查
copal review

# 6. 提交阶段 - 提交更改
copal commit

# 查看整体进度
copal status

# 恢复中断的工作流
copal resume
```

## CLI 命令参考

### 核心命令

| 命令 | 用途 |
| ------- | ------- |
| `copal init [--force] [--dry-run]` | 将模板（AGENTS、UserAgents、`.copal/`）复制到仓库中 |
| `copal validate --target <路径>` | 验证知识库文件的必需前置元数据 |
| `copal analyze\|spec\|plan\|implement\|review\|commit` | 为每个工作流阶段生成提示词和捕获产物 |
| `copal mcp ls` | 列出在 `.copal/mcp-available.json` 中声明的 MCP 工具 |
| `copal status` | 总结提示词、产物和建议的下一阶段 |
| `copal resume` | 显示最近的提示词以恢复工作流 |

### 技能命令

| 命令 | 用途 |
| ------- | ------- |
| `copal skill registry build --skills-root <目录>` | 扫描技能并写入 `registry.json` |
| `copal skill registry list --skills-root <目录> [--lang <语言>]` | 列出已注册的技能，可选按语言过滤 |
| `copal skill search --skills-root <目录> --query <文本> [--lang <语言>]` | 模糊搜索技能元数据 |
| `copal skill scaffold <名称> [--skills-root <目录>] [--lang <语言>]` | 创建最小的技能骨架 |
| `copal skill exec --skills-root <目录> --skill <名称> [--sandbox]` | 流式输出技能的入口日志到标准输出 |

### 记忆命令

| 命令 | 用途 |
| ------- | ------- |
| `copal memory add --type <类型> --content "..."` | 创建记忆条目 |
| `copal memory search --query <文本> [--type <类型>]` | 在活动范围内搜索 |
| `copal memory show <id>` | 检查完整记录 |
| `copal memory update <id> --content "..."` | 更新存储的内容或元数据 |
| `copal memory delete <id>` | 删除记忆及其关系 |
| `copal memory supersede <id> --type <类型> --content "..."` | 添加带有 SUPERSEDES 关系的后续记忆 |
| `copal memory list [--type <类型>]` | 列出活动范围内的所有记忆 |
| `copal memory summary` | 显示记忆统计信息 |

记忆类型包括：`decision`（决策）、`preference`（偏好）、`experience`（经验）、`plan`（计划）、`note`（笔记）

## 项目结构

```
CoPal/
├── copal_cli/              # CLI 主代码
│   ├── cli.py              # CLI 入口点
│   ├── init.py             # 模板安装器
│   ├── stages/             # 阶段命令实现
│   │   ├── analyze.py
│   │   ├── spec.py
│   │   ├── plan.py
│   │   ├── implement.py
│   │   ├── review.py
│   │   └── commit.py
│   ├── system/             # 系统工具
│   │   ├── prompt_builder.py  # 提示词生成器
│   │   ├── mcp.py             # MCP 助手
│   │   ├── status.py          # 状态工具
│   │   └── resume.py          # 恢复工具
│   ├── skills/             # 技能管理
│   │   ├── registry.py        # 技能注册表
│   │   ├── scaffold.py        # 脚手架生成
│   │   ├── executor.py        # 技能执行器
│   │   └── sandbox/           # 沙箱环境
│   ├── memory/             # 记忆层
│   │   ├── models.py          # 数据模型
│   │   ├── networkx_store.py  # 存储后端
│   │   └── cli_commands.py    # CLI 命令
│   └── templates/          # 基础模板和技能脚手架
├── docs/                   # 使用指南和设计文档
│   ├── USAGE.md           # 英文使用指南
│   ├── USAGE_CN.md        # 中文使用指南
│   ├── HOOKS.md           # MCP 钩子文档
│   ├── DEVELOPMENT.md     # 开发指南
│   └── CHANGELOG.md       # 变更日志
├── examples/               # 示例自定义布局
├── tests/                  # Pytest 测试套件
└── pyproject.toml          # 包元数据
```

## 知识库

共享知识库位于 `copal_cli/templates/base/.copal/global/knowledge-base/`，包含：

- **core/** - 全局原则、环境防护和信息架构
- **roles/** - 分析师、规范员、计划员、实现者和审查者的工作手册
- **workflows/** - 规划到实现、实现循环、审查和发布、技能生命周期的分步指南
- **toolsets/** - 常用 CLI 的快速参考指南，以及项目工具和防护脚本

项目可以通过在仓库中重新创建相同路径并从 `UserAgents.md` 链接来覆盖任何模板。

## 技能生命周期

技能是存储在 `.copal/skills/`（或自定义根目录）下的可重用自动化模块。每个技能包含 `skill.json`、`prelude.md`、脚本/测试和可选日志。典型生命周期：

1. 使用 `copal skill scaffold` 或 Python API 创建新技能脚手架
2. 实现脚本、提示词、防护措施和测试。在 `prelude.md` 中记录运行时要求
3. 构建注册表（`copal skill registry build`），以便团队成员通过 `copal skill search` 发现技能
4. 使用 `copal skill exec` 执行，如果技能元数据标记为敏感，传递 `--sandbox` 参数
5. 提交技能目录、`registry.json` 和相关日志，以便其他人安全地重用

## 记忆层使用

记忆层允许您在工作流运行之间持久化重要信息：

```bash
# 记录一个决策
copal memory add --type decision --content "使用 JWT 进行身份验证" \
  --metadata reason="安全且可扩展"

# 搜索相关决策
copal memory search --query "身份验证" --type decision

# 更新决策
copal memory update <id> --content "使用 JWT 和 OAuth2"

# 创建后续决策（取代旧的）
copal memory supersede <id> --type decision --content "改用 OAuth2"

# 查看所有决策
copal memory list --type decision

# 查看内存统计
copal memory summary
```

## MCP 钩子系统

MCP 钩子系统根据 `.copal/mcp-available.json` 中声明的工具，将工具特定的指导注入到阶段提示词中。

### 配置示例

`.copal/hooks/hooks.yaml`:

```yaml
- id: context7-analysis
  stage: analysis
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.analysis.md

- id: active-file-implement
  stage: implement
  all_mcp: ["active-file", "file-tree"]
  inject:
    - mcp/active-file/usage.implement.md
```

钩子块位于 `.copal/hooks/mcp/` 下，包含阶段特定的使用说明。

## 自定义项目

初始化后，自定义您的项目：

1. 编辑 `AGENTS.md`，使"项目自定义"部分指向实际文档
2. 在 `UserAgents.md` 中填充项目特定的规范，并链接到仓库中的任何其他文档
3. （可选）镜像 `.copal/global/knowledge-base/` 以用项目内容覆盖选定的模板
4. 在仓库的任何位置存储可重用的提示词或工作手册，并从 `UserAgents.md` 链接它们

### 代理加载顺序

当助手开始在仓库上工作时，应按顺序读取：

1. 根目录 `AGENTS.md`
2. `.copal/global/knowledge-base` 模板
3. `UserAgents.md`
4. 从 `UserAgents.md` 链接的任何文档

这确保共享模板首先加载，然后是项目特定的覆盖。

## 开发

### 前提条件

- Python 3.9 或更高版本
- pip 或其他 Python 包管理器

### 开发设置

```bash
# 克隆仓库
git clone https://github.com/royisme/CoPal.git
cd CoPal

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=copal_cli --cov-report=html

# 验证知识库文件
copal validate --target .copal/global
```

### 代码质量

- 使用 Python 3.9+ 的类型提示
- 遵循现有代码风格
- 添加测试以覆盖新功能
- 使用 `pytest` 运行测试套件
- 使用 `copal validate` 确保模板前置元数据保持一致

## 配置选项

### 记忆层配置

在 `.copal/memory-config.json` 中配置记忆层：

```json
{
  "backend": "networkx",
  "auto_capture": true,
  "scope_strategy": "workflow_run"
}
```

- `backend`: 存储后端（目前支持 `networkx`）
- `auto_capture`: 是否自动捕获每个阶段的记忆
- `scope_strategy`: 记忆作用域策略（`workflow_run` 或 `global`）

## 常见问题

### 如何更新模板？

拉取最新的 CoPal 仓库并重新运行 `copal init --force` 以刷新共享模板。

### 如何添加自定义角色？

在项目中创建 `docs/agents/knowledge-base/roles/` 目录，添加您的角色文档，并从 `UserAgents.md` 链接。

### 如何共享技能？

1. 创建技能并提交到版本控制
2. 运行 `copal skill registry build` 生成注册表
3. 团队成员可以通过 `copal skill search` 发现并使用 `copal skill exec` 执行

### 记忆数据存储在哪里？

默认情况下，记忆存储在 `.copal/memory/` 目录下的 SQLite 数据库和图文件中。

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 开启 Pull Request

在提交重大更改之前，请先开启 issue 进行讨论。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 致谢

- 记忆层设计受 [mem-layer](https://github.com/codebasehq/mem-layer) 项目启发
- 感谢所有贡献者和用户的支持

## 联系方式

- 问题反馈：[GitHub Issues](https://github.com/royisme/CoPal/issues)
- 文档：[docs/](./docs/)

## 更多资源

- [英文使用指南](./docs/USAGE.md)
- [中文使用指南](./docs/USAGE_CN.md)
- [MCP 钩子文档](./docs/HOOKS.md)
- [开发指南](./docs/DEVELOPMENT.md)
- [变更日志](./docs/CHANGELOG.md)
