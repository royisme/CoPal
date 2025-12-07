from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import Memory, MemoryType

class BranchManager:
    """Manages memory branches for tasks."""
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = memory_dir
        self.branches_dir = memory_dir / "branches"
        self.branches_dir.mkdir(parents=True, exist_ok=True)
        
    def create_branch(self, task_id: str, description: str = "") -> None:
        """Create a new branch for a task."""
        branch_path = self.branches_dir / task_id
        if branch_path.exists():
            raise FileExistsError(f"Branch {task_id} already exists")
            
        branch_path.mkdir()
        meta = {
            "created_at": datetime.now().isoformat(),
            "description": description,
            "status": "active"
        }
        with open(branch_path / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)
            
        # Initialize memories file
        with open(branch_path / "memories.json", "w") as f:
            json.dump({"memories": []}, f, indent=2)

    def get_branch_memories(self, task_id: str) -> List[Dict[str, Any]]:
        """Get memories from a branch."""
        mem_file = self.branches_dir / task_id / "memories.json"
        if not mem_file.exists():
            return []
        with open(mem_file, "r") as f:
            return json.load(f).get("memories", [])
            
    def add_memory_to_branch(self, task_id: str, memory: Memory) -> None:
        """Add a memory to a branch."""
        branch_path = self.branches_dir / task_id
        if not branch_path.exists():
            self.create_branch(task_id, description="Auto-created for memory")
            
        mem_file = branch_path / "memories.json"
        with open(mem_file, "r") as f:
            data = json.load(f)
            
        data.get("memories", []).append(memory.to_dict())
        
        with open(mem_file, "w") as f:
            json.dump(data, f, indent=2)

    def list_branches(self) -> List[str]:
        return [d.name for d in self.branches_dir.iterdir() if d.is_dir()]
