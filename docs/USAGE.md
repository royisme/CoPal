# CoPal 使用指南

## 1. 安装方式（原型阶段）

目前提供 Python 包原型，可通过 `pip install -e` 在本地安装；也可直接复制源代码。

```bash
pip install -e ./CoPal
# 或者在子模块路径执行
pip install -e tools/copal
```

## 2. 初始化

在目标项目根目录执行：

```bash
copal init --target .
```

选项说明：
- `--target`：目标仓库路径，默认当前目录；
- `--force`：如已存在相同文件/目录，强制覆盖。

执行后会生成：

- `AGENTS.md`：索引模板；
- `UserAgents.md`：项目自定义占位文件；
- `.copal/global/`：CoPal 提供的通用知识库。

`.copal/` 目录通常视为只读，后续更新可通过重新运行 `copal init --force` 或 `git submodule update` 获得。

## 3. 自定义步骤

1. 编辑 `AGENTS.md`，在“项目自定义”列补充具体文档链接；
2. 将项目特有的规范写入 `UserAgents.md`，并在仓库其它位置创建/维护相关文档；
3. （可选）复制 `.copal/global/knowledge-base` 中的结构，创建同名文件覆盖默认说明；
4. 如需 Prompt 模板，可在项目自定义目录自建并在 `UserAgents.md` 链接。

## 4. agent 加载策略

代理启动时建议按以下顺序读取：

1. 根目录 `AGENTS.md`（确定导航）；
2. `.copal/global/knowledge-base`（通用模板）；
3. `UserAgents.md`（列出项目自定义内容）；
4. `UserAgents.md` 中引用的其它文档（specs/docs/tasks 等）。

## 5. 更新模板

- CoPal 仓库更新后，可使用 `git submodule update` 或重新运行 `init`（搭配 `--force`）同步；
- 公共模板的改动必须保持通用性，避免写入具体技术细节；
- 项目专属改动应在 `UserAgents.md` 及其引用的文档中维护。

## 6. 未来扩展

- 发布 Python 包（如 `pip install copal-cli`），提供 `copal init` 命令；
- 支持 `copal update`、`copal doctor` 等维护工具；
- 引入 schema 校验与 front matter 检查脚本；
- 适配更多 CLI（例如 Cursor CLI、Gemini CLI 等）。

## 7. 技能生命周期（Skillization）

CoPal 新增 `copal skill` 系列命令，用于管理可复用的自动化技能。完整流程如下：

### 7.1 注册表与检索

```bash
copal skill registry            # 查看已配置的技能注册表
copal skill search lint         # 按名称、标签、所有者或描述检索
```

- 默认注册表为 `.copal/registry.yaml`，会定期与远程源同步。
- 可通过环境变量 `COPAL_SKILL_REGISTRY` 指定额外的企业内网源，或在 `UserAgents.md` 中声明自定义路径。

### 7.2 脚手架与 `prelude.md`

```bash
copal skill scaffold sample/hello-world --target skills/sample
copal skill scaffold sample/hello-world --prelude prelude.md
```

- `--target`：将技能的 `skill.yaml`、入口提示、守卫策略复制到本地目录。
- `--prelude <路径>`：生成 `prelude.md`，记录输入参数、依赖、沙箱要求与运行说明。建议将该文件与任务说明一起提交，供后续贡献者复用。

### 7.3 沙箱保障

技能清单包含 `sandbox.mode` 字段，支持：

- `replay`：只读模拟，不写入磁盘；
- `reuse`：复用隔离环境（默认）；
- `fresh`：每次执行均创建全新容器。

执行时必须提供不弱于清单要求的模式，例如：

```bash
copal skill exec sample/hello-world --prelude prelude.md --sandbox reuse
```

若传入的 `--sandbox` 低于清单声明，CLI 将拒绝执行并给出提示。建议在 `prelude.md` 中记录实际使用的模式，便于审计。

### 7.4 执行与复用示例

1. `copal skill search markdown` → 定位 `sample/doc-lint`。
2. `copal skill scaffold sample/doc-lint --target skills/doc-lint --prelude prelude.md` → 获取脚手架与交接文件。
3. 编辑 `skills/doc-lint/skill.yaml`，设置 `args.path=docs/`。
4. `copal skill exec sample/doc-lint --prelude prelude.md --args "--path docs/"` → 在守护的沙箱中运行。
5. 将生成的 `usage/` 日志和 `prelude.md` 一并附在 PR 描述或回顾笔记中。

通过 `prelude.md` 和统一沙箱策略，团队可实现“写一次脚手架，多次复用执行”的技能化交付。
