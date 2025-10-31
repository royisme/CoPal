---
id: claude-code
origin: copal
type: cli-guide
owner: integration-team
enforcement: recommended
updated: 2025-10-31
---

# Claude Code CLI 指南

## 安装与启动

```bash
npm install -g @anthropic-ai/claude-code
claude --version
```

支持的启动方式：

```bash
claude                              # 交互式终端
claude --headless "explain main.js" # 单次命令
ANTHROPIC_API_KEY=xxx claude        # 指定密钥
claude --settings ./settings.json   # 自定义配置
```

## 插件管理

在 CLI 内使用 `/plugin` 系列命令：

```bash
/plugin marketplace
/plugin install <name>
/plugin enable feature-dev
/plugin disable feature-dev
/plugin validate
```

内置插件示例：`security-guidance`、`pr-review-toolkit`、`feature-dev`、`commit-commands`。

## Git 工作流

- Claude 可自动执行 `git status`、`git diff`、新建分支、生成 commit message、推送与 `gh pr create`。
- 建议人工复核 commit/PR 内容，确保符合团队规范。

## 使用建议

- 在目标仓库目录启动，保证上下文准确。
- 对于长流程，先用 headless 模式执行检查，再进入交互调试。
- 需要 GUI 支持时可安装 VS Code 扩展：`code --install-extension anthropic.claude-code`。
- 可使用 `/logs` 或默认日志目录查看历史命令。

## 常见问题

- **插件不可用**：确认插件是否启用或网络可访问 marketplaces。
- **Git 操作失败**：确保本地 `gh` 或 Git 凭据有效。
- **设置文件**：`claude --settings` 可定义默认模型、审批策略、文件忽略等。
