# Active-File & File-Tree Usage Guide – Implement Stage

## Tool Overview

- **active-file**: Tracks and opens the currently edited file.
- **file-tree**: Provides a navigable view of the project structure.

## Recommendations for the Implement Stage

1. **Locate target files**
   - Use file-tree to browse the project and find files to modify.
   - Use active-file to open the file currently under review.
   - Identify related tests, configs, or documentation nearby.

2. **Apply changes methodically**
   - Follow the plan in `.copal/artifacts/plan.md` and edit files incrementally.
   - Record what changed and why for each file.
   - Ensure code style and conventions remain consistent.

3. **Write and update tests**
   - Locate relevant test files via file-tree.
   - Add or update tests to cover new behaviour.
   - Capture test results in `.copal/artifacts/patch_notes.md`.

4. **Document modifications**
   - List modified files, summaries, new tests, and documentation updates in the patch notes.
   - Highlight any follow-up work or potential risks.

## Best Practices

- Commit in small, reviewable units.
- Write or update tests before finalising code.
- Keep diffs clean by removing unused imports and comments.
- Align with project-specific guidelines from `UserAgents.md`.
