#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复脚本 - 将通用方法从__init__之前移出，插入到__init__之后
"""

import re

def fix_helper_methods_position(file_path):
    """修复通用方法的位置，将它们从__init__之前移出，插入到__init__之后"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到IPSubnetSplitterApp类的开始
    class_start = content.find('class IPSubnetSplitterApp:')
    if class_start == -1:
        print("未找到IPSubnetSplitterApp类")
        return
    
    # 找到__init__方法的开始
    init_start = content.find('    def __init__(self, main_window):', class_start)
    if init_start == -1:
        print("未找到__init__方法")
        return
    
    # 找到__init__方法的结束（第一个在__init__之后定义的方法）
    pattern = r'\n    def [a-z_]+\('
    matches = list(re.finditer(pattern, content[init_start:]))
    
    if not matches:
        print("未找到其他方法")
        return
    
    # 第一个方法定义的位置（相对于init_start）
    first_method_pos = matches[0].start()
    
    # __init__方法的结束位置
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
    
    # 查找_create_scrollbar_callback方法之后不应该存在的属性初始化代码
    # 这些代码应该被移除，因为它们是__init__方法的一部分
    pattern = r'return scrollbar_callback\n\s+self\.ip_mask_var = None.*?self\.root = main_window'
    match = re.search(pattern, init_content, re.DOTALL)
    
    if match:
        print("发现_create_scrollbar_callback之后的属性初始化代码")
        # 移除这些代码
        init_content = init_content[:match.start()] + init_content[match.end():]
    
    # 替换原内容
    new_content = content[:init_start] + init_content + content[init_end:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("修复完成!")

if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    fix_helper_methods_position(file_path)
