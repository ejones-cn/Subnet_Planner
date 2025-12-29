#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

os.chdir(r"f:\trae_projects\Netsub tools")

python_exe = r"f:\trae_projects\Netsub tools\.venv313\Scripts\python.exe"

cmd = [
    python_exe,
    "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--icon=icon.ico",
    "--name=SubnetPlanner",
    "--distpath=dist",
    "--workpath=build",
    "--clean",
    "--noconfirm",
    "--hidden-import=tkinter",
    "--hidden-import=reportlab",
    "--hidden-import=charset_normalizer",
    "--hidden-import=openpyxl",
    "--hidden-import=urllib",
    "--hidden-import=urllib3",
    "--add-data=icon.ico:.",
    "--noupx",
    "--disable-windowed-traceback",
    "--exclude-module=winreg",
    "--exclude-module=_winreg",
    "--exclude-module=win32service",
    "--exclude-module=win32timezone",
    "--exclude-module=xmlrpc",
    "--exclude-module=sqlite3",
    "windows_app.py"
]

print("=" * 60)
print("PyInstaller 打包命令")
print("=" * 60)
print(" ".join(cmd))
print("=" * 60)

result = subprocess.run(cmd, capture_output=True, text=True)

print("\n--- 标准输出 ---")
print(result.stdout)

print("\n--- 标准错误 ---")
print(result.stderr)

print(f"\n--- 返回码: {result.returncode} ---")

if result.returncode == 0:
    exe_path = r"f:\trae_projects\Netsub tools\dist\SubnetPlanner.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print("\n✅ 打包成功!")
        print(f"文件: {exe_path}")
        print(f"大小: {size_mb:.2f} MB")
    else:
        print("\n⚠️ 命令成功但EXE文件未找到")
else:
    print("\n❌ 打包失败!")

sys.exit(result.returncode)
