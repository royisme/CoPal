from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from rich.table import Table
from rich.panel import Panel
from rich.console import Console

from copal_cli.harness.session import SessionManager
from copal_cli.harness.validate import validate_command

logger = logging.getLogger(__name__)
console = Console()

class AgentManager:
    """
    Manages the 'Compounding Engineering' state of a Copal project.
    Acts as the 'Manager' that directs the Agent to the next task.
    """
    
    def __init__(self, target: Path):
        self.target = target
        self.todo_path = target / ".copal" / "artifacts" / "todo.json"
        
        # Ensure directories exist
        self.todo_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.console = Console()
        self.session_manager = SessionManager(target)
        self.manifest_path = target / ".copal" / "manifest.yaml"
        self._manifest: Optional[Manifest] = None
        
    @property
    def manifest(self) -> Manifest:
        if not self._manifest:
            if not self.manifest_path.exists():
                raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
            self._manifest = Manifest.load(self.manifest_path)
        return self._manifest
        
    @property
    def manifest(self) -> Manifest:
        if not self._manifest:
            if not self.manifest_path.exists():
                raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
            self._manifest = Manifest.load(self.manifest_path)
        return self._manifest


    @property
    def artifacts_dir(self) -> Path:
        return self.target / ".copal" / "artifacts"

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

    def advance_task(self, task_id: Optional[str] = None, worktree: bool = False) -> bool:
        """
        Move the next available 'todo' item to 'in_progress'. 
        If task_id is provided, select that specific task.
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
            self.console.print(Panel(
                f"[bold]{target_item.get('action')}[/bold]",
                title=f"▶ Started Task {target_item.get('id')}",
                border_style="blue"
            ))
            
            # Show Recent Session Context for Agent
            if self.session_manager.is_enabled():
                history = self.session_manager.get_recent_sessions(limit=3)
                if history:
                    self.console.print("\n[dim]Recent Sessions:[/dim]")
                    for h in history:
                         self.console.print(f"[dim]- {h.formatted}[/dim]")
            
            # Create Worktree if requested
            if worktree:
                self._create_task_worktree(target_item)
            
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

    def _create_task_worktree(self, task: dict):
        """Create a git worktree for the task."""
        from copal_cli.worktree.git_utils import worktree_add, get_repo_root
        from copal_cli.worktree.sync import sync_assets

        repo_root = get_repo_root(self.target)
        if not repo_root:
            self.console.print("[red]✗ Not a git repository. Cannot create worktree.[/red]")
            return

        task_id = task.get("id")
        wt_name = f"copal-task-{task_id}"
        repo_name = repo_root.name
        wt_root = repo_root.parent / f"{repo_name}.wt"
        target_path = wt_root / wt_name
        
        if target_path.exists():
             self.console.print(f"[yellow]⚠ Worktree {wt_name} already exists at {target_path}.[/yellow]")
             self.console.print(f"[bold]To switch: cd {target_path}[/bold]")
             return

        self.console.print(f"[bold]Creating worktree for task {task_id}...[/bold]")
        if worktree_add(repo_root, target_path, branch=wt_name):
             sync_assets(repo_root, target_path)
             self.console.print(f"[green]✓ Worktree created at {target_path}[/green]")
             self.console.print(f"[bold]To start working: cd {target_path}[/bold]")
        else:
             self.console.print(f"[red]✗ Failed to create worktree.[/red]")

    def complete_task(self, task_id: str) -> bool:
        """
        Mark a task as done.
        """
        data = self.load_todo()
        items = data.get("items", [])
        modified = False
        
        task = None
        for item in items:
            if str(item.get("id")) == str(task_id):
                task = item
                break
        
        if task:
            task["status"] = "done"
            # Save todo.json
            self.save_todo(data)
            
            # Save Session Summary
            summary = self._generate_completion_summary(task)
            self.session_manager.save_session_summary(task_id, summary)
            
            self.console.print(Panel(
                f"[green]Tasks Updated![/green]\n"
                f"Task: {task['id']} marked as [bold]done[/bold].\n"
                f"Session summary saved.",
                title="Task Completed"
            ))
            return True

        self.console.print(f"[red]Task {task_id} not found in todo list.[/red]")
        return False

    def _generate_completion_summary(self, task: dict) -> str:
        """Generate a summary string for the completed task."""
        # In a real agent workflow, this might come from the agent's own output.
        # For now, we generate a basic record.
        return f"Completed task '{task.get('action', 'unknown')}'. Status changed from {task.get('status')} to done."

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

