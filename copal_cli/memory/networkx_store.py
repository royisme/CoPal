"""NetworkX-backed memory store with SQLite persistence."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from pathlib import Path
from typing import Any
from collections.abc import Iterable, Sequence
from uuid import uuid4

try:  # pragma: no cover - import guard
    import networkx as nx
except ModuleNotFoundError:  # pragma: no cover - executed when dependency missing
    class _NodeRegistry(dict):
        def __call__(self, data: bool = False):
            if data:
                yield from self.items()
            else:
                yield from self.keys()

    class _FallbackMultiDiGraph:
        def __init__(self) -> None:
            self.nodes: _NodeRegistry[str, dict[str, Any]] = _NodeRegistry()
            self._edges: dict[str, dict[str, tuple[str, dict[str, Any]]]] = {}

        def add_node(self, node_id: str, **attrs: Any) -> None:
            data = self.nodes.setdefault(node_id, {})
            data.update(attrs)

        def __contains__(self, node_id: str) -> bool:
            return node_id in self.nodes

        def add_edge(
            self,
            source: str,
            target: str,
            key: str | None = None,
            **attrs: Any,
        ) -> None:
            edge_key = key or str(uuid4())
            self.nodes.setdefault(source, {})
            self.nodes.setdefault(target, {})
            bucket = self._edges.setdefault(source, {})
            bucket[edge_key] = (target, attrs)

        def out_edges(self, node_id: str, keys: bool = False, data: bool = False):
            for key, (target, attrs) in self._edges.get(node_id, {}).items():
                if keys and data:
                    yield (node_id, target, key, attrs)
                elif keys:
                    yield (node_id, target, key)
                elif data:
                    yield (node_id, target, attrs)
                else:
                    yield (node_id, target)

        def remove_node(self, node_id: str) -> None:
            self.nodes.pop(node_id, None)
            self._edges.pop(node_id, None)
            for bucket in self._edges.values():
                for key in list(bucket):
                    if bucket[key][0] == node_id:
                        del bucket[key]

    nx = type("nx", (), {"MultiDiGraph": _FallbackMultiDiGraph})()

from .config import resolve_database_path
from .models import EdgeType, Memory, MemoryType, Relationship
from .query import MemoryQueryEngine
from .scope import ScopeManager
from .store_interface import IMemoryStore


class SQLiteMemoryPersistence:
    """Persist memories and relationships to a lightweight SQLite DB."""

    def __init__(self, db_path: Path):
        self._db_path = Path(db_path)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self._conn:  # type: ignore[call-arg]
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    scope TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )

    def iter_memories(self) -> Iterable[Memory]:
        cursor = self._conn.execute("SELECT payload FROM memories")
        for row in cursor:
            payload = json.loads(row["payload"])
            yield Memory.from_dict(payload)

    def iter_relationships(self) -> Iterable[Relationship]:
        cursor = self._conn.execute("SELECT payload FROM relationships")
        for row in cursor:
            payload = json.loads(row["payload"])
            yield Relationship.from_dict(payload)

    def save_memory(self, memory: Memory) -> None:
        payload = json.dumps(memory.to_dict())
        with self._conn:  # type: ignore[call-arg]
            self._conn.execute(
                """
                INSERT INTO memories (id, scope, payload)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    scope=excluded.scope,
                    payload=excluded.payload
                """,
                (memory.id, memory.scope, payload),
            )

    def delete_memory(self, memory_id: str) -> None:
        with self._conn:  # type: ignore[call-arg]
            self._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            self._conn.execute(
                "DELETE FROM relationships WHERE source_id = ? OR target_id = ?",
                (memory_id, memory_id),
            )

    def save_relationship(self, relationship: Relationship) -> None:
        payload = json.dumps(relationship.to_dict())
        with self._conn:  # type: ignore[call-arg]
            self._conn.execute(
                """
                INSERT INTO relationships (id, source_id, target_id, scope, payload)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_id=excluded.source_id,
                    target_id=excluded.target_id,
                    scope=excluded.scope,
                    payload=excluded.payload
                """,
                (
                    relationship.id,
                    relationship.source_id,
                    relationship.target_id,
                    relationship.scope,
                    payload,
                ),
            )

    def delete_relationship(self, relationship_id: str) -> None:
        with self._conn:  # type: ignore[call-arg]
            self._conn.execute(
                "DELETE FROM relationships WHERE id = ?", (relationship_id,)
            )

    def close(self) -> None:
        self._conn.close()


class NetworkXMemoryStore(IMemoryStore):
    """Concrete :class:`IMemoryStore` built on a NetworkX MultiDiGraph."""

    def __init__(
        self,
        target_root: Path,
        *,
        config: dict[str, Any],
        scope_manager: ScopeManager,
    ) -> None:
        db_path = resolve_database_path(target_root, config)
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._persistence = SQLiteMemoryPersistence(db_path)
        self._scope_manager = scope_manager
        self._query_engine = MemoryQueryEngine(self._graph)
        self._load_from_persistence()

    # ... (skipping unchanged parts)

    def list_relationships(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
    ) -> list[Relationship]:
        if memory_id not in self._graph:
            return []
        resolved_scope = scope or self._scope_manager.current_scope
        relationships: list[Relationship] = []
        for _, target, key, data in self._graph.out_edges(memory_id, keys=True, data=True):
            relationship: Relationship = data.get("relationship")
            if relationship is None:
                continue
            if resolved_scope and relationship.scope != resolved_scope:
                continue
            relationships.append(relationship)
        return relationships

    def close(self) -> None:
        self._persistence.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_from_persistence(self) -> None:
        for memory in self._persistence.iter_memories():
            self._graph.add_node(memory.id, memory=memory)
        for relationship in self._persistence.iter_relationships():
            self._graph.add_edge(
                relationship.source_id,
                relationship.target_id,
                key=relationship.id,
                relationship=relationship,
            )

    def _ensure_memory_scope(self, memory: Memory) -> Memory:
        scope = memory.scope or self._scope_manager.current_scope
        if memory.scope != scope:
            memory = replace(memory, scope=scope)
        return memory

    def _normalise_types(
        self, types: Iterable[MemoryType] | None
    ) -> list[MemoryType] | None:
        if types is None:
            return None
        normalised: list[MemoryType] = []
        for item in types:
            if isinstance(item, MemoryType):
                normalised.append(item)
            else:
                normalised.append(MemoryType(str(item)))
        return normalised

    def _record_relationship(self, relationship: Relationship) -> None:
        self._graph.add_edge(
            relationship.source_id,
            relationship.target_id,
            key=relationship.id,
            relationship=relationship,
        )
        self._persistence.save_relationship(relationship)

    # ------------------------------------------------------------------
    # IMemoryStore implementation
    # ------------------------------------------------------------------
    def add_memory(
        self,
        memory: Memory,
        relationships: Sequence[Relationship] | None = None,
    ) -> Memory:
        memory = self._ensure_memory_scope(memory)
        self._graph.add_node(memory.id, memory=memory)
        self._persistence.save_memory(memory)
        for relationship in relationships or ():
            self._record_relationship(relationship)
        return memory

    def get_memory(self, memory_id: str, scope: str | None = None) -> Memory | None:
        if memory_id not in self._graph:
            return None
        data = self._graph.nodes[memory_id]
        memory: Memory | None = data.get("memory")
        if memory is None:
            return None
        resolved_scope = scope or memory.scope
        if resolved_scope != memory.scope:
            return None
        return memory

    def update_memory(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
        **updates: Any,
    ) -> Memory | None:
        memory = self.get_memory(memory_id, scope=scope)
        if memory is None:
            return None

        for key, value in updates.items():
            if value is None:
                continue
            if key == "type":
                if isinstance(value, MemoryType):
                    memory.type = value
                else:
                    memory.type = MemoryType(str(value))
            elif key == "metadata" and isinstance(value, dict):
                memory.metadata.update(value)
            elif hasattr(memory, key):
                setattr(memory, key, value)
        memory.touch()
        self._persistence.save_memory(memory)
        return memory

    def delete_memory(self, memory_id: str, scope: str | None = None) -> bool:
        memory = self.get_memory(memory_id, scope=scope)
        if memory is None:
            return False
        if memory_id in self._graph:
            self._graph.remove_node(memory_id)
        self._persistence.delete_memory(memory_id)
        return True

    def supersede_memory(
        self,
        old_memory_id: str,
        new_memory: Memory,
        relationship_metadata: dict[str, Any] | None = None,
    ) -> Memory:
        old_memory = self.get_memory(old_memory_id)
        if old_memory is None:
            raise KeyError(f"Memory '{old_memory_id}' does not exist")
        scoped_memory = self._ensure_memory_scope(new_memory)
        scoped_memory.valid_from = scoped_memory.valid_from or old_memory.updated_at
        old_memory.valid_until = scoped_memory.created_at
        self._persistence.save_memory(old_memory)
        self._graph.nodes[old_memory.id]["memory"] = old_memory

        relationship = Relationship(
            id=str(uuid4()),
            source_id=scoped_memory.id,
            target_id=old_memory.id,
            type=EdgeType.SUPERSEDES,
            scope=scoped_memory.scope,
            metadata=relationship_metadata or {},
        )
        self.add_memory(scoped_memory, [relationship])
        return scoped_memory

    def search_memories(
        self,
        query: str,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        resolved_scope = scope or self._scope_manager.current_scope
        normalised = self._normalise_types(types)
        return self._query_engine.search(
            query,
            scope=resolved_scope,
            types=normalised,
        )

    def list_memories(
        self,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        resolved_scope = scope or self._scope_manager.current_scope
        normalised = self._normalise_types(types)
        return self._query_engine.list(scope=resolved_scope, types=normalised)

    def summarise_project(self, scope: str | None = None) -> dict[str, Any]:
        resolved_scope = scope or self._scope_manager.current_scope
        memories = self.list_memories(scope=resolved_scope)
        counts: dict[str, int] = {}
        for mem in memories:
            counts[mem.type.value] = counts.get(mem.type.value, 0) + 1
        top_memories = sorted(
            memories,
            key=lambda m: (m.importance, m.updated_at),
            reverse=True,
        )[:5]
        return {
            "scope": resolved_scope,
            "total_memories": len(memories),
            "by_type": counts,
            "top_memories": [m.to_dict() for m in top_memories],
        }

    def list_relationships(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
    ) -> list[Relationship]:
        if memory_id not in self._graph:
            return []
        resolved_scope = scope or self._scope_manager.current_scope
        relationships: list[Relationship] = []
        for _, target, key, data in self._graph.out_edges(memory_id, keys=True, data=True):
            relationship: Relationship = data.get("relationship")
            if relationship is None:
                continue
            if resolved_scope and relationship.scope != resolved_scope:
                continue
            relationships.append(relationship)
        return relationships
