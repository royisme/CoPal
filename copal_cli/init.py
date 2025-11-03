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
            logger.debug(f"Skipped (already exists): {dst}")
            return False
        logger.info(f"Overwriting: {dst}")
        if not dry_run:
            if dst.is_dir():
                shutil.rmtree(dst)
            else:
                dst.unlink()
    else:
        logger.info(f"Creating: {dst}")

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
        logger.error(f"Target path does not exist: {target_root}")
        raise SystemExit(f"Target path does not exist: {target_root}")

    if dry_run:
        logger.info(f"[Dry-run mode] Installing to: {target_root}")
    else:
        logger.info(f"Installing CoPal templates to: {target_root}")

    files_to_copy = [
        (TEMPLATE_DIR / "AGENTS.md", target_root / "AGENTS.md"),
        (TEMPLATE_DIR / "UserAgents.md", target_root / "UserAgents.md"),
        (TEMPLATE_DIR / ".copal" / "global", target_root / ".copal" / "global"),
        (TEMPLATE_DIR / ".copal" / "hooks", target_root / ".copal" / "hooks"),
        (TEMPLATE_DIR / ".copal" / "mcp-available.json", target_root / ".copal" / "mcp-available.json"),
    ]

    copied_count = 0
    for src, dst in files_to_copy:
        if _copy(src, dst, force, dry_run):
            copied_count += 1

    if dry_run:
        logger.info(f"[Dry-run mode] Would create/overwrite {copied_count} files/directories")
        logger.info("Run without --dry-run to perform actual operation")
    else:
        logger.info(f"✓ CoPal templates successfully installed to {target_root}")
        logger.info("Please update AGENTS.md 'Project Customization' section and edit UserAgents.md with project-specific content.")

    return 0
