"""Argparse handlers for the `copal memory` command group."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from collections.abc import Iterable
from uuid import uuid4

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .config import (
    is_memory_enabled,
    load_memory_config,
    resolve_database_path,
)
from .models import Memory, MemoryType
from .json_store import JsonMemoryStore
from .sqlite_store import SQLiteMemoryStore
from .scope import ScopeManager
from .store_interface import IMemoryStore

console = Console()


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
        console.print("[yellow]Memory subsystem is disabled in configuration.[/yellow]")
        return None

    scope_manager = ScopeManager.from_config(target_root, config)
    backend = str(config.get("backend", "sqlite")).lower()

    if backend == "sqlite":
        db_path = resolve_database_path(target_root, config)
        store = SQLiteMemoryStore(
            target_root=target_root,
            db_path=db_path,
            config=config,
            scope_manager=scope_manager,
        )
    else:
        # Fallback to json for compatibility
        store = JsonMemoryStore(
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
    try:
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
        console.print(f"[green]✓ Created memory[/green] [cyan]{memory.id}[/cyan] in scope '[cyan]{memory.scope}[/cyan]'")
        return 0
    finally:
        context.store.close()


def memory_search_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    try:
        scope = context.resolve_scope(getattr(args, "scope", None))
        type_args = getattr(args, "types", None)
        types = [MemoryType(t) for t in type_args] if type_args else None
        results = context.store.search_memories(getattr(args, "query"), scope=scope, types=types)
        if not results:
            console.print("[dim]No memories matched the query.[/dim]")
            return 0
        
        table = Table(title=f"Search Results ({len(results)} memories in scope '{scope}')")
        table.add_column("Type", style="magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Content")
        
        for memory in results:
            table.add_row(memory.type.value, memory.id, memory.content[:60] + "..." if len(memory.content) > 60 else memory.content)
        
        console.print(table)
        return 0
    finally:
        context.store.close()


def memory_show_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    try:
        scope = context.resolve_scope(getattr(args, "scope", None))
        memory = context.store.get_memory(getattr(args, "memory_id"), scope=scope)
        if memory is None:
            console.print("[yellow]Memory not found in the requested scope.[/yellow]")
            return 1
        
        console.print(Panel.fit(
            f"[bold]ID:[/bold] {memory.id}\n"
            f"[bold]Type:[/bold] {memory.type.value}\n"
            f"[bold]Scope:[/bold] {memory.scope}\n"
            f"[bold]Content:[/bold] {memory.content}\n"
            f"[bold]Importance:[/bold] {memory.importance}\n"
            f"[bold]Created:[/bold] {memory.created_at.isoformat()}\n"
            f"[bold]Updated:[/bold] {memory.updated_at.isoformat()}",
            title="[bold blue]Memory Details[/bold blue]"
        ))
        
        if memory.metadata:
            console.print("\n[bold]Metadata:[/bold]")
            for key, value in memory.metadata.items():
                console.print(f"  • [cyan]{key}[/cyan]: {value}")
        
        relationships = context.store.list_relationships(memory.id, scope=scope)
        if relationships:
            console.print("\n[bold]Relationships:[/bold]")
            for rel in relationships:
                console.print(f"  • [dim]({rel.type.value})[/dim] {rel.source_id} → {rel.target_id}")
        return 0
    finally:
        context.store.close()


def memory_update_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    try:
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
            console.print("[yellow]No updates provided.[/yellow]")
            return 1
        memory = context.store.update_memory(args.memory_id, scope=scope, **updates)
        if memory is None:
            console.print("[yellow]Memory not found.[/yellow]")
            return 1
        console.print(f"[green]✓ Updated memory[/green] [cyan]{memory.id}[/cyan]")
        return 0
    finally:
        context.store.close()


def memory_delete_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    try:
        scope = context.resolve_scope(getattr(args, "scope", None))
        deleted = context.store.delete_memory(args.memory_id, scope=scope)
        if not deleted:
            console.print("[yellow]Memory not found.[/yellow]")
            return 1
        console.print(f"[green]✓ Deleted memory[/green] [cyan]{args.memory_id}[/cyan]")
        return 0
    finally:
        context.store.close()


def memory_list_command(args: argparse.Namespace) -> int:
    context = _build_context(args)
    if context is None:
        return 1
    try:
        scope = context.resolve_scope(getattr(args, "scope", None))
        type_args = getattr(args, "types", None)
        types = [MemoryType(t) for t in type_args] if type_args else None
        memories = context.store.list_memories(scope=scope, types=types)
        if not memories:
            console.print(f"[dim]No memories stored for scope '{scope}'.[/dim]")
            return 0
        
        table = Table(title=f"Memories in scope '{scope}'")
        table.add_column("Type", style="magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Content")
        
        for memory in memories:
            table.add_row(memory.type.value, memory.id, memory.content[:60] + "..." if len(memory.content) > 60 else memory.content)
        
        console.print(table)
        return 0
    finally:
        context.store.close()
