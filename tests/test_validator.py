"""Tests for validator module."""
from __future__ import annotations

from pathlib import Path

import pytest

from copal_cli.validator import FrontMatterValidator, validate_command


class TestFrontMatterValidator:
    """Tests for FrontMatterValidator class."""

    def test_valid_front_matter(self, tmp_path):
        """Test validation of valid front matter."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: copal
type: role
owner: team-name
enforcement: required
updated: 2025-01-15
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert result.is_valid
        assert len(result.errors) == 0
        assert result.metadata is not None
        assert result.metadata["id"] == "test-doc"

    def test_missing_front_matter(self, tmp_path):
        """Test validation fails when front matter is missing."""
        file_path = tmp_path / "test.md"
        file_path.write_text("# Test Document\n\nNo front matter here.")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert not result.is_valid
        assert any("No YAML front matter" in error for error in result.errors)

    def test_missing_required_fields(self, tmp_path):
        """Test validation fails when required fields are missing."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: copal
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert not result.is_valid
        assert any("Missing required fields" in error for error in result.errors)

    def test_invalid_origin(self, tmp_path):
        """Test validation fails for invalid origin value."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: invalid
type: role
owner: team
enforcement: required
updated: 2025-01-15
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert not result.is_valid
        assert any("Invalid origin" in error for error in result.errors)

    def test_invalid_enforcement(self, tmp_path):
        """Test validation fails for invalid enforcement value."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: copal
type: role
owner: team
enforcement: invalid
updated: 2025-01-15
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert not result.is_valid
        assert any("Invalid enforcement" in error for error in result.errors)

    def test_invalid_date_format(self, tmp_path):
        """Test validation fails for invalid date format."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: copal
type: role
owner: team
enforcement: required
updated: 2025/01/15
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert not result.is_valid
        assert any("Invalid date format" in error for error in result.errors)

    def test_unknown_type_warning(self, tmp_path):
        """Test warning for unknown type value."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: copal
type: unknown-type
owner: team
enforcement: required
updated: 2025-01-15
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert result.is_valid  # Warnings don't make it invalid
        assert len(result.warnings) > 0
        assert any("Unknown type" in warning for warning in result.warnings)

    def test_empty_field_warning(self, tmp_path):
        """Test warning for empty field values."""
        file_path = tmp_path / "test.md"
        file_path.write_text("""---
id: test-doc
origin: copal
type: role
owner:
enforcement: required
updated: 2025-01-15
---

# Test Document
""")

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert len(result.warnings) > 0
        assert any("empty" in warning.lower() for warning in result.warnings)

    def test_validate_directory(self, tmp_path):
        """Test validating multiple files in a directory."""
        # Create valid file
        (tmp_path / "valid.md").write_text("""---
id: valid
origin: copal
type: role
owner: team
enforcement: required
updated: 2025-01-15
---

# Valid
""")

        # Create invalid file
        (tmp_path / "invalid.md").write_text("# No front matter")

        validator = FrontMatterValidator()
        results = validator.validate_directory(tmp_path, pattern="*.md", recursive=False)

        assert len(results) == 2
        assert sum(1 for r in results if r.is_valid) == 1
        assert sum(1 for r in results if not r.is_valid) == 1

    def test_nonexistent_file(self, tmp_path):
        """Test validation of nonexistent file."""
        file_path = tmp_path / "nonexistent.md"

        validator = FrontMatterValidator()
        result = validator.validate_file(file_path)

        assert not result.is_valid
        assert any("does not exist" in error for error in result.errors)


class TestValidateCommand:
    """Tests for validate_command function."""

    def test_validate_command_nonexistent_path(self):
        """Test validate_command with nonexistent path."""
        result = validate_command(target="/nonexistent/path")
        assert result == 1

    def test_validate_command_success(self, tmp_path):
        """Test validate_command with valid files."""
        (tmp_path / "test.md").write_text("""---
id: test
origin: copal
type: role
owner: team
enforcement: required
updated: 2025-01-15
---

# Test
""")

        result = validate_command(target=str(tmp_path), pattern="*.md")
        assert result == 0

    def test_validate_command_failure(self, tmp_path):
        """Test validate_command with invalid files."""
        (tmp_path / "test.md").write_text("# No front matter")

        result = validate_command(target=str(tmp_path), pattern="*.md")
        assert result == 1
