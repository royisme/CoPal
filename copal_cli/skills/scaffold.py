"""Generate skill scaffolds from reusable templates."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from string import Template
from typing import Iterable, Mapping
DEFAULT_ENTRYPOINT = "run.txt"
DEFAULT_DESCRIPTION = "Describe the purpose of the skill."

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = PACKAGE_DIR.parent / "templates" / "skills"

_SLUG_PATTERN = re.compile(r"[^a-z0-9]+")

class SkillScaffolder:
    """Create a new skill directory with boilerplate files."""

    def __init__(self, *, skills_root: Path):
        self.skills_root = Path(skills_root)

    def create(
        self,
        name: str,
        *,
        language: str = "python",
        description: str | None = None,
    ) -> Path:
        """Create a new skill skeleton and return its directory path."""
        self.skills_root.mkdir(parents=True, exist_ok=True)
        skill_dir = self.skills_root / name
        if skill_dir.exists():
            raise FileExistsError(f"Skill '{name}' already exists at {skill_dir}")
        skill_dir.mkdir(parents=True)
        metadata = {
            "name": name,
            "language": language,
            "description": description or DEFAULT_DESCRIPTION,
            "entrypoint": DEFAULT_ENTRYPOINT,
            "requires_sandbox": False,
        }
        (skill_dir / "skill.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (skill_dir / "prelude.md").write_text(
            f"# {name}\n\n{metadata['description']}\n",
            encoding="utf-8",
        )
        (skill_dir / DEFAULT_ENTRYPOINT).write_text(
            "# Add execution logs here.\n",
            encoding="utf-8",
        )
        return skill_dir




@dataclass(slots=True)
class SkillMetadata:
    """User-supplied attributes for a new skill."""

    name: str
    description: str
    tags: tuple[str, ...] = ()


def _slugify(value: str) -> str:
    """Return a filesystem-safe slug."""

    slug = _SLUG_PATTERN.sub("-", value.lower()).strip("-")
    if not slug:
        raise ValueError("Skill name must contain alphanumeric characters")
    return slug


def _normalise_tags(tags: Iterable[str], fallback: str) -> list[str]:
    """Normalise tags into slugified, de-duplicated values."""

    seen: set[str] = set()
    normalised: list[str] = []
    for tag in tags:
        slug = _slugify(tag)
        if slug not in seen:
            seen.add(slug)
            normalised.append(slug)
    if not normalised:
        normalised.append(fallback)
    return normalised


def _render_template(template_path: Path, context: Mapping[str, str]) -> str:
    """Render a string.Template with the provided context."""

    raw = template_path.read_text(encoding="utf-8")
    return Template(raw).substitute(context)


def _write_file(path: Path, content: str, *, force: bool) -> None:
    """Write content to disk, respecting the force flag."""

    if path.exists() and not force:
        raise FileExistsError(f"Target file already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _update_manifest(manifest_path: Path, entry: Mapping[str, object], *, force: bool) -> None:
    """Insert or update a skill entry inside ``skills.json``."""

    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        data = {"skills": []}

    skills = {item.get("id"): item for item in data.get("skills", []) if item.get("id")}
    identifier = entry["id"]
    if identifier in skills and not force:
        raise FileExistsError(f"Skill already registered: {identifier}")
    skills[identifier] = dict(entry)

    serialised = {
        "skills": sorted(skills.values(), key=lambda item: item["id"]),
    }
    manifest_path.write_text(
        json.dumps(serialised, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def scaffold_skill(
    root: str | Path,
    metadata: SkillMetadata,
    *,
    force: bool = False,
) -> Path:
    """Materialise a new skill directory from templates."""

    root_path = Path(root).resolve()
    root_path.mkdir(parents=True, exist_ok=True)

    skill_id = _slugify(metadata.name)
    skill_dir = root_path / skill_id
    if skill_dir.exists() and not force:
        raise FileExistsError(f"Skill directory already exists: {skill_dir}")
    skill_dir.mkdir(parents=True, exist_ok=True)

    tags = _normalise_tags(metadata.tags, fallback=skill_id)
    created_at = datetime.now(timezone.utc).isoformat()
    module_name = skill_id.replace("-", "_")
    context = {
        "title": metadata.name,
        "description": metadata.description,
        "skill_id": skill_id,
        "created_at": created_at,
        "module_name": module_name,
        "tags_block": "\n".join(f"  - {tag}" for tag in tags),
    }

    for template_path in TEMPLATE_DIR.rglob("*"):
        if template_path.is_dir():
            continue
        relative = template_path.relative_to(TEMPLATE_DIR)
        if relative.suffix == ".jinja":
            relative = relative.with_suffix("")
        destination = skill_dir / relative
        rendered = _render_template(template_path, context)
        _write_file(destination, rendered, force=force)

    manifest_entry = {
        "id": skill_id,
        "name": metadata.name,
        "description": metadata.description,
        "tags": tags,
        "path": str(skill_dir.relative_to(root_path)),
        "created_at": created_at,
        "module": module_name,
    }
    _update_manifest(root_path / "skills.json", manifest_entry, force=force)
    return skill_dir
