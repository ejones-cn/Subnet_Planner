#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成测试：测试信息栏在实际应用中的使用情况
"""

import tkinter as tk
from windows_app import IPSubnetSplitterApp


def test_info_bar_integration():
    """测试信息栏在实际应用中的集成情况"""
    print("\n=== 测试信息栏在实际应用中的集成情况 ===")
    
    # 创建根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建应用程序实例
    app = IPSubnetSplitterApp(root)
    
    # 测试1: 初始状态下信息栏是否隐藏
    print("\n测试1: 初始状态下信息栏是否隐藏")
    is_visible = app.info_bar_frame.winfo_manager() != ""
    print(f"初始状态下信息栏是否隐藏: {not is_visible}")
    
    # 测试2: 在子网切分中使用信息栏
    print("\n测试2: 在子网切分中使用信息栏")
    
    # 设置父网段和切分段
    app.parent_entry.delete(0, tk.END)
    app.parent_entry.insert(0, "192.168.1.0/24")
    app.split_entry.delete(0, tk.END)
    app.split_entry.insert(0, "192.168.1.0/25")
    
    # 执行切分
    app.execute_split()
    
    # 测试3: 测试导出功能中的信息栏
    print("\n测试3: 测试导出功能中的信息栏")
    # 我们不会实际导出文件，只是测试信息栏的调用
    
    # 测试4: 测试清空结果中的信息栏
    print("\n测试4: 测试清空结果中的信息栏")
    app.clear_result()
    
    # 测试5: 测试错误处理中的信息栏
    print("\n测试5: 测试错误处理中的信息栏")
    # 设置无效的网段
    app.parent_entry.delete(0, tk.END)
    app.parent_entry.insert(0, "invalid-cidr")
    app.split_entry.delete(0, tk.END)
    app.split_entry.insert(0, "192.168.1.0/25")
    
    # 执行切分，应该会显示错误信息
    app.execute_split()
    
    # 清理
    root.destroy()
    print("\n信息栏集成测试完成!")


if __name__ == "__main__":
    # 运行集成测试
    test_info_bar_integration()
    print("\n所有信息栏集成测试已完成!")
