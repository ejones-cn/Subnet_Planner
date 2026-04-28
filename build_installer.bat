@echo off
chcp 65001 >nul
echo ========================================
echo  Subnet Planner 安装包编译脚本
echo ========================================
echo.

:: 设置变量
set "VERSION=3.0.0"
set "PACKAGE_DIR=SubnetPlannerV%VERSION%_Package"
set "NUITKA_DIR=SubnetPlanner_Nuitka.dist"

:: 检查 Inno Setup 是否安装
if not exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    echo [错误] 未检测到 Inno Setup 6
    echo 请先安装 Inno Setup 6
    echo 下载地址: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

:: 设置 ISCC 路径
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

:: 检查打包目录是否存在
if not exist "%PACKAGE_DIR%" (
    echo [警告] 未找到标准打包目录: %PACKAGE_DIR%
    
    :: 检查 Nuitka 编译目录
    if exist "%NUITKA_DIR%" (
        echo [信息] 检测到 Nuitka 编译输出目录: %NUITKA_DIR%
        echo [信息] 将使用该目录进行打包
        echo.
    ) else (
        echo [警告] 也未找到 Nuitka 编译目录: %NUITKA_DIR%
        echo.
        echo [询问] 是否需要先运行编译脚本？
        echo 1. 运行 build_compile.py (Nuitka 编译)
        echo 2. 运行 build_package.py (编译+打包)
        echo 3. 手动准备打包目录，稍后重试
        echo.
        set /p "choice=请输入选项 [1/2/3]: "
        
        if "%choice%"=="1" (
            echo.
            echo [信息] 正在运行 build_compile.py...
            python build_compile.py
            if %errorlevel% neq 0 (
                echo [错误] 编译失败！
                pause
                exit /b 1
            )
        ) else if "%choice%"=="2" (
            echo.
            echo [信息] 正在运行 build_package.py...
            python build_package.py
            if %errorlevel% neq 0 (
                echo [错误] 打包失败！
                pause
                exit /b 1
            )
        ) else if "%choice%"=="3" (
            echo [信息] 请手动准备打包目录，然后重新运行此脚本
            pause
            exit /b 0
        ) else (
            echo [错误] 无效选项！
            pause
            exit /b 1
        )
    )
)

:: 创建输出目录
if not exist "installer" mkdir installer

:: 编译安装包
echo.
echo [信息] 开始编译安装包...
echo.
%ISCC% SubnetPlanner.iss

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  安装包编译成功！
    echo  输出目录: installer\
    echo ========================================
) else (
    echo.
    echo [错误] 安装包编译失败！
)

echo.
pause
