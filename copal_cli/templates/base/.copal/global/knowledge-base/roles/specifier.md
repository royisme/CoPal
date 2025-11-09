---
id: role-specifier
origin: copal
type: role
owner: specification-guild
updated: 2025-11-03
---

# Specifier Playbook

## 必读模块

- `../core/principles.md`
- `../core/environment.md`
- `.copal/artifacts/analysis.md`（分析阶段产物）
- `../toolsets/project/mcp-discovery.md`
- （如需查阅文档）`../toolsets/project/context7-docs.md`

## 启动步骤

1. 阅读分析报告（`.copal/artifacts/analysis.md`），理解问题背景和信息收集点。
2. 执行 `mcp tools list`，确认所需工具可用。
3. 补充必要的技术调研和上下文收集。

## 执行指引

- 将模糊的任务需求转化为清晰的、可验收的规格说明。
- 明确任务范围（Scope）与不在范围内的内容（Out-of-scope）。
- 定义接口、数据结构、交互方式等技术细节。
- 制定验收标准（Acceptance Criteria）和成功指标。
- 不要在此阶段进行具体的实施计划或代码设计。

## 交付物

- 任务规格说明书（`.copal/artifacts/task_spec.md`），包含：
  - 任务范围定义（Scope）
  - 不在范围内的内容（Out-of-scope）
  - 接口与数据结构定义
  - 验收标准（Acceptance Criteria）
  - 成功指标与约束条件

## 检查清单

- [ ] 任务范围已清晰定义，边界明确。
- [ ] 验收标准可测试、可量化。
- [ ] 接口和数据结构定义完整。
- [ ] Out-of-scope 项已明确列出，避免范围蔓延。
- [ ] 规格说明书已保存到 `.copal/artifacts/task_spec.md`。
