## MCP Integration in CoPal

### Purpose and Placement
Model Context Protocol (MCP) tools expand what you can read and edit while following the CoPal workflow. Available tools are declared in `.copal/mcp-available.json`; CoPal then uses `.copal/hooks/hooks.yaml` to inject stage-specific guidance (the `usage.<stage>.md` snippets) whenever `any_mcp` or `all_mcp` conditions match. This document is tool-agnostic. Specific MCP tools (e.g. Serena) have their own pages.

### Sources of Guidance
- **Global toolsets**: Read MCP documents under `global/knowledge-base/toolsets/project/` for conceptual rules, safe patterns, and project-wide defaults.
- **Hook snippets**: For each MCP tool ID, check `.copal/hooks/mcp/<tool-id>/usage.<stage>.md` to see the short instructions automatically injected at relevant stages.
- **Project overrides**: Project-level knowledge base entries can override or augment the global guidance. Always reconcile both.

### Loading Order for Agents
The runtime prompt loads instructions in this order (highest priority later):
1. `AGENTS.md`
2. `.copal/global/knowledge-base/`
3. `UserAgents.md`
Respect this precedence when resolving conflicts or seeking clarifications.

### How MCP Hooks Work
- **Declaration**: The project lists available MCP tools in `.copal/mcp-available.json`.
- **Hook rules**: `.copal/hooks/hooks.yaml` contains rules with `id`, `stage`, and `any_mcp`/`all_mcp` selectors to determine whether to inject guidance.
- **Injection payload**: Each rule references `inject` entries—Markdown files such as `usage.analysis.md`, `usage.plan.md`, or `usage.implement.md`—that become part of the prompt for the matching stage when the tool conditions are satisfied.
- **Scoping**: Hooks are evaluated per stage of the CoPal workflow (Analyze, Spec, Plan, Implement, Review, Commit). Injection only happens when the declared MCP availability matches the rule’s conditions.

### Behavior Expectations for AI Agents
- **Lookup before action**: Before using any MCP tool, search for its documentation in `global/knowledge-base/toolsets/project/` and the corresponding `.copal/hooks/mcp/<tool-id>/usage.<stage>.md` files for the current stage.
- **Honor precedence**: Treat global guidance as the default and layer any project-specific overrides above it. If an override conflicts, follow the project rule and note the divergence.
- **Stay conservative**: When documentation is missing or ambiguous, avoid broad, risky operations. Prefer read-only discovery, small scoped edits, and explicit user confirmation for destructive actions.
- **Narrate usage**: When you rely on MCP output, explain which tool and queries you conceptually used so the user can trace decisions.
- **Validate effects**: After applying MCP-guided changes, recommend running the project’s relevant tests or linters; do not assume success without evidence.

### Workflow-Aware Use
- **Analyze / Spec / Plan**: Use MCP discovery to map architecture, dependencies, and constraints. Collect symbols, entrypoints, and data flows without editing.
- **Implement**: Apply MCP edits narrowly—target specific symbols or regions identified in the plan. Avoid wholesale rewrites or speculative refactors.
- **Review / Commit**: Use MCP insights to verify impacted call sites, check for regressions, and confirm that the changes align with the planned scope. Summarize findings and testing needs.

### Safety Reminders
- Prefer precise, reversible actions backed by documented guidance.
- Do not introduce new MCP tools or assume their presence; rely only on those declared in `.copal/mcp-available.json` and confirmed by the user.
- If tool availability or documentation is unclear, pause and seek clarification instead of proceeding with risky changes.
