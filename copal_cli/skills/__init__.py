"""Skill management utilities for the CoPal CLI."""
from __future__ import annotations

from .registry import Registry, SkillEntry
from .scaffold import SkillMetadata, scaffold_skill

from .commands import (
    exec_command,
    registry_build_command,
    registry_list_command,
    scaffold_command,
    search_command,
)

__all__ = [
    "exec_command",
    "registry_build_command",
    "registry_list_command",
    "scaffold_command",
    "search_command",
    "Registry",
    "SkillEntry",
    "SkillMetadata",
    "scaffold_skill",
]
