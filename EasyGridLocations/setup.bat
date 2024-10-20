@echo off
echo Setting up virtual environment...

:: Check if Python is installed
python --version
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python before proceeding.
    pause
    exit /b
)

:: Create virtual environment
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

echo Setup complete!
pause
