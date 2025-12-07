# 重构对齐审查：问题与修复清单

## 已发现问题（按严重度）
- **阻断**：CLI 适配器列表与规范不符  
  - `copal_cli/cli.py` 仍暴露 `cursor/generic`，缺 `gemini`，与文档“仅支持 claude/codex/gemini”冲突。
  - Manifest 生成仍使用 `tools` 字段，解析器只识别 `adapters`，导致适配器配置失效；模板 `templates/v1/manifest.yaml` 也未包含 codex/gemini 和 memory。
- **阻断**：Init 交互未切换 Rich TUI  
  - `copal_cli/harness/init.py` 依旧使用 InquirerPy，未实现 Rich 交互要求。
- **阻断**：初始化资产不完整  
  - 从 `templates/v1` 复制的 pack/doc 结构未覆盖新规范所需的 AGENTS/UserAgents/hooks/docs（repo_map/build/test 等），manifest 模板也缺适配器和 memory 配置。
- **重大**：Memory Layer 与设计不符  
  - 当前 JSON 存储只是平铺 `index.json`，无“主干 + 分支”模型、元数据、合并/回写策略，未落地文档中的 memory 设计。
- **重大**：校验/导出仍宽松  
  - `validate` 不检查 pack 声明的 workflows/prompts/schemas/scripts 是否存在；适配器导出缺文件时仅 warning 不失败，违背“缺资产即 fail”要求。
- **文档偏差**：README/README_CN 示例字段（tools/memory）与实际解析/模板不一致，易误导用户生成无效配置。

## 修复清单（建议顺序）
1) **CLI 与 manifest 对齐**
   - CLI 只暴露 `claude/codex/gemini`；移除 `cursor/generic` 选项。
   - Manifest 统一使用 `adapters` + `memory` 块；更新模板、解析器、示例。
2) **Init 交互改为 Rich TUI**
   - 用 Rich 实现工具/增强选择；移除 InquirerPy 依赖。
3) **模板与资产补齐**
   - base/AGENTS/UserAgents/hooks/docs 采用新工程循环和 memory 指南。
   - `templates/v1/engineering_loop` 保持完整的 workflows/prompts/schemas/templates/scripts/docs；manifest 模板包含 claude/codex/gemini 与 memory。
4) **校验与导出加严**
   - `validate` 检查 pack 声明的所有资源存在性；缺失即失败。
   - 适配器导出时缺文件直接失败，不再静默。
5) **Memory Layer 落地**
   - 定义主干/分支存储结构、索引/元数据格式、分支合并策略；在 memory CLI 和 workflow prompt 中示例化读写。
   - 按“项目记忆 vs 任务记忆”分层：  
     - 项目记忆（主干）：跨任务长期知识，存放架构/约定/依赖/坑点/流程等；只读为主，Codify 阶段沉淀。  
     - 任务记忆（分支）：单任务上下文，记录 Plan/Research/Confirm/Work/Review/Codify 关键输出，任务结束精选合并到项目记忆。  
   - 数据结构示例：  
     - `.copal/memory/index.json`：主干+分支元数据、活跃分支指针。  
     - `.copal/memory/branches/<task_id>/meta.json`、`entries/*.md|json`、`summary.md`。  
     - 项目记忆按主题拆分：`.copal/memory/project/{architecture,conventions,pitfalls,dependencies,release}.md`。  
   - 读写策略：  
     - 各阶段 prompt 要求：Plan/Research/Confirm/Work/Review/Codify 读任务摘要+项目记忆；写关键决策/测试/风险/确认状态。  
     - Codify 阶段从任务摘要提炼可复用知识合并到项目记忆，原分支归档。  
     - 控制噪声：只存决策/结论/失败原因/测试结果，避免流水对话。
6) **文档同步**
   - README/README_CN 与 AGENTS 示例同步到新字段/新流程/受支持适配器。
7) **测试补齐**
   - 针对新 init/export/validate/memory 的正反例测试；覆盖缺资产/缺 schema/适配器缺文件等失败路径。 
