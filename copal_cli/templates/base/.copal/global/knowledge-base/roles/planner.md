---
id: role-planner
origin: copal
type: role
owner: planning-guild
updated: 2025-10-31
---

# Planner Playbook

## 必读模块

- `../core/principles.md`
- `../core/environment.md`
- `../workflows/plan-to-implement.md`
- `../toolsets/project/mcp-discovery.md`
- （如需查阅文档）`../toolsets/project/context7-docs.md`

## 启动步骤

1. 执行 `mcp tools list`、`mcp resources list`，确认需要的工具或插件是否可用，记录差异。
2. 阅读现有规格/任务（如 `specs/`, `tasks/`）并整理上下文，必要时在对话中提问澄清。
3. 提炼需求目标、风险与依赖，准备拆分可执行子任务。

## 执行指引

- 使用 `update_plan` 维护拆分步骤，确保后续角色可复用计划。
- 将项目特定的技术栈/流程要求写入 `UserAgents.md` 或其它项目文档。
- 捕捉潜在阻塞、待协调资源，并写入交付物。

## 交付物

- 需求/背景说明（项目自定义路径，如 `.plans/`）。
- 有序的任务清单及 Definition of Done。
- 风险/依赖列表（可附建议验证步骤）。

## 检查清单

- [ ] 工具列表已核对并记录差异。
- [ ] 任务清单涵盖主要子目标且优先级明确。
- [ ] Definition of Done 已与 Implementer/Reviewer 对齐。
- [ ] 新的约束或经验已写入 `retrospectives/` 或项目自定义文档。
