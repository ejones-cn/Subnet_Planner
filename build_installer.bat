@echo off
chcp 65001 >nul
echo ========================================
echo  Subnet Planner 安装包编译脚本
echo ========================================
echo.

:: 设置变量
set "VERSION=3.0.0"
set "NUITKA_DIR=SubnetPlanner_Nuitka.dist"
set "PFX_FILE=subnetplanner.pfx"
set "SETUP_EXE=installer\SubnetPlannerV%VERSION%_Setup.exe"

:: 查找 Inno Setup 6 安装路径
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if "%ISCC%"=="" (
    echo [错误] 未检测到 Inno Setup 6
    echo 请先安装 Inno Setup 6
    echo 下载地址: https://jrsoftware.org/isdl.php
    echo 或使用 winget 安装: winget install JRSoftware.InnoSetup
    echo.
    pause
    exit /b 1
)

echo [信息] 使用 Inno Setup: %ISCC%
echo.

:: 检查 Nuitka 编译目录是否存在
if not exist "%NUITKA_DIR%" (
    echo [错误] 未找到编译输出目录: %NUITKA_DIR%
    echo.
    echo 请先运行编译脚本:
    echo   python build_compile.py
    echo.
    pause
    exit /b 1
)

:: 检查主程序是否存在
if not exist "%NUITKA_DIR%\SubnetPlanner.exe" (
    echo [错误] 未找到主程序: %NUITKA_DIR%\SubnetPlanner.exe
    echo.
    echo 请先运行编译脚本:
    echo   python build_compile.py
    echo.
    pause
    exit /b 1
)

:: 创建输出目录
if not exist "installer" mkdir installer

:: 编译安装包
echo [信息] 开始编译安装包...
echo.
"%ISCC%" SubnetPlanner.iss

if %errorlevel% neq 0 (
    echo.
    echo [错误] 安装包编译失败！
    pause
    exit /b 1
)

echo.
echo [信息] 安装包编译成功！

:: 数字签名
if exist "%PFX_FILE%" (
    echo.
    echo [信息] 检测到代码签名证书，开始签名...

    :: 查找 signtool
    set "SIGNTOOL="
    for /f "delims=" %%i in ('dir /b /ad /o-n "C:\Program Files (x86)\Windows Kits\10\bin\10.*" 2^>nul') do (
        if exist "C:\Program Files (x86)\Windows Kits\10\bin\%%i\x64\signtool.exe" (
            set "SIGNTOOL=C:\Program Files (x86)\Windows Kits\10\bin\%%i\x64\signtool.exe"
            goto :found_signtool
        )
    )
    :found_signtool

    if not "%SIGNTOOL%"=="" (
        :: 检查环境变量中是否已设置密码，优先使用环境变量
        if defined PFX_PASSWORD (
            set "SIGN_PASSWORD=%PFX_PASSWORD%"
            echo [信息] 使用环境变量中的证书密码进行签名
            echo [提示] 如需更换密码，请先设置: set PFX_PASSWORD=your_password
        ) else (
            echo [提示] PFX_PASSWORD 环境变量未设置，将尝试使用空密码签名
            echo [警告] 未检测到 PFX_PASSWORD 环境变量，将使用空密码
            set "SIGN_PASSWORD="
        )

        echo.
        echo [信息] 正在签名安装包...
        "%SIGNTOOL%" sign /fd SHA256 /f "%PFX_FILE%" /p "%SIGN_PASSWORD%" /t "http://timestamp.digicert.com" "%SETUP_EXE%"

        if !errorlevel! equ 0 (
            echo [信息] 安装包签名成功！
        ) else (
            echo [警告] 安装包签名失败，但不影响使用
        )

        echo.
        echo [信息] 正在签名主程序...
        "%SIGNTOOL%" sign /fd SHA256 /f "%PFX_FILE%" /p "%SIGN_PASSWORD%" /t "http://timestamp.digicert.com" "%NUITKA_DIR%\SubnetPlanner.exe"

        if !errorlevel! equ 0 (
            echo [信息] 主程序签名成功！
        ) else (
            echo [警告] 主程序签名失败，但不影响使用
        )
    ) else (
        echo [警告] 未找到 signtool.exe，跳过签名
        echo [提示] 安装 Windows SDK 后可启用签名功能
    )
) else (
    echo.
    echo [提示] 未检测到代码签名证书 (%PFX_FILE%)
    echo [提示] 添加数字签名可减少杀毒软件误报
)

echo.
echo ========================================
echo  安装包构建完成！
echo  输出文件: %SETUP_EXE%
echo ========================================
echo.
pause
