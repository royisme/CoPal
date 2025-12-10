from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


# Valid new imports
from .harness.init import init_command as harness_init_command
from .harness.validate import validate_command as harness_validate_command
from .harness.export import export_command as harness_export_command
from .harness.status import status_command as harness_status_command
from .harness.skill import skill_create_command, skill_list_command
from .harness.agent_manager import AgentManager

# Keep existing imports for other commands
from .memory.cli_commands import (
    memory_add_command,
    memory_delete_command,
    memory_list_command,
    memory_search_command,
    memory_show_command,
    memory_update_command,
)
from .memory.models import MemoryType
from .worktree.commands import (
    handle_new as worktree_new_command,
    handle_list as worktree_list_command,
    handle_remove as worktree_remove_command,
)
from .system.mcp import print_mcp_available
from .system.resume import print_resume_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def build_parser() -> argparse.ArgumentParser:
    """Build and configure the argument parser for the CoPal CLI."""

    parser = argparse.ArgumentParser(
        prog="copal",
        description="CoPal (Codex/Claude Pal) - Agent Harness Configuration Tool. \n"
                    "Generates and validates configuration for AI coding agents.",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new Copal project (Generate AGENTS.md + .copal/)",
    )
    init_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files when they already exist",
    )
    init_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the actions without writing to disk",
    )
    init_parser.add_argument(
        "--tools",
        help="Comma-separated list of AI adapters (e.g. claude,codex)",
    )
    init_parser.add_argument(
        "--packs",
        help="Comma-separated list of packs (e.g. engineering_loop)",
    )
    init_parser.set_defaults(handler=_handle_init)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration (manifest/packs) and artifacts",
    )
    validate_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    validate_parser.add_argument(
        "--artifacts",
        action="store_true",
        dest="check_artifacts",
        help="Validate generated artifacts against schemas",
    )
    validate_parser.add_argument(
        "--pre-task",
        action="store_true",
        help="Run pre-task validation (git status, tests)",
    )
    validate_parser.set_defaults(handler=_handle_validate)

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export agent commands to specific tools (e.g. .claude/commands/)",
    )
    export_parser.add_argument(
        "tool",
        choices=["claude", "codex", "gemini"],
        help="Target tool to export for",
    )
    export_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    export_parser.set_defaults(handler=_handle_export)

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show Copal project status and artifact summary",
    )
    status_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    status_parser.set_defaults(handler=_handle_status)

    # Next command
    next_parser = subparsers.add_parser(
        "next",
        help="Get the next task in the engineering loop",
    )
    next_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    next_parser.add_argument(
        "--id",
        help="Specific task ID to start",
    )
    next_parser.add_argument(
        "--worktree",
        action="store_true",
        help="Create a git worktree for this task",
    )
    next_parser.set_defaults(handler=_handle_next)

    # Done command
    done_parser = subparsers.add_parser(
        "done",
        help="Mark a task as done",
    )
    done_parser.add_argument(
        "id",
        nargs="?",
        help="Task ID to mark as done (default: current active task)",
    )
    done_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    done_parser.set_defaults(handler=_handle_done)

    # Worktree commands
    wt_parser = subparsers.add_parser(
        "worktree",
        aliases=["wt"],
        help="Manage git worktrees for isolated AI tasks",
    )
    wt_subparsers = wt_parser.add_subparsers(dest="worktree_command", required=True)

    wt_new_parser = wt_subparsers.add_parser("new", help="Create a new worktree")
    wt_new_parser.add_argument("name", help="Name of the worktree/task")
    wt_new_parser.add_argument("--branch", help="Branch name (defaults to name)")
    wt_new_parser.add_argument("--base", help="Base branch to checkout from")
    wt_new_parser.set_defaults(handler=worktree_new_command)

    wt_list_parser = wt_subparsers.add_parser("list", help="List worktrees")
    wt_list_parser.set_defaults(handler=worktree_list_command)

    wt_rm_parser = wt_subparsers.add_parser("remove", aliases=["rm"], help="Remove a worktree")
    wt_rm_parser.add_argument("name", help="Name of the worktree to remove")
    wt_rm_parser.add_argument("--force", "-f", action="store_true", help="Force removal")
    wt_rm_parser.set_defaults(handler=worktree_remove_command)

    # Memory commands
    memory_parser = subparsers.add_parser(
        "memory",
        help="Manage persistent workflow memories (Utility)",
    )
    memory_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    memory_subparsers = memory_parser.add_subparsers(
        dest="memory_command",
        required=True,
    )

    memory_add_parser = memory_subparsers.add_parser(
        "add",
        help="Add a new memory entry",
    )
    memory_add_parser.add_argument(
        "--type",
        required=True,
        choices=[t.value for t in MemoryType],
        help="Memory category",
    )
    memory_add_parser.add_argument(
        "--content",
        required=True,
        help="Memory content",
    )
    memory_add_parser.add_argument(
        "--id",
        help="Explicit memory identifier",
    )
    memory_add_parser.add_argument("--scope", help="Override scope identifier")
    memory_add_parser.add_argument(
        "--importance",
        type=float,
        default=0.5,
        help="Importance score between 0 and 1",
    )
    memory_add_parser.add_argument(
        "--metadata",
        action="append",
        help="Key=value metadata entries",
    )
    memory_add_parser.set_defaults(handler=memory_add_command)

    memory_search_parser = memory_subparsers.add_parser(
        "search",
        help="Search stored memories",
    )
    memory_search_parser.add_argument(
        "--query",
        required=True,
        help="Search query string",
    )
    memory_search_parser.add_argument("--scope", help="Scope filter")
    memory_search_parser.add_argument(
        "--type",
        dest="types",
        action="append",
        choices=[t.value for t in MemoryType],
        help="Filter by memory type",
    )
    memory_search_parser.set_defaults(handler=memory_search_command)

    memory_show_parser = memory_subparsers.add_parser(
        "show",
        help="Show details of a memory",
    )
    memory_show_parser.add_argument("memory_id", help="Memory identifier")
    memory_show_parser.add_argument("--scope", help="Scope filter")
    memory_show_parser.set_defaults(handler=memory_show_command)

    memory_update_parser = memory_subparsers.add_parser(
        "update",
        help="Update an existing memory",
    )
    memory_update_parser.add_argument("memory_id", help="Memory identifier")
    memory_update_parser.add_argument("--scope", help="Scope filter")
    memory_update_parser.add_argument("--content", help="Updated content")
    memory_update_parser.add_argument(
        "--importance",
        type=float,
        help="Updated importance score",
    )
    memory_update_parser.add_argument(
        "--metadata",
        action="append",
        help="Key=value metadata entries",
    )
    memory_update_parser.add_argument(
        "--type",
        choices=[t.value for t in MemoryType],
        help="Updated memory type",
    )
    memory_update_parser.set_defaults(handler=memory_update_command)

    memory_delete_parser = memory_subparsers.add_parser(
        "delete",
        help="Delete a memory entry",
    )
    memory_delete_parser.add_argument("memory_id", help="Memory identifier")
    memory_delete_parser.add_argument("--scope", help="Scope filter")
    memory_delete_parser.set_defaults(handler=memory_delete_command)


    memory_list_parser = memory_subparsers.add_parser(
        "list",
        help="List memories in the active scope",
    )
    memory_list_parser.add_argument("--scope", help="Scope filter")
    memory_list_parser.add_argument(
        "--type",
        dest="types",
        action="append",
        choices=[t.value for t in MemoryType],
        help="Filter by memory type",
    )
    memory_list_parser.set_defaults(handler=memory_list_command)

    # Skill commands
    skill_parser = subparsers.add_parser(
        "skill",
        help="Manage project skills (Claude Code integration)",
    )
    skill_subparsers = skill_parser.add_subparsers(dest="skill_command", required=True)

    skill_create_parser = skill_subparsers.add_parser(
        "create",
        help="Create a new skill from scaffold template",
    )
    skill_create_parser.add_argument(
        "name",
        help="Skill name (e.g., 'code-review', 'test-generator')",
    )
    skill_create_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    skill_create_parser.add_argument(
        "--description", "-d",
        help="Skill description",
    )
    skill_create_parser.add_argument(
        "--tags", "-t",
        help="Comma-separated tags (e.g., 'utility,testing')",
    )
    skill_create_parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive prompts",
    )
    skill_create_parser.set_defaults(handler=_handle_skill_create)

    skill_list_parser = skill_subparsers.add_parser(
        "list",
        aliases=["ls"],
        help="List all skills in the project",
    )
    skill_list_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    skill_list_parser.set_defaults(handler=_handle_skill_list)

    # System commands
    mcp_parser = subparsers.add_parser("mcp", help="Inspect Model Context Protocol configuration")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_ls_parser = mcp_subparsers.add_parser("ls", help="List MCP tools declared in .copal/mcp-available.json")
    mcp_ls_parser.add_argument("--target", default=".")

    # Resume (kept for now, but context might change)
    resume_parser = subparsers.add_parser("resume", help="Resume context (Legacy/Debug)")
    resume_parser.add_argument("--target", default=".")

    return parser


def _handle_skill_create(args: argparse.Namespace) -> int:
    tags = None
    if args.tags:
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    
    return skill_create_command(
        name=args.name,
        target=args.target,
        description=args.description,
        tags=tags,
        interactive=not getattr(args, "no_interactive", False),
    )


def _handle_skill_list(args: argparse.Namespace) -> int:
    return skill_list_command(target=args.target)


def _handle_init(args: argparse.Namespace) -> int:
    tools_arg = getattr(args, "tools", None)
    tools = [t.strip() for t in tools_arg.split(",")] if tools_arg else None

    packs_arg = getattr(args, "packs", None)
    packs = [p.strip() for p in packs_arg.split(",")] if packs_arg else None

    return harness_init_command(
        target=args.target,
        force=args.force,
        dry_run=getattr(args, "dry_run", False),
        tools=tools,
        packs=packs,
    )


def _handle_validate(args: argparse.Namespace) -> int:
    # Check if pre-task validation is requested
    if getattr(args, "pre_task", False):
        from copal_cli.harness.validate import validate_pre_task
        return validate_pre_task(target=args.target)
    
    # Use standard harness validator
    return harness_validate_command(
        target=args.target, 
        check_artifacts=getattr(args, "check_artifacts", False)
    )

def _handle_export(args: argparse.Namespace) -> int:
    return harness_export_command(
        tool=args.tool,
        target=args.target,
    )

def _handle_status(args: argparse.Namespace) -> int:
    return harness_status_command(target=args.target)


def _handle_next(args):
    from copal_cli.harness.agent_manager import AgentManager
    manager = AgentManager(Path(args.target).resolve())
    success = manager.advance_task(args.id, worktree=args.worktree)
    return 0 if success else 1

def _handle_done(args: argparse.Namespace) -> int:
    from rich.console import Console
    console = Console()
    
    manager = AgentManager(Path(args.target).resolve())
    task_id = args.id
    
    if not task_id:
        # Try to infer current task? Or just error for now.
        # Ideally manager tracks "active" task.
        # For v0.1 we require ID or find first in_progress.
        # Let's simple ask Manager to find 'in_progress' one if ID is missing.
        # But for now, let's require ID or infer from Manager.
        
        # Let's check "in_progress" items
        data = manager.load_todo()
        items = data.get("items", [])
        in_progress = [i for i in items if i.get("status") == "in_progress"]
        if len(in_progress) == 1:
            task_id = in_progress[0].get("id")
        elif len(in_progress) > 1:
             console.print("[yellow]Multiple tasks in progress. Please specify ID.[/yellow]")
             return 1
        else:
             console.print("[yellow]No active task found. Specify ID.[/yellow]")
             return 1

    if manager.complete_task(task_id):
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CoPal CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if hasattr(args, "verbose") and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    target = getattr(args, "target", ".")

    # Handlers are now set on parsers via set_defaults(handler=...)
    # for most commands.
    if hasattr(args, "handler"):
        return args.handler(args)
        
    if args.command == "mcp":
        if args.mcp_command == "ls":
            print_mcp_available(Path(target).resolve())
            return 0
    if args.command == "resume":
        print_resume_info(Path(target).resolve())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
