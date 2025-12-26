#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码优化脚本 - 优化move相关方法
"""

import re

def optimize_move_methods(file_path):
    """优化move_left、move_right和move_records方法中的重复代码"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # 添加通用的移动记录检查函数
    check_duplicate_template = '''
    def _check_duplicate_name(self, name, target_tree, tree_name):
        """检查目标表格中是否已存在相同名称的记录"""
        for item in target_tree.get_children():
            values = target_tree.item(item, "values")
            if values[1] == name:
                self.show_error("错误", f"{tree_name}中已存在名称为 '{name}' 的记录")
                return True
        return False
'''
    
    if '_check_duplicate_name' not in content:
        # 在move_left方法之前添加
        pattern = r'(    def move_left\(self\):)'
        match = re.search(pattern, content)
        if match:
            insert_pos = match.start()
            content = content[:insert_pos] + check_duplicate_template + '\n' + content[insert_pos:]
            print("已添加通用重复名称检查函数")
    
    # 添加通用的移动记录执行函数
    execute_move_template = '''
    def _execute_move(self, source_tree, target_tree, items_to_move, target_tree_name):
        """执行移动操作"""
        new_items = []
        
        for selected_item in items_to_move:
            source_tree.delete(selected_item)
        
        for data in items_to_move:
            new_item_id = target_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
            new_items.append(new_item_id)
        
        return new_items
'''
    
    if '_execute_move' not in content:
        pattern = r'(    def move_left\(self\):)'
        match = re.search(pattern, content)
        if match:
            insert_pos = match.start()
            content = content[:insert_pos] + execute_move_template + '\n' + content[insert_pos:]
            print("已添加通用移动执行函数")
    
    # 简化move_left方法
    old_move_left = r'''    def move_left\(self\):
        """向左移：从子网需求表向需求池移动记录（支持多条记录，移动后保持选中）"""
        # 获取选中的子网需求记录
        selected_items = self\.requirements_tree\.selection\(\)
        if not selected_items:
            self\.show_info\("提示", "请先选择要移动的子网需求记录"\)
            return

        # 先检查所有选中记录是否都可以移动
        # 同时收集要移动的记录数据
        items_to_move = \[\]
        for selected_item in selected_items:
            values = self\.requirements_tree\.item\(selected_item, "values"\)
            name = values\[1\]
            hosts = values\[2\]
            items_to_move\.append\(\{"name": name, "hosts": hosts\}\)

            # 检查需求池中是否已存在相同名称的记录
            for item in self\.pool_tree\.get_children\(\):
                pool_values = self\.pool_tree\.item\(item, "values"\)
                if pool_values\[1\] == name:
                    self\.show_error\("错误", f"需求池中已存在名称为 '\{name\}' 的记录"\)
                    return

        # 执行移动操作，并保存新插入记录的ID
        new_pool_items = \[\]
        for selected_item in selected_items:
            # 从子网需求表删除记录
            self\.requirements_tree\.delete\(selected_item\)

        # 插入记录到需求池，并保存新记录的ID
        for data in items_to_move:
            new_item_id = self\.pool_tree\.insert\("", tk\.END, values=\("", data\["name"\], data\["hosts"\]\)\)
            new_pool_items\.append\(new_item_id\)

        # 更新序号和斑马条纹
        self\.update_requirements_tree_zebra_stripes\(\)
        self\.update_pool_tree_zebra_stripes\(\)

        # 移动完成后，在需求池中选中刚刚移动的记录
        if new_pool_items:
            self\.pool_tree\.selection_set\(\*new_pool_items\)'''
    
    new_move_left = '''    def move_left(self):
        """向左移：从子网需求表向需求池移动记录（支持多条记录，移动后保持选中）"""
        selected_items = self.requirements_tree.selection()
        if not selected_items:
            self.show_info("提示", "请先选择要移动的子网需求记录")
            return

        items_to_move = []
        for selected_item in selected_items:
            values = self.requirements_tree.item(selected_item, "values")
            name = values[1]
            hosts = values[2]
            items_to_move.append({"name": name, "hosts": hosts})
            
            if self._check_duplicate_name(name, self.pool_tree, "需求池"):
                return

        new_pool_items = self._execute_move(
            self.requirements_tree, self.pool_tree, items_to_move, "需求池"
        )
        
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()
        
        if new_pool_items:
            self.pool_tree.selection_set(*new_pool_items)'''
    
    content = re.sub(old_move_left, new_move_left, content, flags=re.DOTALL)
    print("已优化move_left方法")
    
    # 简化move_right方法
    old_move_right = r'''    def move_right\(self\):
        """向右移：从需求池向子网需求表移动记录（支持多条记录，移动后保持选中）"""
        # 获取选中的需求池记录
        selected_items = self\.pool_tree\.selection\(\)
        if not selected_items:
            self\.show_info\("提示", "请先选择要移动的需求池记录"\)
            return

        # 先检查所有选中记录是否都可以移动
        # 同时收集要移动的记录数据
        items_to_move = \[\]
        for selected_item in selected_items:
            values = self\.pool_tree\.item\(selected_item, "values"\)
            name = values\[1\]
            hosts = values\[2\]
            items_to_move\.append\(\{"name": name, "hosts": hosts\}\)

            # 检查子网需求表中是否已存在相同名称的记录
            for item in self\.requirements_tree\.get_children\(\):
                req_values = self\.requirements_tree\.item\(item, "values"\)
                if req_values\[1\] == name:
                    self\.show_error\("错误", f"子网需求表中已存在名称为 '\{name\}' 的记录"\)
                    return

        # 执行移动操作，并保存新插入记录的ID
        new_req_items = \[\]
        for selected_item in selected_items:
            # 从需求池删除记录
            self\.pool_tree\.delete\(selected_item\)

        # 插入记录到子网需求表，并保存新记录的ID
        for data in items_to_move:
            new_item_id = self\.requirements_tree\.insert\("", tk\.END, values=\("", data\["name"\], data\["hosts"\]\)\)
            new_req_items\.append\(new_item_id\)

        # 更新序号和斑马条纹
        self\.update_requirements_tree_zebra_stripes\(\)
        self\.update_pool_tree_zebra_stripes\(\)

        # 移动完成后，在子网需求表中选中刚刚移动的记录
        if new_req_items:
            self\.requirements_tree\.selection_set\(\*new_req_items\)'''
    
    new_move_right = '''    def move_right(self):
        """向右移：从需求池向子网需求表移动记录（支持多条记录，移动后保持选中）"""
        selected_items = self.pool_tree.selection()
        if not selected_items:
            self.show_info("提示", "请先选择要移动的需求池记录")
            return

        items_to_move = []
        for selected_item in selected_items:
            values = self.pool_tree.item(selected_item, "values")
            name = values[1]
            hosts = values[2]
            items_to_move.append({"name": name, "hosts": hosts})
            
            if self._check_duplicate_name(name, self.requirements_tree, "子网需求表"):
                return

        new_req_items = self._execute_move(
            self.pool_tree, self.requirements_tree, items_to_move, "子网需求表"
        )
        
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()
        
        if new_req_items:
            self.requirements_tree.selection_set(*new_req_items)'''
    
    content = re.sub(old_move_right, new_move_right, content, flags=re.DOTALL)
    print("已优化move_right方法")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    saved_bytes = original_length - new_length
    print(f"\n优化完成! 共节省 {saved_bytes} 字节")
    
    return saved_bytes

if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    optimize_move_methods(file_path)
