"""Skill management utilities for CoPal."""
from __future__ import annotations

from .registry import Registry, SkillEntry
from .scaffold import SkillMetadata, scaffold_skill

__all__ = [
    "Registry",
    "SkillEntry",
    "SkillMetadata",
    "scaffold_skill",
]
