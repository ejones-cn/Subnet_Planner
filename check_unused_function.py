#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查未使用的函数
"""

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print("=== 检查未使用的函数 ===")

# 查找 _update_background_to_result_frame_color 函数的定义和调用
function_name = "_update_background_to_result_frame_color"
print(f"查找 {function_name} 函数的定义和调用")

def_line = None
call_lines = []

for i, line in enumerate(lines, 1):
    if f"def {function_name}" in line:
        def_line = i
    elif function_name in line and "def " not in line and "class " not in line:
        call_lines.append((i, line.strip()))

if def_line:
    print(f"找到函数定义: 第 {def_line} 行")
else:
    print("未找到函数定义")

if call_lines:
    print("找到函数调用:")
    for line_num, line_content in call_lines:
        print(f"第 {line_num} 行: {line_content}")
else:
    print("未找到函数调用，该函数未被使用")
    
    # 如果函数未被使用，删除函数定义
    print(f"\n将删除未使用的 {function_name} 函数")
    
    # 查找函数定义的完整范围
    if def_line:
        # 从函数定义开始，找到下一个函数定义或类定义
        end_line = len(lines)
        for i in range(def_line, len(lines)):
            if re.match(r'^\s*(def\s+|class\s+)', lines[i]):
                end_line = i
                break
        
        # 删除函数定义
        new_lines = []
        for i, line in enumerate(lines, 1):
            if i < def_line or i >= end_line:
                new_lines.append(line)
        
        # 保存修复后的内容
        with open('windows_app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"已删除第 {def_line} 行到第 {end_line-1} 行的未使用函数")

print("\n=== 检查完成 ===")
