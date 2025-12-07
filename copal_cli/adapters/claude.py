from pathlib import Path
import logging

from copal_cli.adapters.base import Adapter
from copal_cli.config.pack import Pack
from copal_cli.fs.writer import atomic_write

logger = logging.getLogger(__name__)

class ClaudeAdapter(Adapter):
    @property
    def name(self) -> str:
        return "claude"

    def export(self, pack: Pack) -> None:
        """
        Generate Claude Code configuration:
        1. Subagents in .claude/agents/*.md
        2. Commands in .claude/commands/copal/*.md
        """
        self._export_subagents(pack)
        self._export_commands(pack)
        self._export_orchestrator_start(pack)

    def _export_subagents(self, pack: Pack) -> None:
        """
        Export subagent definitions to .claude/agents/
        """
        # User-level agents are typically in ~/.claude/agents, but for project-specific
        # we put them in .claude/agents/ in the project root.
        agents_dir = self.target_root / ".claude" / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)

        for role, prompt_rel_path in pack.prompts.items():
            prompt_path = pack.get_prompt_path(role)
            if not prompt_path or not prompt_path.exists():
                logger.warning(f"Prompt for role {role} not found at {prompt_path}")
                continue

            content = prompt_path.read_text(encoding="utf-8")
            
            # Create agent definition with frontmatter
            agent_content = f"""---
description: Copal {role.title()} Agent - {pack.description}
---
{content}
"""
            # Agent name: copal-{role}
            agent_file = agents_dir / f"copal-{role}.md"
            atomic_write(agent_file, agent_content)
            logger.info(f"Exported subagent {agent_file}")

    def _export_commands(self, pack: Pack) -> None:
        """
        Generate slash commands that utilize the subagents.
        """
        claude_dir = self.target_root / ".claude" / "commands" / "copal"
        claude_dir.mkdir(parents=True, exist_ok=True)
        
        # Mappings of workflow -> prompt role
        role_map = {
            "plan": "planner",
            "research": "researcher",
            "confirm": "single_agent", 
            "work": "worker",
            "review": "reviewer",
            "codify": "codifier"
        }

        for wf_name, wf_rel_path in pack.workflows.items():
            wf_path = pack.get_workflow_path(wf_name)
            if not wf_path or not wf_path.exists():
                logger.error(f"Workflow {wf_name} file not found: {wf_path}")
                continue
                
            content = wf_path.read_text(encoding="utf-8")
            
            try:
                rel_wf = wf_path.relative_to(self.target_root)
            except ValueError:
                rel_wf = wf_path

            prompt_role = role_map.get(wf_name)
            
            # Construct command file content
            command_content = f"""# {wf_name.title()} Workflow

> **Harness Compliance**:
> Before starting, you **MUST** read:
> 1. `AGENTS.md` (Root rules)
> 2. `{rel_wf}` (Reference workflow)

---

## Workflow Instructions
{content}

"""
            # Append instructions to switch agent if applicable
            if prompt_role:
                command_content += f"""
---
> **AGENT SWITCH**:
> Please switch to the **`copal-{prompt_role}`** agent to execute this phase.
> Use: `/agent run copal-{prompt_role} "Execute {wf_name} phase"`
"""

            target_file = claude_dir / f"{wf_name}.md"
            atomic_write(target_file, command_content)
            logger.info(f"Exported command {target_file}")

    def _export_orchestrator_start(self, pack: Pack) -> None:
        """
        Export the 'start' command which initiates the orchestrator loop.
        """
        claude_dir = self.target_root / ".claude" / "commands" / "copal"
        claude_dir.mkdir(parents=True, exist_ok=True)

        content = """# Start Engineering Loop

This command initiates the **Automated Engineering Loop**.

> **Orchestrator Activation**:
> You are handing over control to the **`copal-orchestrator`** agent.
> This agent will manage the lifecycle of the task (Plan -> Research -> Work -> Review).

## Instructions for User
1. Ensure you have provided a clear task description in the chat context.
2. Run the command below to start.

## Auto-Start
/agent run copal-orchestrator "Please assume the role of Orchestrator and execute the engineering loop for the user's task."
"""
        target_file = claude_dir / "start.md"
        atomic_write(target_file, content)
        logger.info(f"Exported orchestrator start command {target_file}")
