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
