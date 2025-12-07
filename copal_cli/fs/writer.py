from __future__ import annotations

import os
import tempfile
import shutil
from pathlib import Path
from typing import Union

def atomic_write(path: Path, content: Union[str, bytes], encoding: str = "utf-8", overwrite: bool = True) -> bool:
    """
    Write content to a file atomically.
    First writes to a temporary file, then renames it to the target path.
    
    Args:
        path: Target file path.
        content: String or bytes to write.
        encoding: Encoding validation for string content.
        overwrite: If False, raise FileExistsError if file exists.
        
    Returns:
        True if written successfully.
    """
    if not overwrite and path.exists():
        raise FileExistsError(f"File already exists: {path}")
        
    # Ensure parent dir exists
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file in the same directory to ensure atomic rename
    # (os.rename is atomic only on same filesystem)
    fd, temp_path = tempfile.mkstemp(dir=path.parent, text=isinstance(content, str))
    
    try:
        with os.fdopen(fd, 'w' if isinstance(content, str) else 'wb') as f:
            f.write(content)
        
        # Atomic rename
        os.replace(temp_path, path)
        return True
    except Exception:
        # Cleanup temp file on failure
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
