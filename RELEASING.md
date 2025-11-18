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

If you want to publish `copal-cli` to PyPI, you can use either `twine` or `uv`:

```bash
# Using twine
python -m pip install twine
twine upload dist/*

# Or using uv (if configured)
uv publish
```

Make sure you have valid PyPI credentials configured before running these commands.

## 4. Versioning notes

* Update the `version` field in `pyproject.toml` before building a new release, or use your preferred version management strategy (e.g. tags + setuptools_scm).
* Keep the changelog (if any) and README in sync with the features included in the release.
