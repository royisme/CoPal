## Serena MCP Tool – Practical Guide for AI Coding Agents

### Overview
Serena connects you to language servers to provide semantic code navigation and structured edits. Use it as a code map (entrypoints, modules, symbols, call sites), a semantic editor (replace or insert at symbol boundaries), and a project assistant (trace how features are implemented). It excels when you need LSP-backed understanding across Go, Python, TypeScript, and other languages. Favor Serena when you want to locate definitions, understand data flow, or edit functions without rewriting whole files.

### Prerequisites
- **Language server availability**: Ensure the appropriate LSP is installed and on `PATH` (e.g., `gopls`, `pyright`, `typescript-language-server`). If Serena reports initialization errors, ask the user to install the language server and restart Serena.
- **Project activation**: Serena operates on one active project root. If results are empty or the project is unrecognized, ask the user to activate/onboard the current repository and confirm the root path.
- **CoPal workflow context**: Run Serena after you have performed `copal analyze/spec/plan` so you align with the agreed scope. Stage-specific hints may be injected from `.copal/hooks/mcp/serena/usage.<stage>.md`—read them before acting.

### Core Usage Patterns
- **Project structure & execution flow**: Use Serena to enumerate modules, entrypoints, and bootstraps. Summarize layers (entry → routing/handlers → services → persistence/utilities) with concrete files and symbols.
- **Symbol & call-site discovery**: Locate definitions and references for functions, classes, or methods. Report paths, approximate locations, and context (e.g., within an HTTP handler or job).
- **Code comprehension & technical analysis**: Traverse call chains, list key functions in a module, and explain responsibilities, data flow, and failure points without loading huge files unnecessarily.
- **Safe incremental editing**: Plan the smallest change first. Edit at the symbol level, prefer inserting helpers over rewriting large sections, and keep each patch reviewable. After edits, instruct the user to run relevant tests or linters.

### Typical CoPal Workflow Integration
- **Analyze/Spec/Plan**: Use Serena to gather architecture maps, entrypoints, and affected symbols to inform the plan. Confirm constraints and reuse existing abstractions.
- **Implement**: Perform small, scoped edits at function or method granularity. Update related call sites only when necessary and clearly justified. Avoid speculative refactors.
- **Review**: Re-scan modified symbols and call sites to check for regressions, type mismatches, and unhandled errors. Provide a review summary and recommend tests to run.

### Troubleshooting
- **“Language server manager is not initialized”**: Likely missing LSP binary, wrong `PATH`, or inactive project. Ask which language the project uses, have the user install the correct language server, ensure it is on `PATH`, then restart and re-activate Serena.
- **“Project not recognized” or empty results**: Confirm the project root and request re-onboarding. Clarify which sub-module to target in monorepos.
- **Edit/apply failures**: The file may have changed or the symbol no longer matches. Re-query current symbols, narrow the edit, and re-apply with refreshed context.

### Safety & Limitations
- You should avoid rewriting large files or entire repositories. Favor narrow, reversible edits grounded in Serena’s symbol-level operations.
- Respect existing architecture and layering; do not introduce major structural changes without explicit direction.
- When changing public signatures, use Serena to find and update all call sites or clearly flag remaining work.
- Never assume tests pass. After meaningful changes, ask the user to run appropriate test or lint commands and handle failures before proceeding.
- Be transparent: describe which Serena queries you conceptually used and why. Defer to project-specific MCP rules or overrides whenever they exist.