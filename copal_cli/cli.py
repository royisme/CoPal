from __future__ import annotations

import argparse
import logging
import sys

from .init import init_command
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
    parser = argparse.ArgumentParser(prog="copal", description="CoPal CLI - 初始化与维护 AI 编码指引模板")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="将 CoPal 模板复制到目标仓库")
    init_parser.add_argument("--target", default=".", help="目标仓库路径（默认当前目录）")
    init_parser.add_argument("--force", action="store_true", help="覆盖已存在的模板文件")
    init_parser.add_argument("--dry-run", action="store_true", help="预览将要执行的操作，不实际写入文件")
    init_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

    validate_parser = subparsers.add_parser("validate", help="验证知识库文件的 YAML front matter")
    validate_parser.add_argument("--target", default=".copal/global", help="目标目录路径（默认 .copal/global）")
    validate_parser.add_argument("--pattern", default="**/*.md", help="文件匹配模式（默认 **/*.md）")
    validate_parser.add_argument("--verbose", "-v", action="store_true", help="显示详细日志")

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

    if args.command == "init":
        return init_command(
            target=args.target,
            force=args.force,
            dry_run=getattr(args, 'dry_run', False)
        )
    elif args.command == "validate":
        return validate_command(
            target=args.target,
            pattern=args.pattern
        )

    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
