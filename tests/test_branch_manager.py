import pytest
import json
from datetime import datetime
from pathlib import Path
from copal_cli.memory.branch_manager import BranchManager
from copal_cli.memory.models import Memory, MemoryType

@pytest.fixture
def bm_init(tmp_path):
    return BranchManager(tmp_path / "memory")

def test_create_branch(bm_init, tmp_path):
    bm = bm_init
    bm.create_branch("task-123", "desc")
    
    branch_dir = tmp_path / "memory" / "branches" / "task-123"
    assert branch_dir.exists()
    assert (branch_dir / "meta.json").exists()
    assert (branch_dir / "memories.json").exists()

def test_create_branch_exists(bm_init):
    bm = bm_init
    bm.create_branch("dup", "d")
    with pytest.raises(FileExistsError):
        bm.create_branch("dup")

def test_add_memory_to_branch(bm_init):
    bm = bm_init
    # Should auto-create branch
    mem = Memory(id="m1", type=MemoryType.NOTE, content="c", scope="task:t1")
    bm.add_memory_to_branch("t1", mem)
    
    mems = bm.get_branch_memories("t1")
    assert len(mems) == 1
    assert mems[0]["id"] == "m1"

def test_get_branch_memories_missing(bm_init):
    bm = bm_init
    assert bm.get_branch_memories("missing") == []

def test_list_branches(bm_init):
    bm = bm_init
    bm.create_branch("b1")
    bm.create_branch("b2")
    branches = bm.list_branches()
    assert "b1" in branches
    assert "b2" in branches
