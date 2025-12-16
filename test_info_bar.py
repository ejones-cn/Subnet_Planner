#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试信息栏功能
"""

import tkinter as tk
from windows_app import IPSubnetSplitterApp
import time


def test_info_bar_show_result():
    """测试信息栏显示结果功能"""
    print("\n=== 测试信息栏显示结果功能 ===")
    
    # 创建根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建应用程序实例
    app = IPSubnetSplitterApp(root)
    
    # 测试1: 显示成功信息
    print("\n测试1: 显示成功信息")
    app.show_result("测试成功信息", error=False)
    # 检查信息栏是否显示
    is_visible = app.info_bar_frame.winfo_manager() != ""
    print(f"成功信息栏是否显示: {is_visible}")
    print(f"成功信息内容: {app.info_label.cget('text')}")
    print(f"成功信息样式: {app.info_label.cget('style')}")
    
    # 测试2: 显示错误信息
    print("\n测试2: 显示错误信息")
    app.show_result("测试错误信息", error=True)
    # 检查信息栏是否显示
    is_visible = app.info_bar_frame.winfo_manager() != ""
    print(f"错误信息栏是否显示: {is_visible}")
    print(f"错误信息内容: {app.info_label.cget('text')}")
    print(f"错误信息样式: {app.info_label.cget('style')}")
    
    # 测试3: 手动隐藏信息栏
    print("\n测试3: 手动隐藏信息栏")
    app.hide_info_bar()
    is_visible = app.info_bar_frame.winfo_manager() != ""
    print(f"手动隐藏后信息栏是否显示: {not is_visible}")
    print(f"手动隐藏后winfo_manager(): '{app.info_bar_frame.winfo_manager()}'")
    assert not is_visible, "手动隐藏功能失败"
    
    # 测试4: 自动隐藏功能（注意：需要主事件循环才能工作）
    print("\n测试4: 自动隐藏功能")
    app.show_result("测试自动隐藏", error=False)
    is_visible = app.info_bar_frame.winfo_manager() != ""
    print(f"显示后信息栏是否显示: {is_visible}")
    print("自动隐藏功能需要主事件循环才能工作，在实际应用中会正常运行")
    print("跳过自动隐藏的实际测试，因为需要mainloop()")
    
    # 清理
    root.destroy()
    print("\n信息栏测试完成!")


def test_info_bar_styles():
    """测试信息栏样式"""
    print("\n=== 测试信息栏样式 ===")
    
    # 创建根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 创建应用程序实例
    app = IPSubnetSplitterApp(root)
    
    # 测试不同类型信息的样式
    test_cases = [
        ("成功信息", False),
        ("错误信息", True),
    ]
    
    for text, is_error in test_cases:
        app.show_result(text, error=is_error)
        style = app.info_label.cget('style')
        content = app.info_label.cget('text')
        
        print(f"\n类型: {'错误' if is_error else '成功'}")
        print(f"信息内容: {content}")
        print(f"应用样式: {style}")
        print(f"是否包含图标: {'是' if content.startswith(('✅', '❌')) else '否'}")
    
    # 清理
    root.destroy()
    print("\n信息栏样式测试完成!")


if __name__ == "__main__":
    # 运行所有测试
    test_info_bar_show_result()
    test_info_bar_styles()
    print("\n所有信息栏测试已完成!")
