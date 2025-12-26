#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码优化脚本 - 添加优化注释
"""

import re

def add_optimization_comments(file_path):
    """为优化过的代码添加注释说明"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 为_create_scrollbar_callback添加优化注释
    pattern1 = r'(    def _create_scrollbar_callback\(self, scrollbar\):)'
    replacement1 = r'''    # 优化点：提取通用的滚动条回调函数，避免重复代码
    def _create_scrollbar_callback(self, scrollbar):'''
    content = re.sub(pattern1, replacement1, content)
    print("已为_create_scrollbar_callback添加优化注释")
    
    # 2. 为_center_dialog添加优化注释
    pattern2 = r'(    def _center_dialog\(self, dialog\):)'
    replacement2 = r'''    # 优化点：提取通用的对话框居中逻辑，避免重复代码
    def _center_dialog(self, dialog):'''
    content = re.sub(pattern2, replacement2, content)
    print("已为_center_dialog添加优化注释")
    
    # 3. 为_setup_tree_edit添加优化注释
    pattern3 = r'(    def _setup_tree_edit\(self, tree, event, tree_name\):)'
    replacement3 = r'''    # 优化点：提取通用的表格编辑逻辑，避免在多个方法中重复相同代码
    def _setup_tree_edit(self, tree, event, tree_name):'''
    content = re.sub(pattern3, replacement3, content)
    print("已为_setup_tree_edit添加优化注释")
    
    # 4. 为_check_duplicate_name添加优化注释
    pattern4 = r'(    def _check_duplicate_name\(self, name, target_tree, tree_name\):)'
    replacement4 = r'''    # 优化点：提取通用的重复名称检查逻辑，避免在move_left和move_right中重复
    def _check_duplicate_name(self, name, target_tree, tree_name):'''
    content = re.sub(pattern4, replacement4, content)
    print("已为_check_duplicate_name添加优化注释")
    
    # 5. 为_execute_move添加优化注释
    pattern5 = r'(    def _execute_move\(self, source_tree, target_tree, items_to_move, target_tree_name\):)'
    replacement5 = r'''    # 优化点：提取通用的移动执行逻辑，避免在move_left和move_right中重复
    def _execute_move(self, source_tree, target_tree, items_to_move, target_tree_name):'''
    content = re.sub(pattern5, replacement5, content)
    print("已为_execute_move添加优化注释")
    
    # 6. 为on_requirements_tree_double_click添加优化注释
    pattern6 = r'(    def on_requirements_tree_double_click\(self, event\):)'
    replacement6 = r'''    # 优化点：使用通用的_setup_tree_edit方法，减少代码重复
    def on_requirements_tree_double_click(self, event):'''
    content = re.sub(pattern6, replacement6, content)
    print("已为on_requirements_tree_double_click添加优化注释")
    
    # 7. 为on_pool_tree_double_click添加优化注释
    pattern7 = r'(    def on_pool_tree_double_click\(self, event\):)'
    replacement7 = r'''    # 优化点：使用通用的_setup_tree_edit方法，减少代码重复
    def on_pool_tree_double_click(self, event):'''
    content = re.sub(pattern7, replacement7, content)
    print("已为on_pool_tree_double_click添加优化注释")
    
    # 8. 为move_left添加优化注释
    pattern8 = r'(    def move_left\(self\):)'
    replacement8 = r'''    # 优化点：使用_check_duplicate_name和_execute_move通用方法，简化代码逻辑
    def move_left(self):'''
    content = re.sub(pattern8, replacement8, content)
    print("已为move_left添加优化注释")
    
    # 9. 为move_right添加优化注释
    pattern9 = r'(    def move_right\(self\):)'
    replacement9 = r'''    # 优化点：使用_check_duplicate_name和_execute_move通用方法，简化代码逻辑
    def move_right(self):'''
    content = re.sub(pattern9, replacement9, content)
    print("已为move_right添加优化注释")
    
    # 10. 为update_requirements_tree_zebra_stripes添加优化注释
    pattern10 = r'(    def update_requirements_tree_zebra_stripes\(self\):)'
    replacement10 = r'''    # 优化点：缓存get_children()结果，避免在循环中重复调用，提升性能
    def update_requirements_tree_zebra_stripes(self):'''
    content = re.sub(pattern10, replacement10, content)
    print("已为update_requirements_tree_zebra_stripes添加优化注释")
    
    # 11. 为update_pool_tree_zebra_stripes添加优化注释
    pattern11 = r'(    def update_pool_tree_zebra_stripes\(self\):)'
    replacement11 = r'''    # 优化点：缓存get_children()结果，避免在循环中重复调用，提升性能
    def update_pool_tree_zebra_stripes(self):'''
    content = re.sub(pattern11, replacement11, content)
    print("已为update_pool_tree_zebra_stripes添加优化注释")
    
    # 12. 为auto_resize_columns添加优化注释
    pattern12 = r'(    def auto_resize_columns\(self, tree\):)'
    replacement12 = r'''    # 优化点：缓存columns列表和索引，避免在循环中重复计算，提升性能
    def auto_resize_columns(self, tree):'''
    content = re.sub(pattern12, replacement12, content)
    print("已为auto_resize_columns添加优化注释")
    
    # 13. 为execute_ipv6_info中的地址类型判断添加优化注释
    pattern13 = r'(            ipv6_type_map = \{)'
    replacement13 = r'''            # 优化点：使用字典查找替代if-elif链，提升代码可读性和性能
            ipv6_type_map = {'''
    content = re.sub(pattern13, replacement13, content)
    print("已为execute_ipv6_info中的地址类型判断添加优化注释")
    
    # 14. 为show_custom_dialog中的居中逻辑添加优化注释
    pattern14 = r'(        self\._center_dialog\(dialog\))'
    replacement14 = r'''        # 优化点：使用通用的_center_dialog方法，避免重复代码
        self._center_dialog(dialog)'''
    content = re.sub(pattern14, replacement14, content)
    print("已为show_custom_dialog中的居中逻辑添加优化注释")
    
    # 15. 为show_custom_confirm中的居中逻辑添加优化注释
    pattern15 = r'(        self\._center_dialog\(dialog\))'
    replacement15 = r'''        # 优化点：使用通用的_center_dialog方法，避免重复代码
        self._center_dialog(dialog)'''
    content = re.sub(pattern15, replacement15, content)
    print("已为show_custom_confirm中的居中逻辑添加优化注释")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n优化注释添加完成!")

if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    add_optimization_comments(file_path)
