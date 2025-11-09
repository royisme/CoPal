"""Skill selection helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .registry import SkillMetadata


@dataclass(slots=True)
class SkillMatch:
    """Represents a search result."""

    skill: SkillMetadata
    score: int


class SkillSelector:
    """Simple substring based skill selector."""

    def __init__(self, skills: Iterable[SkillMetadata]):
        self._skills = list(skills)

    def search(self, query: str, *, language: str | None = None) -> list[SkillMatch]:
        """Return skills that match the query and optional language filter."""
        normalized_query = query.lower()
        matches: list[SkillMatch] = []
        for skill in self._skills:
            if language and skill.language != language:
                continue
            haystacks = [skill.name, skill.description, skill.prelude]
            score = sum(normalized_query in (text or "").lower() for text in haystacks)
            if score:
                matches.append(SkillMatch(skill=skill, score=score))
        matches.sort(key=lambda match: (-match.score, match.skill.name))
        return matches
