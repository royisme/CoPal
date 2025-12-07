from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Sequence

from copal_cli.fs.writer import atomic_write
from .models import Memory, MemoryType, Relationship
from .store_interface import IMemoryStore
from .scope import ScopeManager
from .branch_manager import BranchManager

class JsonMemoryStore(IMemoryStore):
    """
    Enhanced JSON file-based memory store.
    Supports Project Memory (Markdown) and Task Memory (Branches).
    """

    def __init__(
        self,
        target_root: Path,
        config: dict[str, Any],
        scope_manager: ScopeManager,
    ):
        self.target_root = target_root
        self.config = config
        self.scope_manager = scope_manager
        self.memory_dir = target_root / ".copal" / "memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.branch_manager = BranchManager(self.memory_dir)
        self.index_file = self.memory_dir / "index.json"
        
        if not self.index_file.exists():
            atomic_write(self.index_file, json.dumps({"memories": [], "project_meta": {}}, indent=2))
            
    def _load_index(self) -> dict[str, Any]:
        with open(self.index_file, "r") as f:
            return json.load(f)

    def _save_index(self, data: dict[str, Any]) -> None:
        atomic_write(self.index_file, json.dumps(data, indent=2))

    def add_memory(
        self,
        memory: Memory,
        relationships: Sequence[Relationship] | None = None,
    ) -> Memory:
        # Determine storage strategy based on scope
        if memory.scope.startswith("task:"):
            task_id = memory.scope.split(":")[1]
            self.branch_manager.add_memory_to_branch(task_id, memory)
            # Also add to index for global search? Maybe just partial?
            # For now, let's keep index as "global project memory mainly"
        else:
            # Project scope or default
            data = self._load_index()
            data.setdefault("memories", []).append(memory.to_dict())
            self._save_index(data)
            
            # If it's a markdown-able memory, write to markdown
            if memory.type in (MemoryType.NOTE, MemoryType.EXPERIENCE) and memory.scope == "project":
                self._append_to_markdown(memory)
                
        return memory

    def _append_to_markdown(self, memory: Memory) -> None:
        project_mem_dir = self.memory_dir / "project"
        project_mem_dir.mkdir(exist_ok=True)
        
        # Determine topic from metadata or default
        topic = memory.metadata.get("topic", "general")
        md_file = project_mem_dir / f"{topic}.md"
        
        entry = f"\n## {memory.created_at.strftime('%Y-%m-%d %H:%M')}\n\n{memory.content}\n"
        with open(md_file, "a", encoding="utf-8") as f:
            f.write(entry)

    def get_memory(self, memory_id: str, scope: str | None = None) -> Memory | None:
        # Search index first
        data = self._load_index()
        for m_dict in data.get("memories", []):
            if m_dict["id"] == memory_id:
                return Memory.from_dict(m_dict)
                
        # If scope is task, search branch
        if scope and scope.startswith("task:"):
            task_id = scope.split(":")[1]
            branch_mems = self.branch_manager.get_branch_memories(task_id)
            for m_dict in branch_mems:
                if m_dict["id"] == memory_id:
                    return Memory.from_dict(m_dict)
        
        return None

    def update_memory(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
        content: str | None = None,
        **kwargs
    ) -> Memory | None:
        # Load index
        data = self._load_index()
        memories = data.get("memories", [])
        
        target_dict = None
        target_idx = -1
        
        # Search in index
        for i, m in enumerate(memories):
            if m["id"] == memory_id:
                if scope and m.get("scope") != scope:
                    continue
                target_dict = m
                target_idx = i
                break
        
        if target_dict:
            # Update index memory
            if content:
                target_dict["content"] = content
            # Apply other kwargs
            for k, v in kwargs.items():
                if k in target_dict: # Only update known fields? Or simple update
                     target_dict[k] = v
                     
            memories[target_idx] = target_dict
            self._save_index(data)
            return Memory.from_dict(target_dict)
            
        # TODO: Implement branch/task memory update
        return None

    def delete_memory(self, memory_id: str, scope: str | None = None) -> bool:
        data = self._load_index()
        memories = data.get("memories", [])
        
        new_memories = []
        found = False
        
        for m in memories:
            if m["id"] == memory_id:
                if scope and m.get("scope") != scope:
                    new_memories.append(m)
                    continue
                found = True
            else:
                new_memories.append(m)
                
        if found:
            data["memories"] = new_memories
            self._save_index(data)
            return True
            
        # TODO: Implement branch/task memory delete
        return False

    def search_memories(
        self,
        query: str,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        results = []
        
        # Search index
        data = self._load_index()
        for m_dict in data.get("memories", []):
            if self._match(m_dict, query, scope, types):
                results.append(Memory.from_dict(m_dict))
                
        # Search task branch if scope specified
        if scope and scope.startswith("task:"):
            task_id = scope.split(":")[1]
            branch_mems = self.branch_manager.get_branch_memories(task_id)
            for m_dict in branch_mems:
                 if self._match(m_dict, query, scope, types):
                    results.append(Memory.from_dict(m_dict))
                    
        return results

    def _match(self, m_dict: dict, query: str, scope: str | None, types: Iterable[MemoryType] | None) -> bool:
        if scope and m_dict.get("scope") != scope:
            return False
        if types and MemoryType(m_dict["type"]) not in types:
            return False
        if query.lower() in m_dict.get("content", "").lower():
            return True
        return False

    def list_memories(
        self,
        *,
        scope: str | None = None,
        types: Iterable[MemoryType] | None = None,
    ) -> list[Memory]:
        return self.search_memories("", scope=scope, types=types)

    def list_relationships(
        self,
        memory_id: str,
        *,
        scope: str | None = None,
    ) -> list[Relationship]:
        return []

    def close(self) -> None:
        """Close any open resources."""
        pass
