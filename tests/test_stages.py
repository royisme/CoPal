"""Tests for stage commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from copal_cli.stages import (
    analyze_command,
    spec_command,
    plan_command,
    implement_command,
    review_command,
    commit_command,
)


class TestAnalyzeCommand:
    """Tests for analyze command."""

    @patch("copal_cli.stages.analyze.render_stage_prompt")
    def test_analyze_command_success(self, mock_render, tmp_path):
        """Test successful analyze command."""
        # Setup
        prompt_path = tmp_path / ".copal" / "runtime" / "analysis.prompt.md"
        mock_render.return_value = prompt_path

        # Execute
        result = analyze_command(
            target=str(tmp_path),
            title="Test Task",
            goals="Test goals",
            constraints="Test constraints"
        )

        # Verify
        assert result == 0
        assert mock_render.called
        call_args = mock_render.call_args
        assert call_args[1]['stage'] == 'analysis'
        assert call_args[1]['task_meta']['title'] == "Test Task"
        assert call_args[1]['task_meta']['goals'] == "Test goals"
        assert call_args[1]['task_meta']['constraints'] == "Test constraints"

    def test_analyze_command_nonexistent_target(self):
        """Test analyze command with nonexistent target."""
        result = analyze_command(target="/nonexistent/path")
        assert result == 1


class TestSpecCommand:
    """Tests for spec command."""

    @patch("copal_cli.stages.spec.render_stage_prompt")
    def test_spec_command_success(self, mock_render, tmp_path):
        """Test successful spec command."""
        prompt_path = tmp_path / ".copal" / "runtime" / "spec.prompt.md"
        mock_render.return_value = prompt_path

        result = spec_command(target=str(tmp_path))

        assert result == 0
        assert mock_render.called
        call_args = mock_render.call_args
        assert call_args[1]['stage'] == 'spec'


class TestPlanCommand:
    """Tests for plan command."""

    @patch("copal_cli.stages.plan.render_stage_prompt")
    def test_plan_command_success(self, mock_render, tmp_path):
        """Test successful plan command."""
        prompt_path = tmp_path / ".copal" / "runtime" / "plan.prompt.md"
        mock_render.return_value = prompt_path

        result = plan_command(target=str(tmp_path))

        assert result == 0
        assert mock_render.called
        call_args = mock_render.call_args
        assert call_args[1]['stage'] == 'plan'


class TestImplementCommand:
    """Tests for implement command."""

    @patch("copal_cli.stages.implement.render_stage_prompt")
    def test_implement_command_success(self, mock_render, tmp_path):
        """Test successful implement command."""
        prompt_path = tmp_path / ".copal" / "runtime" / "implement.prompt.md"
        mock_render.return_value = prompt_path

        result = implement_command(target=str(tmp_path))

        assert result == 0
        assert mock_render.called
        call_args = mock_render.call_args
        assert call_args[1]['stage'] == 'implement'


class TestReviewCommand:
    """Tests for review command."""

    @patch("copal_cli.stages.review.render_stage_prompt")
    def test_review_command_success(self, mock_render, tmp_path):
        """Test successful review command."""
        prompt_path = tmp_path / ".copal" / "runtime" / "review.prompt.md"
        mock_render.return_value = prompt_path

        result = review_command(target=str(tmp_path))

        assert result == 0
        assert mock_render.called
        call_args = mock_render.call_args
        assert call_args[1]['stage'] == 'review'


class TestCommitCommand:
    """Tests for commit command."""

    def test_commit_command_success(self, tmp_path):
        """Test successful commit command."""
        # Create some artifact files
        artifacts_dir = tmp_path / ".copal" / "artifacts"
        artifacts_dir.mkdir(parents=True)
        (artifacts_dir / "analysis.md").write_text("test")
        (artifacts_dir / "plan.md").write_text("test")

        result = commit_command(target=str(tmp_path), task_id="test-123")

        assert result == 0

        # Check commit.json was created
        commit_file = artifacts_dir / "commit.json"
        assert commit_file.exists()

        import json
        commit_data = json.loads(commit_file.read_text())
        assert commit_data['task_id'] == "test-123"
        assert commit_data['workflow_completed'] is True
        assert len(commit_data['artifacts']) == 2

    def test_commit_command_auto_task_id(self, tmp_path):
        """Test commit command with auto-generated task ID."""
        artifacts_dir = tmp_path / ".copal" / "artifacts"
        artifacts_dir.mkdir(parents=True)

        result = commit_command(target=str(tmp_path))

        assert result == 0

        commit_file = artifacts_dir / "commit.json"
        assert commit_file.exists()

        import json
        commit_data = json.loads(commit_file.read_text())
        assert commit_data['task_id'].startswith('task-')
