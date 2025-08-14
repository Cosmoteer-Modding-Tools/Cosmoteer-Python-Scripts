@echo off
setlocal
title Cosmoteer Image Destroyer

echo Running Cosmoteer Image Destroyer...

REM Always run from this script's folder (handles spaces in paths)
pushd "%~dp0"

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
  echo Virtual environment not found. Run setup.bat first.
  pause
  popd
  exit /b 1
)
call "venv\Scripts\activate.bat"

REM Run the Python script
python "damage_painter.py"

popd
pause
