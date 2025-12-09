"""Tests for CLI module."""
from __future__ import annotations

import sys
from io import StringIO
from unittest.mock import patch

import pytest

from copal_cli.cli import build_parser, main


class TestBuildParser:
    """Tests for build_parser function."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = build_parser()
        assert parser.prog == "copal"

    def test_init_subcommand_exists(self):
        """Test that init subcommand is available."""
        parser = build_parser()
        args = parser.parse_args(["init"])
        assert args.command == "init"

    def test_init_default_target(self):
        """Test that init command has default target."""
        parser = build_parser()
        args = parser.parse_args(["init"])
        assert args.target == "."

    def test_init_custom_target(self):
        """Test that init command accepts custom target."""
        parser = build_parser()
        args = parser.parse_args(["init", "--target", "/custom/path"])
        assert args.target == "/custom/path"

    def test_init_force_flag(self):
        """Test that init command accepts --force flag."""
        parser = build_parser()
        args = parser.parse_args(["init", "--force"])
        assert args.force is True

    def test_init_dry_run_flag(self):
        """Test that init command accepts --dry-run flag."""
        parser = build_parser()
        args = parser.parse_args(["init", "--dry-run"])
        assert args.dry_run is True

    def test_init_verbose_flag(self):
        """Test that init command accepts --verbose flag."""
        parser = build_parser()
        args = parser.parse_args(["--verbose", "init"])
        assert args.verbose is True

    def test_init_verbose_short_flag(self):
        """Test that init command accepts -v flag."""
        parser = build_parser()
        args = parser.parse_args(["-v", "init"])
        assert args.verbose is True


class TestMain:
    """Tests for main function."""

    @patch("copal_cli.cli.harness_init_command")
    def test_main_calls_init_command(self, mock_init):
        """Test that main calls init_command with correct arguments."""
        mock_init.return_value = 0
        result = main(["init", "--target", "/test/path", "--force"])
        assert result == 0
        mock_init.assert_called_once_with(
            target="/test/path",
            force=True,
            dry_run=False,
            tools=None,
            packs=None
        )

    @patch("copal_cli.cli.harness_init_command")
    def test_main_with_dry_run(self, mock_init):
        """Test that main passes dry_run flag correctly."""
        mock_init.return_value = 0
        result = main(["init", "--dry-run"])
        assert result == 0
        mock_init.assert_called_once_with(
            target=".",
            force=False,
            dry_run=True,
            tools=None,
            packs=None
        )

    def test_main_no_command(self):
        """Test that main returns error when no command provided."""
        with pytest.raises(SystemExit):
            main([])

    @patch("copal_cli.cli.harness_init_command")
    def test_main_returns_init_exit_code(self, mock_init):
        """Test that main returns exit code from init_command."""
        mock_init.return_value = 42
        result = main(["init"])
        assert result == 42
