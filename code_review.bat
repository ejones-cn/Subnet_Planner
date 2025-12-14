@echo off
chcp 65001 >nul
rem Batch file to run code review tools

echo ======================================
echo IP Subnet Splitter Tool - Code Review
echo ======================================

rem Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python interpreter not found. Please ensure Python is installed and added to system environment variables.
    pause
    exit /b 1
)

rem Check if required tools are installed
echo Checking if code review tools are installed...
python -m pip show pylint flake8 black isort >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing code review tools...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install code review tools.
        pause
        exit /b 1
    )
)

rem Run code review tools

echo.
echo ======================================
echo Running Pylint (Code Quality Check)...
echo ======================================
python -m pylint *.py

if %errorlevel% neq 0 (
    echo Pylint check completed with issues.
)

rem Wait for user input
echo.
echo Press any key to continue with Flake8...
pause >nul


echo.
echo ======================================
echo Running Flake8 (Code Style Check)...
echo ======================================
python -m flake8 *.py

if %errorlevel% neq 0 (
    echo Flake8 check completed with issues.
)

rem Wait for user input
echo.
echo Press any key to continue with isort...
pause >nul


echo.
echo ======================================
echo Running isort (Import Sorting)...
echo ======================================
python -m isort --check --diff *.py

if %errorlevel% neq 0 (
    echo isort found issues with import sorting.
    echo Press any key to automatically fix import sorting...
    pause >nul
    python -m isort *.py
)

rem Wait for user input
echo.
echo Press any key to continue with Black...
pause >nul


echo.
echo ======================================
echo Running Black (Code Formatting)...
echo ======================================
python -m black --check --diff *.py

if %errorlevel% neq 0 (
    echo Black found issues with code formatting.
    echo Press any key to automatically format code...
    pause >nul
    python -m black *.py
)


echo.
echo ======================================
echo Code Review Completed!
echo ======================================

rem Final check
python -m compileall *.py >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Syntax errors found during compile check.
) else (
    echo Compile check passed, code syntax is correct.
)

echo.
echo Review Tools Summary:
echo 1. Pylint: Code quality and potential issues
echo 2. Flake8: Code style consistency (PEP 8)
echo 3. isort: Import statement organization
echo 4. Black: Code formatting standardization
echo 5. compileall: Syntax correctness verification
echo.
pause
