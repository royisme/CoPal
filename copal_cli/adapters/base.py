from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from copal_cli.config.manifest import Manifest
from copal_cli.config.pack import Pack

class Adapter(ABC):
    def __init__(self, manifest: Manifest, target_root: Path):
        self.manifest = manifest
        self.target_root = target_root

    @abstractmethod
    def export(self, pack: Pack) -> None:
        """Export pack workflows to agent-specific commands."""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name (e.g. 'claude')."""
        pass
