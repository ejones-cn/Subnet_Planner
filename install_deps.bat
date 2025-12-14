@echo off
rem Batch file to install dependencies with domestic PyPI mirror

echo Installing dependencies with domestic PyPI mirror (aliyun)...

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

rem Install dependencies with domestic mirror
python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

rem Check if installation succeeded
if %errorlevel% neq 0 (
    echo Error: Dependency installation failed, error code: %errorlevel%
    pause
    exit /b %errorlevel%
)

echo Dependencies installed successfully.
pause
