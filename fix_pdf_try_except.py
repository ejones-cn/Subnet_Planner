#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复windows_app.py文件中PDF导出部分的try-except语法错误
"""

import os

def fix_pdf_try_except():
    """修复PDF导出部分的try-except语法错误"""
    # 读取文件内容
    with open('windows_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找PDF导出部分
    pdf_start = content.find('elif file_ext == \".pdf\":')
    if pdf_start == -1:
        print("未找到PDF导出部分")
        return
    
    pdf_end = content.find('elif file_ext == \".xlsx\":', pdf_start)
    if pdf_end == -1:
        print("未找到Excel导出部分，无法确定PDF导出结束位置")
        return
    
    # 提取PDF导出部分
    pdf_content = content[pdf_start:pdf_end]
    
    # 查找try块开始位置
    try_start = pdf_content.find('try:')
    if try_start == -1:
        print("未找到try块")
        return
    
    # 查找try块结束位置（需要正确匹配缩进）
    # 计算try块的缩进级别
    try_line = pdf_content[:try_start].split('\n')[-1]
    try_indent = len(try_line) - len(try_line.lstrip())
    
    # 分割PDF内容为行
    pdf_lines = pdf_content.split('\n')
    
    # 查找try块的结束行（即下一个与try块同一缩进级别的except或finally）
    try_block_end = -1
    in_try_block = False
    
    for i, line in enumerate(pdf_lines):
        if 'try:' in line:
            in_try_block = True
            current_indent = len(line) - len(line.lstrip())
            continue
            
        if in_try_block:
            stripped_line = line.lstrip()
            if not stripped_line:  # 空行
                continue
                
            # 检查是否是except或finally
            if stripped_line.startswith('except') or stripped_line.startswith('finally'):
                # 检查缩进是否与try块相同
                line_indent = len(line) - len(line.lstrip())
                if line_indent == current_indent:
                    try_block_end = i
                    break
    
    if try_block_end == -1:
        print("未找到try块的结束位置")
        return
    
    # 输出调试信息
    print(f"try块开始行: {try_start}")
    print(f"try块结束行: {try_block_end}")
    
    # 修复缩进问题
    # 重新构建PDF导出部分
    new_pdf_content = []
    in_try = False
    
    for i, line in enumerate(pdf_lines):
        if 'try:' in line:
            in_try = True
            new_pdf_content.append(line)
        elif in_try:
            stripped_line = line.lstrip()
            if stripped_line.startswith('except') or stripped_line.startswith('finally'):
                # 检查缩进
                line_indent = len(line) - len(line.lstrip())
                if line_indent == try_indent:
                    in_try = False
                    new_pdf_content.append(line)
                else:
                    # 这是try块内部的except，保持原样
                    new_pdf_content.append(line)
            else:
                # 确保所有try块内部的行都有正确的缩进
                if line.strip() and not line.strip().startswith('#'):
                    # 检查缩进是否正确
                    line_indent = len(line) - len(line.lstrip())
                    if line_indent < current_indent + 4:
                        # 缩进不足，添加正确的缩进
                        new_line = ' ' * (current_indent + 4) + line.lstrip()
                        new_pdf_content.append(new_line)
                    else:
                        new_pdf_content.append(line)
                else:
                    new_pdf_content.append(line)
        else:
            new_pdf_content.append(line)
    
    # 重新组合内容
    new_pdf_content = '\n'.join(new_pdf_content)
    
    # 替换原内容
    new_content = content[:pdf_start] + new_pdf_content + content[pdf_end:]
    
    # 保存修复后的文件
    with open('windows_app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("修复完成")

if __name__ == "__main__":
    fix_pdf_try_except()
