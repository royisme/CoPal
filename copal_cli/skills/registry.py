"""Skill registry discovery utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator


@dataclass(slots=True)
class SkillEntry:
    """Lightweight representation of a registered skill."""

    identifier: str
    name: str
    description: str
    tags: tuple[str, ...]
    path: Path

    @property
    def skill_root(self) -> Path:
        """Return the root directory of the skill."""

        return self.path


class Registry:
    """Collection of known skills backed by ``skills.json`` manifest."""

    def __init__(self, root: Path, entries: Dict[str, SkillEntry]) -> None:
        self._root = root
        self._entries = entries

    def __contains__(self, identifier: str) -> bool:  # pragma: no cover - trivial
        return identifier in self._entries

    def __iter__(self) -> Iterator[SkillEntry]:  # pragma: no cover - trivial
        return iter(self._entries.values())

    @property
    def root(self) -> Path:
        """Return the registry root path."""

        return self._root

    @property
    def entries(self) -> Dict[str, SkillEntry]:  # pragma: no cover - trivial
        """Return a copy of the registry entries mapping."""

        return dict(self._entries)

    def get(self, identifier: str) -> SkillEntry | None:
        """Retrieve a skill entry by identifier."""

        return self._entries.get(identifier)

    @classmethod
    def build(cls, root: str | Path) -> "Registry":
        """Build a registry from the provided root directory."""

        root_path = Path(root).resolve()
        manifest_path = root_path / "skills.json"
        if not manifest_path.exists():
            return cls(root_path, {})

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = {}
        for item in data.get("skills", []):
            identifier = item.get("id")
            if not identifier:
                continue
            rel_path = item.get("path", identifier)
            skill_path = (root_path / rel_path).resolve()
            if not skill_path.exists():
                skill_path = root_path / rel_path
            entry = SkillEntry(
                identifier=identifier,
                name=item.get("name", identifier),
                description=item.get("description", ""),
                tags=tuple(item.get("tags", [])),
                path=skill_path,
            )
            entries[identifier] = entry
        return cls(root_path, entries)

    def to_manifest(self) -> dict:
        """Serialize the registry into manifest format."""

        skills: Iterable[dict[str, object]] = (
            {
                "id": entry.identifier,
                "name": entry.name,
                "description": entry.description,
                "tags": list(entry.tags),
                "path": str(entry.path.relative_to(self._root)),
            }
            for entry in sorted(self._entries.values(), key=lambda e: e.identifier)
        )
        return {"skills": list(skills)}
