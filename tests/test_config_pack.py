import pytest
from pathlib import Path
from copal_cli.config.pack import Pack

def test_load_pack_from_dir(tmp_path):
    pack_dir = tmp_path / "test_pack"
    pack_dir.mkdir()
    pack_file = pack_dir / "pack.yaml"
    pack_file.write_text("""
name: test-pack
version: "0.1"
description: test
workflows:
  plan: workflows/plan.md
    """)
    (pack_dir / "workflows").mkdir()
    (pack_dir / "workflows" / "plan.md").touch()
    
    pack = Pack.load(pack_dir)
    assert pack.name == "test-pack"
    assert pack.get_workflow_path("plan") == pack_dir / "workflows" / "plan.md"

def test_load_pack_invalid_yaml(tmp_path):
    pack_file = tmp_path / "pack.yaml"
    pack_file.write_text("invalid: [")
    
    with pytest.raises(ValueError, match="Invalid YAML"):
        Pack.load(pack_file)

def test_get_resource_paths(tmp_path):
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    pack_file = pack_dir / "pack.yaml"
    pack_file.write_text("""
name: p
schemas:
  plan: schemas/plan.json
prompts:
  worker: prompts/worker.md
    """)
    
    pack = Pack.load(pack_dir)
    assert pack.get_schema_path("plan") == pack_dir / "schemas" / "plan.json"
    assert pack.get_prompt_path("worker") == pack_dir / "prompts" / "worker.md"
