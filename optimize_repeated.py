#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码优化脚本 - 合并重复的代码逻辑
"""

import re

def optimize_repeated_code(file_path):
    """优化重复的代码逻辑"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # 1. 提取通用的滚动条回调函数
    scrollbar_callback_template = '''
    def _create_scrollbar_callback(self, scrollbar):
        """创建通用的滚动条回调函数，实现滚动条按需显示"""
        def scrollbar_callback(*args):
            scrollbar.set(*args)
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                scrollbar.grid_remove()
            else:
                scrollbar.grid()
        return scrollbar_callback
'''
    
    # 在类中添加这个通用方法（在__init__方法之后）
    init_pattern = r'(    def __init__\(self, main_window\):.*?self\.cidr_subnet_mask_map = None\n)'
    if '_create_scrollbar_callback' not in content:
        match = re.search(init_pattern, content, re.DOTALL)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + scrollbar_callback_template + '\n' + content[insert_pos:]
            print("已添加通用滚动条回调函数")
    
    # 2. 提取通用的对话框居中逻辑
    center_dialog_template = '''
    def _center_dialog(self, dialog):
        """将对话框居中显示在主窗口上"""
        dialog.update_idletasks()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2
        
        dialog.geometry(f"+{dialog_x}+{dialog_y}")
'''
    
    if '_center_dialog' not in content:
        match = re.search(init_pattern, content, re.DOTALL)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + center_dialog_template + '\n' + content[insert_pos:]
            print("已添加通用对话框居中函数")
    
    # 3. 替换show_custom_dialog中的居中逻辑
    old_center_logic = r'''        # 计算并设置对话框居中位置
        dialog.update_idletasks()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        # 获取主窗口在屏幕上的绝对位置和尺寸
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # 计算对话框在主窗口中心的坐标
        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2

        # 设置对话框位置
        dialog.geometry(f"+{dialog_x}+{dialog_y}")'''
    
    new_center_logic = '        self._center_dialog(dialog)'
    
    content = re.sub(old_center_logic, new_center_logic, content)
    print("已优化show_custom_dialog中的居中逻辑")
    
    # 4. 替换show_custom_confirm中的居中逻辑
    content = re.sub(old_center_logic, new_center_logic, content)
    print("已优化show_custom_confirm中的居中逻辑")
    
    # 5. 提取通用的表格编辑逻辑
    table_edit_template = '''
    def _setup_tree_edit(self, tree, event, tree_name):
        """通用的Treeview单元格编辑设置"""
        region = tree.identify_region(event.x, event.y)
        if region != "cell":
            return False
        
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        
        if not item or not column:
            return False
        
        column_index = int(column[1:]) - 1
        if column_index == 0:
            return False
        
        column_name = tree["columns"][column_index]
        current_value = tree.item(item, "values")[column_index]
        cell_x, cell_y, width, height = tree.bbox(item, column)
        
        self.edit_entry = ttk.Entry(tree, width=width // 10)
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        self.edit_entry.place(x=cell_x, y=cell_y, width=width, height=height)
        
        self.current_edit_item = item
        self.current_edit_column = column_name
        self.current_edit_column_index = column_index
        self.current_edit_tree = tree_name
        
        self.edit_entry.bind("<FocusOut>", self.on_edit_focus_out)
        self.edit_entry.bind("<Return>", self.on_edit_enter)
        self.edit_entry.bind("<Escape>", self.on_edit_escape)
        
        return True
'''
    
    if '_setup_tree_edit' not in content:
        match = re.search(init_pattern, content, re.DOTALL)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + table_edit_template + '\n' + content[insert_pos:]
            print("已添加通用表格编辑函数")
    
    # 6. 替换on_requirements_tree_double_click中的重复代码
    old_requirements_edit = r'''    def on_requirements_tree_double_click\(self, event\):
        """双击Treeview单元格时触发编辑功能（子网需求表）"""
        # 获取双击位置的信息
        region = self\.requirements_tree\.identify_region\(event\.x, event\.y\)
        if region != "cell":
            return

        # 获取双击的行和列
        item = self\.requirements_tree\.identify_row\(event\.y\)
        column = self\.requirements_tree\.identify_column\(event\.x\)

        if not item or not column:
            return

        # 将列标识转换为列索引（例如 #1 -> 0, #2 -> 1）
        column_index = int\(column\[1:\]\) - 1
        # 不允许编辑序号列
        if column_index == 0:
            return
        column_name = self\.requirements_tree\["columns"\]\[column_index\]

        # 获取当前值
        current_value = self\.requirements_tree\.item\(item, "values"\)\[column_index\]

        # 获取单元格的坐标和大小
        cell_x, cell_y, width, height = self\.requirements_tree\.bbox\(item, column\)

        # 创建编辑框
        self\.edit_entry = ttk\.Entry\(self\.requirements_tree, width=width // 10\)  # 估算字符宽度
        self\.edit_entry\.insert\(0, current_value\)
        self\.edit_entry\.select_range\(0, tk\.END\)
        self\.edit_entry\.focus\(\)

        # 设置编辑框在单元格上
        self\.edit_entry\.place\(x=cell_x, y=cell_y, width=width, height=height\)

        # 保存当前编辑的信息
        self\.current_edit_item = item
        self\.current_edit_column = column_name
        self\.current_edit_column_index = column_index
        self\.current_edit_tree = "requirements"  # 保存当前编辑的表格

        # 绑定事件
        self\.edit_entry\.bind\("<FocusOut>", self\.on_edit_focus_out\)
        self\.edit_entry\.bind\("<Return>", self\.on_edit_enter\)
        self\.edit_entry\.bind\("<Escape>", self\.on_edit_escape\)'''
    
    new_requirements_edit = '''    def on_requirements_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能（子网需求表）"""
        self._setup_tree_edit(self.requirements_tree, event, "requirements")'''
    
    content = re.sub(old_requirements_edit, new_requirements_edit, content, flags=re.DOTALL)
    print("已优化on_requirements_tree_double_click方法")
    
    # 7. 替换on_pool_tree_double_click中的重复代码
    old_pool_edit = r'''    def on_pool_tree_double_click\(self, event\):
        """双击Treeview单元格时触发编辑功能（需求池表）"""
        # 获取双击位置的信息
        region = self\.pool_tree\.identify_region\(event\.x, event\.y\)
        if region != "cell":
            return

        # 获取双击的行和列
        item = self\.pool_tree\.identify_row\(event\.y\)
        column = self\.pool_tree\.identify_column\(event\.x\)

        if not item or not column:
            return

        # 将列标识转换为列索引（例如 #1 -> 0, #2 -> 1）
        column_index = int\(column\[1:\]\) - 1
        # 不允许编辑序号列
        if column_index == 0:
            return
        column_name = self\.pool_tree\["columns"\]\[column_index\]

        # 获取当前值
        current_value = self\.pool_tree\.item\(item, "values"\)\[column_index\]

        # 获取单元格的坐标和大小
        cell_x, cell_y, width, height = self\.pool_tree\.bbox\(item, column\)

        # 创建编辑框
        self\.edit_entry = ttk\.Entry\(self\.pool_tree, width=width // 10\)  # 估算字符宽度
        self\.edit_entry\.insert\(0, current_value\)
        self\.edit_entry\.select_range\(0, tk\.END\)
        self\.edit_entry\.focus\(\)

        # 设置编辑框在单元格上
        self\.edit_entry\.place\(x=cell_x, y=cell_y, width=width, height=height\)

        # 保存当前编辑的信息
        self\.current_edit_item = item
        self\.current_edit_column = column_name
        self\.current_edit_column_index = column_index
        self\.current_edit_tree = "pool"  # 保存当前编辑的表格

        # 绑定事件
        self\.edit_entry\.bind\("<FocusOut>", self\.on_edit_focus_out\)
        self\.edit_entry\.bind\("<Return>", self\.on_edit_enter\)
        self\.edit_entry\.bind\("<Escape>", self\.on_edit_escape\)'''
    
    new_pool_edit = '''    def on_pool_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能（需求池表）"""
        self._setup_tree_edit(self.pool_tree, event, "pool")'''
    
    content = re.sub(old_pool_edit, new_pool_edit, content, flags=re.DOTALL)
    print("已优化on_pool_tree_double_click方法")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    saved_bytes = original_length - new_length
    print(f"\n优化完成! 共节省 {saved_bytes} 字节")

    return saved_bytes


if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    optimize_repeated_code(file_path)
