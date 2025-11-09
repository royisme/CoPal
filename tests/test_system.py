"""Tests for system utilities."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from copal_cli.system.fs import ensure_runtime_dirs, read_text, write_text
from copal_cli.system.mcp import read_mcp_available
from copal_cli.system.hooks import select_injection_blocks, _parse_hooks_yaml


class TestFsUtils:
    """Tests for file system utilities."""

    def test_ensure_runtime_dirs(self, tmp_path):
        """Test that ensure_runtime_dirs creates both directories."""
        runtime_dir, artifacts_dir = ensure_runtime_dirs(tmp_path)

        assert runtime_dir == tmp_path / ".copal" / "runtime"
        assert artifacts_dir == tmp_path / ".copal" / "artifacts"
        assert runtime_dir.exists()
        assert artifacts_dir.exists()

    def test_write_and_read_text(self, tmp_path):
        """Test writing and reading text files."""
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"

        write_text(test_file, content)
        assert test_file.exists()

        read_content = read_text(test_file)
        assert read_content == content

    def test_read_text_nonexistent_file(self, tmp_path):
        """Test that read_text raises FileNotFoundError for nonexistent file."""
        test_file = tmp_path / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            read_text(test_file)


class TestMcpUtils:
    """Tests for MCP utilities."""

    def test_read_mcp_available_existing_file(self, tmp_path):
        """Test reading MCP available file."""
        mcp_file = tmp_path / ".copal" / "mcp-available.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_data = ["context7", "active-file", "file-tree"]

        with open(mcp_file, 'w', encoding='utf-8') as f:
            json.dump(mcp_data, f)

        result = read_mcp_available(tmp_path)
        assert result == mcp_data

    def test_read_mcp_available_nonexistent_file(self, tmp_path):
        """Test reading MCP available file that doesn't exist."""
        result = read_mcp_available(tmp_path)
        assert result == []

    def test_read_mcp_available_invalid_json(self, tmp_path):
        """Test reading MCP available file with invalid JSON."""
        mcp_file = tmp_path / ".copal" / "mcp-available.json"
        mcp_file.parent.mkdir(parents=True)
        mcp_file.write_text("invalid json")

        result = read_mcp_available(tmp_path)
        assert result == []


class TestHooksUtils:
    """Tests for hooks utilities."""

    def test_parse_hooks_yaml_basic(self):
        """Test parsing basic hooks YAML."""
        yaml_content = """
version: 1
rules:
  - id: test-rule
    stage: analysis
    any_mcp: ["context7"]
    inject:
      - "mcp/context7/usage.analysis.md"
"""
        rules = _parse_hooks_yaml(yaml_content)

        assert len(rules) == 1
        assert rules[0]['id'] == 'test-rule'
        assert rules[0]['stage'] == 'analysis'
        assert rules[0]['any_mcp'] == ['context7']
        assert rules[0]['inject'] == ['mcp/context7/usage.analysis.md']

    def test_parse_hooks_yaml_multiple_rules(self):
        """Test parsing multiple rules."""
        yaml_content = """
version: 1
rules:
  - id: rule1
    stage: analysis
    any_mcp: ["context7"]
    inject:
      - "block1.md"

  - id: rule2
    stage: plan
    all_mcp: ["active-file", "file-tree"]
    inject:
      - "block2.md"
      - "block3.md"
"""
        rules = _parse_hooks_yaml(yaml_content)

        assert len(rules) == 2
        assert rules[0]['id'] == 'rule1'
        assert rules[1]['id'] == 'rule2'
        assert rules[1]['inject'] == ['block2.md', 'block3.md']

    def test_select_injection_blocks_any_mcp(self, tmp_path):
        """Test selecting injection blocks with any_mcp condition."""
        hooks_yaml = tmp_path / "hooks.yaml"
        hooks_yaml.write_text("""
version: 1
rules:
  - id: test-rule
    stage: analysis
    any_mcp: ["context7", "other"]
    inject:
      - "block.md"
""")

        # Should match because context7 is in mcp_names
        result = select_injection_blocks('analysis', ['context7'], hooks_yaml)
        assert result == ['block.md']

        # Should not match because neither context7 nor other is in mcp_names
        result = select_injection_blocks('analysis', ['different'], hooks_yaml)
        assert result == []

    def test_select_injection_blocks_all_mcp(self, tmp_path):
        """Test selecting injection blocks with all_mcp condition."""
        hooks_yaml = tmp_path / "hooks.yaml"
        hooks_yaml.write_text("""
version: 1
rules:
  - id: test-rule
    stage: implement
    all_mcp: ["active-file", "file-tree"]
    inject:
      - "block.md"
""")

        # Should match because both are present
        result = select_injection_blocks('implement', ['active-file', 'file-tree'], hooks_yaml)
        assert result == ['block.md']

        # Should not match because file-tree is missing
        result = select_injection_blocks('implement', ['active-file'], hooks_yaml)
        assert result == []

    def test_select_injection_blocks_nonexistent_file(self, tmp_path):
        """Test selecting injection blocks when hooks file doesn't exist."""
        hooks_yaml = tmp_path / "nonexistent.yaml"
        result = select_injection_blocks('analysis', ['context7'], hooks_yaml)
        assert result == []

    def test_select_injection_blocks_wrong_stage(self, tmp_path):
        """Test selecting injection blocks for wrong stage."""
        hooks_yaml = tmp_path / "hooks.yaml"
        hooks_yaml.write_text("""
version: 1
rules:
  - id: test-rule
    stage: analysis
    any_mcp: ["context7"]
    inject:
      - "block.md"
""")

        result = select_injection_blocks('plan', ['context7'], hooks_yaml)
        assert result == []
