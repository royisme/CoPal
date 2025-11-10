# CoPal Features Overview

CoPal is a comprehensive AI coding assistant workflow management tool. This document details all major features.

## Core Feature Modules

### 1. Six-Stage Workflow Orchestration 🔄

CoPal provides a structured software development workflow, ensuring a complete process from requirements analysis to code commit.

#### Stage Details

**Analyze Stage**
- **Purpose:** Deeply understand task requirements, gather relevant context
- **Input:** Task title, goals, constraints
- **Output:** Analysis report (`.copal/artifacts/analysis.md`)
- **Role:** Analyst
- **Key Activities:**
  - Understand business requirements
  - Identify technical challenges
  - Gather relevant background knowledge
  - Assess feasibility

**Spec Stage**
- **Purpose:** Write formal technical specification document
- **Input:** Analysis stage output
- **Output:** Technical specification (`.copal/artifacts/spec.md`)
- **Role:** Specifier
- **Key Activities:**
  - Define functional requirements
  - Clarify technical constraints
  - Design interface specifications
  - Establish acceptance criteria

**Plan Stage**
- **Purpose:** Create detailed implementation plan
- **Input:** Specification and analysis results
- **Output:** Implementation plan (`.copal/artifacts/plan.md`)
- **Role:** Planner
- **Key Activities:**
  - Break down tasks
  - Determine implementation order
  - Identify dependencies
  - Estimate effort

**Implement Stage**
- **Purpose:** Execute code implementation according to plan
- **Input:** Detailed implementation plan
- **Output:** Patch notes (`.copal/artifacts/patch-notes.md`)
- **Role:** Implementer
- **Key Activities:**
  - Write code
  - Add tests
  - Update documentation
  - Record changes

**Review Stage**
- **Purpose:** Assess code quality, prepare for release
- **Input:** Implemented code and patch notes
- **Output:** Review report (`.copal/artifacts/review.md`)
- **Role:** Reviewer
- **Key Activities:**
  - Code quality checks
  - Test coverage verification
  - Security review
  - Prepare PR description

**Commit Stage**
- **Purpose:** Record workflow metadata
- **Input:** All previous stage artifacts
- **Output:** Commit metadata (`.copal/artifacts/commit-metadata.json`)
- **Role:** Committer
- **Key Activities:**
  - Organize change history
  - Generate commit messages
  - Record workflow metrics
  - Archive artifacts

### 2. Knowledge Base Management 📚

CoPal provides a complete knowledge base system, supporting team knowledge sharing and best practice propagation.

#### Knowledge Base Structure

**Core Principles**
- Global development principles
- Environment guardrails
- Information architecture guides

**Role Templates**
- Analyst playbook
- Specifier playbook
- Planner playbook
- Implementer playbook
- Reviewer playbook

**Workflow Guides**
- Planning to implementation flow
- Implementation loop pattern
- Review and release process
- Skill lifecycle management

**Toolsets**
- Common CLI tool references
- Project tool integration guides
- Security guardrail scripts

#### Knowledge Base Features

**YAML Front Matter**
- Fast retrieval and filtering
- Version control
- Dependency management

**Template Override Mechanism**
- Preserve shared templates
- Support project-level overrides
- Flexible customization capabilities

**Validation Tools**
- Auto-validate metadata format
- Ensure knowledge base consistency
- Support custom validation rules

### 3. Skill System 🛠️

The skill system allows teams to create, share, and reuse automation modules.

#### Skill Components

**Skill Metadata (skill.json)**
```json
{
  "id": "my-skill",
  "name": "My Automation Skill",
  "language": "python",
  "version": "1.0.0",
  "description": "Automation task description",
  "requires_sandbox": true,
  "tags": ["automation", "testing"]
}
```

**Usage Instructions (prelude.md)**
- Runtime requirements
- Configuration instructions
- Usage examples
- Caveats

**Scripts and Tests**
- `scripts/` - Automation scripts
- `tests/` - Test cases
- `examples/` - Usage examples

**Execution Log (entrypoint.log)**
- Record execution process
- Facilitate debugging and review

#### Skill Features

**Scaffold Generation**
- Quickly create skill structure
- Support multiple languages (Python, Bash, JavaScript, etc.)
- Auto-generate template files

**Registry Management**
- Auto-scan and index skills
- Generate `registry.json`
- Support versioning

**Search and Discovery**
- Fuzzy search skills
- Filter by language
- Tag categorization

**Sandbox Execution**
- Secure execution environment
- Resource limits
- Output filtering
- Path access control

### 4. Memory Layer 🧠

The memory layer persists important information across workflow runs, forming a team knowledge graph.

#### Memory Types

**Decision**
- Technology selection decisions
- Architecture design decisions
- Tool and framework choices
- Example:
  ```bash
  copal memory add --type decision \
    --content "Use PostgreSQL as primary database" \
    --metadata reason="High performance, ACID support, rich ecosystem"
  ```

**Preference**
- Coding standard preferences
- Tool usage preferences
- Workflow preferences
- Example:
  ```bash
  copal memory add --type preference \
    --content "Format Python code with Black" \
    --metadata scope="project-wide"
  ```

**Experience**
- Problem-solving experiences
- Performance optimization experiences
- Error handling experiences
- Example:
  ```bash
  copal memory add --type experience \
    --content "Redis connection pool size should match worker processes" \
    --metadata impact="performance"
  ```

**Plan**
- Feature development plans
- Refactoring plans
- Migration plans
- Example:
  ```bash
  copal memory add --type plan \
    --content "Q1: Complete microservice decomposition" \
    --metadata priority="high"
  ```

**Note**
- Technical notes
- Meeting minutes
- Temporary remarks
- Example:
  ```bash
  copal memory add --type note \
    --content "Consider using gRPC instead of REST API" \
    --metadata context="architecture-discussion"
  ```

#### Memory Features

**Relationship Management**
- `SUPERSEDES` - Supersede relationship
- `RELATES_TO` - Related relationship
- `DEPENDS_ON` - Dependency relationship
- `REFERENCES` - Reference relationship
- `TEMPORAL_SEQUENCE` - Temporal relationship
- `ASSOCIATED_WITH` - Association relationship

**Query Capabilities**
- Keyword search
- Type filtering
- Metadata queries
- Relationship traversal

**Scope Management**
- `workflow_run` - Workflow run scope
- `global` - Global scope
- Automatic scope isolation

**Auto-Capture**
- Optional auto memory capture
- Auto-record each stage
- Configurable capture strategy

### 5. MCP Integration 🔌

Model Context Protocol (MCP) integration allows dynamic injection of usage guidance based on available tools.

#### MCP Tool Support

**context7**
- Deep research and knowledge acquisition
- Library and framework documentation queries
- API specification confirmation
- Stages: Analysis, Plan

**active-file**
- File location and navigation
- Code editing and modification
- Change tracking
- Stage: Implement

**file-tree**
- Directory structure exploration
- File organization understanding
- Path navigation
- Stage: Implement

#### Hook Mechanism

**Conditional Triggers**
```yaml
# Trigger when any tool available
- id: context7-analysis
  stage: analysis
  any_mcp: ["context7"]
  inject:
    - mcp/context7/usage.analysis.md

# Trigger when all tools available
- id: active-file-implement
  stage: implement
  all_mcp: ["active-file", "file-tree"]
  inject:
    - mcp/active-file/usage.implement.md
```

**Stage-Specific Guidance**
- Each tool can have guidance for multiple stages
- Guidance content tailored to stage characteristics
- Auto-inject into prompts

**Flexible Configuration**
- Easy to add new tool support
- Support custom hook blocks
- Composable rule system

### 6. Prompt Generation 📝

CoPal automatically generates structured prompts, ensuring AI assistants get complete context.

#### Prompt Composition

**Runtime Header**
- Current stage information
- Task metadata
- Available tools list
- Artifact locations

**Role Guidance**
- Role-specific responsibilities
- Best practice guides
- Workflow instructions

**MCP Tool Guidance**
- Tool usage instructions
- Examples and templates
- Caveats

**Context Links**
- Previous stage artifacts
- Related knowledge base docs
- Project-specific guidance

#### Prompt Features

**Auto-Assembly**
- Auto-compose based on configuration
- No manual editing needed
- Guarantee consistency

**Version Control**
- Prompts stored in `.copal/runtime/`
- Track history versions
- Easy debugging and optimization

**Extensibility**
- Support custom templates
- Inject project-specific content
- Flexible composition mechanism

## Utility Tools

### Status Management

**View Status (status)**
- Display all stage prompts
- List existing artifacts
- Suggest next action
- Show workflow progress

**Resume Workflow (resume)**
- Show most recent prompt
- Help continue after interruption
- Provide context information

### Validation Tools

**Knowledge Base Validation (validate)**
- Check YAML front matter
- Verify file format
- Ensure consistency
- Custom validation rules

### Initialization Tools

**Project Initialization (init)**
- Copy template files
- Create directory structure
- Preview actions (dry-run)
- Support force overwrite

## Integration Capabilities

### Version Control Integration
- `.copal/` directory can be committed to Git
- Knowledge base file version control
- Skill sharing and collaboration
- Memory persistence

### CI/CD Integration
- Use in CI workflows
- Automated workflow validation
- Skill execution automation
- Artifact archiving

### Team Collaboration
- Share knowledge base and skills
- Unify workflow standards
- Memory sharing and inheritance
- Best practice propagation

## Configuration Options

### Global Configuration

**Knowledge Base Configuration**
- Template paths
- Override strategy
- Validation rules

**MCP Configuration**
- Available tools list (`.copal/mcp-available.json`)
- Hook rules (`.copal/hooks/hooks.yaml`)

**Memory Configuration**
- Backend selection (`.copal/memory-config.json`)
- Auto-capture strategy
- Scope management

### Project Configuration

**User Guidance (UserAgents.md)**
- Project structure description
- Development standards
- Toolchain configuration
- Custom workflows

**Custom Knowledge Base**
- Role overrides
- Workflow extensions
- Toolset supplements

## Extensibility

### Custom Roles
- Create new role templates
- Extend existing roles
- Project-specific roles

### Custom Workflows
- Add new stages
- Modify stage order
- Customize processes

### Custom Skills
- Develop team-specific skills
- Encapsulate common operations
- Share automation modules

### Custom Hooks
- Add new MCP tool support
- Create custom guidance
- Extend hook system

## Security Features

### Sandbox Execution
- Limit resource usage
- Control file access
- Filter sensitive output
- Isolate execution environment

### Validation Mechanisms
- Knowledge base format validation
- Skill metadata validation
- Configuration file validation

### Permission Control
- Skill execution permissions
- File access permissions
- Network access control

## Performance Optimization

### Fast Retrieval
- YAML front matter indexing
- Skill registry caching
- Memory graph indexing

### Incremental Updates
- Sync only changed templates
- Incremental registry builds
- Smart caching mechanisms

## Summary

CoPal provides a complete AI coding assistant workflow management solution, including:

✅ **Structured Workflow** - Six well-defined stages
✅ **Knowledge Management** - Flexible knowledge base system
✅ **Skill Reuse** - Creation and sharing of automation modules
✅ **Memory Persistence** - Cross-workflow knowledge graph
✅ **Tool Integration** - MCP protocol support
✅ **Team Collaboration** - Knowledge and experience sharing
✅ **Extensibility** - Flexible customization capabilities
✅ **Security** - Sandbox and validation mechanisms

Use Cases:
- 🎯 Structured development for personal projects
- 👥 Knowledge sharing in team collaboration
- 🤖 Workflow orchestration for AI assistants
- 📚 Accumulation and propagation of best practices
- 🔧 Encapsulation and reuse of automation tasks

For more details, see:
- [Usage Guide](./USAGE.md)
- [Quick Start](./QUICKSTART.md)
- [Development Guide](./DEVELOPMENT.md)
- [MCP Hooks](./HOOKS.md)
