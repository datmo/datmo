# Datmo Library Upgrade Guide

## Overview
This document outlines the changes made to upgrade the Datmo library from legacy Python 2/3 compatibility to modern Python 3.7+ support.

## Issues Addressed

### 1. Legacy Dependencies
The original `setup.py` contained very old pinned versions that were incompatible with modern Python environments:
- `numpy==1.15.4` (failed to compile on ARM64 Mac)
- `docker==3.6.0` (very outdated)
- `plotly==3.3.0` (missing many features)
- `flask>=0.10.1` (security vulnerabilities)
- Many other outdated packages

### 2. Python 2 Compatibility Code
The codebase contained unnecessary Python 2 compatibility branches and imports that are no longer needed.

## Changes Made

### 1. Updated setup.py
- **Removed Python 2/3 branching logic**
- **Updated all dependencies to modern versions**:
  - `numpy`: `1.15.4` → `>=1.21.0`
  - `docker`: `3.6.0` → `>=6.0.0`
  - `flask`: `>=0.10.1` → `>=2.0.0`
  - `plotly`: `3.3.0` → `>=5.0.0`
  - `requests`: `>=2.20.0` → `>=2.28.0`
  - `celery`: `4.2.1` → `>=5.2.0`
  - And many more...

- **Added modern setup.py features**:
  - `python_requires='>=3.7'`
  - `long_description_content_type='text/markdown'`
  - Proper classifiers for PyPI

### 2. Created Requirements Files
- **requirements.txt**: Core dependencies for production use
- **requirements-dev.txt**: Development dependencies including testing and code quality tools

### 3. Dependency Version Strategy
- Used minimum version constraints (`>=`) instead of exact pins where possible
- Ensured compatibility with Python 3.7-3.11
- Fixed specific packages that had limited version availability (e.g., `giturlparse.py`)

## Installation

### Fresh Installation
```bash
# Clone the repository
git clone https://github.com/datmo/datmo.git
cd datmo

# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black datmo/
isort datmo/
```

## Verification

The upgrade was successful as evidenced by:
1. ✅ Package installs without compilation errors
2. ✅ `datmo --help` command works
3. ✅ `datmo version` returns correct version
4. ✅ All core dependencies resolve properly

## Known Issues

### Dependency Conflicts
Some conflicts may occur with other packages in existing environments:
- MLflow, Streamlit, and other ML packages may have conflicting version requirements
- Consider using a fresh virtual environment for best results

### Python 2 Code Remnants
While the package now works with modern Python, there are still `from __future__ import` statements throughout the codebase. These are harmless in Python 3 but could be removed in a future cleanup.

## Recommendations

### For Users
1. **Use a fresh virtual environment** to avoid dependency conflicts
2. **Python 3.7+** is now required (Python 2 is no longer supported)
3. **Docker 6.0+** is required for containerization features

### For Developers
1. Consider removing `from __future__ import` statements in a future PR
2. Update CI/CD pipelines to test against Python 3.7-3.11
3. Consider updating the codebase to use modern Python features (f-strings, type hints, etc.)

## Testing

Basic functionality has been verified:
```bash
$ datmo --help     # ✅ Works
$ datmo version    # ✅ Returns 0.0.41-dev
```

For comprehensive testing, run the full test suite:
```bash
pytest datmo/
```

## Migration Notes

If you're upgrading from an older version:
1. **Backup your `.datmo` directory** before upgrading
2. **Update your Python environment** to 3.7+
3. **Reinstall the package** in a clean environment
4. **Test your existing projects** to ensure compatibility

## Support

If you encounter issues after the upgrade:
1. Check that you're using Python 3.7+
2. Try installing in a fresh virtual environment
3. Review the dependency conflicts section above
4. Open an issue on the GitHub repository with your environment details
