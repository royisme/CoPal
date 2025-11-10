from __future__ import annotations

import argparse
from pathlib import Path

from copal_cli.memory.cli_commands import (
    memory_add_command,
    memory_delete_command,
    memory_list_command,
    memory_search_command,
    memory_show_command,
    memory_summary_command,
    memory_supersede_command,
    memory_update_command,
)


def make_namespace(**kwargs) -> argparse.Namespace:
    return argparse.Namespace(**kwargs)


def test_memory_cli_workflow(tmp_path: Path, capsys):
    target = tmp_path
    memory_id = "cli-mem-1"

    add_args = make_namespace(
        target=str(target),
        type="note",
        content="Investigate caching strategies",
        scope=None,
        importance=0.7,
        metadata=["stage=analysis"],
        id=memory_id,
    )
    assert memory_add_command(add_args) == 0

    show_args = make_namespace(target=str(target), memory_id=memory_id, scope=None)
    assert memory_show_command(show_args) == 0
    output = capsys.readouterr().out
    assert "Investigate caching strategies" in output

    update_args = make_namespace(
        target=str(target),
        memory_id=memory_id,
        scope=None,
        content="Investigate caching strategies (redis preferred)",
        importance=None,
        metadata=["confidence=0.8"],
        type=None,
    )
    assert memory_update_command(update_args) == 0

    search_args = make_namespace(
        target=str(target),
        query="redis",
        scope=None,
        types=None,
    )
    assert memory_search_command(search_args) == 0
    search_output = capsys.readouterr().out
    assert "redis" in search_output.lower()

    list_args = make_namespace(target=str(target), scope=None, types=None)
    assert memory_list_command(list_args) == 0
    list_output = capsys.readouterr().out
    assert memory_id in list_output

    supersede_args = make_namespace(
        target=str(target),
        old_memory_id=memory_id,
        type="decision",
        content="Standardise on Redis cache",
        scope=None,
        importance=0.9,
        reason="architecture decision",
        metadata=None,
    )
    assert memory_supersede_command(supersede_args) == 0
    supersede_output = capsys.readouterr().out
    assert "superseding" in supersede_output

    summary_args = make_namespace(target=str(target), scope=None)
    assert memory_summary_command(summary_args) == 0
    summary_output = capsys.readouterr().out
    assert "Total memories" in summary_output

    delete_args = make_namespace(target=str(target), memory_id=memory_id, scope=None)
    assert memory_delete_command(delete_args) == 0
