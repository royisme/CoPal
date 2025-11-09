---
id: toolset-project-mcp-discovery
origin: copal
type: mcp-discovery
owner: integration-team
updated: 2025-11-03
---

# MCP Tool Discovery Guide

## When to Use

- Before starting a task, confirm which MCP tools, resources, and templates are available.
- After adding or removing MCP servers, update the knowledge base or project documentation accordingly.

## Quick Commands

```bash
mcp tools list
mcp resources list
mcp connections status
```

## Operating Procedure

1. Run `mcp tools list` at the start of each stage and record differences from the default configuration.
2. Document missing guidance in `UserAgents.md` (or other project docs) and describe how to access the tools.
3. Log discrepancies or follow-up actions in `retrospectives/` and notify maintainers.

## Tips

- MCP discovery is inexpensive—run it frequently to detect environment drift.
- If the command fails, note that MCP is disabled in the current environment and document the reason for future reference.
