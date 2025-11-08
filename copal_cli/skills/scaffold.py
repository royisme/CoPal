"""Skill scaffolding helper."""
from __future__ import annotations

import json
from pathlib import Path

DEFAULT_ENTRYPOINT = "run.txt"
DEFAULT_DESCRIPTION = "Describe the purpose of the skill."


class SkillScaffolder:
    """Create a new skill directory with boilerplate files."""

    def __init__(self, *, skills_root: Path):
        self.skills_root = Path(skills_root)

    def create(
        self,
        name: str,
        *,
        language: str = "python",
        description: str | None = None,
    ) -> Path:
        """Create a new skill skeleton and return its directory path."""
        self.skills_root.mkdir(parents=True, exist_ok=True)
        skill_dir = self.skills_root / name
        if skill_dir.exists():
            raise FileExistsError(f"Skill '{name}' already exists at {skill_dir}")
        skill_dir.mkdir(parents=True)
        metadata = {
            "name": name,
            "language": language,
            "description": description or DEFAULT_DESCRIPTION,
            "entrypoint": DEFAULT_ENTRYPOINT,
            "requires_sandbox": False,
        }
        (skill_dir / "skill.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (skill_dir / "prelude.md").write_text(
            f"# {name}\n\n{metadata['description']}\n",
            encoding="utf-8",
        )
        (skill_dir / DEFAULT_ENTRYPOINT).write_text(
            "# Add execution logs here.\n",
            encoding="utf-8",
        )
        return skill_dir
