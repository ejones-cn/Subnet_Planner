#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Python环境脚本
用于查看编辑器运行按钮使用的Python解释器和模块搜索路径
"""

import sys
import os

print("=== Python环境调试信息 ===")
print(f"Python解释器路径: {sys.executable}")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"脚本文件路径: {os.path.abspath(__file__)}")
print("\n=== 模块搜索路径 ===")
for path in sys.path:
    print(path)
print("\n=== 已安装的reportlab模块信息 ===")
try:
    import reportlab
    print(f"reportlab版本: {reportlab.__version__}")
    print(f"reportlab安装路径: {reportlab.__file__}")
except ImportError as e:
    print(f"reportlab未安装或无法导入: {e}")
    print("\n=== 尝试使用pip安装reportlab ===")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "reportlab"], 
                               capture_output=True, text=True, timeout=30)
        print(f"pip安装输出:\n{result.stdout}")
        if result.stderr:
            print(f"pip安装错误:\n{result.stderr}")
        # 再次尝试导入
        import reportlab
        print(f"\n✓ reportlab安装成功，版本: {reportlab.__version__}")
    except Exception as install_error:
        print(f"pip安装失败: {install_error}")

input("\n按回车键退出...")
