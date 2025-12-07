import pytest
from unittest.mock import MagicMock, patch
from argparse import Namespace
from copal_cli.memory.cli_commands import (
    memory_add_command,
    memory_list_command,
    memory_show_command,
    memory_search_command,
    memory_update_command,
    memory_delete_command,
    _build_context
)
from copal_cli.memory.models import Memory, MemoryType
from copal_cli.memory.store_interface import IMemoryStore

@pytest.fixture
def mock_store():
    store = MagicMock(spec=IMemoryStore)
    return store

@pytest.fixture
def mock_context(mock_store):
    with patch("copal_cli.memory.cli_commands.load_memory_config") as mock_load, \
         patch("copal_cli.memory.cli_commands.is_memory_enabled") as mock_enabled, \
         patch("copal_cli.memory.cli_commands.ScopeManager") as MockScopeManager, \
         patch("copal_cli.memory.cli_commands.JsonMemoryStore", return_value=mock_store):
         
        mock_load.return_value = {"enabled": True, "backend": "json"}
        mock_enabled.return_value = True
        MockScopeManager.from_config.return_value.resolve.side_effect = lambda x: x or "project"
        
        yield

def test_add_command(tmp_path, mock_context, mock_store, capsys):
    args = Namespace(
        target=str(tmp_path),
        scope=None,
        metadata=["topic=test", "invalid"],
        type="note",
        id="mem1",
        content="test content",
        importance="0.8"
    )
    
    ret = memory_add_command(args)
    assert ret == 0
    mock_store.add_memory.assert_called_once()
    captured = capsys.readouterr()
    assert "Created memory mem1" in captured.out

def test_list_command(tmp_path, mock_context, mock_store, capsys):
    mock_store.list_memories.return_value = [
        Memory(id="m1", type=MemoryType.NOTE, content="c1", scope="project")
    ]
    
    args = Namespace(target=str(tmp_path), scope=None, types=None)
    ret = memory_list_command(args)
    assert ret == 0
    assert "c1" in capsys.readouterr().out

def test_show_command(tmp_path, mock_context, mock_store, capsys):
    mock_store.get_memory.return_value = Memory(
        id="m1", type=MemoryType.NOTE, content="c1", scope="project", metadata={"foo": "bar"}
    )
    
    args = Namespace(target=str(tmp_path), scope=None, memory_id="m1")
    ret = memory_show_command(args)
    assert ret == 0
    out = capsys.readouterr().out
    assert "ID: m1" in out
    assert "foo: bar" in out

def test_show_command_not_found(tmp_path, mock_context, mock_store, capsys):
    mock_store.get_memory.return_value = None
    args = Namespace(target=str(tmp_path), scope=None, memory_id="m1")
    ret = memory_show_command(args)
    assert ret == 1

def test_search_command(tmp_path, mock_context, mock_store, capsys):
    mock_store.search_memories.return_value = [
         Memory(id="m1", type=MemoryType.NOTE, content="match", scope="project")
    ]
    args = Namespace(target=str(tmp_path), scope=None, query="match", types=None)
    ret = memory_search_command(args)
    assert ret == 0
    assert "Found 1 memories" in capsys.readouterr().out

def test_update_command(tmp_path, mock_context, mock_store, capsys):
    mock_store.update_memory.return_value = Memory(id="m1", type=MemoryType.NOTE, content="new", scope="project")
    
    args = Namespace(
        target=str(tmp_path),
        scope=None,
        memory_id="m1",
        content="new",
        importance=None,
        metadata=None,
        type=None
    )
    ret = memory_update_command(args)
    assert ret == 0
    assert "Updated memory m1" in capsys.readouterr().out

def test_delete_command(tmp_path, mock_context, mock_store, capsys):
    mock_store.delete_memory.return_value = True
    args = Namespace(target=str(tmp_path), scope=None, memory_id="m1")
    ret = memory_delete_command(args)
    assert ret == 0
    assert "Deleted memory m1" in capsys.readouterr().out

def test_context_disabled(tmp_path, capsys):
    with patch("copal_cli.memory.cli_commands.load_memory_config", return_value={"enabled": False}), \
         patch("copal_cli.memory.cli_commands.is_memory_enabled", return_value=False):
        
        args = Namespace(target=str(tmp_path))
        ctx = _build_context(args)
        assert ctx is None
        assert "disabled" in capsys.readouterr().out
