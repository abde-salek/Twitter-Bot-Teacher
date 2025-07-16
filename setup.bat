@echo off
echo ===================================
echo Flutter Daily Tweet Bot - Setup
echo ===================================

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not found in your PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check for required files
if not exist setup_env.py (
    echo Error: setup_env.py not found
    pause
    exit /b 1
)

if not exist requirements.txt (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

REM Install dependencies
echo Installing required packages...
python -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo.
    echo Failed to install requirements.
    pause
    exit /b 1
)

REM Run setup script
echo.
echo Running environment setup...
python setup_env.py

REM Check if the script ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===================================
    echo Setup ended with errors.
    echo See the logs above for details.
    echo ===================================
) else (
    echo.
    echo ===================================
    echo Setup completed successfully!
    echo ===================================
    echo.
    echo You can now run the bot using run_bot.bat
)

pause 