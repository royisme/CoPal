import pytest
from pathlib import Path
from unittest.mock import MagicMock
from copal_cli.adapters.claude import ClaudeAdapter
from copal_cli.config.manifest import Manifest
from copal_cli.config.pack import Pack

def test_claude_adapter_export(tmp_path):
    # Setup context
    manifest = MagicMock(spec=Manifest)
    target_root = tmp_path
    
    pack = MagicMock(spec=Pack)
    pack.name = "test-pack"
    pack.workflows = {
        "plan": "workflows/plan.md"
    }
    pack.prompts = {
        "planner": "prompts/planner.md"
    }
    
    # Mock methods to return valid paths
    pack.get_workflow_path.return_value = target_root / "workflows" / "plan.md"
    pack.get_prompt_path.return_value = target_root / "prompts" / "planner.md"
    
    # Create source files
    (target_root / "workflows").mkdir()
    (target_root / "workflows" / "plan.md").write_text("# Plan Workflow")
    (target_root / "prompts").mkdir()
    (target_root / "prompts" / "planner.md").write_text("System: Planner")
    
    adapter = ClaudeAdapter(manifest, target_root)
    adapter.export(pack)
    
    # Verify output
    cmd_file = target_root / ".claude" / "commands" / "copal" / "plan.md"
    assert cmd_file.exists()
    content = cmd_file.read_text()
    assert "# Plan Workflow" in content
    assert "System: Planner" in content  # Checks prompt injection if implemented
    assert "CLAUDE.md" not in content # Minimal check

def test_claude_adapter_name(tmp_path):
    adapter = ClaudeAdapter(MagicMock(), tmp_path)
    assert adapter.name == "claude"
