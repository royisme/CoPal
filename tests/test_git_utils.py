import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from copal_cli.worktree.git_utils import get_repo_root, worktree_add, worktree_list, worktree_remove, worktree_prune, _run_git

def test_run_git_success(tmp_path):
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "output"
        mock_run.return_value.stderr = ""
        
        code, out, err = _run_git(["status"], tmp_path)
        assert code == 0
        assert out == "output"

def test_run_git_exception(tmp_path):
    with patch("subprocess.run", side_effect=Exception("boom")):
        code, out, err = _run_git(["status"], tmp_path)
        assert code == -1
        assert "boom" in err

def test_get_repo_root(tmp_path):
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(0, "/root", "")):
        assert get_repo_root(tmp_path) == Path("/root")
        
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(1, "", "")):
        assert get_repo_root(tmp_path) is None

def test_worktree_add(tmp_path):
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(0, "", "")):
        assert worktree_add(tmp_path, Path("/wt"), "branch") is True
        
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(1, "", "err")):
        assert worktree_add(tmp_path, Path("/wt"), "branch") is False

def test_worktree_list(tmp_path):
    output = """worktree /path/1
HEAD 123
branch refs/heads/b1

worktree /path/2
HEAD 456
branch refs/heads/b2
"""
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(0, output, "")):
        wts = worktree_list(tmp_path)
        assert len(wts) == 2
        assert wts[0] == ("/path/1", "123", "b1")

    with patch("copal_cli.worktree.git_utils._run_git", return_value=(1, "", "err")):
        assert worktree_list(tmp_path) == []

def test_worktree_remove(tmp_path):
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(0, "", "")):
        assert worktree_remove(tmp_path, Path("/wt")) is True
        
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(1, "", "err")):
        assert worktree_remove(tmp_path, Path("/wt")) is False

def test_worktree_prune(tmp_path):
    with patch("copal_cli.worktree.git_utils._run_git", return_value=(0, "", "")):
        assert worktree_prune(tmp_path) is True
