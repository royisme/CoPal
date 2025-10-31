---
id: knowledge-base
origin: copal
type: index
updated: 2025-10-31
---

# CoPal 通用知识库

该目录为所有终端型 AI 编码工具共享的**默认**知识骨架，核心目标：

- 为 Codex / Claude Code / Copilot CLI 等工具提供统一的角色、流程与工具指引；
- 用 YAML front matter 标注元数据，方便 LLM 或脚本快速检索；
- 与项目侧自定义内容叠加：若项目提供同名文档，可按约定覆盖默认说明。

## 目录速览

- `core/`：全局原则与环境约束；
- `roles/`：通用角色 Playbook（Planner、Implementer、Reviewer 等）；
- `workflows/`：跨角色工作流，如规划→实施、实施循环、审查发布；
- `toolsets/cli/`：常见 CLI 指南；
- `toolsets/project/`：通用工具发现、文档检索辅助；
- `toolsets/agent/`：CoPal 自带的守卫/脚本示例；
- `logs/`、`retrospectives/`：记录守卫输出与待补充事项（项目侧可覆盖或追加）。

初始化后，项目可在 `UserAgents.md` 中列出自定义文档路径，或在仓库其它位置创建同名文档覆盖默认说明，并在 `AGENTS.md` 中提供链接。
