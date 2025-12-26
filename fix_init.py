#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复脚本 - 将通用方法从__init__内部移出
"""

import re

def fix_init_method(file_path):
    """修复__init__方法，将通用方法移出"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到__init__方法的开始和结束
    init_start = content.find('    def __init__(self, main_window):')
    if init_start == -1:
        print("未找到__init__方法")
        return
    
    # 找到第一个在__init__之后定义的方法
    # 查找第一个"    def "（在__init__之后）
    pattern = r'\n    def [a-z_]+\('
    matches = list(re.finditer(pattern, content[init_start:]))
    
    if not matches:
        print("未找到其他方法")
        return
    
    # 第一个方法定义的位置（相对于init_start）
    first_method_pos = matches[0].start()
    
    # 找到__init__方法的结束位置（在第一个方法之前）
    init_end = init_start + first_method_pos
    
    # 提取__init__方法的内容
    init_content = content[init_start:init_end]
    
    # 检查__init__方法中是否有未关闭的代码
    # 查找"""开始但未结束的文档字符串
    docstring_pattern = r'"""[^"]*$'
    docstring_matches = list(re.finditer(docstring_pattern, init_content, re.MULTILINE))
    
    if docstring_matches:
        print(f"发现{len(docstring_matches)}个未关闭的文档字符串")
        # 移除这些未关闭的文档字符串
        for match in docstring_matches:
            init_content = init_content[:match.start()] + init_content[match.end():]
    
    # 修复__init__方法，移除未关闭的代码
    # 查找"""验证CIDR格式是否有效..."""这样的未关闭文档字符串
    pattern = r'"""验证CIDR格式是否有效\s*\n\s*\n\s*Args:\s*\n\s*cidr: 要验证的CIDR字符串\s*\n\s*\n\s*Returns:\s*\n\s*bool: 如果CIDR格式有效则返回True，否则返回False\s*\n\s*"""'
    init_content = re.sub(pattern, '', init_content)
    
    # 替换原内容
    new_content = content[:init_start] + init_content + content[init_end:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("修复完成!")

if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    fix_init_method(file_path)
