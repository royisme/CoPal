from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from copal_cli.config.manifest import Manifest
from copal_cli.harness.validate import validate_command

logger = logging.getLogger(__name__)
console = Console()

class AgentManager:
    """
    Manages the 'Compounding Engineering' state of a Copal project.
    Acts as the 'Manager' that directs the Agent to the next task.
    """
    
    def __init__(self, target_path: Path):
        self.target_path = target_path
        self.manifest_path = target_path / ".copal" / "manifest.yaml"
        self._manifest: Optional[Manifest] = None
        
    @property
    def manifest(self) -> Manifest:
        if not self._manifest:
            if not self.manifest_path.exists():
                raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
            self._manifest = Manifest.load(self.manifest_path)
        return self._manifest
        
    @property
    def artifacts_dir(self) -> Path:
        return self.target_path / self.manifest.artifacts.dir

    @property
    def todo_path(self) -> Path:
        return self.artifacts_dir / "todo.json"

    def ensure_artifacts_dir(self):
        if not self.artifacts_dir.exists():
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def load_todo(self) -> Dict[str, Any]:
        """Load the todo.json state."""
        if not self.todo_path.exists():
            # If not exists, return empty structure or raise? 
            # Better to return structure matching schema
            return {"items": []}
            
        try:
            with open(self.todo_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            console.print(f"[red]✗ Invalid JSON in {self.todo_path}[/red]")
            return {"items": []}

    def save_todo(self, data: Dict[str, Any]):
        """Save the todo.json state."""
        self.ensure_artifacts_dir()
        with open(self.todo_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Find the first task that is NOT 'done'.
        """
        data = self.load_todo()
        items = data.get("items", [])
        
        for item in items:
            status = item.get("status", "todo").lower()
            if status != "done":
                return item
        return None

    def advance_task(self, task_id: Optional[str] = None) -> bool:
        """
        Advance a task's status.
        If task_id is None, advances the current 'next' task.
        Logic: todo -> in_progress
        """
        data = self.load_todo()
        items = data.get("items", [])
        modified = False
        
        target_item = None
        
        if task_id:
            # Find specific task
            for item in items:
                if str(item.get("id")) == str(task_id):
                    target_item = item
                    break
            if not target_item:
                console.print(f"[red]✗ Task ID {task_id} not found.[/red]")
                return False
        else:
            # Find next available task
            for item in items:
                if item.get("status", "todo") != "done":
                    target_item = item
                    break
            if not target_item:
                console.print(Panel("[green]All tasks are done! Good job![/green]", title="Mission Complete", border_style="green"))
                return False

        current_status = target_item.get("status", "todo")
        action = target_item.get("action")
        tid = target_item.get("id")
        
        if current_status == "todo":
            target_item["status"] = "in_progress"
            console.print(Panel(
                f"[bold cyan]{action}[/bold cyan]",
                title=f"▶ Started Task {tid}",
                border_style="cyan"
            ))
            modified = True
        elif current_status == "in_progress":
            console.print(Panel(
                f"[bold yellow]{action}[/bold yellow]",
                title=f"⚠ Already In Progress (Task {tid})",
                border_style="yellow"
            ))
        
        if modified:
            self.save_todo(data)
            
        return True

    def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as done.
        """
        data = self.load_todo()
        items = data.get("items", [])
        modified = False
        
        for item in items:
            if str(item.get("id")) == str(task_id):
                item["status"] = "done"
                console.print(Panel(
                    f"[bold green]{item.get('action')}[/bold green]",
                    title=f"✓ Completed Task {task_id}",
                    border_style="green"
                ))
                modified = True
                break
                
        if not modified:
             console.print(f"[red]✗ Task ID {task_id} not found.[/red]")
             return False
             
        self.save_todo(data)
        return True

    def summary(self):
        """Print a summary of todo list."""
        data = self.load_todo()
        items = data.get("items", [])
        
        if not items:
            console.print("[dim]No tasks in todo.json[/dim]")
            return

        table = Table(title="Engineering Loop Tasks", box=None, show_lines=True)
        table.add_column("ID", style="dim", width=4)
        table.add_column("Action", style="bold")
        table.add_column("Status", width=12)

        for item in items:
            status = item.get("status", "todo")
            sid = str(item.get("id"))
            action = item.get("action")
            
            status_render = status
            if status == "done":
                status_render = "[green]Done ✓[/green]"
                action = f"[dim]{action}[/dim]"
            elif status == "in_progress":
                status_render = "[cyan reverse] In Progress [/cyan reverse]"
                action = f"[cyan]{action}[/cyan]"
            elif status == "blocked":
                status_render = "[red]Blocked ✋[/red]"
            elif status == "todo":
                status_render = "[dim]Todo[/dim]"
                
            table.add_row(sid, action, status_render)

        console.print(table)

