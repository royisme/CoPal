# UserAgents.md - Project Specific Instructions

> **Purpose**: This file contains project-specific context that AI Agents need to understand your codebase.
> **Important**: This file MUST be populated before any Agent can work effectively on your project.
> **Auto-Init**: If sections below contain placeholders `[...]`, the Agent will auto-populate them on first run.

---

## 1. Project Overview

| Field         | Value                                      |
| ------------- | ------------------------------------------ |
| **Name**      | [Project Name - auto-detected from config] |
| **Type**      | [e.g., CLI Tool, Web App, Library, API]    |
| **Language**  | [Primary language]                         |
| **Framework** | [Main framework if applicable]             |
| **Goal**      | [Brief description of what this project does] |

## 2. Tech Stack

### Core Dependencies

| Category    | Technology | Version | Notes |
| ----------- | ---------- | ------- | ----- |
| Language    | [e.g., Python] | [e.g., 3.11+] | |
| Framework   | [e.g., FastAPI] | | |
| Database    | [e.g., PostgreSQL] | | |
| Testing     | [e.g., pytest] | | |

### Dev Dependencies

- [e.g., black, ruff, mypy]

## 3. Key Commands

```bash
# Install dependencies
[command]

# Run development server / main entry
[command]

# Run tests
[command]

# Lint / Format
[command]

# Build / Package
[command]
```

## 4. Project Structure

```
[root]/
├── [src/]           # Source code
├── [tests/]         # Test files
├── [config/]        # Configuration
└── [docs/]          # Documentation
```

### Key Directories

| Directory | Purpose |
| --------- | ------- |
| [src/]    | [Description] |
| [tests/]  | [Description] |

## 5. Architecture & Patterns

### Design Patterns

- [e.g., Repository Pattern for data access]
- [e.g., Dependency Injection]

### Code Conventions

- [e.g., Use type hints everywhere]
- [e.g., Docstrings in Google style]

### File Naming

- [e.g., snake_case for Python files]
- [e.g., PascalCase for classes]

## 6. Constraints & Rules

> **IMPORTANT**: The Agent MUST follow these rules.

### Must Do

- [ ] [e.g., All functions must have type hints]
- [ ] [e.g., Run tests before committing]
- [ ] [e.g., Update CHANGELOG for user-facing changes]

### Must NOT Do

- [ ] [e.g., No new dependencies without approval]
- [ ] [e.g., No direct database queries outside repository layer]
- [ ] [e.g., No hardcoded secrets or credentials]

## 7. Context Links

> Links to other important documentation the Agent should be aware of.

- [Architecture Doc](.copal/docs/architecture.md)
- [API Reference](./docs/api.md)
- [Contributing Guide](./CONTRIBUTING.md)
