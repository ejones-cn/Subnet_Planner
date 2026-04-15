#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 - 
"""

import tkinter as tk


def setup_window_settings(root: tk.Tk, width: int = 1050, height: int = 950, lock_width: bool = True, min_width: int = 1050, min_height: int = 950, max_width: int = 10000, max_height: int = 10000) -> None:
    """
    
    Args:
        root: 
        width: 
        height: 
        lock_width: 
        min_width: 
        min_height: 
        max_width: 
        max_height: 
    """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    window_x = (screen_width - width) // 2
    window_y = (screen_height - height) // 2
    
    root.geometry(f"{width}x{height}+{window_x}+{window_y}")
    
    root.minsize(min_width, min_height)
    root.maxsize(max_width, max_height)
    
    root.resizable(not lock_width, True)
    
    print(f" : {width}x{height}")
