---
id: workflow-implementation-loop
origin: copal
type: workflow
owner: build-team
updated: 2025-10-31
---

# Workflow · 实施循环

## 目标

使用终端型 AI 工具完成单次开发迭代：分析 → 修改 → 验证 → 记录。

## 输入

- Planner 提供的任务清单与 Definition of Done
- 项目自定义规范与工具指引
- 可用的 MCP 插件与 CLI 设置

## 步骤

1. **环境自检**：按照 `../core/environment.md` 设置审批、沙箱、命令守卫。
2. **理解上下文**：在 CLI 中请求代码定位、阅读结果，必要时用 `update_plan` 更新步骤。
3. **实施改动**：分阶段执行编辑、测试、格式化，保持命令输出。
4. **本地验证**：运行要求的测试/构建命令，并记录结果。
5. **结果记录**：总结关键变更、命令输出、残留问题，更新任务状态。

## 输出

- 代码/配置改动及验证结果
- CLI 日志或 `/usage` 摘要
- 更新后的计划或任务状态

## 质控

- 确认审批/沙箱在执行过程中未被关闭；
- 对失败命令提供解决方案或阻塞说明；
- 将新经验写入项目自定义文档或 `retrospectives/`。
