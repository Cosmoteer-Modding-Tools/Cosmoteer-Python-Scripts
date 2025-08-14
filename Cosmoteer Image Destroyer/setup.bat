@echo off
setlocal
title Cosmoteer Image Destroyer - Setup

echo Setting up virtual environment...

REM Always run from this script's folder
pushd "%~dp0"

REM Check if Python is installed
python --version
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python before proceeding.
    popd
    pause
    exit /b
)

REM Create venv if missing
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo Failed to create virtual environment.
        popd
        pause
        exit /b
    )
) ELSE (
    echo Virtual environment already exists. Skipping creation.
)

REM Activate venv
call venv\Scripts\activate
IF ERRORLEVEL 1 (
    echo Failed to activate virtual environment.
    popd
    pause
    exit /b
)

REM Upgrade pip to the latest version
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install or update dependencies
echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
IF ERRORLEVEL 1 (
    echo Failed to install dependencies.
    popd
    pause
    exit /b
)

echo Setup complete!
popd
pause
