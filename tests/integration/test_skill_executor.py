from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from copal_cli.skills import SkillExecutor
from copal_cli.skills.sandbox import LocalSandbox


def make_executor(tmp_path: Path, **sandbox_kwargs: object) -> SkillExecutor:
    sandbox = LocalSandbox(allowed_roots=[tmp_path], **sandbox_kwargs)
    return SkillExecutor(sandbox=sandbox, sensitive_env_keys=[])


def test_read_allows_allowed_paths(tmp_path: Path) -> None:
    file_path = tmp_path / "allowed.txt"
    file_path.write_text("hello skills\n", encoding="utf-8")

    executor = make_executor(tmp_path)
    result = executor.execute(f"bash:read {file_path}")

    assert "hello skills" in result.stdout
    assert result.stderr == ""
    assert result.exit_code == 0
    assert result.timed_out is False


def test_read_rejects_path_escape(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("forbidden", encoding="utf-8")

    executor = make_executor(allowed_root)
    with pytest.raises(ValueError):
        executor.execute(f"bash:read {outside_file}")


def test_python_execution_times_out(tmp_path: Path) -> None:
    executor = make_executor(tmp_path)
    command = "bash:python import time\ntime.sleep(10)"
    result = executor.execute(command)

    assert result.timed_out is True
    assert result.exit_code != 0


def test_memory_limit_enforced(tmp_path: Path) -> None:
    executor = make_executor(tmp_path)
    command = "bash:python bytearray(400 * 1024 * 1024)"
    result = executor.execute(command)

    assert result.exit_code != 0


def test_network_usage_blocked_by_default(tmp_path: Path) -> None:
    executor = make_executor(tmp_path)
    command = "bash:python import socket\nsocket.create_connection(('example.com', 80), timeout=1)"
    with pytest.raises(ValueError):
        executor.execute(command)


def test_sensitive_output_redacted(tmp_path: Path) -> None:
    sandbox = LocalSandbox(allowed_roots=[tmp_path])
    executor = SkillExecutor(sandbox=sandbox)
    command = "bash:python print('sk-test-1234567890')"
    result = executor.execute(command)

    assert "[REDACTED]" in result.stdout
    assert "sk-test" not in result.stdout
