#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有文件中的版本号是否一致
"""

import re
import os

# 导入版本管理模块
from version import get_version

app_version = get_version()
print(f"当前版本号应该是: v{app_version}")
print("=" * 50)

# 检查README.md
with open("README.md", "r", encoding="utf-8") as f:
    readme_content = f.read()
match = re.search(r"# IP子网切分工具 v(\d+\.\d+\.\d+)", readme_content)
if match:
    readme_version = match.group(1)
    print(f"README.md 版本: v{readme_version}")
    print(f"状态: {'✓ 正确' if readme_version == app_version else '✗ 不一致'}")
else:
    print("README.md 版本: 未找到")
    print("状态: ✗ 错误")

print("-" * 50)

# 检查ip_subnet_calculator.py
import ip_subnet_calculator

print(f"ip_subnet_calculator.py 版本: v{ip_subnet_calculator.__version__}")
print(f"状态: {'✓ 正确' if ip_subnet_calculator.__version__ == app_version else '✗ 不一致'}")

print("-" * 50)

# 检查web_app.py
with open("web_app.py", "r", encoding="utf-8") as f:
    web_app_content = f.read()
matches = re.findall(r"v(\d+\.\d+\.\d+)", web_app_content)
if matches:
    # 获取所有匹配的版本号
    versions = set(matches)
    if len(versions) == 1 and versions.pop() == app_version:
        print("web_app.py 版本: 所有版本号一致")
        print(f"状态: ✓ 正确")
    else:
        print(f"web_app.py 版本: 发现多个版本号 {versions}")
        print("状态: ✗ 不一致")
else:
    print("web_app.py 版本: 未找到")
    print("状态: ✗ 错误")

print("-" * 50)

# 检查version.py
print(f"version.py 版本: v{app_version}")
print(f"状态: ✓ 正确")

print("=" * 50)
print("验证完成！")
