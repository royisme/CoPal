---
id: workflow-review-release
origin: copal
type: workflow
owner: qa-team
updated: 2025-10-31
---

# Workflow · 审查与交付

## 目标

验证实施结果符合需求，准备合并或发布，并沉淀经验。

## 输入

- 实施阶段的代码、日志、命令输出
- Definition of Done 与验收清单
- CLI 会话统计与权限状态

## 步骤

1. **资料收集**：读取 Implementer 提供的日志、retro；确认 CLI `usage`、审批状态。
2. **复跑验证**：在受控环境重跑测试/构建/发布前检查。
3. **代码审查**：评估风险点、潜在的安全/性能问题，确认审批策略被遵守。
4. **交付准备**：生成 review 结果、发布 checklist、回滚方案（如适用）。
5. **更新记录**：调整任务状态，补充项目文档或 retro 中的经验与待办。

## 输出

- Review & QA 报告
- 验证命令输出
- 发布或回滚预案

## 质控

- 所有问题均有明确处理人或时间表；
- 项目规范在需要时更新；
- 审查日志与审批记录妥善保存。
