#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新web_app.py中的版本号脚本
"""

import re

# 导入版本管理模块
from version import get_version

app_version = get_version()

# 读取web_app.py文件
with open("web_app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 替换所有硬编码的版本号
content = re.sub(r"v\d+\.\d+\.\d+", f"v{app_version}", content)

# 写回文件
with open("web_app.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"已更新web_app.py中的版本号为 v{app_version}")
