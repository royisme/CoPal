# CoPal MCP Hooks System

## 概述

CoPal 的 MCP Hook 系统允许根据项目中可用的 MCP (Model Context Protocol) 工具，动态地向阶段 Prompt 中注入特定的使用指引。这使得 Codex 能够在正确的阶段获得正确的工具使用指导。

## 核心概念

### MCP 配置

在项目根目录的 `.copal/mcp-available.json` 文件中配置可用的 MCP 工具：

```json
["context7", "active-file", "file-tree"]
```

### Hook 路由规则

在 `.copal/hooks/hooks.yaml` 中定义何时注入哪些指引块：

```yaml
version: 1

rules:
  # Context7 在分析阶段的使用指引
  - id: context7-analysis
    stage: analysis
    any_mcp: ["context7"]
    inject:
      - "mcp/context7/usage.analysis.md"

  # Context7 在计划阶段的使用指引
  - id: context7-plan
    stage: plan
    any_mcp: ["context7"]
    inject:
      - "mcp/context7/usage.plan.md"

  # Active-file 和 file-tree 在实施阶段的使用指引
  - id: implement-active-context
    stage: implement
    all_mcp: ["active-file", "file-tree"]
    inject:
      - "mcp/active-file/usage.implement.md"
```

### 注入块

注入块是存储在 `.copal/hooks/mcp/` 目录下的 Markdown 文件，包含特定 MCP 工具在特定阶段的使用指引。

## Hook 规则语法

### 基本结构

```yaml
- id: unique-rule-id          # 唯一规则标识符
  stage: stage-name           # 阶段名称（analysis/spec/plan/implement/review）
  any_mcp: [...]              # 任一 MCP 匹配即可（OR 逻辑）
  all_mcp: [...]              # 所有 MCP 都必须匹配（AND 逻辑）
  inject:                     # 要注入的块列表
    - "path/to/block1.md"
    - "path/to/block2.md"
```

### 条件匹配

#### any_mcp（OR 逻辑）

只要列表中的任一 MCP 工具在 `mcp-available.json` 中存在，规则就会匹配：

```yaml
any_mcp: ["context7", "other-tool"]
# 只要 context7 或 other-tool 其中一个可用，就注入
```

#### all_mcp（AND 逻辑）

只有当列表中的所有 MCP 工具都在 `mcp-available.json` 中存在时，规则才会匹配：

```yaml
all_mcp: ["active-file", "file-tree"]
# 必须 active-file 和 file-tree 都可用，才注入
```

## 内置 Hook 示例

### Context7 - 分析阶段

**路径：** `.copal/hooks/mcp/context7/usage.analysis.md`

**何时注入：** 当 `context7` MCP 可用且处于 `analysis` 阶段时

**内容概要：**
- 如何使用 Context7 查询技术栈文档
- 如何收集背景信息和最佳实践
- 如何记录查询结果和版本信息

### Context7 - 计划阶段

**路径：** `.copal/hooks/mcp/context7/usage.plan.md`

**何时注入：** 当 `context7` MCP 可用且处于 `plan` 阶段时

**内容概要：**
- 如何确认将要使用的 API 和接口
- 如何设计技术方案
- 如何识别依赖和约束
- 如何列出将用的 API 和版本号

### Active-File + File-Tree - 实施阶段

**路径：** `.copal/hooks/mcp/active-file/usage.implement.md`

**何时注入：** 当 `active-file` 和 `file-tree` 都可用且处于 `implement` 阶段时

**内容概要：**
- 如何使用 file-tree 定位目标文件
- 如何使用 active-file 访问当前编辑的文件
- 如何执行代码修改和生成测试
- 如何记录修改清单

## 工作流程

1. **命令执行**：用户运行 `copal analyze`（或其他阶段命令）

2. **读取配置**：
   - 读取 `.copal/mcp-available.json` 获取可用 MCP 列表
   - 读取 `.copal/hooks/hooks.yaml` 获取路由规则

3. **规则匹配**：
   - 过滤出 `stage` 字段与当前阶段相同的规则
   - 检查每条规则的 `any_mcp` 或 `all_mcp` 条件
   - 收集所有匹配规则的 `inject` 块

4. **Prompt 渲染**：
   - 读取角色模板（如 `analyst.md`）
   - 依次读取所有匹配的注入块
   - 按顺序拼接：`Runtime Header + Role Template + Injection Blocks`
   - 写入 `.copal/runtime/<stage>.prompt.md`

5. **Codex 执行**：
   - Codex 读取生成的 Prompt 文件
   - 根据注入的 MCP 使用指引执行任务
   - 产出结果到 `.copal/artifacts/`

## 自定义 Hook

### 创建新的 MCP Hook

1. **添加 MCP 到配置**

编辑 `.copal/mcp-available.json`：
```json
["context7", "active-file", "file-tree", "my-custom-mcp"]
```

2. **创建注入块**

创建 `.copal/hooks/mcp/my-custom-mcp/usage.analysis.md`：
```markdown
# My Custom MCP 使用指引 - 分析阶段

## 工具说明
（描述你的 MCP 工具）

## 分析阶段使用建议
（提供使用指引）
```

3. **添加路由规则**

编辑 `.copal/hooks/hooks.yaml`：
```yaml
rules:
  - id: my-custom-mcp-analysis
    stage: analysis
    any_mcp: ["my-custom-mcp"]
    inject:
      - "mcp/my-custom-mcp/usage.analysis.md"
```

4. **测试**

运行 `copal analyze` 并检查生成的 Prompt 文件是否包含你的注入块。

### 创建跨阶段 Hook

如果某个 MCP 工具在多个阶段都有用，可以为每个阶段创建不同的注入块：

```yaml
rules:
  - id: my-tool-analysis
    stage: analysis
    any_mcp: ["my-tool"]
    inject:
      - "mcp/my-tool/usage.analysis.md"

  - id: my-tool-plan
    stage: plan
    any_mcp: ["my-tool"]
    inject:
      - "mcp/my-tool/usage.plan.md"

  - id: my-tool-implement
    stage: implement
    any_mcp: ["my-tool"]
    inject:
      - "mcp/my-tool/usage.implement.md"
```

### 创建组合 Hook

需要多个 MCP 同时存在才注入的场景：

```yaml
rules:
  - id: advanced-debugging
    stage: implement
    all_mcp: ["debugger", "profiler", "trace-logger"]
    inject:
      - "mcp/debugging/advanced-workflow.md"
```

## 最佳实践

1. **保持注入块简洁**：每个注入块应专注于单一阶段的单一工具使用

2. **明确使用场景**：在注入块中清楚说明何时使用、如何使用该工具

3. **提供示例**：在注入块中包含具体的命令示例或代码片段

4. **注明版本**：如果 MCP 工具有版本差异，在注入块中注明适用版本

5. **避免重复**：不要在多个注入块中重复相同的内容

6. **测试验证**：创建新 hook 后，运行相应阶段命令验证注入效果

## 故障排查

### Hook 没有被注入

检查清单：
- [ ] MCP 是否在 `.copal/mcp-available.json` 中列出？
- [ ] `hooks.yaml` 中的 `stage` 是否与当前阶段匹配？
- [ ] `any_mcp` 或 `all_mcp` 条件是否满足？
- [ ] 注入块文件是否存在于指定路径？
- [ ] YAML 语法是否正确（缩进、列表格式）？

### 如何调试

使用 `--verbose` 标志查看详细日志：

```bash
copal analyze --verbose
```

检查日志中是否有：
- "Selected X injection blocks for stage 'analysis'"
- "Injected block: mcp/xxx/usage.xxx.md"

查看生成的 Prompt 文件：

```bash
cat .copal/runtime/analysis.prompt.md
```

检查注入的内容是否出现在文件末尾。

## 参考

- [MCP 官方文档](https://modelcontextprotocol.org)
- [CoPal AGENTS.md](../templates/base/AGENTS.md) - 完整工作流导航
- [CoPal USAGE.md](USAGE.md) - 使用指南

## 未来增强（v0.2+）

- REQUEST_MCP 协商机制：允许 Codex 在执行过程中请求新的 MCP 工具
- 条件表达式：支持更复杂的条件逻辑（NOT、XOR 等）
- Hook 优先级：支持多个规则匹配时的优先级排序
- 动态参数：向注入块传递参数（如文件路径、配置值等）
