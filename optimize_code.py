#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码优化脚本 - 删除未使用的函数
"""

import re

def remove_unused_functions(file_path):
    """删除未使用的函数"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 需要删除的函数列表
    functions_to_remove = [
        '_export_to_pdf',
        '_export_to_json',
        '_export_to_txt',
        '_export_to_csv',
        '_export_to_excel',
        '_calculate_auto_col_widths',
    ]
    
    # 删除每个函数
    for func_name in functions_to_remove:
        # 匹配函数定义到下一个函数定义或类定义
        pattern = rf'\n    def {func_name}\(.*?\n(?=\n    def |\n    class |\Z)'
        matches = list(re.finditer(pattern, content, re.DOTALL))
        
        if matches:
            for match in reversed(matches):
                content = content[:match.start()] + content[match.end():]
            print(f"已删除函数: {func_name}")
        else:
            print(f"未找到函数: {func_name}")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("优化完成!")


if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    remove_unused_functions(file_path)
