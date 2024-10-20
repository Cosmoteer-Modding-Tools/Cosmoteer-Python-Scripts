@echo off
echo Setting up virtual environment...

:: Check if Python is installed
python --version
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python before proceeding.
    pause
    exit /b
)

:: Check if virtual environment exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo Failed to create virtual environment.
        pause
        exit /b
    )
) ELSE (
    echo Virtual environment already exists. Skipping creation.
)

:: Activate virtual environment
call venv\Scripts\activate
IF ERRORLEVEL 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b
)

:: Upgrade pip to the latest version
echo Upgrading pip...
pip install --upgrade pip

:: Install or update dependencies
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo Failed to install dependencies.
    pause
    exit /b
)

echo Setup complete!
pause
