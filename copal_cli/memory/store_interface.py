"""Abstract interface for memory back-ends."""

from __future__ import annotations

from typing import Any, Iterable, Protocol, Sequence

from .models import Memory, MemoryType, Relationship


class IMemoryStore(Protocol):
    """Protocol describing memory operations required by the CLI."""

    def add_memory(
        self,
        memory: Memory,
        relationships: Sequence[Relationship] | None = None,
    ) -> Memory:
        """Persist a new memory and optional relationships."""

    def get_memory(self, memory_id: str, scope: str | None = None) -> Memory | None:
        """Return a memory by identifier."""

    def update_memory(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
        **updates: Any,
    ) -> Memory | None:
        """Update the provided memory fields."""

    def delete_memory(self, memory_id: str, scope: str | None = None) -> bool:
        """Delete a memory and return whether deletion occurred."""

    def supersede_memory(
        self,
        old_memory_id: str,
        new_memory: Memory,
        relationship_metadata: dict[str, Any] | None = None,
    ) -> Memory:
        """Create a new memory that supersedes an existing one."""

    def search_memories(
        self,
        query: str,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        """Search for memories matching the provided query."""

    def list_memories(
        self,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        """Return all memories in scope, optionally filtered by type."""

    def summarise_project(self, scope: str | None = None) -> dict[str, Any]:
        """Return an aggregate summary of stored memories."""

    def list_relationships(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
    ) -> list[Relationship]:
        """Return relationships originating from the memory."""
