# CoPal 使用指南

本指南详细介绍如何安装、配置和使用 CoPal 来管理 AI 编程助手的工作流。

## 目录

- [安装](#安装)
- [初始化](#初始化)
- [自定义项目](#自定义项目)
- [代理加载顺序](#代理加载顺序)
- [工作流命令](#工作流命令)
- [技能管理](#技能管理)
- [记忆管理](#记忆管理)
- [MCP 配置](#mcp-配置)
- [更新模板](#更新模板)
- [最佳实践](#最佳实践)

## 安装

CoPal 目前作为源代码包提供。使用可编辑模式在本地安装，以便立即反映更新：

```bash
# 从 GitHub 克隆
git clone https://github.com/royisme/CoPal.git
cd CoPal

# 基础安装
pip install -e .

# 或者，安装开发依赖（包括测试工具）
pip install -e ".[dev]"
```

CoPal 需要 Python 3.9 或更新版本。

### 验证安装

```bash
# 检查 CLI 是否可用
copal --help

# 查看版本信息
copal --version
```

## 初始化

从目标仓库的根目录运行 init 命令：

```bash
copal init --target .
```

### 选项说明

- `--target` – 目标目录（默认：当前工作目录）
- `--force` – 如果文件已存在则覆盖
- `--dry-run` – 显示将要创建的文件，但不实际写入磁盘
- `--verbose` – 启用详细日志输出

### 创建的内容

命令会创建：
- `AGENTS.md` – 根导航指南，为 AI 助手提供入口点
- `UserAgents.md` – 项目特定指导的占位符
- `.copal/` – 包含以下内容的目录：
  - `global/knowledge-base/` – 共享知识库模板
  - `hooks/` – MCP 钩子配置
  - `mcp-available.json` – 可用 MCP 工具声明
  - `runtime/` – 运行时生成的提示词（自动创建）
  - `artifacts/` – 工作流产物存储（自动创建）

### 注意事项

将 `.copal/` 视为只读，除非您有意扩展模板。要同步 CoPal 的更新，请重新运行 `copal init --force`。

## 自定义项目

### 1. 编辑根导航文档

编辑 `AGENTS.md`，使"项目自定义"部分指向实际文档：

```markdown
## 项目自定义

请阅读以下项目特定文档：

- [项目概述](./docs/overview.md)
- [架构设计](./docs/architecture.md)
- [编码规范](./docs/coding-standards.md)
```

### 2. 填充项目特定指导

在 `UserAgents.md` 中填充项目特定的规范和惯例：

```markdown
# 用户代理指导

## 项目结构

本项目采用模块化架构...

## 开发工作流

1. 从 main 分支创建功能分支
2. 实现功能并添加测试
3. 运行 linter 和测试套件
4. 提交 PR 进行审查

## 技术栈

- 后端：Python 3.9+ with FastAPI
- 数据库：PostgreSQL 14+
- 测试：pytest + pytest-cov
```

并链接到仓库中的其他文档。

### 3. 覆盖知识库模板（可选）

如需覆盖共享模板：

1. 创建镜像路径，例如 `docs/agents/knowledge-base/roles/`
2. 复制并修改您需要自定义的模板
3. 在 `UserAgents.md` 中链接这些文档

例如，覆盖实现者角色：

```bash
mkdir -p docs/agents/knowledge-base/roles
cp .copal/global/knowledge-base/roles/implementer.md \
   docs/agents/knowledge-base/roles/implementer.md
# 编辑 docs/agents/knowledge-base/roles/implementer.md
```

然后在 `UserAgents.md` 中添加：

```markdown
## 自定义角色

- [实现者角色](./docs/agents/knowledge-base/roles/implementer.md)
```

### 4. 存储可重用提示词

在仓库的任何位置存储可重用的提示词或工作手册：

```
docs/
├── agents/
│   ├── prompts/
│   │   ├── code-review.md
│   │   └── testing-strategy.md
│   └── workflows/
│       └── feature-development.md
```

从 `UserAgents.md` 链接它们：

```markdown
## 工作流指南

- [功能开发流程](./docs/agents/workflows/feature-development.md)
- [代码审查标准](./docs/agents/prompts/code-review.md)
- [测试策略](./docs/agents/prompts/testing-strategy.md)
```

## 代理加载顺序

当 AI 助手开始在仓库上工作时，应按以下顺序读取文档：

1. **根目录 `AGENTS.md`** - 提供整体导航和结构
2. **`.copal/global/knowledge-base` 模板** - 加载共享角色和工作流
3. **`UserAgents.md`** - 加载项目特定的指导和覆盖
4. **从 `UserAgents.md` 链接的任何文档** - 详细的项目文档

这种顺序确保：
- 共享模板首先加载，提供通用指导
- 项目特定的覆盖随后加载，提供定制化指导
- AI 助手获得完整的上下文和知识

## 工作流命令

CoPal 提供六个主要的工作流阶段。每个阶段生成提示词并期望特定的产物。

### 1. 分析阶段（Analyze）

理解任务并收集上下文。

```bash
copal analyze --title "添加用户认证" \
               --goals "实现基于 JWT 的认证系统" \
               --constraints "必须兼容现有的用户数据库"
```

**输出：**
- `.copal/runtime/analysis.prompt.md` – 分析提示词
- 期望产物：`.copal/artifacts/analysis.md` – 分析结果

**提示词包含：**
- 任务元数据（标题、目标、约束）
- 分析师角色指导
- MCP 工具使用提示（如果配置了 context7）

### 2. 规范阶段（Spec）

编写正式的任务规范。

```bash
copal spec
```

**输出：**
- `.copal/runtime/spec.prompt.md` – 规范提示词
- 期望产物：`.copal/artifacts/spec.md` – 任务规范

**提示词包含：**
- 规范员角色指导
- 前一阶段的分析结果
- 规范编写最佳实践

### 3. 计划阶段（Plan）

制定可执行的实施计划。

```bash
copal plan
```

**输出：**
- `.copal/runtime/plan.prompt.md` – 计划提示词
- 期望产物：`.copal/artifacts/plan.md` – 实施计划

**提示词包含：**
- 计划员角色指导
- 规范和分析结果
- MCP 工具使用提示（如果配置了 context7）
- 计划编写模板

### 4. 实现阶段（Implement）

执行计划并记录更改。

```bash
copal implement
```

**输出：**
- `.copal/runtime/implement.prompt.md` – 实现提示词
- 期望产物：`.copal/artifacts/patch-notes.md` – 更改说明

**提示词包含：**
- 实现者角色指导
- 详细的实施计划
- MCP 工具使用提示（如果配置了 active-file 和 file-tree）
- 代码更改指导

### 5. 审查阶段（Review）

评估质量并起草 PR 说明。

```bash
copal review
```

**输出：**
- `.copal/runtime/review.prompt.md` – 审查提示词
- 期望产物：`.copal/artifacts/review.md` – 审查结果

**提示词包含：**
- 审查者角色指导
- 实现的更改说明
- 质量检查清单
- PR 准备指导

### 6. 提交阶段（Commit）

记录工作流元数据。

```bash
copal commit
```

**输出：**
- `.copal/runtime/commit.prompt.md` – 提交提示词
- 期望产物：`.copal/artifacts/commit-metadata.json` – 工作流元数据

**提示词包含：**
- 提交指导
- 工作流完成清单
- 元数据收集模板

### 状态和恢复

```bash
# 查看工作流状态
copal status

# 恢复中断的工作流（显示最近的提示词）
copal resume
```

## 技能管理

技能是存储在 `.copal/skills/`（或自定义根目录）下的可重用自动化模块。

### 创建技能脚手架

```bash
# 创建 Python 技能
copal skill scaffold my-skill \
  --skills-root .copal/skills \
  --lang python \
  --description "自动化单元测试生成"

# 创建 Bash 技能
copal skill scaffold deploy-script \
  --lang bash \
  --description "自动化部署脚本"
```

**创建的内容：**
```
.copal/skills/my-skill/
├── skill.json           # 元数据（ID、语言、描述等）
├── prelude.md          # 使用说明和要求
├── entrypoint.log      # 执行日志
├── scripts/            # 脚本目录
├── tests/              # 测试目录
└── examples/           # 示例目录
```

### 构建技能注册表

扫描技能并生成注册表：

```bash
copal skill registry build --skills-root .copal/skills
```

生成 `.copal/skills/registry.json`，包含所有技能的索引。

### 列出技能

```bash
# 列出所有技能
copal skill registry list --skills-root .copal/skills

# 按语言过滤
copal skill registry list --skills-root .copal/skills --lang python
```

### 搜索技能

```bash
# 模糊搜索
copal skill search --skills-root .copal/skills --query "测试"

# 按语言搜索
copal skill search --skills-root .copal/skills \
  --query "部署" \
  --lang bash
```

### 执行技能

```bash
# 执行技能
copal skill exec --skills-root .copal/skills --skill my-skill

# 在沙箱中执行（如果技能要求）
copal skill exec --skills-root .copal/skills \
  --skill my-skill \
  --sandbox
```

### 技能生命周期

1. **创建** - 使用 `copal skill scaffold` 创建脚手架
2. **开发** - 实现脚本、测试和文档
3. **注册** - 运行 `copal skill registry build`
4. **发现** - 团队成员使用 `copal skill search` 查找
5. **执行** - 使用 `copal skill exec` 运行
6. **共享** - 提交到版本控制供团队重用

### Python API 使用

对于更丰富的模板支持，使用 Python API：

```python
from copal_cli.skills import scaffold_skill

scaffold_skill(
    name="advanced-skill",
    skills_root=".copal/skills",
    lang="python",
    description="高级自动化技能",
    force=False
)
```

## 记忆管理

记忆层在工作流运行之间持久化决策、经验和笔记。

### 记忆类型

- `decision` - 技术决策和选择
- `preference` - 团队偏好和约定
- `experience` - 经验教训和见解
- `plan` - 计划和策略
- `note` - 一般笔记和观察

### 添加记忆

```bash
# 记录决策
copal memory add \
  --type decision \
  --content "使用 PostgreSQL 作为主数据库" \
  --metadata reason="高性能和可靠性" \
  --metadata impact="high"

# 记录偏好
copal memory add \
  --type preference \
  --content "使用 Black 格式化 Python 代码" \
  --metadata scope="project-wide"

# 记录经验
copal memory add \
  --type experience \
  --content "Redis 连接池大小应该与工作进程数匹配" \
  --metadata severity="important"
```

### 搜索记忆

```bash
# 关键词搜索
copal memory search --query "数据库"

# 按类型搜索
copal memory search --query "认证" --type decision

# 搜索偏好
copal memory search --type preference
```

### 查看记忆详情

```bash
# 查看完整记录
copal memory show <memory-id>
```

输出包括：
- 内容和元数据
- 创建和更新时间
- 关系（如果有）

### 更新记忆

```bash
# 更新内容
copal memory update <memory-id> \
  --content "使用 PostgreSQL 14+ 作为主数据库"

# 更新元数据
copal memory update <memory-id> \
  --metadata version="14.5" \
  --metadata updated_reason="版本升级"
```

### 取代记忆

创建新记忆并与旧记忆建立 SUPERSEDES 关系：

```bash
copal memory supersede <old-memory-id> \
  --type decision \
  --content "迁移到 MongoDB 以获得更好的灵活性" \
  --metadata reason="需要更灵活的模式"
```

### 删除记忆

```bash
# 删除记忆及其所有关系
copal memory delete <memory-id>
```

### 列出记忆

```bash
# 列出所有记忆
copal memory list

# 按类型列出
copal memory list --type decision
```

### 记忆统计

```bash
# 查看记忆统计信息
copal memory summary
```

输出包括：
- 各类型记忆的数量
- 总记忆数
- 关系统计

### 配置记忆层

在 `.copal/memory-config.json` 中配置：

```json
{
  "backend": "networkx",
  "auto_capture": true,
  "scope_strategy": "workflow_run"
}
```

**配置选项：**
- `backend` - 存储后端（当前支持 `networkx`）
- `auto_capture` - 是否自动捕获每个阶段的记忆
- `scope_strategy` - 记忆作用域策略：
  - `workflow_run` - 每次工作流运行独立作用域
  - `global` - 全局作用域

## MCP 配置

Model Context Protocol (MCP) 钩子系统将工具特定的指导注入到阶段提示词中。

### 声明可用工具

在 `.copal/mcp-available.json` 中声明：

```json
["context7", "active-file", "file-tree"]
```

### 查看可用工具

```bash
copal mcp ls
```

### 配置钩子规则

在 `.copal/hooks/hooks.yaml` 中配置钩子规则：

```yaml
# context7 在分析阶段的使用指导
- id: context7-analysis
  stage: analysis
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.analysis.md

# context7 在计划阶段的使用指导
- id: context7-plan
  stage: plan
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.plan.md

# active-file 和 file-tree 在实现阶段的使用指导
- id: active-file-implement
  stage: implement
  all_mcp: ["active-file", "file-tree"]
  inject:
    - mcp/active-file/usage.implement.md
```

### 规则语法

**基本结构：**

```yaml
- id: unique-rule-id       # 唯一规则 ID
  stage: stage-name        # analysis/spec/plan/implement/review/commit
  any_mcp: [list]          # OR 逻辑；任一 MCP 存在时触发
  all_mcp: [list]          # AND 逻辑；所有 MCP 都存在时触发
  inject:                  # 要注入的钩子块列表
    - path/to/block.md
```

**条件逻辑：**
- `any_mcp` - 列表中至少一个工具可用时触发
- `all_mcp` - 列表中所有工具都可用时才触发

### 创建自定义钩子

1. **声明 MCP** - 添加到 `.copal/mcp-available.json`
2. **创建钩子块** - 在 `.copal/hooks/mcp/<tool>/usage.<stage>.md` 下创建 Markdown 文件
3. **添加路由规则** - 在 `.copal/hooks/hooks.yaml` 中引用该块
4. **测试** - 运行相关阶段命令并验证提示词包含新指导

### 内置钩子示例

**context7 - 分析阶段：**
- 路径：`.copal/hooks/mcp/context7/usage.analysis.md`
- 触发条件：分析阶段且 context7 可用
- 内容：如何研究库、收集背景知识、在分析产物中捕获发现

**context7 - 计划阶段：**
- 路径：`.copal/hooks/mcp/context7/usage.plan.md`
- 触发条件：计划阶段且 context7 可用
- 内容：确认 API、设计解决方案、记录依赖和版本

**active-file + file-tree - 实现阶段：**
- 路径：`.copal/hooks/mcp/active-file/usage.implement.md`
- 触发条件：实现阶段且 active-file 和 file-tree 都可用
- 内容：定位文件、应用更改、编写测试、捕获补丁说明

## 更新模板

### 同步最新模板

```bash
# 拉取最新的 CoPal 仓库
cd /path/to/CoPal
git pull origin main

# 重新安装
pip install -e .

# 在项目中刷新模板
cd /path/to/your-project
copal init --force
```

### 注意事项

- 保持共享模板通用；将项目特定的详细信息存储在您自己的文档中
- 为任何自定义知识库更新维护变更日志，以便团队成员了解更改内容
- 在更新前备份自定义内容

## 最佳实践

### 1. 工作流管理

- **按顺序执行阶段** - 按照 analyze → spec → plan → implement → review → commit 顺序
- **捕获产物** - 每个阶段在 `.copal/artifacts/` 中创建产物
- **使用状态命令** - 定期运行 `copal status` 检查进度
- **恢复中断的工作** - 使用 `copal resume` 恢复

### 2. 知识库管理

- **最小化覆盖** - 仅覆盖确实需要自定义的模板
- **版本控制** - 将自定义知识库文件提交到版本控制
- **文档链接** - 在 `UserAgents.md` 中清楚地链接所有自定义文档
- **定期同步** - 定期从 CoPal 同步最新的共享模板

### 3. 技能开发

- **文档化要求** - 在 `prelude.md` 中详细记录运行时要求
- **包含测试** - 为技能添加测试以确保可靠性
- **使用沙箱** - 对敏感操作标记 `requires_sandbox: true`
- **版本化技能** - 在 `skill.json` 中包含版本信息
- **共享注册表** - 提交 `registry.json` 以便团队发现

### 4. 记忆使用

- **及时记录** - 在做出决策时立即记录
- **添加上下文** - 使用元数据提供额外上下文
- **定期审查** - 定期审查和更新记忆
- **使用类型** - 适当地使用不同的记忆类型
- **建立关系** - 使用 supersede 建立决策演变链

### 5. MCP 集成

- **声明工具** - 在 `.copal/mcp-available.json` 中声明所有可用工具
- **阶段特定指导** - 为不同阶段创建特定的使用指导
- **测试钩子** - 验证钩子在正确的阶段触发
- **保持简洁** - 钩子内容应简洁且切中要点

### 6. 团队协作

- **共享配置** - 提交 `.copal/` 配置到版本控制
- **统一规范** - 在 `UserAgents.md` 中记录团队约定
- **技能共享** - 共享和重用团队技能
- **记忆共享** - 使用全局作用域共享重要决策

## 验证

使用 `copal validate` 确保知识库文件具有正确的前置元数据：

```bash
# 验证默认知识库
copal validate --target .copal/global

# 验证自定义知识库
copal validate --target docs/agents/knowledge-base

# 使用自定义模式
copal validate --target .copal/global --pattern "**/*.md"
```

## 故障排除

### 问题：init 命令失败

**解决方案：**
- 检查目标目录是否存在且可写
- 使用 `--verbose` 查看详细错误信息
- 使用 `--dry-run` 预览操作

### 问题：找不到 MCP 工具

**解决方案：**
- 检查 `.copal/mcp-available.json` 是否存在
- 验证 JSON 格式是否正确
- 使用 `copal mcp ls` 验证配置

### 问题：记忆搜索无结果

**解决方案：**
- 检查记忆是否在当前作用域
- 尝试不同的搜索关键词
- 使用 `copal memory list` 查看所有记忆

### 问题：技能执行失败

**解决方案：**
- 检查 `skill.json` 格式是否正确
- 验证 `prelude.md` 中的要求是否满足
- 使用 `--sandbox` 如果技能标记为需要沙箱
- 检查日志文件中的错误信息

## 获取帮助

- **命令帮助** - 使用 `copal <command> --help` 获取命令帮助
- **文档** - 查看 [docs/](../docs/) 目录中的其他文档
- **问题** - 在 [GitHub Issues](https://github.com/royisme/CoPal/issues) 提交问题
- **示例** - 查看 [examples/](../examples/) 目录中的示例

## 下一步

- 阅读 [HOOKS.md](./HOOKS.md) 了解 MCP 钩子系统详情
- 阅读 [DEVELOPMENT.md](./DEVELOPMENT.md) 了解开发和贡献指南
- 查看 [CHANGELOG.md](./CHANGELOG.md) 了解最新更新
