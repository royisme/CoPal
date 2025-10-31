---
id: copilot-cli
origin: copal
type: cli-guide
owner: integration-team
enforcement: recommended
updated: 2025-10-31
---

# GitHub Copilot CLI 指南

## 安装与登录

```bash
npm install -g @github/copilot   # 需 Node.js 22+、npm 10+
copilot --version
```

首次运行需在 CLI 中执行 `/login` 绑定 GitHub 账号。

## 会话管理

```bash
copilot                 # 交互式会话
copilot --banner        # 显示启动动画
copilot --continue      # 恢复最近会话
copilot --resume        # 浏览历史对话
```

会话内常用命令：`/login`、`/exit`、`/clear`、`/usage`、`/help`。

## 安全策略

- `copilot -p`：逐个审批访问路径。
- `copilot --allow-all-paths`：信任所有路径（谨慎使用）。
- `copilot --allow-tool "shell(git *)"`：允许特定命令。
- `copilot --deny-tool "shell(rm -rf *)"`：拒绝危险命令。
- 使用 `/usage` 获取 premium 请求、token 使用、代码变更统计。

## 非交互模式

```bash
copilot "Add error handling to src/api/users.js"
copilot --model claude-haiku-4.5 "Run tests and fix failures"
copilot --agent security-scanner "Scan for vulnerabilities"
```

可结合 shell：`copilot "Generate docs" && cat docs/api.md`。

## 文件引用

- 在提示中输入 `@` 选择文件或图片，支持模糊搜索、显示近期修改文件。
- 可一次引用多个文件提高上下文准确性。

## 常见问题

- **认证失败**：确认付费订阅有效，可先 `/logout` 再 `/login`。
- **会话丢失**：查看 `~/.copilot/session-state`，用 `--resume` 选择历史。
- **权限不足**：调整 `--allow-tool`、`--allow-all-paths`，或在审批提示时授权。
