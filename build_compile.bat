@echo off
REM 设置命令提示符编码为UTF-8，支持中文显示
chcp 65001 >nul 2>&1

setlocal enabledelayedexpansion

REM Subnet Planner 编译脚本
REM 支持 Nuitka 和 PyInstaller 两种编译方式

:DISPLAY_HELP
echo ===========================================
echo 🔧 Subnet Planner 编译脚本 🔧
echo ===========================================
echo 支持的编译器：Nuitka (默认)、PyInstaller、两者都编译
echo 支持的模式：单文件模式 (默认)、多文件模式
echo.
echo 使用方法：
echo   1. 直接运行：默认使用 Nuitka 单文件模式编译
echo   2. 指定编译器：build_compile.bat --type pyinstaller
echo   3. 多文件模式：build_compile.bat --no-onefile
echo   4. 显示帮助：build_compile.bat --help
echo   5. 编译所有版本：build_compile.bat --type both
echo.
echo 推荐用法：
echo   - 开发调试：多文件模式（编译快、启动快）
echo   - 分发部署：单文件模式（方便分发）
echo   - 全面测试：同时使用两种编译器编译
echo ===========================================
echo.

:CHECK_PYTHON
REM 检查 Python 环境
echo 🐍 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误：未安装 Python 或 Python 未添加到 PATH 环境变量
echo    请安装 Python 3.10 或更高版本，并确保添加到 PATH
    pause
    exit /b 1
) else (
    python --version
    echo ✅ Python 环境正常
)
echo.

:RUN_COMPILE
echo 🚀 开始编译...
echo 正在执行：python build_compile.py --onefile %*
echo.

REM 执行编译脚本
python build_compile.py --onefile %*

if %errorlevel% equ 0 (
    echo.
    echo 🎉 编译成功！
    echo 📦 输出文件：
    echo    - Nuitka 多文件模式：当前目录下的 SubnetPlannerV*.exe
    echo    - Nuitka 单文件模式：当前目录下的 SubnetPlannerV*.exe
    echo    - PyInstaller：dist 目录下的 SubnetPlannerV*.exe
    echo.
    echo 💡 提示：
    echo    - 多文件模式生成的程序启动更快，占用内存更小
    echo    - 单文件模式生成的程序更方便分发
    echo    - 若编译失败，请查看上面的错误信息
) else (
    echo.
    echo ❌ 编译失败！
    echo    请查看上面的错误信息，或使用 --help 查看详细帮助
    echo    常见问题：
    echo    1. 缺少依赖库，请先安装依赖
    echo    2. 杀毒软件阻止编译，请暂时关闭杀毒软件
    echo    3. 权限问题，请以管理员身份运行本脚本
)

echo.
echo ===========================================
echo 编译脚本执行完毕
pause
endlocal