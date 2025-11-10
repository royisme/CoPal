"""Data models for the CoPal memory layer.

The structures defined here are inspired by the mem-layer project
(https://github.com/codebasehq/mem-layer) and adapted for the CoPal CLI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _now() -> datetime:
    return datetime.utcnow()


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.strftime(ISO_FORMAT)


def _deserialize_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, ISO_FORMAT)
    except ValueError:
        # Fallback for strings without microseconds
        return datetime.fromisoformat(value.replace("Z", ""))


class MemoryType(Enum):
    """Enumeration of supported memory categories."""

    DECISION = "decision"
    PREFERENCE = "preference"
    EXPERIENCE = "experience"
    PLAN = "plan"
    NOTE = "note"


class EdgeType(Enum):
    """Relationship types between memories."""

    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    REFERENCES = "references"
    TEMPORAL_SEQUENCE = "temporal_sequence"
    SUPERSEDES = "supersedes"
    ASSOCIATED_WITH = "associated_with"


@dataclass(slots=True)
class Memory:
    """A memory node stored in the knowledge graph."""

    id: str
    type: MemoryType
    content: str
    scope: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    importance: float = 0.5
    access_count: int = 0
    last_accessed: datetime | None = None

    def touch(self) -> None:
        """Update timestamps when the memory is accessed or mutated."""

        self.updated_at = _now()
        self.access_count += 1
        self.last_accessed = self.updated_at

    def to_dict(self) -> dict[str, Any]:
        """Serialise the memory for persistence."""

        return {
            "id": self.id,
            "type": self.type.value,
            "content": self.content,
            "scope": self.scope,
            "metadata": self.metadata,
            "created_at": _serialize_datetime(self.created_at),
            "updated_at": _serialize_datetime(self.updated_at),
            "valid_from": _serialize_datetime(self.valid_from),
            "valid_until": _serialize_datetime(self.valid_until),
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": _serialize_datetime(self.last_accessed),
        }

    @staticmethod
    def from_dict(payload: dict[str, Any]) -> "Memory":
        """Rehydrate a :class:`Memory` from stored data."""

        return Memory(
            id=payload["id"],
            type=MemoryType(payload["type"]),
            content=payload.get("content", ""),
            scope=payload.get("scope", "default"),
            metadata=payload.get("metadata", {}) or {},
            created_at=_deserialize_datetime(payload.get("created_at")) or _now(),
            updated_at=_deserialize_datetime(payload.get("updated_at")) or _now(),
            valid_from=_deserialize_datetime(payload.get("valid_from")),
            valid_until=_deserialize_datetime(payload.get("valid_until")),
            importance=float(payload.get("importance", 0.5)),
            access_count=int(payload.get("access_count", 0)),
            last_accessed=_deserialize_datetime(payload.get("last_accessed")),
        )


@dataclass(slots=True)
class Relationship:
    """Directional relationship between two memories."""

    id: str
    source_id: str
    target_id: str
    type: EdgeType
    scope: str
    weight: float = 1.0
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_now)
    created_by: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "scope": self.scope,
            "weight": self.weight,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "created_at": _serialize_datetime(self.created_at),
            "created_by": self.created_by,
        }

    @staticmethod
    def from_dict(payload: dict[str, Any]) -> "Relationship":
        return Relationship(
            id=payload["id"],
            source_id=payload["source_id"],
            target_id=payload["target_id"],
            type=EdgeType(payload["type"]),
            scope=payload.get("scope", "default"),
            weight=float(payload.get("weight", 1.0)),
            confidence=float(payload.get("confidence", 1.0)),
            metadata=payload.get("metadata", {}) or {},
            created_at=_deserialize_datetime(payload.get("created_at")) or _now(),
            created_by=payload.get("created_by"),
        )
