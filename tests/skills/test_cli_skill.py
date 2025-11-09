"""Integration tests for the skill command group."""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from copal_cli.cli import main


def _create_skill(
    root: Path,
    *,
    name: str,
    description: str,
    language: str = "python",
    requires_sandbox: bool = False,
    prelude: str | None = None,
    logs: list[str] | None = None,
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "name": name,
        "description": description,
        "language": language,
        "entrypoint": "run.txt",
        "requires_sandbox": requires_sandbox,
    }
    (skill_dir / "skill.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (skill_dir / "prelude.md").write_text(
        prelude or f"# {name}\n\n{description}",
        encoding="utf-8",
    )
    log_lines = logs or [f"executing {name}"]
    (skill_dir / "run.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return skill_dir


def test_skill_cli_happy_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    skills_root = tmp_path / "skills"
    _create_skill(
        skills_root,
        name="hello-world",
        description="Prints a friendly greeting",
        prelude="# Prelude\nThis skill greets the world.",
        logs=["Hello from skill", "All done"],
    )

    exit_code = main(["skill", "registry", "build", "--skills-root", str(skills_root)])
    assert exit_code == 0
    capsys.readouterr()
    assert (skills_root / "registry.json").exists()

    exit_code = main(
        [
            "skill",
            "search",
            "--skills-root",
            str(skills_root),
            "--query",
            "hello",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "hello-world" in captured.out
    assert "Prelude" in captured.out

    exit_code = main(
        [
            "skill",
            "exec",
            "--skills-root",
            str(skills_root),
            "--skill",
            "hello-world",
        ]
    )
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Hello from skill" in captured.out
    assert "All done" in captured.out


def test_skill_exec_missing_skill(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    exit_code = main(["skill", "registry", "build", "--skills-root", str(skills_root)])
    assert exit_code == 0
    capsys.readouterr()

    caplog.clear()
    with caplog.at_level(logging.ERROR):
        exit_code = main(
            [
                "skill",
                "exec",
                "--skills-root",
                str(skills_root),
                "--skill",
                "does-not-exist",
            ]
        )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "does-not-exist" in caplog.text


def test_skill_exec_requires_sandbox(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    skills_root = tmp_path / "skills"
    _create_skill(
        skills_root,
        name="secure-task",
        description="Requires sandbox",
        requires_sandbox=True,
        logs=["Sensitive operation"],
    )

    exit_code = main(["skill", "registry", "build", "--skills-root", str(skills_root)])
    assert exit_code == 0
    capsys.readouterr()

    caplog.clear()
    with caplog.at_level(logging.ERROR):
        exit_code = main(
            [
                "skill",
                "exec",
                "--skills-root",
                str(skills_root),
                "--skill",
                "secure-task",
            ]
        )
    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "requires sandbox" in caplog.text

    exit_code = main(
        [
            "skill",
            "exec",
            "--skills-root",
            str(skills_root),
            "--skill",
            "secure-task",
            "--sandbox",
        ]
    )
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Sensitive operation" in captured.out
