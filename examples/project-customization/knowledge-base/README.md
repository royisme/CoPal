# 自定义知识库占位

在此目录中，你可以按照 `.copal/global/knowledge-base` 的结构创建自定义文档，例如：

- `core/environment.md`：补充项目专属命令或审批策略；
- `roles/implementer.md`：说明前端/后端等不同子团队的约定；
- `workflows/deployment.md`：记录发布流程；
- `toolsets/cli/custom-cli.md`：介绍内部工具或脚本。

建议保留与 global 同名的文件结构，以便 agent 在加载时按约定覆盖默认模板。
