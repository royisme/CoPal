---
id: cli-runtime-basics
origin: copal
type: environment
owner: copal-team
enforcement: required
updated: 2025-10-31
---

# 终端代理运行约束

- **工作目录**：默认在仓库根目录执行命令；如需跨目录操作，请显式指定 `--cwd` 或绝对路径。
- **审批策略**：
  - Codex：`codex --ask-for-approval on-request` / `suggest` / `never`（根据风险选择）。
  - Claude Code：在设置文件或启动参数中启用审批提示。
  - Copilot CLI：使用 `-p`、`--allow-tool`、`--deny-tool` 管理权限。
- **沙箱模式**：优先使用受限模式（Codex `--sandbox workspace-write` 等），仅在隔离环境下开启 full-access。
- **命令守卫**：
  - 可参考 `toolsets/agent/agents-guardrail-uv.md` 实现简单的命令拦截。
  - 项目可添加语言专属守卫（例如禁止裸 `python`、`pip`）。
- **MCP / 插件发现**：在每个任务前执行 `mcp tools list`、`mcp resources list`，确保工具与文档保持同步。
- **日志与审计**：
  - Codex：查看 `~/.config/codex/logs/` 或使用 `codex logs --tail`。
  - Claude Code：使用 `/logs` 或检查默认日志目录。
  - Copilot CLI：通过 `/usage` 获取请求统计、代码变更与 token 使用。
  将重要日志摘要附在任务总结或 `logs/` 目录中。
