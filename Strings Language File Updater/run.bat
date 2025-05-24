@echo off
REM ────────────────────────────────────────────────────────────
REM Activate the tool’s venv and launch it
REM ────────────────────────────────────────────────────────────

REM 1) Make sure venv is present
if not exist venv\Scripts\activate (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

REM 2) Activate & force qtpy binding
call venv\Scripts\activate
set QT_API=pyside6

REM 3) Launch
python stringsorganizer.py
