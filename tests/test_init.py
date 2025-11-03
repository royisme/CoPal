"""Tests for init module."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from copal_cli.init import _copy, init_command, TEMPLATE_DIR


class TestCopyFunction:
    """Tests for _copy function."""

    def test_copy_skips_existing_without_force(self, tmp_path):
        """Test that _copy skips existing files when force is False."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("source content")
        dst.write_text("existing content")

        result = _copy(src, dst, force=False, dry_run=False)

        assert result is False
        assert dst.read_text() == "existing content"

    def test_copy_overwrites_with_force(self, tmp_path):
        """Test that _copy overwrites existing files when force is True."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("source content")
        dst.write_text("existing content")

        result = _copy(src, dst, force=True, dry_run=False)

        assert result is True
        assert dst.read_text() == "source content"

    def test_copy_creates_new_file(self, tmp_path):
        """Test that _copy creates new files."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("source content")

        result = _copy(src, dst, force=False, dry_run=False)

        assert result is True
        assert dst.exists()
        assert dst.read_text() == "source content"

    def test_copy_creates_parent_directories(self, tmp_path):
        """Test that _copy creates parent directories."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "subdir" / "nested" / "dest.txt"
        src.write_text("source content")

        result = _copy(src, dst, force=False, dry_run=False)

        assert result is True
        assert dst.exists()
        assert dst.read_text() == "source content"

    def test_copy_directory(self, tmp_path):
        """Test that _copy handles directories."""
        src = tmp_path / "source_dir"
        dst = tmp_path / "dest_dir"
        src.mkdir()
        (src / "file.txt").write_text("content")

        result = _copy(src, dst, force=False, dry_run=False)

        assert result is True
        assert dst.is_dir()
        assert (dst / "file.txt").exists()

    def test_copy_dry_run_does_not_write(self, tmp_path):
        """Test that _copy in dry-run mode does not write files."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("source content")

        result = _copy(src, dst, force=False, dry_run=True)

        assert result is True
        assert not dst.exists()

    def test_copy_dry_run_with_existing_force(self, tmp_path):
        """Test that _copy in dry-run mode with force does not overwrite."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "dest.txt"
        src.write_text("source content")
        dst.write_text("existing content")

        result = _copy(src, dst, force=True, dry_run=True)

        assert result is True
        assert dst.read_text() == "existing content"


class TestInitCommand:
    """Tests for init_command function."""

    def test_init_command_fails_on_nonexistent_target(self):
        """Test that init_command fails when target doesn't exist."""
        with pytest.raises(SystemExit):
            init_command(target="/nonexistent/path", force=False, dry_run=False)

    @patch("copal_cli.init._copy")
    def test_init_command_copies_all_templates(self, mock_copy, tmp_path):
        """Test that init_command copies all required templates."""
        mock_copy.return_value = True

        result = init_command(target=str(tmp_path), force=False, dry_run=False)

        assert result == 0
        assert mock_copy.call_count == 5  # Updated to 5 files

        # Verify the files that should be copied
        calls = [call[0] for call in mock_copy.call_args_list]
        src_files = [call[0] for call in calls]
        dst_files = [call[1] for call in calls]

        assert any("AGENTS.md" in str(src) for src in src_files)
        assert any("UserAgents.md" in str(src) for src in src_files)
        assert any(".copal" in str(src) for src in src_files)

        assert any("AGENTS.md" in str(dst) for dst in dst_files)
        assert any("UserAgents.md" in str(dst) for dst in dst_files)
        assert any(".copal" in str(dst) for dst in dst_files)

    @patch("copal_cli.init._copy")
    def test_init_command_passes_force_flag(self, mock_copy, tmp_path):
        """Test that init_command passes force flag to _copy."""
        mock_copy.return_value = True

        init_command(target=str(tmp_path), force=True, dry_run=False)

        # Verify force flag is passed
        for call in mock_copy.call_args_list:
            assert call[0][2] is True  # force parameter

    @patch("copal_cli.init._copy")
    def test_init_command_dry_run(self, mock_copy, tmp_path):
        """Test that init_command works in dry-run mode."""
        mock_copy.return_value = True

        result = init_command(target=str(tmp_path), force=False, dry_run=True)

        assert result == 0
        assert mock_copy.call_count == 5  # Updated to 5 files

        # Verify dry_run flag is passed
        for call in mock_copy.call_args_list:
            assert call[0][3] is True  # dry_run parameter

    @patch("copal_cli.init._copy")
    def test_init_command_counts_copied_files(self, mock_copy, tmp_path):
        """Test that init_command counts copied files correctly."""
        # Simulate some files being skipped
        mock_copy.side_effect = [True, False, True, True, False]  # Updated to 5 calls

        result = init_command(target=str(tmp_path), force=False, dry_run=False)

        assert result == 0
        assert mock_copy.call_count == 5  # Updated to 5 files


class TestTemplateDir:
    """Tests for TEMPLATE_DIR constant."""

    def test_template_dir_exists(self):
        """Test that TEMPLATE_DIR exists."""
        assert TEMPLATE_DIR.exists()
        assert TEMPLATE_DIR.is_dir()

    def test_template_dir_contains_agents_md(self):
        """Test that TEMPLATE_DIR contains AGENTS.md."""
        agents_md = TEMPLATE_DIR / "AGENTS.md"
        assert agents_md.exists()
        assert agents_md.is_file()

    def test_template_dir_contains_useragents_md(self):
        """Test that TEMPLATE_DIR contains UserAgents.md."""
        useragents_md = TEMPLATE_DIR / "UserAgents.md"
        assert useragents_md.exists()
        assert useragents_md.is_file()

    def test_template_dir_contains_copal_global(self):
        """Test that TEMPLATE_DIR contains .copal/global directory."""
        copal_global = TEMPLATE_DIR / ".copal" / "global"
        assert copal_global.exists()
        assert copal_global.is_dir()
