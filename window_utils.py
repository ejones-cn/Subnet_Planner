#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
窗口工具模块
提供窗口设置和管理相关的辅助功能
"""

import tkinter as tk


def setup_window_settings(root: tk.Tk, width: int = 1050, height: int = 950, lock_width: bool = True, min_width: int = 1050, min_height: int = 950, max_width: int = 10000, max_height: int = 10000, position: tuple[int, int] | None = None) -> None:
    """设置窗口初始大小和位置
    
    Args:
        root: 窗口对象
        width: 窗口宽度
        height: 窗口高度
        lock_width: 是否锁定宽度
        min_width: 最小宽度
        min_height: 最小高度
        max_width: 最大宽度
        max_height: 最大高度
        position: 窗口位置 (x, y)，如果为 None 则居中显示
    """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    if position:
        window_x, window_y = position
    else:
        window_x = (screen_width - width) // 2
        window_y = (screen_height - height) // 2
    
    root.geometry(f"{width}x{height}+{window_x}+{window_y}")
    
    root.minsize(min_width, min_height)
    root.maxsize(max_width, max_height)
    
    root.resizable(not lock_width, True)
    
    print(f"窗口设置: {width}x{height}, 位置: ({window_x}, {window_y})")
