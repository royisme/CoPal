import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from copal_cli.worktree.sync import sync_assets

def test_sync_assets_no_source(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    dst = tmp_path / "dst"
    assert sync_assets(src, dst) is False

def test_sync_assets_success(tmp_path):
    src = tmp_path / "src"
    src_copal = src / ".copal"
    src_copal.mkdir(parents=True)
    
    (src_copal / "global").mkdir()
    (src_copal / "global" / "file.txt").write_text("content")
    (src_copal / "skills").mkdir()
    (src_copal / "memory-config.json").write_text("{}")
    
    dst = tmp_path / "dst"
    dst.mkdir()
    
    assert sync_assets(src, dst) is True
    
    dst_copal = dst / ".copal"
    assert (dst_copal / "global" / "file.txt").read_text() == "content"
    assert (dst_copal / "memory-config.json").exists()
    assert (dst_copal / "runtime").exists()
    assert (dst_copal / "memory").exists()

def test_sync_assets_failure(tmp_path):
    src = tmp_path / "src"
    src_copal = src / ".copal"
    src_copal.mkdir(parents=True)
    
    dst = tmp_path / "dst"
    
    # Mock shutil.copytree to fail
    with patch("copal_cli.worktree.sync._copy_dir", side_effect=Exception("Copy failed")):
        assert sync_assets(src, dst) is False
