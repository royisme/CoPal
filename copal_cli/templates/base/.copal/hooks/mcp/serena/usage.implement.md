For detailed usage and safety rules, see global knowledge base: toolsets/project/mcp-serena.en.md and mcp-overview.en.md.
Edit at the symbol level: replace function bodies or add helpers instead of rewriting whole files.
Use Serena to re-open the targeted symbols and nearby call sites before applying edits.
Keep each change small and reviewable; avoid speculative refactors not in the plan.
After edits, ask the user to run focused tests/linters (e.g., go test ./..., pytest, npm test) and share results.
If an edit fails to apply, refresh the symbol view and retry with a narrower patch.
