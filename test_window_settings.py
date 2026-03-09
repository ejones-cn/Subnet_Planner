#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试窗口设置函数的使用
"""

import tkinter as tk
from window_utils import setup_window_settings

def test_window_settings():
    """测试窗口设置函数"""
    # 创建测试窗口
    root = tk.Tk()
    root.title("测试窗口设置")
    
    # 使用共享的窗口设置函数
    setup_window_settings(root, width=600, height=400, lock_width=False, min_width=400, min_height=300, max_width=800, max_height=600)
    
    # 添加一个简单的标签
    tk.Label(root, text="这是一个测试窗口，使用了共享的窗口设置函数", font=("Arial", 12)).pack(pady=50)
    
    # 运行测试窗口
    root.mainloop()

if __name__ == "__main__":
    test_window_settings()
