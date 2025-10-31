---
id: kb-information-architecture
origin: copal
type: blueprint
owner: copal-team
updated: 2025-10-31
---

# CoPal 信息架构蓝图

## 0. 目标

- 为 Codex / Claude Code / Copilot CLI 等工具提供可复用的协作骨架；
- 将公共模板与项目自定义内容分离，支持 init 后用户自行扩展；
- 使 LLM 能通过前置 metadata 快速定位所需指引。

## 1. 目录层次

```
.copal/
└── global/                # CoPal 提供的默认模板（本目录）
    └── knowledge-base/    # 角色、流程、工具指引等

UserAgents.md              # 项目维护的自定义指引入口
```

项目可在 `UserAgents.md` 中引用自定义文档，或在仓库其它位置创建与 `global` 同名的文件覆盖默认内容。

## 2. 模块说明

- `core/`：全局原则、运行环境与维护蓝图。
- `roles/`：通用角色 Playbook，描述职责、启动步骤、交付物与检查清单。
- `workflows/`：跨角色流程（如规划→实施、实施循环、审查发布）。
- `toolsets/cli/`：主要 CLI 工具的使用指南。
- `toolsets/project/`：与平台无关的工具发现、文档检索参考。
- `toolsets/agent/`：CoPal 自带示例脚本（如命令守卫），项目可选择使用或改写。
- `logs/`、`retrospectives/`：留给守卫或执行过程记录，便于后续改进。

## 3. 覆盖策略

- 初始化后，项目应在 `UserAgents.md` 中列出自定义文档路径；
- 若需要覆盖默认说明，可在仓库中创建与 `global` 同名的文件（例如 `docs/agents/roles/implementer.md`），并在 `UserAgents.md` 链接；
- Agent 加载顺序：`AGENTS.md` → `.copal/global/...` → `UserAgents.md`（以及其中引用的文档）。

## 4. 推荐编排

| 文档类型 | 建议结构 |
| --- | --- |
| `AGENTS.md` (项目根) | 1. 全局约束摘要<br>2. 关键词 → 模块映射<br>3. 启动流程<br>4. 指向 `UserAgents.md` 等自定义文档 |
| `UserAgents.md` | 项目概况、角色扩展、常用命令、安全策略、关联文档 |
| `roles/*.md` | Front matter + 必读模块 + 启动步骤 + 指引 + 交付物 + 检查清单 |
| `workflows/*.md` | 目标、输入、步骤、输出、质控 |
| `toolsets/cli/*.md` | 安装/登录、常用命令、安全设置、扩展、常见问题 |

## 5. Init 工作流

1. 用户在目标仓库运行 `copal init`。
2. `global/` 模板复制至 `.copal/global/`，同时生成 `AGENTS.md` 与 `UserAgents.md` 模板。
3. 项目维护者在 `UserAgents.md` 中补充自定义内容，并在仓库其它位置编写所需文档。
4. 后续更新可通过 git 同步 CoPal 模板；项目自定义内容完全归项目仓库维护。

## 6. 维护建议

- 对公共模板的改动需保持通用性，避免绑定具体技术栈；
- 若新增 CLI / 工作流，请先在此蓝图记录结构，再扩展其他文档；
- 推荐编写脚本检测 front matter 合法性与 metadata 完整度。
