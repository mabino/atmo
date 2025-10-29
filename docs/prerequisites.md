# Development Prerequisites

## macOS Requirements
- macOS 13 Ventura or later
- Xcode 16+ with command-line tools installed (`xcode-select --install`)
- Swift toolchain that supports SwiftUI for macOS (bundled with Xcode)

## Python Environment
- Python 3.9.6 (matches `pybridge/python-version.txt`)
- Local virtual environment located at `.venv`
- Align the environment with the locked dependency set:
  ```bash
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install --requirement pybridge/requirements.lock
  ```
- Install local test tooling (not bundled in the runtime lockfile):
  ```bash
  .venv/bin/pip install pytest
  ```
- Run the Python test suite via the interpreter so the repository root stays on `sys.path`:
  ```bash
  .venv/bin/python -m pytest tests
  ```
- If `.venv` already exists, remove it first (`rm -rf .venv`) or rerun the `pip install --requirement` step to sync with the lockfile.

## Additional Tools
- `pytest` (to be installed when Python bridge tests are added)
- `xcodebuild` available on PATH for CI/test automation
