import pytest
from pathlib import Path
from copal_cli.config.manifest import Manifest

def test_load_valid_manifest(tmp_path):
    manifest_file = tmp_path / "manifest.yaml"
    manifest_file.write_text("""
version: "0.1"
project:
  name: test-project
  description: test desc
default_pack: test-pack
artifacts:
  dir: .artifacts
    """)
    
    manifest = Manifest.load(manifest_file)
    assert manifest.version == "0.1"
    assert manifest.project.name == "test-project"
    assert manifest.default_pack == "test-pack"
    assert manifest.artifacts.dir == ".artifacts"

def test_load_missing_required_fields(tmp_path):
    manifest_file = tmp_path / "manifest.yaml"
    manifest_file.write_text("""
version: "0.1"
# missing project and default_pack
    """)
    
    with pytest.raises(ValueError, match="Missing required field"):
        Manifest.load(manifest_file)

def test_save_manifest(tmp_path):
    manifest_file = tmp_path / "manifest.yaml"
    manifest_file.write_text("""
version: "0.1"
project:
  name: test
default_pack: pack
artifacts:
  dir: art
    """)
    
    manifest = Manifest.load(manifest_file)
    manifest.project.name = "updated"
    manifest.save()
    
    raw = manifest_file.read_text()
    assert "name: updated" in raw

def test_find_manifest(tmp_path):
    copal_dir = tmp_path / ".copal"
    copal_dir.mkdir()
    (copal_dir / "manifest.yaml").touch()
    
    from copal_cli.config.manifest import find_manifest
    
    # Test finding from root
    found = find_manifest(tmp_path)
    assert found == copal_dir / "manifest.yaml"
    
    # Test finding from subdirectory
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    found_sub = find_manifest(subdir)
    assert found_sub == copal_dir / "manifest.yaml"
