#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移除文件开头的BOM（Byte Order Mark）字符
"""

import os

# 要处理的文件路径
file_path = "windows_app.py"

# 读取文件内容，使用二进制模式以正确处理BOM字符
with open(file_path, "rb") as f:
    content = f.read()

# 检查并移除BOM字符
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
    print(f"已移除文件 {file_path} 开头的BOM字符")
else:
    print(f"文件 {file_path} 开头没有BOM字符")

# 写回文件，使用二进制模式避免再次添加BOM字符
with open(file_path, "wb") as f:
    f.write(content)
