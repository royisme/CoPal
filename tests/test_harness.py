
import pytest
from unittest.mock import patch
from copal_cli.harness.init import init_command
from copal_cli.harness.export import export_command
from copal_cli.harness.validate import validate_command
from copal_cli.config.pack import Pack

@pytest.fixture
def mock_console():
    with patch("copal_cli.harness.init.console") as m:
        yield m

def test_init_dry_run(mock_console, tmp_path):
    # Mock prompt to avoid interactive
    with patch("copal_cli.harness.init.Prompt.ask") as mock_ask:
        mock_ask.side_effect = ["claude", "engineering_loop"]
        
        result = init_command(str(tmp_path), dry_run=True)
        assert result == 0
        assert not (tmp_path / ".copal").exists()

def test_init_real(mock_console, tmp_path):
    with patch("copal_cli.harness.init.Prompt.ask") as mock_ask:
        mock_ask.side_effect = ["claude", "engineering_loop"]
        
        result = init_command(str(tmp_path), dry_run=False)
        assert result == 0
        
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / ".copal" / "manifest.yaml").exists()
        assert (tmp_path / ".copal" / "packs" / "engineering_loop").exists()

def test_export_claude(mock_console, tmp_path):
    # Setup project
    with patch("copal_cli.harness.init.Prompt.ask") as mock_ask:
        mock_ask.side_effect = ["claude", "engineering_loop"]
        init_command(str(tmp_path))
    
    # Run export
    result = export_command("claude", str(tmp_path))
    assert result == 0
    
    # Check output
    commands_dir = tmp_path / ".claude" / "commands" / "copal"
    assert commands_dir.exists()
    assert (commands_dir / "plan.md").exists()
    assert (commands_dir / "research.md").exists()

def test_validate_config(mock_console, tmp_path):
    # Setup project
    with patch("copal_cli.harness.init.Prompt.ask") as mock_ask:
        mock_ask.side_effect = ["claude", "engineering_loop"]
        init_command(str(tmp_path))
        
    result = validate_command(str(tmp_path))
    assert result == 0

def test_validate_artifacts_missing(mock_console, tmp_path):
     # Setup project
    with patch("copal_cli.harness.init.Prompt.ask") as mock_ask:
        mock_ask.side_effect = ["claude", "engineering_loop"]
        init_command(str(tmp_path))
    
    # Needs strict validation now? No, check_artifacts checks existing artifacts vs schema.
    # If artifacts dir missing, it returns 0 (warn).
    # If schema declared but artifacts missing, it skips in current validate.py implementation?
    # Wait, my validate.py changes ADDED strict check for "declared resources declared in pack" (workflows, prompts).
    # Artifacts validation iterates schema in pack and checks if artifact exists in artifacts dir.
    # Lines 86-90 in modified validate.py: "if not artifact_file.exists(): continue". 
    # So it doesn't fail if artifact is missing. It only validates IF it exists.
    # EXCEPT, the test asserts result == 0.
    result = validate_command(str(tmp_path), check_artifacts=True)
    assert result == 0
