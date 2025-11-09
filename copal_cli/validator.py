"""YAML front matter validation for CoPal knowledge base files."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of YAML front matter validation."""

    file_path: Path
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    metadata: dict[str, Any] | None = None


class FrontMatterValidator:
    """Validator for YAML front matter in markdown files."""

    REQUIRED_FIELDS = {"id", "origin", "type", "owner", "enforcement", "updated"}
    VALID_ORIGINS = {"copal", "project"}
    VALID_ENFORCEMENTS = {"required", "recommended", "optional"}
    VALID_TYPES = {
        "role",
        "workflow",
        "toolset-index",
        "cli-guide",
        "principle",
        "environment",
        "information-architecture",
        "mcp-discovery",
        "agent-script",
    }

    # Pattern to match YAML front matter
    FRONT_MATTER_PATTERN = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n",
        re.DOTALL | re.MULTILINE
    )

    # Pattern to validate date format (YYYY-MM-DD)
    DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    def __init__(self):
        """Initialize the validator."""
        self.results: list[ValidationResult] = []

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate YAML front matter in a single file.

        Args:
            file_path: Path to the markdown file to validate.

        Returns:
            ValidationResult: Validation result with errors and warnings.
        """
        errors: list[str] = []
        warnings: list[str] = []
        metadata: dict[str, Any] | None = None

        if not file_path.exists():
            errors.append(f"File does not exist: {file_path}")
            return ValidationResult(file_path, False, errors, warnings, metadata)

        if not file_path.is_file():
            errors.append(f"Path is not a file: {file_path}")
            return ValidationResult(file_path, False, errors, warnings, metadata)

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            errors.append(f"Failed to read file: {e}")
            return ValidationResult(file_path, False, errors, warnings, metadata)

        # Extract front matter
        match = self.FRONT_MATTER_PATTERN.match(content)
        if not match:
            errors.append("No YAML front matter found (must start with ---)")
            return ValidationResult(file_path, False, errors, warnings, metadata)

        front_matter_text = match.group(1)
        metadata = self._parse_simple_yaml(front_matter_text)

        if metadata is None:
            errors.append("Failed to parse YAML front matter")
            return ValidationResult(file_path, False, errors, warnings, metadata)

        # Validate required fields
        missing_fields = self.REQUIRED_FIELDS - set(metadata.keys())
        if missing_fields:
            errors.append(f"Missing required fields: {', '.join(sorted(missing_fields))}")

        # Validate field values
        if "origin" in metadata and metadata["origin"] not in self.VALID_ORIGINS:
            errors.append(
                f"Invalid origin '{metadata['origin']}'. "
                f"Must be one of: {', '.join(self.VALID_ORIGINS)}"
            )

        if "enforcement" in metadata and metadata["enforcement"] not in self.VALID_ENFORCEMENTS:
            errors.append(
                f"Invalid enforcement '{metadata['enforcement']}'. "
                f"Must be one of: {', '.join(self.VALID_ENFORCEMENTS)}"
            )

        if "type" in metadata and metadata["type"] not in self.VALID_TYPES:
            warnings.append(
                f"Unknown type '{metadata['type']}'. "
                f"Expected one of: {', '.join(sorted(self.VALID_TYPES))}"
            )

        if "updated" in metadata:
            if not self.DATE_PATTERN.match(str(metadata["updated"])):
                errors.append(
                    f"Invalid date format for 'updated': '{metadata['updated']}'. "
                    "Expected YYYY-MM-DD"
                )

        # Check for empty values
        for key, value in metadata.items():
            if value == "" or value is None:
                warnings.append(f"Field '{key}' is empty")

        is_valid = len(errors) == 0
        return ValidationResult(file_path, is_valid, errors, warnings, metadata)

    def validate_directory(
        self,
        directory: Path,
        pattern: str = "**/*.md",
        recursive: bool = True
    ) -> list[ValidationResult]:
        """Validate all markdown files in a directory.

        Args:
            directory: Directory to search for markdown files.
            pattern: Glob pattern for file matching (default: **/*.md).
            recursive: Whether to search recursively (default: True).

        Returns:
            list[ValidationResult]: List of validation results.
        """
        results: list[ValidationResult] = []

        if not directory.exists():
            logger.error(f"Directory does not exist: {directory}")
            return results

        if recursive:
            files = directory.glob(pattern)
        else:
            clean_pattern = pattern[3:] if pattern.startswith("**/") else pattern
            files = directory.glob(clean_pattern)

        for file_path in sorted(files):
            if file_path.is_file():
                result = self.validate_file(file_path)
                results.append(result)

        return results

    def _parse_simple_yaml(self, text: str) -> dict[str, Any] | None:
        """Parse simple YAML text (key: value pairs only).

        This is a simplified parser that handles basic key-value pairs.
        For more complex YAML, consider using the pyyaml library.

        Args:
            text: YAML text to parse.

        Returns:
            dict[str, Any] | None: Parsed metadata or None if parsing fails.
        """
        metadata: dict[str, Any] = {}

        for line in text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                continue

            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                value = value[1:-1]

            metadata[key] = value

        return metadata if metadata else None

    def print_report(self, results: list[ValidationResult]) -> None:
        """Print a summary report of validation results.

        Args:
            results: List of validation results to report.
        """
        if not results:
            logger.info("No files to validate")
            return

        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid

        logger.info(f"\n{'='*60}")
        logger.info("YAML Front Matter Validation Report")
        logger.info(f"{'='*60}")
        logger.info(f"Total files: {total}")
        logger.info(f"Valid: {valid} ✓")
        logger.info(f"Invalid: {invalid} ✗")
        logger.info(f"{'='*60}\n")

        # Print invalid files first
        for result in results:
            if not result.is_valid:
                logger.error(f"\n✗ {result.file_path}")
                for error in result.errors:
                    logger.error(f"  ERROR: {error}")
                for warning in result.warnings:
                    logger.warning(f"  WARNING: {warning}")

        # Print warnings for valid files
        for result in results:
            if result.is_valid and result.warnings:
                logger.info(f"\n✓ {result.file_path}")
                for warning in result.warnings:
                    logger.warning(f"  WARNING: {warning}")


def validate_command(*, target: str, pattern: str = "**/*.md") -> int:
    """Validate YAML front matter in knowledge base files.

    Args:
        target: Target directory to validate.
        pattern: Glob pattern for file matching.

    Returns:
        int: Exit code (0 if all valid, 1 if any invalid).
    """
    target_path = Path(target).resolve()

    if not target_path.exists():
        logger.error(f"Target path does not exist: {target_path}")
        return 1

    logger.info(f"Validating YAML front matter in: {target_path}")
    logger.info(f"Pattern: {pattern}\n")

    validator = FrontMatterValidator()
    results = validator.validate_directory(target_path, pattern=pattern)

    validator.print_report(results)

    # Return 0 if all valid, 1 if any invalid
    return 0 if all(r.is_valid for r in results) else 1
