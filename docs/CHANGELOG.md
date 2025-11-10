# Changelog

## 2025-11-01 · Local Memory Layer

### Added
- Introduced a pluggable memory subsystem with a NetworkX + SQLite backend and CLI commands for CRUD operations.
- Added automatic memory capture for each workflow stage (analysis through commit) when auto-capture is enabled.
- Documented memory configuration in `docs/USAGE.md`.

### Impact for Downstream Projects
- New dependency on `networkx`; update project environments accordingly.
- Re-run `copal init` if you want the memory hooks and configuration defaults in existing repositories.

## 2025-10-31 · Skillization Lifecycle Preview

### Added
- Documented `copal skill registry/search/scaffold/exec` commands in the README and usage guide.
- Introduced sandbox guarantee levels (`replay`, `reuse`, `fresh`) and `prelude.md` hand-off requirements.
- Added knowledge-base workflow and CLI guides to teach the new skill lifecycle.

### Impact for Downstream Projects
- Update `UserAgents.md` to reference preferred skill registries and required sandbox modes.
- Ensure planners attach generated `prelude.md` files when handing off tasks.
- Encourage implementers to capture `copal skill exec` logs inside `usage/` for review automation.
