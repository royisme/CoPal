# CoPal 快速开始指南

5分钟快速上手 CoPal！

## 步骤 1：安装 CoPal

```bash
# 克隆仓库
git clone https://github.com/royisme/CoPal.git
cd CoPal

# 安装
pip install -e .
```

## 步骤 2：初始化项目

在您的项目根目录中：

```bash
cd /path/to/your-project
copal init --target .
```

这会创建：
- `AGENTS.md` - AI 助手的导航指南
- `UserAgents.md` - 项目特定指导
- `.copal/` - 知识库和配置目录

## 步骤 3：自定义项目（可选）

编辑 `UserAgents.md` 添加项目特定的信息：

```markdown
# 用户代理指导

## 项目结构
本项目使用 Python + FastAPI...

## 开发规范
- 使用 Black 格式化代码
- 测试覆盖率必须 > 80%
```

## 步骤 4：运行第一个工作流

```bash
# 1. 分析任务
copal analyze --title "添加用户注册" --goals "实现用户注册功能"

# 2. 编写规范（AI 助手会读取提示词并创建规范）
# 查看生成的提示词：.copal/runtime/analysis.prompt.md
# AI 助手应创建：.copal/artifacts/analysis.md

# 3. 继续其他阶段
copal spec      # 编写规范
copal plan      # 制定计划
copal implement # 实现功能
copal review    # 代码审查
copal commit    # 提交记录

# 4. 查看进度
copal status
```

## 步骤 5：配置 MCP 工具（可选）

如果您使用 context7 或其他 MCP 工具：

```bash
# 声明可用工具
cat <<'JSON' > .copal/mcp-available.json
["context7", "active-file", "file-tree"]
JSON

# 查看已配置的工具
copal mcp ls
```

## 常用命令速查

### 工作流命令
```bash
copal analyze           # 分析阶段
copal spec             # 规范阶段
copal plan             # 计划阶段
copal implement        # 实现阶段
copal review           # 审查阶段
copal commit           # 提交阶段
copal status           # 查看状态
copal resume           # 恢复工作流
```

### 技能命令
```bash
copal skill scaffold my-skill --lang python   # 创建技能
copal skill registry build                     # 构建注册表
copal skill search --query "测试"              # 搜索技能
copal skill exec --skill my-skill             # 执行技能
```

### 记忆命令
```bash
copal memory add --type decision --content "..." # 添加记忆
copal memory search --query "认证"               # 搜索记忆
copal memory list --type decision               # 列出决策
copal memory show <id>                          # 查看详情
```

## 工作流示例

### 示例：添加新功能

```bash
# 1. 分析需求
copal analyze \
  --title "添加 OAuth2 登录" \
  --goals "支持 Google 和 GitHub OAuth2 登录" \
  --constraints "保持与现有认证系统兼容"

# AI 助手读取 .copal/runtime/analysis.prompt.md
# AI 助手创建 .copal/artifacts/analysis.md

# 2. 编写规范
copal spec
# AI 助手读取提示词，创建 .copal/artifacts/spec.md

# 3. 制定计划
copal plan
# AI 助手读取提示词，创建 .copal/artifacts/plan.md

# 4. 实现功能
copal implement
# AI 助手按计划实现，创建 .copal/artifacts/patch-notes.md

# 5. 代码审查
copal review
# AI 助手审查代码，创建 .copal/artifacts/review.md

# 6. 记录元数据
copal commit
# AI 助手记录元数据到 .copal/artifacts/commit-metadata.json

# 7. 查看完整状态
copal status
```

## 记忆管理示例

```bash
# 记录技术决策
copal memory add \
  --type decision \
  --content "使用 Redis 作为会话存储" \
  --metadata reason="高性能和持久化支持"

# 搜索相关决策
copal memory search --query "Redis"

# 更新决策
copal memory update <id> --content "使用 Redis 7+ 作为会话存储"

# 取代旧决策
copal memory supersede <id> \
  --type decision \
  --content "迁移到 Valkey（Redis 的分支）"
```

## 技能管理示例

```bash
# 创建部署技能
copal skill scaffold deployment \
  --skills-root .copal/skills \
  --lang bash \
  --description "自动化部署到生产环境"

# 开发技能...
# 编辑 .copal/skills/deployment/scripts/deploy.sh
# 编辑 .copal/skills/deployment/prelude.md

# 构建注册表
copal skill registry build --skills-root .copal/skills

# 团队成员搜索技能
copal skill search --query "部署"

# 执行技能
copal skill exec --skills-root .copal/skills --skill deployment
```

## 目录结构

初始化后的项目结构：

```
your-project/
├── AGENTS.md                    # AI 助手导航
├── UserAgents.md               # 项目特定指导
├── .copal/
│   ├── global/                 # 共享知识库
│   │   └── knowledge-base/
│   │       ├── core/           # 核心原则
│   │       ├── roles/          # 角色模板
│   │       ├── workflows/      # 工作流指南
│   │       └── toolsets/       # 工具集
│   ├── hooks/                  # MCP 钩子
│   │   ├── hooks.yaml         # 钩子配置
│   │   └── mcp/               # MCP 工具指导
│   ├── mcp-available.json     # 可用 MCP 工具
│   ├── runtime/               # 运行时提示词（自动生成）
│   ├── artifacts/             # 工作流产物（自动生成）
│   ├── skills/                # 技能库（可选）
│   └── memory/                # 记忆存储（可选）
└── [您的项目文件]
```

## 最佳实践提示

1. **按顺序执行阶段** - 始终按照 analyze → spec → plan → implement → review → commit 顺序
2. **保存产物** - AI 助手应将每个阶段的结果保存在 `.copal/artifacts/` 中
3. **使用记忆** - 记录重要决策和经验，便于后续参考
4. **共享技能** - 将有用的自动化封装为技能，供团队重用
5. **定期同步** - 定期运行 `copal init --force` 获取最新的模板更新

## 下一步

- 📖 阅读[完整使用指南](./USAGE_CN.md)了解所有功能
- 🔧 查看[开发指南](./DEVELOPMENT.md)了解如何贡献
- 🎯 探索[示例](../examples/)了解高级用法
- 💡 查看[MCP 钩子文档](./HOOKS.md)了解工具集成

## 需要帮助？

- 使用 `copal <command> --help` 查看命令帮助
- 查看 [GitHub Issues](https://github.com/royisme/CoPal/issues) 提问或报告问题
- 阅读[完整文档](./USAGE_CN.md)获取详细说明

祝使用愉快！🚀
