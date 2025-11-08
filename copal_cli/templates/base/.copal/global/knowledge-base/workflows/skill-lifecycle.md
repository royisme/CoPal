---
id: workflow-skill-lifecycle
origin: copal
type: workflow
owner: automation-guild
updated: 2025-10-31
---

# Workflow · 技能全流程

## 目标

通过标准化步骤让团队发现、脚手架、执行并复用技能，确保沙箱一致与交接完整。

## 输入

- 业务需求或重复性任务
- 已登记的技能信息（注册表、标签、所有者）
- 现有 `prelude.md` 或运行日志（若复用）

## 步骤

1. **检索技能**：运行 `copal skill registry` 查看可用源，使用 `copal skill search <关键词>` 根据标签、能力或所有者筛选候选技能。
2. **选择策略**：确认技能的 `skill.yaml` 是否满足当前任务的沙箱、参数和依赖要求；若无现成技能，记录缺口并通知维护者。
3. **脚手架准备**：执行 `copal skill scaffold <id> --target <目录>`，必要时追加 `--prelude prelude.md` 生成交接文件。若技能已存在，仅更新版本或参数。
4. **自定义参数**：在脚手架目录中编辑 `skill.yaml` 或 `args/` 子文件，记录本次运行所需的输入、输出路径与环境变量。
5. **沙箱确认**：阅读技能清单的 `sandbox.mode`，确保执行时使用不低于要求的模式（`replay` / `reuse` / `fresh`）。
6. **执行技能**：`copal skill exec <id> --prelude prelude.md --sandbox <模式> [--args ...]`，并在命令输出中保留日志链接或 `usage/` 路径。
7. **结果交接**：将 `prelude.md`、运行日志、差异摘要随任务或 PR 一并提交；如发现改进点，更新脚手架或在 `retrospectives/` 记录。

## 输出

- 更新后的 `prelude.md`（含参数、沙箱模式、依赖）
- 技能执行日志与结果（可为 `usage/` 目录或 CLI 截图）
- 对技能本身的迭代建议或问题反馈

## 质控

- 未提供 `prelude.md` 的任务不得进入实施阶段；
- `copal skill exec` 必须引用和技能清单一致的 `--sandbox`；
- 若技能需要提升权限（例如从 `replay` 升级为 `reuse`），须由项目维护者审批并更新注册表。
