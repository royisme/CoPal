---
id: role-analyst
origin: copal
type: role
owner: analysis-guild
updated: 2025-11-03
---

# Analyst Playbook

## 必读模块

- `../core/principles.md`
- `../core/environment.md`
- `../toolsets/project/mcp-discovery.md`
- （如需查阅文档）`../toolsets/project/context7-docs.md`

## 启动步骤

1. 执行 `mcp tools list`、`mcp resources list`，确认需要的工具或插件是否可用。
2. 阅读任务输入（标题、目标、约束条件）并理解核心问题。
3. 识别信息缺口和待澄清事项，在对话中与用户交互确认。

## 执行指引

- 收集并整理问题背景、目标与约束条件。
- 列出需要进一步收集的信息点（技术栈、依赖、环境等）。
- 标记不明确或有歧义的需求，提出澄清问题。
- 不要在此阶段进行任务拆解或技术方案设计，仅专注于问题理解。

## 交付物

- 分析报告（`.copal/artifacts/analysis.md`），包含：
  - 问题理解摘要
  - 信息收集点清单
  - 待澄清事项列表
  - 背景与上下文说明

## 检查清单

- [ ] 已明确理解任务的核心目标。
- [ ] 已列出所有需要收集的信息点。
- [ ] 已识别所有待澄清的模糊需求。
- [ ] 分析报告已保存到 `.copal/artifacts/analysis.md`。
