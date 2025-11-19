import shutil
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

def sync_assets(source_root: Path, target_root: Path) -> bool:
    """
    Sync CoPal assets from source repo to target worktree.
    Copies .copal/global, .copal/skills, and config files.
    Initializes empty .copal/runtime.
    """
    source_copal = source_root / ".copal"
    target_copal = target_root / ".copal"
    
    if not source_copal.exists():
        logger.warning(f"No .copal directory found in {source_root}")
        return False
        
    try:
        # Create target .copal directory
        target_copal.mkdir(parents=True, exist_ok=True)
        
        # 1. Copy Global Knowledge Base
        _copy_dir(source_copal / "global", target_copal / "global")
        
        # 2. Copy Skills
        _copy_dir(source_copal / "skills", target_copal / "skills")
        
        # 3. Copy Config Files
        _copy_file(source_copal / "memory-config.json", target_copal / "memory-config.json")
        _copy_file(source_copal / "mcp-available.json", target_copal / "mcp-available.json")
        
        # 4. Initialize Runtime (Empty)
        (target_copal / "runtime").mkdir(exist_ok=True)
        
        # 5. Initialize Memory (Empty directory structure if needed, but config is copied)
        # We generally want fresh memory for a new task, or maybe shared?
        # For now, we start fresh as per "One Task, One Workspace" philosophy.
        (target_copal / "memory").mkdir(exist_ok=True)
        
        logger.info(f"Successfully synced CoPal assets to {target_root}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to sync assets: {e}")
        return False

def _copy_dir(src: Path, dst: Path):
    """Copy directory if it exists."""
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        logger.debug(f"Copied {src} to {dst}")

def _copy_file(src: Path, dst: Path):
    """Copy file if it exists."""
    if src.exists():
        shutil.copy2(src, dst)
        logger.debug(f"Copied {src} to {dst}")
