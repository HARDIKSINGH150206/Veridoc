@echo off
setlocal
pushd "%~dp0.."
if errorlevel 1 exit /b 1
if not exist ".venv\Scripts\python.exe" (
    echo Dependencies are missing. Run uv sync from the repository folder first.
    popd
    exit /b 1
)
".venv\Scripts\python.exe" "packaging\launcher.py"
set "launcher_exit=%errorlevel%"
popd
exit /b %launcher_exit%
