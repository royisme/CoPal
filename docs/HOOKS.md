# MCP Hooks Overview

CoPal's MCP hook system injects tool-specific guidance into stage prompts based on the tools declared in `.copal/mcp-available.json`. This ensures the assistant receives the right usage tips at the right stage.

## Core Concepts

### MCP Configuration

Define the available tools in `.copal/mcp-available.json`:

```json
["context7", "active-file", "file-tree"]
```

### Hook Routing Rules

Describe which hook blocks should load in `.copal/hooks/hooks.yaml`:

```yaml
- id: context7-analysis
  stage: analysis
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.analysis.md

- id: context7-plan
  stage: plan
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.plan.md

- id: active-file-implement
  stage: implement
  all_mcp: ["active-file", "file-tree"]
  inject:
    - mcp/active-file/usage.implement.md
```

Each block referenced in `inject` lives under `.copal/hooks/mcp/` and contains stage-specific usage instructions.

## Rule Syntax

### Basic structure

```yaml
- id: unique-rule-id
  stage: stage-name            # analysis/spec/plan/implement/review
  any_mcp: [list]              # OR logic; trigger if any MCP is present
  all_mcp: [list]              # AND logic; trigger only if all MCPs are present
  inject:
    - path/to/block.md
```

### Conditional logic

- **any_mcp** – Fires when at least one tool in the list is available.
- **all_mcp** – Fires only when every tool in the list is available.

## Built-in Examples

### Context7 – Analysis stage
- **Path**: `.copal/hooks/mcp/context7/usage.analysis.md`
- **When**: `context7` is present during `analysis`
- **Content**: How to research libraries, gather background knowledge, and capture findings in the analysis artifact.

### Context7 – Plan stage
- **Path**: `.copal/hooks/mcp/context7/usage.plan.md`
- **When**: `context7` is present during `plan`
- **Content**: Confirm APIs, design solutions, and document dependencies and versions.

### Active-file + File-tree – Implement stage
- **Path**: `.copal/hooks/mcp/active-file/usage.implement.md`
- **When**: Both `active-file` and `file-tree` are present during `implement`
- **Content**: Locate files, apply changes, write tests, and capture patch notes.

### Serena – End-to-end example
- **Tool docs**: Write the primary guidance under `.copal/global/knowledge-base/toolsets/project/mcp-serena.en.md` (tool-agnostic overview lives beside it in `mcp-overview.en.md`).
- **Hook blocks**: Add concise stage tips under `.copal/hooks/mcp/serena/usage.<stage>.md` for the stages you want to support (e.g., `analysis`, `plan`, `implement`, `review`).
- **Routing rule**: Register each stage in `.copal/hooks/hooks.yaml` using `any_mcp: ["serena"]` and an `inject` path that matches the block. This ensures prompts pull the right hints whenever the project declares Serena in `.copal/mcp-available.json`.

## Workflow

1. **Command execution** – The user runs a stage command, e.g. `copal analyze`.
2. **Read configuration** – CoPal reads `.copal/mcp-available.json` and `.copal/hooks/hooks.yaml`.
3. **Match rules** – Rules that match the current stage and MCP availability are selected.
4. **Render prompt** – The runtime header, role template, and matching hook blocks are concatenated into `.copal/runtime/<stage>.prompt.md`.
5. **Agent execution** – The assistant reads the prompt and writes results to `.copal/artifacts/`.

## Custom Hooks

### Add a new MCP hook

1. **Declare the MCP** – Add it to `.copal/mcp-available.json`.
2. **Create a hook block** – Add a markdown file under `.copal/hooks/mcp/<tool>/usage.<stage>.md`.
3. **Add a routing rule** – Reference the block from `.copal/hooks/hooks.yaml`.
4. **Test** – Run the relevant stage command and verify the prompt includes the new guidance.

### Cross-stage hooks

Create separate blocks for each stage if a tool needs guidance at multiple points.

### Combined hooks

Use `all_mcp` when multiple tools must be available before injecting the guidance.

## Best Practices

1. Keep hook blocks concise and focused on a single tool and stage.
2. Clearly state when and how to use the tool.
3. Provide command examples or code snippets where useful.
4. Reference versions if the tool behaviour changes across releases.
5. Avoid duplicating content across multiple hook blocks.
6. Test new hooks by running the relevant stage command.

## Troubleshooting

### No content injected

Checklist:
- [ ] Is the MCP listed in `.copal/mcp-available.json`?
- [ ] Does the rule's `stage` match the command you're running?
- [ ] Do the `any_mcp` / `all_mcp` conditions match the available tools?
- [ ] Does the referenced markdown file exist?
- [ ] Is the YAML syntax correct?

### Debugging tips

- Run stage commands with `--verbose` to see hook selection logs.
- Inspect the generated `.copal/runtime/<stage>.prompt.md` file to confirm which blocks were included.

## References

- [Model Context Protocol](https://modelcontextprotocol.org)
- [CoPal AGENTS.md](../copal_cli/templates/base/AGENTS.md)
- [CoPal USAGE.md](USAGE.md)

## Future Enhancements (v0.2+)

- Negotiated MCP requests at runtime
- Richer conditional expressions (NOT, XOR, etc.)
- Priority handling when multiple rules inject content
- Parameterised hook blocks (e.g., pass paths or configuration values)
