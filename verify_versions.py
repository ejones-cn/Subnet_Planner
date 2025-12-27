#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有文件中的版本号是否一致
"""

import re
import os
import ip_subnet_calculator

# 导入版本管理模块
from version import get_version as get_windows_version
from web_version import get_version as get_web_version

# 获取两个版本号
windows_version = get_windows_version()
web_version = get_web_version()

print("=" * 60)
print("子网规划师版本验证")
print("=" * 60)

# Windows版版本验证
print(f"Windows版当前版本号: v{windows_version}")
print("-" * 40)

# 检查README.md (Windows版)
with open("README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()
match = re.search(r"# 子网规划师 v(\d+\.\d+\.\d+)", readme_content)
if match:
    readme_version = match.group(1)
    print(f"README.md 版本: v{readme_version}")
    print(f"状态: {'✓ 正确' if readme_version == windows_version else '✗ 不一致'}")
else:
    print("README.md 版本: 未找到")
    print("状态: ✗ 错误")

print("-" * 40)

# 检查ip_subnet_calculator.py (Windows版)
print(f"ip_subnet_calculator.py 版本: v{ip_subnet_calculator.__version__}")
print(f"状态: {'✓ 正确' if ip_subnet_calculator.__version__ == windows_version else '✗ 不一致'}")

print("-" * 40)

# 检查version.py (Windows版)
print(f"version.py 版本: v{windows_version}")
print("状态: ✓ 正确")

print("\n" + "=" * 60)

# Web版版本验证
print(f"Web版当前版本号: v{web_version}")
print("-" * 40)

# 检查web_app.py (Web版)
# 检查是否正确导入了web_version模块
with open("web_app.py", "r", encoding="utf-8") as f:
    web_app_content = f.read()

# 检查版本导入语句是否正确
if "from web_version import __version__" in web_app_content:
    print("web_app.py 版本: 正确导入了web_version模块")
    print("状态: ✓ 正确")
else:
    print("web_app.py 版本: 未正确导入web_version模块")
    print("状态: ✗ 错误")

print("-" * 40)

# 检查web_version.py (Web版)
print(f"web_version.py 版本: v{web_version}")
print("状态: ✓ 正确")

print("=" * 60)
print("验证完成！")
