from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .init import init_command
from .memory.cli_commands import (
    memory_add_command,
    memory_delete_command,
    memory_list_command,
    memory_search_command,
    memory_show_command,
    memory_summary_command,
    memory_supersede_command,
    memory_update_command,
)
from .memory.models import MemoryType
from .skills.commands import (
    exec_command as skill_exec_command,
    registry_build_command as skill_registry_build_command,
    registry_list_command as skill_registry_list_command,
    scaffold_command as skill_scaffold_command,
    search_command as skill_search_command,
)
from .validator import validate_command
from .stages import (
    analyze_command,
    spec_command,
    plan_command,
    implement_command,
    review_command,
    commit_command,
)
from .system.mcp import print_mcp_available
from .system.status import print_status
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
        description="CoPal CLI - AI coding workflow orchestrator",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Copy CoPal templates into the target repository",
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
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )
    init_parser.set_defaults(handler=_handle_init)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate knowledge base files for required YAML front matter",
    )
    validate_parser.add_argument(
        "--target",
        default=".copal/global",
        help="Directory to validate (default: .copal/global)",
    )
    validate_parser.add_argument(
        "--pattern",
        default="**/*.md",
        help="Glob pattern to select files (default: **/*.md)",
    )
    validate_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )
    validate_parser.set_defaults(handler=_handle_validate)

    # Skill commands
    skill_parser = subparsers.add_parser(
        "skill",
        help="Manage reusable skills",
    )
    skill_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )
    skill_subparsers = skill_parser.add_subparsers(dest="skill_command", required=True)

    registry_parser = skill_subparsers.add_parser(
        "registry",
        help="Build or inspect the skill registry",
    )
    registry_subparsers = registry_parser.add_subparsers(
        dest="skill_registry_command",
        required=True,
    )

    registry_build_parser = registry_subparsers.add_parser(
        "build",
        help="Scan the skills directory and rebuild registry.json",
    )
    registry_build_parser.add_argument(
        "--skills-root",
        default=".copal/skills",
        help="Skills root directory (default: .copal/skills)",
    )
    registry_build_parser.set_defaults(handler=skill_registry_build_command)

    registry_list_parser = registry_subparsers.add_parser(
        "list",
        help="List skills from registry.json",
    )
    registry_list_parser.add_argument(
        "--skills-root",
        default=".copal/skills",
        help="Skills root directory (default: .copal/skills)",
    )
    registry_list_parser.add_argument(
        "--lang",
        help="Filter results by programming language",
    )
    registry_list_parser.set_defaults(handler=skill_registry_list_command)

    search_parser = skill_subparsers.add_parser(
        "search",
        help="Search skills by keyword",
    )
    search_parser.add_argument(
        "--skills-root",
        default=".copal/skills",
        help="Skills root directory (default: .copal/skills)",
    )
    search_parser.add_argument(
        "--query",
        required=True,
        help="Search query",
    )
    search_parser.add_argument(
        "--lang",
        help="Filter results by programming language",
    )
    search_parser.set_defaults(handler=skill_search_command)

    scaffold_parser = skill_subparsers.add_parser(
        "scaffold",
        help="Create a new skill skeleton",
    )
    scaffold_parser.add_argument("name", help="Skill name")
    scaffold_parser.add_argument(
        "--skills-root",
        default=".copal/skills",
        help="Skills root directory (default: .copal/skills)",
    )
    scaffold_parser.add_argument(
        "--lang",
        default="python",
        help="Programming language for the skill (default: python)",
    )
    scaffold_parser.add_argument(
        "--description",
        help="Skill description",
    )
    scaffold_parser.set_defaults(handler=skill_scaffold_command)

    exec_parser = skill_subparsers.add_parser(
        "exec",
        help="Stream a skill's entrypoint to stdout",
    )
    exec_parser.add_argument(
        "--skills-root",
        default=".copal/skills",
        help="Skills root directory (default: .copal/skills)",
    )
    exec_parser.add_argument(
        "--skill",
        required=True,
        help="Skill name to execute",
    )
    exec_parser.add_argument(
        "--lang",
        help="Validate the expected language of the skill",
    )
    exec_parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Acknowledge sandbox requirement when a skill demands it",
    )
    exec_parser.set_defaults(handler=skill_exec_command)

    # Memory commands
    memory_parser = subparsers.add_parser(
        "memory",
        help="Manage persistent workflow memories",
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

    memory_supersede_parser = memory_subparsers.add_parser(
        "supersede",
        help="Create a memory that supersedes another",
    )
    memory_supersede_parser.add_argument("old_memory_id", help="Existing memory ID")
    memory_supersede_parser.add_argument(
        "--type",
        required=True,
        choices=[t.value for t in MemoryType],
        help="Type of the new memory",
    )
    memory_supersede_parser.add_argument(
        "--content",
        required=True,
        help="Content of the new memory",
    )
    memory_supersede_parser.add_argument("--scope", help="Scope override")
    memory_supersede_parser.add_argument(
        "--importance",
        type=float,
        default=0.5,
        help="Importance score of the new memory",
    )
    memory_supersede_parser.add_argument(
        "--reason",
        help="Reason the previous memory is superseded",
    )
    memory_supersede_parser.add_argument(
        "--metadata",
        action="append",
        help="Key=value metadata entries",
    )
    memory_supersede_parser.set_defaults(handler=memory_supersede_command)

    memory_summary_parser = memory_subparsers.add_parser(
        "summary",
        help="Summarise memories for the scope",
    )
    memory_summary_parser.add_argument("--scope", help="Scope filter")
    memory_summary_parser.set_defaults(handler=memory_summary_command)

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

    # Stage commands
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analysis stage – understand the task and gather context",
    )
    analyze_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    analyze_parser.add_argument("--title", help="Optional task title")
    analyze_parser.add_argument("--goals", help="Optional task goals")
    analyze_parser.add_argument(
        "--constraints",
        help="Optional task constraints",
    )
    analyze_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    spec_parser = subparsers.add_parser(
        "spec",
        help="Specification stage – write a formal task specification",
    )
    spec_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    spec_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    plan_parser = subparsers.add_parser(
        "plan",
        help="Planning stage – produce an executable plan",
    )
    plan_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    plan_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    implement_parser = subparsers.add_parser(
        "implement",
        help="Implementation stage – capture patch notes and guidance",
    )
    implement_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    implement_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    review_parser = subparsers.add_parser(
        "review",
        help="Review stage – assess quality and draft PR notes",
    )
    review_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    review_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    commit_parser = subparsers.add_parser(
        "commit",
        help="Commit stage – record workflow metadata",
    )
    commit_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )
    commit_parser.add_argument("--task-id", help="Optional task identifier")
    commit_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging output",
    )

    # System commands
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="Inspect Model Context Protocol configuration",
    )
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_ls_parser = mcp_subparsers.add_parser(
        "ls",
        help="List MCP tools declared in .copal/mcp-available.json",
    )
    mcp_ls_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Show workflow status, prompts, and artifacts",
    )
    status_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )

    resume_parser = subparsers.add_parser(
        "resume",
        help="Resume from the most recent generated prompt",
    )
    resume_parser.add_argument(
        "--target",
        default=".",
        help="Target repository path (default: current directory)",
    )

    return parser


def _handle_init(args: argparse.Namespace) -> int:
    return init_command(
        target=args.target,
        force=args.force,
        dry_run=getattr(args, "dry_run", False),
    )


def _handle_validate(args: argparse.Namespace) -> int:
    return validate_command(target=args.target, pattern=args.pattern)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CoPal CLI."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if hasattr(args, "verbose") and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    target = getattr(args, "target", ".")

    if args.command == "init":
        return args.handler(args)
    if args.command == "validate":
        return args.handler(args)
    if args.command == "skill":
        return args.handler(args)
    if args.command == "memory":
        return args.handler(args)
    if args.command == "analyze":
        return analyze_command(
            target=target,
            title=getattr(args, "title", None),
            goals=getattr(args, "goals", None),
            constraints=getattr(args, "constraints", None),
        )
    if args.command == "spec":
        return spec_command(target=target)
    if args.command == "plan":
        return plan_command(target=target)
    if args.command == "implement":
        return implement_command(target=target)
    if args.command == "review":
        return review_command(target=target)
    if args.command == "commit":
        return commit_command(target=target, task_id=getattr(args, "task_id", None))
    if args.command == "mcp":
        if args.mcp_command == "ls":
            print_mcp_available(Path(target).resolve())
            return 0
    if args.command == "status":
        print_status(Path(target).resolve())
        return 0
    if args.command == "resume":
        print_resume_info(Path(target).resolve())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
