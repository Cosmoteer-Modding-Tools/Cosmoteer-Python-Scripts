@echo off
:: Check if the script is running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
    cd /d "%~dp0"
    python "SymLinkCreator.py"
) else (
    echo Not running with administrator privileges. Elevating...
    :: Re-run this script as administrator
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d ""%~dp0"" && python ""SymLinkCreator.py""' -Verb RunAs"
)
