#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查找指定函数的调用位置
"""

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# 查找_calculate_auto_col_widths函数的调用
function_name = "_calculate_auto_col_widths"

print(f"=== 查找 {function_name} 函数的调用位置 ===")

for i, line in enumerate(lines, 1):
    if function_name in line and "def " not in line:
        print(f"第 {i} 行: {line.strip()}")
