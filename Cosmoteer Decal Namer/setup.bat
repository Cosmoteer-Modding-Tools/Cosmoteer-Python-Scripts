:: setup.bat
@echo off
REM ────────────────────────────────────────────────────────────
REM Create and configure a virtual environment for decal_namer
REM ────────────────────────────────────────────────────────────

REM 1) Make sure Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8 or later.
    pause
    exit /b 1
)

REM 2) Create venv folder
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    pause
    exit /b 1
)

REM 3) Activate venv
call venv\Scripts\activate

REM 4) Upgrade pip and install dependencies
pip install --upgrade pip
pip install PySide6 Pillow

echo.
echo Setup complete!  
echo Run ^"run.bat^" to launch the decal namer.
pause
