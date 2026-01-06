#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式管理器模块
负责集中管理应用程序的所有样式设置
支持根据当前语言动态调整样式
项目版本：v2.5.3
"""

import tkinter as tk
from tkinter import ttk
from i18n import get_language, _ as translate


class StyleManager:
    """样式管理器类，负责管理应用程序的所有样式设置"""
    
    def __init__(self, root=None):
        """初始化样式管理器
        
        Args:
            root: 根窗口对象，用于获取当前样式
        """
        self.root = root
        self.style = ttk.Style() if root else None
        self.setup_default_styles()
    
    def setup_default_styles(self):
        """设置默认样式"""
        if not self.style:
            return
        
        # 使用默认主题
        self.style.theme_use("vista")
    
    def get_current_font_settings(self):
        """获取当前语言的字体设置
        
        Returns:
            tuple: (字体名称, 字体大小)
        """
        current_language = get_language()
        
        if current_language in ["zh", "zh_tw"]:
            # 中文(简/繁)版：微软雅黑，10号字体
            return ("微软雅黑", 10)
        elif current_language == "ja":
            # 日文版：MS Gothic，10号字体
            return ("MS Gothic", 10)
        else:
            # 英文版：Arial，10号字体
            return ("Arial", 10)
    
    def get_tab_width(self):
        """获取当前语言的标签宽度设置
        
        Returns:
            int: 标签宽度
        """
        current_language = get_language()
        
        if current_language in ["zh", "zh_tw"]:
            # 中文(简/繁)版：标签宽度10
            return 10
        elif current_language == "ja":
            # 日文版：标签宽度18
            return 18
        else:
            # 英文版：标签宽度14
            return 14
    
    def get_button_size(self, button_type="default"):
        """获取当前语言的按钮尺寸设置
        
        Args:
            button_type: 按钮类型，支持 "default", "execute_planning", "export_planning", "export_result"
            
        Returns:
            tuple: (宽度, 高度)
        """
        current_language = get_language()
        
        # 根据语言和按钮类型确定宽度，高度统一使用10
        if current_language in ["zh", "zh_tw", "ja"]:
            # 中文(简/繁)和日文版：统一宽度12，特殊按钮类型也是12
            return (12, 10)
        else:
            # 英文版：规划和导出按钮宽度16，默认按钮14
            if button_type in ["execute_planning", "export_planning", "export_result"]:
                return (16, 10)
            else:
                return (14, 10)
    
    def update_all_styles(self):
        """更新所有样式，根据当前语言重新设置"""
        if not self.style:
            return
        
        current_language = get_language()
        font_family, font_size = self.get_current_font_settings()
        
        # 基础字体样式
        base_font_style = {
            "font": (font_family, font_size)
        }
        
        print(f"[StyleManager] {translate('updating_styles')}, {translate('current_language')}: {current_language}, {translate('font')}: {font_family}, {translate('size')}: {font_size}")
        
        # 1. 统一设置基本控件的字体样式
        self.style.configure("TLabel", **base_font_style)
        self.style.configure("TEntry", **base_font_style)
        
        # 信息标签样式
        self.style.configure("Error.TLabel", **base_font_style, foreground="red")  # 错误信息红色
        self.style.configure("Success.TLabel", **base_font_style, foreground="#5E5E5E")  # 成功信息灰色

        if current_language in ["zh", "zh_tw"]:
            self.style.configure("TButton", **base_font_style, focuscolor="#888888", focuswidth=1, padding=(0, 1))
        elif current_language == "ja":
            self.style.configure("TButton", **base_font_style, focuscolor="#888888", focuswidth=1, padding=(2, 3))
        else:
            self.style.configure("TButton", **base_font_style, focuscolor="#888888", focuswidth=1, padding=(3, 2))

        # 2. 设置滚动条宽度一致
        scrollbar_style = {"width": 5}
        for scrollbar_type in ["TScrollbar", "Vertical.TScrollbar", "Horizontal.TScrollbar"]:
            self.style.configure(scrollbar_type, **scrollbar_style)
        
        # 3. 为按钮添加焦点样式映射
        self.style.map(
            "TButton",
            focuscolor=[("focus", "#888888"), ("!focus", "#888888")],
            focuswidth=[("focus", 1), ("!focus", 1)],
        )
        
        # 4. 设置Notebook的基本样式
        self.style.configure("TNotebook", background="#ffffff")
        
        # 5. 设置LabelFrame样式
        self.style.configure("TLabelframe")
        self.style.configure(
            "TLabelframe.Label", 
            borderwidth=0, 
            relief="flat", 
            font=(font_family, font_size)
        )
        
        # 6. 为三个标签页分别创建不同颜色的标签样式
        # 蓝色标签样式 - 切分段信息
        self.style.configure(
            "Blue.TNotebook.Tab",
            background="#e3f2fd",  # 浅蓝色背景
            foreground="#1976d2",  # 深蓝色文字
            padding=(15, 6),  # 增加内边距
            relief="flat",  # 边框样式
            font=(font_family, font_size),
        )
        
        self.style.map(
            "Blue.TNotebook.Tab",
            background=[
                ("selected", "#9196f3"),  # 选中时使用更鲜艳的蓝色
                ("!selected", "#e3f2fd"),
            ],
            foreground=[("selected", "white"), ("!selected", "#1976d2")],
            font=[
                ("selected", (font_family, font_size, "bold")),
                ("!selected", (font_family, font_size, "normal")),
            ],
        )
        
        # 绿色标签样式 - 剩余网段表
        self.style.configure(
            "Green.TNotebook.Tab",
            background="#e8f5e9",  # 浅绿色背景
            foreground="#388e3c",  # 深绿色文字
            padding=(15, 6),  # 增加内边距
            relief="flat",  # 边框样式
            font=(font_family, font_size),
        )
        
        self.style.map(
            "Green.TNotebook.Tab",
            background=[
                ("selected", "#4caf50"),  # 选中时使用更鲜艳的绿色
                ("!selected", "#e8f5e9"),
            ],
            foreground=[("selected", "white"), ("!selected", "#388e3c")],
            font=[
                ("selected", (font_family, font_size, "bold")),
                ("!selected", (font_family, font_size, "normal")),
            ],
        )
        
        # 紫色标签样式 - 网段分布图
        self.style.configure(
            "Purple.TNotebook.Tab",
            background="#f3e5f5",  # 浅紫色背景
            foreground="#7b1fa2",  # 深紫色文字
            padding=(15, 6),  # 增加内边距
            relief="flat",  # 边框样式
            font=(font_family, font_size),
        )
        
        self.style.map(
            "Purple.TNotebook.Tab",
            background=[
                ("selected", "#9c27b0"),  # 选中时使用更鲜艳的紫色
                ("!selected", "#f3e5f5"),
            ],
            foreground=[("selected", "white"), ("!selected", "#7b1fa2")],
            font=[
                ("selected", (font_family, font_size, "bold")),
                ("!selected", (font_family, font_size, "normal")),
            ],
        )
        
        # 7. 设置Treeview样式
        self.style.configure(
            "TTreeview",
            background="#e0e0e0",
            fieldbackground="#ffffff",
            foreground="black",
            rowheight=25,
            padding=(5, 2),
            borderwidth=0,
            relief="flat",
        )
        
        # 8. 表头样式设置
        self.style.configure(
            "TTreeview.Heading",
            background="#1976d2",
            foreground="white",
            font=(font_family, font_size, "bold"),
            padding=(10, 5),
            relief="ridge",
        )
        
        # 9. 移除Treeview外框
        self.style.configure("TTreeview", borderwidth=0, relief="flat")
        
        # 10. 选中状态设置
        self.style.map("TTreeview", background=[("selected", "#4A6984")], foreground=[("selected", "white")])
        
        # 11.# 设置Combobox样式
        self.style.configure("TCombobox", **base_font_style)
        self.style.map(
            "TCombobox",
            selectbackground=[("focus", "#4A6984"), ("!focus", "#4A6984")],
            selectforeground=[("focus", "white"), ("!focus", "white")],
        )
    
    def get_colored_notebook_font_settings(self):
        """获取ColoredNotebook组件的字体设置
        
        Returns:
            tuple: (字体名称, 字体大小)
        """
        return self.get_current_font_settings()


# 创建全局样式管理器实例
style_manager = None


def init_style_manager(root):
    """初始化全局样式管理器
    
    Args:
        root: 根窗口对象
    """
    global style_manager
    style_manager = StyleManager(root)
    return style_manager


def get_style_manager():
    """获取全局样式管理器实例
    
    Returns:
        StyleManager: 样式管理器实例
    """
    return style_manager


def update_styles():
    """更新所有样式，根据当前语言重新设置
    这是一个便捷函数，用于在语言切换时调用
    """
    if style_manager:
        style_manager.update_all_styles()
    else:
        print(f"[StyleManager] {translate('style_manager_not_initialized')}")



def get_current_font_settings():
    """获取当前语言的字体设置
    
    Returns:
        tuple: (字体名称, 字体大小)
    """
    if style_manager:
        return style_manager.get_current_font_settings()
    else:
        # 未初始化时返回默认设置
        current_language = get_language()
        if current_language in ["zh", "zh_tw"]:
            return ("微软雅黑", 10)
        elif current_language == "ja":
            return ("MS Gothic", 10)
        else:
            return ("Arial", 10)
