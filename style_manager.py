#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
样式管理器模块
负责集中管理应用程序的所有样式设置
支持根据当前语言动态调整样式
"""

import tkinter as tk
from tkinter import ttk
from version import get_version
from i18n import get_language, _ as translate
from font_config import FontConfig

__version__ = get_version()


class StyleManager:
    """样式管理器类，负责管理应用程序的所有样式设置"""

    # 标签宽度设置映射表
    TAB_WIDTH_SETTINGS = {
        "zh": 10,
        "zh_tw": 10,
        "ja": 16,
        "ko": 11,
        "default": 18
    }

    # 按钮内边距设置映射表
    BUTTON_PADDING_SETTINGS = {
        "zh": (0, 1),
        "zh_tw": (0, 2),
        "ja": (2, 4),
        "ko": (2, 2),
        "default": (3, 3)
    }

    #  标签页内边距设置映射表
    TAB_PADDING_SETTINGS = {
        "zh": (15, 3),
        "zh_tw": (15, 3),
        "ja": (15, 3),
        "ko": (15, 3),
        "default": (15, 3)
    }

    # 标签页垂直内边距设置映射表（用于 ColoredNotebook）
    TAB_VERTICAL_PADDING_SETTINGS = {
        "zh": 2,
        "zh_tw": 4,
        "ja": 6,
        "ko": 2,
        "default": 4
    }

    # 彩色标签页样式配置
    TAB_STYLES = {
        "Blue": {
            "background": "#e3f2fd",
            "foreground": "#1976d2",
            "selected_background": "#9196f3",
            "selected_foreground": "white"
        },
        "Green": {
            "background": "#e8f5e9",
            "foreground": "#388e3c",
            "selected_background": "#4caf50",
            "selected_foreground": "white"
        },
        "Purple": {
            "background": "#f3e5f5",
            "foreground": "#7b1fa2",
            "selected_background": "#9c27b0",
            "selected_foreground": "white"
        }
    }

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
        self.style.theme_use("vista")

    def _get_setting(self, settings_dict, language):
        """根据语言获取设置值

        Args:
            settings_dict: 设置字典
            language: 当前语言

        Returns:
            对应的设置值
        """
        return settings_dict.get(language, settings_dict.get("default", (0, 0))) or (0, 0)

    def get_current_font_settings(self):
        """获取当前语言的字体设置

        Returns:
            tuple: (字体名称, 字体大小)
        """
        current_language = get_language()
        return FontConfig.get_ui_font_settings(current_language)
    
    def get_pin_button_font_size(self):
        """获取当前语言的钉住按钮字体大小设置

        Returns:
            int: 钉住按钮字体大小
        """
        current_language = get_language()
        return FontConfig.get_pin_button_font_size(current_language)
    
    def get_function_button_font_size(self):
        """获取当前语言的功能按钮字体大小设置（添加、删除、撤销、移动、导入等）

        Returns:
            int: 功能按钮字体大小
        """
        current_language = get_language()
        return FontConfig.get_function_button_font_size(current_language)
    
    def get_info_bar_font_size(self):
        """获取当前语言的信息栏字体大小设置

        Returns:
            int: 信息栏字体大小
        """
        current_language = get_language()
        return FontConfig.get_info_bar_font_size(current_language)
    
    def get_move_button_font(self):
        """获取当前语言的移动按钮字体设置

        Returns:
            str: 移动按钮字体
        """
        current_language = get_language()
        return FontConfig.get_move_button_font(current_language)

    def get_tab_width(self):
        """获取当前语言的标签宽度设置

        Returns:
            int: 标签宽度
        """
        current_language = get_language()
        return self._get_setting(self.TAB_WIDTH_SETTINGS, current_language)

    def get_tab_vertical_padding(self):
        """获取当前语言的标签页垂直内边距设置

        Returns:
            int: 标签页垂直内边距
        """
        current_language = get_language()
        return self._get_setting(self.TAB_VERTICAL_PADDING_SETTINGS, current_language)

    def get_button_size(self, button_type="default"):
        """获取当前语言的按钮尺寸设置

        Args:
            button_type: 按钮类型，支持 "default", "execute_planning", "export_planning", "export_result"

        Returns:
            tuple: (宽度, 高度)
        """
        current_language = get_language()

        if current_language in ["zh", "zh_tw"]:
            if button_type in ["execute_planning", "export_planning", "export_result"]:
                return (12, 10)
            return (12, 10)
        elif current_language in ["ja", "ko"]:
            if button_type in ["execute_planning", "export_planning", "export_result"]:
                return (16, 10)
            return (12, 10)
        else:
            if button_type in ["execute_planning", "export_planning", "export_result"]:
                return (16, 10)
            return (14, 10)

    def _configure_colored_tab(self, color_name, font_family, font_size):
        """配置彩色标签页样式

        Args:
            color_name: 颜色名称（Blue/Green/Purple）
            font_family: 字体名称
            font_size: 字体大小
        """
        if not self.style:
            return
            
        current_language = get_language()
        tab_padding = self._get_setting(self.TAB_PADDING_SETTINGS, current_language)
        style_config = self.TAB_STYLES[color_name]
        tab_style_name = f"{color_name}.TNotebook.Tab"

        self.style.configure(
            tab_style_name,
            background=style_config["background"],
            foreground=style_config["foreground"],
            padding=tab_padding,
            relief="flat",
            font=(font_family, font_size),
        )

        self.style.map(
            tab_style_name,
            background=[
                ("selected", style_config["selected_background"]),
                ("!selected", style_config["background"]),
            ],
            foreground=[
                ("selected", style_config["selected_foreground"]),
                ("!selected", style_config["foreground"]),
            ],
            font=[
                ("selected", (font_family, font_size, "bold")),
                ("!selected", (font_family, font_size, "normal")),
            ],
        )

    def update_all_styles(self):
        """更新所有样式，根据当前语言重新设置"""
        if not self.style:
            return

        current_language = get_language()
        font_family, font_size = self.get_current_font_settings()
        # 获取功能按钮的独立字体大小配置
        function_button_font_size = self.get_function_button_font_size()

        base_font_style = {"font": (font_family, font_size)}
        # 创建功能按钮的样式配置，使用独立的字体大小
        function_button_font_style = {"font": (font_family, function_button_font_size)}

        print(f"[StyleManager] 更新样式, 当前语言: {current_language}, 字体: {font_family}, 大小: {font_size}")

        # 基本控件样式
        self.style.configure("TLabel", **base_font_style)
        self.style.configure("TEntry", **base_font_style)
        self.style.configure("TFrame")
        self.style.configure("Error.TLabel", **base_font_style, foreground="#ff6b6b")
        self.style.configure("Success.TLabel", **base_font_style, foreground="#4ecdc4")

        # 按钮样式 - 默认按钮
        button_padding = self._get_setting(self.BUTTON_PADDING_SETTINGS, current_language)
        self.style.configure("TButton", **base_font_style, padding=button_padding)
        # 功能按钮样式 - 添加、删除、撤销、移动、导入等
        self.style.configure("Function.TButton", **function_button_font_style, padding=button_padding)
        # 移动按钮样式 - 使用独立的字体配置，大小继承自功能按钮
        move_button_font = FontConfig.get_move_button_font(current_language)
        move_button_style = {"font": (move_button_font, function_button_font_size)}
        self.style.configure("Move.TButton", **move_button_style, padding=button_padding)  # type: ignore

        # 滚动条样式
        scrollbar_style = {"width": 3}
        for scrollbar_type in ["TScrollbar", "Vertical.TScrollbar", "Horizontal.TScrollbar"]:
            self.style.configure(scrollbar_type, **scrollbar_style)

        # Notebook样式
        self.style.configure("TNotebook")

        # LabelFrame样式
        self.style.configure("TLabelframe")
        self.style.configure(
            "TLabelframe.Label",
            borderwidth=0,
            relief="flat",
            font=(font_family, font_size)
        )

        # 彩色标签页样式
        for color_name in ["Blue", "Green", "Purple"]:
            self._configure_colored_tab(color_name, font_family, font_size)

        # Treeview样式
        self.style.configure(
            "TTreeview",
            rowheight=25,
            padding=(5, 2),
            borderwidth=0,
            relief="flat",
        )

        # 表头样式
        self.style.configure(
            "TTreeview.Heading",
            font=(font_family, font_size, "bold"),
            padding=(10, 5),
            relief="ridge",
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
        print("[StyleManager] 样式管理器未初始化")


def get_current_font_settings():
    """获取当前语言的字体设置

    Returns:
        tuple: (字体名称, 字体大小)
    """
    if style_manager:
        return style_manager.get_current_font_settings()
    current_language = get_language()
    return FontConfig.get_ui_font_settings(current_language)


def get_pin_button_font_size():
    """获取当前语言的钉住按钮字体大小设置

    Returns:
        int: 钉住按钮字体大小
    """
    current_language = get_language()
    return FontConfig.get_pin_button_font_size(current_language)


def get_function_button_font_size():
    """获取当前语言的功能按钮字体大小设置（添加、删除、撤销、移动、导入等）

    Returns:
        int: 功能按钮字体大小
    """
    current_language = get_language()
    return FontConfig.get_function_button_font_size(current_language)


def get_info_bar_font_size():
    """获取当前语言的信息栏字体大小设置

    Returns:
        int: 信息栏字体大小
    """
    current_language = get_language()
    return FontConfig.get_info_bar_font_size(current_language)


def get_move_button_font():
    """获取当前语言的移动按钮字体设置

    Returns:
        str: 移动按钮字体名称
    """
    current_language = get_language()
    return FontConfig.get_move_button_font(current_language)
