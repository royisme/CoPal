---
id: role-implementer
origin: copal
type: role
owner: build-team
updated: 2025-10-31
---

# Implementer Playbook

## 必读模块

- `../core/principles.md`
- `../core/environment.md`
- `../workflows/implementation-loop.md`
- `../toolsets/cli/index.md`
- 相关 CLI 指南（如 `../toolsets/cli/codex-cli.md`、`claude-code.md`、`copilot-cli.md`）

## 启动步骤

1. 选择合适的 CLI 并配置审批/沙箱策略（见 `../toolsets/cli/*`）。
2. 运行 `mcp tools list`，确认任务所需的 MCP 或插件已启用。
3. 阅读 Planner 的任务清单与 Definition of Done，补充缺失上下文。

## 执行指引

- 在 CLI 会话内完成代码编辑、测试、Git 操作，并保留命令输出。
- 将复杂任务拆分为多次提示或 `codex exec`/`claude --headless` 调用，持续更新 `update_plan`。
- 若遇到缺少指引的技术细节，可在 `UserAgents.md` 或其它项目文档中记录并补充指引。
- 使用 CLI 的日志/usage 功能记录操作历史，作为 Review 依据。

## 交付物

- 代码/配置变更及对应测试或验证结果。
- 关键命令输出（测试、构建、格式化等）。
- 更新后的任务或计划状态（已完成/阻塞/待复查）。

## 检查清单

- [ ] 所选 CLI 的审批和沙箱设置已启用。
- [ ] 关键验证命令运行成功并记录结果。
- [ ] 所有改动已在提交或笔记中说明原因与影响。
- [ ] 新经验或约束已更新到项目自定义文档或 `retrospectives/`。
