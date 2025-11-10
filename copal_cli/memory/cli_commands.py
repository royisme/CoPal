"""Argparse handlers for the `copal memory` command group."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from collections.abc import Iterable
from uuid import uuid4

from .config import (
    is_memory_enabled,
    load_memory_config,
)
from .models import Memory, MemoryType
from .networkx_store import NetworkXMemoryStore
from .scope import ScopeManager
from .store_interface import IMemoryStore


@dataclass
class MemoryCLIContext:
    """Runtime context shared across CLI handlers."""

    target_root: Path
    config: dict[str, object]
    scope_manager: ScopeManager
    store: IMemoryStore

    def resolve_scope(self, override: str | None) -> str:
        return self.scope_manager.resolve(override)


def _ensure_target_root(target: str) -> Path:
    root = Path(target).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / ".copal").mkdir(exist_ok=True)
    return root


def _build_context(args: argparse.Namespace) -> MemoryCLIContext | None:
    target_root = _ensure_target_root(getattr(args, "target", "."))
    config = load_memory_config(target_root)
    if not is_memory_enabled(config):
        print("Memory subsystem is disabled in configuration.")
        return None
    backend = str(config.get("backend", "networkx"))
    scope_manager = ScopeManager.from_config(target_root, config)
    if backend != "networkx":
        raise ValueError(
            "Only the 'networkx' memory backend is available in this build."
        )
    store = NetworkXMemoryStore(
        target_root,
        config=config,
        scope_manager=scope_manager,
    )
    return MemoryCLIContext(
        target_root=target_root,
        config=config,
        scope_manager=scope_manager,
        store=store,
    )


def _parse_metadata(pairs: Iterable[str] | None) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if not pairs:
        return metadata
    for pair in pairs:
        if "=" not in pair:
            continue
        key, value = pair.split("=", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def memory_add_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    metadata = _parse_metadata(getattr(args, "metadata", None))
    memory_type = MemoryType(getattr(args, "type"))
    memory_id = getattr(args, "id", None) or str(uuid4())
    memory = Memory(
        id=memory_id,
        type=memory_type,
        content=getattr(args, "content"),
        scope=scope,
        metadata=metadata,
        importance=float(getattr(args, "importance", 0.5)),
    )
    context.store.add_memory(memory)
    print(f"Created memory {memory.id} in scope '{memory.scope}'.")
    return 0


def memory_search_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    type_args = getattr(args, "types", None)
    types = [MemoryType(t) for t in type_args] if type_args else None
    results = context.store.search_memories(getattr(args, "query"), scope=scope, types=types)
    if not results:
        print("No memories matched the query.")
        return 0
    print(f"Found {len(results)} memories in scope '{scope}':")
    for memory in results:
        print(f"- [{memory.type.value}] {memory.id}: {memory.content}")
    return 0


def memory_show_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    memory = context.store.get_memory(getattr(args, "memory_id"), scope=scope)
    if memory is None:
        print("Memory not found in the requested scope.")
        return 1
    print(f"ID: {memory.id}")
    print(f"Type: {memory.type.value}")
    print(f"Scope: {memory.scope}")
    print(f"Content: {memory.content}")
    print(f"Importance: {memory.importance}")
    print(f"Created: {memory.created_at.isoformat()}Z")
    print(f"Updated: {memory.updated_at.isoformat()}Z")
    if memory.metadata:
        print("Metadata:")
        for key, value in memory.metadata.items():
            print(f"  - {key}: {value}")
    relationships = context.store.list_relationships(memory.id, scope=scope)
    if relationships:
        print("Relationships:")
        for rel in relationships:
            print(
                f"  - ({rel.type.value}) {rel.source_id} -> {rel.target_id}"
            )
    return 0


def memory_update_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    updates: dict[str, object] = {}
    if getattr(args, "content", None):
        updates["content"] = args.content
    if getattr(args, "importance", None) is not None:
        updates["importance"] = float(args.importance)
    metadata = _parse_metadata(getattr(args, "metadata", None))
    if metadata:
        updates["metadata"] = metadata
    if getattr(args, "type", None):
        updates["type"] = MemoryType(args.type)
    if not updates:
        print("No updates provided.")
        return 1
    memory = context.store.update_memory(args.memory_id, scope=scope, **updates)
    if memory is None:
        print("Memory not found.")
        return 1
    print(f"Updated memory {memory.id}.")
    return 0


def memory_delete_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    deleted = context.store.delete_memory(args.memory_id, scope=scope)
    if not deleted:
        print("Memory not found.")
        return 1
    print(f"Deleted memory {args.memory_id}.")
    return 0


def memory_supersede_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    metadata = _parse_metadata(getattr(args, "metadata", None))
    new_memory = Memory(
        id=str(uuid4()),
        type=MemoryType(getattr(args, "type")),
        content=getattr(args, "content"),
        scope=scope,
        metadata=metadata,
        importance=float(getattr(args, "importance", 0.5)),
    )
    superseded = context.store.supersede_memory(
        getattr(args, "old_memory_id"),
        new_memory,
        relationship_metadata={"reason": getattr(args, "reason", "superseded")},
    )
    print(
        "Created memory {new_id} superseding {old_id}.".format(
            new_id=superseded.id,
            old_id=args.old_memory_id,
        )
    )
    return 0


def memory_summary_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    summary = context.store.summarise_project(scope=scope)
    print(f"Scope: {summary['scope']}")
    print(f"Total memories: {summary['total_memories']}")
    if summary["by_type"]:
        print("Counts by type:")
        for key, value in summary["by_type"].items():
            print(f"  - {key}: {value}")
    if summary["top_memories"]:
        print("Top memories by importance:")
        for entry in summary["top_memories"]:
            print(f"  - [{entry['type']}] {entry['id']}: {entry['content']}")
    return 0


def memory_list_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    scope = context.resolve_scope(getattr(args, "scope", None))
    type_args = getattr(args, "types", None)
    types = [MemoryType(t) for t in type_args] if type_args else None
    memories = context.store.list_memories(scope=scope, types=types)
    if not memories:
        print("No memories stored for this scope.")
        return 0
    print(f"Memories in scope '{scope}':")
    for memory in memories:
        print(f"- [{memory.type.value}] {memory.id}: {memory.content}")
    return 0
