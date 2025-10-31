# 项目自定义指引

该目录用于存放**项目专属**的角色指引、流程说明、技术栈规范等内容。建议结构：

```
UserAgents.md                        # 项目自定义入口
docs/agents/                         # 供示例使用的扩展文档（可自定义路径）
└── knowledge-base/                  # 如需覆盖通用模板，可复制结构
    ├── core/
    ├── roles/
    ├── workflows/
    └── toolsets/
```

推荐步骤：

1. `copal init` 后，编辑 `UserAgents.md`，概述项目结构、命令、审批策略；
2. 如需覆盖默认知识库，可复制 `.copal/global/knowledge-base` 的结构到 `docs/agents/knowledge-base`；
3. 在 `UserAgents.md` 中链接上述文档，并在 `AGENTS.md` 的“项目自定义”列指向 `UserAgents.md`；
4. 将自定义文档纳入版本管理，定期更新以反映最新实践。

> 若项目已有既定文档体系，可在此处仅保留链接或索引，确保 agent 可以快速定位信息。
