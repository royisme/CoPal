"""Unit tests for session.py SessionManager class."""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from datetime import datetime, timezone

from copal_cli.harness.session import SessionManager, SessionSummary
from copal_cli.memory.models import Memory, MemoryType, EdgeType


@pytest.fixture
def mock_memory_enabled():
    """Mock memory as enabled with SQLite store."""
    with patch("copal_cli.harness.session.is_memory_enabled") as mock_enabled, \
         patch("copal_cli.harness.session.load_memory_config") as mock_config, \
         patch("copal_cli.harness.session.resolve_database_path") as mock_db_path, \
         patch("copal_cli.harness.session.SQLiteMemoryStore") as mock_store_cls, \
         patch("copal_cli.harness.session.ScopeManager") as mock_scope_mgr:
        
        mock_enabled.return_value = True
        mock_config.return_value = {"enabled": True}
        mock_db_path.return_value = Path("/tmp/test_memory.sqlite")
        
        mock_store = MagicMock()
        mock_store_cls.return_value = mock_store
        
        mock_scope = MagicMock()
        mock_scope.current_scope = "test-scope"
        mock_scope_mgr.from_config.return_value = mock_scope
        
        yield {
            "store": mock_store,
            "scope_manager": mock_scope,
        }


@pytest.fixture
def mock_memory_disabled():
    """Mock memory as disabled."""
    with patch("copal_cli.harness.session.is_memory_enabled") as mock_enabled, \
         patch("copal_cli.harness.session.load_memory_config") as mock_config, \
         patch("copal_cli.harness.session.ScopeManager") as mock_scope_mgr:
        
        mock_enabled.return_value = False
        mock_config.return_value = {"enabled": False}
        
        mock_scope = MagicMock()
        mock_scope.current_scope = "test-scope"
        mock_scope_mgr.from_config.return_value = mock_scope
        
        yield


class TestSessionSummary:
    """Tests for SessionSummary dataclass."""
    
    def test_formatted_property(self):
        summary = SessionSummary(
            id="session-123",
            task_id="1",
            content="Implemented feature X",
            created_at=datetime(2025, 12, 8, 10, 30, tzinfo=timezone.utc)
        )
        formatted = summary.formatted
        assert "2025-12-08 10:30" in formatted
        assert "Task 1" in formatted
        assert "Implemented feature X" in formatted


class TestSessionManager:
    """Tests for SessionManager class."""

    def test_init_with_memory_enabled(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        
        assert manager.is_enabled() is True
        assert manager._store is not None

    def test_init_with_memory_disabled(self, tmp_path, mock_memory_disabled):
        manager = SessionManager(tmp_path)
        
        assert manager.is_enabled() is False
        assert manager._store is None

    def test_save_session_summary_creates_memory(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        mock_store = mock_memory_enabled["store"]
        
        # No previous session
        mock_store.list_memories.return_value = []
        
        result = manager.save_session_summary("task-1", "Completed task successfully")
        
        assert result is not None
        assert result.startswith("session-")
        
        # Verify add_memory was called
        mock_store.add_memory.assert_called_once()
        call_args = mock_store.add_memory.call_args
        memory = call_args[0][0]
        
        assert memory.type == MemoryType.EXPERIENCE
        assert memory.content == "Completed task successfully"
        assert memory.metadata["task_id"] == "task-1"
        assert memory.metadata["type"] == "session_summary"

    def test_save_session_summary_links_to_previous(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        mock_store = mock_memory_enabled["store"]
        
        # Mock existing previous session
        prev_memory = Memory(
            id="prev-session-001",
            type=MemoryType.EXPERIENCE,
            content="Previous session",
            metadata={"task_id": "task-0", "type": "session_summary"},
            scope="test-scope",
        )
        mock_store.list_memories.return_value = [prev_memory]
        mock_store.get_memory.return_value = prev_memory
        
        result = manager.save_session_summary("task-1", "New session")
        
        assert result is not None
        
        # Verify relationship was created
        call_args = mock_store.add_memory.call_args
        relationships = call_args[0][1]
        
        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.source_id == "prev-session-001"
        assert rel.type == EdgeType.TEMPORAL_SEQUENCE

    def test_save_session_summary_disabled_returns_none(self, tmp_path, mock_memory_disabled):
        manager = SessionManager(tmp_path)
        
        result = manager.save_session_summary("task-1", "Content")
        
        assert result is None

    def test_get_recent_sessions_empty(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        mock_store = mock_memory_enabled["store"]
        mock_store.list_memories.return_value = []
        
        result = manager.get_recent_sessions(limit=5)
        
        assert result == []

    def test_get_recent_sessions_returns_summaries(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        mock_store = mock_memory_enabled["store"]
        
        # Create mock memories
        now = datetime.now(timezone.utc)
        memories = [
            Memory(
                id=f"session-{i}",
                type=MemoryType.EXPERIENCE,
                content=f"Session {i} content",
                metadata={"task_id": str(i), "type": "session_summary"},
                scope="test-scope",
                created_at=now,
            )
            for i in range(3)
        ]
        mock_store.list_memories.return_value = memories
        
        result = manager.get_recent_sessions(limit=5)
        
        assert len(result) == 3
        assert all(isinstance(s, SessionSummary) for s in result)

    def test_get_recent_sessions_filters_non_summaries(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        mock_store = mock_memory_enabled["store"]
        
        now = datetime.now(timezone.utc)
        # Mix of session summaries and other EXPERIENCE memories
        memories = [
            Memory(
                id="session-1",
                type=MemoryType.EXPERIENCE,
                content="Real session",
                metadata={"task_id": "1", "type": "session_summary"},
                scope="test-scope",
                created_at=now,
            ),
            Memory(
                id="other-exp",
                type=MemoryType.EXPERIENCE,
                content="Other experience",
                metadata={"type": "other"},
                scope="test-scope",
                created_at=now,
            ),
        ]
        mock_store.list_memories.return_value = memories
        
        result = manager.get_recent_sessions(limit=5)
        
        assert len(result) == 1
        assert result[0].id == "session-1"

    def test_get_recent_sessions_disabled_returns_empty(self, tmp_path, mock_memory_disabled):
        manager = SessionManager(tmp_path)
        
        result = manager.get_recent_sessions(limit=5)
        
        assert result == []

    def test_close(self, tmp_path, mock_memory_enabled):
        manager = SessionManager(tmp_path)
        mock_store = mock_memory_enabled["store"]
        
        manager.close()
        
        mock_store.close.assert_called_once()
