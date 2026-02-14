#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试列宽自适应功能
"""
import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from windows_app import IPSubnetSplitterApp

def test_column_width():
    """测试列宽自适应功能"""
    # 创建主窗口
    root = tk.Tk()
    
    # 设置窗口大小
    root.geometry("850x750")
    root.minsize(850, 750)
    
    # 创建应用实例
    app = IPSubnetSplitterApp(root)
    
    # 等待UI初始化
    root.update_idletasks()
    
    # 设置测试数据
    test_parent_cidr = "10.21.48.0/20"
    
    # 设置父网段
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
    for item in app.requirements_tree.get_children():
        app.requirements_tree.delete(item)
    
    # 添加测试需求
    for name, hosts in test_requirements:
        app.requirements_tree.insert("", tk.END, values=(len(app.requirements_tree.get_children()) + 1, name, hosts))
    
    # 执行子网规划
    app.execute_subnet_planning()
    
    # 等待UI更新
    root.update_idletasks()
    
    # 检查列宽
    print("\n=== 列宽测试结果 ===")
    columns = app.allocated_tree['columns']
    for col in columns:
        width = app.allocated_tree.column(col, 'width')
        print(f"列 '{col}' 宽度: {width}px")
    
    # 检查通配符掩码列的宽度
    wildcard_width = app.allocated_tree.column('wildcard', 'width')
    print(f"\n通配符掩码列宽度: {wildcard_width}px")
    
    # 验证宽度是否合理（不应该过大）
    if wildcard_width < 200:
        print("✓ 通配符掩码列宽度合理，已自适应内容")
    else:
        print("✗ 通配符掩码列宽度过大，未能自适应内容")
    
    # 测试name列是否能自适应
    name_width = app.allocated_tree.column('name', 'width')
    print(f"\n子网名称列宽度: {name_width}px")
    
    # 关闭应用
    root.after(1000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    test_column_width()