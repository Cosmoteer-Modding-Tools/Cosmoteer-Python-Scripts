@echo off
REM run_script.bat - Runs the Rules Generator with Translation

echo ==========================================
echo          Running Strings Generator
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed. Please run setup.bat first.
    pause
    exit /b
)

REM Check if the Python script exists
IF NOT EXIST "strings_generator.py" (
    echo Python script (strings_generator.py) not found in the current directory.
    echo Please ensure the script is present.
    pause
    exit /b
)

REM Run the Python script
python strings_generator.py

echo.
echo Script execution completed.
pause
