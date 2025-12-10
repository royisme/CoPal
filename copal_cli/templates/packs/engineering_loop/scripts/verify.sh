#!/bin/bash
# Default verification script for Engineering Loop
# This script attempts to run common verification tools.
# You should customize this or point manifest.verify.command to your own script.

echo "🔍 Running Verification..."

# 1. Try to detect and run project tests
if [ -f "pyproject.toml" ]; then
    if command -v pytest &> /dev/null; then
        echo "Running pytest..."
        pytest
        exit $?
    fi
elif [ -f "package.json" ]; then
    echo "Running npm test..."
    npm test
    exit $?
elif [ -f "Makefile" ]; then
    echo "Running make test..."
    make test
    exit $?
fi

echo "⚠️ No standard verification found. Please edit this script or .copal/manifest.yaml."
exit 0
