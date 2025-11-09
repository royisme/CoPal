from __future__ import annotations

import argparse
import logging
import sys

from .init import init_command
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
    init_parser.set_defaults(handler=_handle_init)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="验证知识库文件的 YAML front matter")
    validate_parser.add_argument("--target", default=".copal/global", help="目标目录路径（默认 .copal/global）")
    validate_parser.add_argument("--pattern", default="**/*.md", help="文件匹配模式（默认 **/*.md）")
    validate_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    validate_parser.set_defaults(handler=_handle_validate)

    skill_parser = subparsers.add_parser("skill", help="管理技能注册表与执行")
    skill_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    skill_subparsers = skill_parser.add_subparsers(dest="skill_command", required=True)

    registry_parser = skill_subparsers.add_parser("registry", help="技能注册表相关操作")
    registry_subparsers = registry_parser.add_subparsers(dest="skill_registry_command", required=True)

    registry_build_parser = registry_subparsers.add_parser("build", help="构建技能注册表")
    registry_build_parser.add_argument(
        "--skills-root", default=".copal/skills", help="技能根目录（默认 .copal/skills）"
    )
    registry_build_parser.set_defaults(handler=skill_registry_build_command)

    registry_list_parser = registry_subparsers.add_parser("list", help="列出注册表中的技能")
    registry_list_parser.add_argument(
        "--skills-root", default=".copal/skills", help="技能根目录（默认 .copal/skills）"
    )
    registry_list_parser.add_argument("--lang", help="按语言过滤技能")
    registry_list_parser.set_defaults(handler=skill_registry_list_command)

    search_parser = skill_subparsers.add_parser("search", help="根据查询关键字搜索技能")
    search_parser.add_argument(
        "--skills-root", default=".copal/skills", help="技能根目录（默认 .copal/skills）"
    )
    search_parser.add_argument("--query", required=True, help="搜索关键词")
    search_parser.add_argument("--lang", help="按语言过滤技能")
    search_parser.set_defaults(handler=skill_search_command)

    scaffold_parser = skill_subparsers.add_parser("scaffold", help="创建新的技能模板")
    scaffold_parser.add_argument("name", help="技能名称")
    scaffold_parser.add_argument(
        "--skills-root", default=".copal/skills", help="技能根目录（默认 .copal/skills）"
    )
    scaffold_parser.add_argument("--lang", default="python", help="技能使用的语言（默认 python）")
    scaffold_parser.add_argument("--description", help="技能描述")
    scaffold_parser.set_defaults(handler=skill_scaffold_command)

    exec_parser = skill_subparsers.add_parser("exec", help="执行指定技能")
    exec_parser.add_argument(
        "--skills-root", default=".copal/skills", help="技能根目录（默认 .copal/skills）"
    )
    exec_parser.add_argument("--skill", required=True, help="要执行的技能名称")
    exec_parser.add_argument("--lang", help="校验技能语言")
    exec_parser.add_argument("--sandbox", action="store_true", help="在沙箱模式下运行技能")
    exec_parser.set_defaults(handler=skill_exec_command)

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
