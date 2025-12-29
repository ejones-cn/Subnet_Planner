#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用 Nuitka 编译 Python 代码为真正的机器码 EXE 文件
Nuitka 会将 Python 代码编译为 C 代码，再编译为机器码
"""

import os
import subprocess
import sys
import shutil


def clean_old_builds():
    """清理旧的编译文件"""
    print("清理旧的编译文件...")
    dirs_to_clean = ["build", "dist", "windows_app.build", "windows_app.dist"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name} 目录")


def compile_with_nuitka():
    """使用 Nuitka 编译为机器码"""
    print("开始使用 Nuitka 编译为机器码...")
    
    # Nuitka 编译命令
    # --onefile: 生成单个 EXE 文件
    # --windows-disable-console: 禁用控制台窗口
    # --enable-plugin=tk-inter: 启用 tkinter 插件
    # --output-filename: 指定输出文件名
    # --include-data-files: 包含数据文件
    # --assume-yes-for-downloads: 自动下载依赖
    # --follow-imports: 跟踪所有导入
    # --output-dir: 输出目录
    
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--onefile",
        "--windows-disable-console",
        "--enable-plugin=tk-inter",
        "--output-filename=SubnetPlanner.exe",
        "--output-dir=dist",
        "--include-data-files=icon.ico=icon.ico",
        "--include-data-files=icon.png=icon.png",
        "--assume-yes-for-downloads",
        "--follow-imports",
        "--remove-output",
        "windows_app.py"
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("=" * 60)
        print("✅ 编译成功！")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"❌ 编译失败: {e}")
        return False


def check_result():
    """检查编译结果"""
    print("\n检查编译结果...")
    
    exe_path = os.path.join("dist", "SubnetPlanner.exe")
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"✅ EXE 文件已生成: {exe_path}")
        print(f"   文件大小: {file_size:.2f} MB")
        print(f"   绝对路径: {os.path.abspath(exe_path)}")
        return exe_path
    else:
        print("❌ EXE 文件未生成！")
        return None


def main():
    print("=" * 60)
    print("Nuitka 机器码编译器")
    print("=" * 60)
    print("将 Python 代码编译为真正的机器码 EXE 文件")
    print("=" * 60)
    print()
    
    # 清理旧文件
    clean_old_builds()
    print()
    
    # 执行编译
    if compile_with_nuitka():
        # 检查结果
        exe_path = check_result()
        if exe_path:
            print()
            print("=" * 60)
            print("✅ 编译完成！")
            print("=" * 60)
            print(f"生成的 EXE 文件: {exe_path}")
            print()
            print("💡 说明:")
            print("  - 这是真正的机器码 EXE 文件")
            print("  - 可以独立运行，无需 Python 环境")
            print("  - 性能优于 PyInstaller 打包")
            print("  - 更难被反编译")
            print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ 编译失败，请检查错误信息")
        print("=" * 60)


if __name__ == "__main__":
    main()
