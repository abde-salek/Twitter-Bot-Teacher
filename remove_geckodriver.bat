@echo off
echo ===================================
echo GeckoDriver Compatibility Fix Tool
echo ===================================

REM Check if running with admin privileges
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo This script needs to be run with administrator privileges.
    echo Right-click the batch file and select "Run as administrator"
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not found in your PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check for required files
if not exist remove_geckodriver.py (
    echo Error: remove_geckodriver.py not found
    pause
    exit /b 1
)

REM Run the script
echo Running GeckoDriver compatibility fix tool...
python remove_geckodriver.py

REM Check if the script ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===================================
    echo Tool ended with errors.
    echo See the logs above for details.
    echo ===================================
) else (
    echo.
    echo ===================================
    echo Tool completed successfully!
    echo ===================================
)

pause 