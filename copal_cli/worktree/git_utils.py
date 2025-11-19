import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

def _run_git(args: List[str], cwd: Path) -> Tuple[int, str, str]:
    """Run a git command and return returncode, stdout, stderr."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def get_repo_root(cwd: Path) -> Optional[Path]:
    """Get the root directory of the git repository."""
    code, out, _ = _run_git(["rev-parse", "--show-toplevel"], cwd)
    if code == 0:
        return Path(out.strip())
    return None

def worktree_add(cwd: Path, path: Path, branch: str, base_branch: Optional[str] = None) -> bool:
    """Create a new worktree."""
    # Use -b to create the branch
    cmd = ["worktree", "add", "-b", branch, str(path)]
    if base_branch:
        cmd.append(base_branch)
    
    logger.info(f"Creating worktree at {path} for branch {branch}")
    code, out, err = _run_git(cmd, cwd)
    
    if code != 0:
        logger.error(f"Failed to create worktree: {err}")
        return False
    return True

def worktree_list(cwd: Path) -> List[Tuple[str, str, str]]:
    """List worktrees. Returns list of (path, head_sha, branch)."""
    code, out, err = _run_git(["worktree", "list", "--porcelain"], cwd)
    if code != 0:
        logger.error(f"Failed to list worktrees: {err}")
        return []

    worktrees = []
    current_wt = {}
    
    for line in out.splitlines():
        if not line:
            if current_wt:
                worktrees.append(current_wt)
                current_wt = {}
            continue
            
        if line.startswith("worktree "):
            current_wt["path"] = line[9:].strip()
        elif line.startswith("HEAD "):
            current_wt["head"] = line[5:].strip()
        elif line.startswith("branch "):
            current_wt["branch"] = line[7:].strip()
            
    if current_wt:
        worktrees.append(current_wt)
        
    # Convert to tuple format for easier consumption
    return [
        (
            wt.get("path", ""),
            wt.get("head", ""),
            wt.get("branch", "").replace("refs/heads/", "")
        )
        for wt in worktrees
        if "path" in wt
    ]

def worktree_remove(cwd: Path, path: Path, force: bool = False) -> bool:
    """Remove a worktree."""
    cmd = ["worktree", "remove", str(path)]
    if force:
        cmd.append("--force")
        
    logger.info(f"Removing worktree at {path}")
    code, out, err = _run_git(cmd, cwd)
    
    if code != 0:
        logger.error(f"Failed to remove worktree: {err}")
        return False
    return True

def worktree_prune(cwd: Path) -> bool:
    """Prune worktree information."""
    code, out, err = _run_git(["worktree", "prune"], cwd)
    return code == 0
