"""Skill registry management utilities."""
from __future__ import annotations

import json
import logging
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SkillMetadata:
    """Metadata describing a single skill."""

    name: str
    path: Path = field(repr=False, compare=False)
    description: str
    language: str
    entrypoint: str
    prelude: str = ""
    requires_sandbox: bool = False

    def to_dict(self) -> dict[str, object]:
        """Serialise the metadata into a JSON friendly dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "entrypoint": self.entrypoint,
            "prelude": self.prelude,
            "requires_sandbox": self.requires_sandbox,
            "path": str(self.path.name),
        }


class SkillRegistry:
    """In-memory representation of the available skills."""

    def __init__(self, *, root: Path, skills: Iterable[SkillMetadata]):
        self.root = Path(root)
        ordered = sorted(skills, key=lambda skill: skill.name)
        self._skills: "OrderedDict[str, SkillMetadata]" = OrderedDict(
            (skill.name, skill) for skill in ordered
        )

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._skills)

    def __iter__(self) -> Iterator[SkillMetadata]:  # pragma: no cover - convenience
        return iter(self._skills.values())

    @property
    def skills(self) -> list[SkillMetadata]:
        """Return the registry contents as a list."""
        return list(self._skills.values())

    def list(self, *, language: str | None = None) -> list[SkillMetadata]:
        """Return skills filtered by language if specified."""
        if language is None:
            return self.skills
        return [skill for skill in self._skills.values() if skill.language == language]

    def get(self, name: str) -> SkillMetadata:
        """Return metadata for the skill with the given name."""
        if name not in self._skills:
            raise KeyError(name)
        return self._skills[name]

    def to_index(self) -> dict[str, object]:
        """Serialise the registry to a JSON structure."""
        return {"skills": [skill.to_dict() for skill in self._skills.values()]}

    def write_index(self) -> Path:
        """Write the registry index JSON file and return its path."""
        index_path = self.root / "registry.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        with index_path.open("w", encoding="utf-8") as fh:
            json.dump(self.to_index(), fh, indent=2, ensure_ascii=False)
        return index_path

    @classmethod
    def from_index(cls, root: Path) -> "SkillRegistry":
        """Load a registry from an existing index file."""
        index_path = Path(root) / "registry.json"
        if not index_path.exists():
            raise FileNotFoundError(index_path)
        with index_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        skills: list[SkillMetadata] = []
        for item in payload.get("skills", []):
            path = Path(root) / str(item.get("path", item.get("name")))
            skills.append(
                SkillMetadata(
                    name=str(item["name"]),
                    path=path,
                    description=str(item.get("description", "")),
                    language=str(item.get("language", "")),
                    entrypoint=str(item.get("entrypoint", "")),
                    prelude=str(item.get("prelude", "")),
                    requires_sandbox=bool(item.get("requires_sandbox", False)),
                )
            )
        return cls(root=Path(root), skills=skills)


class SkillRegistryBuilder:
    """Builder that scans a skills directory for metadata."""

    def __init__(self, *, skills_root: Path):
        self.skills_root = Path(skills_root)

    def build(self) -> SkillRegistry:
        """Scan the skills root and construct a registry."""
        self.skills_root.mkdir(parents=True, exist_ok=True)
        skills: list[SkillMetadata] = []
        for entry in sorted(self.skills_root.iterdir()):
            if not entry.is_dir():
                continue
            metadata_path = entry / "skill.json"
            if not metadata_path.exists():
                logger.debug("Skipping %s (missing skill.json)", entry)
                continue
            with metadata_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            name = str(payload.get("name") or entry.name)
            description = str(payload.get("description", ""))
            language = str(payload.get("language", ""))
            entrypoint = str(payload.get("entrypoint", "run.txt"))
            requires_sandbox = bool(payload.get("requires_sandbox", False))
            prelude_path = entry / "prelude.md"
            prelude = ""
            if prelude_path.exists():
                prelude = prelude_path.read_text(encoding="utf-8").strip()
            skills.append(
                SkillMetadata(
                    name=name,
                    path=entry,
                    description=description,
                    language=language,
                    entrypoint=entrypoint,
                    prelude=prelude,
                    requires_sandbox=requires_sandbox,
                )
            )
        registry = SkillRegistry(root=self.skills_root, skills=skills)
        logger.debug("Discovered %d skill(s) in %s", len(registry.skills), self.skills_root)
        return registry

    def build_and_write(self) -> SkillRegistry:
        """Convenience method to build the registry and persist it."""
        registry = self.build()
        registry.write_index()
        return registry
