"""Skill command executor for CoPal."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Iterable, Sequence

from .sandbox import LocalSandbox, SandboxExecutionError


@dataclass(slots=True)
class ExecutionResult:
    """Represents the outcome of an execution."""

    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    metadata: dict[str, object]


class SkillExecutor:
    """Parse and execute skill commands via an isolated sandbox."""

    BASH_PREFIX = "bash:"
    DEFAULT_ALLOWED_ACTIONS = {"read", "python", "sh", "node"}
    SENSITIVE_KEY_HINTS = ("TOKEN", "KEY", "SECRET", "PASSWORD")
    REDACTION_TOKEN = "[REDACTED]"

    def __init__(
        self,
        sandbox: LocalSandbox | None = None,
        allowed_actions: Iterable[str] | None = None,
        sensitive_env_keys: Sequence[str] | None = None,
    ) -> None:
        self._sandbox = sandbox or LocalSandbox()
        self._allowed_actions = set(allowed_actions or self.DEFAULT_ALLOWED_ACTIONS)
        self._sensitive_tokens = self._collect_sensitive_tokens(sensitive_env_keys)

    def execute(self, command: str, *, timeout: float | None = None) -> ExecutionResult:
        """Parse a bash-prefixed command and execute it inside the sandbox."""

        action, payload = self._parse_command(command)
        self._validate_action(action)

        try:
            sandbox_result = self._sandbox.run(action, payload, timeout=timeout)
        except SandboxExecutionError as exc:
            raise ValueError(str(exc)) from exc

        return ExecutionResult(
            stdout=self._redact(sandbox_result.stdout),
            stderr=self._redact(sandbox_result.stderr),
            exit_code=sandbox_result.exit_code,
            timed_out=sandbox_result.timed_out,
            metadata=dict(sandbox_result.metadata or {}),
        )

    def _parse_command(self, command: str) -> tuple[str, str]:
        if not command.startswith(self.BASH_PREFIX):
            raise ValueError("Command must start with 'bash:' prefix")

        payload = command[len(self.BASH_PREFIX) :].strip()
        if not payload:
            raise ValueError("Empty bash command")

        parts = payload.split(None, 1)
        action = parts[0]
        remainder = parts[1] if len(parts) > 1 else ""
        return action, remainder

    def _validate_action(self, action: str) -> None:
        if action not in self._allowed_actions:
            raise ValueError(f"Action '{action}' is not allowed")

    def _collect_sensitive_tokens(self, sensitive_env_keys: Sequence[str] | None) -> list[str]:
        keys: Sequence[str]
        if sensitive_env_keys is not None:
            keys = sensitive_env_keys
        else:
            keys = [
                key
                for key in os.environ
                if any(hint in key.upper() for hint in self.SENSITIVE_KEY_HINTS)
            ]
        tokens: list[str] = []
        for key in keys:
            value = os.environ.get(key)
            if value:
                tokens.append(value)
        return tokens

    def _redact(self, value: str) -> str:
        if not value:
            return value

        redacted = value
        for token in self._sensitive_tokens:
            if token:
                escaped = re.escape(token)
                redacted = re.sub(escaped, self.REDACTION_TOKEN, redacted)

        # Generic API key style redaction
        redacted = re.sub(r"sk-[A-Za-z0-9_-]{8,}", self.REDACTION_TOKEN, redacted)
        return redacted


__all__ = ["SkillExecutor", "ExecutionResult"]
