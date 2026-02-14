#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试列宽自适应功能
"""
# flake8: noqa: E402 - 允许导入不在文件顶部

# 先设置sys.path，然后再导入模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from windows_app import IPSubnetSplitterApp


def test_column_width():
    """测试列宽自适应功能"""
    root = tk.Tk()
    root.geometry("850x750")
    root.minsize(850, 750)

    app = IPSubnetSplitterApp(root)
    root.update_idletasks()

    # 设置测试数据
    test_parent_cidr = "10.21.48.0/20"

    # 设置父网段
    if hasattr(app, 'planning_parent_entry') and app.planning_parent_entry:
        app.planning_parent_entry.delete(0, tk.END)
        app.planning_parent_entry.insert(0, test_parent_cidr)

    # 模拟添加子网需求
    test_requirements = [
        ("办公室", "20"),
        ("人事部", "10"),
        ("财务部", "10"),
        ("市场部", "10"),
        ("采购部", "10"),
        ("财务部", "10"),
        ("安全部", "10"),
        ("数据部", "10"),
        ("纪检部", "10"),
    ]

    # 清空现有需求
    if hasattr(app, 'requirements_tree') and app.requirements_tree:
        for item in app.requirements_tree.get_children():
            app.requirements_tree.delete(item)

    # 添加测试需求
    if hasattr(app, 'requirements_tree') and app.requirements_tree:
        for name, hosts in test_requirements:
            app.requirements_tree.insert(
                "", tk.END, 
                values=(len(app.requirements_tree.get_children()) + 1, name, hosts)
            )

    # 执行子网规划
    if hasattr(app, 'execute_subnet_planning'):
        app.execute_subnet_planning()

    root.update_idletasks()

    # 检查列宽
    print("\n=== 列宽测试结果 ===")
    if hasattr(app, 'allocated_tree') and app.allocated_tree:
        # 直接遍历columns，不使用中间变量
        for column in app.allocated_tree['columns']:
            column_name = str(column)
            width = app.allocated_tree.column(column_name, 'width')
            print(f"列 '{column_name}' 宽度: {width}px")

        # 检查通配符掩码列
        columns = app.allocated_tree['columns']
        if 'wildcard' in columns:
            wildcard_width = app.allocated_tree.column('wildcard', 'width')
            print(f"\n通配符掩码列宽度: {wildcard_width}px")
            if wildcard_width < 200:
                print("✓ 通配符掩码列宽度合理")
            else:
                print("✗ 通配符掩码列宽度过大")

        # 检查name列
        if 'name' in columns:
            name_width = app.allocated_tree.column('name', 'width')
            print(f"\n子网名称列宽度: {name_width}px")

    # 关闭应用
    root.after(1000, root.destroy)
    root.mainloop()


if __name__ == "__main__":
    test_column_width()
