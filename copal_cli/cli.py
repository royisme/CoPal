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
    parser = argparse.ArgumentParser(
        prog="copal", description="CoPal CLI - 初始化与维护 AI 编码指引模板"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="将 CoPal 模板复制到目标仓库")
    init_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    init_parser.add_argument("--force", action="store_true", help="覆盖已存在的模板文件")
    init_parser.add_argument("--dry-run", action="store_true", help="预览将要执行的操作，不实际写入文件")
    init_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")
    init_parser.set_defaults(handler=_handle_init)

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

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


def _handle_init(args: argparse.Namespace) -> int:
    return init_command(
        target=args.target,
        force=args.force,
        dry_run=getattr(args, "dry_run", False),
    )


def _handle_validate(args: argparse.Namespace) -> int:
    return validate_command(
        target=args.target,
        pattern=args.pattern,
    )


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
