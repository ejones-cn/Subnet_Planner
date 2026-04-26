#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
窗口工具模块
提供窗口设置和管理相关的辅助功能
"""

import os
import sys
import tkinter as tk


def _translate(key, **kwargs):
    """延迟导入翻译函数，避免循环导入"""
    try:
        from i18n import translate
        return translate(key, **kwargs)
    except (ImportError, Exception):
        return key


def get_app_directory() -> str:
    """获取应用程序所在目录
    
    优先使用 sys.argv[0]（最可靠的方法，适用于所有打包方式）
    其次使用 Windows API ctypes（仅限 Windows 平台）
    最后回退到 __file__（开发环境）
    
    Returns:
        应用程序所在目录的绝对路径
    """
    app_dir = None
    
    # 优先使用 sys.argv[0]（这是最可靠的方法）
    if sys.argv and sys.argv[0]:
        exe_path = sys.argv[0]
        if not os.path.isabs(exe_path):
            exe_path = os.path.abspath(exe_path)
        if os.path.exists(exe_path):
            app_dir = os.path.dirname(exe_path)
    
    # 如果 sys.argv[0] 不可用，尝试使用 ctypes（仅限Windows平台）
    if app_dir is None and sys.platform == 'win32':
        try:
            import ctypes
            from ctypes import wintypes
            
            GetModuleFileNameW = ctypes.windll.kernel32.GetModuleFileNameW
            GetModuleFileNameW.argtypes = [wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
            GetModuleFileNameW.restype = wintypes.DWORD
            
            buffer = ctypes.create_unicode_buffer(260)
            if GetModuleFileNameW(None, buffer, 260) > 0:
                exe_path = buffer.value
                if os.path.exists(exe_path):
                    app_dir = os.path.dirname(exe_path)
        except Exception:
            pass
    
    # 如果以上都失败，使用 __file__（开发环境）
    if app_dir is None:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    return app_dir


def setup_window_settings(root, width=1050, height=950, lock_width=True, min_width=1050, min_height=950, max_width=10000, max_height=10000, position=None):
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
    
    print(_translate("window_settings", width=width, height=height, x=window_x, y=window_y))
