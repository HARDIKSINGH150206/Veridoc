# Developer Setup

This document explains how to set up a development machine for VeriDoc on Windows, macOS and Linux, run the app, run tests, check the model files and build the pendrive. The code does not exist yet, so every command that needs code is marked `TBD` and must be filled in when the code lands.

Last updated: 2026-10-25
Status: Draft v1

## 1. Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Git | Current | Branching rules in TEAM_GUIDE |
| Python | 3.11 or later | Used by the backend and tests |
| uv | Current | Dependency manager; `pyproject.toml` and `uv.lock` have one owner |
| Node.js | Current LTS | Only for running the JavaScript test vectors and linting the verify page; not needed at runtime |
| pre-commit | Current | Runs ruff and gitleaks on commit |
| C/C++ build tools | Platform default | Needed if `llama-cpp-python` builds from source |
| SQLAlchemy 2.0 and Alembic | Installed by uv | Database access and migrations; no separate server |

### Windows

1. Install Git, Python 3.11 or later, and Node.js LTS.
2. Install Visual Studio Build Tools with the C++ workload only if a wheel for `llama-cpp-python` is not available.
3. Install uv.
4. Use PowerShell or Git Bash.

### macOS

1. Install Xcode command line tools, then Git, Python 3.11 or later and Node.js.
2. Install uv.
3. On Apple Silicon use the native arm64 Python.

### Linux

1. Install Git, Python 3.11 or later, build-essential, and Node.js.
2. Install uv.

## 2. Clone and branch

```
git clone https://github.com/HARDIKSINGH150206/Veridoc.git Veridoc
cd Veridoc
git checkout dev
git checkout -b feat/<area>-<name>
```

Always branch from `dev`, never from `main`. Pull and rebase every morning: `git pull --rebase origin dev`. The beginner walkthrough, with commands for all three systems, is in [ONBOARDING](ONBOARDING.md); branch rules are in [GIT_WORKFLOW](GIT_WORKFLOW.md).

## 3. Environment

1. Copy `.env.example` to `.env` (the example file lists names only; see ARCHITECTURE section 12 for what each one means). `.env` is git-ignored and must never be committed.
2. Set `VERIDOC_HOME` to a folder outside the repository.

## 4. Install dependencies

| Step | Command |
|---|---|
| Create the environment and install | `uv sync` |
| Install pre-commit hooks | `uv run pre-commit install` (run once per clone) |
| Install JavaScript test dependencies | `TBD` |
| Create or upgrade the vault schema (Alembic) | `TBD` (will run `alembic upgrade head` against a vault under `VERIDOC_HOME`) |

## 5. Models

Models are not in the repository. `models/manifest.json` lists model names and SHA-256 hashes only. Exact models are `TBD` pending benchmarks.

1. Download the model files listed in the manifest from their official source into `VERIDOC_MODEL_DIR`.
2. Verify each file's SHA-256 against the manifest:
   - Linux and macOS: `shasum -a 256 <file>`
   - Windows PowerShell: `Get-FileHash <file> -Algorithm SHA256`
3. The app repeats this check at startup. A mismatch turns on safe mode.
4. Never commit model files. `.gitignore` blocks common weight formats.

Speech models for faster-whisper are downloaded the same way and listed in the manifest.

## 6. Run

| Task | Command |
|---|---|
| Start the app in development | `TBD` |
| Open the UI | `http://127.0.0.1:<port>` (the port is printed at startup) |
| Force safe mode | Set `VERIDOC_SAFE_MODE=1` (name only; behaviour `TBD`) |
| Open the verify page | Open `apps/verify/verify.html` directly in a browser |

## 7. Test and quality

Tests live inside each package under `packages/<name>/tests/`.

| Task | Command |
|---|---|
| Run all Python tests | `uv run pytest` (exits with code 5 while no tests exist yet) |
| Run one package's tests | `TBD` |
| Run the JavaScript cross-language vector test | `TBD` |
| Lint | `uv run ruff check .` and `uv run ruff format --check .` |
| Type check | `uv run mypy .` |
| Hardcoding check | `python scripts/check_hardcoding.py` (also runs in pre-commit) |
| Secret scan | runs in the pre-commit hook; manually: `uv run pre-commit run gitleaks --all-files` |
| Dependency audit | `TBD` (pip-audit) |
| Trust report | `TBD` |
| Offline check (all screens load with the network blocked) | `TBD` |
| Migration check (insert-only triggers block UPDATE and DELETE after `alembic upgrade head`) | `TBD` |

All of these run in CI once `.github/workflows/` is added.

## 8. Pendrive build

1. Format a USB 3 stick as exFAT.
2. Build the release folder with `TBD`.
3. The folder holds: `START.bat`, `start.sh`, portable Python runtimes for Windows, macOS and Linux, the app, bundled web assets, `verify.html`, `models/manifest.json`, and the model files (hash-checked).
4. Copy the folder to the stick using relative paths only.
5. On first run the app detects the hardware tier and selects a model.
6. Test on a second laptop with the network off, and with the default antivirus on Windows.

## 9. Troubleshooting

| Problem | Likely cause | Action |
|---|---|---|
| Safe mode banner | Model missing, hash mismatch or low RAM | Open S11 for the reason; re-download the model |
| Antivirus blocks the launcher | Unknown executable | Use the pre-tested runtimes; see PERFORMANCE |
| Hindi text shows boxes | Fonts not bundled | Check `apps/web/assets` for Noto Devanagari |
| Port in use | Another app | Set `VERIDOC_PORT` |
