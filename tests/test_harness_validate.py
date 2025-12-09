import pytest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from copal_cli.harness.validate import validate_command, validate_pre_task

@pytest.fixture
def mock_console():
    with patch("copal_cli.harness.validate.console") as mock:
        yield mock

def test_validate_no_manifest(tmp_path, mock_console):
    ret = validate_command(target=str(tmp_path))
    assert ret == 2
    args, _ = mock_console.print.call_args
    assert "Manifest not found" in str(args[0])

def test_validate_valid_manifest(tmp_path, mock_console):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: valid
default_pack: p
packs:
  - p
    """)
    
    with patch("copal_cli.harness.validate.Pack.load") as mock_pack_load:
        mock_pack = MagicMock()
        mock_pack.name = "p"
        mock_pack.workflows = {}
        mock_pack.prompts = {}
        mock_pack.scripts = {}
        mock_pack.templates = {}
        mock_pack.schemas = {}
        mock_pack_load.return_value = mock_pack
        
        ret = validate_command(target=str(tmp_path))
        assert ret == 0

def test_validate_strict_pack_missing_resource(tmp_path, mock_console):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: strict_check
default_pack: p
packs:
  - p
    """)

    with patch("copal_cli.harness.validate.Pack.load") as mock_pack_load:
        mock_pack = MagicMock()
        mock_pack.name = "p"
        # Declare a workflow but mock getter to return missing path
        mock_pack.workflows = {"missing_flow": "workflows/missing.md"}
        mock_pack.prompts = {}
        mock_pack.scripts = {}
        mock_pack.templates = {}
        mock_pack.schemas = {}
        
        # get_workflow_path returns path that doesn't exist
        mock_pack.get_workflow_path.return_value = copal_dir / "missing.md"
        
        mock_pack_load.return_value = mock_pack
        
        ret = validate_command(target=str(tmp_path))
        assert ret == 2 # Expect failure due to missing resource

def test_validate_artifacts_check_success(tmp_path, mock_console):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: artifact_check
default_pack: p
packs:
  - p
artifacts:
  dir: artifacts
    """)
    
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    
    # Create valid artifact
    (artifacts_dir / "plan.json").write_text('{"foo": "bar"}')
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"type": "object", "properties": {"foo": {"type": "string"}}}')

    with patch("copal_cli.harness.validate.Pack.load") as mock_pack_load:
        mock_pack = MagicMock()
        mock_pack.name = "p"
        mock_pack.workflows = {}
        mock_pack.prompts = {}
        mock_pack.scripts = {}
        mock_pack.templates = {}
        
        mock_pack.schemas = {"plan": "schemas/plan.json"}
        mock_pack.get_schema_path.return_value = schema_file
        
        mock_pack_load.return_value = mock_pack
        
        ret = validate_command(target=str(tmp_path), check_artifacts=True)
        assert ret == 0

def test_validate_artifacts_schema_failure(tmp_path, mock_console):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: artifact_fail
default_pack: p
packs:
  - p
artifacts:
  dir: artifacts
    """)
    
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    
    # Invalid data type for foo
    (artifacts_dir / "plan.json").write_text('{"foo": 123}')
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{"type": "object", "properties": {"foo": {"type": "string"}}}')

    with patch("copal_cli.harness.validate.Pack.load") as mock_pack_load:
        mock_pack = MagicMock()
        mock_pack.name = "p"
        mock_pack.schemas = {"plan": "schemas/plan.json"}
        mock_pack.get_schema_path.return_value = schema_file
        # Set other attrs empty
        mock_pack.workflows = {}
        mock_pack.prompts = {}
        mock_pack.scripts = {}
        mock_pack.templates = {}
        
        mock_pack_load.return_value = mock_pack
        
        ret = validate_command(target=str(tmp_path), check_artifacts=True)
        assert ret == 3

def test_validate_artifacts_invalid_json(tmp_path, mock_console):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: bad_json
default_pack: p
packs:
  - p
artifacts:
  dir: artifacts
    """)
    
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    (artifacts_dir / "plan.json").write_text('{invalid_json')
    
    schema_file = tmp_path / "schema.json"
    schema_file.write_text('{}')

    with patch("copal_cli.harness.validate.Pack.load") as mock_pack_load:
        mock_pack = MagicMock()
        mock_pack.name = "p"
        mock_pack.schemas = {"plan": "schemas/plan.json"}
        mock_pack.get_schema_path.return_value = schema_file
        # Set other attrs empty
        mock_pack.workflows = {}
        mock_pack.prompts = {}
        mock_pack.scripts = {}
        mock_pack.templates = {}
        
        mock_pack_load.return_value = mock_pack
        
        ret = validate_command(target=str(tmp_path), check_artifacts=True)
        # Should catch JSONDecodeError logic
        # If validate.py returns 3 on artifact error
        assert ret == 3


# ============================================================
# Tests for validate_pre_task
# ============================================================

class TestValidatePreTask:
    """Tests for the validate_pre_task function."""

    def test_pre_task_clean_git_no_test_cmd(self, tmp_path, mock_console):
        """Test pre-task validation with clean git and no test command configured."""
        copal_dir = tmp_path / ".copal"
        copal_dir.mkdir()
        (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test_project
default_pack: p
packs:
  - p
        """)
        
        with patch("copal_cli.harness.validate.subprocess.check_output") as mock_git:
            mock_git.return_value = ""  # Clean git status
            
            ret = validate_pre_task(target=str(tmp_path))
            
            assert ret == 0
            mock_git.assert_called_once()

    def test_pre_task_dirty_git(self, tmp_path, mock_console):
        """Test pre-task validation fails with uncommitted changes."""
        copal_dir = tmp_path / ".copal"
        copal_dir.mkdir()
        (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test_project
default_pack: p
packs:
  - p
        """)
        
        with patch("copal_cli.harness.validate.subprocess.check_output") as mock_git:
            mock_git.return_value = " M dirty_file.py"  # Dirty git status
            
            ret = validate_pre_task(target=str(tmp_path))
            
            assert ret == 1

    def test_pre_task_not_git_repo(self, tmp_path, mock_console):
        """Test pre-task validation skips git check if not a git repo."""
        copal_dir = tmp_path / ".copal"
        copal_dir.mkdir()
        (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test_project
default_pack: p
packs:
  - p
        """)
        
        with patch("copal_cli.harness.validate.subprocess.check_output") as mock_git:
            mock_git.side_effect = FileNotFoundError("git not found")
            
            ret = validate_pre_task(target=str(tmp_path))
            
            # Should succeed despite no git
            assert ret == 0

    def test_pre_task_with_test_cmd_success(self, tmp_path, mock_console):
        """Test pre-task validation runs test command successfully."""
        copal_dir = tmp_path / ".copal"
        copal_dir.mkdir()
        (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test_project
default_pack: p
packs:
  - p
verify:
  command: "echo 'tests passed'"
        """)
        
        with patch("copal_cli.harness.validate.subprocess.check_output") as mock_git, \
             patch("copal_cli.harness.validate.subprocess.check_call") as mock_test:
            mock_git.return_value = ""  # Clean git
            mock_test.return_value = 0  # Test passes
            
            ret = validate_pre_task(target=str(tmp_path))
            
            assert ret == 0
            mock_test.assert_called_once()

    def test_pre_task_with_test_cmd_failure(self, tmp_path, mock_console):
        """Test pre-task validation fails when test command fails."""
        import subprocess
        
        copal_dir = tmp_path / ".copal"
        copal_dir.mkdir()
        (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test_project
default_pack: p
packs:
  - p
verify:
  command: "exit 1"
        """)
        
        with patch("copal_cli.harness.validate.subprocess.check_output") as mock_git, \
             patch("copal_cli.harness.validate.subprocess.check_call") as mock_test:
            mock_git.return_value = ""  # Clean git
            mock_test.side_effect = subprocess.CalledProcessError(1, "exit 1")
            
            ret = validate_pre_task(target=str(tmp_path))
            
            assert ret == 1

    def test_pre_task_no_manifest(self, tmp_path, mock_console):
        """Test pre-task validation fails if no manifest exists."""
        with patch("copal_cli.harness.validate.subprocess.check_output") as mock_git:
            mock_git.return_value = ""  # Clean git
            
            ret = validate_pre_task(target=str(tmp_path))
            
            assert ret == 2

