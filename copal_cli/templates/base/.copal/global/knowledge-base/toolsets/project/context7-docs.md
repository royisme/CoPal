---
id: toolset-project-context7-docs
origin: copal
type: cli-guide
owner: integration-team
updated: 2025-11-03
---

# Context7 Documentation Retrieval Guide

## When to Use

- Quickly pull official documentation for third-party libraries, frameworks, or tools.
- Retrieve API references for a specific version to aid implementation and verification.

## Steps

1. (Optional) Run `mcp tools list` to ensure `context7` is installed.
2. Resolve the library ID:
   ```bash
   context7 resolve-library-id "<library-name>"
   ```
3. Fetch documentation for a specific topic:
   ```bash
   context7 get-library-docs --id <id> --topic <topic> --tokens <limit>
   ```

## Output Requirements

- Cite the source and version of the documentation in specifications or design documents.
- If retrieval fails or the library is missing, record the issue in `retrospectives/` and raise it with maintainers.

## Troubleshooting

- **Network failure** – Check local proxy or credentials and retry.
- **Version mismatch** – Provide full version identifiers (e.g., `/vercel/next.js/v14.3.0`).
