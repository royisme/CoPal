from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import yaml

@dataclass
class Pack:
    name: str
    version: str
    description: str
    workflows: Dict[str, str]
    templates: Dict[str, str]
    schemas: Dict[str, str]
    scripts: Dict[str, str]
    prompts: Dict[str, str] = field(default_factory=dict)
    
    _base_path: Optional[Path] = None

    @classmethod
    def load(cls, path: Path) -> Pack:
        """Load pack from a pack.yaml file or directory containing it."""
        if path.is_dir():
            pack_file = path / "pack.yaml"
        else:
            pack_file = path
            
        if not pack_file.exists():
            raise FileNotFoundError(f"Pack configuration not found at {pack_file}")
            
        try:
            with open(pack_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in pack config: {e}")
            
        return cls(
            name=data.get("name", "unknown"),
            version=str(data.get("version", "0.1")),
            description=data.get("description", ""),
            workflows=data.get("workflows", {}),
            templates=data.get("templates", {}),
            schemas=data.get("schemas", {}),
            scripts=data.get("scripts", {}),
            prompts=data.get("prompts", {}),  # Added prompts support
            _base_path=pack_file.parent
        )

    def get_workflow_path(self, name: str) -> Optional[Path]:
        if name in self.workflows and self._base_path:
            return (self._base_path / self.workflows[name]).resolve()
        return None

    def get_prompt_path(self, name: str) -> Optional[Path]:
        if name in self.prompts and self._base_path:
            return (self._base_path / self.prompts[name]).resolve()
        return None

    def get_schema_path(self, name: str) -> Optional[Path]:
        if name in self.schemas and self._base_path:
            return (self._base_path / self.schemas[name]).resolve()
        return None

    def get_script_path(self, name: str) -> Optional[Path]:
        if name in self.scripts and self._base_path:
            return (self._base_path / self.scripts[name]).resolve()
        return None

    def get_template_path(self, name: str) -> Optional[Path]:
        if name in self.templates and self._base_path:
            return (self._base_path / self.templates[name]).resolve()
        return None
