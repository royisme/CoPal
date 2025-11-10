# CoPal Quick Start Guide

Get started with CoPal in 5 minutes!

## Step 1: Install CoPal

```bash
# Clone the repository
git clone https://github.com/royisme/CoPal.git
cd CoPal

# Install
pip install -e .
```

## Step 2: Initialize Your Project

In your project root directory:

```bash
cd /path/to/your-project
copal init --target .
```

This creates:
- `AGENTS.md` - Navigation guide for AI assistants
- `UserAgents.md` - Project-specific guidance
- `.copal/` - Knowledge base and configuration directory

## Step 3: Customize Your Project (Optional)

Edit `UserAgents.md` to add project-specific information:

```markdown
# User Agent Guidance

## Project Structure
This project uses Python + FastAPI...

## Development Standards
- Use Black for code formatting
- Test coverage must be > 80%
```

## Step 4: Run Your First Workflow

```bash
# 1. Analyze task
copal analyze --title "Add user registration" --goals "Implement user registration feature"

# 2. Write specification (AI assistant reads prompt and creates spec)
# View generated prompt: .copal/runtime/analysis.prompt.md
# AI assistant should create: .copal/artifacts/analysis.md

# 3. Continue with other stages
copal spec      # Write specification
copal plan      # Create plan
copal implement # Implement feature
copal review    # Code review
copal commit    # Commit record

# 4. Check progress
copal status
```

## Step 5: Configure MCP Tools (Optional)

If you're using context7 or other MCP tools:

```bash
# Declare available tools
cat <<'JSON' > .copal/mcp-available.json
["context7", "active-file", "file-tree"]
JSON

# View configured tools
copal mcp ls
```

## Command Quick Reference

### Workflow Commands
```bash
copal analyze           # Analysis stage
copal spec             # Specification stage
copal plan             # Planning stage
copal implement        # Implementation stage
copal review           # Review stage
copal commit           # Commit stage
copal status           # View status
copal resume           # Resume workflow
```

### Skill Commands
```bash
copal skill scaffold my-skill --lang python   # Create skill
copal skill registry build                     # Build registry
copal skill search --query "testing"           # Search skills
copal skill exec --skill my-skill             # Execute skill
```

### Memory Commands
```bash
copal memory add --type decision --content "..." # Add memory
copal memory search --query "auth"               # Search memory
copal memory list --type decision                # List decisions
copal memory show <id>                           # View details
```

## Workflow Example

### Example: Adding a New Feature

```bash
# 1. Analyze requirements
copal analyze \
  --title "Add OAuth2 login" \
  --goals "Support Google and GitHub OAuth2 login" \
  --constraints "Must be compatible with existing auth system"

# AI assistant reads .copal/runtime/analysis.prompt.md
# AI assistant creates .copal/artifacts/analysis.md

# 2. Write specification
copal spec
# AI assistant reads prompt, creates .copal/artifacts/spec.md

# 3. Create plan
copal plan
# AI assistant reads prompt, creates .copal/artifacts/plan.md

# 4. Implement feature
copal implement
# AI assistant implements according to plan, creates .copal/artifacts/patch-notes.md

# 5. Code review
copal review
# AI assistant reviews code, creates .copal/artifacts/review.md

# 6. Record metadata
copal commit
# AI assistant records metadata to .copal/artifacts/commit-metadata.json

# 7. View complete status
copal status
```

## Memory Management Example

```bash
# Record technical decision
copal memory add \
  --type decision \
  --content "Use Redis for session storage" \
  --metadata reason="High performance and persistence support"

# Search related decisions
copal memory search --query "Redis"

# Update decision
copal memory update <id> --content "Use Redis 7+ for session storage"

# Supersede old decision
copal memory supersede <id> \
  --type decision \
  --content "Migrate to Valkey (Redis fork)"
```

## Skill Management Example

```bash
# Create deployment skill
copal skill scaffold deployment \
  --skills-root .copal/skills \
  --lang bash \
  --description "Automated deployment to production"

# Develop skill...
# Edit .copal/skills/deployment/scripts/deploy.sh
# Edit .copal/skills/deployment/prelude.md

# Build registry
copal skill registry build --skills-root .copal/skills

# Team members search for skill
copal skill search --query "deploy"

# Execute skill
copal skill exec --skills-root .copal/skills --skill deployment
```

## Directory Structure

Project structure after initialization:

```
your-project/
├── AGENTS.md                    # AI assistant navigation
├── UserAgents.md               # Project-specific guidance
├── .copal/
│   ├── global/                 # Shared knowledge base
│   │   └── knowledge-base/
│   │       ├── core/           # Core principles
│   │       ├── roles/          # Role templates
│   │       ├── workflows/      # Workflow guides
│   │       └── toolsets/       # Toolsets
│   ├── hooks/                  # MCP hooks
│   │   ├── hooks.yaml         # Hook configuration
│   │   └── mcp/               # MCP tool guidance
│   ├── mcp-available.json     # Available MCP tools
│   ├── runtime/               # Runtime prompts (auto-generated)
│   ├── artifacts/             # Workflow artifacts (auto-generated)
│   ├── skills/                # Skill library (optional)
│   └── memory/                # Memory storage (optional)
└── [Your project files]
```

## Best Practice Tips

1. **Execute stages in order** - Always follow analyze → spec → plan → implement → review → commit sequence
2. **Save artifacts** - AI assistant should save each stage's results in `.copal/artifacts/`
3. **Use memory** - Record important decisions and experiences for future reference
4. **Share skills** - Encapsulate useful automation as skills for team reuse
5. **Sync regularly** - Periodically run `copal init --force` to get latest template updates

## Next Steps

- 📖 Read the [Complete Usage Guide](./USAGE.md) to learn about all features
- 🔧 Check the [Development Guide](./DEVELOPMENT.md) to learn how to contribute
- 🎯 Explore [Examples](../examples/) for advanced usage
- 💡 See [MCP Hooks Documentation](./HOOKS.md) for tool integration

## Need Help?

- Use `copal <command> --help` for command help
- Check [GitHub Issues](https://github.com/royisme/CoPal/issues) to ask questions or report issues
- Read the [complete documentation](./USAGE.md) for detailed instructions

Happy coding! 🚀
