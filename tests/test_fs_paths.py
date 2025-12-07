from pathlib import Path
import pytest
from copal_cli.fs.paths import safe_path_join, normalize_path

def test_safe_path_join_valid(tmp_path):
    base = tmp_path
    result = safe_path_join(base, "foo", "bar.txt")
    expected = base / "foo" / "bar.txt"
    assert result == expected

def test_safe_path_join_traversal_attempt(tmp_path):
    base = tmp_path
    with pytest.raises(ValueError, match="Path traversal detected"):
        safe_path_join(base, "..", "etc", "passwd")

def test_safe_path_join_absolute_traversal(tmp_path):
    base = tmp_path
    with pytest.raises(ValueError, match="Path traversal detected"):
        safe_path_join(base, "/etc/passwd")

def test_normalize_path():
    p = normalize_path("foo/bar")
    assert isinstance(p, Path)
    assert p.is_absolute()
