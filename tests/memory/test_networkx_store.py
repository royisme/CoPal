from __future__ import annotations

from pathlib import Path

from copal_cli.memory.models import EdgeType, Memory, MemoryType
from copal_cli.memory.networkx_store import NetworkXMemoryStore
from copal_cli.memory.scope import ScopeManager


def build_store(tmp_path: Path):
    target_root = tmp_path / "repo"
    target_root.mkdir()
    config = {"backend": "networkx", "database": ".copal/memory.db"}
    scope_manager = ScopeManager.from_config(target_root, config)
    store = NetworkXMemoryStore(target_root, config=config, scope_manager=scope_manager)
    return store, target_root, scope_manager


def test_add_and_get_memory(tmp_path):
    store, _, scope_manager = build_store(tmp_path)
    scope = scope_manager.current_scope
    memory = Memory(
        id="mem-1",
        type=MemoryType.NOTE,
        content="Investigated authentication edge cases",
        scope=scope,
        importance=0.7,
    )
    store.add_memory(memory)

    fetched = store.get_memory("mem-1")
    assert fetched is not None
    assert fetched.content.startswith("Investigated")

    # Reload from disk to ensure persistence
    reloaded, *_ = build_store(tmp_path)
    persisted = reloaded.get_memory("mem-1")
    assert persisted is not None
    assert persisted.scope == scope


def test_update_search_and_delete(tmp_path):
    store, _, scope_manager = build_store(tmp_path)
    scope = scope_manager.current_scope
    memory = Memory(
        id="mem-2",
        type=MemoryType.DECISION,
        content="Adopt PostgreSQL for session storage",
        scope=scope,
    )
    store.add_memory(memory)

    store.update_memory("mem-2", content="Adopt Redis for session storage")
    updated = store.get_memory("mem-2")
    assert updated is not None
    assert "Redis" in updated.content

    matches = store.search_memories("Redis", scope=scope)
    assert matches
    assert matches[0].id == "mem-2"

    assert store.delete_memory("mem-2")
    assert store.get_memory("mem-2") is None


def test_supersede_memory_creates_relationship(tmp_path):
    store, _, scope_manager = build_store(tmp_path)
    scope = scope_manager.current_scope

    old_memory = Memory(
        id="mem-old",
        type=MemoryType.DECISION,
        content="Use SHA1 hashing",
        scope=scope,
    )
    store.add_memory(old_memory)

    new_memory = Memory(
        id="mem-new",
        type=MemoryType.DECISION,
        content="Use SHA256 hashing",
        scope=scope,
    )

    store.supersede_memory("mem-old", new_memory, relationship_metadata={"reason": "security"})

    superseding = store.get_memory("mem-new")
    assert superseding is not None

    relationships = store.list_relationships("mem-new", scope=scope)
    assert relationships
    assert relationships[0].type is EdgeType.SUPERSEDES
    assert relationships[0].metadata["reason"] == "security"

    superseded = store.get_memory("mem-old")
    assert superseded is not None
    assert superseded.valid_until is not None
