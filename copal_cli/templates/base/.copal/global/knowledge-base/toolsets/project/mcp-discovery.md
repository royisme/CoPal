---
id: mcp-discovery
origin: copal
type: tool-discovery
owner: integration-team
enforcement: recommended
updated: 2025-10-31
---

# MCP 工具发现指引

## 使用场景

- 任务开始前确认当前可用的 MCP 工具、资源、模板；
- 新增/移除 MCP 服务器后更新知识库或项目自定义文档。

## 快速命令

```bash
mcp tools list
mcp tools show <tool-id>
mcp resources list
mcp templates list
```

## 操作步骤

1. 在启动阶段运行 `mcp tools list`，记录与默认配置的差异。
2. 缺少指引时，将结果记录在 `UserAgents.md`（或其他项目文档）并补充使用说明。
3. 将差异或待补充事项记录到 `retrospectives/`，通知相关负责人。

## 提示

- MCP 查询开销极低，可随时重复执行；
- 若命令不可用，说明当前环境未启用 MCP，请在项目文档中说明原因。
