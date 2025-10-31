<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS 索引（模板）

> 将本文件复制到目标仓库根目录后，请根据项目实际情况补充“项目自定义”段落。

## 全局约束

1. **语言一致**：默认使用中文回复，除非用户另有要求。
2. **计划优先**：使用 `update_plan` 跟踪多步骤任务。
3. **命令安全**：遵循所用 CLI 的审批/沙箱策略，禁止绕过人工确认的高危操作。
4. **日志可追溯**：保留关键命令输出或引用 CLI 的 `usage/logs`。
5. **知识维护**：发现缺失指引请更新 `UserAgents.md` 或相关项目文档，并记录在 retro。

## 快速导航

| 触发关键词 / 场景 | CoPal 默认模块 | 用户自定义 |
| --- | --- | --- |
| “proposal” / “spec” / “plan” | `.copal/global/knowledge-base/workflows/plan-to-implement.md` | 请在 `UserAgents.md` 指明项目流程 |
| “实现” / “执行测试” | `.copal/global/knowledge-base/roles/implementer.md` | `UserAgents.md` 或其他项目文档 |
| “审核” / “发布” | `.copal/global/knowledge-base/roles/reviewer.md` | 同上 |
| “Codex” / “Claude Code” / “Copilot” | `.copal/global/knowledge-base/toolsets/cli/*.md` | 若有内部工具请在 `UserAgents.md` 补充 |
| “MCP” / “插件” | `.copal/global/knowledge-base/toolsets/project/mcp-discovery.md` | |

> 初始化后，请在第三列补充具体的项目文档链接（可放在 `UserAgents.md` 或其它路径）。

## 启动流程

1. 阅读本文件后，进入 `.copal/global/knowledge-base/README.md` 熟悉目录结构；
2. 根据任务类型加载 `roles/` 中的 Playbook 并完成“启动步骤”；
3. 运行 `mcp tools list`、配置 CLI 审批/沙箱；
4. 按 `workflows/` 执行任务，保留日志输出；
5. 若需要项目特定说明，请查阅 `UserAgents.md` 或项目自定义文档。

## 项目自定义（请在 init 后修改）

- 概述项目结构（如子仓库、技术栈、部署流程等）；
- 指定关键命令（测试、构建、部署）与对应 CLI 使用方式；
- 说明额外的安全策略或审批要求；
- 如需更多文档，可在仓库其它位置编写并在此处链接。

## 外部指引

- `openspec/AGENTS.md`：Spec 驱动流程；
- `CLAUDE.md` 或其他 CLI 深度文档：可在项目仓库中拆分并在 `UserAgents.md` 链接。

> 更新公共模板时请回到 CoPal 仓库提交改动；项目自定义内容在自身仓库维护。
