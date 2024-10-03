@echo off
REM setup.bat - Automated setup script for the Rules Generator with Translation

echo ==========================================
echo          Strings Generator Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python is not installed on this system.
    echo Would you like to download Python now? (Y/N)
    set /p choice=
    IF /I "%choice%"=="Y" (
        start https://www.python.org/downloads/
        echo Please install Python from the opened link, then run this setup script again.
    ) ELSE (
        echo Python is required to run this script. Exiting setup.
    )
    pause
    exit /b
) ELSE (
    echo Python is installed.
    python --version
)

echo.
echo Installing required Python packages...

REM Upgrade pip to the latest version
python -m pip install --upgrade pip

REM Install required packages
python -m pip install googletrans==4.0.0-rc1
python -m pip install pyinstaller

echo.
echo All required packages have been installed successfully!

echo.
echo Setup is complete. You can now run the script using run_script.bat.
pause
