---
id: codex-cli
origin: copal
type: cli-guide
owner: integration-team
enforcement: recommended
updated: 2025-10-31
---

# Codex CLI 指南

## 安装与验证

```bash
npm install -g @openai/codex
codex --version
```

如使用 Homebrew：`brew install codex`。

## 常用启动方式

```bash
codex                          # 进入交互式 TUI
codex "fix lint errors"         # 带初始提示的互动会话
codex exec "explain utils.ts"  # 自动化 / headless 模式
```

## 安全设置

- 审批策略：
  - `codex --ask-for-approval suggest` / `on-request` / `on-failure` / `never`
- 沙箱模式：
  - `codex --sandbox read-only`
  - `codex --sandbox workspace-write`
  - `codex --sandbox danger-full-access`

## MCP 管理

```bash
codex mcp list
codex mcp add docs -- npx -y mcp-server-docs
codex mcp get docs --json
codex mcp remove docs
codex mcp login <server>
```

## 使用建议

- 在仓库根目录启动，确保 Git 状态、上下文可用。
- 大型任务拆分为多个指令，结合 `update_plan` 跟踪进度。
- 使用 `codex logs --tail`（或查看 `~/.config/codex/logs/`）审计命令历史。
- 发布前可切换到更严格的审批模式。

## 常见问题

- **授权失败**：确认已登录 OpenAI 账号并配置 API Key。
- **MCP 无法启动**：检查 `--` 后的命令是否可执行，手动运行验证。
- **任务超时**：拆分请求或提供更详细指令，减少单次执行量。
