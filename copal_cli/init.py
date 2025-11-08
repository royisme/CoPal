from __future__ import annotations

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

PACKAGE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = PACKAGE_DIR / "templates" / "base"


def _copy(src: Path, dst: Path, force: bool, dry_run: bool = False) -> bool:
    """Copy a file or directory from source to destination.

    Args:
        src: Source path (file or directory).
        dst: Destination path.
        force: If True, overwrite existing files/directories.
        dry_run: If True, only log what would be done without actual copying.

    Returns:
        bool: True if file would be/was copied, False if skipped.
    """
    if dst.exists():
        if not force:
            logger.debug(f"跳过（已存在）: {dst}")
            return False
        logger.info(f"覆盖: {dst}")
        if not dry_run:
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
    else:
        logger.info(f"创建: {dst}")

    if dry_run:
        return True

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return True


def init_command(*, target: str, force: bool, dry_run: bool = False) -> int:
    """Initialize CoPal templates in the target repository.

    Args:
        target: Target repository path (absolute or relative).
        force: If True, overwrite existing files.
        dry_run: If True, preview changes without writing files.

    Returns:
        int: Exit code (0 for success, 1 for failure).

    Raises:
        SystemExit: If target path does not exist.
    """
    target_root = Path(target).resolve()
    if not target_root.exists():
        logger.error(f"目标路径不存在: {target_root}")
        raise SystemExit(f"目标路径不存在: {target_root}")

    if dry_run:
        logger.info(f"[预览模式] 将要安装到: {target_root}")
    else:
        logger.info(f"开始安装 CoPal 模板到: {target_root}")

    files_to_copy = [
        (TEMPLATE_DIR / "AGENTS.md", target_root / "AGENTS.md"),
        (TEMPLATE_DIR / "UserAgents.md", target_root / "UserAgents.md"),
        (TEMPLATE_DIR / ".copal" / "global", target_root / ".copal" / "global"),
    ]

    copied_count = 0
    for src, dst in files_to_copy:
        if _copy(src, dst, force, dry_run):
            copied_count += 1

    if dry_run:
        logger.info(f"[预览模式] 将创建/覆盖 {copied_count} 个文件/目录")
        logger.info("运行时不带 --dry-run 参数以执行实际操作")
    else:
        logger.info(f"✓ CoPal 模板已成功安装到 {target_root}")
        logger.info(
            "请在 `AGENTS.md` 的“项目自定义”列补充链接，并编辑 `UserAgents.md` 填写项目专属内容。"
        )

    return 0
