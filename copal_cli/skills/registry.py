"""Skill registry discovery utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence


class RegistryError(ValueError):
    """Raised when the skills registry cannot be created."""


def _load_yaml_block(block: str) -> Dict[str, object]:
    """Parse a minimal subset of YAML for skill metadata.

    The parser first attempts to use :mod:`yaml` if available, falling back to a
    very small hand-written subset that supports the constructs required by the
    tests (scalars and simple lists).
    """

    block = block.strip()
    if not block:
        return {}

    try:  # pragma: no cover - executed only when PyYAML is installed.
        import yaml  # type: ignore

        loaded = yaml.safe_load(block) or {}
        if not isinstance(loaded, dict):
            raise RegistryError("Skill metadata must be a mapping")
        return loaded
    except ModuleNotFoundError:
        return _parse_simple_yaml(block)


def _parse_simple_yaml(block: str) -> Dict[str, object]:
    result: Dict[str, object] = {}
    current_key: Optional[str] = None
    current_list: Optional[List[object]] = None

    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-"):
            if current_key is None or current_list is None:
                raise RegistryError("List item found before list key in metadata")
            current_list.append(line[1:].strip())
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
                result[key] = items
                current_key = key
                current_list = None
            elif value:
                result[key] = value
                current_key = key
                current_list = None
            else:
                result[key] = []
                current_key = key
                current_list = result[key]
        else:
            raise RegistryError(f"Unable to parse metadata line: {raw_line!r}")

    return result


@dataclass(frozen=True)
class SkillMeta:
    identifier: str
    name: str
    description: str
    tags: Sequence[str]
    origin: str
    skill_path: Path

    @classmethod
    def from_file(cls, path: Path, origin: str) -> "SkillMeta":
        text = path.read_text(encoding="utf-8")
        metadata_block = _extract_metadata_block(text)
        metadata = _load_yaml_block(metadata_block)

        required = {"id", "name", "description", "tags"}
        missing = sorted(required - metadata.keys())
        if missing:
            raise RegistryError(f"Missing fields {missing} in {path}")

        tags = metadata["tags"]
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            raise RegistryError(f"Tags must be a list of strings in {path}")

        identifier = str(metadata["id"]).strip()
        name = str(metadata["name"]).strip()
        description = str(metadata["description"]).strip()

        if not identifier or not name or not description:
            raise RegistryError(f"Fields id, name, and description must be non-empty in {path}")

        return cls(
            identifier=identifier,
            name=name,
            description=description,
            tags=tuple(tag.strip() for tag in tags),
            origin=origin,
            skill_path=path.parent,
        )

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.identifier,
            "name": self.name,
            "description": self.description,
            "tags": list(self.tags),
            "origin": self.origin,
            "path": str(self.skill_path),
        }

    @property
    def searchable_text(self) -> str:
        parts = [self.name, self.description, " ".join(self.tags)]
        return " \n".join(part for part in parts if part)


class Registry:
    def __init__(self, skills: Sequence[SkillMeta]):
        self._skills = list(skills)
        self._by_id = {skill.identifier: skill for skill in skills}

    @property
    def skills(self) -> Sequence[SkillMeta]:
        return tuple(self._skills)

    @classmethod
    def build(
        cls,
        skill_roots: Mapping[str, Path],
        output_dir: Path,
        *,
        prelude_max_chars: int = 1500,
    ) -> "Registry":
        discovered: List[SkillMeta] = []
        seen_ids: Dict[str, Path] = {}

        for origin, root in skill_roots.items():
            if root is None:
                continue
            root = Path(root)
            if not root.exists():
                continue
            for skill_file in sorted(root.rglob("SKILL.md")):
                skill = SkillMeta.from_file(skill_file, origin)
                if skill.identifier in seen_ids:
                    raise RegistryError(
                        "Duplicate skill id '{id}' between {first} and {second}".format(
                            id=skill.identifier,
                            first=seen_ids[skill.identifier],
                            second=skill_file,
                        )
                    )
                seen_ids[skill.identifier] = skill_file
                discovered.append(skill)

        if not discovered:
            return cls([])

        discovered.sort(key=lambda s: (s.name.lower(), s.identifier))
        registry = cls(discovered)

        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "skills.json").write_text(
            json.dumps([skill.to_dict() for skill in discovered], indent=2),
            encoding="utf-8",
        )
        prelude_content = _synthesise_prelude(discovered, prelude_max_chars)
        (output_dir / "prelude.md").write_text(prelude_content, encoding="utf-8")

        return registry


def _extract_metadata_block(text: str) -> str:
    text = text.lstrip()
    if not text.startswith("---"):
        raise RegistryError("Skill metadata must start with a YAML front matter block")

    lines = text.splitlines()
    if lines[0].strip() != "---":
        raise RegistryError("Skill metadata must start with '---'")

    end_index: Optional[int] = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break

    if end_index is None:
        raise RegistryError("Skill metadata front matter not terminated")

    metadata_lines = lines[1:end_index]
    return "\n".join(metadata_lines)


def _synthesise_prelude(skills: Sequence[SkillMeta], max_chars: int) -> str:
    sections: List[str] = []
    for skill in skills:
        section = f"## {skill.name}\n{skill.description.strip()}\n"
        if skill.tags:
            section += f"Tags: {', '.join(skill.tags)}\n"
        sections.append(section.strip())

    prelude = "\n\n".join(sections).strip() + "\n"

    if len(prelude) <= max_chars:
        return prelude

    if max_chars <= 1:
        return "…"[:max_chars]

    truncated = prelude[: max_chars - 1].rstrip()
    return truncated + "…\n"
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
