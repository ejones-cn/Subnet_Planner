#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
窗口工具模块 - 提供窗口大小设置和调整限制功能
"""

import tkinter as tk

def setup_window_settings(root, width=850, height=750, lock_width=True, min_width=850, min_height=750, max_width=1100, max_height=10000):
    """设置窗口大小和调整限制
    
    Args:
        root: 窗口对象
        width: 初始宽度
        height: 初始高度
        lock_width: 是否锁定宽度
        min_width: 最小宽度
        min_height: 最小高度
        max_width: 最大宽度
        max_height: 最大高度
    """
    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 计算窗口居中的坐标
    window_x = (screen_width - width) // 2
    window_y = (screen_height - height) // 2
    
    # 设置窗口大小和位置
    root.geometry(f"{width}x{height}+{window_x}+{window_y}")
    
    # 设置窗口最小和最大尺寸
    root.minsize(min_width, min_height)
    root.maxsize(max_width, max_height)
    
    # 设置窗口可调整性
    root.resizable(not lock_width, True)
    
    print(f"📏 窗口尺寸: {width}x{height}")
