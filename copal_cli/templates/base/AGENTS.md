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

# CoPal Workflow - AGENTS 工作流导航

> 本文件提供 CoPal 工作流的完整导航，帮助 AI 编码助手（Codex）按正确顺序执行任务。

## 工作流概述

CoPal 将任务分为 6 个阶段，每个阶段由 CLI 命令触发，生成对应的 Prompt 文件供 Codex 阅读和执行：

1. **Analyze** - 分析任务，理解问题
2. **Spec** - 形成任务说明书
3. **Plan** - 制定可执行计划
4. **Implement** - 产出补丁和修改建议
5. **Review** - 评估质量，生成 PR
6. **Commit** - 记录工作流元数据

## 详细工作流

### 1. Analyze（分析阶段）

**执行命令：**
```bash
copal analyze --title "<任务标题>" --goals "<目标>" --constraints "<约束条件>"
```

**Codex 任务：**
1. 读取生成的 Prompt 文件：`.copal/runtime/analysis.prompt.md`
2. 按照 Prompt 指引，分析任务并理解问题
3. 产出分析报告：`.copal/artifacts/analysis.md`

**产物内容：**
- 问题理解摘要
- 信息收集点清单
- 待澄清事项列表
- 背景与上下文说明

**下一步：** 完成后执行 `copal spec`

---

### 2. Spec（规格阶段）

**执行命令：**
```bash
copal spec
```

**Codex 任务：**
1. 读取生成的 Prompt 文件：`.copal/runtime/spec.prompt.md`
2. 基于分析报告（`.copal/artifacts/analysis.md`），形成任务说明书
3. 产出规格说明：`.copal/artifacts/task_spec.md`

**产物内容：**
- 任务范围定义（Scope）
- 不在范围内的内容（Out-of-scope）
- 接口与数据结构定义
- 验收标准（Acceptance Criteria）
- 成功指标与约束条件

**下一步：** 完成后执行 `copal plan`

---

### 3. Plan（计划阶段）

**执行命令：**
```bash
copal plan
```

**Codex 任务：**
1. 读取生成的 Prompt 文件：`.copal/runtime/plan.prompt.md`
2. 基于任务说明书（`.copal/artifacts/task_spec.md`），制定可执行计划
3. 产出计划文档：`.copal/artifacts/plan.md`

**产物内容：**
- 详细的实施步骤
- 涉及的文件清单
- 风险评估与缓解策略
- 回滚方案

**MCP 增强：**
- 如果启用了 `context7` MCP，Prompt 会注入文档查询指引

**下一步：** 完成后执行 `copal implement`

---

### 4. Implement（实施阶段）

**执行命令：**
```bash
copal implement
```

**Codex 任务：**
1. 读取生成的 Prompt 文件：`.copal/runtime/implement.prompt.md`
2. 基于计划文档（`.copal/artifacts/plan.md`），产出修改建议
3. 产出补丁说明：`.copal/artifacts/patch_notes.md`（及代码补丁）

**产物内容：**
- 修改的文件列表
- 每个文件的修改摘要
- 测试建议和覆盖率说明
- 需要更新的文档

**MCP 增强：**
- 如果同时启用了 `active-file` 和 `file-tree` MCP，Prompt 会注入文件定位和修改指引

**下一步：** 完成后执行 `copal review`

---

### 5. Review（审查阶段）

**执行命令：**
```bash
copal review
```

**Codex 任务：**
1. 读取生成的 Prompt 文件：`.copal/runtime/review.prompt.md`
2. 评估实施质量，检查一致性和覆盖率
3. 产出审查报告：`.copal/artifacts/review_report.md` 和 `.copal/artifacts/pr_draft.md`

**产物内容：**
- 一致性评估（与计划和规格的对照）
- 测试覆盖率分析
- 风险评估与建议
- PR 描述草案

**下一步：** 完成后执行 `copal commit`

---

### 6. Commit（提交阶段）

**执行命令：**
```bash
copal commit [--task-id <任务ID>]
```

**产物：**
- 元数据文件：`.copal/artifacts/commit.json`
- 记录任务 ID、时间戳、产物列表

**完成：** 工作流已完成，可以开始新任务

---

## 系统命令

### MCP 工具管理

```bash
# 列出可用的 MCP 工具
copal mcp ls
```

查看 `.copal/mcp-available.json` 中配置的 MCP 工具。

### 状态查看

```bash
# 显示当前工作流状态
copal status
```

显示：
- 可用的 MCP 工具
- 已生成的 Prompt 文件
- 已产出的 Artifacts
- 建议的下一步命令

### 恢复工作流

```bash
# 恢复中断的工作流
copal resume
```

显示最近的阶段和 Prompt 文件，帮助 Codex 从中断处继续。

---

## MCP 集成说明

CoPal 支持 MCP (Model Context Protocol) 集成，根据可用的 MCP 工具动态注入相关指引。

### 配置 MCP

在项目根目录创建 `.copal/mcp-available.json`：

```json
["context7", "active-file", "file-tree"]
```

### MCP 增强效果

- **context7**: 在 `analyze` 和 `plan` 阶段注入文档查询指引
- **active-file + file-tree**: 在 `implement` 阶段注入文件定位和修改指引

---

## 快速开始示例

```bash
# 1. 初始化 CoPal（仅需一次）
copal init

# 2. 配置 MCP（可选）
echo '["context7", "active-file", "file-tree"]' > .copal/mcp-available.json

# 3. 开始一个新任务
copal analyze --title "添加用户认证功能" --goals "实现 JWT 登录" --constraints "零依赖"

# 4. Codex 读取 .copal/runtime/analysis.prompt.md 并产出 analysis.md

# 5. 依次执行后续阶段
copal spec
copal plan
copal implement
copal review
copal commit

# 6. 查看状态
copal status
```

---

## 全局约束

1. **语言一致**：默认使用中文回复，除非用户另有要求
2. **计划优先**：使用 `update_plan` 跟踪多步骤任务
3. **命令安全**：遵循所用 CLI 的审批/沙箱策略，禁止绕过人工确认的高危操作
4. **日志可追溯**：保留关键命令输出或引用 CLI 的 `usage/logs`
5. **知识维护**：发现缺失指引请更新 `UserAgents.md` 或相关项目文档

## 项目自定义

初始化后，请在 `UserAgents.md` 中补充：
- 项目结构和技术栈
- 关键命令（测试、构建、部署）
- 安全策略或审批要求
- 其他项目特定的文档链接

---

> 更新公共模板时请回到 CoPal 仓库提交改动；项目自定义内容在自身仓库维护。
