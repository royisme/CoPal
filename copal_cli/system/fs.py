"""File system utilities for CoPal CLI."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_runtime_dirs(target_root: Path) -> tuple[Path, Path]:
    """Ensure .copal/runtime and .copal/artifacts directories exist.

    Args:
        target_root: Root directory of the target repository.

    Returns:
        tuple[Path, Path]: Paths to runtime and artifacts directories.
    """
    runtime_dir = target_root / ".copal" / "runtime"
    artifacts_dir = target_root / ".copal" / "artifacts"

    runtime_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f"Runtime directory: {runtime_dir}")
    logger.debug(f"Artifacts directory: {artifacts_dir}")

    return runtime_dir, artifacts_dir


def read_text(path: Path) -> str:
    """Read text content from a file.

    Args:
        path: Path to the file to read.

    Returns:
        str: Content of the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding='utf-8')


def write_text(path: Path, content: str) -> None:
    """Write text content to a file.

    Args:
        path: Path to the file to write.
        content: Content to write to the file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    logger.debug(f"Wrote file: {path}")
