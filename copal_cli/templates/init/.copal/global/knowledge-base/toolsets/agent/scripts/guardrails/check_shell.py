"""Guardrail script that enforces the use of `uv` for Python and pip commands.

The script flags commands that invoke bare `python` or `pip` and suggests
`uv run` or `uv pip` alternatives. Extend the matching logic or output format
as needed for your project."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


GLOBAL_DIR = Path(__file__).resolve().parents[4]
LOG_FILE = GLOBAL_DIR / "logs" / "guardrail-history.jsonl"


def append_log(payload: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def show_snapshot(limit: int) -> int:
    if not LOG_FILE.exists():
        print("[guardrail] No history yet.")
        return 0

    with LOG_FILE.open("r", encoding="utf-8") as fh:
        lines = fh.readlines()[-limit:]

    if not lines:
        print("[guardrail] Log is empty.")
        return 0

    print("Recent violations:")
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"- {line.strip()}")
            continue
        timestamp = record.get("timestamp")
        command = record.get("command")
        suggestion = record.get("suggestion")
        print(f"- {timestamp}: {command} -> Suggested {suggestion}")
    return 0


def check_command(command: str) -> int:
    normalized = command.strip()
    if not normalized:
        print("[guardrail] No command provided.", file=sys.stderr)
        return 2

    lower = normalized.lower()
    wrapped_with_uv = lower.startswith("uv run ") or lower.startswith("uv pip ")

    violations = []
    if "python" in lower and not wrapped_with_uv:
        violations.append(
            {
                "reason": "detected-python",
                "suggestion": f"uv run {normalized}",
            }
        )

    if lower.startswith("pip "):
        remainder = normalized.split(" ", 1)[1] if " " in normalized else ""
        violations.append(
            {
                "reason": "detected-pip",
                "suggestion": f"uv pip {remainder}".strip(),
            }
        )

    if not violations:
        print("[guardrail] ✅ Command accepted.")
        return 0

    for item in violations:
        suggestion = item["suggestion"]
        reason = item["reason"]
        print(f"[Violation] {reason}: {normalized}")
        print(f"[Suggestion] Use: {suggestion}")

        append_log(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": normalized,
                "reason": reason,
                "suggestion": suggestion,
            }
        )

    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="UV guardrail example")
    parser.add_argument("--command", help="Command string to validate", default="")
    parser.add_argument("--snapshot", action="store_true", help="Show recent violations")
    parser.add_argument("--limit", type=int, default=20, help="Maximum entries to display for snapshots")

    args = parser.parse_args(argv)

    if args.snapshot:
        return show_snapshot(args.limit)

    if not args.command:
        parser.print_help()
        return 2

    return check_command(args.command)


if __name__ == "__main__":
    sys.exit(main())
