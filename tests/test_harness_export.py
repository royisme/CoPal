import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from copal_cli.harness.export import export_command

@pytest.fixture
def mock_console():
    with patch("copal_cli.harness.export.console") as mock:
        yield mock

def test_export_no_manifest(tmp_path, mock_console):
    ret = export_command("claude", target=str(tmp_path))
    assert ret == 2
    args, _ = mock_console.print.call_args
    assert "Manifest not found" in str(args[0])

def test_export_claude_valid(tmp_path, mock_console):
    # Setup infrastructure
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test
default_pack: p
packs:
  - p
""")
    # Setup pack files
    pack_dir = copal_dir / "packs" / "p"
    pack_dir.mkdir(parents=True)
    (pack_dir / "pack.yaml").write_text("""
name: p
workflows:
  plan: workflows/plan.md
""")
    (pack_dir / "workflows").mkdir()
    (pack_dir / "workflows" / "plan.md").write_text("PLAN CONTENT")

    ret = export_command("claude", target=str(tmp_path))
    assert ret == 0
    
    # Verify file created
    cmd_file = tmp_path / ".claude" / "commands" / "copal" / "plan.md"
    assert cmd_file.exists()
    content = cmd_file.read_text()
    assert "PLAN CONTENT" in content
    assert "# Plan Workflow" in content

def test_export_codex_valid(tmp_path, mock_console):
    # Setup infrastructure
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test
default_pack: p
packs:
  - p
""")
    # Setup pack files
    pack_dir = copal_dir / "packs" / "p"
    pack_dir.mkdir(parents=True)
    (pack_dir / "pack.yaml").write_text("""
name: p
workflows:
  work: workflows/work.md
""")
    (pack_dir / "workflows").mkdir()
    (pack_dir / "workflows" / "work.md").write_text("WORK CONTENT")

    ret = export_command("codex", target=str(tmp_path))
    assert ret == 0
    
    # Verify file created
    prompt_file = tmp_path / ".codex" / "prompts" / "copal" / "work.md"
    assert prompt_file.exists()
    content = prompt_file.read_text()
    assert "WORK CONTENT" in content

def test_export_gemini_valid(tmp_path, mock_console):
    # Setup infrastructure
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test
default_pack: p
packs:
  - p
""")
    # Setup pack files
    pack_dir = copal_dir / "packs" / "p"
    pack_dir.mkdir(parents=True)
    (pack_dir / "pack.yaml").write_text("""
name: p
workflows:
  research: workflows/research.md
""")
    (pack_dir / "workflows").mkdir()
    (pack_dir / "workflows" / "research.md").write_text("RESEARCH CONTENT")

    ret = export_command("gemini", target=str(tmp_path))
    assert ret == 0
    
    # Verify file created
    prompt_file = tmp_path / ".gemini" / "prompts" / "copal" / "research.md"
    assert prompt_file.exists()
    content = prompt_file.read_text()
    assert "RESEARCH CONTENT" in content

def test_export_fail_missing_resource(tmp_path, mock_console):
    # This tests stricter failure logic in adapters
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("""
version: "0.1"
project:
  name: test
default_pack: p
packs:
  - p
""")
    # Setup pack but MISSING workflow file
    pack_dir = copal_dir / "packs" / "p"
    pack_dir.mkdir(parents=True)
    (pack_dir / "pack.yaml").write_text("""
name: p
workflows:
  plan: workflows/plan.md
""")
    (pack_dir / "workflows").mkdir()
    # No file written

    ret = export_command("claude", target=str(tmp_path))
    assert ret == 1
    
    # Verify error message logged
    args, _ = mock_console.print.call_args
    assert "Failed to export pack" in str(args[0])

def test_export_unknown_tool(tmp_path, mock_console):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").write_text("version: '0.1'\nproject:\n  name: t\ndefault_pack: p")
    
    ret = export_command("unknown", target=str(tmp_path))
    assert ret == 1
