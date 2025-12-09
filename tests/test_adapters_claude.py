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
    pack.description = "Test Pack Description"
    pack.workflows = {
        "plan": "workflows/plan.md"
    }
    pack.prompts = {
        "planner": "prompts/planner.md"
    }
    
    # Create pack directory structure for skill export
    pack_base = target_root / "pack"
    pack_base.mkdir()
    pack._base_path = pack_base  # Required for _export_skill
    
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
    
    # Verify Subagent config
    agent_file = target_root / ".claude" / "agents" / "copal-planner.md"
    assert agent_file.exists()
    agent_content = agent_file.read_text()
    assert "System: Planner" in agent_content
    assert "Copal Planner Agent" in agent_content
    
    # Verify Command Config
    cmd_file = target_root / ".claude" / "commands" / "copal" / "plan.md"
    assert cmd_file.exists()
    cmd_content = cmd_file.read_text()
    assert "# Plan Workflow" in cmd_content
    assert "AGENT SWITCH" in cmd_content
    assert "copal-planner" in cmd_content
    
    # Verify Start Command
    start_cmd = target_root / ".claude" / "commands" / "copal" / "start.md"
    assert start_cmd.exists()
    assert "copal-orchestrator" in start_cmd.read_text()

def test_claude_adapter_name(tmp_path):
    adapter = ClaudeAdapter(MagicMock(), tmp_path)
    assert adapter.name == "claude"
