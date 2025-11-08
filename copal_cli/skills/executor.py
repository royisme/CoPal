"""Skill execution utilities."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TextIO

from .registry import SkillMetadata

logger = logging.getLogger(__name__)


class SkillExecutionError(RuntimeError):
    """Raised when a skill fails to execute."""


class SkillExecutor:
    """Execute a skill by streaming its entrypoint file."""

    def __init__(self, *, stream: TextIO):
        self.stream = stream

    def execute(self, skill: SkillMetadata, *, sandbox: bool = False) -> None:
        """Execute the provided skill."""
        if skill.requires_sandbox and not sandbox:
            raise PermissionError(
                f"Skill '{skill.name}' requires sandbox execution. Re-run with --sandbox."
            )
        entry_path = Path(skill.path) / skill.entrypoint
        if not entry_path.exists():
            raise FileNotFoundError(entry_path)
        logger.debug("Streaming entrypoint %s", entry_path)
        with entry_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                self.stream.write(line.rstrip("\n") + "\n")
        self.stream.flush()
