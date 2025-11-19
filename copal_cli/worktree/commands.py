import argparse
import logging
import os
from pathlib import Path
from typing import Optional

from .git_utils import worktree_add, worktree_list, worktree_remove, get_repo_root
from .sync import sync_assets

logger = logging.getLogger(__name__)

def handle_new(args: argparse.Namespace) -> int:
    """Handle 'copal worktree new' command."""
    cwd = Path(os.getcwd())
    repo_root = get_repo_root(cwd)
    
    if not repo_root:
        logger.error("Not inside a git repository.")
        return 1
        
    name = args.name
    branch = args.branch or name
    base = args.base
    
    # Strategy: Create worktrees in a sibling directory "../{repo_name}.wt/{name}"
    # This keeps the main repo clean and avoids nesting issues.
    repo_name = repo_root.name
    wt_root = repo_root.parent / f"{repo_name}.wt"
    target_path = wt_root / name
    
    if target_path.exists():
        logger.error(f"Worktree path already exists: {target_path}")
        return 1
        
    # 1. Create Worktree
    logger.info(f"Creating worktree '{name}' at {target_path}...")
    if not worktree_add(repo_root, target_path, branch, base):
        return 1
        
    # 2. Sync Assets
    logger.info("Syncing CoPal assets...")
    if not sync_assets(repo_root, target_path):
        logger.warning("Failed to sync some assets. You may need to run 'copal init' manually in the new worktree.")
        
    logger.info(f"Successfully created worktree '{name}'!")
    logger.info(f"To switch to it: cd {target_path}")
    
    return 0

def handle_list(args: argparse.Namespace) -> int:
    """Handle 'copal worktree list' command."""
    cwd = Path(os.getcwd())
    worktrees = worktree_list(cwd)
    
    if not worktrees:
        logger.info("No worktrees found.")
        return 0
        
    print(f"{'PATH':<60} {'BRANCH':<30} {'HEAD':<10}")
    print("-" * 100)
    
    for path, head, branch in worktrees:
        print(f"{path:<60} {branch:<30} {head[:7]:<10}")
        
    return 0

def handle_remove(args: argparse.Namespace) -> int:
    """Handle 'copal worktree remove' command."""
    cwd = Path(os.getcwd())
    repo_root = get_repo_root(cwd)
    
    if not repo_root:
        logger.error("Not inside a git repository.")
        return 1
        
    name = args.name
    force = args.force
    
    # Try to find the worktree path
    # 1. Check if name is a full path
    target_path = Path(name)
    if not target_path.is_absolute():
        # 2. Check default location
        repo_name = repo_root.name
        wt_root = repo_root.parent / f"{repo_name}.wt"
        target_path = wt_root / name
    
    if not target_path.exists():
        logger.error(f"Worktree path not found: {target_path}")
        # Fallback: try to find by branch name matching the directory name?
        # For now, strict path matching based on our convention.
        return 1
        
    if not worktree_remove(repo_root, target_path, force):
        return 1
        
    logger.info(f"Removed worktree '{name}'")
    return 0
