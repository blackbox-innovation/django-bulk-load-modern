#!/usr/bin/env bash
set -e

echo "Building django-bulk-load-modern..."

# Clean previous builds
rm -rf dist/
rm -rf *.egg-info/

# Build the package
echo "Building package with uv..."
uv build

# Show what was built
echo "Built packages:"
ls -la dist/

echo ""
echo "To publish to TestPyPI (for testing):"
echo "  uv publish --publish-url https://test.pypi.org/legacy/"
echo ""
echo "To publish to PyPI (for production):"
echo "  uv publish"
echo ""
echo "Make sure you have configured your PyPI credentials first:"
echo "  - Set PYPI_TOKEN environment variable, or"
echo "  - Configure ~/.pypirc file"