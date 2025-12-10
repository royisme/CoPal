import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from copal_cli.harness.init import init_command

@pytest.fixture
def mock_ask():
    with patch("copal_cli.harness.init.Prompt.ask") as mock_ask:
        # Side effect for tools and packs
        # tools -> "claude"
        # packs -> "engineering_loop"
        mock_ask.side_effect = ["claude", "engineering_loop"]
        yield mock_ask

@pytest.fixture
def mock_console():
    with patch("copal_cli.harness.init.console") as mock:
        yield mock

@pytest.fixture
def mock_template_dir(tmp_path):
    # Setup fake templates
    tpl_dir = tmp_path / "templates"
    tpl_dir.mkdir()
    
    (tpl_dir / "manifest.yaml").write_text("template manifest")
    (tpl_dir / "AGENTS.md").write_text("template agents")
    (tpl_dir / "UserAgents.md").write_text("template user agents")
    (tpl_dir / "engineering_loop").mkdir()
    (tpl_dir / "engineering_loop" / "pack.yaml").write_text("pack")
    (tpl_dir / "docs").mkdir()
    (tpl_dir / "docs" / "repo_map.md").write_text("docs")
    
    with patch("copal_cli.harness.init.INIT_TEMPLATE_DIR", tpl_dir):
        with patch("copal_cli.harness.init.PACKS_TEMPLATE_DIR", tpl_dir):
            yield tpl_dir

def test_init_command_dry_run(mock_ask, mock_console, mock_template_dir, tmp_path):
    ret = init_command(target=str(tmp_path), dry_run=True)
    assert ret == 0
    # Nothing should be written
    assert not (tmp_path / ".copal").exists()

def test_init_command_execution(mock_ask, mock_console, mock_template_dir, tmp_path):
    ret = init_command(target=str(tmp_path))
    assert ret == 0
    
    # Check structure
    assert (tmp_path / ".copal").exists()
    assert (tmp_path / ".copal" / "manifest.yaml").exists()
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / ".copal" / "packs" / "engineering_loop").exists()
    assert (tmp_path / ".copal" / "docs" / "architecture.md").exists()
