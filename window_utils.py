#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 - 
"""

import tkinter as tk

def setup_window_settings(root, width=1050, height=950, lock_width=True, min_width=1050, min_height=950, max_width=1100, max_height=10000):
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
    # 
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # 
    window_x = (screen_width - width) // 2
    window_y = (screen_height - height) // 2
    
    # 
    root.geometry(f"{width}x{height}+{window_x}+{window_y}")
    
    # 
    root.minsize(min_width, min_height)
    root.maxsize(max_width, max_height)
    
    # 
    root.resizable(not lock_width, True)
    
    print(f" : {width}x{height}")
