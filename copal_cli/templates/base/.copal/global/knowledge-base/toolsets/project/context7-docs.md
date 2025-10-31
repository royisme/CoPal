---
id: context7-docs
origin: copal
type: knowledge
owner: integration-team
enforcement: recommended
updated: 2025-10-31
---

# Context7 文档检索指引

## 使用场景

- 快速查询第三方库、框架或工具的官方文档；
- 指定版本 API 说明用于实现与验证。

## 操作步骤

1. （可选）`mcp tools list` 确认已经安装 `context7` 相关工具。
2. `context7 resolve-library-id "<library-name>"` 获取精确 ID。
3. `context7 get-library-docs --id <id> --topic <topic> --tokens <limit>` 下载所需内容。

## 产出要求

- 在方案/设计文档中标记引用来源与版本；
- 若解析失败或缺少库，在 `retrospectives/` 说明并提 Issue。

## 常见问题

- **网络失败**：检查本地配置或代理，必要时刷新凭证；
- **版本冲突**：尽量使用完整版本号（如 `/vercel/next.js/v14.3.0`）。
