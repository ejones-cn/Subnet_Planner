@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo  Subnet Planner Build All Script
echo ========================================
echo.

set "PFX_PASSWORD="
set "SHOW_PASSWORD_PROMPT=1"
set "EXPECT_PASSWORD="

for /f "tokens=1,* delims= " %%A in ("%*") do (
    if /i "%%A"=="--password" (
        set "PFX_PASSWORD=%%B"
        set "SHOW_PASSWORD_PROMPT=0"
    ) else if /i "%%A"=="-p" (
        set "PFX_PASSWORD=%%B"
        set "SHOW_PASSWORD_PROMPT=0"
    )
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [INFO] Python detected
python --version
echo.

echo ========================================
echo  Step 1/2: Compile Program
echo ========================================
echo.

set "HAVE_CERT=0"
set "PFX_ARG="

if exist "subnetplanner.pfx" (
    set "HAVE_CERT=1"
    echo [INFO] Certificate found: subnetplanner.pfx
    
    if not "!PFX_PASSWORD!"=="" (
        echo [INFO] Password provided via command line
    ) else (
        echo.
        set /p "PFX_PASSWORD=Enter PFX password (Enter to skip): "
    )
    
    if not "!PFX_PASSWORD!"=="" (
        set "PFX_ARG=--pfx-password=!PFX_PASSWORD!"
        echo [INFO] Will sign code
    ) else (
        echo [INFO] Skipping code signing
    )
) else (
    echo [INFO] Certificate not found, skipping signing
)

python build_compile.py !PFX_ARG!

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Compilation failed!
    pause
    exit /b 1
)

echo.
echo [INFO] Compilation succeeded!
echo.

echo ========================================
echo  Step 2/2: Generate Installer
echo ========================================
echo.

if not exist "SubnetPlanner_Nuitka.dist" (
    echo [ERROR] Nuitka output not found
    pause
    exit /b 1
)

if not exist "SubnetPlanner_Nuitka.dist\SubnetPlanner.exe" (
    echo [ERROR] Main executable not found
    pause
    exit /b 1
)

set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if "!ISCC!"=="" (
    echo [ERROR] Inno Setup 6 not found
    pause
    exit /b 1
)

echo [INFO] Using Inno Setup: !ISCC!
echo.

if not exist "installer" mkdir installer

echo [INFO] Compiling installer...
call "!ISCC!" SubnetPlanner.iss

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installer compilation failed!
    pause
    exit /b 1
)

echo.
echo [INFO] Installer compiled!

if !HAVE_CERT! equ 1 (
    if not "!PFX_PASSWORD!"=="" (
        echo.
        echo [INFO] Starting code signing...

        set "SIGNTOOL="
        for /f "delims=" %%i in ('dir /b /ad /o-n "C:\Program Files (x86)\Windows Kits\10\bin\10.*" 2^>nul') do (
            if exist "C:\Program Files (x86)\Windows Kits\10\bin\%%i\x64\signtool.exe" (
                set "SIGNTOOL=C:\Program Files (x86)\Windows Kits\10\bin\%%i\x64\signtool.exe"
                goto :found_signtool
            )
        )
        :found_signtool

        if not "!SIGNTOOL!"=="" (
            set "SETUP_EXE=installer\SubnetPlannerV3.0.0_Setup.exe"
            echo [INFO] Signing installer...
            call "!SIGNTOOL!" sign /fd SHA256 /f "subnetplanner.pfx" /p "!PFX_PASSWORD!" /t "http://timestamp.digicert.com" "!SETUP_EXE!"

            if !errorlevel! equ 0 (
                echo [INFO] Installer signed successfully!
            ) else (
                echo [WARNING] Installer signing failed
            )
        ) else (
            echo [WARNING] signtool.exe not found, skipping sign
        )
    )
)

echo.
echo ========================================
echo  Build All Completed!
echo ========================================
echo.
echo Output:
if exist "installer\SubnetPlannerV3.0.0_Setup.exe" (
    echo   Installer: installer\SubnetPlannerV3.0.0_Setup.exe
)
echo   Build: SubnetPlanner_Nuitka.dist\
echo.
pause
