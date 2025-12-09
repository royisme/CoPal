from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

from copal_cli.memory.models import Memory, MemoryType, Relationship, EdgeType, _now
from copal_cli.memory.sqlite_store import SQLiteMemoryStore
from copal_cli.memory.config import load_memory_config, resolve_database_path, is_memory_enabled
from copal_cli.memory.scope import ScopeManager

logger = logging.getLogger(__name__)

@dataclass
class SessionSummary:
    id: str
    task_id: str
    content: str
    created_at: datetime
    
    @property
    def formatted(self) -> str:
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] Task {self.task_id}: {self.content}"

class SessionManager:
    """Manages session-level memories (EXPERIENCE) for long-running agent contexts."""

    def __init__(self, target_root: Path):
        self.target_root = target_root
        self.config = load_memory_config(target_root)
        self.scope_manager = ScopeManager.from_config(target_root, self.config)
        
        # Initialize store only if enabled
        self._store: Optional[SQLiteMemoryStore] = None
        if is_memory_enabled(self.config):
            # For now, default to SQLite. Can abstract later if needed.
            try:
                db_path = resolve_database_path(target_root, self.config)
                self._store = SQLiteMemoryStore(
                    target_root=target_root,
                    db_path=db_path,
                    config=self.config,
                    scope_manager=self.scope_manager,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize memory store for session manager: {e}")

    def close(self):
        if self._store:
            self._store.close()

    def is_enabled(self) -> bool:
        return self._store is not None

    def save_session_summary(self, task_id: str, summary_content: str) -> Optional[str]:
        """
        Save a session summary as an EXPERIENCE memory.
        Links it to the previous session memory if found.
        """
        if not self._store:
            return None

        # 1. Create the new memory
        memory_id = f"session-{_now().strftime('%Y%m%d-%H%M%S')}-{uuid4().hex[:8]}"
        memory = Memory(
            id=memory_id,
            type=MemoryType.EXPERIENCE,
            content=summary_content,
            scope=self.scope_manager.current_scope,
            metadata={"task_id": task_id, "type": "session_summary"},
            importance=0.8, # High importance for recent history
        )

        # 2. Find previous session to link
        prev_session = self._get_latest_session_memory()
        relationships = []
        if prev_session:
            relationships.append(Relationship(
                id=f"rel-{uuid4()}",
                source_id=prev_session.id,
                target_id=memory.id,
                type=EdgeType.TEMPORAL_SEQUENCE,
                scope=self.scope_manager.current_scope,
            ))

        # 3. Save to store
        try:
            self._store.add_memory(memory, relationships)
            logger.info(f"Saved session summary {memory.id}")
            return memory.id
        except Exception as e:
            logger.error(f"Failed to save session summary: {e}")
            return None

    def get_recent_sessions(self, limit: int = 5) -> List[SessionSummary]:
        """Retrieve the N most recent session summaries."""
        if not self._store:
            return []

        try:
            # Query for EXPERIENCE memories with metadata type=session_summary
            # Since SQLite store search/list capabilities might be limited in filtering by metadata,
            # we rely on listing EXPERIENCE types and sorting/filtering in memory for now.
            # TODO: Add nicer filtering to store interface later.
            memories = self._store.list_memories(
                scope=self.scope_manager.current_scope,
                types=[MemoryType.EXPERIENCE]
            )
            
            # Filter for session summaries and sort by creation time desc
            summaries = []
            for m in memories:
                if m.metadata.get("type") == "session_summary":
                    summaries.append(SessionSummary(
                        id=m.id,
                        task_id=m.metadata.get("task_id", "unknown"),
                        content=m.content,
                        created_at=m.created_at
                    ))
            
            # Sort descending (newest first)
            summaries.sort(key=lambda s: s.created_at, reverse=True)
            return summaries[:limit]

        except Exception as e:
            logger.error(f"Failed to retrieve recent sessions: {e}")
            return []

    def _get_latest_session_memory(self) -> Optional[Memory]:
        """Get the single most recent session memory."""
        recents = self.get_recent_sessions(limit=1)
        if not recents:
            return None
        
        # We need the full Memory object to get its ID for linking
        # Re-fetch is safest or just use what we have if we trust ID consistency.
        # Ideally get_recent_sessions returns objects that contain enough info.
        # Let's just re-fetch the memory by ID from the store.
        if not self._store:
            return None
            
        return self._store.get_memory(recents[0].id)
