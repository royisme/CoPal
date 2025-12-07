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
        Generate Claude Code commands: .claude/commands/copal/*.md
        
        Logic:
        For each workflow in the pack (plan, work, etc.):
        1. Inject Mandatory Header (Read AGENTS.md + Workflow file).
        2. Append the corresponding agent prompt (if available) from 'prompts'.
        3. Write to .claude/commands/copal/<name>.md
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
                raise FileNotFoundError(f"Workflow {wf_name} missing at {wf_path}")
                
            content = wf_path.read_text(encoding="utf-8")
            
            # 1. Inject Compliance Header and Prompt Reference
            # Get relative path for display instructions
            try:
                rel_wf = wf_path.relative_to(self.target_root)
            except ValueError:
                rel_wf = wf_path # Fallback if outside root
            
            prompt_role = role_map.get(wf_name)
            prompt_content = ""
            
            if prompt_role:
                prompt_path = pack.get_prompt_path(prompt_role)
                if prompt_path and prompt_path.exists():
                     prompt_content = prompt_path.read_text(encoding="utf-8")
            
            # Construct command file content
            # Strategy: The command file *is* the workflow wrapper.
            
            command_content = f"""# {wf_name.title()} Workflow

> **Harness Compliance**:
> Before starting, you **MUST** read:
> 1. `AGENTS.md` (Root rules)
> 2. `{rel_wf}` (Reference workflow)

---

## Workflow Instructions
{content}

"""
            if prompt_content:
                command_content += f"""
---

## Agent Role Definition
{prompt_content}
"""

            # 3. Write
            target_file = claude_dir / f"{wf_name}.md"
            atomic_write(target_file, command_content)
            logger.info(f"Exported {target_file}")
