import logging

from copal_cli.adapters.base import Adapter
from copal_cli.config.pack import Pack
from copal_cli.fs.writer import atomic_write

logger = logging.getLogger(__name__)

class GeminiAdapter(Adapter):
    @property
    def name(self) -> str:
        return "gemini"

    def export(self, pack: Pack) -> None:
        """
        Generate Gemini CLI prompts: .gemini/prompts/copal/*.md
        """
        gemini_dir = self.target_root / ".gemini" / "prompts" / "copal"
        gemini_dir.mkdir(parents=True, exist_ok=True)
        
        # Mapping of workflow -> prompt role
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
            
            # Append Prompt
            prompt_role = role_map.get(wf_name)
            if prompt_role:
                prompt_path = pack.get_prompt_path(prompt_role)
                if prompt_path and prompt_path.exists():
                    prompt_content = prompt_path.read_text(encoding="utf-8")
                    content += "\n\n---\n\n## Agent Role Definition\n\n" + prompt_content
            
            # Write
            target_file = gemini_dir / f"{wf_name}.md"
            atomic_write(target_file, content)
            logger.info(f"Exported {target_file}")
