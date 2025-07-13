@echo off
echo ===================================
echo Flutter Daily Tweet Bot - MOCK MODE
echo ===================================
echo Running in mock mode - no actual API calls will be made

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not found in your PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check for required files
if not exist main.py (
    echo Error: main.py not found
    pause
    exit /b 1
)

REM Run the script in mock mode
echo Running Flutter Daily Tweet Bot in MOCK MODE...
python main.py --mock

REM Check if the script ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===================================
    echo Script ended with errors.
    echo See the logs above for details.
    echo ===================================
    pause
) else (
    echo.
    echo ===================================
    echo Bot completed successfully in MOCK MODE!
    echo ===================================
)

pause 