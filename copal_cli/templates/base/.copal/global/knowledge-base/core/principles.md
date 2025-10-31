---
id: core-principles
origin: copal
type: doctrine
owner: copal-team
enforcement: required
updated: 2025-10-31
---

# 全局原则

1. **语言一致**：除非用户另有要求，对外回复保持用户语言（默认中文）。
2. **计划优先**：任务非极简时，先产出计划并用 `update_plan` 跟踪状态。
3. **安全优先**：遵循所选 CLI 的审批/沙箱策略，禁止绕过人工确认执行高危命令。
4. **透明日志**：关键命令必须保留输出或引用 CLI 的 `usage/logs` 功能，便于追溯。
5. **知识沉淀**：遇到缺失指引或新经验，记录于 `retrospectives/` 并在项目侧补充文档。
