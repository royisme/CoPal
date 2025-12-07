import pytest
from unittest.mock import MagicMock, patch
from argparse import Namespace
from pathlib import Path
from copal_cli.worktree.commands import handle_new, handle_list, handle_remove

@pytest.fixture
def mock_git():
    with patch("copal_cli.worktree.commands.get_repo_root") as mock_root, \
         patch("copal_cli.worktree.commands.worktree_add") as mock_add, \
         patch("copal_cli.worktree.commands.worktree_list") as mock_list, \
         patch("copal_cli.worktree.commands.worktree_remove") as mock_remove, \
         patch("copal_cli.worktree.commands.sync_assets") as mock_sync:
         
        yield mock_root, mock_add, mock_list, mock_remove, mock_sync

def test_handle_new_success(tmp_path, mock_git):
    mock_root, mock_add, _, _, mock_sync = mock_git
    mock_root.return_value = tmp_path / "repo"
    mock_add.return_value = True
    mock_sync.return_value = True
    
    # We mock cwd context for the command
    with patch("os.getcwd", return_value=str(tmp_path / "repo")):
        args = Namespace(name="feat", branch=None, base=None)
        ret = handle_new(args)
        assert ret == 0
        mock_add.assert_called_once()
        mock_sync.assert_called_once()

def test_handle_new_no_repo(tmp_path, mock_git):
    mock_root, _, _, _, _ = mock_git
    mock_root.return_value = None
    
    with patch("os.getcwd", return_value=str(tmp_path)):
        args = Namespace(name="feat", branch=None, base=None)
        assert handle_new(args) == 1

def test_handle_list(tmp_path, mock_git, capsys):
    _, _, mock_list, _, _ = mock_git
    mock_list.return_value = [("/path/to/wt", "HEAD", "branch1")]
    
    with patch("os.getcwd", return_value=str(tmp_path)):
        ret = handle_list(Namespace())
        assert ret == 0
        assert "branch1" in capsys.readouterr().out

def test_handle_remove(tmp_path, mock_git):
    mock_root, _, _, mock_remove, _ = mock_git
    repo_root = tmp_path / "repo"
    mock_root.return_value = repo_root
    
    # Simulate worktree existing
    wt_dir = tmp_path / "repo.wt" / "feat"
    wt_dir.mkdir(parents=True)
    
    mock_remove.return_value = True
    
    with patch("os.getcwd", return_value=str(repo_root)):
        args = Namespace(name="feat", force=False)
        ret = handle_remove(args)
        assert ret == 0
        mock_remove.assert_called_once()
