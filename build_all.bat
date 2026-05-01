@echo off
chcp 65001 >nul
echo ========================================
echo  Subnet Planner 一键打包脚本
echo ========================================
echo.

:: 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] 检测到 Python 环境
python --version
echo.

:: 步骤1：编译程序
echo ========================================
echo  步骤 1/2：编译程序
echo ========================================
echo.

:: 检查是否设置了 PFX_PASSWORD 环境变量
if defined PFX_PASSWORD (
    set "PFX_ARG=--pfx-password=%PFX_PASSWORD%"
    echo [信息] 检测到 PFX_PASSWORD 环境变量，将使用证书签名
) else (
    set "PFX_ARG="
    echo [提示] 未设置 PFX_PASSWORD 环境变量，编译将跳过签名
    echo [提示] 如需签名，请先设置: set PFX_PASSWORD=your_password
    echo.
)

python build_compile.py %PFX_ARG%

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序编译失败！
    pause
    exit /b 1
)

echo.
echo [信息] 程序编译成功！
echo.

:: 步骤2：生成安装包
echo ========================================
echo  步骤 2/2：生成安装包
echo ========================================
echo.

:: 检查 Nuitka 输出目录是否存在
if not exist "SubnetPlanner_Nuitka.dist" (
    echo [错误] 未找到编译输出目录: SubnetPlanner_Nuitka.dist
    echo.
    pause
    exit /b 1
)

:: 检查主程序是否存在
if not exist "SubnetPlanner_Nuitka.dist\SubnetPlanner.exe" (
    echo [错误] 未找到主程序: SubnetPlanner_Nuitka.dist\SubnetPlanner.exe
    echo.
    pause
    exit /b 1
)

:: 查找 Inno Setup 6
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

:: 创建输出目录
if not exist "installer" mkdir installer

:: 编译安装包
echo [信息] 开始编译安装包...
"%ISCC%" SubnetPlanner.iss

if %errorlevel% neq 0 (
    echo.
    echo [错误] 安装包编译失败！
    pause
    exit /b 1
)

echo.
echo [信息] 安装包编译成功！

:: 数字签名（如有证书）
if exist "subnetplanner.pfx" (
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
        :: 检查环境变量中是否已设置密码
        if defined PFX_PASSWORD (
            set "SIGN_PASSWORD=%PFX_PASSWORD%"
            echo [信息] 使用环境变量中的证书密码进行签名
            echo [提示] 如需更换密码，请先设置: set PFX_PASSWORD=your_password
        ) else (
            echo [警告] 未检测到 PFX_PASSWORD 环境变量，将使用空密码
            set "SIGN_PASSWORD="
        )

        set "SETUP_EXE=installer\SubnetPlannerV3.0.0_Setup.exe"

        echo.
        echo [信息] 正在签名安装包...
        "%SIGNTOOL%" sign /fd SHA256 /f "subnetplanner.pfx" /p "%SIGN_PASSWORD%" /t "http://timestamp.digicert.com" "%SETUP_EXE%"

        if !errorlevel! equ 0 (
            echo [信息] 安装包签名成功！
        ) else (
            echo [警告] 安装包签名失败，但不影响使用
        )
    ) else (
        echo [警告] 未找到 signtool.exe，跳过签名
        echo [提示] 安装 Windows SDK 后可启用签名功能
    )
) else (
    echo.
    echo [提示] 未检测到代码签名证书 (subnetplanner.pfx)
    echo [提示] 添加数字签名可减少杀毒软件误报
)

echo.
echo ========================================
echo  一键打包完成！
echo ========================================
echo.
echo 输出文件:
if exist "installer\SubnetPlannerV3.0.0_Setup.exe" (
    echo   安装包: installer\SubnetPlannerV3.0.0_Setup.exe
    for %%A in ("installer\SubnetPlannerV3.0.0_Setup.exe") do echo   大小: %%~zA 字节
)
echo   编译输出: SubnetPlanner_Nuitka.dist\
echo.
pause
