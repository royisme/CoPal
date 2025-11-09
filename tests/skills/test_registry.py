from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest

from copal_cli.skills.registry import Registry, RegistryError


def write_skill(path: Path, metadata: str, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{metadata}\n---\n{body}", encoding="utf-8")


def test_build_registry_creates_outputs(tmp_path: Path) -> None:
    user_root = tmp_path / "user"
    project_root = tmp_path / "project"
    user_root.mkdir()
    project_root.mkdir()

    write_skill(
        user_root / "alpha" / "SKILL.md",
        """id: greet\nname: Greeter\ndescription: Offers friendly greetings.\ntags:\n  - communication\n  - welcome""",
        "# Greeter\nSays hello.",
    )
    write_skill(
        project_root / "beta" / "SKILL.md",
        """id: calc\nname: Calculator\ndescription: Performs basic calculations.\ntags:\n  - math\n  - utility""",
        "# Calculator\nAdds numbers.",
    )

    registry = Registry.build({"user": user_root, "project": project_root}, tmp_path / "out")

    assert len(registry.skills) == 2

    skills_json = json.loads((tmp_path / "out" / "skills.json").read_text(encoding="utf-8"))
    assert {entry["id"] for entry in skills_json} == {"greet", "calc"}

    prelude = (tmp_path / "out" / "prelude.md").read_text(encoding="utf-8")
    assert "Greeter" in prelude and "Calculator" in prelude
    assert len(prelude) <= 1500


def test_malformed_metadata_raises(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    write_skill(
        root / "broken" / "SKILL.md",
        """id: broken\ndescription: Missing the name field.\ntags:\n  - error""",
    )

    with pytest.raises(RegistryError):
        Registry.build({"project": root}, tmp_path / "out")


def test_duplicate_skill_id_raises(tmp_path: Path) -> None:
    user_root = tmp_path / "user"
    project_root = tmp_path / "project"

    write_skill(
        user_root / "first" / "SKILL.md",
        """id: shared\nname: Primary\ndescription: First definition.\ntags:\n  - duplicate""",
    )
    write_skill(
        project_root / "second" / "SKILL.md",
        """id: shared\nname: Secondary\ndescription: Second definition.\ntags:\n  - duplicate""",
    )

    with pytest.raises(RegistryError):
        Registry.build({"user": user_root, "project": project_root}, tmp_path / "out")


def test_prelude_truncation(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    long_description = "Lorem ipsum " * 200
    write_skill(
        root / "verbose" / "SKILL.md",
        f"""id: verbose\nname: Verbose Skill\ndescription: {long_description}\ntags:\n  - long\n  - text""",
    )

    Registry.build({"project": root}, tmp_path / "out", prelude_max_chars=120)
    prelude = (tmp_path / "out" / "prelude.md").read_text(encoding="utf-8")
    assert len(prelude) <= 120
    assert prelude.endswith("…\n")
