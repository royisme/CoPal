# Changelog

## 2025-10-31 · Skillization Lifecycle Preview

### Added
- Documented `copal skill registry/search/scaffold/exec` commands in the README and usage guide.
- Introduced sandbox guarantee levels (`replay`, `reuse`, `fresh`) and `prelude.md` hand-off requirements.
- Added knowledge-base workflow and CLI guides to teach the new skill lifecycle.

### Impact for Downstream Projects
- Update `UserAgents.md` to reference preferred skill registries and required sandbox modes.
- Ensure planners attach generated `prelude.md` files when handing off tasks.
- Encourage implementers to capture `copal skill exec` logs inside `usage/` for review automation.
