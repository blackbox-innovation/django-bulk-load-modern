# Publishing django-bulk-load-modern to PyPI

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Create an API token at https://pypi.org/manage/account/token/
3. Save your token securely

## Setting up Authentication

### Option 1: Environment Variable (Recommended)
```bash
export PYPI_TOKEN="pypi-..."
```

### Option 2: .pypirc file
Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
```

## Testing with TestPyPI (Recommended First Step)

1. Create a TestPyPI account at https://test.pypi.org/account/register/
2. Create a TestPyPI token at https://test.pypi.org/manage/account/token/
3. Build and publish to TestPyPI:
   ```bash
   ./build_and_publish.sh
   uv publish --publish-url https://test.pypi.org/legacy/
   ```
4. Test installation from TestPyPI:
   ```bash
   uv pip install --index-url https://test.pypi.org/simple/ django-bulk-load-modern
   ```

## Publishing to PyPI

Once you've tested on TestPyPI:

```bash
# Build the package
./build_and_publish.sh

# Publish to PyPI
uv publish
```

## Post-Publication

1. Test installation:
   ```bash
   uv pip install django-bulk-load-modern
   ```

2. Update the GitHub repository:
   ```bash
   git add -A
   git commit -m "feat: initial release of django-bulk-load-modern v2.0.0"
   git push fork main
   ```

3. Create a GitHub release:
   - Go to https://github.com/blackbox-innovation/django-bulk-load-modern/releases
   - Click "Create a new release"
   - Tag: v2.0.0
   - Title: "django-bulk-load-modern v2.0.0"
   - Description: Include key features and migration notes

## Version Updates

For future releases:
1. Update version in `pyproject.toml` and `setup.py`
2. Update CHANGELOG_FORK.md
3. Build and test
4. Publish to PyPI
5. Create GitHub release