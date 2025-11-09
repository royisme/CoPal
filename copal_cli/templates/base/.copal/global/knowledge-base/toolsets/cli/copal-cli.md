---
id: copal-cli
origin: copal
type: cli-guide
owner: automation-guild
enforcement: baseline
updated: 2025-10-31
---

# CoPal CLI 指南

## 核心命令

```bash
copal init --target .             # 安装模板
copal validate --target .copal    # 校验 front matter
copal skill registry              # 列出技能注册表
copal skill search <关键词>       # 检索技能
copal skill scaffold <id>         # 拉取技能脚手架
copal skill exec <id>             # 执行技能
```

## 技能脚手架

- `--target <目录>`：放置技能清单与入口提示。
- `--prelude <路径>`：生成交接文件，记录参数、沙箱、依赖。
- 建议将 `prelude.md` 与任务说明或 PR 一并提交，便于复用。

## 沙箱策略

| 模式 | 说明 | 常见场景 |
| --- | --- | --- |
| `replay` | 只读回放，不写入磁盘 | 审核技能步骤、dry run |
| `reuse` | 复用隔离环境（默认） | 重复执行、增量输出 |
| `fresh` | 每次全新环境 | 高敏感或具副作用的脚本 |

执行 `copal skill exec` 时必须提供与技能清单相同或更严格的 `--sandbox`，否则命令会失败。

## Prelude 约定

`prelude.md` 需包含：

1. 任务背景与技能 ID；
2. 输入参数、环境变量、外部资源链接；
3. 预期产出（文件、日志、工件路径）；
4. 上一次执行摘要与负责人；
5. 复现命令（含 `--sandbox`、`--args`）。

## 审计与日志

- CLI 默认在 `.copal/logs/` 下写入执行日志，可用于 PR 引用；
- 执行前确认 Git 工作区干净，避免误提交脚手架中的临时文件；
- 对关键技能运行结果附上 `usage/` 目录或命令输出片段。

## 常见问题

- **注册表不可用**：检查 `COPAL_SKILL_REGISTRY` 是否指向有效 YAML，或回退到内置 `.copal/registry.yaml`。
- **沙箱冲突**：如果技能要求 `fresh` 但本地环境无法创建容器，需要联系维护者调整策略。
- **prelude 缺失字段**：执行 `copal skill scaffold ... --prelude prelude.md --force` 重新生成，并手动补齐项目特定配置。
