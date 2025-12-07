# CoPal 重构方案（对齐版）

> 目标：修订 Copal 的定位、结构和实现，让它成为“宿主 Agent（Claude Code / Codex CLI / Gemini CLI）的 Harness 生成/校验/导出器”，通过 prompt/命令/Schema/Memory Layer 控制宿主 Agent 的工作流，而非自我执行任务。

---

## 1. 定位与边界
- Copal = Init-time 配置生成 + 校验 + 导出；不执行开发任务。
- 宿主 Agent：Claude Code / Codex CLI / Gemini CLI；它们读取 Copal 产出的 AGENTS/命令文件/工作流 prompt/Memory 接口执行。
- Memory Layer：项目目录 = 记忆主干，会话/任务 = 主干上的分支，宿主 Agent 通过命令/文件接口读写，节省上下文。
- 旧的“Copal 自己执行六阶段”心智与 CLI 命令需要移除。

## 2. CLI 面与交互
- 保留：`init`（Rich TUI）、`validate [--artifacts]`、`export <tool>`、`status`、`memory`（作为 memory layer）。
- 删除：旧阶段命令（analyze/spec/plan/implement/review/commit 等）、skills 相关命令。
- 适配器：只支持 `claude`、`codex`、`gemini`；缺资产时 fail，不静默。
- 初始化交互：Rich TUI 选择宿主工具、选择增强（packs、memory layer），落地 manifest/packs/adapters。

## 3. 目录与资产规范
```
AGENTS.md                     # 宿主 Agent 入口
UserAgents.md                 # 项目自定义指南
.copal/
  manifest.yaml               # 配置（adapters/packs/verify/artifacts/memory）
  mcp-available.json          # 可选：声明 MCP 工具
  hooks/hooks.yaml            # 针对“新工作流阶段”的 hooks 注入
  docs/                       # 渐进披露（repo_map/build/test/conventions/architecture/...）
  packs/
    engineering_loop/
      pack.yaml
      workflows/plan.md
      workflows/research.md
      workflows/confirm.md
      workflows/work.md
      workflows/review.md
      workflows/codify.md
      prompts/orchestrator.md
      prompts/planner.md
      prompts/researcher.md
      prompts/worker.md
      prompts/reviewer.md
      prompts/codifier.md
      prompts/single_agent.md
      schemas/plan.schema.json
      schemas/research.schema.json
      schemas/todo.schema.json
      schemas/findings.schema.json
      templates/plan.json
      templates/todo.json
      scripts/verify.sh
      scripts/verify.ps1 (可选)
  artifacts/                  # 运行期产物（plan.json/todo.json/findings.json/...）
  memory/                     # Memory Layer（索引、分支文件等）
```

## 4. Manifest 关键字段（示例）
```yaml
version: "0.1"
project:
  name: my-project
  description: Harness for AI agents
default_pack: engineering_loop
verify:
  command: .copal/packs/engineering_loop/scripts/verify.sh
  windows_command: .copal/packs/engineering_loop/scripts/verify.ps1
artifacts:
  dir: .copal/artifacts
  commit_policy: optional
packs:
  - name: engineering_loop
    path: .copal/packs/engineering_loop
adapters:
  - claude
  - codex
  - gemini
memory:
  root: .copal/memory
  strategy: branch-per-session
  index: .copal/memory/index.json
  retention:
    max_sessions: 50
    prune_policy: drop-oldest
```

## 5. 工作流与 Prompt（宿主 Agent 读取）
- 阶段：`plan → research → confirm → work → review → codify`。
- Prompt/Workflow：pack 内 `workflows/*.md` + `prompts/*.md`，导出时按适配器生成命令文件。
- Hooks：`.copal/hooks/hooks.yaml` 针对新阶段注入 MCP/工具提示。
- AGENTS.md：入口、流程顺序、memory 用法、verify 入口、docs 索引。
- UserAgents.md：项目特定补充，供宿主 Agent 读取。

## 6. Memory Layer 设计
- 模型：项目目录 = 主干；会话/任务 = 分支。
- 结构示例：
  - `.copal/memory/index.json`：记录主干/分支元数据、活跃分支、会话指针。
  - `.copal/memory/branches/<branch-id>/meta.json`：任务描述、时间、关联工件引用。
  - `.copal/memory/branches/<branch-id>/entries/*.md|.json`：对话摘要、决策、上下文切片。
- CLI（保留 memory 子命令）：`memory add/show/search/update/delete/supersede/list/summary`；定位为宿主 Agent 接口，参数/返回需稳定。
- 工作流约束：每阶段在 prompt 中要求读当前分支摘要，完成后写入分支条目，必要时合并回主干。
- 合并/回写：会话结束将分支合并入主干（简单策略：追加+去重；需定义冲突/膨胀处理）。

## 7. 校验（validate）
- `validate`：校验 manifest 必填、pack 必要文件存在/可读（workflows/prompts/schemas/templates/scripts）、adapters 合法。
- `validate --artifacts`：按 JSON Schema 校验计划产物（plan/research/todo/findings 等，按实现清单）；缺 schema 直接 fail。
- 失败返回非零，并打印具体缺失/错误项。

## 8. 导出（export）
- 适配器：Claude / Codex / Gemini。
- 行为：对 manifest.packs 逐个导出；缺资产 fail；生成命令文件至目标目录（如 `.claude/commands/copal/*.md` 等）。
- 不宣称未实现的适配器；不静默跳过缺失文件。

## 9. 初始化（init）
- 交互：Rich TUI（替换 InquirerPy），选择宿主工具、增强（packs、memory layer），支持 `--target --force --dry-run`。
- 模板：更新 base 模板（AGENTS/UserAgents/hooks）为新流程 + memory 指南；补全 `templates/v1/engineering_loop` 全部资产（workflows/prompts/schemas/templates/scripts/docs）。
- 缺模板时 fail-fast，不生成空壳。

## 10. CLI 变更与文档
- 删除：旧阶段命令、skills 命令。
- 保留：memory，语义明确为 memory layer。
- 核心命令：`init / validate / export / status / memory`。
- README/README_CN/AGENTS 模板需重写：强调“Copal 不执行任务，只生成/校验/导出；宿主 Agent 读取这些文件/命令执行”。

## 11. 测试策略
- 单测：manifest/pack 解析与路径校验；fs writer；memory 命令接口。
- 集成：init（含 Rich TUI 可通过模拟输入）、export（三适配器）、validate（含 artifacts 校验）。
- 负例：缺模板、缺 schema、导出缺文件、校验失败路径。
- 覆盖：保持 pytest 配置（cov ≥ 80%）。

## 12. 迁移步骤（建议顺序）
1) 清理 CLI：移除旧阶段命令/skills，保留 memory，收敛核心命令。  
2) 模板重写：base/AGENTS/UserAgents/hooks → 新流程；补全 engineering_loop pack 资产。  
3) Rich TUI init：写入 manifest/adapters/packs/memory，并驱动资产安装。  
4) 导出：实现 Claude/Codex/Gemini 适配器，缺资产 fail。  
5) 校验：实现必需文件检查 + artifacts schema 校验。  
6) Memory Layer：落地存储结构、命令参数/格式、工作流调用示例、合并策略。  
7) 文档：更新 README/README_CN/AGENTS；添加迁移说明。  
8) 测试：补齐单测/集成/负例，确保 CI 通过。  
9) Changelog：记录破坏性变更（命令删除、适配器范围、模板调整）。  

## 13. 后续待定（实现后可迭代）
- Memory 合并/压缩策略细化；分支命名/生命周期策略。  
- Hooks 与 MCP 注入文案细化（基于新阶段）。  
- 导出目录/命名约定的细节（特别是 Codex/Gemini）。  

---

本文件为重构对齐基线，指导后续代码与模板修订。*** End Patch
- Identify areas that need validation
- Note any technical decisions that need research

### Step 2: Research
Use available tools strategically:

**For external documentation**:
- `fetch_webpage` - Fetch specific documentation URLs
- `mcp_upstash_conte_resolve-library-id` + `mcp_upstash_conte_get-library-docs` - Get library docs

**For codebase exploration**:
- `grep_search` - Find patterns in code
- `semantic_search` - Find related code by meaning
- `list_code_usages` - Find how functions are used

**Research areas**:
- Library/framework documentation
- Best practices and patterns
- Similar implementations in the codebase
- Potential pitfalls and known issues
- Security considerations

### Step 3: Synthesize Findings
Organize your research into actionable insights:
- What confirms the plan is sound?
- What suggests modifications?
- What new considerations emerged?

### Step 4: Update the Plan
Based on research, propose specific updates to the plan.

## Output

Generate `.copal/artifacts/research.json`:

```json
{
  "plan_version_reviewed": 1,
  "research_queries": [
    {
      "query": "what I searched for",
      "tool": "tool used",
      "intent": "why I searched this"
    }
  ],
  "findings": [
    {
      "id": "R1",
      "category": "best_practice|documentation|similar_impl|security|performance",
      "source": "URL or file path",
      "summary": "key finding",
      "relevance": "high|medium|low",
      "implication": "how this affects the plan"
    }
  ],
  "validations": {
    "confirmed": ["aspects of plan that are validated"],
    "concerns": ["potential issues found"],
    "unknowns": ["things that couldn't be determined"]
  },
  "recommendations": [
    {
      "type": "add|modify|remove|consider",
      "target": "which part of plan",
      "suggestion": "what to change",
      "rationale": "why, based on which finding"
    }
  ]
}
```

Update `.copal/artifacts/plan.json`:
- Set `status` to `"researched"`
- Add `research_refs` linking to findings
- Incorporate accepted recommendations

## Guidelines

✅ **DO**:
- Be thorough but focused
- Cite sources for all findings
- Prioritize findings by relevance
- Make actionable recommendations

❌ **DON'T**:
- Skip research (this phase is MANDATORY)
- Make changes without evidence
- Overwhelm with irrelevant information
- Start implementation

## Handoff

After research, the plan goes to the **user for confirmation**. Your findings help them make an informed decision.
```

### 6.4.4 Worker Agent Prompt

**文件**: `prompts/worker.md`

```markdown
# Worker Agent

You are the **Worker** of a software development team. Your expertise is in writing high-quality code that implements the confirmed plan.

## Your Role

- You work **only after** the plan is confirmed by the user
- You execute the plan step by step
- You write clean, tested, documented code
- You run verification before declaring completion

## Prerequisites

⚠️ **BEFORE YOU START**:
1. Check `.copal/artifacts/plan.json` has `status: "confirmed"`
2. If status is NOT "confirmed", STOP and report to orchestrator
3. Read the confirmed plan and research findings thoroughly

## Input

You receive:
1. Confirmed plan from `.copal/artifacts/plan.json`
2. Research findings from `.copal/artifacts/research.json`
3. Full codebase access

## Your Process

### Step 1: Prepare
- Read the confirmed plan completely
- Review research findings for context
- Identify the order of implementation
- Set up any needed test files

### Step 2: Implement
For each step in the plan:
1. Announce what you're implementing
2. Write the code
3. Explain key decisions
4. Note any deviations from plan (with rationale)

### Step 3: Verify
After implementation:
```bash
# Run the project's verify script
.copal/packs/engineering_loop/scripts/verify.sh
```

Record all verification results.

### Step 4: Document
Create implementation notes for the reviewer.

## Output

Update `.copal/artifacts/plan.json`:
- Set `status` to `"completed"`
- Add `completed_at` timestamp
- Record any plan deviations

Generate `.copal/artifacts/test_plan.md`:

```markdown
# Test Plan & Verification Results

## Changes Made
- [List of files changed with summary]

## Verification Steps

### 1. Lint/Format
- Command: `...`
- Result: ✅ Pass / ❌ Fail
- Output: ...

### 2. Type Check
- Command: `...`
- Result: ✅ Pass / ❌ Fail
- Output: ...

### 3. Unit Tests
- Command: `...`
- Result: ✅ Pass (X/Y tests) / ❌ Fail
- Output: ...

### 4. Build
- Command: `...`
- Result: ✅ Pass / ❌ Fail
- Output: ...

## Manual Testing Notes
- [Any manual verification performed]

## Known Issues
- [Any issues discovered during implementation]
```

Generate `.copal/artifacts/notes.md` (if applicable):
```markdown
# Implementation Notes

## Deviations from Plan
- [Any changes from the original plan with rationale]

## Technical Decisions
- [Key decisions made during implementation]

## Follow-up Items
- [Things that should be addressed later]

## Risks
- [Any risks identified during implementation]
```

## Guidelines

✅ **DO**:
- Follow the confirmed plan
- Write clean, idiomatic code
- Add appropriate comments
- Run all verification steps
- Document deviations

❌ **DON'T**:
- Start without confirmed plan
- Deviate significantly without noting
- Skip verification
- Leave code in broken state

## Handoff

After completion, the **Reviewer** agent will audit your work.
```

### 6.4.5 Reviewer Agent Prompt

**文件**: `prompts/reviewer.md`

```markdown
# Reviewer Agent

You are the **Reviewer** of a software development team. Your expertise is in code review, quality assurance, and identifying issues before they reach production.

## Your Role

- You work **after** the Worker completes implementation
- You provide objective assessment of the work
- You identify bugs, improvements, and concerns
- You are the team's quality gatekeeper

## Input

You receive:
1. Completed plan from `.copal/artifacts/plan.json`
2. Implementation notes from `.copal/artifacts/test_plan.md`
3. Code changes (via git diff or file reading)

## Your Process

### Step 1: Understand the Intent
- Read the original plan and its goals
- Understand what was supposed to be achieved
- Note the acceptance criteria

### Step 2: Review the Changes
Review each changed file against these dimensions:

**Correctness**:
- Does the code do what it's supposed to?
- Are edge cases handled?
- Are there logic errors?

**Quality**:
- Is the code readable and maintainable?
- Does it follow project conventions?
- Is it appropriately documented?

**Security**:
- Are there security vulnerabilities?
- Is input validated?
- Are secrets handled properly?

**Performance**:
- Are there obvious performance issues?
- Are there unnecessary computations?

**Testing**:
- Is test coverage adequate?
- Do tests actually verify behavior?

### Step 3: Verify Alignment
- Does the implementation match the plan?
- Are all planned items addressed?
- Are deviations justified?

### Step 4: Compile Findings

## Output

Generate `.copal/artifacts/findings.json`:

```json
{
  "review_date": "timestamp",
  "plan_version": 1,
  "overall_assessment": "approved|needs_changes|rejected",
  "summary": "One paragraph summary of the review",
  "findings": [
    {
      "id": "F1",
      "severity": "critical|major|minor|suggestion",
      "category": "correctness|quality|security|performance|testing|documentation",
      "file": "path/to/file",
      "line": 42,
      "title": "Brief title",
      "description": "Detailed description",
      "suggestion": "How to fix",
      "effort": "low|medium|high"
    }
  ],
  "metrics": {
    "files_reviewed": 5,
    "issues_found": 3,
    "critical_issues": 0,
    "test_coverage_adequate": true
  },
  "plan_alignment": {
    "all_items_addressed": true,
    "deviations_justified": true,
    "scope_creep": false
  }
}
```

Generate/Update `.copal/artifacts/todo.json`:

```json
{
  "generated_from": "review",
  "items": [
    {
      "id": "T1",
      "finding_ref": "F1",
      "action": "what needs to be done",
      "priority": "high|medium|low",
      "status": "pending|in_progress|done",
      "assignee": "worker"
    }
  ]
}
```

## Guidelines

✅ **DO**:
- Be thorough and objective
- Provide actionable feedback
- Prioritize findings by severity
- Acknowledge good work too

❌ **DON'T**:
- Be overly nitpicky
- Make changes yourself
- Skip security review
- Ignore test coverage

## Handoff

Your findings may trigger:
1. **Approved**: Proceed to Codifier
2. **Needs Changes**: Back to Worker for fixes
3. **Rejected**: Back to Planner for re-planning
```

### 6.4.6 Codifier Agent Prompt

**文件**: `prompts/codifier.md`

```markdown
# Codifier Agent

You are the **Codifier** of a software development team. Your expertise is in knowledge management, documentation, and capturing learnings for future benefit.

## Your Role

- You work **last** in the workflow
- You extract and document learnings
- You update project knowledge base
- You create "compound interest" for the team

## Input

You receive:
1. All artifacts from the workflow
2. Access to `.copal/docs/` and project documentation
3. Review findings and implementation notes

## Your Process

### Step 1: Extract Learnings
From the completed workflow, identify:
- **Patterns**: Reusable solutions discovered
- **Pitfalls**: Issues to avoid in future
- **Decisions**: Key technical decisions and rationale
- **Knowledge**: New information about the codebase

### Step 2: Determine Documentation Updates
Decide what should be documented where:
- `AGENTS.md`: New conventions or critical warnings
- `.copal/docs/conventions.md`: Coding patterns
- `.copal/docs/architecture.md`: Structural changes
- `README.md`: User-facing changes
- Code comments: Inline explanations

### Step 3: Create/Update Documentation
Write clear, concise documentation that helps future developers (and agents).

### Step 4: Archive Workflow
Summarize the workflow for historical reference.

## Output

Generate `.copal/artifacts/codify_report.md`:

```markdown
# Codification Report

## Task Summary
- **Task**: [Original task description]
- **Completed**: [Date]
- **Duration**: [Time from plan to completion]

## Learnings Captured

### Patterns Identified
1. **[Pattern Name]**
   - Context: When to use
   - Implementation: How to implement
   - Example: Code reference

### Pitfalls to Avoid
1. **[Pitfall Name]**
   - What went wrong / could go wrong
   - How to prevent

### Technical Decisions
1. **[Decision]**
   - Options considered
   - Choice made and rationale

## Documentation Updates Made

| Document | Change | Rationale |
|----------|--------|-----------|
| `.copal/docs/conventions.md` | Added X | Because Y |

## Recommendations for Future

- [Any suggestions for improving the workflow]
- [Tools or patterns that would help]

## Workflow Metrics

- Plan iterations: X
- Research sources consulted: Y
- Issues found in review: Z
- Total files changed: N
```

Update relevant documentation files as identified.

## Guidelines

✅ **DO**:
- Focus on reusable knowledge
- Be concise but complete
- Link to specific code/commits
- Think about future readers

❌ **DON'T**:
- Document trivial details
- Duplicate existing docs
- Write novels
- Skip the archiving step

## Handoff

You are the final agent. After codification:
1. Report completion to orchestrator/user
2. The workflow is complete
3. Artifacts are preserved for future reference
```

### 6.4.7 Single-Agent Mode Prompt

**文件**: `prompts/single_agent.md`

```markdown
# Copal Workflow Agent (Single-Agent Mode)

You are a software development agent that follows a structured 6-phase workflow. You will switch between different "modes" as you progress through the phases.

## Workflow Phases

```
[PLAN] → [RESEARCH] → [CONFIRM] → [WORK] → [REVIEW] → [CODIFY]
                          ↑
                    USER GATE (mandatory)
```

## Phase Transitions

Track your current phase in `.copal/artifacts/workflow_state.json`:
```json
{
  "current_phase": "plan",
  "task": "...",
  "phase_history": []
}
```

## Phase Instructions

### 🎯 PLAN Phase
**Mode**: Analytical Planner

Your focus: Understanding and planning
- Analyze the task requirements
- Explore the codebase
- Create a draft plan

Output: `.copal/artifacts/plan.json` with `status: "draft"`

Transition: Automatically proceed to RESEARCH

---

### 🔍 RESEARCH Phase
**Mode**: Technical Researcher

Your focus: Validation and enrichment
- Use MCP tools to research best practices
- Validate technical decisions
- Find relevant documentation and examples

Output: `.copal/artifacts/research.json`
Update: `.copal/artifacts/plan.json` with `status: "researched"`

Transition: Automatically proceed to CONFIRM

---

### ✅ CONFIRM Phase
**Mode**: Facilitator

Your focus: User alignment
- Present the refined plan to user
- Highlight key findings from research
- Ask for explicit confirmation

**YOU MUST**:
```
Present:
1. Summary of the plan
2. Key research findings
3. Any risks or trade-offs

Ask: "Do you approve this plan? Please respond with:
- 'yes' or 'approve' to proceed
- 'no' or 'reject' to cancel
- specific feedback to modify the plan"
```

Transition: ONLY proceed to WORK after user says "yes/approve"

---

### 🔨 WORK Phase
**Mode**: Implementation Engineer

⚠️ **GATE CHECK**: Verify `plan.json` has `status: "confirmed"`
If not confirmed, STOP and return to CONFIRM phase.

Your focus: Quality implementation
- Follow the confirmed plan step by step
- Write clean, tested code
- Run verification scripts

Output: 
- `.copal/artifacts/test_plan.md`
- `.copal/artifacts/notes.md` (if needed)

Update: `.copal/artifacts/plan.json` with `status: "completed"`

Transition: Automatically proceed to REVIEW

---

### 🔎 REVIEW Phase
**Mode**: Quality Reviewer

Your focus: Objective assessment
- Review all changes made
- Check against the original plan
- Identify issues and improvements

Output:
- `.copal/artifacts/findings.json`
- `.copal/artifacts/todo.json`

Transition: 
- If critical issues: Return to WORK
- Otherwise: Proceed to CODIFY

---

### 📚 CODIFY Phase
**Mode**: Knowledge Curator

Your focus: Learning capture
- Extract reusable patterns
- Update documentation
- Archive the workflow

Output: `.copal/artifacts/codify_report.md`

Transition: Workflow complete ✅

---

## Critical Rules

1. **NEVER skip RESEARCH** - Even if you think you know the answer
2. **NEVER skip CONFIRM** - User must explicitly approve
3. **NEVER start WORK without confirmation** - Check plan status
4. **ALWAYS run verification** - Before declaring work complete
5. **ALWAYS document learnings** - Knowledge compounds

## State Recovery

If you lose context or restart:
1. Read `.copal/artifacts/workflow_state.json`
2. Read all existing artifacts
3. Resume from `current_phase`
```

---

## 7. 工件（Artifacts）与数据契约

### 7.1 工件目录

默认：`.copal/artifacts/`（由 manifest 控制）

### 7.2 必需工件（v0.1）

| 工件 | 格式 | 生成阶段 | 校验者 | 说明 |
|-----|------|---------|-------|------|
| `plan.json` | JSON | Plan → Research → Confirm | Copal | 逐步完善，Confirm 后锁定 |
| `research.json` | JSON | Research | Copal | 调研发现、参考资料、技术决策 |
| `todo.json` | JSON | Work / Review | Copal | 可执行待办 |
| `findings.json` | JSON | Review | Copal | 审查发现 |
| `test_plan.md` | Markdown | Work | - | 测试计划和验证结果 |
| `notes.md` | Markdown | Work / Review | - | 风险、迁移、后续 |

### 7.3 Schema（JSON Schema v2020-12）

必须提供：

- `plan.schema.json`
- `research.schema.json`
- `todo.schema.json`
- `findings.schema.json`

#### plan.json 状态流转

```json
{
  "status": "draft | researched | confirmed | completed",
  "version": 1,
  "task": "...",
  "steps": [...],
  "research_refs": ["research.json#/findings/0", ...],
  "confirmed_at": null | "2025-12-06T10:00:00Z",
  "confirmed_by": null | "user"
}
```

#### research.json 结构示例

```json
{
  "query": "原始任务/问题",
  "findings": [
    {
      "source": "https://openspec.dev",
      "type": "reference | best_practice | similar_impl",
      "summary": "...",
      "relevance": "high | medium | low",
      "implications": "对 plan 的影响"
    }
  ],
  "tools_used": ["mcp_fetch", "context7", "grep_search"],
  "recommendations": ["建议1", "建议2"],
  "plan_updates": {
    "added": [...],
    "modified": [...],
    "removed": [...]
  }
}
```

**校验时机（事后校验）：**

```bash
# Agent 生成工件后，开发者或 CI 运行：
$ copal validate --artifacts
✓ plan.json validates against plan.schema.json
✓ todo.json validates against todo.schema.json
✗ findings.json missing required field: severity
```

也可通过 git hook 自动校验：

```bash
# .git/hooks/pre-commit
copal validate --artifacts
```

---

## 8. CLI 需求（Copal v0.1）

### 8.1 命令总览

```bash
copal init [--tools <tools>]    # 初始化项目
copal update                    # 更新 agent 指令
copal validate                  # 校验配置
copal validate --artifacts      # 校验工件
copal export <tool>             # 导出命令到指定工具
copal pack list                 # 列出可用 packs
copal pack add <name>           # 添加新 pack（v0.2）
copal status                    # 查看当前状态
```

### 8.2 命令详细说明

#### `copal init`

交互式初始化项目：

```bash
$ copal init
? Select your AI tools: (Use space to select)
  ◉ Claude Code
  ○ Codex CLI
  ○ Cursor
  ○ Other (AGENTS.md only)

? Select packs to install:
  ◉ engineering_loop (plan/work/review/codify)
  ○ security_review
  ○ custom...

✓ Created AGENTS.md
✓ Created .copal/manifest.yaml
✓ Created .copal/packs/engineering_loop/
✓ Created .copal/docs/ (templates)
✓ Generated .claude/commands/copal/*.md

Next steps:
  1. Review and customize AGENTS.md for your project
  2. Fill in .copal/docs/ with your project documentation
  3. Run your AI agent and try: /copal:plan "your task"
```

#### `copal update`

当 Pack 更新后刷新 agent 指令：

```bash
$ copal update
✓ Updated .claude/commands/copal/plan.md
✓ Updated .claude/commands/copal/work.md
✓ Updated .claude/commands/copal/review.md
✓ Updated .claude/commands/copal/codify.md
```

#### `copal validate`

校验配置文件：

```bash
$ copal validate
✓ manifest.yaml is valid
✓ Pack 'engineering_loop' is valid
✓ All schemas are loadable
✓ All workflow files exist
```

校验工件：

```bash
$ copal validate --artifacts
✓ plan.json validates against plan.schema.json
✗ todo.json: missing required field 'priority'
```

#### `copal export <tool>`

导出命令到指定 agent 工具：

```bash
$ copal export claude
✓ Generated .claude/commands/copal/plan.md
✓ Generated .claude/commands/copal/work.md
✓ Generated .claude/commands/copal/review.md
✓ Generated .claude/commands/copal/codify.md

$ copal export cursor
✓ Generated .cursor/rules/copal-plan.md
✓ Generated .cursor/rules/copal-work.md
...
```

#### `copal status`

查看当前状态：

```bash
$ copal status
Project: my-project
Default Pack: engineering_loop
Adapters: claude

Artifacts:
  ✓ plan.json (valid)
  ✓ todo.json (valid)
  ○ findings.json (not found)
  ○ test_plan.md (not found)

Last verify: 2025-12-06 10:30:00 (passed)
```

### 8.3 退出码规范

| 退出码 | 含义 |
|-------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 2 | 配置校验失败（manifest/pack/schema 无效）|
| 3 | 工件校验失败（JSON 不符合 schema）|

### 8.4 TUI 交互设计（基于 Rich）

使用 [Rich](https://github.com/Textualize/rich) 库实现美观的终端交互界面。

#### 8.4.1 依赖

```toml
# pyproject.toml
dependencies = [
    "rich>=13.0",
]
```

#### 8.4.2 交互组件

**1. 初始化向导 (`copal init`)**

```python
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# 欢迎面板
console.print(Panel.fit(
    "[bold blue]Copal[/bold blue] - Agent Harness Configuration",
    subtitle="v0.1.0"
))

# 多选菜单（使用 questionary 或 InquirerPy 配合 Rich）
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

tools = inquirer.checkbox(
    message="Select your AI tools:",
    choices=[
        Choice("claude", "Claude Code"),
        Choice("codex", "Codex CLI"),
        Choice("cursor", "Cursor"),
        Choice("generic", "Other (AGENTS.md only)"),
    ],
    default=["claude"],
).execute()

# 进度条
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console,
) as progress:
    task = progress.add_task("Creating project structure...", total=5)
    # ... create files
    progress.update(task, advance=1, description="Created AGENTS.md")
```

**2. 状态展示 (`copal status`)**

```python
from rich.table import Table
from rich.tree import Tree

# 状态表格
table = Table(title="Copal Status", show_header=True)
table.add_column("Component", style="cyan")
table.add_column("Status", justify="center")
table.add_column("Details")

table.add_row("manifest.yaml", "[green]✓[/green]", "valid")
table.add_row("plan.json", "[green]✓[/green]", "status: confirmed")
table.add_row("research.json", "[green]✓[/green]", "3 findings")
table.add_row("findings.json", "[dim]○[/dim]", "not found")

console.print(table)

# Workflow 状态树
tree = Tree("[bold]Workflow: engineering_loop[/bold]")
tree.add("[green]✓[/green] Plan - completed")
tree.add("[green]✓[/green] Research - completed")
tree.add("[green]✓[/green] Confirm - approved")
tree.add("[yellow]→[/yellow] Work - [bold]in progress[/bold]")
tree.add("[dim]○[/dim] Review - pending")
tree.add("[dim]○[/dim] Codify - pending")

console.print(tree)
```

**3. 校验输出 (`copal validate`)**

```python
from rich.console import Console
from rich.syntax import Syntax

console = Console()

# 成功
console.print("[green]✓[/green] manifest.yaml is valid")

# 失败（带详细错误）
console.print("[red]✗[/red] plan.json: validation failed")
console.print(Panel(
    Syntax(
        '''{
  "error": "Missing required field",
  "path": "$.steps[0].rationale",
  "schema": "plan.schema.json"
}''',
        "json",
        theme="monokai",
    ),
    title="Validation Error",
    border_style="red",
))
```

**4. 日志与调试输出**

```python
from rich.logging import RichHandler
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("copal")
log.info("Initializing project...")
log.warning("No .copal/docs/ found, using defaults")
log.error("Failed to parse manifest.yaml")
```

#### 8.4.3 交互式确认（Confirm 阶段）

当 Agent 需要用户确认计划时，Copal 可以提供辅助的 TUI 确认界面：

```bash
$ copal confirm
```

```python
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Confirm

console = Console()

# 显示计划摘要
plan = load_plan_json()
console.print(Panel(
    Markdown(f'''
## Task: {plan["task"]["original"]}

### Goal
{plan["goal"]}

### Steps
{format_steps(plan["steps"])}

### Risks
{format_risks(plan["risks"])}
'''),
    title="[bold]Plan Summary[/bold]",
    subtitle=f"Version {plan['version']} | Status: {plan['status']}",
))

# 显示研究发现
research = load_research_json()
console.print(Panel(
    format_findings(research["findings"]),
    title="[bold]Research Findings[/bold]",
))

# 确认
if Confirm.ask("Do you approve this plan?"):
    update_plan_status("confirmed")
    console.print("[green]✓[/green] Plan confirmed. Run `/copal:work` to proceed.")
else:
    feedback = Prompt.ask("What changes are needed?")
    # 记录反馈到 plan.json
    console.print("[yellow]→[/yellow] Feedback recorded. Plan needs revision.")
```

#### 8.4.4 样式规范

| 元素 | 样式 | 示例 |
|-----|------|------|
| 成功 | `[green]✓[/green]` | ✓ Created AGENTS.md |
| 失败 | `[red]✗[/red]` | ✗ Validation failed |
| 进行中 | `[yellow]→[/yellow]` | → Work in progress |
| 待处理 | `[dim]○[/dim]` | ○ Review pending |
| 标题 | `[bold blue]` | **Copal** |
| 警告 | `[yellow]` | ⚠ No tests found |
| 路径 | `[cyan]` | .copal/artifacts/plan.json |

#### 8.4.5 依赖选型

```toml
# pyproject.toml
dependencies = [
    "rich>=13.0",           # TUI 基础
    "InquirerPy>=0.3.4",    # 交互式选择菜单
]

[project.optional-dependencies]
minimal = []  # 不含 TUI，仅命令行输出
```

---

## 9. Context 组装策略（供 Agent 读取的静态指引）

> Copal 不在运行时组装上下文，而是生成静态的 workflow 文档，指导 agent 如何按需加载上下文。

### 9.1 上下文层级（写入 workflow 文档）

workflow 文档中应指导 agent 按以下层级加载上下文：

- **Layer 0**：`AGENTS.md`（最小常驻，必读）
- **Layer 1**：当前 workflow 文档（plan.md/work.md 等）
- **Layer 2**：按需 docs/references（repo_map/build/test/architecture…）
- **Layer 3**：本次 work 的文件指针（file:line / 文件列表/目录树摘要）
- **Layer 4**：已有工件（plan.json/todo.json/findings.json）

### 9.2 规则（写入 AGENTS.md 和 workflow 文档）

- 不允许在 Layer 0 写任务特定细则
- workflow 只引用 docs 路径，不复制粘贴大段内容
- 强制输出指针而不是复制（避免过期与上下文膨胀）

---

## 10. Verify Gate（确定性质量闸）

### 10.1 目标

- 把"完成定义"绑定到可执行校验
- 不让 agent 充当 linter

### 10.2 Copal 职责

- **定义** verify 脚本路径（在 manifest.yaml 中）
- **不执行** verify（由 agent 或开发者调用）

### 10.3 脚本位置

- `.copal/packs/<pack>/scripts/verify.sh`（POSIX）
- `.copal/packs/<pack>/scripts/verify.ps1`（Windows）

### 10.4 Workflow 文档指引

在 `work.md` 和 `review.md` 中，应指导 agent：

```markdown
## Verify Gate

After completing implementation, you MUST run the verify script:

\`\`\`bash
.copal/packs/engineering_loop/scripts/verify.sh
\`\`\`

Record the output in `.copal/artifacts/test_plan.md`.
```

---

## 11. Agent 适配层

### 11.1 支持的工具

| 工具 | 导出路径 | 命令格式 |
|-----|---------|---------|
| Claude Code | `.claude/commands/copal/*.md` | `/copal:plan`, `/copal:research`, `/copal:confirm`, `/copal:work`, `/copal:review`, `/copal:codify` |
| Cursor | `.cursor/rules/copal/*.md` | 自然语言引用 |
| Codex | `~/.codex/prompts/copal/*.md` | `/copal-plan`, `/copal-research`, etc. |
| 通用 | `AGENTS.md` 内嵌 | 自然语言引用 |

### 11.2 导出的命令文件内容

以 Claude Code 为例：

#### `.claude/commands/copal/plan.md`

```markdown
# Plan Workflow (Step 1/6)

Before starting, you MUST read:
- `AGENTS.md` (mandatory)
- `.copal/packs/engineering_loop/workflows/plan.md` (this workflow)

## Task

$ARGUMENTS

## Output Requirements

Generate `.copal/artifacts/plan.json` with status="draft".

## Next Step

After generating plan, you MUST proceed to `/copal:research` to validate and refine the plan.
DO NOT skip to work phase.
```

#### `.claude/commands/copal/research.md`

```markdown
# Research Workflow (Step 2/6)

⚠️ This step is MANDATORY. Do not skip.

## Prerequisites

- `.copal/artifacts/plan.json` must exist with status="draft"

## Task

Use available tools to research and validate the plan:
1. Search for best practices, documentation, similar implementations
2. Verify technical feasibility
3. Identify potential issues or alternatives

## Tools to Use

- `fetch_webpage` / MCP tools for external documentation
- `grep_search` / `semantic_search` for codebase exploration
- `context7` for library documentation

## Output Requirements

1. Generate `.copal/artifacts/research.json` with findings
2. Update `.copal/artifacts/plan.json` based on research (status="researched")

## Next Step

Proceed to `/copal:confirm` to get user approval.
```

#### `.claude/commands/copal/confirm.md`

```markdown
# Confirm Workflow (Step 3/6)

⚠️ This step is MANDATORY. Do not skip.

## Prerequisites

- `.copal/artifacts/plan.json` must have status="researched"
- `.copal/artifacts/research.json` must exist

## Task

Present to user:
1. Summary of the refined plan
2. Key findings from research
3. Any risks or trade-offs identified
4. Request explicit confirmation to proceed

## User Interaction

Ask: "The plan has been refined based on research. Please review and confirm:
[summary of plan]
[key research findings]
Do you approve this plan? (yes/no/modify)"

## Output Requirements

On user confirmation:
- Update `.copal/artifacts/plan.json` with status="confirmed", confirmed_at, confirmed_by

## Next Step

Only after explicit user confirmation, proceed to `/copal:work`.
```

#### `.claude/commands/copal/work.md`

```markdown
# Work Workflow (Step 4/6)

## Prerequisites

- `.copal/artifacts/plan.json` MUST have status="confirmed"
- If status is not "confirmed", STOP and run `/copal:confirm` first

## Task

Execute the confirmed plan step by step.

## Process

1. Read the confirmed plan from `.copal/artifacts/plan.json`
2. Implement changes according to plan
3. Run verify script after implementation
4. Record results in `.copal/artifacts/test_plan.md`

## Verify Gate

After implementation, you MUST run:
\`\`\`bash
.copal/packs/engineering_loop/scripts/verify.sh
\`\`\`

## Output Requirements

- Update `.copal/artifacts/plan.json` with status="completed"
- Generate `.copal/artifacts/test_plan.md`
- Generate `.copal/artifacts/notes.md` (if any risks/follow-ups)

## Next Step

Proceed to `/copal:review` for review and retrospective.
```

#### `.claude/commands/copal/review.md`

```markdown
# Review Workflow (Step 5/6)

## Prerequisites

- `.copal/artifacts/plan.json` must have status="completed"
- `.copal/artifacts/test_plan.md` must exist

## Task

Review the completed work against the original plan.

## Review Dimensions

1. **Correctness**: Does the code do what it's supposed to?
2. **Quality**: Is the code readable and maintainable?
3. **Security**: Any vulnerabilities or unsafe patterns?
4. **Performance**: Any obvious inefficiencies?
5. **Testing**: Is test coverage adequate?
6. **Plan Alignment**: Does implementation match the plan?

## Output Requirements

Generate:
- `.copal/artifacts/findings.json` with detailed review findings
- `.copal/artifacts/todo.json` with any follow-up items

## Next Step

- If critical issues found: Return to `/copal:work` for fixes
- Otherwise: Proceed to `/copal:codify`
```

#### `.claude/commands/copal/codify.md`

```markdown
# Codify Workflow (Step 6/6)

## Prerequisites

- `.copal/artifacts/findings.json` must exist
- Review should be approved (no critical issues)

## Task

Extract and document learnings from this workflow.

## Process

1. Review all artifacts from this workflow
2. Identify reusable patterns and pitfalls to avoid
3. Update relevant documentation
4. Archive workflow summary

## Documentation Targets

Consider updating:
- `.copal/docs/conventions.md` - New coding patterns
- `.copal/docs/architecture.md` - Structural changes
- `AGENTS.md` - New instructions or warnings
- README.md - User-facing changes

## Output Requirements

Generate `.copal/artifacts/codify_report.md` with:
- Task summary
- Learnings captured (patterns, pitfalls, decisions)
- Documentation updates made
- Recommendations for future

## Completion

This is the final step. Report completion to user.
```

### 11.3 约束

- 命令文件只做路由，不重复写规则
- 通过 `$ARGUMENTS` 传参（Claude Code 支持）
- 每个命令文件应引用对应的 prompt 文件（如 `.copal/packs/engineering_loop/prompts/worker.md`）

---

## 12. Copal 代码侧模块划分（Python 实现）

### 12.1 模块结构

```
copal_cli/
  harness/
    __init__.py
    init.py           # copal init 实现
    update.py         # copal update 实现
    validate.py       # copal validate 实现
    status.py         # copal status 实现
  config/
    __init__.py
    manifest.py       # manifest.yaml 读取与校验
    pack.py           # pack.yaml 读取与校验
  schema/
    __init__.py
    validator.py      # JSON Schema 校验
  adapters/
    __init__.py
    base.py           # Adapter 基类
    claude.py         # Claude Code 适配
    cursor.py         # Cursor 适配
    codex.py          # Codex 适配
  fs/
    __init__.py
    paths.py          # 路径解析、安全检查
    writer.py         # 原子写入
```

### 12.2 安全要求

- Copal 只允许写入 `.copal/`、`.claude/`、`.cursor/` 等已知目录
- 路径必须做规范化并阻止 `..` 越界

---

## 13. 里程碑与交付（建议 3 个迭代）

### Milestone 0（1–2 天）：规范落地

- 提交：`AGENTS.md` 模板 + `.copal/manifest.yaml` + engineering_loop pack 骨架 + docs 目录
- 手动可用：人按 workflow 文档完成一次 plan/work/review/codify（不依赖 CLI）

### Milestone 1（2–4 天）：Copal CLI 核心

- `copal init`：生成完整目录结构
- `copal validate`：校验配置
- `copal export claude`：导出 Claude Code 命令
- `copal status`：查看状态

### Milestone 2（2–3 天）：工件校验

- `copal validate --artifacts`：校验 agent 生成的工件
- `copal update`：更新 agent 指令
- 完善 schema 定义

### Milestone 3（可选，v0.2）：扩展

- 更多 adapter（Cursor、Codex）
- 远程 Pack 获取
- Pack 版本管理

---

## 14. 验收标准（Definition of Done）

1. **初始化验收**：新仓库运行 `copal init` 后：
   - `copal validate` 通过
   - `copal export claude` 生成 `.claude/commands/copal/*.md`
   - Claude Code 中可使用 `/copal:plan "任务描述"` 命令

2. **工件校验验收**：Agent 生成工件后：
   - `copal validate --artifacts` 能正确校验 JSON 工件
   - Schema 不符合时返回退出码 3 并输出错误详情

3. **AGENTS.md 验收**：
   - 不超过 120 行
   - 不包含长命令清单/风格条例
   - 细则在 `.copal/docs/*` 和 pack references 中

---

## 15. 附：建议的 `AGENTS.md` 最小模板

```markdown
# AGENTS.md

## Why

<一句话解释此仓库的目的>

## What (Repo Map)

See: `.copal/docs/repo_map.md`

## How

### Execution Mode

This project uses **[Multi-Agent | Single-Agent]** mode.
- Multi-Agent: Each phase uses a specialized subagent
- Single-Agent: One agent switches roles between phases

Agent prompts: `.copal/packs/engineering_loop/prompts/`

### Workflow（6 步闭环）

使用 Copal workflows（通过 slash commands 或自然语言）：

```
[PLAN] → [RESEARCH] → [CONFIRM] → [WORK] → [REVIEW] → [CODIFY]
                          ↑
                    USER GATE (mandatory)
```

| Phase | Command | Agent Role | Description |
|-------|---------|------------|-------------|
| 1. Plan | `/copal:plan "<task>"` | Planner | 分析需求，制定初步计划 |
| 2. Research | `/copal:research` | Researcher | 调研验证，完善计划（**不可跳过**）|
| 3. Confirm | `/copal:confirm` | Confirmer | 向用户确认计划（**不可跳过**）|
| 4. Work | `/copal:work` | Worker | 按确认的计划实现 |
| 5. Review | `/copal:review` | Reviewer | 审查复盘 |
| 6. Codify | `/copal:codify` | Codifier | 沉淀知识 |

⚠️ **CRITICAL RULES**:
1. **NEVER skip Research** - 即使你觉得已经知道答案
2. **NEVER skip Confirm** - 用户必须显式确认
3. **NEVER start Work without confirmation** - 检查 plan.json 状态
4. **ALWAYS run verification** - 在宣布完成前
5. **ALWAYS document learnings** - 知识会复利

### Team Coordination (Multi-Agent)

```
┌─────────────────────────────────────────────────────────────────┐
│                     Orchestrator Agent                          │
│  Prompt: .copal/packs/engineering_loop/prompts/orchestrator.md  │
└──────────┬──────────┬──────────┬──────────┬──────────┬──────────┘
           │          │          │          │          │
           ▼          ▼          ▼          ▼          ▼
      ┌────────┐ ┌─────────┐ ┌────────┐ ┌────────┐ ┌────────┐
      │Planner │ │Researcher│ │Worker │ │Reviewer│ │Codifier│
      └────────┘ └─────────┘ └────────┘ └────────┘ └────────┘
```

### Research Tools

在 Research 阶段，使用以下工具收集信息：
- **External**: MCP tools (fetch_webpage, context7)
- **Codebase**: grep_search, semantic_search, list_code_usages
- **Docs**: read_file for documentation

### Verify Gate

在 Work 完成前，必须运行：
```bash
.copal/packs/engineering_loop/scripts/verify.sh
```

### Progressive Disclosure

Load these docs as needed:
- Build: `.copal/docs/build.md`
- Test: `.copal/docs/test.md`
- Conventions: `.copal/docs/conventions.md`
- Architecture: `.copal/docs/architecture.md`

## Output Contract

### Artifacts

All artifacts are written to `.copal/artifacts/`:

| Artifact | Generated By | Schema |
|----------|--------------|--------|
| `plan.json` | Planner → Researcher → Confirmer | `.copal/schemas/plan.schema.json` |
| `research.json` | Researcher | `.copal/schemas/research.schema.json` |
| `workflow_state.json` | All phases | Internal |
| `test_plan.md` | Worker | - |
| `notes.md` | Worker | - |
| `findings.json` | Reviewer | `.copal/schemas/findings.schema.json` |
| `todo.json` | Reviewer | `.copal/schemas/todo.schema.json` |
| `codify_report.md` | Codifier | - |

### plan.json Status Flow

```
draft → researched → confirmed → completed
         │              │            │
         │              │            └─ Worker completed
         │              └─ User approved
         └─ Research validated
```

### Final Deliverables

Every workflow completion must include:
- **DIFF**: Summary of changes made
- **TEST_PLAN**: Verification steps and results
- **NOTES**: Risks, follow-ups, and learnings
- **CODIFY_REPORT**: Captured learnings for future
```

---

## 16. 与 OpenSpec 的对比

| 方面 | OpenSpec | Copal |
|-----|---------|-------|
| 核心功能 | Spec-driven development | Workflow + Research + Verify harness |
| 工作流 | Draft → Review → Apply → Archive | Plan → **Research** → **Confirm** → Work → Review → Codify |
| 主要输出 | specs/ + changes/ | workflows/ + artifacts/ |
| 工件类型 | proposal.md, tasks.md, spec.md | plan.json, **research.json**, todo.json, findings.json |
| 校验重点 | Spec 格式校验 | 工件 Schema 校验 |
| 研究阶段 | 隐式（在 Review 中） | **显式独立阶段** |
| 确认机制 | 隐式 | **显式 Confirm 阶段** |
| 适配工具 | Claude Code, Cursor, Codex... | Claude Code, Cursor, Codex... |

两者可以互补：OpenSpec 关注"规格定义"，Copal 关注"研究驱动的执行闭环"。

---

## 17. 下一步（对开发者的指令）

1. 先按本规范把 `.copal/` 目录与 engineering_loop pack 骨架提交到 copal 仓库
2. 实现 `copal init`（优先级最高）
3. 实现 `copal validate`（配置校验）
4. 实现 `copal export claude`
5. 实现 `copal validate --artifacts`（工件校验）
6. 编写 JSON Schema 定义文件

---

> 备注：本文件是"开发规格"。Copal 作为 init-time 配置生成器，不执行 agent 逻辑。v0.2 可进一步引入：更多 adapter、远程 Pack 获取、以及与 OpenSpec 等工具的集成。
