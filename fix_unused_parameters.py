#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复未使用的参数问题
"""

import re

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义正则表达式模式，匹配未使用的event参数
event_param_pattern = r'\s*def\s+\w+\(self,\s*event\s*\)'
event_param_pattern2 = r'\s*def\s+\w+\(self,\s*event\s*,\s*'

# 修复未使用的event参数，将其改为下划线_
fixed_content = re.sub(event_param_pattern, r'\g<0>'.replace('event', '_'), content)
fixed_content = re.sub(event_param_pattern2, r'\g<0>'.replace('event', '_'), fixed_content)

# 修复info_type未使用的参数
info_type_pattern = r'\s*def\s+\w+\(self,\s*\w+,\s*info_type="info"\)'
fixed_content = re.sub(info_type_pattern, r'\g<0>'.replace('info_type', '_'), fixed_content)

# 保存修复后的内容
with open('windows_app.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("已修复未使用的参数问题，将未使用的参数改为下划线_")
