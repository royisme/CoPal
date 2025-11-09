"""Local sandbox implementation for executing skill actions."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

try:  # pragma: no cover - optional on non-Unix systems
    import resource
except ImportError:  # pragma: no cover
    resource = None  # type: ignore


class SandboxExecutionError(RuntimeError):
    """Raised when the sandbox rejects a request before execution."""


@dataclass(slots=True)
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    metadata: dict[str, object] = field(default_factory=dict)


class LocalSandbox:
    """Execute commands in a constrained environment."""

    DEFAULT_TIMEOUT = 5.0
    DEFAULT_CPU_LIMIT = 2  # seconds
    DEFAULT_MEMORY_LIMIT_MB = 256
    NETWORK_DENY_PATTERNS = (
        "curl",
        "wget",
        "import socket",
        "socket.create_connection",
        "requests.",
        "httpx.",
        "urllib.request",
    )

    def __init__(
        self,
        *,
        allowed_roots: Iterable[str | os.PathLike[str]] | None = None,
        network_allowed: bool = False,
        default_timeout: float | None = None,
        cpu_time_limit: int | None = None,
        memory_limit_mb: int | None = None,
    ) -> None:
        cwd = Path.cwd()
        skills_root = cwd / "copal_cli" / "skills"
        roots = [cwd]
        if skills_root.exists():
            roots.append(skills_root)

        if allowed_roots:
            roots.extend(Path(path) for path in allowed_roots)

        self._allowed_roots = [root.resolve() for root in roots]
        self._network_allowed = network_allowed
        self._default_timeout = default_timeout if default_timeout is not None else self.DEFAULT_TIMEOUT
        self._cpu_time_limit = cpu_time_limit if cpu_time_limit is not None else self.DEFAULT_CPU_LIMIT
        self._memory_limit_bytes = (
            memory_limit_mb * 1024 * 1024 if memory_limit_mb is not None else self.DEFAULT_MEMORY_LIMIT_MB * 1024 * 1024
        )
        self._log_dir = Path(os.path.expanduser("~/.codex-skills/logs"))
        self._log_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def run(self, action: str, payload: str, *, timeout: float | None = None) -> SandboxResult:
        if action == "read":
            result = self._read_file(payload)
        else:
            result = self._execute_process(action, payload, timeout)

        self._write_audit_log(action, payload, result)
        return result

    # ------------------------------------------------------------------
    def _read_file(self, payload: str) -> SandboxResult:
        if not payload.strip():
            raise SandboxExecutionError("read action requires a path argument")

        parts = shlex.split(payload)
        if not parts:
            raise SandboxExecutionError("Invalid read payload")

        path = Path(parts[0]).expanduser()
        resolved = path.resolve()
        self._ensure_allowed_path(resolved)

        try:
            content = resolved.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = resolved.read_bytes().decode("utf-8", errors="replace")

        metadata = {"path": str(resolved)}
        return SandboxResult(stdout=content, stderr="", exit_code=0, timed_out=False, metadata=metadata)

    # ------------------------------------------------------------------
    def _execute_process(self, action: str, payload: str, timeout: float | None) -> SandboxResult:
        if not self._network_allowed and any(token in payload for token in self.NETWORK_DENY_PATTERNS):
            raise SandboxExecutionError("Network access is disabled in the sandbox")

        command = self._build_command(action, payload)
        env = self._build_environment()

        preexec_fn: Callable[[], None] | None = None
        if resource is not None:
            def limiter() -> None:
                resource.setrlimit(resource.RLIMIT_CPU, (self._cpu_time_limit, self._cpu_time_limit))
                resource.setrlimit(resource.RLIMIT_AS, (self._memory_limit_bytes, self._memory_limit_bytes))
            preexec_fn = limiter

        proc = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            preexec_fn=preexec_fn,
        )

        deadline = timeout if timeout is not None else self._default_timeout
        timed_out = False

        try:
            stdout, stderr = proc.communicate(timeout=deadline)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            stdout, stderr = proc.communicate()

        return SandboxResult(
            stdout=stdout,
            stderr=stderr,
            exit_code=proc.returncode,
            timed_out=timed_out,
            metadata={"command": command},
        )

    # ------------------------------------------------------------------
    def _build_command(self, action: str, payload: str) -> list[str]:
        if action == "python":
            return [sys.executable, "-c", payload]
        if action == "sh":
            return ["/bin/sh", "-lc", payload]
        if action == "node":
            return ["node", "-e", payload]

        raise SandboxExecutionError(f"Unsupported action '{action}'")

    def _build_environment(self) -> dict[str, str]:
        env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": os.environ.get("HOME", str(Path.home())),
            "PYTHONWARNINGS": "ignore",
        }
        if not self._network_allowed:
            env.update({
                "NO_NETWORK": "1",
                "HTTP_PROXY": "",
                "HTTPS_PROXY": "",
                "ALL_PROXY": "",
            })
        return env

    def _ensure_allowed_path(self, resolved: Path) -> None:
        for root in self._allowed_roots:
            try:
                resolved.relative_to(root)
                return
            except ValueError:
                continue
        raise SandboxExecutionError(f"Access to path '{resolved}' is not permitted")

    # ------------------------------------------------------------------
    def _write_audit_log(self, action: str, payload: str, result: SandboxResult) -> None:
        timestamp = datetime.now(tz=timezone.utc)
        entry = {
            "id": uuid.uuid4().hex,
            "timestamp": timestamp.isoformat(),
            "action": action,
            "payload": payload,
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "metadata": result.metadata,
        }
        log_path = self._log_dir / f"{timestamp.strftime('%Y%m%dT%H%M%S%f')}-{entry['id']}.json"
        with log_path.open("w", encoding="utf-8") as handle:
            json.dump(entry, handle, ensure_ascii=False, indent=2)


__all__ = ["LocalSandbox", "SandboxResult", "SandboxExecutionError"]
