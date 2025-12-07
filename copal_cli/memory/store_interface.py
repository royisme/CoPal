"""Abstract interface for memory back-ends."""


from typing import Any, Protocol
from collections.abc import  Sequence

from .models import Memory, Relationship


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

    def search_memories(
        self,
        query: str,
        *,
        scope: str | None = None,
        types: Sequence[Any] | None = None,
    ) -> list[Memory]:
        """Search memories matching query and filters."""

    def list_memories(
        self,
        *,
        scope: str | None = None,
        types: Sequence[Any] | None = None,
    ) -> list[Memory]:
        """List memories matching filters."""

    def list_relationships(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
    ) -> list[Relationship]:
        """Return relationships originating from the memory."""

    def close(self) -> None:
        """Close any open resources (e.g. database connections)."""
