@echo off
rem Batch file to run IP Subnet Splitter Tool

echo Starting IP Subnet Splitter Tool...

rem Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
)

rem Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python interpreter not found. Please ensure Python is installed and added to system environment variables.
    pause
    exit /b 1
)

rem Run the application
python windows_app.py

rem Check if application exited normally
if %errorlevel% neq 0 (
    echo Application exited abnormally, error code: %errorlevel%
    pause
    exit /b %errorlevel%
)

echo Application closed normally.
pause