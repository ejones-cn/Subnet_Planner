#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os

os.chdir(r"f:\trae_projects\Subnet_Planner")

cmd = [
    r"C:\Users\ejone\AppData\Local\Programs\Python\Python314\python.exe",
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
    "--add-data=icon.ico;.",
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

print("执行打包命令...")
print(" ".join(cmd))

result = subprocess.run(cmd, capture_output=True, text=True)
print("标准输出:")
print(result.stdout)
print("标准错误:")
print(result.stderr)
print(f"返回码: {result.returncode}")

if result.returncode == 0:
    print("\n打包成功！")
    exe_path = r"f:\trae_projects\Subnet_Planner\dist\SubnetPlanner.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"文件: {exe_path}")
        print(f"大小: {size_mb:.2f} MB")
else:
    print("\n打包失败！")
