---
id: workflow-plan-to-implement
origin: copal
type: workflow
owner: planning-guild
updated: 2025-10-31
---

# Workflow · 规划到实施

## 目标

将用户需求转化为可执行的任务计划，并明确验收标准。

## 输入

- 用户/业务需求或缺陷报告
- 现有规格、文档、任务清单

## 步骤

1. **收集上下文**：阅读相关规格（如 `openspec/AGENTS.md`）、历史任务、retro 记录。
2. **确认工具**：运行 `mcp tools list`、`mcp resources list`，记录差异并通知维护者；使用 `copal skill search <关键词>` 检查是否已有可复用技能，并在计划中标注候选技能 ID。
3. **拆分任务**：输出按优先级排列的子任务，标注依赖与责任角色；明确需要脚手架的技能，并指定 `prelude.md` 的负责人。
4. **定义验收**：与执行/审核角色达成一致的 Definition of Done，并说明技能执行所需的沙箱模式与产出（日志、prelude）。
5. **发布计划**：在项目约定目录（例如 `.plans/`）写入背景、目标、任务、风险与验证步骤，附上技能来源链接或注册表条目。

## 输出

- 任务清单与优先级
- Definition of Done
- 依赖与风险记录

## 质控

- Planner 与 Implementer 共同确认任务颗粒度与输入完整；
- Reviewer 可抽样核对计划与实际交付的对齐程度。
