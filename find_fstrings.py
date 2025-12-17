#!/usr/bin/env python3

import re
import sys

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.readlines()

# 查找所有没有占位符的f-string
fstring_pattern = re.compile(r'f"[^"]*"')
placeholder_pattern = re.compile(r'\{[^\}]*\}')

for line_num, line in enumerate(content, 1):
    fstrings = fstring_pattern.findall(line)
    for fstring in fstrings:
        if not placeholder_pattern.search(fstring):
            print(f"Line {line_num}: {fstring}")
