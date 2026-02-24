<#
.SYNOPSIS
    Subnet Planner 编译脚本
.DESCRIPTION
    支持 Nuitka 和 PyInstaller 两种编译方式
    支持多文件模式和单文件模式
.EXAMPLE
    # 默认使用 Nuitka 多文件模式编译
    .\build_compile.ps1
    
    # 使用 PyInstaller 编译
    .\build_compile.ps1 --type pyinstaller
    
    # 使用单文件模式编译
    .\build_compile.ps1 --onefile
    
    # 显示详细帮助
    .\build_compile.ps1 --help
    
    # 同时使用两种编译器编译
    .\build_compile.ps1 --type both
#>

# 设置UTF-8编码
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "🔧 Subnet Planner 编译脚本 🔧" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "支持的编译器：Nuitka (默认)、PyInstaller、两者都编译" -ForegroundColor Green
Write-Host "支持的模式：单文件模式 (默认)、多文件模式" -ForegroundColor Green
Write-Host ""
Write-Host "📋 使用方法：" -ForegroundColor Yellow
Write-Host "   1. 直接运行：默认使用 Nuitka 单文件模式编译" -ForegroundColor White
Write-Host "   2. 指定编译器：.\build_compile.ps1 --type pyinstaller" -ForegroundColor White
Write-Host "   3. 多文件模式：.\build_compile.ps1 --no-onefile" -ForegroundColor White
Write-Host "   4. 显示详细帮助：.\build_compile.ps1 --help" -ForegroundColor White
Write-Host "   5. 编译所有版本：.\build_compile.ps1 --type both" -ForegroundColor White
Write-Host ""
Write-Host "🎯 推荐用法：" -ForegroundColor Yellow
Write-Host "   - 开发调试：多文件模式（编译快、启动快）" -ForegroundColor White
Write-Host "   - 分发部署：单文件模式（方便分发）" -ForegroundColor White
Write-Host "   - 全面测试：同时使用两种编译器编译" -ForegroundColor White
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 环境
Write-Host "🐍 检查 Python 环境..." -ForegroundColor Yellow
Try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
    Write-Host "✅ Python 环境正常" -ForegroundColor Green
} Catch {
    Write-Host "❌ 错误：未安装 Python 或 Python 未添加到 PATH 环境变量" -ForegroundColor Red
    Write-Host "   请安装 Python 3.10 或更高版本，并确保添加到 PATH" -ForegroundColor Red
    Read-Host "按 Enter 键退出..."
    exit 1
}
Write-Host ""

# 执行编译脚本
Write-Host "🚀 开始编译..." -ForegroundColor Yellow
$compileCommand = "python build_compile.py --onefile $args"
Write-Host "正在执行：$compileCommand" -ForegroundColor White
Write-Host ""

# 运行编译命令
Try {
    Invoke-Expression $compileCommand
    
    # 检查返回值
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "🎉 编译成功！" -ForegroundColor Green
        Write-Host "📦 输出文件：" -ForegroundColor Yellow
        Write-Host "   - Nuitka 多文件模式：当前目录下的 SubnetPlannerV*.exe" -ForegroundColor White
        Write-Host "   - Nuitka 单文件模式：当前目录下的 SubnetPlannerV*.exe" -ForegroundColor White
        Write-Host "   - PyInstaller：dist 目录下的 SubnetPlannerV*.exe" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 提示：" -ForegroundColor Yellow
        Write-Host "   - 多文件模式生成的程序启动更快，占用内存更小" -ForegroundColor White
        Write-Host "   - 单文件模式生成的程序更方便分发" -ForegroundColor White
        Write-Host "   - 若编译失败，请查看上面的错误信息" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "❌ 编译失败！" -ForegroundColor Red
        Write-Host "   请查看上面的错误信息，或使用 --help 查看详细帮助" -ForegroundColor White
        Write-Host "   常见问题：" -ForegroundColor Yellow
        Write-Host "   1. 缺少依赖库，请先安装依赖" -ForegroundColor White
        Write-Host "   2. 杀毒软件阻止编译，请暂时关闭杀毒软件" -ForegroundColor White
        Write-Host "   3. 权限问题，请以管理员身份运行本脚本" -ForegroundColor White
    }
} Catch {
    Write-Host ""
    Write-Host "❌ 执行编译命令时发生错误：$($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "编译脚本执行完毕" -ForegroundColor Cyan
Read-Host "按 Enter 键退出..."
