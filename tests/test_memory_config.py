import pytest
import json
from pathlib import Path
from copal_cli.memory.config import (
    load_memory_config,
    resolve_database_path,
    is_memory_enabled,
    is_auto_capture_enabled,
    DEFAULT_CONFIG,
)

def test_load_memory_config_defaults(tmp_path):
    # No config file
    cfg = load_memory_config(tmp_path)
    assert cfg == DEFAULT_CONFIG

def test_load_memory_config_exists(tmp_path):
    config_dir = tmp_path / ".copal"
    config_dir.mkdir()
    (config_dir / "config.json").write_text(json.dumps({"memory": {"backend": "json"}}))
    
    cfg = load_memory_config(tmp_path)
    assert cfg["backend"] == "json"
    assert cfg["auto_capture"] is True

def test_load_memory_config_invalid(tmp_path):
    config_dir = tmp_path / ".copal"
    config_dir.mkdir()
    (config_dir / "config.json").write_text("{invalid")
    
    cfg = load_memory_config(tmp_path)
    assert cfg == DEFAULT_CONFIG

def test_resolve_database_path_default(tmp_path):
    cfg = DEFAULT_CONFIG.copy()
    db_path = resolve_database_path(tmp_path, cfg)
    assert db_path == tmp_path / ".copal/memory.db"
    assert db_path.parent.exists()

def test_resolve_database_path_absolute(tmp_path):
    abs_path = tmp_path / "abs" / "db.sqlite"
    cfg = {"database": str(abs_path)}
    db_path = resolve_database_path(tmp_path, cfg)
    assert db_path == abs_path
    assert db_path.parent.exists()

def test_is_memory_enabled():
    assert is_memory_enabled({"enabled": True}) is True
    assert is_memory_enabled({"enabled": False}) is False
    assert is_memory_enabled({}) is True # Default

def test_is_auto_capture_enabled():
    assert is_auto_capture_enabled({"auto_capture": True}) is True
    assert is_auto_capture_enabled({"auto_capture": False}) is False
