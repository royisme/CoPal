"""Helpers that integrate memory capture into the CoPal workflow."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from .config import (
    is_auto_capture_enabled,
    is_memory_enabled,
    load_memory_config,
)
from .models import Memory, MemoryType
from .networkx_store import NetworkXMemoryStore
from .scope import ScopeManager

logger = logging.getLogger(__name__)


def maybe_record_stage_memory(
    *,
    target_root: Path,
    memory_type: MemoryType,
    content: str,
    metadata: Optional[dict[str, Any]] = None,
    scope_override: str | None = None,
    importance: float = 0.5,
) -> None:
    """Persist a memory entry if auto capture is enabled."""

    try:
        config = load_memory_config(target_root)
        if not is_memory_enabled(config) or not is_auto_capture_enabled(config):
            return
        scope_manager = ScopeManager.from_config(target_root, config)
        store = NetworkXMemoryStore(
            target_root,
            config=config,
            scope_manager=scope_manager,
        )
        scope = scope_manager.resolve(scope_override)
        memory = Memory(
            id=str(uuid4()),
            type=memory_type,
            content=content,
            scope=scope,
            metadata=metadata or {},
            importance=importance,
        )
        store.add_memory(memory)
    except Exception as exc:  # pragma: no cover - fail quietly
        logger.debug("Failed to record memory for stage: %s", exc)
