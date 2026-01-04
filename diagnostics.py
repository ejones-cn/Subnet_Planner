#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断脚本，用于检查代码库中的常见问题"""

import ast
import os

# 要检查的文件列表
files_to_check = [
    'chart_utils.py',
    'export_utils.py',
    'i18n.py',
    'windows_app.py'
]

print("开始诊断检查...\n")

total_files = len(files_to_check)
passed_files = 0

for file in files_to_check:
    print(f"检查文件: {file}")
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file):
            print(f"  ✗ 文件不存在")
            continue
        
        # 检查UTF-8编码
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("  ✓ 编码正确 (UTF-8)")
        
        # 检查语法
        ast.parse(content)
        print("  ✓ 语法正确")
        
        # 检查是否有变量遮蔽问题 - 查找函数内部定义的_变量
        # 首先检查文件是否直接导入了翻译函数_
        has_translation_import = 'from i18n import _' in content
        
        if has_translation_import and '_(' in content and 'def ' in content:
            # 查找函数内部是否重新定义了_变量
            lines = content.split('\n')
            in_function = False
            for line in lines:
                line = line.strip()
                if line.startswith('def '):
                    in_function = True
                elif in_function and (line.startswith('return ') or line.startswith('def ') or line == ''):
                    # 重置函数状态 on return, new def, or empty line
                    in_function = line.startswith('def ')
                elif in_function and ('_ = ' in line or 'def _(' in line):
                    print("  ⚠ 可能存在翻译函数变量遮蔽问题")
                    break
        
        passed_files += 1
        print("  ✅ 检查通过\n")
        
    except SyntaxError as e:
        print(f"  ✗ 语法错误: {e}\n")
    except UnicodeDecodeError as e:
        print(f"  ✗ 编码错误: {e}\n")
    except Exception as e:
        print(f"  ✗ 其他错误: {e}\n")

print(f"诊断完成! 共检查 {total_files} 个文件，{passed_files} 个通过。")
