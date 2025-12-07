# Packaging & Release Guide

This document is intended for maintainers of `copal-cli`. It describes how to build and publish a new release of the CLI.

## 1. Build artifacts

Make sure you have a clean working tree and an up-to-date Python environment.

We recommend using `uv` for local builds:

```bash
uv build
```

This will produce source and wheel distributions under the `dist/` directory.

Alternatively, you can use the standard Python build toolchain:

```bash
python -m build
```

## 2. Test the distribution locally

Before publishing, you can create a fresh virtual environment and install the built wheel:

```bash
python -m venv .venv-test
source .venv-test/bin/activate   # Windows: .venv-test\Scripts\activate
python -m pip install dist/copal_cli-<version>-py3-none-any.whl
copal --help
```

Replace `<version>` with the actual version you just built.

## 3. Publish to PyPI

## 3. Publish to PyPI

**Recommended**: Use `uv` for a fast and secure release.

```bash
# 1. Configure PyPI token (if not already set)
# export UV_PUBLISH_TOKEN=pypi-...

# 2. Publish
uv publish
```

**Alternative**: Use `twine`

```bash
python -m pip install twine
twine upload dist/*
```

## Release Workflow

### 1. Version Bump (Automated)

We use `bump-my-version` to manage version strings across the codebase (`pyproject.toml`, `init.py`, etc.).

```bash
# Bump patch version (0.1.0 -> 0.1.1)
uv run bump-my-version bump patch

# Bump minor version (0.1.0 -> 0.2.0)
uv run bump-my-version bump minor
```

This will automatically:

- Update version strings in all configured files.
- Create a git commit.
- Create a git tag (e.g., `v0.1.1`).

**Critical**: Push the commit and tags to the remote repository.

```bash
git push --follow-tags
```

### 2. Build

```bash
uv build
```

### 3. Publish to PyPI

```bash
uv publish
```
