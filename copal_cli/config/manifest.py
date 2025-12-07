from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Any

import yaml

logger = logging.getLogger(__name__)

@dataclass
class ProjectInfo:
    name: str
    description: str = ""

@dataclass
class ArtifactsConfig:
    dir: str
    commit_policy: str = "optional"

@dataclass
class VerifyConfig:
    command: str
    windows_command: Optional[str] = None

@dataclass
class MemoryConfig:
    enabled: bool = True
    provider: str = "json"

@dataclass
class Manifest:
    version: str
    project: ProjectInfo
    default_pack: str
    verify: Optional[VerifyConfig]
    artifacts: ArtifactsConfig
    packs: List[Dict[str, str]] = field(default_factory=list)
    adapters: List[str] = field(default_factory=list)
    memory: Optional[MemoryConfig] = None
    
    _raw_path: Optional[Path] = None

    @classmethod
    def load(cls, path: Path) -> Manifest:
        """Load manifest from a YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Manifest not found at {path}")
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in manifest: {e}")

        # Basic validation
        if not isinstance(data, dict):
            raise ValueError("Manifest root must be a dictionary")
            
        if "tools" in data:
            raise ValueError("Invalid manifest: 'tools' field is deprecated/not supported. Use 'adapters'.")
            
        required_fields = ["version", "project", "default_pack"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field in manifest: {field}")

        # Parse nested structures
        project_data = data.get("project", {})
        project_info = ProjectInfo(
            name=project_data.get("name", "unnamed"),
            description=project_data.get("description", "")
        )

        artifacts_data = data.get("artifacts", {})
        artifacts_config = ArtifactsConfig(
            dir=artifacts_data.get("dir", ".copal/artifacts"),
            commit_policy=artifacts_data.get("commit_policy", "optional")
        )

        verify_data = data.get("verify")
        verify_config = None
        if verify_data:
            verify_config = VerifyConfig(
                command=verify_data.get("command", ""),
                windows_command=verify_data.get("windows_command")
            )

        packs = data.get("packs", [])
        if not isinstance(packs, list):
            packs = []
            
        adapters = data.get("adapters", [])
        if not isinstance(adapters, list):
            adapters = []

        memory_config = None
        memory_data = data.get("memory")
        if memory_data:
             memory_config = MemoryConfig(
                 enabled=memory_data.get("enabled", True),
                 provider=memory_data.get("provider", "json")
             )
        
        manifest = cls(
            version=str(data.get("version", "0.1")),
            project=project_info,
            default_pack=data.get("default_pack", ""),
            verify=verify_config,
            artifacts=artifacts_config,
            packs=packs,
            adapters=adapters,
            memory=memory_config,
            _raw_path=path
        )
        return manifest

    def save(self, path: Optional[Path] = None) -> None:
        """Save manifest to YAML."""
        target_path = path or self._raw_path
        if not target_path:
            raise ValueError("No path specified for saving manifest")
            
        verify_dict = None
        if self.verify:
            verify_dict = {
                "command": self.verify.command,
            }
            if self.verify.windows_command:
                verify_dict["windows_command"] = self.verify.windows_command

        data = {
            "version": self.version,
            "project": {
                "name": self.project.name,
                "description": self.project.description
            },
            "default_pack": self.default_pack,
            "artifacts": {
                "dir": self.artifacts.dir,
                "commit_policy": self.artifacts.commit_policy
            },
            "packs": self.packs,
            "adapters": self.adapters
        }
        
        if verify_dict:
            data["verify"] = verify_dict

        with open(target_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, indent=2)

def find_manifest(start_path: Path) -> Optional[Path]:
    """Find .copal/manifest.yaml starting from start_path upwards."""
    current = start_path.resolve()
    while True:
        manifest_path = current / ".copal" / "manifest.yaml"
        if manifest_path.exists():
            return manifest_path
        
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None
