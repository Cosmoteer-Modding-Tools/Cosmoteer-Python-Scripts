@echo off
REM ────────────────────────────────────────────────────────────
REM Create & configure a virtual environment for the tool
REM ────────────────────────────────────────────────────────────

REM 1) Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

REM 2) Create venv
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

REM 3) Activate venv
call venv\Scripts\activate

REM 4) Ensure qtpy uses PySide6
set QT_API=pyside6

REM 5) Upgrade pip & install deps
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo To launch the tool, run ^"run.bat^"
pause
