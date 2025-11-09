# Project Customisation Guide

Use this directory to store project-specific role guidance, workflows, and tech-stack notes.

Suggested structure:

```
UserAgents.md                        # Entry point for project-specific guidance
docs/agents/                         # Optional directory for extended docs
└── knowledge-base/                  # Mirror global templates if you need overrides
    ├── roles/
    ├── workflows/
    └── toolsets/
```

Recommended steps:

1. After running `copal init`, edit `UserAgents.md` to describe the project structure, commands, and safety policies.
2. Copy any templates from `.copal/global/knowledge-base/` that you need to override and place them under `docs/agents/knowledge-base/`.
3. Link those documents from `UserAgents.md` so agents know where to find them.
4. Keep custom documents under version control and update them as the project evolves.

> If the project already has an established documentation system, this directory can simply contain links or indexes that point the agent to the right resources.
