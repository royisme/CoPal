from __future__ import annotations

import argparse
import logging
import sys

from .init import init_command
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
    """Build and configure the argument parser for CoPal CLI.

    Returns:
        argparse.ArgumentParser: Configured parser with subcommands.
    """
    parser = argparse.ArgumentParser(prog="copal", description="CoPal CLI - AI 编码工作流管理工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Init command
    init_parser = subparsers.add_parser("init", help="将 CoPal 模板复制到目标仓库")
    init_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    init_parser.add_argument("--force", action="store_true", help="覆盖已存在的模板文件")
    init_parser.add_argument("--dry-run", action="store_true", help="预览将要执行的操作，不实际写入文件")
    init_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="验证知识库文件的 YAML front matter")
    validate_parser.add_argument("--target", default=".copal/global", help="目标目录路径（默认 .copal/global）")
    validate_parser.add_argument("--pattern", default="**/*.md", help="文件匹配模式（默认 **/*.md）")
    validate_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    # Stage commands
    analyze_parser = subparsers.add_parser("analyze", help="分析阶段 - 理解问题和收集信息")
    analyze_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    analyze_parser.add_argument("--title", help="任务标题")
    analyze_parser.add_argument("--goals", help="任务目标")
    analyze_parser.add_argument("--constraints", help="约束条件")
    analyze_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    spec_parser = subparsers.add_parser("spec", help="规格阶段 - 形成任务说明书")
    spec_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    spec_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    plan_parser = subparsers.add_parser("plan", help="计划阶段 - 制定可执行计划")
    plan_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    plan_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    implement_parser = subparsers.add_parser("implement", help="实施阶段 - 产出补丁和修改建议")
    implement_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    implement_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    review_parser = subparsers.add_parser("review", help="审查阶段 - 评估质量和生成 PR")
    review_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    review_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    commit_parser = subparsers.add_parser("commit", help="提交阶段 - 记录工作流元数据")
    commit_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    commit_parser.add_argument("--task-id", help="任务标识符")
    commit_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    # System commands
    mcp_parser = subparsers.add_parser("mcp", help="MCP 工具管理")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", required=True)
    mcp_ls_parser = mcp_subparsers.add_parser("ls", help="列出可用的 MCP 工具")
    mcp_ls_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")

    status_parser = subparsers.add_parser("status", help="显示当前工作流状态")
    status_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")

    resume_parser = subparsers.add_parser("resume", help="恢复中断的工作流")
    resume_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CoPal CLI.

    Args:
        argv: Command-line arguments. If None, uses sys.argv.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    # Configure logging level
    if hasattr(args, 'verbose') and args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Get target path (most commands use it)
    target = getattr(args, 'target', '.')

    # Route to appropriate command
    if args.command == "init":
        return init_command(
            target=target,
            force=args.force,
            dry_run=getattr(args, 'dry_run', False)
        )
    elif args.command == "validate":
        return validate_command(
            target=args.target,
            pattern=args.pattern
        )
    elif args.command == "analyze":
        return analyze_command(
            target=target,
            title=getattr(args, 'title', None),
            goals=getattr(args, 'goals', None),
            constraints=getattr(args, 'constraints', None)
        )
    elif args.command == "spec":
        return spec_command(target=target)
    elif args.command == "plan":
        return plan_command(target=target)
    elif args.command == "implement":
        return implement_command(target=target)
    elif args.command == "review":
        return review_command(target=target)
    elif args.command == "commit":
        return commit_command(
            target=target,
            task_id=getattr(args, 'task_id', None)
        )
    elif args.command == "mcp":
        if args.mcp_command == "ls":
            from pathlib import Path
            print_mcp_available(Path(target).resolve())
            return 0
    elif args.command == "status":
        from pathlib import Path
        print_status(Path(target).resolve())
        return 0
    elif args.command == "resume":
        from pathlib import Path
        print_resume_info(Path(target).resolve())
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
