---
id: role-reviewer
origin: copal
type: role
owner: qa-team
updated: 2025-10-31
---

# Reviewer Playbook

## 必读模块

- `../core/principles.md`
- `../core/environment.md`
- `../workflows/review-release.md`
- 对应 CLI 指南（根据实现所用工具选择）

## 启动步骤

1. 检查 `retrospectives/` 是否有尚未解决的约束或遗留问题。
2. 获取实现阶段的日志（例如 Copilot `/usage`、Codex `logs`、Claude Code `/logs`）。
3. 准备复跑关键命令（测试、构建、lint）以验证实现结果。

## 审查指引

- 对照 Definition of Done 和 Planner 需求确认功能完整性。
- 检查 CLI 会话是否遵守审批/沙箱策略，排除高风险命令。
- 将代码、文档、日志中的问题汇总成可执行反馈。
- 必要时在 `UserAgents.md` 或相关项目文档中更新规范或提出改进建议。

## 交付物

- Review 报告或问题清单。
- 验证命令的输出记录。
- 发布前置条件或回滚策略（适用时）。
- 更新的任务状态（通过/待修改/阻塞原因）。

## 检查清单

- [ ] 所有关键验证命令已复跑且通过。
- [ ] 发现的问题已登记并指派责任人跟进。
- [ ] 项目规范若需更新，已在 `UserAgents.md` 或相关文档中提出修改建议。
- [ ] 日志与审批记录存档完毕。
