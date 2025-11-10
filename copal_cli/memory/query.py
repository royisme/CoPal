"""Query helpers for the memory graph."""

from __future__ import annotations

import re
from typing import Any
from collections.abc import Iterable

from .models import Memory, MemoryType


class MemoryQueryEngine:
    """Lightweight search utilities built on top of NetworkX."""

    def __init__(self, graph: Any):
        self._graph = graph

    def search(
        self,
        query: str,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        type_set = set(types) if types else None
        results: list[Memory] = []
        for node_id, data in self._graph.nodes(data=True):
            memory: Memory = data.get("memory")
            if memory is None:
                continue
            if scope and memory.scope != scope:
                continue
            if type_set and memory.type not in type_set:
                continue
            haystacks = [memory.content]
            if memory.metadata:
                haystacks.extend(str(v) for v in memory.metadata.values())
            if any(pattern.search(text or "") for text in haystacks):
                results.append(memory)
        return results

    def list(
        self,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        type_set = set(types) if types else None
        results: list[Memory] = []
        for _, data in self._graph.nodes(data=True):
            memory: Memory = data.get("memory")
            if memory is None:
                continue
            if scope and memory.scope != scope:
                continue
            if type_set and memory.type not in type_set:
                continue
            results.append(memory)
        return results
