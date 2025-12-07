
import pytest
from copal_cli.memory.json_store import JsonMemoryStore
from copal_cli.memory.sqlite_store import SQLiteMemoryStore
from copal_cli.memory.models import Memory, MemoryType, Relationship, EdgeType
from copal_cli.memory.scope import ScopeManager

@pytest.fixture(params=["json", "sqlite"])
def memory_store(tmp_path, request):
    config = {"backend": request.param}
    scope_manager = ScopeManager.from_config(tmp_path, config)
    if request.param == "sqlite":
        db_path = tmp_path / ".copal" / "memory.db"
        return SQLiteMemoryStore(target_root=tmp_path, db_path=db_path, config=config, scope_manager=scope_manager)
    return JsonMemoryStore(tmp_path, config, scope_manager)

def test_add_memory(memory_store):
    mem = Memory(
        id="mem-1",
        type=MemoryType.DECISION,
        content="Use Python",
        scope="project",
    )
    memory_store.add_memory(mem)
    
    fetched = memory_store.get_memory("mem-1")
    assert fetched is not None
    assert fetched.content == "Use Python"
    assert fetched.type == MemoryType.DECISION

def test_search_memory(memory_store):
    mem1 = Memory(id="1", type=MemoryType.DECISION, content="Foo Bar", scope="project")
    mem2 = Memory(id="2", type=MemoryType.NOTE, content="Baz Quux", scope="project")
    memory_store.add_memory(mem1)
    memory_store.add_memory(mem2)
    
    results = memory_store.search_memories("Bar")
    assert len(results) == 1
    assert results[0].id == "1"

def test_delete_memory(memory_store):
    mem = Memory(id="d1", type=MemoryType.NOTE, content="Delete me", scope="default")
    memory_store.add_memory(mem)
    
    assert memory_store.get_memory("d1") is not None
    assert memory_store.delete_memory("d1") is True
    assert memory_store.get_memory("d1") is None
    assert memory_store.delete_memory("d1") is False

def test_update_memory(memory_store):
    mem = Memory(id="u1", type=MemoryType.NOTE, content="Original", scope="default")
    memory_store.add_memory(mem)
    
    updated = memory_store.update_memory("u1", content="Updated", importance=0.9)
    assert updated.content == "Updated"
    assert updated.importance == 0.9
    
    fetched = memory_store.get_memory("u1")
    assert fetched.content == "Updated"


def test_relationships_sqlite_only(tmp_path):
    config = {"backend": "sqlite"}
    scope_manager = ScopeManager.from_config(tmp_path, config)
    store = SQLiteMemoryStore(
        target_root=tmp_path,
        db_path=tmp_path / ".copal" / "memory.db",
        config=config,
        scope_manager=scope_manager,
    )

    m1 = Memory(id="r1", type=MemoryType.NOTE, content="source", scope="project")
    m2 = Memory(id="r2", type=MemoryType.NOTE, content="target", scope="project")
    rel = Relationship(
        id="rel1",
        source_id="r1",
        target_id="r2",
        type=EdgeType.ASSOCIATED_WITH,
        scope="project",
    )
    store.add_memory(m1, relationships=[rel])
    store.add_memory(m2)

    rels = store.list_relationships("r1", scope="project")
    assert len(rels) == 1
    assert rels[0].target_id == "r2"
    # scope filter should hide if mismatched
    assert store.list_relationships("r1", scope="other") == []
