:: run.bat
@echo off
REM ────────────────────────────────────────────────────────────
REM Activate the decal_namer virtual environment and run it
REM ────────────────────────────────────────────────────────────

REM 1) Check for venv
if not exist venv\Scripts\activate (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM 2) Activate and launch
call venv\Scripts\activate
python decal_namer.py
