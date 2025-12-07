from __future__ import annotations

import contextlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Sequence

from .models import Memory, MemoryType, Relationship, EdgeType, _serialize_datetime, _deserialize_datetime, _now
from .store_interface import IMemoryStore
from .scope import ScopeManager


class SQLiteMemoryStore(IMemoryStore):
    """SQLite-backed memory store with basic conflict-safe writes."""

    def __init__(
        self,
        *,
        target_root: Path,
        db_path: Path,
        config: dict[str, Any],
        scope_manager: ScopeManager,
    ):
        self.target_root = target_root
        self.db_path = db_path
        self.config = config
        self.scope_manager = scope_manager
        self._ensure_db()

    # --- setup -----------------------------------------------------------------
    @contextlib.contextmanager
    def _get_connection(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    valid_from TEXT,
                    valid_until TEXT,
                    importance REAL,
                    access_count INTEGER,
                    last_accessed TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    weight REAL,
                    confidence REAL,
                    metadata TEXT,
                    created_at TEXT,
                    created_by TEXT,
                    UNIQUE(source_id, target_id, type, scope)
                )
                """
            )
            conn.commit()

    # --- helpers --------------------------------------------------------------
    @staticmethod
    def _row_to_memory(row: sqlite3.Row) -> Memory:
        return Memory(
            id=row["id"],
            type=MemoryType(row["type"]),
            content=row["content"],
            scope=row["scope"],
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=_deserialize_datetime(row["created_at"]),
            updated_at=_deserialize_datetime(row["updated_at"]),
            valid_from=_deserialize_datetime(row["valid_from"]),
            valid_until=_deserialize_datetime(row["valid_until"]),
            importance=float(row["importance"]),
            access_count=int(row["access_count"] or 0),
            last_accessed=_deserialize_datetime(row["last_accessed"]),
        )

    @staticmethod
    def _row_to_relationship(row: sqlite3.Row) -> Relationship:
        return Relationship(
            id=row["id"],
            source_id=row["source_id"],
            target_id=row["target_id"],
            type=EdgeType(row["type"]),
            scope=row["scope"],
            weight=float(row["weight"] or 1.0),
            confidence=float(row["confidence"] or 1.0),
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=_deserialize_datetime(row["created_at"]),
            created_by=row["created_by"],
        )

    # --- core API -------------------------------------------------------------
    def add_memory(
        self,
        memory: Memory,
        relationships: Sequence[Relationship] | None = None,
    ) -> Memory:
        # touch timestamps
        memory.touch()
        payload = memory.to_dict()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO memories
                (id, type, content, scope, metadata, created_at, updated_at,
                 valid_from, valid_until, importance, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["id"],
                    payload["type"],
                    payload["content"],
                    payload["scope"],
                    json.dumps(payload.get("metadata") or {}),
                    payload["created_at"],
                    payload["updated_at"],
                    payload["valid_from"],
                    payload["valid_until"],
                    payload["importance"],
                    payload["access_count"],
                    payload["last_accessed"],
                ),
            )
            if relationships:
                for rel in relationships:
                    rel_dict = rel.to_dict()
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO relationships
                        (id, source_id, target_id, type, scope, weight, confidence, metadata, created_at, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            rel_dict["id"],
                            rel_dict["source_id"],
                            rel_dict["target_id"],
                            rel_dict["type"],
                            rel_dict["scope"],
                            rel_dict["weight"],
                            rel_dict["confidence"],
                            json.dumps(rel_dict.get("metadata") or {}),
                            rel_dict["created_at"],
                            rel_dict["created_by"],
                        ),
                    )
            conn.commit()
        return memory

    def get_memory(self, memory_id: str, scope: str | None = None) -> Memory | None:
        query = "SELECT * FROM memories WHERE id = ?"
        params: list[Any] = [memory_id]
        if scope:
            query += " AND scope = ?"
            params.append(scope)
        with self._get_connection() as conn:
            row = conn.execute(query, params).fetchone()
            if not row:
                return None
            mem = self._row_to_memory(row)
            # Update access stats
            mem.touch()
            conn.execute(
                "UPDATE memories SET access_count = ?, last_accessed = ?, updated_at = ? WHERE id = ?",
                (mem.access_count, _serialize_datetime(mem.last_accessed), _serialize_datetime(mem.updated_at), mem.id),
            )
            conn.commit()
            return mem

    def update_memory(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
        **updates: Any,
    ) -> Memory | None:
        existing = self.get_memory(memory_id, scope=scope)
        if not existing:
            return None

        # Apply updates in-memory
        for key, value in updates.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        existing.touch()

        payload = existing.to_dict()
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE memories SET
                    type = ?,
                    content = ?,
                    scope = ?,
                    metadata = ?,
                    updated_at = ?,
                    valid_from = ?,
                    valid_until = ?,
                    importance = ?,
                    access_count = ?,
                    last_accessed = ?
                WHERE id = ?
                """,
                (
                    payload["type"],
                    payload["content"],
                    payload["scope"],
                    json.dumps(payload.get("metadata") or {}),
                    payload["updated_at"],
                    payload["valid_from"],
                    payload["valid_until"],
                    payload["importance"],
                    payload["access_count"],
                    payload["last_accessed"],
                    payload["id"],
                ),
            )
            conn.commit()
        return existing

    def delete_memory(self, memory_id: str, scope: str | None = None) -> bool:
        query = "DELETE FROM memories WHERE id = ?"
        params: list[Any] = [memory_id]
        if scope:
            query += " AND scope = ?"
            params.append(scope)
        with self._get_connection() as conn:
            cur = conn.execute(query, params)
            conn.commit()
            return cur.rowcount > 0

    def search_memories(
        self,
        query: str,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        q = "SELECT * FROM memories WHERE lower(content) LIKE ?"
        params: list[Any] = [f"%{query.lower()}%"]
        if scope:
            q += " AND scope = ?"
            params.append(scope)
        if types:
            placeholders = ",".join("?" for _ in types)
            q += f" AND type IN ({placeholders})"
            params.extend([t.value for t in types])
        with self._get_connection() as conn:
            rows = conn.execute(q, params).fetchall()
            return [self._row_to_memory(row) for row in rows]

    def list_memories(
        self,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        q = "SELECT * FROM memories WHERE 1=1"
        params: list[Any] = []
        if scope:
            q += " AND scope = ?"
            params.append(scope)
        if types:
            placeholders = ",".join("?" for _ in types)
            q += f" AND type IN ({placeholders})"
            params.extend([t.value for t in types])
        with self._get_connection() as conn:
            rows = conn.execute(q, params).fetchall()
            return [self._row_to_memory(row) for row in rows]

    def list_relationships(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
    ) -> list[Relationship]:
        q = "SELECT * FROM relationships WHERE source_id = ?"
        params: list[Any] = [memory_id]
        if scope:
            q += " AND scope = ?"
            params.append(scope)
        with self._get_connection() as conn:
            rows = conn.execute(q, params).fetchall()
            return [self._row_to_relationship(row) for row in rows]
