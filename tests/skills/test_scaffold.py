"""Tests for the skill scaffolding helpers."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:  # pragma: no cover - environmental guard
    sys.path.insert(0, str(PROJECT_ROOT))

from copal_cli.skills import Registry, SkillMetadata, scaffold_skill


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_scaffold_creates_expected_layout(tmp_path: Path) -> None:
    metadata = SkillMetadata(
        name="Conversational Search",
        description="Assistants can answer questions using retrieval.",
        tags=("retrieval", "Claude"),
    )

    skill_dir = scaffold_skill(tmp_path, metadata)

    expected_files = [
        skill_dir / "SKILL.md",
        skill_dir / "CHANGELOG.md",
        skill_dir / "scripts" / "run.py",
        skill_dir / "examples" / "request.md",
        skill_dir / "tests" / "test_smoke.py",
    ]
    for file in expected_files:
        assert file.exists(), f"missing expected artifact: {file}"

    skill_doc = read(skill_dir / "SKILL.md")
    assert 'title: "Conversational Search"' in skill_doc
    assert 'description: "Assistants can answer questions using retrieval."' in skill_doc
    assert "retrieval" in skill_doc
    assert "claude" in skill_doc  # tags are normalised to lowercase

    manifest = json.loads(read(tmp_path / "skills.json"))
    assert manifest["skills"][0]["id"] == "conversational-search"
    assert manifest["skills"][0]["tags"] == ["retrieval", "claude"]


def test_scaffold_requires_force_for_existing(tmp_path: Path) -> None:
    metadata = SkillMetadata(
        name="Planning Helper",
        description="initial",
        tags=("plan",),
    )
    scaffold_skill(tmp_path, metadata)

    with pytest.raises(FileExistsError):
        scaffold_skill(tmp_path, metadata)


def test_scaffold_force_overwrites_metadata(tmp_path: Path) -> None:
    original = SkillMetadata(
        name="Review Companion",
        description="initial",
        tags=("review",),
    )
    skill_dir = scaffold_skill(tmp_path, original)

    updated = SkillMetadata(
        name="Review Companion",
        description="updated",
        tags=("reviews", "qa"),
    )
    scaffold_skill(tmp_path, updated, force=True)

    content = read(skill_dir / "SKILL.md")
    assert "updated" in content
    manifest = json.loads(read(tmp_path / "skills.json"))
    entry = manifest["skills"][0]
    assert entry["tags"] == ["reviews", "qa"]


def test_registry_build_discovers_scaffolded_skill(tmp_path: Path) -> None:
    metadata = SkillMetadata(
        name="Summarisation Agent",
        description="Summarise transcripts into short notes.",
        tags=("summaries",),
    )
    scaffold_skill(tmp_path, metadata)

    registry = Registry.build(tmp_path)
    entry = registry.get("summarisation-agent")
    assert entry is not None
    assert entry.name == "Summarisation Agent"
    assert entry.description.startswith("Summarise transcripts")
    assert "summaries" in entry.tags
    assert entry.path.exists()
