#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复脚本 - 将通用方法从__init__之前移出，并修复__init__方法的完整性
"""

import re

def fix_complete_init(file_path):
    """完整修复__init__方法"""

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
    
    # 提取新增的通用方法
    helper_methods = []
    
    # _setup_tree_edit
    setup_tree_edit_match = re.search(
        r'(    # 优化点：提取通用的表格编辑逻辑，避免在多个方法中重复相同代码\n    def _setup_tree_edit\(self, tree, event, tree_name\):.*?return True\n)',
        content, re.DOTALL
    )
    if setup_tree_edit_match:
        helper_methods.append(setup_tree_edit_match.group(1))
        print("找到_setup_tree_edit方法")
    
    # _center_dialog
    center_dialog_match = re.search(
        r'(    # 优化点：提取通用的对话框居中逻辑，避免重复代码\n    def _center_dialog\(self, dialog\):.*?dialog\.geometry\(f"\+{dialog_x}\+\{dialog_y\}"\)\n)',
        content, re.DOTALL
    )
    if center_dialog_match:
        helper_methods.append(center_dialog_match.group(1))
        print("找到_center_dialog方法")
    
    # _create_scrollbar_callback
    scrollbar_callback_match = re.search(
        r'(    # 优化点：提取通用的滚动条回调函数，避免重复代码\n    def _create_scrollbar_callback\(self, scrollbar\):.*?return scrollbar_callback\n)',
        content, re.DOTALL
    )
    if scrollbar_callback_match:
        helper_methods.append(scrollbar_callback_match.group(1))
        print("找到_create_scrollbar_callback方法")
    
    # 移除这些通用方法
    for method in helper_methods:
        content = content.replace(method, '')
    
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
    
    # 修复__init__方法，移除未关闭的代码
    # 查找"""验证CIDR格式是否有效..."""这样的未关闭文档字符串
    pattern = r'"""验证CIDR格式是否有效\s*\n\s*\n\s*Args:\s*\n\s*cidr: 要验证的CIDR字符串\s*\n\s*\n\s*Returns:\s*\n\s*bool: 如果CIDR格式有效则返回True，否则返回False\s*\n\s*"""'
    init_content = re.sub(pattern, '', init_content)
    
    # 查找_create_scrollbar_callback之后的属性初始化代码
    # 这些代码应该被移除，因为它们是__init__方法的一部分
    pattern = r'return scrollbar_callback\n\s+self\.ip_mask_var = None.*?self\.root = main_window'
    match = re.search(pattern, init_content, re.DOTALL)
    
    if match:
        print("发现_create_scrollbar_callback之后的属性初始化代码")
        # 移除这些代码
        init_content = init_content[:match.start()] + init_content[match.end():]
    
    # 替换原内容
    new_content = content[:init_start] + init_content + content[init_end:]
    
    # 将通用方法插入到__init__方法之后
    # 找到__init__方法的结束位置
    init_end = new_content.find('    def update_history_tree(self):', init_start)
    if init_end == -1:
        print("未找到update_history_tree方法")
        return
    
    # 将通用方法插入到__init__方法之后
    helper_methods_text = '\n'.join(helper_methods)
    new_content = new_content[:init_end] + helper_methods_text + '\n' + new_content[init_end:]
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("修复完成!")


if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    fix_complete_init(file_path)
