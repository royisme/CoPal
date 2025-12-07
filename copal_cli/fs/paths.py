from __future__ import annotations

import os
from pathlib import Path

def safe_path_join(base_dir: Path, *paths: str) -> Path:
    """
    Safely join a base directory with one or more path components.
    Ensures that the resulting path is strictly within the base directory.
    
    Args:
        base_dir: The trusted base directory.
        *paths: Path components to join.
        
    Returns:
        The resolved absolute path.
        
    Raises:
        ValueError: If the resulting path attempts to escape the base directory.
    """
    base_dir = base_dir.resolve()
    # Join all components
    final_path = base_dir.joinpath(*paths).resolve()
    
    # Check if the final path is relative to base_dir
    # This prevents directory traversal attacks like "../../../etc/passwd"
    try:
        final_path.relative_to(base_dir)
    except ValueError:
        raise ValueError(f"Path traversal detected: {final_path} is not within {base_dir}")
        
    return final_path

def normalize_path(path_str: str) -> Path:
    """Convert string path to resolved Path object."""
    return Path(path_str).resolve()
