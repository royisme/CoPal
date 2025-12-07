from pathlib import Path
import pytest
from copal_cli.fs.writer import atomic_write

def test_atomic_write_new_file(tmp_path):
    target = tmp_path / "foo.txt"
    content = "hello world"
    atomic_write(target, content)
    assert target.exists()
    assert target.read_text() == content

def test_atomic_write_overwrite(tmp_path):
    target = tmp_path / "foo.txt"
    target.write_text("old")
    
    atomic_write(target, "new", overwrite=True)
    assert target.read_text() == "new"

def test_atomic_write_no_overwrite(tmp_path):
    target = tmp_path / "foo.txt"
    target.write_text("old")
    
    with pytest.raises(FileExistsError):
        atomic_write(target, "new", overwrite=False)
    
    assert target.read_text() == "old"

def test_atomic_write_bytes(tmp_path):
    target = tmp_path / "foo.bin"
    content = b"hello bytes"
    atomic_write(target, content)
    assert target.read_bytes() == content

def test_atomic_write_creates_parents(tmp_path):
    target = tmp_path / "dir" / "subdir" / "foo.txt"
    atomic_write(target, "content")
    assert target.exists()
