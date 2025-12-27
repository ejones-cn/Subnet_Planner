#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子网规划师应用程序 - 主窗口
"""

# 所有导入语句放在最顶部
import tkinter as tk
import math
import datetime
import re
from tkinter import ttk, filedialog
import tkinter.font as tkfont
import sys
import os
import traceback
import csv

# 外部库导入
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# 导入自定义模块
from ip_subnet_calculator import (
    split_subnet,
    ip_to_int,
    get_subnet_info,
    suggest_subnet_planning,
    merge_subnets,
    get_ip_info,
    range_to_cidr,
    check_subnet_overlap,
)

# 导出工具模块
from export_utils import ExportUtils

# 版本管理模块
from version import get_version


# 自定义的ColoredNotebook类，支持每个标签不同颜色
class ColoredNotebook(ttk.Frame):
    def __init__(self, master, style=None, tab_change_callback=None, is_top_level=False, **kwargs):
        super().__init__(master, **kwargs)
        # 标识是否为顶级标签页
        self.is_top_level = is_top_level

        # 确保框架能够填充父容器的空间
        self.pack_propagate(True)
        self.grid_propagate(True)

        # 绑定大小变化事件，确保内容区域能正确调整大小
        self.bind('<Configure>', self.on_configure)

        # 保存样式对象
        self.style = style
        # 保存标签页切换回调函数
        self.tab_change_callback = tab_change_callback

        # 为每个实例生成唯一ID，用于创建唯一的样式名称
        self.unique_id = id(self)

        # 为每个Notebook实例创建唯一的样式名称
        self.light_blue_style = f"LightBlue{self.unique_id}.TFrame"
        self.light_green_style = f"LightGreen{self.unique_id}.TFrame"
        self.light_orange_style = f"LightOrange{self.unique_id}.TFrame"
        self.light_purple_style = f"LightPurple{self.unique_id}.TFrame"
        self.light_pink_style = f"LightPink{self.unique_id}.TFrame"

        # 初始化这些样式
        self.style.configure(self.light_blue_style, background="#e3f2fd")
        self.style.configure(self.light_green_style, background="#e8f5e9")
        self.style.configure(self.light_orange_style, background="#fff3e0")
        self.style.configure(self.light_purple_style, background="#f3e5f5")
        self.style.configure(self.light_pink_style, background="#fce4ec")

        # 颜色映射字典，用于优化重复的条件判断
        self.color_styles = {
            "#e3f2fd": self.light_blue_style,  # 蓝色标签
            "#e8f5e9": self.light_green_style,  # 绿色标签
            "#fff3e0": self.light_orange_style,  # 橙色标签
            "#f3e5f5": self.light_purple_style,  # 紫色标签
            "#fce4ec": self.light_pink_style,  # 粉色标签
            "#e0f2f1": self.light_blue_style,  # 青色标签
        }

        # 鼠标按下时的激活颜色映射
        self.mouse_down_colors = {
            "#e3f2fd": "#bbdefb",  # 蓝色标签
            "#e8f5e9": "#c8e6c9",  # 绿色标签
            "#fff3e0": "#ffe0b2",  # 橙色标签
            "#f3e5f5": "#e1bee7",  # 紫色标签
            "#fce4ec": "#f8bbd0",  # 粉色标签
            "#e0f2f1": "#b2dfdb",  # 青色标签
        }

        # 鼠标释放时的激活颜色映射
        self.mouse_up_colors = {
            "#e3f2fd": "#90caf9",  # 蓝色标签
            "#e8f5e9": "#a5d6a7",  # 绿色标签
            "#fff3e0": "#ffcc80",  # 橙色标签
            "#f3e5f5": "#ce93d8",  # 紫色标签
            "#fce4ec": "#f48fb1",  # 粉色标签
            "#e0f2f1": "#80deea",  # 青色标签
        }

        # 创建标签栏容器，使用ttk.Frame并继承默认样式
        self.tab_bar_container = ttk.Frame(self)
        self.tab_bar_container.pack(side="top", fill="x")

        # 创建标签栏 - 使用ttk.Frame并继承默认样式
        self.tab_bar = ttk.Frame(self.tab_bar_container)
        self.tab_bar.pack(side="left", fill="y")

        # 创建一个占位Frame，使用ttk.Frame并继承默认样式
        self.tab_bar_spacer = ttk.Frame(self.tab_bar_container)
        self.tab_bar_spacer.pack(side="left", fill="both", expand=True)

        # 创建右侧按钮容器 - 使用ttk.Frame并继承默认样式
        self.tab_bar_right_buttons = ttk.Frame(self.tab_bar_container)
        self.tab_bar_right_buttons.pack(side="right", fill="y")

        # 创建内容区域 - 移除箭头指向的灰色框线
        self.content_area = ttk.Frame(self, borderwidth=0, relief="flat")
        self.content_area.pack(side="top", fill="both", expand=True, padx=0, pady=0)

        # 确保content_area能完全填充笔记本控件的空间
        self.content_area.pack_propagate(True)
        self.content_area.grid_propagate(True)

        # 标签配置
        self.tabs = []
        self.active_tab = None

    def on_configure(self, _):
        """当笔记本控件大小变化时调用，确保内容区域能正确调整大小"""
        # 确保content_area能完全填充笔记本控件的空间
        if hasattr(self, 'content_area'):
            # 更新content_area的大小
            self.content_area.pack_configure(fill='both', expand=True)

            # 触发内容区域的重绘
            self.content_area.update_idletasks()

            # 如果有选中的标签，确保其内容框架也能正确调整大小
            if hasattr(self, 'active_tab') and self.active_tab is not None and 0 <= self.active_tab < len(self.tabs):
                selected_tab = self.tabs[self.active_tab]
                selected_tab["content"].pack_configure(fill='both', expand=True)

    def _on_tab_mouse_down(self, button, color):
        """当鼠标按下标签页时，更新内容区域背景色为按下状态颜色"""
        # 只有当前按下的标签页是激活标签页时才更新内容区域背景色
        if hasattr(self, "active_tab") and button.tab_index == self.active_tab:
            # 根据标签颜色设置内容区域背景色为按下状态颜色（使用之前的激活颜色，较暗）
            active_color = self.mouse_down_colors.get(color, "#e1bee7")
            # 获取对应的样式名称
            style_name = self.color_styles.get(color, self.light_blue_style)
            self.style.configure(style_name, background=active_color)

    def _on_tab_mouse_up(self, button, color):
        """当鼠标释放标签页时，恢复内容区域背景色为激活状态颜色"""
        # 只有当前释放的标签页是激活标签页时才更新内容区域背景色
        if hasattr(self, "active_tab") and button.tab_index == self.active_tab:
            # 根据标签颜色设置内容区域背景色为激活状态颜色（使用更亮的颜色）
            active_color = self.mouse_up_colors.get(color, "#ce93d8")
            # 获取对应的样式名称
            style_name = self.color_styles.get(color, self.light_blue_style)
            self.style.configure(style_name, background=active_color)

    def _update_background_to_result_frame_color(self):
        """更新标签栏背景色以匹配result_frame"""
        try:
            # 直接获取父容器的背景色，而不是通过style.lookup
            # 对于ttk组件，我们需要先获取其内部的label或content组件
            bg_color = None

            # 尝试多种方式获取父容器的背景色
            if hasattr(self.master, 'winfo_children'):
                # 获取父容器的子组件
                children = self.master.winfo_children()
                for child in children:
                    # 检查子组件是否有cget方法
                    if not hasattr(child, 'cget'):
                        continue
                    
                    # 尝试从子组件获取背景色
                    try:
                        child_bg = child.cget("background")
                        if child_bg and not child_bg.startswith("system."):
                            bg_color = child_bg
                            break
                    except (AttributeError, tk.TclError):
                        continue

            # 如果无法从子组件获取背景色，尝试直接从父容器获取
            if not bg_color or bg_color.startswith("system."):
                try:
                    bg_color = self.master.cget("background")
                except (AttributeError, tk.TclError):
                    pass

            # 如果还是无法获取背景色，使用默认的背景色
            if not bg_color or bg_color.startswith("system."):
                bg_color = self.style.lookup("TFrame", "background")

            # 使用style来设置ttk.Frame的背景色，为每个实例创建唯一的样式名称
            temp_style_name = f"TempColoredNotebookStyle{self.unique_id}.TFrame"
            self.style.configure(temp_style_name, background=bg_color)

            # 应用样式到所有ttk.Frame组件
            self.tab_bar_container.configure(style=temp_style_name)
            self.tab_bar.configure(style=temp_style_name)
            self.tab_bar_spacer.configure(style=temp_style_name)
            self.content_area.configure(style=temp_style_name)

        except (tk.TclError, AttributeError, ValueError):
            # 发生错误时，不设置自定义背景色，使用默认样式
            pass

    def add_tab(self, label, content_frame, color="#e0e0e0"):
        """添加一个新标签"""
        tab = {"label": label, "content": content_frame, "color": color, "button": None}

        # 创建标签按钮 - 移除边框和间距，使标签栏更好地融入背景
        # 设置初始样式参数
        button_params = {
            "text": label,
            "bg": color,
            "relief": "flat",
            "borderwidth": 0,
            "padx": 12,
            "pady": 5,
            "font": ("微软雅黑", 10, "normal"),
            "width": 10,  # 设置固定宽度，确保所有标签宽度一致
        }

        # 根据是否为顶级标签页设置不同的文字颜色和鼠标按下状态颜色
        if self.is_top_level:
            # 顶级标签页：默认深灰色文字，鼠标按下时更亮的橙色背景和深灰色文字
            button_params["foreground"] = "#333333"  # 默认深灰色文字
            button_params["activebackground"] = "#ffb74d"  # 亮橙色背景（比激活状态#ff9800更亮）
            button_params["activeforeground"] = "#333333"  # 深灰色文字
        else:
            # 内部标签页：默认深灰色文字，鼠标按下时使用比选中状态更亮的颜色和深灰色文字
            button_params["foreground"] = "#333333"  # 默认深灰色文字
            # 为内部标签页设置鼠标按下状态颜色（现在使用之前的激活状态颜色，较暗）
            button_params["activebackground"] = self.mouse_down_colors.get(color, "#e1bee7")
            button_params["activeforeground"] = "#333333"  # 深灰色文字

        button = tk.Button(self.tab_bar, **button_params)

        # 保存按钮对应的标签索引，以便在事件处理中使用
        button.tab_index = len(self.tabs)

        # 绑定标签页切换事件
        button.bind("<Button-1>", lambda e, t=len(self.tabs): self.select_tab(t))

        # 只有内部标签页需要为鼠标按下/释放添加内容区域背景色变化效果
        if not self.is_top_level:
            # 绑定鼠标按下事件 - 更新内容区域背景色为按下状态颜色
            button.bind("<Button-1>", lambda e, c=color: self._on_tab_mouse_down(e.widget, c), add="+")
            # 绑定鼠标释放事件 - 恢复内容区域背景色为激活状态颜色
            button.bind("<ButtonRelease-1>", lambda e, c=color: self._on_tab_mouse_up(e.widget, c), add="+")
        button.pack(side="left", padx=0, pady=0)

        tab["button"] = button
        self.tabs.append(tab)

        # 如果是第一个标签，自动选中
        if len(self.tabs) == 1:
            self.select_tab(0)
        else:
            # 确保所有标签页都应用正确的样式
            current_active_tab = getattr(self, "active_tab", 0)
            self.select_tab(current_active_tab)

    def select_tab(self, tab_index):
        """选中一个标签"""
        if tab_index < 0 or tab_index >= len(self.tabs):
            return

        # 隐藏所有内容
        for tab in self.tabs:
            tab["content"].pack_forget()

            # 根据是否为顶级标签页应用不同的非激活样式
            if self.is_top_level:
                # 顶级标签页非激活状态：灰底深灰色文字不加粗
                tab["button"].config(
                    relief="flat",
                    bg="#808080",  # 灰色背景
                    font=("微软雅黑", 10, "normal"),
                    foreground="white",  # 白色文字
                )
            else:
                # 内部标签页非激活状态：保持原有背景色，深灰色文字
                tab["button"].config(
                    relief="flat",
                    bg=tab["color"],
                    font=("微软雅黑", 10, "normal"),
                    foreground="#333333",  # 默认深灰色文字
                )

        # 显示选中的标签内容
        selected_tab = self.tabs[tab_index]
        selected_tab["content"].pack(fill="both", expand=True, padx=0, pady=0)

        # 更新当前激活的标签页索引
        self.active_tab = tab_index

        # 根据是否为顶级标签页应用不同的激活样式
        if self.is_top_level:
            # 顶级标签页激活状态：橙底黑字并加粗
            selected_tab["button"].config(
                relief="flat",
                bg="#ff9800",  # 橙色背景
                font=("微软雅黑", 10, "bold"),  # 加粗字体
                foreground="#000000",  # 黑色文字
            )
        else:
            # 内部标签页激活状态：使用更亮的颜色（之前的鼠标按下颜色）
            selected_color = self.mouse_up_colors.get(selected_tab["color"], "#ce93d8")

            selected_tab["button"].config(
                relief="flat", bg=selected_color, font=("微软雅黑", 10, "bold"), foreground="#000000"
            )

        # 更新对应内容框架样式的背景色，使其与选中标签的颜色保持一致
        # 只有内部标签页需要更新样式，顶级标签页不需要
        if not self.is_top_level:
            # 获取对应的样式名称
            style_name = self.color_styles.get(selected_tab["color"], self.light_blue_style)
            self.style.configure(style_name, background=selected_color)

        # 更新背景色以匹配result_frame
        self._update_background_to_result_frame_color()

        # 调用标签页切换回调函数
        if self.tab_change_callback:
            self.tab_change_callback(tab_index)


class IPSubnetSplitterApp:
    def validate_cidr(self, text, entry=None, style_based=False):
        """通用CIDR验证函数

        Args:
            text: 要验证的CIDR字符串
            entry: 可选的输入框对象，用于显示验证结果
            style_based: 是否使用样式来显示验证结果，否则使用前景色

        Returns:
            验证结果，True表示有效，False表示无效，"1"表示用于validatecommand的有效
        """
        text = text.strip()
        is_valid = bool(re.match(self.cidr_pattern, text)) if text else True

        if entry:
            if style_based:
                entry.config(style='Valid.TEntry' if is_valid else 'Invalid.TEntry')
            else:
                entry.config(foreground='black' if is_valid else 'red')

        # 对于validatecommand，始终返回"1"，允许所有输入，只做视觉提示
        # 对于直接调用，返回布尔值表示验证结果
        return "1" if entry else is_valid

    def __init__(self, main_window):
        # 应用程序信息
        self.app_name = "子网规划师"
        self.app_version = get_version()

        # CIDR格式验证正则表达式
        self.cidr_pattern = (
            r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            + r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/'
            + r'([0-9]|[1-2][0-9]|3[0-2])$'
        )

        # 存储删除记录历史，支持多次撤销
        self.deleted_history = []

        # 高级工具历史记录列表
        self.ipv4_history = ["192.168.1.1"]  # IPv4地址查询历史
        self.ipv6_history = ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"]  # IPv6地址查询历史
        self.range_start_history = ["192.168.0.1"]  # IP范围起始地址历史
        self.range_end_history = ["192.168.30.254"]  # IP范围结束地址历史

        # 切分子网相关属性
        self.split_parent_networks = []
        self.split_networks = []
        self.parent_entry = None
        self.split_entry = None
        self.execute_btn = None
        self.reexecute_btn = None
        self.history_tree = None
        self.export_btn = None
        self.notebook = None
        self.split_info_frame = None
        self.split_tree = None
        self.remaining_frame = None
        self.remaining_tree = None
        self.chart_frame = None
        self.chart_scrollbar = None
        self.chart_canvas = None
        self.remaining_scroll_v = None
        self.chart_data = None

        # 网段规划相关属性
        self.planning_parent_networks = []
        self.planning_parent_entry = None
        self.pool_tree = None
        self.pool_scrollbar = None
        self.requirements_tree = None
        self.requirements_scrollbar = None
        self.undo_delete_btn = None
        self.swap_btn = None
        self.planning_notebook = None
        self.execute_planning_btn = None
        self.allocated_frame = None
        self.allocated_tree = None
        self.planning_remaining_frame = None
        self.planning_remaining_tree = None

        # 编辑相关属性
        self.edit_entry = None
        self.current_edit_item = None
        self.current_edit_column = None
        self.current_edit_column_index = None
        self.current_edit_tree = None

        # 高级工具相关属性
        self.advanced_notebook = None
        self.ipv4_info_frame = None
        self.ipv6_info_frame = None
        self.merge_frame = None
        self.overlap_frame = None
        self.ipv6_info_entry = None
        self.ipv6_cidr_var = None
        self.ipv6_cidr_combobox = None
        self.ipv6_info_btn = None
        self.ipv6_info_tree = None
        self.subnet_merge_text = None
        self.merge_btn = None
        self.range_start_entry = None
        self.range_end_entry = None
        self.range_to_cidr_btn = None
        self.merge_result_frame = None
        self.merge_result_tree = None
        self.merge_result_scrollbar = None
        self.ip_info_entry = None
        self.subnet_mask_cidr_map = None
        self.cidr_subnet_mask_map = None
        self.ip_mask_var = None
        self.ip_mask_combobox = None
        self.ip_cidr_var = None
        self.ip_cidr_combobox = None
        self.ip_info_btn = None
        self.ip_info_tree = None
        self.overlap_text = None
        self.overlap_btn = None
        self.overlap_result_tree = None

        # 其他属性
        self.theme_var = None
        self.is_pinned = None

        # 初始化导出工具
        self.export_utils = ExportUtils()

        self.root = main_window
        self.root.title(f"子网规划师 v{self.app_version}")
        # 所有窗口大小、位置和限制设置都由主程序入口统一管理
        # 这里只设置窗口标题

        # 设置样式
        self.style = ttk.Style()

        # 使用默认主题
        self.style.theme_use("vista")

        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TButton", font=("微软雅黑", 10), focuscolor="#888888", focuswidth=1)
        self.style.configure("TEntry", font=("微软雅黑", 10))
        # 设置滚动条宽度一致 - 针对Windows平台的特殊处理
        # 恢复默认滚动条布局，包含完整的箭头元素
        # 当滚动条未激活时，通过回调函数隐藏整个滚动条
        # 设置滚动条宽度
        self.style.configure("TScrollbar", width=5)
        self.style.configure("Vertical.TScrollbar", width=5)
        self.style.configure("Horizontal.TScrollbar", width=5)

        # 为按钮添加焦点样式映射，进一步控制焦点效果
        self.style.map(
            "TButton",
            focuscolor=[("focus", "#888888"), ("!focus", "#888888")],
            focuswidth=[("focus", 1), ("!focus", 1)],
        )

        # 恢复窗口原始背景色，使用系统默认颜色以保持界面协调
        # 不设置自定义的window_bg，让系统使用默认的背景色方案

        # 保持ttk组件的默认背景色，让系统主题来处理颜色协调问题
        # 只保留之前设置的字体样式，不修改背景色

        # 优化的标签样式设置
        try:
            # 设置Notebook的基本样式，使用默认边框样式
            self.style.configure("TNotebook", background="#ffffff")

            # 使用默认边框样式，移除深灰色边框
            self.style.configure("TLabelframe")
            # 增大LabelFrame标题的字体大小
            self.style.configure("TLabelframe.Label", borderwidth=0, relief="flat", font=("微软雅黑", 12))

            # 移除对所有标签的基础样式配置，避免干扰特定标签样式
            # 直接为每个标签样式配置完整的样式属性

            # 为三个标签页分别创建不同颜色的标签样式 - 现代化配色方案
            # 蓝色标签样式 - 切分段信息
            self.style.configure(
                "Blue.TNotebook.Tab",
                background="#e3f2fd",  # 浅蓝色背景
                foreground="#1976d2",  # 深蓝色文字
                padding=(15, 6),  # 增加内边距
                relief="flat",  # 边框样式
                font=("微软雅黑", 10),
            )  # 统一字体

            # 蓝色标签选中状态
            self.style.map(
                "Blue.TNotebook.Tab",
                background=[
                    ("selected", "#2196f3"),  # 选中时使用更鲜艳的蓝色
                    ("!selected", "#e3f2fd"),
                ],  # 非选中时的背景色
                foreground=[("selected", "white"), ("!selected", "#1976d2")],  # 选中时白色文字
                font=[
                    ("selected", ("微软雅黑", 10, "bold")),
                    ("!selected", ("微软雅黑", 10, "normal")),
                ],  # 选中时加粗，非选中时正常
            )  # 非选中时的文字颜色

            # 绿色标签样式 - 剩余网段表
            self.style.configure(
                "Green.TNotebook.Tab",
                background="#e8f5e9",  # 浅绿色背景
                foreground="#388e3c",  # 深绿色文字
                padding=(15, 6),  # 增加内边距
                relief="flat",  # 边框样式
                font=("微软雅黑", 10),
            )  # 统一字体

            # 绿色标签选中状态
            self.style.map(
                "Green.TNotebook.Tab",
                background=[
                    ("selected", "#4caf50"),  # 选中时使用更鲜艳的绿色
                    ("!selected", "#e8f5e9"),
                ],  # 非选中时的背景色
                foreground=[("selected", "white"), ("!selected", "#388e3c")],  # 选中时白色文字
                font=[
                    ("selected", ("微软雅黑", 10, "bold")),
                    ("!selected", ("微软雅黑", 10, "normal")),
                ],  # 选中时加粗，非选中时正常
            )  # 非选中时的文字颜色

            # 紫色标签样式 - 网段分布图
            self.style.configure(
                "Purple.TNotebook.Tab",
                background="#f3e5f5",  # 浅紫色背景
                foreground="#7b1fa2",  # 深紫色文字
                padding=(15, 6),  # 增加内边距
                relief="flat",  # 边框样式
                font=("微软雅黑", 10),
            )  # 统一字体

            # 紫色标签选中状态
            self.style.map(
                "Purple.TNotebook.Tab",
                background=[
                    ("selected", "#9c27b0"),  # 选中时使用更鲜艳的紫色
                    ("!selected", "#f3e5f5"),
                ],  # 非选中时的背景色
                foreground=[("selected", "white"), ("!selected", "#7b1fa2")],  # 选中时白色文字
                font=[
                    ("selected", ("微软雅黑", 10, "bold")),
                    ("!selected", ("微软雅黑", 10, "normal")),
                ],  # 选中时加粗，非选中时正常
            )  # 非选中时的文字颜色

            print("标签样式设置完成")

        except (tk.TclError, AttributeError):
            pass
        # 为Treeview添加表格线样式配置 - Windows系统专用解决方案
        # 在Windows上强制显示表格线的最终解决方案

        # 使用最基本、最兼容的样式设置
        # 在Windows系统上，简单的样式设置反而更可靠

        # 1. 基础Treeview样式设置 - 修复Windows表格线显示问题
        # 在Windows上，Treeview的表格线需要通过特定的样式配置来实现
        self.style.configure(
            "TTreeview",
            background="#e0e0e0",  # 设置背景色为浅灰色，与单元格背景色形成对比
            fieldbackground="#ffffff",  # 单元格背景设为白色
            foreground="black",  # 文本颜色
            rowheight=25,  # 调整行高，让表格线更明显
            padding=(5, 2),  # 调整内边距，让表格线更明显
            borderwidth=0,  # 去掉表格外框
            relief="flat",  # 去掉边框样式
        )

        # 2. 表头样式设置 - 确保表头与表格线协调
        self.style.configure(
            "TTreeview.Heading",
            background="#1976d2",
            foreground="white",
            font=("微软雅黑", 10, "bold"),
            padding=(10, 5),  # 增大表头内边距
            relief="ridge",  # 表头使用凸起样式，与表格线形成对比
        )

        # 3. 去掉Treeview外框
        self.style.configure("TTreeview", borderwidth=0, relief="flat")

        # 4. 启用斑马条纹，通过背景色对比来增强表格线效果
        # 斑马条纹样式已经在configure_treeview_styles方法中配置

        # 2. 表头样式设置，移除深灰色边框，使用默认颜色
        self.style.configure(
            "TTreeview.Heading",
            background="#1976d2",
            foreground="white",
            font=("微软雅黑", 10, "bold"),
            padding=(5, 3),
            relief="flat",  # 去掉表头边框样式
            borderwidth=0,  # 去掉表头边框宽度
        )

        # 3. 选中状态设置
        # 修改Treeview的选中背景色为#4A6984
        self.style.map("TTreeview", background=[("selected", "#4A6984")], foreground=[("selected", "white")])

        # 添加Combobox样式设置，只修改选中颜色
        self.style.map(
            "TCombobox",
            selectbackground=[("focus", "#4A6984"), ("!focus", "#4A6984")],
            selectforeground=[("focus", "white"), ("!focus", "white")],
        )

        # 7. 信息栏样式配置 - 紧凑设计，调大字体
        # 统一使用#DCDAD5背景色，仅保留文字颜色区分，增大字体大小
        self.style.configure("Success.TLabel", foreground="#424242", font=("微软雅黑", 9), relief="flat")
        self.style.configure("Error.TLabel", foreground="#c62828", font=("微软雅黑", 9), relief="flat")
        self.style.configure("Info.TLabel", foreground="#424242", font=("微软雅黑", 9), relief="flat")

        # 信息栏框架样式 - 使用极淡灰色边框
        self.style.configure("InfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5")
        self.style.configure("SuccessInfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5")
        self.style.configure("ErrorInfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5")
        self.style.configure("InfoInfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5")

        # 8. 斑马条纹样式配置
        # 在Treeview中通过标签(tags)实现斑马条纹效果
        # 注意：ttk.Style不直接支持斑马条纹，需要在插入行时使用tags

        # 初始化历史记录相关属性
        self.history_states = []
        self.current_history_index = -1
        self.planning_history_records = []

        # 添加组合键绑定，用于测试信息栏（彩蛋功能）
        # 使用Ctrl+Shift+I组合键打开/关闭测试信息栏
        self.root.bind('<Control-Shift-Key-I>', self.toggle_test_info_bar)
        # 保存测试信息栏的状态
        self.test_info_bar_enabled = False

        # 创建主框架 - 调整内边距使其更加紧凑
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建信息栏框架 - 放置在main_frame中，位于底部
        self.info_bar_frame = ttk.Frame(self.main_frame, style="InfoBar.TFrame")
        # 默认隐藏，使用pack_forget()
        self.info_bar_frame.pack_forget()
        # 先设置信息栏的布局，确保它在底部
        self.info_bar_frame.pack(side="bottom", fill="x", pady=(0, 10), padx=10)
        # 立即隐藏，等待需要时显示
        self.info_bar_frame.pack_forget()

        # 创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块
        self.create_top_level_notebook()

        # 在右上角添加关于链接按钮和钉住按钮，确保它们显示在标题栏右侧
        self.create_about_link()

        # 信息栏高度统一为30px，与place布局一致
        self.info_bar_frame.configure(height=30)  # 使用正确的高度值30px

        # 确保信息栏框架的grid布局配置正确
        self.info_bar_frame.grid_rowconfigure(0, weight=1)  # 行填充整个高度
        # 信息标签列占满所有剩余空间
        self.info_bar_frame.grid_columnconfigure(0, weight=1)  # 权重1，占据所有剩余空间
        # 关闭按钮列固定宽度，不占据剩余空间
        self.info_bar_frame.grid_columnconfigure(1, weight=0)  # 权重0，固定宽度

        # 设置关闭按钮样式，使其宽度与高度一致（30px）
        self.style.configure(
            "InfoBarCloseButton.TButton",
            padding=(2, 0),  # 按用户要求设置padding为(2, 0)
            foreground="#9E9E9E",
            font=("微软雅黑", 8),
            width=2,  # 字符宽度，配合padding使用
        )
        # 使用默认的颜色和其他样式

        # 改用grid布局，确保关闭按钮始终可见
        # 重置grid配置
        self.info_bar_frame.grid_rowconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(0, weight=1)  # 信息标签占主要空间
        self.info_bar_frame.grid_columnconfigure(1, weight=0)  # 关闭按钮固定宽度

        # 信息标签使用grid布局，不设置固定宽度，为边框留出空间
        # 调整padding，为边框留出空间
        # padding格式：(left, top, right, bottom)
        self.info_label = ttk.Label(
            self.info_bar_frame, text="", padding=(3, 3, 0, 0), anchor="w"
        )  # 减小内边距，为边框留出空间
        # 为边框留出空间，上下各2px，左右各3px
        self.info_label.grid(row=0, column=0, sticky="ew", padx=(3, 0), pady=2)  # 为边框留出空间

        # 关闭按钮使用grid布局，减小左侧边距，让文字能更接近关闭按钮
        # 使用tk.Button而非ttk.Button，避免Windows平台样式限制
        self.info_close_btn = ttk.Button(
            self.info_bar_frame,
            text="✕",
            command=self.hide_info_bar,
            style="InfoBarCloseButton.TButton",  # 使用自定义样式，确保宽度与高度一致
            cursor="hand2",
        )
        # 调整sticky参数为"ns"，确保垂直居中
        # 减小左侧边距，从0改为0px，右侧边距6px，调整pady为1，与信息栏高度一致
        self.info_close_btn.grid(row=0, column=1, padx=(0, 3), pady=2)  # 左侧边距0px，右侧边距6px，与信息栏高度一致

        # 初始化信息栏状态
        self.info_auto_hide_id = None  # 保存自动隐藏的定时器ID

        # 确保信息标签显示在关闭按钮上层
        self.info_label.lift(self.info_close_btn)

        # 初始化图表数据
        self.chart_data = None

        # 初始化历史记录
        self.history_records = []

        # 创建临时标签用于测量文本宽度，避免重复创建和销毁
        self._temp_label = tk.Label(self.root)
        self._temp_label.pack_forget()

        # 信息栏相关常量
        self.INFO_BAR_LEFT_OFFSET = 235
        self.INFO_BAR_RIGHT_OFFSET = 136
        self.INFO_BAR_PADDING = 3
        self.MIN_INFO_BAR_WIDTH = 300
        self.CLOSE_BTN_WIDTH = 30
        self.MIN_PIXEL_WIDTH = 50
        self.INFO_BAR_PLACE_LEFT = 238
        self.INFO_BAR_PLACE_RIGHT = 136
        self.INFO_BAR_PLACE_Y = 21.5
        self.INFO_BAR_PLACE_HEIGHT = 30
        self.MIN_INFO_BAR_PLACE_WIDTH = 300

        """验证CIDR格式是否有效
        
        Args:
            cidr: 要验证的CIDR字符串
            
        Returns:
            bool: 如果CIDR格式有效则返回True，否则返回False
        """

    def update_history_tree(self):
        """更新历史记录列表"""
        try:
            # 清空现有历史记录
            self.clear_tree_items(self.history_tree)

            # 重新插入所有历史记录
            for index, history_record in enumerate(self.history_records, 1):
                # 设置斑马条纹标签
                tags = ("even",) if index % 2 == 0 else ("odd",)
                # 格式化为: 1.  10.0.0.8/5 | 10.21.60.0/23
                formatted_record = f"{index}. {history_record['parent']}  |  {history_record['split']}"
                self.history_tree.insert("", tk.END, values=(formatted_record,), tags=tags)
        except (tk.TclError, AttributeError) as e:
            # 错误处理，确保GUI更新失败不会导致程序崩溃
            print(f"更新历史记录列表失败: {str(e)}")

    def reexecute_split(self):
        """从历史记录重新执行切分操作"""
        # 获取选中的历史记录
        selected_items = self.history_tree.selection()
        if not selected_items:
            self.show_info("提示", "请选择一条历史记录")
            return

        # 获取选中项的值
        selected_item = selected_items[0]
        item_values = self.history_tree.item(selected_item, "values")

        if not item_values:
            return

        # 解析格式化的记录字符串："1. 10.0.0.8/5 | 10.21.60.0/23"
        record_str = item_values[0]
        # 移除序号部分，保留后面的网段信息
        # 使用更灵活的分割方式，处理不同数量的空格
        # 匹配序号后的网段信息，例如："1.  10.0.0.8/5 | 10.21.60.0/23" -> "10.0.0.8/5 | 10.21.60.0/23"
        match = re.match(r'^\d+\.\s+(.*)$', record_str)
        if not match:
            return
        network_part = match.group(1)

        # 分割父网段和切分段，处理不同数量的空格
        parts = re.split(r'\s*\|\s*', network_part)
        if len(parts) < 2:
            return

        # 提取父网段和切分段
        parent = parts[0]
        split = parts[1]

        # 填充到输入框
        self.parent_entry.delete(0, tk.END)
        self.parent_entry.insert(0, parent)
        self.split_entry.delete(0, tk.END)
        self.split_entry.insert(0, split)

        # 执行切分，设置from_history=True，不记入历史
        self.execute_split(from_history=True)

    # def update_planning_history_tree(self):
    #     """更新子网规划历史记录列表"""
    #     # 清空现有历史记录
    #     for item in self.planning_history_tree.get_children():
    #         self.planning_history_tree.delete(item)
    #
    #     # 重新插入所有历史记录
    #     for index, history_record in enumerate(self.planning_history_records, 1):
    #         # 格式化记录内容
    #         if history_record['action_type'] == "初始状态":
    #             base_record = f"{index}. 初始状态"
    #         elif history_record['action_type'].startswith("删除子网") or history_record['action_type'].startswith("添加子网"):
    #             # 对于删除和添加操作，只显示操作本身的信息，不显示所有子网
    #             base_record = f"{index}. {history_record['action_type']}"
    #         else:
    #             base_record = f"{index}. {history_record['action_type']}: {history_record['req_str']}"
    #
    #         # 为当前步骤添加明显标记
    #         if index - 1 == self.current_history_index:
    #             formatted_record = f"→ {base_record}"
    #             tags = ("even" if index % 2 == 0 else "odd", "current")
    #         else:
    #             formatted_record = f"  {base_record}"
    #             tags = ("even" if index % 2 == 0 else "odd",)
    #
    #         # 插入历史记录
    #         self.planning_history_tree.insert(
    #             "",
    #             tk.END,
    #             values=(formatted_record,),
    #             tags=tags
    #         )

    # def update_current_operation_indicator(self):
    #     """更新当前操作记录的指示"""
    #     # 更新历史记录树，显示当前操作的指示
    #     self.update_planning_history_tree()

    # def reexecute_planning_from_history(self, event):
    #     """从历史记录重新执行子网规划"""
    #     # 获取选中的历史记录（双击事件会自动选择）
    #     selected_items = self.planning_history_tree.selection()
    #     if not selected_items:
    #         return
    #
    #     # 获取选中项的索引
    #     selected_item = selected_items[0]
    #     # 获取选中项在树中的索引
    #     item_index = self.planning_history_tree.index(selected_item)
    #
    #     # 获取对应的历史记录
    #     if 0 <= item_index < len(self.planning_history_records):
    #         history_record = self.planning_history_records[item_index]
    #
    #         # 更新父网段输入框
    #         self.planning_parent_entry.delete(0, tk.END)
    #         self.planning_parent_entry.insert(0, history_record['parent'])
    #
    #         # 清空现有子网需求
    #         for item in self.requirements_tree.get_children():
    #             self.requirements_tree.delete(item)
    #
    #         # 添加历史记录中的子网需求
    #         for i, (name, hosts) in enumerate(history_record['requirements']):
    #             tags = ("even",) if i % 2 == 0 else ("odd",)
    #             self.requirements_tree.insert("", tk.END, values=("", name, hosts), tags=tags)
    #
    #         # 更新序号和斑马条纹
    #         self.update_requirements_tree_zebra_stripes()
    #
    #         # 执行子网规划，设置from_history=True，不记入历史
    #         self.execute_subnet_planning(from_history=True)

    def save_current_state(self, action_type):
        """保存当前状态到操作记录中

        Args:
            action_type: 操作类型描述
        """
        # 获取当前子网需求
        subnet_requirements = []
        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item, "values")
            subnet_requirements.append((values[1], int(values[2])))

        # 获取当前父网段
        parent = self.planning_parent_entry.get().strip()

        # 格式化需求信息
        req_str = ", ".join([f"{name}({hosts})" for name, hosts in subnet_requirements])

        # 创建操作记录
        history_record = {
            'action_type': action_type,
            'parent': parent,
            'requirements': subnet_requirements,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'req_str': req_str,
        }

        # 检查当前状态是否与上一个状态相同，如果相同则不保存
        # 只有当连续两次都是"执行规划"操作且状态相同时才跳过
        if self.history_states and action_type == "执行规划" and self.history_states[-1]['action_type'] == "执行规划":
            last_state = self.history_states[-1]
            if last_state['requirements'] == subnet_requirements and last_state['parent'] == parent:
                return

        # 如果当前不是最新状态，截断历史记录
        if self.current_history_index < len(self.history_states) - 1:
            self.history_states = self.history_states[: self.current_history_index + 1]
            self.planning_history_records = self.planning_history_records[: self.current_history_index + 1]

        # 添加新状态
        self.history_states.append(history_record)
        self.planning_history_records.append(history_record)
        self.current_history_index += 1

        # 只保留最近20条状态记录
        if len(self.history_states) > 20:
            self.history_states.pop(0)
            self.planning_history_records.pop(0)
            self.current_history_index -= 1

        # 注意：由于操作记录功能已改为需求池功能，以下历史记录相关功能已不再需要
        # self.update_planning_history_tree()
        # self.update_undo_redo_buttons_state()

    def _move_records_between_trees(self, source_tree, target_tree, selected_items, move_from, move_to):
        """通用方法：在两个树之间移动记录（支持多条记录，移动后保持选中）
        
        Args:
            source_tree: 源树控件
            target_tree: 目标树控件
            selected_items: 选中的项目ID列表
            move_from: 移动来源的描述（用于错误提示）
            move_to: 移动目标的描述（用于错误提示）
            
        Returns:
            list: 新插入的项目ID列表，用于后续选中操作
        """
        if not selected_items:
            self.show_info("提示", f"请先选择要移动的{move_from}记录")
            return []

        # 先检查所有选中记录是否都可以移动
        # 同时收集要移动的记录数据
        items_to_move = []
        for selected_item in selected_items:
            values = source_tree.item(selected_item, "values")
            name = values[1]
            hosts = values[2]
            items_to_move.append({"name": name, "hosts": hosts})

            # 检查目标表中是否已存在相同名称的记录
            for item in target_tree.get_children():
                target_values = target_tree.item(item, "values")
                if target_values[1] == name:
                    self.show_error("错误", f"{move_to}中已存在名称为 '{name}' 的记录")
                    return []

        # 执行移动操作，并保存新插入记录的ID
        new_target_items = []
        
        # 先从源树删除所有选中记录
        for selected_item in selected_items:
            source_tree.delete(selected_item)

        # 然后插入到目标树，并保存新记录的ID
        for data in items_to_move:
            new_item_id = target_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
            new_target_items.append(new_item_id)

        # 更新序号和斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()

        return new_target_items
        
    def move_left(self):
        """向左移：从子网需求表向需求池移动记录（支持多条记录，移动后保持选中）"""
        selected_items = self.requirements_tree.selection()
        new_items = self._move_records_between_trees(
            source_tree=self.requirements_tree, 
            target_tree=self.pool_tree, 
            selected_items=selected_items, 
            move_from="子网需求表", 
            move_to="需求池"
        )
        
        # 移动完成后，在目标树中选中刚刚移动的记录
        if new_items:
            self.pool_tree.selection_set(*new_items)
    def move_right(self):
        """向右移：从需求池向子网需求表移动记录（支持多条记录，移动后保持选中）"""
        selected_items = self.pool_tree.selection()
        new_items = self._move_records_between_trees(
            source_tree=self.pool_tree, 
            target_tree=self.requirements_tree, 
            selected_items=selected_items, 
            move_from="需求池", 
            move_to="子网需求表"
        )
        
        # 移动完成后，在目标树中选中刚刚移动的记录
        if new_items:
            self.requirements_tree.selection_set(*new_items)
    def move_records(self):
        """根据选中情况自动判断移动方向：
        - 仅选中子网需求表数据：移动到需求池
        - 仅选中需求池数据：移动到子网需求表
        - 同时选中两个表数据：交换数据
        """
        # 获取两个表格中的选中记录
        selected_requirements = self.requirements_tree.selection()
        selected_pool_items = self.pool_tree.selection()
        
        # 情况1：仅选中子网需求表数据，移动到需求池
        if selected_requirements and not selected_pool_items:
            new_items = self._move_records_between_trees(
                source_tree=self.requirements_tree, 
                target_tree=self.pool_tree, 
                selected_items=selected_requirements, 
                move_from="子网需求表", 
                move_to="需求池"
            )
            
            # 移动完成后，在目标树中选中刚刚移动的记录
            if new_items:
                self.pool_tree.selection_set(*new_items)
        
        # 情况2：仅选中需求池数据，移动到子网需求表
        elif not selected_requirements and selected_pool_items:
            new_items = self._move_records_between_trees(
                source_tree=self.pool_tree, 
                target_tree=self.requirements_tree, 
                selected_items=selected_pool_items, 
                move_from="需求池", 
                move_to="子网需求表"
            )
            
            # 移动完成后，在目标树中选中刚刚移动的记录
            if new_items:
                self.requirements_tree.selection_set(*new_items)
        
        # 情况3：同时选中两个表数据，交换数据
        elif selected_requirements and selected_pool_items:
            # 准备交换的记录数据
            req_items_to_move = []
            for item in selected_requirements:
                values = self.requirements_tree.item(item, "values")
                req_items_to_move.append({"name": values[1], "hosts": values[2]})

            pool_items_to_move = []
            for item in selected_pool_items:
                values = self.pool_tree.item(item, "values")
                pool_items_to_move.append({"name": values[1], "hosts": values[2]})

            # 检查交换后是否会导致重复名称
            req_names_to_swap = [data["name"] for data in req_items_to_move]
            pool_names_to_swap = [data["name"] for data in pool_items_to_move]

            # 检查需求池表
            all_pool_names = []
            for item in self.pool_tree.get_children():
                if item not in selected_pool_items:
                    values = self.pool_tree.item(item, "values")
                    all_pool_names.append(values[1])

            for name in req_names_to_swap:
                if name in all_pool_names:
                    self.show_error("错误", f"需求池中已存在名称为 '{name}' 的记录")
                    return

            # 检查子网需求表
            all_req_names = []
            for item in self.requirements_tree.get_children():
                if item not in selected_requirements:
                    values = self.requirements_tree.item(item, "values")
                    all_req_names.append(values[1])

            for name in pool_names_to_swap:
                if name in all_req_names:
                    self.show_error("错误", f"子网需求表中已存在名称为 '{name}' 的记录")
                    return

            # 执行交换操作
            new_req_items = []
            new_pool_items = []

            # 删除所有选中的记录
            for item in selected_requirements:
                self.requirements_tree.delete(item)

            for item in selected_pool_items:
                self.pool_tree.delete(item)

            # 将需求池的记录添加到子网需求表
            for data in pool_items_to_move:
                new_item_id = self.requirements_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
                new_req_items.append(new_item_id)

            # 将子网需求表的记录添加到需求池
            for data in req_items_to_move:
                new_item_id = self.pool_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
                new_pool_items.append(new_item_id)

            # 更新两个表格的序号和斑马条纹
            self.update_requirements_tree_zebra_stripes()
            self.update_pool_tree_zebra_stripes()
            
            # 交换完成后，选中所有新插入的记录
            if new_req_items:
                self.requirements_tree.selection_set(*new_req_items)
            if new_pool_items:
                self.pool_tree.selection_set(*new_pool_items)
        
        # 情况4：未选中任何记录
        else:
            self.show_info("提示", "请选择要移动或交换的记录")
            return
    def swap_records(self):
        """交换两个表格中选中的记录（支持多条记录，完全交换所有选中记录）"""
        # 获取两个表格中的选中记录
        selected_requirements = self.requirements_tree.selection()
        selected_pool_items = self.pool_tree.selection()

        # 检查是否同时选中了两个表格中的记录
        if not selected_requirements or not selected_pool_items:
            self.show_info("提示", "请同时选择两个表格中的记录进行交换")
            return

        # 准备交换的记录数据
        # 1. 从子网需求表收集所有选中记录的数据
        req_items_to_move = []
        for item in selected_requirements:
            values = self.requirements_tree.item(item, "values")
            req_items_to_move.append({"name": values[1], "hosts": values[2]})

        # 2. 从需求池表收集所有选中记录的数据
        pool_items_to_move = []
        for item in selected_pool_items:
            values = self.pool_tree.item(item, "values")
            pool_items_to_move.append({"name": values[1], "hosts": values[2]})

        # 第一阶段：检查所有交换后是否会导致重复名称
        # 收集所有要交换的名称
        req_names_to_swap = [data["name"] for data in req_items_to_move]
        pool_names_to_swap = [data["name"] for data in pool_items_to_move]

        # 检查需求池表：要交换到需求池的req_names是否与需求池中已有的名称冲突（排除当前选中的pool_items）
        all_pool_names = []
        for item in self.pool_tree.get_children():
            if item not in selected_pool_items:
                values = self.pool_tree.item(item, "values")
                all_pool_names.append(values[1])

        for name in req_names_to_swap:
            if name in all_pool_names:
                self.show_error("错误", f"需求池中已存在名称为 '{name}' 的记录")
                return

        # 检查子网需求表：要交换到子网需求表的pool_names是否与子网需求表中已有的名称冲突（排除当前选中的req_items）
        all_req_names = []
        for item in self.requirements_tree.get_children():
            if item not in selected_requirements:
                values = self.requirements_tree.item(item, "values")
                all_req_names.append(values[1])

        for name in pool_names_to_swap:
            if name in all_req_names:
                self.show_error("错误", f"子网需求表中已存在名称为 '{name}' 的记录")
                return

        # 第二阶段：执行完全交换操作
        swapped_records = []

        # 保存新插入记录的ID，用于交换后重新选中
        new_req_items = []
        new_pool_items = []

        # 1. 先删除所有选中的记录
        # 从子网需求表删除选中记录
        for item in selected_requirements:
            self.requirements_tree.delete(item)

        # 从需求池表删除选中记录
        for item in selected_pool_items:
            self.pool_tree.delete(item)

        # 2. 然后将对方的记录添加到自己的表格中
        # 将需求池的记录添加到子网需求表，并保存新插入记录的ID
        for data in pool_items_to_move:
            new_item_id = self.requirements_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
            new_req_items.append(new_item_id)
            swapped_records.append(f"{data['name']} ↔ ...")

        # 将子网需求表的记录添加到需求池，并保存新插入记录的ID
        for data in req_items_to_move:
            new_item_id = self.pool_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
            new_pool_items.append(new_item_id)

        # 更新两个表格的序号和斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()

        # 3. 交换完成后，重新选中刚刚交换的记录
        # 选中子网需求表中刚刚交换的记录
        if new_req_items:
            # selection_set不能直接接受列表，需要将列表转换为单独的参数
            self.requirements_tree.selection_set(*new_req_items)

        # 选中需求池表中刚刚交换的记录
        if new_pool_items:
            # selection_set不能直接接受列表，需要将列表转换为单独的参数
            self.pool_tree.selection_set(*new_pool_items)

        # 保存交换操作到历史记录
        action_type = (
            f"交换记录: 子网需求表 {len(selected_requirements)} 条记录 ↔ 需求池 {len(selected_pool_items)} 条记录"
        )
        self.save_current_state(action_type)

    def create_split_input_section(self):
        """创建子网切分功能的输入区域"""
        # 创建一个主框架，用于放置输入参数面板和历史记录面板
        input_history_frame = ttk.Frame(self.split_frame)
        input_history_frame.pack(fill=tk.X, expand=False, pady=(0, 8), anchor=tk.W)  # 撑满宽度，上下排列，靠左对齐

        # 创建输入参数面板
        input_frame = ttk.LabelFrame(
            input_history_frame, text="输入参数", padding=(10, 10, 10, 10)
        )  # 单独控制各边内边距：左10, 上5, 右5, 下5
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))  # 靠左放置，垂直填充

        # 配置grid行列，减小间距
        input_frame.grid_columnconfigure(0, minsize=50, weight=0)  # 标签列固定最小宽度
        input_frame.grid_columnconfigure(1, weight=0)  # 文本框列固定宽度，不拉伸
        input_frame.grid_columnconfigure(2, weight=0, minsize=5)  # 文本框和按钮之间的间隔列，减小到5px
        input_frame.grid_columnconfigure(3, weight=0)  # 按钮列固定宽度
        input_frame.grid_columnconfigure(4, weight=0)  # 按钮列固定宽度
        input_frame.grid_columnconfigure(5, weight=1)  # 右侧填充列，确保整个区域靠左对齐

        # 配置行权重和最小高度，4行布局
        input_frame.grid_rowconfigure(0, weight=0, minsize=0)  # 第0行权重0，最小高度0像素
        input_frame.grid_rowconfigure(1, weight=0)  # 第1行权重0，不拉伸
        input_frame.grid_rowconfigure(2, weight=0)  # 第2行权重0，不拉伸
        input_frame.grid_rowconfigure(3, weight=0, minsize=0)  # 第3行权重0，最小高度0像素

        # 父网段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text="父网段", anchor="w", font=("微软雅黑", 10)).grid(
            row=1, column=0, sticky=tk.W + tk.N + tk.S, pady=8, padx=(0, 5)
        )
        # 初始化子网切分的历史记录列表
        self.split_parent_networks = ["10.0.0.0/8"]  # 子网切分的父网段历史记录
        self.split_networks = ["10.21.60.0/23"]  # 子网切分的切分段历史记录

        # 父网段 - 使用Combobox，支持下拉选择和即时验证
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.parent_entry)), '%P')
        self.parent_entry = ttk.Combobox(
            input_frame,
            values=self.split_parent_networks,
            width=22,
            font=("微软雅黑", 10),
            validate='all',
            validatecommand=vcmd,
        )
        self.parent_entry.grid(row=1, column=1, padx=0, pady=8, sticky=tk.W + tk.N + tk.S)
        self.parent_entry.insert(0, "10.0.0.0/8")  # 默认值
        self.parent_entry.config(state="normal")  # 允许手动输入

        # 切分段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text="切分段", anchor="w", font=("微软雅黑", 10)).grid(
            row=2, column=0, sticky=tk.W + tk.N + tk.S, pady=8, padx=(0, 5)
        )
        vcmd = (self.root.register(lambda text: self.validate_cidr(text, self.split_entry)), '%P')
        self.split_entry = ttk.Combobox(
            input_frame,
            values=self.split_networks,
            width=22,
            font=("微软雅黑", 10),
            validate='all',
            validatecommand=vcmd,
        )
        self.split_entry.grid(row=2, column=1, padx=0, pady=8, sticky=tk.W + tk.N + tk.S)
        self.split_entry.insert(0, "10.21.60.0/23")  # 默认值
        self.split_entry.config(state="normal")  # 允许手动输入

        # 按钮区域
        # 执行按钮 - 跨四行的方形样式，使用grid布局
        self.execute_btn = ttk.Button(input_frame, text="执行切分", command=self.execute_split, width=10)
        # 使用grid布局，通过rowspan=4实现跨四行效果，形成方形按钮
        # 将sticky改为NSEW，确保按钮在单元格内居中对齐
        self.execute_btn.grid(row=0, column=3, rowspan=4, padx=(2, 0), pady=0, sticky=tk.NSEW)

        # 创建历史记录面板，与输入参数面板同级
        history_frame = ttk.LabelFrame(input_history_frame, text="历史记录", padding=(10, 5, 10, 5))
        history_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # 靠右放置，填充剩余空间

        # 创建历史记录表格
        self.history_tree = ttk.Treeview(history_frame, columns=('record'), show='', height=4)
        # 添加右键复制功能
        self.bind_treeview_right_click(self.history_tree)

        # 设置列宽
        self.history_tree.column('record', width=180, stretch=True)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.history_tree)

        # 移除内部框架，直接使用grid布局管理组件

        # 配置grid布局，增加一列用于按钮
        history_frame.grid_rowconfigure(0, weight=0)  # 表格行固定高度，正好显示4行
        history_frame.grid_columnconfigure(0, weight=1)  # 表格列可扩展
        history_frame.grid_columnconfigure(1, weight=0)  # 滚动条列不可扩展
        history_frame.grid_columnconfigure(2, weight=0)  # 按钮列不可扩展

        # 添加垂直滚动条
        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def scrollbar_callback(*args):
            # 更新滚动条位置
            history_scroll.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                history_scroll.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                history_scroll.grid()

        self.history_tree.configure(yscrollcommand=scrollbar_callback)

        # 使用grid布局精确控制位置
        self.history_tree.grid(row=0, column=0, sticky=tk.NSEW, pady=5, padx=(0, 2))  # 表格在第0行第0列，占据主要空间
        # 初始隐藏滚动条，只有当内容超过可视区域时才显示
        history_scroll.grid(row=0, column=1, sticky=tk.NS, pady=5)
        scrollbar_callback(0.0, 1.0)

        # 配置更紧凑的按钮样式，减小内部文字间距
        self.style.configure("CompactText.TButton", font=("微软雅黑", 10), padding=(2, 0, 2, 0))  # 减小垂直内边距

        # 创建重新切分按钮，宽度与历史记录表一致
        self.reexecute_btn = ttk.Button(
            history_frame, text="重新切分", command=self.reexecute_split, width=10, style="TButton"
        )
        self.reexecute_btn.grid(row=0, column=2, sticky=tk.NSEW, pady=5, padx=(5, 0))

    def adjust_remaining_tree_width(self):
        """调整剩余网段表表格的宽度，使其自适应窗口大小"""
        # 让表格更新界面
        self.remaining_tree.update_idletasks()

        # 获取剩余网段框架的宽度
        frame_width = self.remaining_frame.winfo_width()

        # 计算每列的宽度
        total_columns = 7
        if frame_width > 0:
            # 为每列分配适当的宽度（减去滚动条和边距）
            column_width = (frame_width - 30) // total_columns  # 30为滚动条和边距留出空间

            # 设置index列宽度（保持固定宽度）
            self.remaining_tree.column("index", width=40)

            # 设置其他列的宽度
            for col in ["cidr", "network", "netmask", "wildcard", "broadcast"]:
                self.remaining_tree.column(col, width=column_width)

            # 调整最后一列的宽度以填充剩余空间
            last_col_width = (frame_width - 30) - (column_width * (total_columns - 2) + 40)
            if last_col_width > 0:
                self.remaining_tree.column("usable", width=last_col_width)
            else:
                self.remaining_tree.column("usable", width=110)

    def on_tab_change(self, tab_index):
        """标签页切换时的处理函数"""
        # 如果切换到剩余网段表标签页（索引为1），触发表格自适应
        if tab_index == 1:
            # 确保界面更新后再调整宽度
            self.remaining_tree.update_idletasks()
            # 调用完整的表格宽度调整方法
            self.adjust_remaining_tree_width()
        # 如果切换到网段分布图标签页（索引为2），触发图表自适应
        elif tab_index == 2:
            # 确保图表Canvas已初始化再绘制
            if hasattr(self, 'chart_canvas'):
                self.draw_distribution_chart()

    def create_top_level_notebook(self):
        """创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块"""
        # 创建一个自定义的笔记本控件来显示不同的功能模块
        self.top_level_notebook = ColoredNotebook(self.main_frame, style=self.style, is_top_level=True)
        self.top_level_notebook.pack(fill=tk.BOTH, expand=True)

        # 子网切分模块 - 使用默认样式以继承主窗体底色
        # 创建子网切分模块主容器
        self.split_frame = ttk.Frame(self.top_level_notebook.content_area, padding="10")

        # 创建子网切分功能的输入区域
        self.create_split_input_section()

        # 创建子网切分功能的结果区域
        self.create_split_result_section()

        # 子网规划模块 - 使用默认样式以继承主窗体底色
        self.planning_frame = ttk.Frame(
            self.top_level_notebook.content_area, padding="10"  # 添加padding，替代main_planning_frame的作用
        )

        # 设置子网规划功能的界面
        self.setup_planning_page()

        # 高级工具模块 - 使用默认样式以继承主窗体底色
        self.advanced_frame = ttk.Frame(self.top_level_notebook.content_area, padding="10")

        # 设置高级工具功能的界面
        self.setup_advanced_tools_page()

        # 添加顶级标签页 - 使用不同颜色
        self.top_level_notebook.add_tab("子网规划", self.planning_frame, "#fce4ec")  # 淡粉色
        self.top_level_notebook.add_tab("子网切分", self.split_frame, "#fff3e0")  # 浅橙色
        self.top_level_notebook.add_tab("高级工具", self.advanced_frame, "#e8f5e9")  # 浅绿色

    def create_split_result_section(self):
        """创建子网切分功能的结果显示区域"""
        result_frame = ttk.LabelFrame(self.split_frame, text="切分结果", padding="10")
        # 调整底部外边距，将结果区域与窗体下边距缩小
        result_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 0))

        # 导出结果按钮 - 使用 place 布局手动控制位置，使用默认TButton样式
        self.export_btn = ttk.Button(result_frame, text="导出结果", command=self.export_result, width=10)
        # 手动指定按钮位置：右上角，距离右边0像素，距离顶部-3像素
        self.export_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 创建一个自定义的笔记本控件来显示不同的结果页面
        self.notebook = ColoredNotebook(result_frame, style=self.style, tab_change_callback=self.on_tab_change)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 将导出结果按钮提升到最上层，避免被遮挡
        self.export_btn.lift()

        # 切分段信息页面
        self.split_info_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_blue_style)

        # 创建切分段信息表格
        self.split_tree = ttk.Treeview(self.split_info_frame, columns=("item", "value"), show="headings", height=5)
        # 添加右键复制功能
        self.bind_treeview_right_click(self.split_tree)
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        # 设置合适的列宽
        self.split_tree.column("item", width=100, minwidth=100, stretch=False)
        self.split_tree.column("value", width=250)
        self.split_tree.pack(fill=tk.BOTH, expand=True, pady=0)

        # 配置斑马条纹样式和信息标签样式
        self.configure_treeview_styles(self.split_tree, include_special_tags=True)

        # 剩余网段表页面
        self.remaining_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_green_style)

        # 创建剩余网段信息表格
        self.remaining_tree = ttk.Treeview(
            self.remaining_frame,
            columns=("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable"),
            show="headings",
            height=5,
        )
        # 添加右键复制功能
        self.bind_treeview_right_click(self.remaining_tree)
        self.remaining_tree.heading("index", text="序号")
        self.remaining_tree.heading("cidr", text="CIDR")
        self.remaining_tree.heading("network", text="网络地址")
        self.remaining_tree.heading("netmask", text="子网掩码")
        self.remaining_tree.heading("wildcard", text="通配符掩码")
        self.remaining_tree.heading("broadcast", text="广播地址")
        self.remaining_tree.heading("usable", text="可用地址数")

        # 设置列宽，使用minwidth替代width，让列可以自适应
        self.remaining_tree.column("index", minwidth=40, width=40, stretch=False, anchor="e")
        self.remaining_tree.column("cidr", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("network", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("netmask", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("wildcard", minwidth=100, width=120, stretch=True)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.remaining_tree)

        # 网段分布图页面
        self.chart_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_purple_style)

        # 添加标签页，每个标签页设置不同的颜色
        self.notebook.add_tab("切分段信息", self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab("剩余网段", self.remaining_frame, "#e8f5e9")  # 浅绿色
        self.notebook.add_tab("网段分布图", self.chart_frame, "#f3e5f5")  # 浅紫色

        # 配置chart_frame的grid布局
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=0)

        # 创建滚动容器，使用grid布局
        scroll_frame = ttk.Frame(self.chart_frame)
        scroll_frame.grid(row=0, column=0, sticky=tk.NSEW)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        # 添加滚动条
        self.chart_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)

        # 创建Canvas用于绘制柱状图，设置背景色为深灰色以匹配图表背景
        # 禁止水平滚动，只允许垂直滚动
        self.chart_canvas = tk.Canvas(scroll_frame, bg="#333333")
        self.chart_canvas.grid(row=0, column=0, sticky=tk.NSEW, pady=0)

        # 配置滚动条
        self.chart_scrollbar.config(command=self.chart_canvas.yview)
        self.chart_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def chart_scrollbar_callback(*args):
            # 更新滚动条位置
            self.chart_scrollbar.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                self.chart_scrollbar.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                self.chart_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 配置Canvas的滚动条命令
        self.chart_canvas.config(yscrollcommand=chart_scrollbar_callback, xscrollcommand=None)

        # 初始检查是否需要显示滚动条
        chart_scrollbar_callback(0.0, 1.0)

        # 绑定窗口大小变化事件，实现图表自适应
        self.chart_canvas.bind("<Configure>", self.on_chart_resize)
        # 绑定鼠标滚轮事件
        self.chart_canvas.bind("<MouseWheel>", self.on_chart_mousewheel)

        # 调整列宽，确保所有列都能完整显示并自适应窗口宽度
        self.remaining_tree.column("broadcast", minwidth=100, width=130, stretch=True)
        self.remaining_tree.column("usable", minwidth=100, width=110, stretch=True)

        # 配置remaining_frame的grid布局
        self.remaining_frame.grid_rowconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(1, weight=0)

        # 添加垂直滚动条
        self.remaining_scroll_v = ttk.Scrollbar(
            self.remaining_frame, orient=tk.VERTICAL, command=self.remaining_tree.yview
        )

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def remaining_scrollbar_callback(*args):
            # 更新滚动条位置
            self.remaining_scroll_v.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                self.remaining_scroll_v.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)

        self.remaining_tree.configure(yscrollcommand=remaining_scrollbar_callback)

        # 设置布局：Treeview在左，垂直滚动条在右，都填满整个可用空间
        self.remaining_tree.grid(row=0, column=0, sticky=tk.NSEW)
        # 初始隐藏滚动条
        self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)
        remaining_scrollbar_callback(0.0, 1.0)

        # 绑定窗口大小变化事件，实现表格自适应
        self.root.bind("<Configure>", self.on_window_resize)

        # 初始提示
        self.clear_result()

        # Treeview表格线样式已在初始化时设置

        # 在窗口完全渲染后再调用动态计算方法，确保获取准确的高度
        self.root.after(100, self.initial_table_setup)

    def _create_result_main_frame(self):
        """创建结果显示区域的主框架"""
        result_frame = ttk.LabelFrame(self.split_frame, text="切分结果", padding="10")
        # 调整底部外边距，将结果区域与窗体下边距缩小
        result_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 0))
        return result_frame

    def _create_export_button(self, parent_frame):
        """添加导出结果按钮"""
        # 导出结果按钮 - 使用 place 布局手动控制位置，使用默认TButton样式
        self.export_btn = ttk.Button(parent_frame, text="导出结果", command=self.export_result, width=10)
        # 手动指定按钮位置：右上角，距离右边0像素，距离顶部-3像素
        self.export_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 将导出结果按钮提升到最上层，避免被遮挡
        self.export_btn.lift()

    def _create_result_notebook(self, parent_frame):
        """创建笔记本控件来显示不同的结果页面"""
        # 创建一个自定义的笔记本控件来显示不同的结果页面
        self.notebook = ColoredNotebook(parent_frame, style=self.style, tab_change_callback=self.on_tab_change)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def _create_split_info_page(self):
        """创建切分段信息页面"""
        # 切分段信息页面
        self.split_info_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_blue_style)

        # 创建切分段信息表格
        self.split_tree = ttk.Treeview(self.split_info_frame, columns=("item", "value"), show="headings", height=5)
        # 添加右键复制功能
        self.bind_treeview_right_click(self.split_tree)
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        # 设置合适的列宽
        self.split_tree.column("item", width=100, minwidth=100, stretch=False)
        self.split_tree.column("value", width=250)
        self.split_tree.pack(fill=tk.BOTH, expand=True, pady=0)

        # 配置斑马条纹样式和信息标签样式
        self.configure_treeview_styles(self.split_tree, include_special_tags=True)

    def _create_remaining_subnets_page(self):
        """创建剩余网段表页面"""
        # 剩余网段表页面
        self.remaining_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_green_style)

        # 创建剩余网段信息表格
        self.remaining_tree = ttk.Treeview(
            self.remaining_frame,
            columns=("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable"),
            show="headings",
            height=5,
        )
        # 添加右键复制功能
        self.bind_treeview_right_click(self.remaining_tree)
        self.remaining_tree.heading("index", text="序号")
        self.remaining_tree.heading("cidr", text="CIDR")
        self.remaining_tree.heading("network", text="网络地址")
        self.remaining_tree.heading("netmask", text="子网掩码")
        self.remaining_tree.heading("wildcard", text="通配符掩码")
        self.remaining_tree.heading("broadcast", text="广播地址")
        self.remaining_tree.heading("usable", text="可用地址数")

        # 设置列宽，使用minwidth替代width，让列可以自适应
        self.remaining_tree.column("index", minwidth=40, width=40, stretch=False, anchor="e")
        self.remaining_tree.column("cidr", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("network", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("netmask", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("wildcard", minwidth=100, width=120, stretch=True)

        # 调整列宽，确保所有列都能完整显示并自适应窗口宽度
        self.remaining_tree.column("broadcast", minwidth=100, width=130, stretch=True)
        self.remaining_tree.column("usable", minwidth=100, width=110, stretch=True)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.remaining_tree)

    def _create_network_chart_page(self):
        """创建网段分布图页面"""
        # 网段分布图页面
        self.chart_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_purple_style()
        )

        # 配置chart_frame的grid布局
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=0)

        # 创建滚动容器，使用grid布局
        scroll_frame = ttk.Frame(self.chart_frame)
        scroll_frame.grid(row=0, column=0, sticky=tk.NSEW)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=0)

        # 添加滚动条
        self.chart_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)

        # 创建Canvas用于绘制柱状图，设置背景色为深灰色以匹配图表背景
        # 禁止水平滚动，只允许垂直滚动
        self.chart_canvas = tk.Canvas(scroll_frame, bg="#333333")
        self.chart_canvas.grid(row=0, column=0, sticky=tk.NSEW, pady=0)

        # 配置滚动条
        self.chart_scrollbar.config(command=self.chart_canvas.yview)
        self.chart_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def chart_scrollbar_callback(*args):
            # 更新滚动条位置
            self.chart_scrollbar.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                self.chart_scrollbar.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                self.chart_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 配置Canvas的滚动条命令
        self.chart_canvas.config(yscrollcommand=chart_scrollbar_callback, xscrollcommand=None)

        # 初始检查是否需要显示滚动条
        chart_scrollbar_callback(0.0, 1.0)

        # 绑定窗口大小变化事件，实现图表自适应
        self.chart_canvas.bind("<Configure>", self.on_chart_resize)
        # 绑定鼠标滚轮事件
        self.chart_canvas.bind("<MouseWheel>", self.on_chart_mousewheel)

    def _add_result_tabs(self):
        """添加标签页到笔记本"""
        # 添加标签页，每个标签页设置不同的颜色
        self.notebook.add_tab("切分段信息", self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab("剩余网段", self.remaining_frame, "#e8f5e9")  # 浅绿色
        self.notebook.add_tab("网段分布图", self.chart_frame, "#f3e5f5")  # 浅紫色

    def _setup_scrollbars(self):
        """配置滚动条"""
        # 配置remaining_frame的grid布局
        self.remaining_frame.grid_rowconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(1, weight=0)

        # 添加垂直滚动条
        self.remaining_scroll_v = ttk.Scrollbar(
            self.remaining_frame, orient=tk.VERTICAL, command=self.remaining_tree.yview
        )

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def remaining_scrollbar_callback(*args):
            # 更新滚动条位置
            self.remaining_scroll_v.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                self.remaining_scroll_v.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)

        self.remaining_tree.configure(yscrollcommand=remaining_scrollbar_callback)

        # 设置布局：Treeview在左，垂直滚动条在右，都填满整个可用空间
        self.remaining_tree.grid(row=0, column=0, sticky=tk.NSEW)
        # 初始隐藏滚动条
        self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)
        remaining_scrollbar_callback(0.0, 1.0)

    def _setup_initial_state(self):
        """设置初始状态"""
        # 绑定窗口大小变化事件，实现表格自适应
        self.root.bind("<Configure>", self.on_window_resize)

        # 初始提示
        self.clear_result()

        # Treeview表格线样式已在初始化时设置

        # 在窗口完全渲染后再调用动态计算方法，确保获取准确的高度
        self.root.after(100, self.initial_table_setup)

    def setup_planning_page(self):
        """设置子网规划功能的界面"""
        # 直接使用self.planning_frame，移除中间层main_planning_frame

        # 设置grid布局
        self.planning_frame.grid_columnconfigure(0, weight=1)  # 左侧列可伸缩
        self.planning_frame.grid_columnconfigure(1, weight=1)  # 右侧列可伸缩
        self.planning_frame.grid_rowconfigure(0, weight=0)  # 父网段设置行，固定高度
        self.planning_frame.grid_rowconfigure(1, weight=0)  # 需求池和子网需求行，固定高度
        self.planning_frame.grid_rowconfigure(2, weight=1)  # 规划结果行，可伸缩

        # 父网段设置区域
        parent_frame = ttk.LabelFrame(self.planning_frame, text="父网段设置", padding=(5, 10, 10, 10))
        parent_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 0))  # 左上角
        # 设置父网段设置面板的固定宽度
        parent_frame.configure(width=250)

        # 初始化父网段列表 - 为子网规划创建独立的历史记录列表
        self.planning_parent_networks = ["10.21.48.0/20"]  # 默认父网段

        # 父网段下拉文本框
        ttk.Label(parent_frame, text="").pack(side=tk.LEFT, padx=(0, 0))
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.planning_parent_entry)), '%P')
        self.planning_parent_entry = ttk.Combobox(
            parent_frame,
            values=self.planning_parent_networks,
            width=16,
            font=("微软雅黑", 10),
            validate='all',
            validatecommand=vcmd,
        )
        self.planning_parent_entry.pack(side=tk.LEFT, padx=(0, 0), fill=tk.X, expand=True)
        self.planning_parent_entry.insert(0, "10.21.48.0/20")  # 默认值
        self.planning_parent_entry.config(state="normal")  # 允许手动输入

        # 需求池区域
        history_frame = ttk.LabelFrame(self.planning_frame, text="需求池", padding=(10, 10, 0, 10))
        history_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))  # 左下角
        # 设置需求池面板的固定宽度
        history_frame.configure(width=250)

        # 子网需求区域
        requirements_frame = ttk.LabelFrame(self.planning_frame, text="子网需求", padding=(10, 10, 0, 10))
        requirements_frame.grid(
            row=0, column=1, rowspan=2, sticky="nsew", padx=(5, 0), pady=(0, 10)
        )  # 右侧跨两行
        # 设置子网需求面板的固定宽度
        requirements_frame.configure(width=250)

        # 内部容器框架，用于组织表格和按钮
        inner_frame = ttk.Frame(requirements_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # 设置grid布局
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=0)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_columnconfigure(1, weight=0)

        # 创建需求池表格，结构与子网需求表相同
        self.pool_tree = ttk.Treeview(history_frame, columns=("index", "name", "hosts"), show="headings", height=6)
        # 添加右键复制功能
        self.bind_treeview_right_click(self.pool_tree)
        self.pool_tree.heading("index", text="序号")
        self.pool_tree.heading("name", text="子网名称")
        self.pool_tree.heading("hosts", text="主机数量")

        # 设置列宽，与子网需求表保持一致
        self.pool_tree.column("index", width=40, minwidth=20, stretch=False, anchor="e")
        self.pool_tree.column("name", width=80, minwidth=80, stretch=True)  # 减小初始宽度，允许伸缩
        self.pool_tree.column("hosts", width=80, minwidth=40, stretch=False)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.pool_tree)

        # 绑定双击事件以实现编辑功能
        self.pool_tree.bind("<Double-1>", self.on_pool_tree_double_click)
        # 绑定左键单击事件以实现取消选择功能
        self.pool_tree.bind("<Button-1>", self.on_treeview_click)


        # 添加滚动条，确保只作用于表格，位于表格右侧
        self.pool_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)

        # 使用通用方法创建带自动隐藏滚动条的Treeview
        # self.create_scrollable_treeview(history_frame, self.pool_tree, self.pool_scrollbar)

        # 直接创建Treeview和滚动条，不使用自动隐藏功能
        self.pool_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.pool_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.pool_scrollbar.config(command=self.pool_tree.yview)
        self.pool_tree.config(yscrollcommand=self.pool_scrollbar.set)

        # 移除双击事件绑定，用户不能直接选择历史记录，只能通过撤销/重做操作
        # self.planning_history_tree.bind("<Double-1>", self.reexecute_planning_from_history)

        # 设置grid布局
        inner_frame.grid_rowconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(0, weight=0)  # 按钮列，固定宽度
        inner_frame.grid_columnconfigure(1, weight=1)  # 表格列，可伸缩
        inner_frame.grid_columnconfigure(2, weight=0)  # 滚动条列，固定宽度

        # 子网需求操作按钮框架
        button_frame = ttk.Frame(inner_frame)
        button_frame.grid(row=0, column=0, sticky="nsew")
        # 设置按钮框架的最小宽度，确保两个按钮大小一致
        button_frame.configure(width=70)

        # 子网需求表格
        self.requirements_tree = ttk.Treeview(
            inner_frame, columns=("index", "name", "hosts"), show="headings", height=5  # 设置为5行高度，添加序号列
        )
        # 添加右键复制功能
        self.bind_treeview_right_click(self.requirements_tree)
        self.requirements_tree.heading("index", text="序号")
        self.requirements_tree.heading("name", text="子网名称")
        self.requirements_tree.heading("hosts", text="主机数量")
        # 字段宽度设置
        self.requirements_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")
        self.requirements_tree.column("name", width=80, minwidth=80, stretch=True)  # 减小初始宽度，允许伸缩
        self.requirements_tree.column("hosts", width=80, minwidth=80, stretch=False)

        # 绑定双击事件以实现编辑功能
        self.requirements_tree.bind("<Double-1>", self.on_requirements_tree_double_click)
        # 绑定左键单击事件以实现取消选择功能
        self.requirements_tree.bind("<Button-1>", self.on_treeview_click)


        # 放置表格
        self.requirements_tree.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # 添加滚动条，确保只作用于表格，位于表格右侧
        self.requirements_scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL)

        # 使用通用方法创建带自动隐藏滚动条的Treeview
        # self.create_scrollable_treeview_with_grid(
        #     inner_frame, self.requirements_tree, self.requirements_scrollbar, 
        #     tree_row=0, tree_column=1, scrollbar_row=0, scrollbar_column=2,
        #     tree_padx=(10, 0), scrollbar_padx=(0, 0)
        # )

        # 直接创建Treeview和滚动条，不使用自动隐藏功能
        self.requirements_tree.grid(row=0, column=1, sticky=tk.NSEW)
        self.requirements_scrollbar.grid(row=0, column=2, sticky=tk.NS)
        self.requirements_scrollbar.config(command=self.requirements_tree.yview)
        self.requirements_tree.config(yscrollcommand=self.requirements_scrollbar.set)

        # 允许同时选择两张表中的记录，移除选择事件绑定

        # 按钮框架内部布局 - 按照用户要求设置行权重
        button_frame.grid_rowconfigure(0, weight=0)  # 添加按钮
        button_frame.grid_rowconfigure(1, weight=0)  # 删除按钮
        button_frame.grid_rowconfigure(2, weight=0)  # 撤销按钮
        button_frame.grid_rowconfigure(3, weight=0)  # 导入按钮
        button_frame.grid_rowconfigure(4, weight=1)  # 空白区域，将底部按钮推到底部
        button_frame.grid_rowconfigure(5, weight=0)  # 空白行，保持原有结构
        button_frame.grid_rowconfigure(6, weight=0)  # 交换记录按钮
        button_frame.grid_columnconfigure(0, weight=1)

        # 添加按钮
        add_btn = ttk.Button(button_frame, text="添加", command=self.add_subnet_requirement, width=7)
        add_btn.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # 删除按钮
        delete_btn = ttk.Button(button_frame, text="删除", command=self.delete_subnet_requirement, width=7)
        delete_btn.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        # 撤销按钮
        self.undo_delete_btn = ttk.Button(button_frame, text="撤销", command=self.undo_delete, width=7)
        self.undo_delete_btn.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # 移动/交换按钮（根据选中情况自动判断操作）
        # 交换记录按钮 - 使用交换图标
        self.swap_btn = ttk.Button(button_frame, text="↔", command=self.move_records, width=7)
        self.swap_btn.grid(row=3, column=0, sticky="ew", pady=(0, 5))

        # 导入按钮
        import_btn = ttk.Button(button_frame, text="导入", command=self.import_requirements, width=7)
        import_btn.grid(row=6, column=0, sticky="ew", pady=(0, 0))

        # 规划子网按钮已移动到规划结果区域，此处不再显示

        # 添加示例数据 - 带斑马条纹标签
        requirements_data = [
            ("办公室", "20"),
            ("人事部", "10"),
            ("财务部", "10"),
            ("规划部", "30"),
            ("法务部", "10"),
            ("采购部", "10"),
            ("安管办", "10"),
            ("党群部", "20"),
            ("纪委办", "10"),
            ("信息部", "20"),
            ("工程部", "20"),
            ("销售部", "20"),
            ("研发部", "15"),
            ("生产部", "100"),
            ("运输部", "20"),
        ]
        for index, (name, hosts) in enumerate(requirements_data, 1):
            tag = "even" if index % 2 == 0 else "odd"
            self.requirements_tree.insert("", tk.END, values=("", name, hosts), tags=(tag,))

        # 调用方法更新序号
        self.update_requirements_tree_zebra_stripes()

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.requirements_tree)
        self.configure_treeview_styles(self.pool_tree)  # 配置需求池表格样式

        # 设置表格选择模式为多选，允许一次选择多条记录
        self.requirements_tree.configure(selectmode=tk.EXTENDED)
        self.pool_tree.configure(selectmode=tk.EXTENDED)

        # 删除原来的执行规划按钮容器
        # 按钮已移动到删除按钮下方

        # 规划结果区域 - 使用grid布局，跨两列显示
        result_frame = ttk.LabelFrame(self.planning_frame, text="规划结果", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky="nwse", pady=(0, 0))

        # 创建笔记本控件显示规划结果
        self.planning_notebook = ColoredNotebook(result_frame, style=self.style)
        self.planning_notebook.pack(fill=tk.BOTH, expand=True)

        # 设置统一的按钮宽度，使用合适的宽度确保文字完全显示
        button_width = 10

        # 导出规划按钮 - 使用 place 布局手动控制位置，使用默认TButton样式
        export_planning_btn = ttk.Button(
            result_frame, text="导出规划", command=self.export_planning_result, width=button_width
        )
        # 手动指定按钮位置：右上角，距离右边0像素，距离顶部-3像素
        export_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 创建醒目的按钮样式，使用更深的蓝色系，确保文字清晰显示
        self.style.configure(
            "Accent.TButton",
            background="#1565c0",  # 深蓝色，确保白色文字清晰显示
            foreground="white",  # 白色文字
            font=("微软雅黑", 10, "bold"),
            padding=6,
        )

        # 配置蓝色按钮的鼠标悬停效果
        self.style.map(
            "Accent.TButton",
            background=[
                ("active", "#0d47a1"),  # 鼠标悬停时使用更深的蓝色
                ("!active", "#1565c0"),  # 正常状态
                ("pressed", "#0d47a1"),
            ],  # 按下状态
            foreground=[("active", "white"), ("!active", "white"), ("pressed", "white")],
        )

        # 创建醒目的按钮样式，使用更深的绿色系，确保文字清晰显示
        self.style.configure(
            "RedAccent.TButton",
            background="#2e7d32",  # 深绿色，确保白色文字清晰显示
            foreground="white",  # 白色文字
            font=("微软雅黑", 10, "bold"),
            padding=6,
        )

        # 配置绿色按钮的鼠标悬停效果
        self.style.map(
            "RedAccent.TButton",
            background=[
                ("active", "#1b5e20"),  # 鼠标悬停时使用更深的绿色
                ("!active", "#2e7d32"),  # 正常状态
                ("pressed", "#1b5e20"),
            ],  # 按下状态
            foreground=[("active", "white"), ("!active", "white"), ("pressed", "white")],
        )

        # 规划子网按钮 - 使用 place 布局，位于导出规划按钮左方，大小相同，使用默认TButton样式
        self.execute_planning_btn = ttk.Button(
            result_frame, text="规划子网", command=self.execute_subnet_planning, width=button_width
        )
        # 动态计算规划子网按钮的位置：导出规划按钮左边，间隔10像素
        button_gap = 10
        # 先更新窗口，确保能获取到导出规划按钮的实际宽度
        self.root.update_idletasks()
        export_btn_width = export_planning_btn.winfo_reqwidth()
        execute_btn_x = -export_btn_width - button_gap

        # 使用动态计算的位置放置规划子网按钮
        self.execute_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=execute_btn_x, y=-3)

        # 已分配子网页面
        self.allocated_frame = ttk.Frame(
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.light_blue_style
        )
        self.allocated_tree = ttk.Treeview(
            self.allocated_frame,
            columns=("index", "name", "cidr", "required", "available", "network", "netmask", "broadcast"),
            show="headings",
            height=5,  # 设置为5行高度
        )

        # 添加右键复制功能
        self.bind_treeview_right_click(self.allocated_tree)

        # 设置列标题
        self.allocated_tree.heading("index", text="序号")
        self.allocated_tree.heading("name", text="子网名称")
        self.allocated_tree.heading("cidr", text="CIDR")
        self.allocated_tree.heading("required", text="需求数")
        self.allocated_tree.heading("available", text="可用数")
        self.allocated_tree.heading("network", text="网络地址")
        self.allocated_tree.heading("netmask", text="子网掩码")
        self.allocated_tree.heading("broadcast", text="广播地址")

        # 设置列宽为自动，根据内容自动调整宽度
        self.allocated_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")  # 序号列固定宽度40
        self.allocated_tree.column("name", width=0, minwidth=100, stretch=True)  # 子网名称列自动宽度
        self.allocated_tree.column("cidr", width=0, minwidth=90, stretch=True)  # CIDR列自动宽度
        self.allocated_tree.column("required", width=0, minwidth=30, stretch=True)  # 需求数列自动宽度
        self.allocated_tree.column("available", width=0, minwidth=40, stretch=True)  # 可用数列自动宽度
        self.allocated_tree.column("network", width=0, minwidth=70, stretch=True)  # 网络地址列自动宽度
        self.allocated_tree.column("netmask", width=0, minwidth=100, stretch=True)  # 子网掩码列自动宽度
        self.allocated_tree.column("broadcast", width=0, minwidth=100, stretch=True)  # 广播地址列自动宽度

        # 添加垂直滚动条
        allocated_v_scrollbar = ttk.Scrollbar(
            self.allocated_frame, orient=tk.VERTICAL, command=self.allocated_tree.yview
        )

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def allocated_scrollbar_callback(*args):
            # 更新滚动条位置
            allocated_v_scrollbar.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                allocated_v_scrollbar.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                allocated_v_scrollbar.grid()

        # 配置表格使用滚动条（仅垂直）
        self.allocated_tree.configure(yscrollcommand=allocated_scrollbar_callback)

        # 重新布局表格和滚动条，使用grid布局实现自适应
        self.allocated_frame.grid_rowconfigure(0, weight=1)
        self.allocated_frame.grid_columnconfigure(0, weight=1)

        self.allocated_tree.grid(row=0, column=0, sticky="nsew")
        allocated_v_scrollbar.grid(row=0, column=1, sticky="ns")
        allocated_scrollbar_callback(0.0, 1.0)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.allocated_tree)

        # 剩余网段页面
        self.planning_remaining_frame = ttk.Frame(
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.light_green_style
        )
        self.planning_remaining_tree = ttk.Treeview(
            self.planning_remaining_frame,
            columns=("index", "cidr", "network", "netmask", "broadcast", "usable"),
            show="headings",
            height=5,  # 设置为5行高度
        )

        # 添加右键复制功能
        self.bind_treeview_right_click(self.planning_remaining_tree)

        # 设置列标题
        self.planning_remaining_tree.heading("index", text="序号")
        self.planning_remaining_tree.heading("cidr", text="CIDR")
        self.planning_remaining_tree.heading("network", text="网络地址")
        self.planning_remaining_tree.heading("netmask", text="子网掩码")
        self.planning_remaining_tree.heading("broadcast", text="广播地址")
        self.planning_remaining_tree.heading("usable", text="可用地址数")

        # 设置列宽，所有列都启用拉伸以实现自适应
        self.planning_remaining_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")
        self.planning_remaining_tree.column("cidr", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column(
            "network", width=80, minwidth=70, stretch=True
        )  # 调小网络地址列宽并启用拉伸
        self.planning_remaining_tree.column("netmask", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("broadcast", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("usable", width=80, minwidth=60, stretch=True)

        # 添加垂直滚动条
        remaining_v_scrollbar = ttk.Scrollbar(
            self.planning_remaining_frame,
            orient=tk.VERTICAL,
            command=self.planning_remaining_tree.yview,
        )

        # 创建自定义滚动条回调函数，实现滚动条按需显示
        def planning_remaining_scrollbar_callback(*args):
            # 更新滚动条位置
            remaining_v_scrollbar.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                remaining_v_scrollbar.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                remaining_v_scrollbar.grid()

        # 配置表格使用滚动条（仅垂直）
        self.planning_remaining_tree.configure(yscrollcommand=planning_remaining_scrollbar_callback)

        # 重新布局表格和滚动条，使用grid布局实现自适应
        self.planning_remaining_frame.grid_rowconfigure(0, weight=1)
        self.planning_remaining_frame.grid_columnconfigure(0, weight=1)

        self.planning_remaining_tree.grid(row=0, column=0, sticky="nsew")
        remaining_v_scrollbar.grid(row=0, column=1, sticky="ns")
        planning_remaining_scrollbar_callback(0.0, 1.0)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.planning_remaining_tree)

        # 添加标签页 - 使用与切分结果一致的颜色
        self.planning_notebook.add_tab("已分配子网", self.allocated_frame, "#e3f2fd")  # 浅蓝色
        self.planning_notebook.add_tab("剩余网段", self.planning_remaining_frame, "#e8f5e9")  # 浅绿色

        # 添加窗口大小变化事件处理，确保表格能自适应宽度
        self.planning_notebook.content_area.bind('<Configure>', lambda e: self.resize_tables())

        # 为规划模块表格添加空行或示例数据，显示斑马条纹效果
        # 子网需求表格 - 保留示例数据，确保有数据
        # 已分配子网表格 - 初始化时不添加空行
        for item in self.allocated_tree.get_children():
            self.allocated_tree.delete(item)
        # 删除了初始化时添加10行空行的代码

        # 规划剩余网段表格 - 初始化时不添加空行
        for item in self.planning_remaining_tree.get_children():
            self.planning_remaining_tree.delete(item)
        # 删除了初始化时添加10行空行的代码

    def initial_table_setup(self):
        """在窗口完全渲染后初始化表格"""
        try:
            # 更新表格的斑马条纹样式
            if hasattr(self, 'split_tree'):
                self.update_table_zebra_stripes(self.split_tree)
            if hasattr(self, 'remaining_tree'):
                self.update_table_zebra_stripes(self.remaining_tree)
            if hasattr(self, 'allocated_tree'):
                self.update_table_zebra_stripes(self.allocated_tree)
            if hasattr(self, 'planning_remaining_tree'):
                self.update_table_zebra_stripes(self.planning_remaining_tree)
        except (tk.TclError, AttributeError):
            pass

    def configure_treeview_styles(self, tree, include_special_tags=False):
        """配置Treeview控件的基本样式（斑马条纹、错误和信息标签）

        Args:
            tree: 要配置的Treeview对象
            include_special_tags: 是否包含错误和信息标签配置
        """
        try:
            tree.tag_configure("even", background="#d8d8d8")
            tree.tag_configure("odd", background="#ffffff")

            tree.tag_configure("section", background="#d8d8d8", foreground="#000000")

            tree.tag_configure("current", font=tree.cget("font") + ("bold",), foreground="#0066cc")

            if include_special_tags:
                tree.tag_configure("error", foreground="red")
                tree.tag_configure("info", foreground="blue")
        except (tk.TclError, AttributeError):
            pass

    def update_table_zebra_stripes(self, tree, update_index=False):
        """更新表格的斑马条纹标签

        Args:
            tree: 要处理的Treeview对象
            update_index: 是否更新序号列（适用于包含序号的表格）
        """
        try:
            # 只更新行标签，样式已在初始化时配置
            children = tree.get_children()
            for index, item in enumerate(children, start=1):
                tag = "even" if index % 2 == 0 else "odd"

                if update_index:
                    # 更新序号列
                    values = list(tree.item(item, "values"))
                    if values and values[0] != index:  # 只有当序号不一致时才更新
                        values[0] = index
                        tree.item(item, values=values, tags=(tag,))
                    else:
                        # 只更新斑马条纹标签，减少不必要的UI更新
                        current_tags = tree.item(item, "tags")
                        if tag not in current_tags:
                            tree.item(item, tags=(tag,))
                else:
                    # 只更新斑马条纹标签
                    current_tags = tree.item(item, "tags")
                    if tag not in current_tags:  # 只有当标签不一致时才更新
                        tree.item(item, tags=(tag,))
        except AttributeError:
            # 忽略属性不存在的错误
            pass
        except (tk.TclError, TypeError):
            # 忽略Tcl和类型错误，不影响程序运行
            pass

    def auto_resize_columns(self, tree):
        """自动调整表格列宽以适应内容

        Args:
            tree: 要调整列宽的Treeview对象
        """

        # 为每列设置一个合理的默认最小宽度（基于列类型）
        default_min_widths = {
            '序号': 60,
            '子网名称': 120,
            'CIDR': 80,
            '需求数': 70,
            '可用数': 70,
            '网络地址': 100,
            '子网掩码': 100,
            '广播地址': 100,
            '起始IP': 100,
            '结束IP': 100,
            '剩余可用数': 100,
            '网段': 120,
            '大小': 80,
        }

        # 调整列宽以适应表头
        for col in tree['columns']:
            # 获取表头文本
            header = tree.heading(col, 'text') or ''  # 确保header不是None

            # 跳过序号列，保持固定宽度6
            if header == '序号' or col == 'index':
                continue

            # 设置临时标签文本并测量宽度
            self._temp_label.config(text=header)
            header_width = self._temp_label.winfo_reqwidth() + 20  # 增加一些边距

            # 获取列中内容的最大宽度
            max_width = header_width
            for item in tree.get_children():
                value = tree.item(item, 'values')
                if value and len(value) > list(tree['columns']).index(col):
                    cell_value = str(value[list(tree['columns']).index(col)])
                    # 设置临时标签文本并测量宽度
                    self._temp_label.config(text=cell_value)
                    cell_width = self._temp_label.winfo_reqwidth() + 20  # 增加一些边距
                    # 确保cell_width和max_width都是有效的数值
                    max_width = max(max_width, cell_width)

            # 应用默认最小宽度，如果计算出的宽度小于默认值
            if header in default_min_widths and max_width < default_min_widths[header]:
                max_width = default_min_widths[header]

            # 设置列宽
            tree.column(col, width=max_width, stretch=True)

    def resize_tables(self):
        """调整表格列宽以适应容器大小并更新空行数"""
        try:
            # 动态更新所有表格的空行数
            tree_names = ['split_tree', 'remaining_tree', 'allocated_tree', 'planning_remaining_tree']
            for tree_name in tree_names:
                if hasattr(self, tree_name):
                    self.update_table_zebra_stripes(getattr(self, tree_name))

            # 仅调整规划结果区域的表格列宽，不影响子网需求区域
            if hasattr(self, 'planning_notebook') and hasattr(self.planning_notebook, 'content_area'):
                # 调整已分配子网表格，根据内容自动调整列宽
                if hasattr(self, 'allocated_tree'):
                    self.auto_resize_columns(self.allocated_tree)

                # 调整剩余网段表格，根据内容自动调整列宽
                if hasattr(self, 'planning_remaining_tree'):
                    self.auto_resize_columns(self.planning_remaining_tree)
        except AttributeError:
            # 忽略属性不存在的错误
            pass
        except ValueError:
            # 忽略值错误
            pass
        except (tk.TclError, TypeError):
            # 忽略Tcl和类型错误
            pass

    def add_subnet_requirement(self):
        """添加子网需求"""
        # 创建临时窗口
        temp_window = tk.Toplevel(self.root)
        temp_window.title("添加子网需求")
        temp_window.resizable(False, False)
        temp_window.transient(self.root)
        temp_window.grab_set()

        # 先隐藏对话框，避免定位过程中的闪现
        temp_window.withdraw()

        # 计算居中位置并设置对话框的尺寸和位置
        window_width = 320
        window_height = 220
        self.center_window(temp_window, window_width, window_height)

        # 显示对话框
        temp_window.deiconify()

        # 创建主内容框架，设置合适的内边距
        main_frame = ttk.Frame(temp_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 设置主框架的列权重，使用3列布局，中间列放表单内容，左右列留白用于居中
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=0)
        main_frame.columnconfigure(3, weight=1)

        # 子网名称 - 标签在中间列左侧，输入框在中间列右侧
        ttk.Label(main_frame, text="子网名称:").grid(row=0, column=1, sticky=tk.E, pady=15, padx=(10, 10))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=2, sticky=tk.W, pady=15, padx=(0, 10))
        # 自动获得焦点，方便直接输入
        name_entry.focus_set()
        
        # 为子网名称添加验证
        def validate_name(text):
            is_valid = bool(text.strip())
            name_entry.config(foreground='black' if is_valid else 'red')
            return "1"  # 始终允许输入，只做视觉提示
        name_entry.config(validate="all", validatecommand=(temp_window.register(validate_name), "%P"))

        # 主机数量 - 标签在中间列左侧，输入框在中间列右侧
        ttk.Label(main_frame, text="主机数量:").grid(row=1, column=1, sticky=tk.E, pady=15, padx=(10, 10))
        hosts_var = tk.StringVar()
        hosts_entry = ttk.Entry(main_frame, textvariable=hosts_var, width=20)
        hosts_entry.grid(row=1, column=2, sticky=tk.W, pady=15, padx=(0, 10))
        
        # 为主机数量添加验证
        def validate_hosts(text):
            # 允许空输入，只验证非空时是否为正整数
            if not text:
                hosts_entry.config(foreground='black')
                return "1"
            is_valid = text.isdigit() and int(text) > 0
            hosts_entry.config(foreground='black' if is_valid else 'red')
            return "1"  # 始终允许输入，只做视觉提示
        hosts_entry.config(validate="all", validatecommand=(temp_window.register(validate_hosts), "%P"))

        # 定义回车键事件处理函数
        def on_return_key(_event):
            save_requirement()

        # 只在窗口创建时绑定一次回车键事件
        temp_window.bind("<Return>", on_return_key)

        # 按钮框架 - 横跨所有列，确保按钮组居中
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=20)

        def save_requirement(target_table="requirements"):
            """保存子网需求

            Args:
                target_table: 目标表，"requirements"表示子网需求表，"pool"表示需求池表
            """
            # 解绑回车键事件，防止错误对话框显示时重复触发

            name = name_var.get().strip()
            hosts = hosts_var.get().strip()

            if not name:
                self.show_error("错误", "请输入子网名称")
                return

            if not hosts.isdigit() or int(hosts) <= 0:
                self.show_error("错误", "请输入有效的主机数量")
                return

            # 检查是否存在相同名称的子网，同时检查子网需求表和需求池表
            # 检查子网需求表
            for item in self.requirements_tree.get_children():
                values = self.requirements_tree.item(item, "values")
                existing_name = values[1]  # 子网名称在第二列
                if existing_name == name:
                    self.show_error("错误", f"已经存在名称为 '{name}' 的子网，请使用其他名称")
                    return

            # 检查需求池表
            for item in self.pool_tree.get_children():
                values = self.pool_tree.item(item, "values")
                existing_name = values[1]  # 子网名称在第二列
                if existing_name == name:
                    self.show_error("错误", f"已经存在名称为 '{name}' 的子网，请使用其他名称")
                    return

            if target_table == "requirements":
                # 添加到子网需求表 - 带斑马条纹标签
                # 获取当前表格中的行数，计算新行的索引（从1开始）
                current_rows = len(self.requirements_tree.get_children())
                new_index = current_rows + 1
                tag = "even" if new_index % 2 == 0 else "odd"
                self.requirements_tree.insert("", tk.END, values=(new_index, name, hosts), tags=(tag,))

                # 重新应用所有行的斑马条纹，确保一致性
                self.update_requirements_tree_zebra_stripes()
            else:
                # 添加到需求池表 - 带斑马条纹标签
                # 获取当前表格中的行数，计算新行的索引（从1开始）
                current_rows = len(self.pool_tree.get_children())
                new_index = current_rows + 1
                tag = "even" if new_index % 2 == 0 else "odd"
                self.pool_tree.insert("", tk.END, values=(new_index, name, hosts), tags=(tag,))

                # 重新应用所有行的斑马条纹，确保一致性
                self.update_pool_tree_zebra_stripes()

            # 保存当前状态到操作记录，包含添加的子网信息
            self.save_current_state(f"添加子网: {name}({hosts})")

            temp_window.destroy()

        # 创建按钮并在按钮框架中居中
        save_requirement_btn = ttk.Button(
            button_frame, text="保存需求", command=lambda: save_requirement("requirements"), width=10
        )
        save_to_pool_btn = ttk.Button(button_frame, text="暂存到池", command=lambda: save_requirement("pool"), width=10)

        # 使用pack布局让按钮在按钮框架中居中显示
        save_requirement_btn.pack(side=tk.LEFT, padx=(0, 10))
        save_to_pool_btn.pack(side=tk.LEFT)

        # 绑定Esc键关闭对话框
        temp_window.bind("<Escape>", lambda event: temp_window.destroy())

    def center_window(self, window, width, height):
        """将窗口居中显示在主窗口中

        Args:
            window: 要居中的窗口对象
            width: 窗口宽度
            height: 窗口高度
        """
        # 获取主窗口的位置和尺寸
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # 计算对话框的居中位置（不包含主窗口标题栏）
        title_bar_height = 30  # 通常标题栏高度约为30像素
        dialog_x = root_x + (root_width - width) // 2
        dialog_y = root_y + title_bar_height + (root_height - title_bar_height - height) // 2

        # 一次性设置对话框的尺寸和位置
        window.geometry(f"{width}x{height}+{dialog_x}+{dialog_y}")

    def delete_subnet_requirement(self):
        """删除选中的子网需求或需求池记录，并重新应用斑马条纹"""
        # 检查两个表格中是否有选中的记录
        selected_requirements = self.requirements_tree.selection()
        selected_pool_items = self.pool_tree.selection()

        if not selected_requirements and not selected_pool_items:
            self.show_warning("提示", "请先选择要删除的记录")
            return

        # 显示自定义的居中确认对话框
        confirm = self.show_custom_confirm("确认删除", "确定要删除选中的记录吗？此操作可以通过撤销按钮恢复。")
        if not confirm:
            return

        # 收集要删除的子网信息和详细记录
        deleted_subnets = []
        deleted_records = []

        # 删除子网需求表中的选中记录
        for item in selected_requirements:
            values = self.requirements_tree.item(item, "values")
            deleted_subnets.append(f"{values[1]}({values[2]})")
            # 保存详细记录，包括表格类型和记录数据
            deleted_records.append({"tree": "requirements", "values": tuple(values), "item": item})
            self.requirements_tree.delete(item)

        # 删除需求池表中的选中记录
        for item in selected_pool_items:
            values = self.pool_tree.item(item, "values")
            deleted_subnets.append(f"{values[1]}({values[2]})")
            # 保存详细记录，包括表格类型和记录数据
            deleted_records.append({"tree": "pool", "values": tuple(values), "item": item})
            self.pool_tree.delete(item)

        # 保存删除记录到历史列表，支持多次撤销
        if deleted_records:
            self.deleted_history.append(deleted_records)

        # 删除后重新应用斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()

        # 保存当前状态到操作记录，包含删除的子网信息
        if deleted_subnets:
            action_type = f"删除子网: {', '.join(deleted_subnets)}"
        else:
            action_type = "删除子网"
        self.save_current_state(action_type)

    def update_requirements_tree_zebra_stripes(self):
        """更新子网需求表的斑马条纹和序号"""
        self.update_table_zebra_stripes(self.requirements_tree, update_index=True)

    def update_pool_tree_zebra_stripes(self):
        """更新需求池表的斑马条纹和序号"""
        self.update_table_zebra_stripes(self.pool_tree, update_index=True)

    def import_requirements(self):
        """导入子网需求数据"""
        self._import_data()

    def _import_data(self):
        """导入数据的主方法"""
        # 显示导入选项对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("导入数据")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 先隐藏对话框，避免定位过程中的闪现
        dialog.withdraw()

        # 计算居中位置，增加高度确保取消按钮能完整显示
        window_width = 350
        window_height = 270
        self.center_window(dialog, window_width, window_height)

        # 显示对话框
        dialog.deiconify()

        # 创建主内容框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 说明文本
        info_text = "请选择导入方式："
        ttk.Label(main_frame, text=info_text, font=('微软雅黑', 10)).pack(pady=(0, 15))

        # 按钮框架 - 纵向排列，居中放置
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=0)

        # 导入文件按钮
        import_file_btn = ttk.Button(button_frame, text="从文件导入", 
                                    command=lambda: self._import_from_file(dialog),
                                    width=18)
        import_file_btn.pack(pady=15)

        # 下载Excel模板按钮
        download_excel_btn = ttk.Button(
            button_frame,
            text="下载Excel模板",
            command=lambda: self._generate_template("excel"),
            width=18
        )
        download_excel_btn.pack(pady=0)

        # 下载CSV模板按钮
        download_csv_btn = ttk.Button(
            button_frame,
            text="下载CSV模板",
            command=lambda: self._generate_template("csv"),
            width=18
        )
        download_csv_btn.pack(pady=5)

        # 取消按钮 - 直接放在主框架中，使用pack布局
        cancel_btn = ttk.Button(main_frame, text="取消", command=dialog.destroy, width=10)
        cancel_btn.pack(pady=(20, 10), side=tk.RIGHT, padx=10)

    def _import_from_file(self, parent_dialog):
        """从文件导入数据

        Args:
            parent_dialog: 父对话框
        """
        parent_dialog.destroy()

        # 选择文件
        file_path = filedialog.askopenfilename(
            title="选择要导入的文件",
            filetypes=[
                ("Excel文件", "*.xlsx"),
                ("CSV文件", "*.csv"),
            ],
            initialdir=""
        )

        if not file_path:
            return

        # 解析文件
        try:
            data_list = self._parse_import_file(file_path)
        except Exception as e:
            self.show_error("错误", f"文件解析失败: {str(e)}")
            return

        if not data_list:
            self.show_info("提示", "文件中没有找到有效数据")
            return

        # 验证数据（包含重复性检查）
        errors = self._validate_import_data(data_list)

        # 显示验证结果对话框
        self._show_import_result(errors, data_list)

    def _parse_import_file(self, file_path):
        """解析导入文件

        Args:
            file_path: 文件路径

        Returns:
            list: 解析后的数据列表，每个元素是包含"name"和"hosts"的字典
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        data_list = []

        if file_ext == ".xlsx":
            # Excel文件解析
            from openpyxl import load_workbook
            wb = load_workbook(file_path, read_only=True)
            ws = wb.active

            # 跳过表头，从第二行开始读取
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                if row and len(row) >= 2:
                    name = str(row[0]).strip() if row[0] else ""
                    hosts = str(row[1]).strip() if row[1] else ""
                    if name and hosts:
                        data_list.append({"name": name, "hosts": hosts, "row": row_idx})

            wb.close()

        elif file_ext == ".csv":
            # CSV文件解析，尝试多种编码
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
            csv_data = None

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, newline='') as f:
                        csv_data = list(csv.reader(f))
                    break
                except UnicodeDecodeError:
                    continue

            if csv_data is None:
                raise Exception("无法识别文件编码，请确保文件使用UTF-8或GBK编码")

            # 跳过表头，从第二行开始读取
            for row_idx, row in enumerate(csv_data[1:], start=2):
                if row and len(row) >= 2:
                    name = str(row[0]).strip() if row[0] else ""
                    hosts = str(row[1]).strip() if row[1] else ""
                    if name and hosts:
                        data_list.append({"name": name, "hosts": hosts, "row": row_idx})

        else:
            raise Exception("不支持的文件格式，请使用Excel (.xlsx) 或CSV (.csv) 文件")

        return data_list

    def _validate_import_data(self, data_list):
        """验证导入数据

        Args:
            data_list: 数据列表

        Returns:
            list: 错误列表，每个元素是包含"row"、"name"、"hosts"、"error"的字典
        """
        errors = []

        # 获取现有数据名称（同时检查子网需求表和需求池表）
        existing_names = set()

        # 检查子网需求表
        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item, "values")
            existing_names.add(values[1])

        # 检查需求池表
        for item in self.pool_tree.get_children():
            values = self.pool_tree.item(item, "values")
            existing_names.add(values[1])

        # 验证每条数据
        for idx, data in enumerate(data_list):
            row = data.get("row", idx + 1)
            name = data.get("name", "")
            hosts = data.get("hosts", "")

            # 检查必填字段
            if not name:
                errors.append({"row": row, "name": name, "hosts": hosts, 
                              "error": "子网名称不能为空"})
                continue

            if not hosts:
                errors.append({"row": row, "name": name, "hosts": hosts, 
                              "error": "主机数量不能为空"})
                continue

            # 检查主机数量是否为正整数
            if not hosts.isdigit():
                errors.append({"row": row, "name": name, "hosts": hosts, 
                              "error": "主机数量必须是正整数"})
                continue

            if int(hosts) <= 0:
                errors.append({"row": row, "name": name, "hosts": hosts, 
                              "error": "主机数量必须大于0"})
                continue

            # 检查同批次重复
            if any(d["name"] == name for d in data_list[:idx]):
                errors.append({"row": row, "name": name, "hosts": hosts, 
                              "error": "文件中存在重复的子网名称"})
                continue

            # 检查重复性（同时检查两张表）
            if name in existing_names:
                errors.append({"row": row, "name": name, "hosts": hosts, 
                              "error": "子网名称已存在"})
                continue

            # 添加到已存在名称集合中，避免同批次重复
            existing_names.add(name)

        return errors

    def _show_import_result(self, errors, data_list):
        """显示导入验证结果对话框（显示所有数据，包括有效和无效）

        Args:
            errors: 错误列表
            data_list: 数据列表
        """
        dialog = tk.Toplevel(self.root)
        dialog.title("导入数据验证")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 先隐藏对话框，避免定位过程中的闪现
        dialog.withdraw()

        # 计算居中位置
        window_width = 750
        window_height = 500
        self.center_window(dialog, window_width, window_height)

        # 显示对话框
        dialog.deiconify()

        # 创建主内容框架
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 统计信息
        error_count = len(errors)
        total_count = len(data_list)
        valid_count = total_count - error_count

        summary_text = f"共 {total_count} 条数据，{valid_count} 条有效，{error_count} 条无效"
        ttk.Label(main_frame, text=summary_text, font=('微软雅黑', 10, 'bold')).pack(pady=(0, 10))

        # 创建表格显示所有数据
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        result_tree = ttk.Treeview(tree_frame, columns=("row", "name", "hosts", "status"), 
                                  show="headings", height=12)
        # 添加右键复制功能
        result_tree.bind("<Button-3>", lambda event, t=result_tree: self.copy_cell_data(event, t))
        result_tree.heading("row", text="行号")
        result_tree.heading("name", text="子网名称")
        result_tree.heading("hosts", text="主机数量")
        result_tree.heading("status", text="状态")

        result_tree.column("row", width=20, minwidth=20, anchor="e")
        result_tree.column("name", width=200, minwidth=80)
        result_tree.column("hosts", width=80, minwidth=40)
        result_tree.column("status", width=100, minwidth=80)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=result_tree.yview)

        result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 将错误列表转换为字典，提高查找效率
        error_dict = {e["row"]: e for e in errors}

        # 填充所有数据
        for data in data_list:
            row = data.get("row", 0)
            name = data.get("name", "")
            hosts = data.get("hosts", "")

            # 从字典中查找对应的错误信息（O(1)复杂度）
            error = error_dict.get(row)
            if error:
                status = error["error"]
                # 无效数据用红色标签
                tag = "invalid"
            else:
                status = "有效"
                # 有效数据用绿色标签
                tag = "valid"

            result_tree.insert("", tk.END, values=(row, name, hosts, status), tags=(tag,))

        # 配置标签样式
        result_tree.tag_configure("valid", foreground="green")
        result_tree.tag_configure("invalid", foreground="red")
        
        # 配置斑马条纹样式
        result_tree.tag_configure("even", background="#d8d8d8")
        result_tree.tag_configure("odd", background="#ffffff")
        
        # 应用斑马条纹效果
        for index, item in enumerate(result_tree.get_children()):
            # 获取当前标签
            current_tags = result_tree.item(item, "tags")
            # 添加斑马纹标签
            stripe_tag = "even" if index % 2 == 0 else "odd"
            # 合并标签，保持原有状态标签和新的斑马纹标签
            result_tree.item(item, tags=(*current_tags, stripe_tag))

        # 预先计算有效数据列表，避免在按钮点击时重复计算
        valid_data = [d for d in data_list if d.get("row", 0) not in error_dict]

        # 按钮框架 - 使用pack布局让按钮排列更整齐
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        # 导入到需求池表按钮
        import_pool_btn = ttk.Button(button_frame, text="导入需求池", 
                                     command=lambda: self._import_valid_data(valid_data, "pool", dialog),
                                     width=12)
        import_pool_btn.pack(side=tk.LEFT, padx=5)

        # 导入到子网需求表按钮
        import_req_btn = ttk.Button(button_frame, text="导入子网需求", 
                                    command=lambda: self._import_valid_data(valid_data, "requirements", dialog),
                                    width=12)
        import_req_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮 - 靠右显示，与其他按钮并排
        cancel_btn = ttk.Button(button_frame, text="取消", command=dialog.destroy, width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def _import_valid_data(self, valid_data, target_table, dialog=None):
        """导入有效数据

        Args:
            valid_data: 有效数据列表
            target_table: 目标表
            dialog: 对话框（可选）
        """
        if not valid_data:
            self.show_info("提示", "没有可导入的数据")
            if dialog:
                dialog.destroy()
            return

        # 导入数据
        for data in valid_data:
            name = data["name"]
            hosts = data["hosts"]

            if target_table == "requirements":
                # 添加到子网需求表
                current_rows = len(self.requirements_tree.get_children())
                new_index = current_rows + 1
                tag = "even" if new_index % 2 == 0 else "odd"
                self.requirements_tree.insert("", tk.END, values=(new_index, name, hosts), tags=(tag,))
            else:
                # 添加到需求池表
                current_rows = len(self.pool_tree.get_children())
                new_index = current_rows + 1
                tag = "even" if new_index % 2 == 0 else "odd"
                self.pool_tree.insert("", tk.END, values=(new_index, name, hosts), tags=(tag,))

        # 更新斑马条纹
        if target_table == "requirements":
            self.update_requirements_tree_zebra_stripes()
        else:
            self.update_pool_tree_zebra_stripes()

        # 保存状态
        self.save_current_state(f"导入数据: {len(valid_data)} 条记录")

        # 显示成功消息
        target_name = "子网需求表" if target_table == "requirements" else "需求池表"
        self.show_info("成功", f"成功导入 {len(valid_data)} 条记录到{target_name}")

        # 关闭对话框
        if dialog:
            dialog.destroy()

    def _generate_template(self, template_type):
        """生成模板文件

        Args:
            template_type: 模板类型，"excel"或"csv"
        """
        # 选择保存位置
        if template_type == "excel":
            default_ext = ".xlsx"
            filetypes = [("Excel文件", "*.xlsx")]
        else:
            default_ext = ".csv"
            filetypes = [("CSV文件", "*.csv")]

        file_path = filedialog.asksaveasfilename(
            title="保存模板",
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=f"子网需求导入模板{default_ext}",
            initialdir=""
        )

        if not file_path:
            return

        try:
            if template_type == "excel":
                # 生成Excel模板
                wb = Workbook()
                ws = wb.active
                ws.title = "子网需求"

                # 设置表头
                headers = ["子网名称", "主机数量"]
                for col_idx, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col_idx, value=header)
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加示例数据
                example_data = [
                    ["办公室", "20"],
                    ["人事部", "10"],
                    ["财务部", "10"],
                    ["规划部", "30"],
                    ["信息部", "20"],
                ]
                for row_idx, row_data in enumerate(example_data, 2):
                    for col_idx, value in enumerate(row_data, 1):
                        ws.cell(row=row_idx, column=col_idx, value=value)

                wb.save(file_path)

            else:
                # 生成CSV模板
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f)
                    # 写入表头
                    writer.writerow(["子网名称", "主机数量"])
                    # 写入示例数据
                    writer.writerow(["办公室", "20"])
                    writer.writerow(["人事部", "10"])
                    writer.writerow(["财务部", "10"])
                    writer.writerow(["规划部", "30"])
                    writer.writerow(["信息部", "20"])

            self.show_info("成功", f"模板已保存到: {file_path}")

        except Exception as e:
            self.show_error("错误", f"模板生成失败: {str(e)}")

    def copy_cell_data(self, event, tree):
        """复制表格中单元格数据的通用功能"""
        # 获取点击位置的行和列
        region = tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        
        # 获取点击的行ID和列
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        
        if not item:
            return
        
        # 获取列索引
        column_index = int(column.replace("#", "")) - 1
        
        # 获取行数据
        values = tree.item(item, "values")
        if not values or column_index >= len(values):
            return
        
        # 获取单元格数据
        cell_data = str(values[column_index])
        
        # 将数据复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(cell_data)
        
        # 可选：显示复制成功的提示
        self.show_result("已复制到剪贴板", keep_data=True)
    
    def bind_treeview_right_click(self, tree):
        """为Treeview绑定右键复制功能"""
        # 绑定右键菜单事件
        tree.bind("<Button-3>", lambda event, t=tree: self.copy_cell_data(event, t))
    
    def show_custom_dialog(self, title, message, dialog_type="info"):
        """显示自定义的居中对话框，支持info、error、warning类型"""
        result = None

        # 确保主窗口完全初始化，先更新主窗口布局
        self.root.update_idletasks()

        # 创建Toplevel窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)  # 设置为父窗口的子窗口
        dialog.grab_set()  # 模态对话框，阻止父窗口接收事件

        # 设置对话框最小宽度和高度，适当调高高度使其更加协调
        dialog.minsize(width=350, height=180)

        # 设置对话框内容
        frame = ttk.Frame(dialog, padding=40)
        frame.pack(fill=tk.BOTH, expand=True)

        # 设置frame的grid布局，删除第2行的weight设置，避免按钮下面出现过多空白
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)

        # 添加消息文本，居中显示，调整wraplength适应新的宽度
        msg_label = ttk.Label(frame, text=message, wraplength=250, font=('微软雅黑', 10))
        msg_label.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # 创建按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, sticky="e")

        # 确定按钮（用于info、error、warning类型）
        def on_ok():
            nonlocal result
            result = True
            dialog.destroy()

        # 根据对话框类型设置按钮
        if dialog_type in ["info", "error", "warning"]:
            # 只有确定按钮，使用默认样式
            ok_btn = ttk.Button(btn_frame, text="确定", command=on_ok)
            ok_btn.pack(side=tk.RIGHT)

            # 绑定回车键和Esc键
            dialog.bind('<Return>', lambda e: on_ok())
            dialog.bind('<Escape>', lambda e: on_ok())
            
            # 设置对话框为焦点，并将焦点聚焦到确定按钮上
            dialog.focus_set()
            ok_btn.focus_set()

        # 计算并设置对话框居中位置
        dialog.update_idletasks()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        # 获取主窗口在屏幕上的绝对位置和尺寸
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # 计算对话框在主窗口中心的坐标
        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2

        # 设置对话框位置
        dialog.geometry(f"+{dialog_x}+{dialog_y}")

        # 等待对话框关闭
        self.root.wait_window(dialog)

        return result

    def show_info(self, title, message):
        """显示信息对话框"""
        return self.show_custom_dialog(title, message, "info")

    def show_error(self, title, message):
        """显示错误对话框"""
        return self.show_custom_dialog(title, message, "error")

    def show_warning(self, title, message):
        """显示警告对话框"""
        return self.show_custom_dialog(title, message, "warning")

    def show_custom_confirm(self, title, message):
        """显示自定义的居中确认对话框"""
        result = None

        # 确保主窗口完全初始化，先更新主窗口布局
        self.root.update_idletasks()

        # 创建Toplevel窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)  # 设置为父窗口的子窗口
        dialog.grab_set()  # 模态对话框

        # 设置对话框最小宽度和高度
        dialog.minsize(width=500, height=150)

        # 设置对话框内容
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # 设置frame的grid布局，让按钮垂直居中
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        # 添加消息文本，居中显示，使用合适的wraplength
        msg_label = ttk.Label(frame, text=message, wraplength=450, font=('微软雅黑', 10))
        msg_label.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        # 创建按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, sticky="e")

        # 取消按钮
        def on_cancel():
            nonlocal result
            result = False
            dialog.destroy()

        cancel_btn = ttk.Button(btn_frame, text="取消", command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 确定按钮，使用默认样式
        def on_ok():
            nonlocal result
            result = True
            dialog.destroy()

        ok_btn = ttk.Button(btn_frame, text="确定", command=on_ok)
        ok_btn.pack(side=tk.RIGHT)

        # 绑定回车键和Esc键
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # 设置对话框为焦点，并将焦点聚焦到确定按钮上
        dialog.focus_set()
        ok_btn.focus_set()

        # 计算并设置对话框居中位置
        dialog.update_idletasks()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        # 获取主窗口在屏幕上的绝对位置和尺寸
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # 计算对话框在主窗口中心的坐标
        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2

        # 设置对话框位置
        dialog.geometry(f"+{dialog_x}+{dialog_y}")

        # 等待对话框关闭
        self.root.wait_window(dialog)

        return result

    def undo_delete(self):
        """撤销最近的删除操作，支持多次撤销"""
        # 检查是否有删除记录历史
        if not self.deleted_history:
            self.show_info("提示", "没有可撤销的删除操作")
            return

        # 从历史记录中取出最近一次删除的记录批次
        deleted_records = self.deleted_history.pop()

        # 恢复被删除的记录
        restored_subnets = []

        for record in deleted_records:
            tree_type = record["tree"]
            values = record["values"]

            # 根据记录类型选择对应的表格
            if tree_type == "requirements":
                # 恢复到子网需求表
                self.requirements_tree.insert("", tk.END, values=values)
            elif tree_type == "pool":
                # 恢复到需求池表
                self.pool_tree.insert("", tk.END, values=values)

            # 收集恢复的子网信息
            restored_subnets.append(f"{values[1]}({values[2]})")

        # 恢复后重新应用斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()

        # 保存当前状态到操作记录，包含恢复的子网信息
        if restored_subnets:
            action_type = f"撤销删除: 恢复了 {', '.join(restored_subnets)}"
        else:
            action_type = "撤销删除"
        self.save_current_state(action_type)
        
        # 显示成功提示
        self.show_info("成功", f"成功恢复了 {len(deleted_records)} 条记录")

    def on_requirements_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能（子网需求表）"""
        # 获取双击位置的信息
        region = self.requirements_tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        # 获取双击的行和列
        item = self.requirements_tree.identify_row(event.y)
        column = self.requirements_tree.identify_column(event.x)

        if not item or not column:
            return

        # 将列标识转换为列索引（例如 #1 -> 0, #2 -> 1）
        column_index = int(column[1:]) - 1
        # 不允许编辑序号列
        if column_index == 0:
            return
        column_name = self.requirements_tree["columns"][column_index]

        # 获取当前值
        current_value = self.requirements_tree.item(item, "values")[column_index]

        # 获取单元格的坐标和大小
        cell_x, cell_y, width, height = self.requirements_tree.bbox(item, column)

        # 创建编辑框
        self.edit_entry = ttk.Entry(self.requirements_tree, width=width // 10)  # 估算字符宽度
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # 添加验证和即时反红功能
        def validate_edit(text):
            if column_index == 1:  # 子网名称列
                is_valid = bool(text.strip())
            elif column_index == 2:  # 主机数量列
                is_valid = text.isdigit() and int(text) > 0 if text else True
            else:
                is_valid = True
            self.edit_entry.config(foreground='black' if is_valid else 'red')
            return "1"  # 始终允许输入，只做视觉提示
        self.edit_entry.config(validate="all", validatecommand=(self.root.register(validate_edit), "%P"))

        # 设置编辑框在单元格上
        self.edit_entry.place(x=cell_x, y=cell_y, width=width, height=height)

        # 保存当前编辑的信息
        self.current_edit_item = item
        self.current_edit_column = column_name
        self.current_edit_column_index = column_index
        self.current_edit_tree = "requirements"  # 保存当前编辑的表格

        # 绑定事件
        self.edit_entry.bind("<FocusOut>", self.on_edit_focus_out)
        self.edit_entry.bind("<Return>", self.on_edit_enter)
        self.edit_entry.bind("<Escape>", self.on_edit_escape)

    def on_pool_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能（需求池表）"""
        # 获取双击位置的信息
        region = self.pool_tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        # 获取双击的行和列
        item = self.pool_tree.identify_row(event.y)
        column = self.pool_tree.identify_column(event.x)

        if not item or not column:
            return

        # 将列标识转换为列索引（例如 #1 -> 0, #2 -> 1）
        column_index = int(column[1:]) - 1
        # 不允许编辑序号列
        if column_index == 0:
            return
        column_name = self.pool_tree["columns"][column_index]

        # 获取当前值
        current_value = self.pool_tree.item(item, "values")[column_index]

        # 获取单元格的坐标和大小
        cell_x, cell_y, width, height = self.pool_tree.bbox(item, column)

        # 创建编辑框
        self.edit_entry = ttk.Entry(self.pool_tree, width=width // 10)  # 估算字符宽度
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # 添加验证和即时反红功能
        def validate_edit(text):
            if column_index == 1:  # 子网名称列
                is_valid = bool(text.strip())
            elif column_index == 2:  # 主机数量列
                is_valid = text.isdigit() and int(text) > 0 if text else True
            else:
                is_valid = True
            self.edit_entry.config(foreground='black' if is_valid else 'red')
            return "1"  # 始终允许输入，只做视觉提示
        self.edit_entry.config(validate="all", validatecommand=(self.root.register(validate_edit), "%P"))

        # 设置编辑框在单元格上
        self.edit_entry.place(x=cell_x, y=cell_y, width=width, height=height)

        # 保存当前编辑的信息
        self.current_edit_item = item
        self.current_edit_column = column_name
        self.current_edit_column_index = column_index
        self.current_edit_tree = "pool"  # 保存当前编辑的表格

        # 绑定事件
        self.edit_entry.bind("<FocusOut>", self.on_edit_focus_out)
        self.edit_entry.bind("<Return>", self.on_edit_enter)
        self.edit_entry.bind("<Escape>", self.on_edit_escape)

    def on_edit_focus_out(self, _):
        """编辑框失去焦点时保存数据"""
        self.save_edit()

    def on_edit_enter(self, _):
        """按下Enter键时保存数据"""
        self.save_edit()

    def on_edit_escape(self, _):
        """按下Escape键时取消编辑"""
        self.edit_entry.destroy()
        del self.current_edit_item
        del self.current_edit_column
        del self.current_edit_column_index
        if hasattr(self, 'current_edit_tree'):
            del self.current_edit_tree

    def on_treeview_click(self, event):
        """处理Treeview左键单击事件，实现取消选择功能"""
        # 获取点击位置的信息
        tree = event.widget
        region = tree.identify_region(event.x, event.y)
        if region != "cell" and region != "row":
            return
        
        # 获取点击的行
        item = tree.identify_row(event.y)
        if not item:
            return
        
        # 获取当前选中的所有项
        selected_items = list(tree.selection())
        
        # 获取按键状态
        is_ctrl = event.state & 0x4  # Ctrl键
        is_shift = event.state & 0x1  # Shift键
        
        # Ctrl+点击：切换选择状态
        if is_ctrl:
            if item in selected_items:
                # 已选中，取消选择
                tree.selection_remove(item)
            else:
                # 未选中，添加到选择
                tree.selection_add(item)
        # Shift+点击：选择范围
        elif is_shift:
            if selected_items:
                all_items = tree.get_children()
                last_selected = selected_items[-1]
                start_idx = all_items.index(last_selected)
                end_idx = all_items.index(item)
                
                # 先取消所有选中项
                tree.selection_remove(selected_items)
                
                # 选择范围
                for idx in range(min(start_idx, end_idx), max(start_idx, end_idx) + 1):
                    tree.selection_add(all_items[idx])
            else:
                # 没有选中项，直接选择当前项
                tree.selection_set(item)
        # 普通点击
        else:
            if item in selected_items:
                # 点击已选中项
                if len(selected_items) == 1:
                    # 唯一选中项，取消选择
                    tree.selection_remove(item)
                else:
                    # 多个选中项，只选择当前项
                    tree.selection_set(item)
            else:
                # 点击未选中项，只选择当前项
                tree.selection_set(item)
        
        # 阻止事件继续传递，避免默认行为冲突
        return "break"

    def save_edit(self):
        """保存编辑的数据"""
        if hasattr(self, 'current_edit_item'):
            # 获取新值
            new_value = self.edit_entry.get().strip()

            # 验证数据
            if not new_value:
                self.show_error("错误", "输入不能为空")
                return

            # 获取原始值
            if self.current_edit_tree == "requirements":
                original_value = self.requirements_tree.item(self.current_edit_item, "values")[
                    self.current_edit_column_index
                ]
            else:
                original_value = self.pool_tree.item(self.current_edit_item, "values")[self.current_edit_column_index]

            # 如果值没有变化，直接保存，不进行重复检查
            if new_value == original_value:
                # 根据当前编辑的表格，更新相应的Treeview数据
                if self.current_edit_tree == "requirements":
                    # 更新子网需求表
                    values = list(self.requirements_tree.item(self.current_edit_item, "values"))
                    values[self.current_edit_column_index] = new_value
                    self.requirements_tree.item(self.current_edit_item, values=values)
                    # 更新斑马条纹
                    self.update_table_zebra_stripes(self.requirements_tree)
                else:
                    # 更新需求池表
                    values = list(self.pool_tree.item(self.current_edit_item, "values"))
                    values[self.current_edit_column_index] = new_value
                    self.pool_tree.item(self.current_edit_item, values=values)
                    # 更新斑马条纹
                    self.update_table_zebra_stripes(self.pool_tree)

                # 清理编辑状态
                self.edit_entry.destroy()
                del self.current_edit_item
                del self.current_edit_column
                del self.current_edit_column_index
                if hasattr(self, 'current_edit_tree'):
                    del self.current_edit_tree
                return

            if self.current_edit_column == "name":
                # 检查是否存在相同名称的子网（排除当前正在编辑的行）
                # 1. 检查子网需求表
                for item in self.requirements_tree.get_children():
                    # 只有当当前编辑的是子网需求表时，才需要排除当前记录
                    if self.current_edit_tree == "requirements" and item == self.current_edit_item:
                        continue
                    values = self.requirements_tree.item(item, "values")
                    existing_name = values[1]  # 子网名称在第二列
                    if existing_name == new_value:
                        self.show_error("错误", f"已经存在名称为 '{new_value}' 的子网，请使用其他名称")
                        return
                # 2. 检查需求池表
                for item in self.pool_tree.get_children():
                    # 只有当当前编辑的是需求池表时，才需要排除当前记录
                    if self.current_edit_tree == "pool" and item == self.current_edit_item:
                        continue
                    values = self.pool_tree.item(item, "values")
                    existing_name = values[1]  # 子网名称在第二列
                    if existing_name == new_value:
                        self.show_error("错误", f"已经存在名称为 '{new_value}' 的子网，请使用其他名称")
                        return

            if self.current_edit_column == "hosts":
                try:
                    hosts = int(new_value)
                    if hosts <= 0:
                        self.show_error("错误", "主机数量必须大于0")
                        return
                except ValueError:
                    self.show_error("错误", "主机数量必须是整数")
                    return

            # 根据当前编辑的表格，更新相应的Treeview数据
            if hasattr(self, 'current_edit_tree') and self.current_edit_tree == "requirements":
                # 更新子网需求表
                values = list(self.requirements_tree.item(self.current_edit_item, "values"))
                values[self.current_edit_column_index] = new_value
                self.requirements_tree.item(self.current_edit_item, values=values)
                # 更新斑马条纹
                self.update_requirements_tree_zebra_stripes()
            elif hasattr(self, 'current_edit_tree') and self.current_edit_tree == "pool":
                # 更新需求池表
                values = list(self.pool_tree.item(self.current_edit_item, "values"))
                values[self.current_edit_column_index] = new_value
                self.pool_tree.item(self.current_edit_item, values=values)
                # 更新斑马条纹
                self.update_pool_tree_zebra_stripes()

            # 销毁编辑框
            self.edit_entry.destroy()

            # 清理临时属性
            del self.current_edit_item
            del self.current_edit_column
            del self.current_edit_column_index
            if hasattr(self, 'current_edit_tree'):
                del self.current_edit_tree

    def execute_subnet_planning(self, from_history=False):
        """执行子网规划

        Args:
            from_history: 是否从历史记录重新执行，True表示不将操作记入历史
        """
        # 获取父网段
        parent = self.planning_parent_entry.get().strip()
        if not parent:
            self.show_error("错误", "请输入父网段")
            return

        if not self.validate_cidr(parent):
            self.show_error("错误", "父网段格式不正确，请输入有效的CIDR格式（例如：192.168.1.0/24）")
            return

        # 获取子网需求
        subnet_requirements = []
        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item, "values")
            subnet_requirements.append((values[1], int(values[2])))

        if not subnet_requirements:
            self.show_error("错误", "请添加至少一个子网需求")
            return

        try:
            # 执行子网规划
            # 转换子网需求格式以匹配函数参数要求
            formatted_requirements = [{'name': name, 'hosts': hosts} for name, hosts in subnet_requirements]

            # 调用子网规划函数
            plan_result = suggest_subnet_planning(parent, formatted_requirements)

            # 检查是否有错误
            if 'error' in plan_result:
                self.show_error("错误", f"子网规划失败: {plan_result['error']}")
                return

            # 清空结果表格
            self.clear_tree_items(self.allocated_tree)
            self.clear_tree_items(self.planning_remaining_tree)

            # 显示已分配子网
            for i, subnet in enumerate(plan_result['allocated_subnets'], 1):
                # 设置斑马条纹标签
                tags = ("even",) if i % 2 == 0 else ("odd",)
                self.allocated_tree.insert(
                    "",
                    tk.END,
                    values=(
                        i,
                        subnet["name"],
                        subnet["cidr"],
                        subnet["required_hosts"],
                        subnet["available_hosts"],
                        subnet["info"]["network"],
                        subnet["info"]["netmask"],
                        subnet["info"]["broadcast"],
                    ),
                    tags=tags,
                )
            # 斑马条纹样式已在初始化时配置

            # 数据添加完成后，自动调整列宽以适应内容
            self.auto_resize_columns(self.allocated_tree)

            # 显示剩余网段
            for i, subnet in enumerate(plan_result['remaining_subnets_info'], 1):
                # 设置斑马条纹标签
                tags = ("even",) if i % 2 == 0 else ("odd",)
                self.planning_remaining_tree.insert(
                    "",
                    tk.END,
                    values=(
                        i,
                        plan_result['remaining_subnets'][i - 1],
                        subnet["network"],
                        subnet["netmask"],
                        subnet["broadcast"],
                        subnet["usable_addresses"],  # 修正为正确的字段名
                    ),
                    tags=tags,
                )
            # 斑马条纹样式已在初始化时配置

            # 数据添加完成后，自动调整列宽以适应内容
            self.auto_resize_columns(self.planning_remaining_tree)

            # 子网规划完成，不显示对话框提示

            # 如果不是从历史记录执行，将操作记录保存到历史
            if not from_history:
                # 检查当前父网段是否在列表中，如果不在则添加（使用子网规划专用的父网段历史记录）
                current_parent = self.planning_parent_entry.get().strip()
                if current_parent and current_parent not in self.planning_parent_networks:
                    self.planning_parent_networks.append(current_parent)
                    self.planning_parent_entry.config(values=self.planning_parent_networks)

                # 保存当前状态到操作记录
                self.save_current_state("执行规划")

        except ValueError as e:
            error_msg = str(e)
            if "not permitted" in error_msg and "Octet" in error_msg:
                match = re.search(r"Octet\D*(\d+)", error_msg)
                if match:
                    octet = match.group(1)
                    message = f"子网规划失败: IP地址中包含无效的八位组 '{octet}'（必须小于等于255）"
                else:
                    message = f"子网规划失败: {error_msg}"
            else:
                message = f"子网规划失败: {error_msg}"
            self.show_error("错误", message)
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_error("错误", f"子网规划失败: 发生未知错误 - {str(e)}")

    def execute_split(self, from_history=False):
        """执行切分操作

        Args:
            from_history: 是否从历史记录重新执行，True表示不将操作记入历史
        """
        parent = self.parent_entry.get().strip()
        split = self.split_entry.get().strip()

        # 验证输入
        if not parent or not split:
            # 清空表格并显示错误信息
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert("", tk.END, values=("错误", "父网段和切分网段都不能为空！"), tags=("error",))
            return

        # 验证CIDR格式
        if not self.validate_cidr(parent):
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert(
                "", tk.END, values=("错误", "父网段格式无效，请输入有效的CIDR格式！"), tags=("error",)
            )
            self.show_error("输入错误", "父网段格式无效，请输入有效的CIDR格式（如: 10.0.0.0/8）")
            return
        if not self.validate_cidr(split):
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert(
                "", tk.END, values=("错误", "切分网段格式无效，请输入有效的CIDR格式！"), tags=("error",)
            )
            self.show_error("输入错误", "切分网段格式无效，请输入有效的CIDR格式（如: 10.21.60.0/23）")
            return

        try:
            # 调用切分函数
            result = split_subnet(parent, split)

            # 清空现有结果
            self.clear_tree_items(self.split_tree)
            self.clear_tree_items(self.remaining_tree)

            if "error" in result:
                # 显示错误信息
                self.split_tree.insert("", tk.END, values=("错误", result["error"]), tags=("error",))
                return

            # 添加切分段信息，同时设置斑马条纹标签
            row_index = 0
            self.split_tree.insert("", tk.END, values=("父网段", result["parent_info"]["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("切分网段", result["split_info"]["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("-" * 10, "-" * 20), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1

            # 添加切分后的网段信息
            split_info = result["split_info"]
            self.split_tree.insert("", tk.END, values=("网络地址", split_info["network"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("子网掩码", split_info["netmask"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("通配符掩码", split_info["wildcard"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("广播地址", split_info["broadcast"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("起始地址", split_info["host_range_start"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("结束地址", split_info["host_range_end"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("总地址数", split_info["num_addresses"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("可用地址数", split_info["usable_addresses"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("前缀长度", split_info["prefixlen"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=("CIDR", split_info["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))

            # 显示剩余网段表表格
            if result["remaining_subnets_info"]:
                for i, network in enumerate(result["remaining_subnets_info"], 1):
                    # 设置斑马条纹标签
                    tags = ("even",) if i % 2 == 0 else ("odd",)
                    self.remaining_tree.insert(
                        "",
                        tk.END,
                        values=(
                            i,
                            network["cidr"],
                            network["network"],
                            network["netmask"],
                            network.get("wildcard", ""),
                            network["broadcast"],
                            network["usable_addresses"],
                        ),
                        tags=tags,
                    )

            else:
                self.remaining_tree.insert("", tk.END, values=(1, "无", "无", "无", "无", "无"))

            # 让表格自适应窗口宽度
            self.adjust_remaining_tree_width()

            # 优化滚动条状态更新，减少不必要的计算
            if hasattr(self, 'remaining_scroll_v'):
                # 获取当前滚动位置
                yview = self.remaining_tree.yview()
                # 检查是否需要显示滚动条
                need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

                # 只在状态变化时才更新UI，减少不必要的刷新
                current_state = self.remaining_scroll_v.winfo_ismapped()
                if need_scrollbar != current_state:
                    if need_scrollbar:
                        # 内容可滚动，显示滚动条
                        self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)
                        self.remaining_scroll_v.set(yview[0], yview[1])
                    else:
                        # 内容不可滚动，隐藏滚动条
                        self.remaining_scroll_v.grid_remove()

            # 准备图表数据
            self.prepare_chart_data(result, split_info, result["remaining_subnets_info"])

            # 绘制图表
            self.draw_distribution_chart()

            # 如果不是从历史记录重新执行，则将操作记录到历史列表
            if not from_history:
                # 检查当前父网段是否在列表中，如果不在则添加（使用子网切分专用的父网段历史记录）
                if parent and parent not in self.split_parent_networks:
                    self.split_parent_networks.append(parent)
                    # 限制历史记录大小，最多保留100条
                    if len(self.split_parent_networks) > 100:
                        self.split_parent_networks.pop(0)
                    self.parent_entry.config(values=self.split_parent_networks)

                # 检查当前切分段是否在列表中，如果不在则添加
                if split and split not in self.split_networks:
                    self.split_networks.append(split)
                    # 限制历史记录大小，最多保留100条
                    if len(self.split_networks) > 100:
                        self.split_networks.pop(0)
                    self.split_entry.config(values=self.split_networks)

                # 检查是否已存在相同的记录
                duplicate_exists = any(
                    record['parent'] == parent and record['split'] == split for record in self.history_records
                )

                # 如果不存在相同记录，则添加到历史记录
                if not duplicate_exists:
                    split_record = {'parent': parent, 'split': split}
                    self.history_records.append(split_record)
                    # 限制历史记录大小，最多保留50条
                    if len(self.history_records) > 50:
                        self.history_records.pop(0)

                    # 更新历史记录列表
                    self.update_history_tree()

        except ValueError as e:
            error_msg = str(e)
            if "not permitted" in error_msg and "Octet" in error_msg:
                match = re.search(r"Octet\D*(\d+)", error_msg)
                if match:
                    octet = match.group(1)
                    message = f"IP地址中包含无效的八位组 '{octet}'（必须小于等于255）"
                else:
                    message = error_msg
            else:
                message = error_msg
            self.clear_result()
            self.split_tree.insert("", tk.END, values=("错误", message), tags=("error",))
        except (tk.TclError, AttributeError, TypeError) as e:
            self.clear_result()
            self.split_tree.insert("", tk.END, values=("错误", f"发生未知错误: {str(e)}"), tags=("error",))

    def clear_tree_items(self, tree):
        """清空表格中的所有项

        Args:
            tree: 要清空的Treeview对象
        """
        # 批量删除所有子项，减少UI更新次数
        children = tree.get_children()
        if children:
            tree.delete(*children)

    def hide_info_bar(self):
        """隐藏信息栏"""
        # 取消自动隐藏定时器
        if self.info_auto_hide_id:
            self.root.after_cancel(self.info_auto_hide_id)
            self.info_auto_hide_id = None
        # 隐藏信息栏 - 使用place_forget()
        self.info_bar_frame.pack_forget()

    def setup_advanced_tools_page(self):
        """设置高级工具功能的界面"""
        # 创建一个笔记本控件来显示不同的高级工具功能
        self.advanced_notebook = ColoredNotebook(self.advanced_frame, style=self.style)
        self.advanced_notebook.pack(fill=tk.BOTH, expand=True)

        # 1. IPv4地址信息查询功能 - 浅蓝色
        self.ipv4_info_frame = ttk.Frame(
            self.advanced_notebook.content_area, padding="10", style=self.advanced_notebook.light_blue_style
        )
        self.create_ipv4_info_section()

        # 2. IPv6地址信息查询功能 - 浅绿色
        self.ipv6_info_frame = ttk.Frame(
            self.advanced_notebook.content_area, padding="10", style=self.advanced_notebook.light_green_style
        )
        self.create_ipv6_info_section()

        # 3. 子网合并与范围转CIDR功能 - 浅紫色
        self.merge_frame = ttk.Frame(
            self.advanced_notebook.content_area, padding="10", style=self.advanced_notebook.light_purple_style
        )
        self.create_merged_subnets_and_cidr_section()

        # 5. 子网重叠检测功能 - 淡粉色
        self.overlap_frame = ttk.Frame(
            self.advanced_notebook.content_area, padding="10", style=self.advanced_notebook.light_pink_style
        )
        self.create_subnet_overlap_section()

        # 添加高级工具标签页
        self.advanced_notebook.add_tab("IPv4查询", self.ipv4_info_frame, "#e3f2fd")  # 浅蓝色
        self.advanced_notebook.add_tab("IPv6查询", self.ipv6_info_frame, "#e8f5e9")  # 浅绿色
        self.advanced_notebook.add_tab("子网合并", self.merge_frame, "#f3e5f5")  # 浅紫色
        self.advanced_notebook.add_tab("重叠检测", self.overlap_frame, "#fce4ec")  # 淡粉色

    def create_ipv6_info_section(self):
        """创建IPv6地址信息查询功能界面"""
        # 在ipv6_info_frame中增加中间容器，内边距10
        content_container = ttk.Frame(self.ipv6_info_frame, padding="10")
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建输入区域
        input_frame = ttk.LabelFrame(content_container, text="IPv6地址信息查询", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # IPv6地址输入 - 使用Combobox，支持下拉选择和记忆功能
        ttk.Label(input_frame, text="IPv6地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.ipv6_info_entry = ttk.Combobox(input_frame, values=self.ipv6_history, width=48, font=("微软雅黑", 10))
        self.ipv6_info_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.ipv6_info_entry.insert(0, "2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        self.ipv6_info_entry.config(state="normal")  # 允许手动输入
        
        # IPv6地址验证函数
        def validate_ipv6(text):
            """验证IPv6地址格式"""
            text = text.strip()
            # IPv6地址正则表达式（简化版，支持压缩格式）
            ipv6_pattern = r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
            is_valid = bool(re.match(ipv6_pattern, text)) if text else True
            # 设置文本颜色
            self.ipv6_info_entry.config(foreground='black' if is_valid else 'red')
            # 始终返回"1"，允许所有输入，只做视觉提示
            return "1"
        
        # 配置验证
        self.ipv6_info_entry.config(validate="all", validatecommand=(self.ipv6_info_entry.register(validate_ipv6), "%P"))
        
        # 初始验证一次
        validate_ipv6(self.ipv6_info_entry.get())

        # CIDR下拉列表（IPv6支持1-128）
        ttk.Label(input_frame, text="CIDR:").pack(side=tk.LEFT, padx=(0, 5))
        self.ipv6_cidr_var = tk.StringVar()
        self.ipv6_cidr_combobox = ttk.Combobox(
            input_frame, textvariable=self.ipv6_cidr_var, width=3, state="readonly", font=("微软雅黑", 10)
        )
        self.ipv6_cidr_combobox['values'] = list(range(1, 129))
        self.ipv6_cidr_combobox.current(63)  # 默认选择64
        self.ipv6_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))

        self.ipv6_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv6_info)
        self.ipv6_info_btn.pack(side=tk.RIGHT)

        # 创建结果区域
        result_frame = ttk.LabelFrame(content_container, text="查询结果", padding=(10, 10, 0, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview和垂直滚动条
        self.ipv6_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        # 添加右键复制功能
        self.bind_treeview_right_click(self.ipv6_info_tree)
        self.ipv6_info_tree.heading("item", text="项目")
        self.ipv6_info_tree.heading("value", text="值")

        self.ipv6_info_tree.column("item", width=100)
        self.ipv6_info_tree.column("value", width=350)

        # 添加垂直滚动条
        ipv6_info_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)

        # 使用通用方法创建带自动隐藏滚动条的Treeview
        self.create_scrollable_treeview(result_frame, self.ipv6_info_tree, ipv6_info_scrollbar)

        self.configure_treeview_styles(self.ipv6_info_tree, include_special_tags=True)

    def create_merged_subnets_and_cidr_section(self):
        """创建子网合并和范围转CIDR功能界面"""
        # 创建输入部分的容器，包含所有组件
        input_container = ttk.Frame(self.merge_frame, padding="10")
        input_container.pack(fill=tk.BOTH, expand=True)

        # 创建两列框架，放置在输入容器中
        left_frame = ttk.Frame(input_container)
        right_frame = ttk.Frame(input_container)

        # 使用grid布局，固定左侧宽度，右侧自适应
        input_container.grid_columnconfigure(0, minsize=140, weight=0)  # 固定左侧宽度
        input_container.grid_columnconfigure(1, weight=1)  # 右侧自适应
        input_container.grid_rowconfigure(0, weight=1)  # 确保行能够撑满高度

        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 确保左侧面板内部的行能撑满高度
        left_frame.grid_rowconfigure(0, weight=1)  # 子网列表面板行
        left_frame.grid_rowconfigure(1, weight=0)  # IP地址范围面板行（固定高度）

        # 左侧上方：子网合并列表 - 使用grid布局
        subnet_frame = ttk.LabelFrame(left_frame, text="子网合并列表", padding=(10, 10, 0, 10))
        subnet_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        # 配置左侧面板的grid布局
        left_frame.grid_rowconfigure(0, weight=1)  # 子网列表面板随窗体变化
        left_frame.grid_rowconfigure(1, weight=0)  # IP地址范围面板固定高度
        left_frame.grid_columnconfigure(0, weight=1)  # 第一列占满宽度

        # 子网合并列表输入文本框
        self.subnet_merge_text = tk.Text(subnet_frame, height=8, width=17, font=("微软雅黑", 10))

        # 添加垂直滚动条
        subnet_merge_scrollbar = ttk.Scrollbar(subnet_frame, orient=tk.VERTICAL)
        self.subnet_merge_text.insert(tk.END, "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24\n10.21.16.0/24\n10.21.17.0/24\n10.21.18.0/24\n10.21.19.128/26\n10.21.19.192/26")

        # 配置子网合并列表面板的grid布局
        subnet_frame.grid_columnconfigure(0, weight=1)  # 文本框列
        subnet_frame.grid_columnconfigure(1, weight=0)  # 滚动条列
        subnet_frame.grid_rowconfigure(0, weight=1)  # 文本框行
        subnet_frame.grid_rowconfigure(1, weight=0)  # 按钮行

        # 使用通用方法创建带自动隐藏滚动条的Text组件
        self.create_scrollable_text(subnet_frame, self.subnet_merge_text, subnet_merge_scrollbar)

        # 子网合并按钮 - 固定在右下角
        self.merge_btn = ttk.Button(subnet_frame, text="合并子网", command=self.execute_merge_subnets)
        self.merge_btn.grid(row=1, column=0, columnspan=1, sticky="w", pady=(5, 0), padx=(0, 10))

        # 左侧下方：IP地址范围 - 使用grid布局
        range_frame = ttk.LabelFrame(left_frame, text="IP地址范围", padding="10")
        range_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))  # 仅水平填充，固定高度

        # 起始IP - 使用Combobox，支持下拉选择和记忆功能
        start_frame = ttk.Frame(range_frame)
        start_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(start_frame, text="起始:").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_start_entry = ttk.Combobox(
            start_frame, values=self.range_start_history, width=13, font=("微软雅黑", 10)
        )
        self.range_start_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_start_entry.insert(0, "192.168.0.1")
        self.range_start_entry.config(state="normal")  # 允许手动输入
        
        # IP范围地址验证函数
        def validate_range_ip(text, entry):
            """验证IP范围地址格式"""
            text = text.strip()
            # IPv4地址正则表达式 - 修复了点号匹配问题，使用\.转义点号
            ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            is_valid = bool(re.match(ipv4_pattern, text)) if text else True
            # 设置文本颜色
            entry.config(foreground='black' if is_valid else 'red')
            # 始终返回"1"，允许所有输入，只做视觉提示
            return "1"
        
        # 为起始IP添加验证
        def validate_start_ip(text):
            return validate_range_ip(text, self.range_start_entry)
        self.range_start_entry.config(validate="all", validatecommand=(self.range_start_entry.register(validate_start_ip), "%P"))
        
        # 初始验证一次
        validate_start_ip(self.range_start_entry.get())

        # 结束IP - 使用Combobox，支持下拉选择和记忆功能
        end_frame = ttk.Frame(range_frame)
        end_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(end_frame, text="结束:").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_end_entry = ttk.Combobox(end_frame, values=self.range_end_history, width=13, font=("微软雅黑", 10))
        self.range_end_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_end_entry.insert(0, "192.168.30.254")
        self.range_end_entry.config(state="normal")  # 允许手动输入
        
        # 为结束IP添加验证
        def validate_end_ip(text):
            return validate_range_ip(text, self.range_end_entry)
        self.range_end_entry.config(validate="all", validatecommand=(self.range_end_entry.register(validate_end_ip), "%P"))
        
        # 初始验证一次
        validate_end_ip(self.range_end_entry.get())

        # 范围转CIDR按钮 - 靠左放置
        self.range_to_cidr_btn = ttk.Button(range_frame, text="转换为CIDR", command=self.execute_range_to_cidr)
        self.range_to_cidr_btn.pack(side=tk.LEFT, pady=(5, 0))

        # 右侧：CIDR结果
        self.merge_result_frame = ttk.LabelFrame(right_frame, text="CIDR结果", padding=(10, 10, 0, 10))
        self.merge_result_frame.pack(fill=tk.BOTH, expand=True)

        # 创建正常的结果树（非转置）
        columns = ["CIDR", "网络地址", "子网掩码", "广播地址", "主机数"]
        self.merge_result_tree = ttk.Treeview(self.merge_result_frame, columns=columns, show="headings")
        # 添加右键复制功能
        self.bind_treeview_right_click(self.merge_result_tree)

        # 设置列标题和初始宽度
        for i, col in enumerate(columns):
            self.merge_result_tree.heading(col, text=col)
            if i == 0:  # CIDR列
                self.merge_result_tree.column(col, width=110, minwidth=110, stretch=False)
            elif i == 1:  # 网络地址列
                self.merge_result_tree.column(col, width=70, minwidth=70)
            elif i == 2:  # 子网掩码列
                self.merge_result_tree.column(col, width=70, minwidth=70)
            elif i == 3:  # 广播地址列
                self.merge_result_tree.column(col, width=70, minwidth=70)
            elif i == 4:  # 主机数列
                self.merge_result_tree.column(col, width=40, minwidth=40)

        # 添加垂直滚动条 - 作为实例变量，方便后续重新绑定
        self.merge_result_scrollbar = ttk.Scrollbar(self.merge_result_frame, orient=tk.VERTICAL)
        self.create_scrollable_treeview(self.merge_result_frame, self.merge_result_tree, self.merge_result_scrollbar)

        self.configure_treeview_styles(self.merge_result_tree)

    def create_scrollable_treeview(self, parent_frame, treeview, scrollbar, no_scrollbar_padx=(0, 10)):
        """
        创建带自动隐藏滚动条的Treeview，并实现滚动条隐藏时自动调整外边距

        参数:
            parent_frame: Treeview和滚动条的父容器
            treeview: 要添加滚动条的Treeview组件
            scrollbar: 滚动条组件
            no_scrollbar_padx: 滚动条隐藏时Treeview的右边距，默认(0, 10)
        """

        # 创建滚动条回调函数，实现自动隐藏和外边距调整
        def scrollbar_callback(*args):
            # 设置滚动条位置
            scrollbar.set(*args)

            # 检查是否需要显示滚动条
            yview = treeview.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            # 根据是否需要滚动条调整Treeview的右边距
            if need_scrollbar:
                # 显示滚动条
                scrollbar.grid(row=0, column=1, sticky=tk.NS)
                # 调整Treeview的grid配置，移除右边距
                treeview.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=0)
                
            else:
                # 隐藏滚动条
                scrollbar.grid_remove()
                # 调整Treeview的grid配置，添加右边距
                treeview.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=no_scrollbar_padx)

        # 绑定滚动条和Treeview
        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=scrollbar_callback)

        # 使用grid布局，确保Treeview和滚动条正确对齐
        treeview.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 配置grid权重，使Treeview可以扩展
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        # 初始调用一次回调函数，设置初始状态
        scrollbar_callback(0.0, 1.0)

    def create_scrollable_treeview_with_grid(self, parent_frame, treeview, scrollbar, 
                                           tree_row=0, tree_column=0, scrollbar_row=0, scrollbar_column=1,
                                           tree_padx=(0, 0), scrollbar_padx=(0, 0), no_scrollbar_padx=(0, 10)):
        """
        创建带自动隐藏滚动条的Treeview，并实现滚动条隐藏时自动调整外边距
        支持自定义grid位置

        参数:
            parent_frame: Treeview和滚动条的父容器
            treeview: 要添加滚动条的Treeview组件
            scrollbar: 滚动条组件
            tree_row: Treeview的grid行位置，默认0
            tree_column: Treeview的grid列位置，默认0
            scrollbar_row: 滚动条的grid行位置，默认0
            scrollbar_column: 滚动条的grid列位置，默认1
            tree_padx: Treeview的grid padx参数，默认(0, 0)
            scrollbar_padx: 滚动条的grid padx参数，默认(0, 0)
            no_scrollbar_padx: 滚动条隐藏时Treeview的右边距，默认(0, 10)
        """

        # 创建滚动条回调函数，实现自动隐藏和外边距调整
        def scrollbar_callback(*args):
            # 设置滚动条位置
            scrollbar.set(*args)

            # 检查是否需要显示滚动条
            yview = treeview.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            # 根据是否需要滚动条调整Treeview的右边距
            if need_scrollbar:
                # 显示滚动条
                scrollbar.grid(row=scrollbar_row, column=scrollbar_column, sticky=tk.NS, padx=scrollbar_padx)
                # 调整Treeview的grid配置，移除右边距
                treeview.grid_configure(row=tree_row, column=tree_column, sticky=tk.NSEW, padx=tree_padx)
                
                # 如果是需求池表或子网需求表，减小name列宽度为滚动条留出空间
                if treeview in [getattr(self, 'pool_tree', None), getattr(self, 'requirements_tree', None)]:
                    try:
                        treeview.column("name", width=110)  # 减小name列宽度
                    except tk.TclError:
                        pass  # 如果列不存在则忽略
            else:
                # 隐藏滚动条
                scrollbar.grid_remove()
                # 调整Treeview的grid配置，添加右边距
                adjusted_padx = (tree_padx[0], tree_padx[1] + no_scrollbar_padx[1]) if tree_padx else no_scrollbar_padx
                treeview.grid_configure(row=tree_row, column=tree_column, sticky=tk.NSEW, padx=adjusted_padx)

        # 绑定滚动条和Treeview
        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=scrollbar_callback)

        # 使用grid布局，确保Treeview和滚动条正确对齐
        treeview.grid(row=tree_row, column=tree_column, sticky=tk.NSEW, padx=tree_padx)
        scrollbar.grid(row=scrollbar_row, column=scrollbar_column, sticky=tk.NS, padx=scrollbar_padx)

        # 配置grid权重，使Treeview可以扩展
        parent_frame.grid_rowconfigure(tree_row, weight=1)
        parent_frame.grid_columnconfigure(tree_column, weight=1)

        # 初始调用一次回调函数，设置初始状态
        scrollbar_callback(0.0, 1.0)

    def create_scrollable_text(self, parent_frame, text_widget, scrollbar, no_scrollbar_padx=(0, 10)):
        """
        创建带自动隐藏滚动条的Text组件，并实现滚动条隐藏时自动调整外边距

        参数:
            parent_frame: Text组件和滚动条的父容器
            text_widget: 要添加滚动条的Text组件
            scrollbar: 滚动条组件
            no_scrollbar_padx: 滚动条隐藏时Text组件的右边距，默认(0, 10)
        """

        # 创建滚动条回调函数，实现自动隐藏和外边距调整
        def scrollbar_callback(*args):
            # 设置滚动条位置
            scrollbar.set(*args)

            # 检查是否需要显示滚动条
            yview = text_widget.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            # 根据是否需要滚动条调整Text组件的右边距
            if need_scrollbar:
                # 显示滚动条
                scrollbar.grid(row=0, column=1, sticky=tk.NS)
                # 调整Text组件的grid配置，移除右边距
                text_widget.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=0)
            else:
                # 隐藏滚动条
                scrollbar.grid_remove()
                # 调整Text组件的grid配置，添加右边距
                text_widget.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=no_scrollbar_padx)

        # 绑定滚动条和Text组件
        scrollbar.config(command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar_callback)

        # 使用grid布局，确保Text组件和滚动条正确对齐
        text_widget.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 配置grid权重，使Text组件可以扩展
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)

        # 初始调用一次回调函数，设置初始状态
        scrollbar_callback(0.0, 1.0)

    def create_ipv4_info_section(self):
        """创建IPv4地址信息查询功能界面"""
        # 在ipv4_info_frame中增加中间容器
        content_container = ttk.Frame(self.ipv4_info_frame, padding="10")
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建输入区域
        input_frame = ttk.LabelFrame(content_container, text="IPv4地址信息查询", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # IP地址输入 - 使用Combobox，支持下拉选择和记忆功能
        ttk.Label(input_frame, text="IPv4地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_info_entry = ttk.Combobox(input_frame, values=self.ipv4_history, width=21, font=("微软雅黑", 10))
        self.ip_info_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.ip_info_entry.insert(0, "192.168.1.1")
        self.ip_info_entry.config(state="normal")  # 允许手动输入
        
        # IPv4地址验证函数
        def validate_ipv4(text):
            """验证IPv4地址格式"""
            text = text.strip()
            # IPv4地址正则表达式 - 修复了点号匹配问题，使用\.转义点号
            ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            is_valid = bool(re.match(ipv4_pattern, text)) if text else True
            # 设置文本颜色
            self.ip_info_entry.config(foreground='black' if is_valid else 'red')
            # 始终返回"1"，允许所有输入，只做视觉提示
            return "1"
        
        # 配置验证
        self.ip_info_entry.config(validate="all", validatecommand=(self.ip_info_entry.register(validate_ipv4), "%P"))
        
        # 初始验证一次
        validate_ipv4(self.ip_info_entry.get())

        # 常用子网掩码与CIDR的映射关系，包含所有CIDR 1~32
        self.subnet_mask_cidr_map = {
            "128.0.0.0": "1",
            "192.0.0.0": "2",
            "224.0.0.0": "3",
            "240.0.0.0": "4",
            "248.0.0.0": "5",
            "252.0.0.0": "6",
            "254.0.0.0": "7",
            "255.0.0.0": "8",
            "255.128.0.0": "9",
            "255.192.0.0": "10",
            "255.224.0.0": "11",
            "255.240.0.0": "12",
            "255.248.0.0": "13",
            "255.252.0.0": "14",
            "255.254.0.0": "15",
            "255.255.0.0": "16",
            "255.255.128.0": "17",
            "255.255.192.0": "18",
            "255.255.224.0": "19",
            "255.255.240.0": "20",
            "255.255.248.0": "21",
            "255.255.252.0": "22",
            "255.255.254.0": "23",
            "255.255.255.0": "24",
            "255.255.255.128": "25",
            "255.255.255.192": "26",
            "255.255.255.224": "27",
            "255.255.255.240": "28",
            "255.255.255.248": "29",
            "255.255.255.252": "30",
            "255.255.255.254": "31",
            "255.255.255.255": "32",
        }

        # 创建反向映射，用于从CIDR获取子网掩码
        self.cidr_subnet_mask_map = {v: k for k, v in self.subnet_mask_cidr_map.items()}

        # 子网掩码下拉列表
        ttk.Label(input_frame, text="子网掩码:").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_mask_var = tk.StringVar()
        self.ip_mask_combobox = ttk.Combobox(
            input_frame, textvariable=self.ip_mask_var, width=15, state="readonly", font=("微软雅黑", 10)
        )
        self.ip_mask_combobox['values'] = list(self.subnet_mask_cidr_map.keys())
        self.ip_mask_combobox.current(list(self.subnet_mask_cidr_map.keys()).index("255.255.255.0"))
        self.ip_mask_combobox.pack(side=tk.LEFT, padx=(0, 10))
        # 绑定子网掩码选择事件
        self.ip_mask_combobox.bind("<<ComboboxSelected>>", self.on_subnet_mask_change)

        # CIDR下拉列表
        ttk.Label(input_frame, text="CIDR:").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_cidr_var = tk.StringVar()
        self.ip_cidr_combobox = ttk.Combobox(
            input_frame, textvariable=self.ip_cidr_var, width=3, state="readonly", font=("微软雅黑", 10)
        )
        self.ip_cidr_combobox['values'] = list(range(1, 33))
        self.ip_cidr_combobox.current(23)  # 默认选择24
        self.ip_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))
        # 绑定CIDR选择事件
        self.ip_cidr_combobox.bind("<<ComboboxSelected>>", self.on_cidr_change)

        self.ip_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv4_info)
        self.ip_info_btn.pack(side=tk.RIGHT)

        # 创建结果区域
        result_frame = ttk.LabelFrame(content_container, text="查询结果", padding=(10, 10, 0, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview和垂直滚动条
        self.ip_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        # 添加右键复制功能
        self.bind_treeview_right_click(self.ip_info_tree)
        self.ip_info_tree.heading("item", text="项目")
        self.ip_info_tree.heading("value", text="值")

        self.ip_info_tree.column("item", width=100)
        self.ip_info_tree.column("value", width=350)

        # 添加垂直滚动条
        ip_info_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)
        ip_info_scrollbar.config(command=self.ip_info_tree.yview)

        # 创建滚动条回调函数，实现自动隐藏和外边距调整
        def scrollbar_callback(*args):
            # 设置滚动条位置
            ip_info_scrollbar.set(*args)

            # 检查是否需要显示滚动条
            yview = self.ip_info_tree.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            # 根据是否需要滚动条调整Treeview的右边距
            if need_scrollbar:
                # 显示滚动条
                ip_info_scrollbar.grid(row=0, column=1, sticky=tk.NS)
                # 调整Treeview的grid配置，移除右边距
                self.ip_info_tree.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=0)
            else:
                # 隐藏滚动条
                ip_info_scrollbar.grid_remove()
                # 调整Treeview的grid配置，添加右边距
                self.ip_info_tree.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=(0, 10))

        self.ip_info_tree.config(yscrollcommand=scrollbar_callback)

        # 使用grid布局，确保Treeview和滚动条正确对齐
        self.ip_info_tree.grid(row=0, column=0, sticky=tk.NSEW)
        ip_info_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 配置grid权重，使Treeview可以扩展
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        # 初始调用一次回调函数，设置初始状态
        scrollbar_callback(0.0, 1.0)

        self.configure_treeview_styles(self.ip_info_tree, include_special_tags=True)

    def create_subnet_overlap_section(self):
        """创建子网重叠检测功能界面"""
        # 在overlap_frame中增加中间容器，内边距10
        content_container = ttk.Frame(self.overlap_frame, padding="10")
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建输入区域
        input_frame = ttk.LabelFrame(content_container, text="子网列表", padding=(10, 10, 0, 10))
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # 子网输入文本框和滚动条
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill=tk.BOTH, expand=False)

        self.overlap_text = tk.Text(text_frame, height=10, width=60, font=("微软雅黑", 10))
        self.overlap_text.insert(tk.END, "192.168.0.0/24\n192.168.0.128/25\n10.0.0.0/16\n10.0.0.128/25\n10.0.10.0/20\n10.10.0.0/23")

        # 添加垂直滚动条，并使用通用方法创建带自动隐藏滚动条的Text组件
        overlap_text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)

        # 使用通用方法创建带自动隐藏滚动条的Text组件
        self.create_scrollable_text(text_frame, self.overlap_text, overlap_text_scrollbar)

        # 直接创建检测重叠按钮 - 靠右放置
        self.overlap_btn = ttk.Button(input_frame, text="检测重叠", command=self.execute_check_overlap)
        self.overlap_btn.pack(side=tk.RIGHT, pady=(5, 0), padx=(0, 10))

        # 创建结果区域
        result_frame = ttk.LabelFrame(content_container, text="检测结果", padding=(10, 10, 0, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.overlap_result_tree = ttk.Treeview(result_frame, columns=("status", "message"), show="headings", height=5)
        # 添加右键复制功能
        self.bind_treeview_right_click(self.overlap_result_tree)
        self.overlap_result_tree.heading("status", text="状态")
        self.overlap_result_tree.heading("message", text="描述")

        self.overlap_result_tree.column("status", width=50)
        self.overlap_result_tree.column("message", width=450)

        # 添加垂直滚动条
        overlap_result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)

        # 使用通用方法创建带自动隐藏滚动条的Treeview
        self.create_scrollable_treeview(result_frame, self.overlap_result_tree, overlap_result_scrollbar)

        self.configure_treeview_styles(self.overlap_result_tree)

    def execute_merge_subnets(self):
        """执行子网合并操作"""
        try:
            # 清空结果树
            for item in self.merge_result_tree.get_children():
                self.merge_result_tree.delete(item)

            # 重新初始化表格结构为正常表格（非转置）
            # 清除所有列
            for col in self.merge_result_tree["columns"]:
                self.merge_result_tree.heading(col, text="")
            self.merge_result_tree.config(columns=())

            # 创建正常的列结构：每列代表一个属性
            columns = ["CIDR", "网络地址", "子网掩码", "广播地址", "主机数"]
            self.merge_result_tree.config(columns=columns)

            # 设置列标题和宽度
            for i, col in enumerate(columns):
                self.merge_result_tree.heading(col, text=col)
                if i == 0:  # CIDR列
                    self.merge_result_tree.column(col, minwidth=110, stretch=True)
                elif i == 1:  # 网络地址列
                    self.merge_result_tree.column(col, minwidth=100, stretch=True)
                elif i == 2:  # 子网掩码列
                    self.merge_result_tree.column(col, minwidth=120, stretch=True)
                elif i == 3:  # 广播地址列
                    self.merge_result_tree.column(col, minwidth=100, stretch=True)
                elif i == 4:  # 主机数列
                    self.merge_result_tree.column(col, minwidth=60, stretch=True)

            # 重新绑定滚动条，保持自动隐藏功能
            if hasattr(self, 'merge_result_scrollbar'):
                # 重新调用create_scrollable_treeview方法来重新绑定滚动条
                self.create_scrollable_treeview(
                    self.merge_result_frame, 
                    self.merge_result_tree, 
                    self.merge_result_scrollbar
                )

            # 获取输入的子网合并列表
            subnets_text = self.subnet_merge_text.get(1.0, tk.END).strip()
            if not subnets_text:
                self.show_info("提示", "请输入子网合并列表")
                return

            # 解析子网合并列表
            subnets = [line.strip() for line in subnets_text.splitlines() if line.strip()]

            # 执行合并
            result = merge_subnets(subnets)

            # 检查是否有错误
            if isinstance(result, dict) and "error" in result:
                self.show_info("错误", result["error"])
                return

            # 显示结果
            merged_subnets = result.get("merged_subnets", [])

            # 如果没有结果，直接返回
            if not merged_subnets:
                return

            # 填充正常表格数据：每行显示一个合并后的子网
            row_index = 0
            for subnet in merged_subnets:
                info = get_subnet_info(subnet)
                row_values = [
                    subnet,  # CIDR
                    info["network"],  # 网络地址
                    info["netmask"],  # 子网掩码
                    info["broadcast"],  # 广播地址
                    info["usable_addresses"],  # 可用主机数
                ]
                tag = "odd" if row_index % 2 == 0 else "even"
                self.merge_result_tree.insert("", tk.END, values=row_values, tags=(tag,))
                row_index += 1
            
            # 操作成功完成，添加到历史记录
            self.update_range_start_history()
            self.update_range_end_history()

        except ValueError as e:
            self.show_info("错误", f"合并失败: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info("错误", f"操作失败: {str(e)}")

    def execute_ipv6_info(self):
        """执行IPv6地址信息查询"""
        try:
            for item in self.ipv6_info_tree.get_children():
                self.ipv6_info_tree.delete(item)

            ipv6_full = self.ipv6_info_entry.get().strip()
            if not ipv6_full:
                self.show_info("提示", "请输入IPv6地址")
                return

            # 移除CIDR前缀，获取纯IPv6地址
            ipv6 = ipv6_full.split('/')[0]
            cidr = self.ipv6_cidr_var.get()
            
            # 验证IPv6地址格式
            try:
                import ipaddress
                ipaddress.IPv6Address(ipv6)
            except ValueError as e:
                # 使用handle_ip_subnet_error函数获取友好的中文错误信息
                from ip_subnet_calculator import handle_ip_subnet_error
                error_info = handle_ip_subnet_error(e, "IP地址验证")
                self.show_info("错误", error_info["error"])
                return

            network_str = f"{ipv6}/{cidr}"

            ipv6_info = get_ip_info(network_str)
            original_ip_info = get_ip_info(ipv6)

            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("ip_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("IP版本", ipv6_info.get("version", "")))
            ip_address = ipv6_info.get("ip_address", "")
            address_type = "未知"
            if ipv6_info.get("is_loopback"):
                address_type = "回环地址"
            elif ipv6_info.get("is_unspecified"):
                address_type = "未指定地址"
            elif ipv6_info.get("is_multicast"):
                address_type = "组播地址"
            elif ipv6_info.get("is_link_local"):
                address_type = "链路本地单播地址"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                address_type = "唯一本地单播地址 (ULA)"
            elif ip_address.startswith("2001:0db8:"):
                address_type = "文档/测试地址"
            elif ip_address.startswith("2000:"):
                address_type = "全球单播地址"
            elif "::ffff:" in ip_address:
                address_type = "IPv4映射的IPv6地址"
            self.ipv6_info_tree.insert("", tk.END, values=("地址类型", address_type))
            self.ipv6_info_tree.insert("", tk.END, values=("CIDR前缀", ipv6_info.get("cidr", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("前缀长度", ipv6_info.get("prefix_length", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("网络地址", ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("广播地址", ipv6_info.get("broadcast_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("第一个可用主机", ipv6_info.get("first_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("最后一个可用主机", ipv6_info.get("last_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("总主机数", ipv6_info.get("total_hosts", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("可用主机数", ipv6_info.get("usable_hosts", "")))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址格式", ""), tags=("section",))
            self.ipv6_info_tree.insert("", tk.END, values=("压缩格式", ipv6_info.get("compressed", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("展开格式", ipv6_info.get("exploded", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("反向DNS格式", ipv6_info.get("reverse_dns", "")))

            if "::ffff:" in ip_address:
                ipv4_part = ip_address.split("::ffff:")[-1]
                self.ipv6_info_tree.insert("", tk.END, values=("映射的IPv4地址", ipv4_part))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址属性", ""), tags=("section",))
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否全局可路由", "是" if ipv6_info.get("is_global") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否私有地址", "是" if ipv6_info.get("is_private") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否链路本地", "是" if ipv6_info.get("is_link_local") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否回环地址", "是" if ipv6_info.get("is_loopback") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否组播地址", "是" if ipv6_info.get("is_multicast") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否未指定地址", "是" if ipv6_info.get("is_unspecified") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否保留地址", "是" if ipv6_info.get("is_reserved") else "否")
            )
            self.ipv6_info_tree.insert("", tk.END, values=("是否IPv4映射", "是" if "::ffff:" in ip_address else "否"))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址结构分析", ""), tags=("section",))

            prefix_analysis = ""
            if ipv6_info.get("is_multicast"):
                prefix_analysis = "多播地址前缀"
                if ip_address.startswith("ff01:"):
                    prefix_analysis += " (接口本地多播)"
                elif ip_address.startswith("ff02:"):
                    prefix_analysis += " (链路本地多播)"
                elif ip_address.startswith("ff05:"):
                    prefix_analysis += " (站点本地多播)"
                elif ip_address.startswith("ff0e:"):
                    prefix_analysis += " (全球多播)"
                else:
                    prefix_analysis += " (其他多播类型)"
            elif ip_address.startswith("fe80:"):
                prefix_analysis = "链路本地前缀 (fe80::/10)"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                prefix_analysis = "唯一本地地址前缀 (fc00::/7)"
            elif ip_address.startswith("2000:") or ip_address.startswith("2001:") or ip_address.startswith("2002:"):
                prefix_analysis = "全球单播地址前缀 (2000::/3)"
            elif ip_address.startswith("::ffff:"):
                prefix_analysis = "IPv4映射地址前缀 (::ffff:0:0/96)"
            elif ip_address.startswith("64:ff9b::"):
                prefix_analysis = "IPv4/IPv6转换地址前缀 (64:ff9b::/96)"
            elif ip_address.startswith("2001:db8::"):
                prefix_analysis = "文档地址前缀 (2001:db8::/32)"
            elif ip_address == "::1":
                prefix_analysis = "回环地址 (::1/128)"
            elif ip_address == "::":
                prefix_analysis = "未指定地址 (::/128)"
            elif ip_address.startswith("100::"):
                prefix_analysis = "黑洞地址前缀 (100::/64)"
            elif ip_address.startswith("2001:10::"):
                prefix_analysis = "ORCHID地址前缀 (2001:10::/28)"
            elif ip_address.startswith("fec0:"):
                prefix_analysis = "站点本地地址前缀 (已弃用)"
            else:
                if ipv6_info.get("is_global"):
                    prefix_analysis = "全球单播地址前缀"
                elif ipv6_info.get("is_private"):
                    prefix_analysis = "私有地址前缀"
                elif ipv6_info.get("is_link_local"):
                    prefix_analysis = "链路本地地址前缀"
                else:
                    prefix_analysis = "未知地址前缀"
            user_cidr = ipv6_info.get("prefix_length", ipv6_info.get("cidr", 128))

            full_prefix_analysis = f"{prefix_analysis}，网络前缀：/{user_cidr}"
            self.ipv6_info_tree.insert("", tk.END, values=("前缀分析", full_prefix_analysis))

            # 使用原始IP地址的展开格式计算段数（总是8段）
            original_segments = original_ip_info.get("exploded", "").split(":")
            if len(original_segments) > 1:
                self.ipv6_info_tree.insert("", tk.END, values=("地址段数量", f"{len(original_segments)}"))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("二进制表示", ""), tags=("section",))
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("binary", "")))

            if ipv6_info.get("subnet_mask"):
                subnet_mask = ipv6_info["subnet_mask"]
                subnet_bin = subnet_mask.replace(':', '').zfill(32)
                subnet_bin_grouped = ' '.join([subnet_bin[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", subnet_bin_grouped))

            if ipv6_info.get("network_address"):
                network_addr = ipv6_info["network_address"]
                network_bin = network_addr.replace(':', '').zfill(32)
                network_bin_grouped = ' '.join([network_bin[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("网络地址", network_bin_grouped))

            if ipv6_info.get("broadcast_address"):
                broadcast_addr = ipv6_info["broadcast_address"]
                broadcast_bin = broadcast_addr.replace(':', '').zfill(32)
                broadcast_bin_grouped = ' '.join([broadcast_bin[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("广播地址", broadcast_bin_grouped))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("十六进制表示", ""), tags=("section",))
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("hexadecimal", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("网络地址", ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("广播地址", ipv6_info.get("broadcast_address", "")))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("十进制数值表示", ""), tags=("section",))
            if "integer" in ipv6_info:
                self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info["integer"]))

            if ipv6_info.get("subnet_mask"):
                subnet_mask = ipv6_info["subnet_mask"]
                subnet_int = int(ipaddress.IPv6Address(subnet_mask))
                self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", subnet_int))

            if ipv6_info.get("network_address"):
                network_addr = ipv6_info["network_address"]
                network_int = int(ipaddress.IPv6Address(network_addr))
                self.ipv6_info_tree.insert("", tk.END, values=("网络地址", network_int))

            if ipv6_info.get("broadcast_address"):
                broadcast_addr = ipv6_info["broadcast_address"]
                broadcast_int = int(ipaddress.IPv6Address(broadcast_addr))
                self.ipv6_info_tree.insert("", tk.END, values=("广播地址", broadcast_int))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址段详情", ""), tags=("section",))
            exploded = original_ip_info.get("exploded", "")
            if exploded:
                segments = exploded.split(":")
            else:
                segments = ["0000"] * 8

            for i, segment in enumerate(segments):
                if segment:
                    dec_value = int(segment, 16)
                    bin_value = f"{dec_value:016b}"
                    self.ipv6_info_tree.insert(
                        "",
                        tk.END,
                        values=(f"第{i + 1}段", f"{segment} (十六进制) = {dec_value} (十进制) = {bin_value} (二进制)"),
                    )
                else:
                    self.ipv6_info_tree.insert(
                        "", tk.END, values=(f"第{i + 1}段", "0000 (十六进制) = 0 (十进制) = 0000000000000000 (二进制)")
                    )

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("网络规模与用途", ""), tags=("section",))

            prefix_length = ipv6_info.get("prefix_length", ipv6_info.get("cidr", 128))
            size_desc = ""
            if prefix_length == 128:
                size_desc = "单主机地址（/128前缀）"
            elif prefix_length == 64:
                size_desc = "小型网络（/64前缀）"
            elif prefix_length == 48:
                size_desc = "中型网络（/48前缀）"
            elif 40 <= prefix_length <= 47:
                size_desc = f"区域级网络（/{prefix_length}前缀）"
            elif 32 < prefix_length <= 39:
                size_desc = f"大型网络（/{prefix_length}前缀）"
            elif prefix_length <= 32:
                size_desc = "超大型网络（/32或更短前缀）"
            else:
                size_desc = f"特殊网络（/{prefix_length}前缀）"
            self.ipv6_info_tree.insert("", tk.END, values=("子网规模", size_desc))

            usage_desc = ""
            if ipv6_info.get("is_loopback"):
                usage_desc = "用于本地主机测试和诊断"
            elif ipv6_info.get("is_link_local"):
                usage_desc = "用于同一链路内的设备通信，无需路由器"
            elif ipv6_info.get("is_multicast"):
                usage_desc = "用于一对多通信，支持组播应用"
            elif "::ffff:" in ip_address:
                usage_desc = "用于在IPv6网络中表示IPv4地址"
            elif ip_address.startswith("64:ff9b::"):
                usage_desc = "用于IPv4/IPv6网络之间的地址转换"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                usage_desc = "用于内部网络通信，不可路由到公网"
            elif ip_address.startswith("2000:") or ip_address.startswith("2001:") or ip_address.startswith("2002:"):
                usage_desc = "可在全球范围内路由，用于公网通信"
            elif ip_address.startswith("2001:db8::"):
                usage_desc = "用于文档示例和教学，不用于实际网络部署"
            elif ip_address.startswith("100::"):
                usage_desc = "用于黑洞路由，丢弃不需要的流量"
            elif ip_address.startswith("2001:10::"):
                usage_desc = "用于ORCHID（Overlay Routable Cryptographic Hash Identifiers）系统"
            elif ip_address == "::":
                usage_desc = "表示未指定地址，通常用于初始启动阶段"
            elif ip_address.startswith("fec0:"):
                usage_desc = "已弃用的站点本地地址，不建议在新网络中使用"
            elif ipv6_info.get("is_global"):
                usage_desc = "可在全球范围内路由，用于公网通信"
            elif ipv6_info.get("is_private"):
                usage_desc = "用于内部网络通信，不可路由到公网"
            else:
                usage_desc = "根据地址类型和前缀规划的特定用途"
            self.ipv6_info_tree.insert("", tk.END, values=("主要用途", usage_desc))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("配置建议", ""), tags=("section",))

            advice = ""
            if ipv6_info.get("is_global"):
                advice = "建议配置防火墙规则，限制不必要的入站访问"
            elif ipv6_info.get("is_private"):
                advice = "建议使用SLAAC或DHCPv6自动分配地址"
            if ipv6_info.get("prefix_length", 0) < 64:
                advice += "\n建议为终端设备分配/64前缀，符合IPv6最佳实践"
            self.ipv6_info_tree.insert("", tk.END, values=("网络配置", advice))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("RFC标准参考", ""), tags=("section",))

            rfc_ref = ""
            if ipv6_info.get("is_multicast"):
                rfc_ref = "RFC 4291, RFC 3306"
            elif ip_address.startswith("fe80:"):
                rfc_ref = "RFC 4291"
            elif ip_address.startswith("fc00:"):
                rfc_ref = "RFC 4193"
            elif ip_address.startswith("2000:"):
                rfc_ref = "RFC 4291, RFC 7454"
            elif "::ffff:" in ip_address:
                rfc_ref = "RFC 4291"
            self.ipv6_info_tree.insert("", tk.END, values=("相关RFC", rfc_ref))

            if ip_address.startswith("::ffff:"):
                ipv4_mapped = ip_address.replace("::ffff:", "")
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=("IPv4映射地址", ipv4_mapped))

            elif ip_address.startswith("2001:0db8:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "文档/测试地址 (RFC 3849)"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 3849 - IPv6文档地址分配"))
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "唯一本地地址 (ULA)"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 4193 - IPv6唯一本地地址"))
            elif ip_address.startswith("fe80:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "链路本地地址"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 4291 - IPv6寻址架构"))
            elif ipv6_info.get("is_multicast"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "组播地址"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 4291 - IPv6寻址架构"))
            
            # 操作成功完成，添加到历史记录
            self.update_ipv6_history()

        except ValueError as e:
            self.show_info("错误", f"查询失败: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info("错误", f"操作失败: {str(e)}")

    def execute_ipv4_info(self):
        """执行IPv4地址信息查询"""
        try:
            for item in self.ip_info_tree.get_children():
                self.ip_info_tree.delete(item)

            ip = self.ip_info_entry.get().strip()
            if not ip:
                self.show_info("提示", "请输入IP地址")
                return
            
            # 验证IPv4地址格式
            try:
                import ipaddress
                ipaddress.IPv4Address(ip)
            except ValueError as e:
                # 使用handle_ip_subnet_error函数获取友好的中文错误信息
                from ip_subnet_calculator import handle_ip_subnet_error
                error_info = handle_ip_subnet_error(e, "IP地址验证")
                self.show_info("错误", error_info["error"])
                return

            subnet_mask = self.ip_mask_var.get()
            cidr = self.ip_cidr_var.get()

            network_str = None
            if cidr:
                try:
                    network_str = f"{ip}/{cidr}"
                except (ValueError, TypeError):
                    pass

            if not network_str and subnet_mask:
                try:
                    mask_int = ip_to_int(subnet_mask)
                    prefix_len = bin(mask_int).count('1')
                    network_str = f"{ip}/{prefix_len}"
                except (ValueError, TypeError):
                    pass

            basic_info = True
            subnet_info = None

            if network_str:
                try:
                    subnet_info = get_subnet_info(network_str)
                    basic_info = False
                except (ValueError, TypeError):
                    pass

            info = get_ip_info(ip)

            if not basic_info and subnet_info:
                self.ip_info_tree.insert("", tk.END, values=("IP地址", ip))
                self.ip_info_tree.insert("", tk.END, values=("子网掩码", subnet_info["netmask"]))
                wildcard_mask = '.'.join(str(255 - int(octet)) for octet in subnet_info["netmask"].split('.'))
                self.ip_info_tree.insert("", tk.END, values=("通配符掩码", wildcard_mask))
                self.ip_info_tree.insert("", tk.END, values=("CIDR", subnet_info["cidr"]))
                self.ip_info_tree.insert("", tk.END, values=("网络类别", info.get("class", "") + "类"))
                self.ip_info_tree.insert("", tk.END, values=("默认子网掩码", info.get("default_netmask", "")))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("地址范围", ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=("网络地址", subnet_info["network"]))
                self.ip_info_tree.insert("", tk.END, values=("广播地址", subnet_info["broadcast"]))
                self.ip_info_tree.insert("", tk.END, values=("第一个可用地址", subnet_info["host_range_start"]))
                self.ip_info_tree.insert("", tk.END, values=("最后一个可用地址", subnet_info["host_range_end"]))
                self.ip_info_tree.insert("", tk.END, values=("可用主机数", subnet_info["usable_addresses"]))
                self.ip_info_tree.insert("", tk.END, values=("总主机数", subnet_info["num_addresses"]))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("二进制表示", ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info["binary"]))
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=("子网掩码", '.'.join(f'{int(octet):08b}' for octet in subnet_info["netmask"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(
                        "通配符掩码",
                        '.'.join(f'{255 - int(octet):08b}' for octet in subnet_info["netmask"].split('.')),
                    ),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=("网络地址", '.'.join(f'{int(octet):08b}' for octet in subnet_info["network"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=("广播地址", '.'.join(f'{int(octet):08b}' for octet in subnet_info["broadcast"].split('.'))),
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("十六进制表示", ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info["hexadecimal"]))
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=("子网掩码", '.'.join(f'{int(octet):02x}' for octet in subnet_info["netmask"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(
                        "通配符掩码",
                        '.'.join(f'{255 - int(octet):02x}' for octet in subnet_info["netmask"].split('.')),
                    ),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=("网络地址", '.'.join(f'{int(octet):02x}' for octet in subnet_info["network"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=("广播地址", '.'.join(f'{int(octet):02x}' for octet in subnet_info["broadcast"].split('.'))),
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("十进制数值表示", ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info["integer"]))
                self.ip_info_tree.insert("", tk.END, values=("子网掩码", str(ip_to_int(subnet_info["netmask"]))))
                wildcard_int = ip_to_int('.'.join(str(255 - int(octet)) for octet in subnet_info["netmask"].split('.')))
                self.ip_info_tree.insert("", tk.END, values=("通配符掩码", str(wildcard_int)))
                self.ip_info_tree.insert("", tk.END, values=("网络地址", str(ip_to_int(subnet_info["network"]))))
                self.ip_info_tree.insert("", tk.END, values=("广播地址", str(ip_to_int(subnet_info["broadcast"]))))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("IP属性", ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=("IP版本", info["version"]))
                self.ip_info_tree.insert("", tk.END, values=("是否私有IP", "是" if info["is_private"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否保留IP", "是" if info["is_reserved"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否回环地址", "是" if info["is_loopback"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否组播地址", "是" if info["is_multicast"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否全局可路由", "是" if info["is_global"] else "否"))
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否链路本地地址", "是" if info["is_link_local"] else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否未指定地址", "是" if info["is_unspecified"] else "否")
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))

                ip_purpose = ""
                if info["is_loopback"]:
                    ip_purpose = "本地回环地址，用于测试本地网络"
                elif info["is_private"]:
                    ip_purpose = "私有地址，用于内部网络"
                elif info["is_multicast"]:
                    ip_purpose = "组播地址，用于一对多通信"
                elif info["is_reserved"]:
                    ip_purpose = "保留地址，用于特殊用途"
                elif info["is_global"]:
                    ip_purpose = "全球可路由地址，用于公网通信"
                else:
                    ip_purpose = "未知用途"
                self.ip_info_tree.insert("", tk.END, values=("IP地址用途", ip_purpose))

                subnet_size = subnet_info["usable_addresses"]
                size_desc = ""
                if subnet_size <= 254:
                    size_desc = "小型网络，适合家庭或小型办公室"
                elif subnet_size <= 65534:
                    size_desc = "中型网络，适合企业或校园网络"
                else:
                    size_desc = "大型网络，适合大型机构或运营商"
                self.ip_info_tree.insert("", tk.END, values=("子网规模", size_desc))

                config_advice = ""
                if subnet_size > 65534:
                    config_advice = "建议划分为多个子网，便于管理和减少广播域"
                elif info["is_private"]:
                    config_advice = "建议使用DHCP服务器自动分配IP地址"
                else:
                    config_advice = "建议配置静态路由和防火墙规则"
                self.ip_info_tree.insert("", tk.END, values=("配置建议", config_advice))
            else:
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info.get("ip_address", ip)))
                self.ip_info_tree.insert("", tk.END, values=("IP版本", info.get("version", "")))
                self.ip_info_tree.insert("", tk.END, values=("网络类别", info.get("class", "") + "类"))
                self.ip_info_tree.insert("", tk.END, values=("默认子网掩码", info.get("default_netmask", "")))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("数值表示", ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=("二进制表示", info.get("binary", "")))
                self.ip_info_tree.insert("", tk.END, values=("十六进制表示", info.get("hexadecimal", "")))
                self.ip_info_tree.insert("", tk.END, values=("整数表示", info.get("integer", "")))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("IP属性", ""), tags=("section",))
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否私有IP", "是" if info.get("is_private", False) else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否保留IP", "是" if info.get("is_reserved", False) else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否回环地址", "是" if info.get("is_loopback", False) else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否组播地址", "是" if info.get("is_multicast", False) else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否全局可路由", "是" if info.get("is_global", False) else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否链路本地地址", "是" if info.get("is_link_local", False) else "否")
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=("是否未指定地址", "是" if info.get("is_unspecified", False) else "否")
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("扩展信息", ""), tags=("section",))

                ip_purpose = ""
                if info.get("is_loopback", False):
                    ip_purpose = "本地回环地址，用于测试本地网络"
                elif info.get("is_private", False):
                    ip_purpose = "私有地址，用于内部网络"
                elif info.get("is_multicast", False):
                    ip_purpose = "组播地址，用于一对多通信"
                elif info.get("is_reserved", False):
                    ip_purpose = "保留地址，用于特殊用途"
                elif info.get("is_global", False):
                    ip_purpose = "全球可路由地址，用于公网通信"
                else:
                    ip_purpose = "未知用途"
                self.ip_info_tree.insert("", tk.END, values=("IP地址用途", ip_purpose))

                config_advice = ""
                if info.get("is_private", False):
                    config_advice = "建议使用DHCP服务器自动分配IP地址"
                else:
                    config_advice = "建议配置静态路由和防火墙规则"
                self.ip_info_tree.insert("", tk.END, values=("配置建议", config_advice))
            
            # 操作成功完成，添加到历史记录
            self.update_ipv4_history()

        except ValueError as e:
            self.show_info("错误", f"查询失败: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info("错误", f"操作失败: {str(e)}")

    def execute_range_to_cidr(self):
        """执行IP地址范围转CIDR操作"""
        try:
            # 清空结果树
            for item in self.merge_result_tree.get_children():
                self.merge_result_tree.delete(item)

            # 获取输入的IP范围
            start_ip = self.range_start_entry.get().strip()
            end_ip = self.range_end_entry.get().strip()

            if not start_ip or not end_ip:
                self.show_info("提示", "请输入完整的IP范围")
                return

            # 执行转换
            result = range_to_cidr(start_ip, end_ip)

            # 检查是否有错误
            if isinstance(result, dict) and "error" in result:
                self.show_info("错误", result["error"])
                return

            # 显示结果
            cidr_list = result.get("cidr_list", [])

            # 转置表格：清空并重新创建列
            for item in self.merge_result_tree.get_children():
                self.merge_result_tree.delete(item)

            # 清除所有列
            for col in self.merge_result_tree["columns"]:
                self.merge_result_tree.heading(col, text="")
            self.merge_result_tree.config(columns=())

            # 如果没有结果，直接返回
            if not cidr_list:
                return

            # 创建转置后的列：第一列为属性名称，后续每列为一个CIDR
            columns = ["属性"] + cidr_list
            self.merge_result_tree.config(columns=columns)

            # 设置列标题和宽度
            for i, col in enumerate(columns):
                self.merge_result_tree.heading(col, text=col)
                if i == 0:  # 第一列（属性列）
                    self.merge_result_tree.column(col, width=90, minwidth=90, stretch=False)  # 增大一半并固定
                else:  # 其他列
                    self.merge_result_tree.column(col, width=120)

            # 重新绑定滚动条，保持自动隐藏功能
            if hasattr(self, 'merge_result_scrollbar'):
                # 重新调用create_scrollable_treeview方法来重新绑定滚动条
                self.create_scrollable_treeview(
                    self.merge_result_frame, 
                    self.merge_result_tree, 
                    self.merge_result_scrollbar
                )

            # 定义要显示的属性列表
            properties = [
                ("CIDR", lambda info, cidr: cidr),
                ("网络地址", lambda info, cidr: info["network"]),
                ("子网掩码", lambda info, cidr: info["netmask"]),
                ("广播地址", lambda info, cidr: info["broadcast"]),
                ("可用主机数", lambda info, cidr: info["usable_addresses"]),
            ]

            # 填充转置后的数据
            row_index = 0
            for prop_name, prop_func in properties:
                row_values = [prop_name]
                for cidr in cidr_list:
                    info = get_subnet_info(cidr)
                    row_values.append(prop_func(info, cidr))
                tag = "odd" if row_index % 2 == 0 else "even"
                self.merge_result_tree.insert("", tk.END, values=row_values, tags=(tag,))
                row_index += 1
            
            # 操作成功完成，添加到历史记录
            self.update_range_start_history()
            self.update_range_end_history()

        except ValueError as e:
            self.show_info("错误", f"转换失败: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info("错误", f"操作失败: {str(e)}")

    def execute_check_overlap(self):
        """执行子网重叠检测操作"""
        try:
            # 清空结果树
            for item in self.overlap_result_tree.get_children():
                self.overlap_result_tree.delete(item)

            # 获取输入的子网列表
            subnets_text = self.overlap_text.get(1.0, tk.END).strip()
            if not subnets_text:
                self.show_info("提示", "请输入子网列表")
                return

            # 解析子网列表
            subnets = [line.strip() for line in subnets_text.splitlines() if line.strip()]

            # 执行重叠检测
            result = check_subnet_overlap(subnets)

            # 检查是否有错误
            if isinstance(result, dict) and "error" in result:
                self.show_info("错误", result["error"])
                return

            # 显示结果
            overlaps = result.get("overlaps", [])
            row_index = 0

            # 如果没有重叠，显示无重叠信息
            if not overlaps:
                tag = "odd" if row_index % 2 == 0 else "even"
                self.overlap_result_tree.insert("", tk.END, values=("无", "未检测到子网重叠"), tags=(tag,))
            else:
                # 显示所有重叠信息
                for overlap in overlaps:
                    status = "重叠"
                    description = f"{overlap['subnet1']} 与 {overlap['subnet2']} ({overlap['type']})"
                    tag = "odd" if row_index % 2 == 0 else "even"
                    self.overlap_result_tree.insert("", tk.END, values=(status, description), tags=(tag,))
                    row_index += 1

        except (ValueError, tk.TclError, AttributeError, TypeError) as e:
            self.show_info("错误", f"执行子网重叠检测失败: {str(e)}")

    def update_ipv4_history(self, _event=None):
        """更新IPv4地址查询历史记录"""
        ip_value = self.ip_info_entry.get().strip()
        if ip_value and ip_value not in self.ipv4_history:
            # 将新地址添加到历史记录开头
            self.ipv4_history.insert(0, ip_value)
            # 限制历史记录数量为10条
            if len(self.ipv4_history) > 10:
                self.ipv4_history.pop()
            # 更新Combobox的values属性
            self.ip_info_entry['values'] = self.ipv4_history

    def update_ipv6_history(self, _event=None):
        """更新IPv6地址查询历史记录"""
        ipv6_value = self.ipv6_info_entry.get().strip()
        if ipv6_value and ipv6_value not in self.ipv6_history:
            # 将新地址添加到历史记录开头
            self.ipv6_history.insert(0, ipv6_value)
            # 限制历史记录数量为10条
            if len(self.ipv6_history) > 10:
                self.ipv6_history.pop()
            # 更新Combobox的values属性
            self.ipv6_info_entry['values'] = self.ipv6_history

    def update_range_start_history(self, _event=None):
        """更新IP范围起始地址历史记录"""
        start_value = self.range_start_entry.get().strip()
        if start_value and start_value not in self.range_start_history:
            # 将新地址添加到历史记录开头
            self.range_start_history.insert(0, start_value)
            # 限制历史记录数量为10条
            if len(self.range_start_history) > 10:
                self.range_start_history.pop()
            # 更新Combobox的values属性
            self.range_start_entry['values'] = self.range_start_history

    def update_range_end_history(self, _event=None):
        """更新IP范围结束地址历史记录"""
        end_value = self.range_end_entry.get().strip()
        if end_value and end_value not in self.range_end_history:
            # 将新地址添加到历史记录开头
            self.range_end_history.insert(0, end_value)
            # 限制历史记录数量为10条
            if len(self.range_end_history) > 10:
                self.range_end_history.pop()
            # 更新Combobox的values属性
            self.range_end_entry['values'] = self.range_end_history

    def on_subnet_mask_change(self, _event):
        """当子网掩码改变时，更新CIDR值"""
        selected_mask = self.ip_mask_var.get()
        if selected_mask in self.subnet_mask_cidr_map:
            cidr = self.subnet_mask_cidr_map[selected_mask]
            self.ip_cidr_var.set(cidr)

    def on_cidr_change(self, _event):
        """当CIDR改变时，更新子网掩码值"""
        selected_cidr = self.ip_cidr_var.get()
        if selected_cidr in self.cidr_subnet_mask_map:
            subnet_mask = self.cidr_subnet_mask_map[selected_cidr]
            self.ip_mask_var.set(subnet_mask)

    def toggle_test_info_bar(self, _event=None):
        """打开功能调试对话框（彩蛋功能）
        快捷键：Ctrl+Shift+I
        """
        # 创建功能调试对话框
        test_dialog = tk.Toplevel(self.root)
        test_dialog.title("功能调试")
        test_dialog.resizable(False, False)  # 固定对话框大小，不可调节
        test_dialog.transient(self.root)

        # 计算对话框居中显示的位置（相对于主窗口）
        dialog_width = 400
        dialog_height = 450  # 增加对话框高度，确保主题切换控件能显示完整

        # 获取主窗口的位置和大小
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # 计算对话框居中位置
        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2

        # 设置对话框大小和位置
        test_dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")

        # 创建对话框内容框架
        content_frame = ttk.Frame(test_dialog, padding="15")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 使用grid布局管理器来精确控制各个组件的位置
        content_frame.grid_rowconfigure(0, weight=0)  # 标题行不扩展
        content_frame.grid_rowconfigure(1, weight=0)  # 说明行不扩展
        content_frame.grid_rowconfigure(2, weight=1)  # 按钮矩阵行扩展，用于垂直居中
        content_frame.grid_rowconfigure(3, weight=0)  # 主题切换行不扩展
        content_frame.grid_rowconfigure(4, weight=0)  # 关闭按钮行不扩展
        content_frame.grid_columnconfigure(0, weight=1)  # 唯一列扩展

        # 添加标题标签
        title_label = ttk.Label(content_frame, text="功能调试面板", font=("微软雅黑", 12, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        # 添加说明标签
        desc_label = ttk.Label(content_frame, text="点击下方按钮测试不同类型的信息栏显示效果：")
        desc_label.grid(row=1, column=0, pady=(0, 15))

        # 创建按钮框架（使用grid布局实现3x2矩阵）
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=2, column=0, sticky=tk.NS)  # 垂直居中对齐

        # 按钮样式
        button_style = "TButton"
        button_width = 15

        # 第一行按钮
        success_btn = ttk.Button(
            button_frame,
            text="测试正确信息",
            width=button_width,
            style=button_style,
            command=lambda: self.show_result("测试正确信息：操作成功！", error=False),
        )
        success_btn.grid(row=0, column=0, padx=5, pady=5)

        error_btn = ttk.Button(
            button_frame,
            text="测试错误信息",
            width=button_width,
            style=button_style,
            command=lambda: self.show_result("测试错误信息：操作失败！", error=True, keep_data=True),
        )
        error_btn.grid(row=0, column=1, padx=5, pady=5)

        # 第二行按钮
        long_text = "测试长文本信息：这是一条非常长的测试信息，用于测试信息栏的文本截断功能。" * 3
        long_text_btn = ttk.Button(
            button_frame,
            text="测试长文本信息",
            width=button_width,
            style=button_style,
            command=lambda: self.show_result(long_text, error=False),
        )
        long_text_btn.grid(row=1, column=0, padx=5, pady=5)

        # 中英文混排长文本测试按钮
        mixed_text = (
            "中英文混排测试：This is a long text with mixed Chinese and English characters. 这是一条包含中英文混合的长文本，用于测试信息栏的截断功能。"
            * 2
        )
        mixed_text_btn = ttk.Button(
            button_frame,
            text="测试中英文混排",
            width=button_width,
            style=button_style,
            command=lambda: self.show_result(mixed_text, error=False),
        )
        mixed_text_btn.grid(row=1, column=1, padx=5, pady=5)

        # 添加第三行按钮：隐藏信息栏和清空结果
        hide_info_btn = ttk.Button(
            button_frame, text="隐藏信息栏", width=button_width, style=button_style, command=self.hide_info_bar
        )
        hide_info_btn.grid(row=2, column=0, padx=5, pady=5)

        clear_result_btn = ttk.Button(
            button_frame, text="清空子网切分", width=button_width, style=button_style, command=self.clear_result
        )
        clear_result_btn.grid(row=2, column=1, padx=5, pady=5)

        # 主题切换部分
        theme_frame = ttk.LabelFrame(content_frame, text="主题切换", padding="10")
        theme_frame.grid(row=3, column=0, sticky=tk.EW, pady=(15, 10))

        # 配置主题切换框架的列
        theme_frame.grid_columnconfigure(0, weight=0)  # 标签列
        theme_frame.grid_columnconfigure(1, weight=1)  # 下拉列表列
        theme_frame.grid_columnconfigure(2, weight=0)  # 按钮列

        # 主题选择标签
        theme_label = ttk.Label(theme_frame, text="选择主题：")
        theme_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)

        # 获取系统可用的内置主题列表
        theme_list = self.style.theme_names()

        # 创建主题选择下拉列表
        self.theme_var = tk.StringVar(value=self.style.theme_use())  # 设置默认主题为当前使用的主题

        # 创建下拉列表控件
        theme_combobox = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=theme_list, state="readonly")
        theme_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # 主题切换函数
        def switch_theme():
            new_theme = self.theme_var.get()
            try:
                # 使用系统内置主题切换，彻底移除sv-ttk，解决黑色底色问题
                self.style.theme_use(new_theme)
                # 重新配置Treeview样式，确保在新主题下表格线仍然可见
                tree_names = [
                    'split_tree',
                    'remaining_tree',
                    'allocated_tree',
                    'planning_remaining_tree',
                    'pool_tree',
                    'requirements_tree',
                    'history_tree',
                ]
                for tree_name in tree_names:
                    if hasattr(self, tree_name):
                        tree = getattr(self, tree_name)
                        # 检查split_tree是否需要包含特殊标签
                        include_special = tree_name == 'split_tree'
                        self.configure_treeview_styles(tree, include_special)

                # 重新配置信息栏关闭按钮样式，确保在新主题下大小设定仍然生效
                if hasattr(self, 'style'):
                    self.style.configure(
                        "InfoBarCloseButton.TButton",
                        padding=(2, 0),  # 按用户要求统一设置padding为(2, 0)
                        font=("微软雅黑", 8),  # 字体设置为微软雅黑，大小为8
                        foreground="#9E9E9E",
                        width=2,  # 字符宽度，配合padding使用
                    )
            except (tk.TclError, AttributeError) as e:
                print(f"主题切换出错: {e}")
                # 出错时恢复到默认主题
                self.style.theme_use("vista")

        # 创建应用主题按钮
        theme_switch_btn = ttk.Button(
            theme_frame, text="应用主题", width=button_width, style=button_style, command=switch_theme
        )
        theme_switch_btn.grid(row=0, column=2, padx=(10, 0), pady=5)

        # 关闭按钮框架
        close_frame = ttk.Frame(content_frame)
        close_frame.grid(row=4, column=0, sticky=tk.EW, pady=(15, 0))
        close_frame.grid_columnconfigure(0, weight=1)  # 左侧空白区域扩展

        # 添加关闭按钮到右下角
        close_btn = ttk.Button(
            close_frame, text="关闭", width=button_width, style=button_style, command=test_dialog.destroy
        )
        close_btn.grid(row=0, column=1, padx=5)

    def show_result(self, text, error=False, keep_data=False):
        """显示结果

        Args:
            text: 要显示的文本
            error: 是否为错误信息
            keep_data: 是否保留数据
        """
        # 只有在不保留数据且显示错误信息时才清空表格
        if not keep_data and error:
            self.clear_result()

        # 显示在信息栏中
        # 取消之前的自动隐藏定时器
        if self.info_auto_hide_id:
            self.root.after_cancel(self.info_auto_hide_id)
            self.info_auto_hide_id = None

        # 根据信息类型设置样式和图标，使用带框风格，保持一致
        if error:
            label_style = "Error.TLabel"
            frame_style = "ErrorInfoBar.TFrame"
            icon = "❎ "  # 使用明确的带框叉号 (U+274E)
        else:
            label_style = "Success.TLabel"
            frame_style = "SuccessInfoBar.TFrame"
            icon = "✅ "  # 使用带框钩 (U+2705)，与带框叉风格一致

        # 更新信息标签和框架样式

        # 获取信息栏的实际宽度
        # 确保使用一致的宽度计算逻辑，无论是第一次还是第二次显示
        # 始终使用主窗口宽度作为参考，确保第一次和第二次显示时截断一致
        main_window_width = self.root.winfo_width()
        # 使用主窗口宽度的85%作为信息栏宽度，放大截断位置
        info_bar_width = int(main_window_width * 0.96)
        # 确保不小于原始的最小宽度
        info_bar_width = max(info_bar_width, self.MIN_INFO_BAR_WIDTH)

        # 确保info_bar_frame已经添加到父容器中
        if self.info_bar_frame.winfo_manager() == "":
            # 先临时显示，以便获取宽度
            self.info_bar_frame.pack(side="bottom", fill="x", pady=(0, 0), padx=10)

        # 更新窗口，确保能获取到准确的宽度
        self.root.update_idletasks()

        # 设置最大像素宽度（考虑信息栏的实际宽度、关闭按钮宽度和内边距）
        # 可用宽度 = 信息栏宽度 - 内边距 - 关闭按钮宽度
        # 增加内边距减去值，确保能显示更多字符
        max_pixel_width = info_bar_width - 20 - self.CLOSE_BTN_WIDTH  # 减去更小的内边距和关闭按钮宽度

        # 确保最大像素宽度为正数
        max_pixel_width = max(max_pixel_width, self.MIN_PIXEL_WIDTH)

        # 创建字体对象，用于测量文本宽度
        try:
            font = tkfont.Font(family="微软雅黑", size=9)
        except tk.TclError:
            font = tkfont.Font(family="Arial", size=9)

        # 计算字符串的实际像素宽度
        def calculate_pixel_width(text):
            return font.measure(text)

        # 基于像素宽度的截断函数
        def truncate_text_by_pixel(text, icon, max_pixel_width):
            # 计算图标的宽度
            icon_width = calculate_pixel_width(icon)

            # 可用宽度：总宽度减去图标宽度
            available_width = max_pixel_width - icon_width

            # 先尝试显示完整文本（加上图标）
            full_text_with_icon = icon + text
            full_width = calculate_pixel_width(full_text_with_icon)

            # 如果完整文本可以显示，直接返回
            if full_width <= max_pixel_width:
                return text

            # 计算省略号的宽度
            ellipsis_width = calculate_pixel_width("...")

            # 二分查找合适的截断位置，考虑省略号宽度
            low = 0
            high = len(text)
            best_length = 0

            while low <= high:
                mid = (low + high) // 2
                current_text = text[:mid]
                current_width = calculate_pixel_width(current_text)

                if current_width <= available_width - ellipsis_width:
                    best_length = mid
                    low = mid + 1
                else:
                    high = mid - 1

            # 确保截断后的文本不会过长
            truncated = text[:best_length]

            # 调整截断位置，确保加上省略号和图标后不会超过最大宽度
            while best_length > 0:
                truncated = text[:best_length]
                truncated_width = calculate_pixel_width(truncated) + ellipsis_width + icon_width
                if truncated_width <= max_pixel_width:
                    return truncated + "..."
                best_length -= 1

            return "..."

        # 移除文本中的换行符，确保在信息框中单行显示
        text = text.replace('\n', ' ')
        
        # 调用截断函数
        truncated_text = truncate_text_by_pixel(text, icon, max_pixel_width)

        # 显示完整文本（带有图标）
        self.info_label.config(text=icon + truncated_text, style=label_style)
        self.info_bar_frame.configure(style=frame_style)

        # 显示信息栏 - 使用pack布局，放置在main_frame底部

        if self.info_bar_frame.winfo_manager() == "":
            # 放置在main_frame底部
            self.info_bar_frame.pack(side="bottom", fill="x", pady=(0, 0), padx=10)
        else:
            # 如果已经显示，确保布局正确
            self.info_bar_frame.pack_configure(side="bottom", fill="x", pady=(0, 0), padx=10)

        # 去掉自动隐藏功能，需要手动隐藏

    def prepare_chart_data(self, result, split_info, remaining_subnets):
        """准备图表数据"""
        try:
            # 获取父网段信息
            parent_cidr = result.get("parent", "")
            if not parent_cidr:
                self.chart_data = None
                return

            parent_info = get_subnet_info(parent_cidr)
            if "error" in parent_info:
                self.chart_data = None
                return

            parent_start = ip_to_int(parent_info.get("network", "0.0.0.0"))
            parent_end = ip_to_int(parent_info.get("broadcast", "0.0.0.0"))
            parent_range = parent_end - parent_start + 1

            # 准备所有网段数据
            self.chart_data = {
                "parent": {
                    "start": parent_start,
                    "end": parent_end,
                    "range": parent_range,
                    "name": parent_info.get("cidr", parent_cidr),
                    "color": "#f3e5f5",  # 浅紫色背景
                },
                "networks": [],
            }

            # 添加切分网段
            if split_info:
                split_start = ip_to_int(split_info.get("network", "0.0.0.0"))
                split_end = ip_to_int(split_info.get("broadcast", "0.0.0.0"))
                self.chart_data["networks"].append(
                    {
                        "start": split_start,
                        "end": split_end,
                        "range": split_end - split_start + 1,
                        "name": split_info.get("cidr", result.get("split", "")),
                        "color": "#2196f3",  # 现代蓝色
                        "type": "split",
                    }
                )

            # 添加剩余网段 - 使用更现代化的颜色方案
            # 优化：使用元组存储，减少内存分配和提高访问速度
            subnet_colors = (
                "#4caf50",
                "#ff9800",
                "#f44336",
                "#9c27b0",
                "#00bcd4",
                "#795548",
                "#ffeb3b",
                "#607d8b",
            )  # 现代化颜色列表
            # 优化：预先计算颜色数量，避免循环中重复计算
            colors_count = len(subnet_colors)
            
            for index, subnet in enumerate(remaining_subnets):
                subnet_start = ip_to_int(subnet.get("network", "0.0.0.0"))
                subnet_end = ip_to_int(subnet.get("broadcast", "0.0.0.0"))
                self.chart_data["networks"].append(
                    {
                        "start": subnet_start,
                        "end": subnet_end,
                        "range": subnet_end - subnet_start + 1,
                        "name": subnet.get("cidr", ""),
                        "color": subnet_colors[index % colors_count],  # 循环使用颜色
                        "type": "remaining",
                    }
                )

            # 按起始地址排序
            self.chart_data["networks"].sort(key=lambda x: x["start"])
        except (ValueError, TypeError, AttributeError):
            # 如果出现任何错误，就不绘制图表
            self.chart_data = None

    def on_chart_resize(self, _):
        """Canvas尺寸变化时重新绘制图表"""
        # 当Canvas尺寸变化时重新绘制图表
        self.draw_distribution_chart()

    def on_chart_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.chart_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def draw_text_with_stroke(
        self,
        text,
        x,
        y,
        font,
        anchor=tk.W,
        fill="#ffffff",
        stroke_color="#000000",
    ):
        """绘制带描边的文字（使用4方向基础描边，平衡性能和可读性）

        Args:
            text: 要绘制的文字
            x: 起始x坐标
            y: 起始y坐标
            font: 字体设置
            anchor: 文字锚点
            fill: 文字颜色
            stroke_color: 描边颜色
        """
        # 直接使用4方向描边，这是最稳定和清晰的实现方式
        # 4个方向：左上、左下、右上、右下
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        # 绘制描边
        for dx, dy in directions:
            self.chart_canvas.create_text(
                x + dx, y + dy,
                text=text,
                font=font,
                anchor=anchor,
                fill=stroke_color
            )

        # 绘制主文字，覆盖在描边上
        self.chart_canvas.create_text(
            x, y,
            text=text,
            font=font,
            anchor=anchor,
            fill=fill
        )

    def draw_distribution_chart(self):
        """绘制网段分布柱状图 - 参考Web版本的呈现方式"""
        # 检查chart_data属性是否存在且不为None
        if not hasattr(self, 'chart_data') or not self.chart_data:
            return

        try:
            # 清空Canvas
            self.chart_canvas.delete("all")

            # 获取父框架尺寸，确保Canvas宽度不会超过父框架
            parent_width = self.chart_frame.winfo_width()

            # 获取Canvas尺寸
            width = self.chart_canvas.winfo_width()
            canvas_height = self.chart_canvas.winfo_height()

            # 如果Canvas还没有渲染完成，使用默认尺寸
            if width < 10 or width > parent_width:
                width = parent_width - 30  # 使用父框架宽度减去边距
            if canvas_height < 10:
                canvas_height = 400

            # 设置边距（参考Web版布局）
            margin_left = 50
            margin_right = 80
            margin_top = 50

            # 计算可用绘图区域宽度
            chart_width = width - margin_left - margin_right

            # 获取父网段信息
            parent_info = self.chart_data.get("parent", {})
            parent_range = parent_info.get("range", 1)

            # 获取网段列表
            networks = self.chart_data.get("networks", [])
            if not networks:
                # 没有网段时显示提示
                self.chart_canvas.create_text(width / 2, canvas_height / 2, text="无网段数据", font=("微软雅黑", 12))
                return

            # 不绘制主标题，父网段和切分网段同等地位显示

            # 使用对数比例尺来更好显示差距巨大的网段大小（参考Web版算法）
            log_max = math.log10(parent_range)
            log_min = 3  # 最小显示3个数量级（1000个地址）
            min_bar_width = 50  # 小网段的最小显示宽度

            # 柱状图配置 - 调整为更紧凑的显示
            bar_height = 30
            padding = 10
            x = margin_left
            y = margin_top

            # 动态设置Canvas高度
            required_height = (
                y  # 起始位置
                + (bar_height + padding)  # 父网段
                + (bar_height + padding)  # 切分网段
                + 40  # 剩余网段标题
                + (len(networks) * (bar_height + padding))  # 所有剩余网段
                + 80
            )  # 图例和底部边距

            # 确保背景色覆盖整个滚动区域，而不仅仅是初始可见区域
            background_height = max(required_height, canvas_height)
            self.chart_canvas.create_rectangle(0, 0, width, background_height, fill="#333333", outline="", width=0)

            # 获取Canvas的实际宽度，确保scrollregion宽度不超过Canvas宽度
            actual_width = self.chart_canvas.winfo_width()
            if actual_width < 10:
                actual_width = width

            # 设置Canvas滚动区域，确保宽度不超过Canvas实际宽度，只允许垂直滚动
            self.chart_canvas.config(scrollregion=(0, 0, actual_width, background_height))

            # 确保Canvas只允许垂直滚动，不允许水平滚动
            self.chart_canvas.config(xscrollcommand=None)

            # 绘制父网段
            parent_range = parent_info.get("range", 1)
            log_value = max(log_min, math.log10(parent_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)

            # 确保柱状图宽度不会超过可用绘图区域
            bar_width = min(bar_width, chart_width)

            # 绘制父网段条（使用明显的深灰色）
            color = "#636e72"  # 明显的深灰色
            self.chart_canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

            # 绘制父网段信息
            usable_addresses = parent_range - 2 if parent_range > 2 else parent_range

            # 网段信息 - 使用带描边的文字绘制，提高可见度
            parent_cidr = parent_info.get("name", "")  # 从parent_info获取父网段CIDR
            segment_text = f"父网段: {parent_cidr}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = ("微软雅黑", 11, "bold")  # 使用粗体提高可读性
            # 使用带描边的文字绘制方法
            self.draw_text_with_stroke(segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

            # 可用地址数 - 使用带描边的文字绘制，提高可见度
            address_text = f"可用地址数: {usable_addresses:,}"
            text_x = x + 250
            # 使用带描边的文字绘制方法
            self.draw_text_with_stroke(address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

            y += bar_height + padding

            # 绘制切分网段
            split_networks = [net for net in networks if net.get("type") == "split"]
            for i, network in enumerate(split_networks):
                # 使用对数比例尺计算宽度（参考Web版）
                network_range = network.get("range", 1)
                log_value = max(log_min, math.log10(network_range))
                bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)

                # 确保柱状图宽度不会超过可用绘图区域
                bar_width = min(bar_width, chart_width)

                # 绘制切分网段条（明显的蓝色）
                color = "#4a7eb4"  # 明显的蓝色
                self.chart_canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

                # 绘制网段信息（参考Web版布局）
                name = network.get("name", "")
                usable_addresses = network_range - 2 if network_range > 2 else network_range

                # 网段信息 - 使用带描边的文字绘制，提高可见度
                segment_text = f"切分网段: {name}"
                text_x = x + 15
                text_y = y + bar_height / 2
                font = ("微软雅黑", 11, "bold")  # 使用粗体提高可读性
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                # 可用地址数 - 使用带描边的文字绘制，提高可见度
                address_text = f"可用地址数: {usable_addresses:,}"
                text_x = x + 250
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                y += bar_height + padding

                # 添加切分网段和剩余网段之间的虚线分割
                self.chart_canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)

            # 绘制剩余网段标题
            y += 20  # 额外间距
            title_font = ("微软雅黑", 11)  # 调小标题字体
            remaining_count = len([n for n in networks if n.get("type") != "split"])
            self.chart_canvas.create_text(
                x,
                y,
                text=f"剩余网段 ({remaining_count} 个):",
                font=title_font,
                anchor=tk.W,
                fill="#ffffff",
            )
            y += 15

            # 为剩余网段分配高区分度的柔和配色方案
            # 优化：使用元组存储，减少内存分配和提高访问速度
            subnet_colors = (
                "#5e9c6a",
                "#db6679",
                "#f0ab55",
                "#8b6cb8",
                "#5b8fd9",
                "#3c70d8",
                "#e68838",
                "#a04132",
                "#6a9da8",
                "#87c569",
                "#6d8de8",
                "#c16fa0",
                "#a99bc6",
                "#a44d69",
                "#b9d0f8",
                "#5d4ea5",
                "#f5ad8c",
                "#5b8fd9",
                "#db6679",
                "#a6c589",
            )

            # 绘制剩余网段
            remaining_networks = [net for net in networks if net.get("type") != "split"]
            for i, network in enumerate(remaining_networks):
                # 使用对数比例尺计算宽度
                network_range = network.get("range", 1)
                log_value = max(log_min, math.log10(network_range))
                bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)

                # 确保柱状图宽度不会超过可用绘图区域
                bar_width = min(bar_width, chart_width)

                # 为每个剩余网段选择不同颜色（参考Web版）
                color_index = i % len(subnet_colors)
                color = subnet_colors[color_index]

                # 绘制剩余网段条
                self.chart_canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

                # 绘制网段信息
                name = network.get("name", "")
                usable_addresses = network_range - 2 if network_range > 2 else network_range

                # 网段信息 - 使用带描边的文字绘制，提高可见度
                segment_text = f"网段 {i + 1}: {name}"
                text_x = x + 15
                text_y = y + bar_height / 2
                font = ("微软雅黑", 9, "bold")  # 使用粗体提高可读性
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                # 可用地址数 - 使用带描边的文字绘制，提高可见度
                address_text = f"可用地址数: {usable_addresses:,}"
                text_x = x + 250
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                y += bar_height + padding

            # 添加剩余网段和图例之间的虚线分割
            self.chart_canvas.create_line(x, y, x + chart_width, y, fill="#cccccc", dash=(5, 2), width=1)

            # 绘制图例（参考Web版）
            legend_y = y + 15
            self.chart_canvas.create_text(x, legend_y, text="图例:", font=("微软雅黑", 11), anchor=tk.W, fill="#ffffff")

            # 增加图例文字与图例图形之间的间距
            legend_items_y = legend_y + 25

            # 父网段图例
            self.chart_canvas.create_rectangle(x, legend_items_y, x + 20, legend_items_y + 15, fill="#636e72")
            self.chart_canvas.create_text(
                x + 30,
                legend_items_y + 6,
                text="父网段",
                font=("微软雅黑", 9),
                anchor=tk.W,
                fill="#ffffff",
            )

            # 切分网段图例
            self.chart_canvas.create_rectangle(x + 100, legend_items_y, x + 120, legend_items_y + 12, fill="#4a7eb4")
            self.chart_canvas.create_text(
                x + 130,
                legend_items_y + 6,
                text="切分网段",
                font=("微软雅黑", 9),
                anchor=tk.W,
                fill="#ffffff",
            )

            # 剩余网段图例（显示多彩示例，匹配高区分度配色方案）
            legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
            for j, color in enumerate(legend_colors):
                self.chart_canvas.create_rectangle(
                    x + 230 + j * 25,
                    legend_items_y,
                    x + 250 + j * 25,
                    legend_items_y + 12,
                    fill=color,
                )

            self.chart_canvas.create_text(
                x + 340,
                legend_items_y + 6,
                text="剩余网段(多色)",
                font=("微软雅黑", 9),
                anchor=tk.W,
                fill="#ffffff",
            )

            # 优化：显式调用update_idletasks，确保Canvas及时更新和资源释放
            self.chart_canvas.update_idletasks()

        except (tk.TclError, ValueError, TypeError) as e:
            # 出现错误时显示提示
            self.chart_canvas.delete("all")
            width = self.chart_canvas.winfo_width() or 600
            height = self.chart_canvas.winfo_height() or 400
            title_font = ("微软雅黑", 12, "bold")
            self.chart_canvas.create_text(
                width / 2, height / 2, text=f"图表绘制失败: {str(e)}", font=title_font, fill="red"
            )

    def on_window_resize(self, _):
        """窗口大小变化时的处理函数，实现表格和图表自适应"""
        # 确保表格能够自适应窗口宽度
        self.remaining_tree.update_idletasks()
        self.adjust_remaining_tree_width()

        # 窗口大小变化时不需要重新配置斑马条纹，样式已在初始化时设置
        # 图表将在 on_chart_resize 中单独处理，避免重复绘制
        # 重新绘制所有Treeview的表格线 - 使用ttk样式方案不需要手动绘制

    def _prepare_export_data(self, data_source):
        """准备导出数据
        
        Args:
            data_source: 字典，包含导出数据的源信息
            
        Returns:
            tuple: (main_data, main_headers, remaining_data, remaining_headers)
        """
        main_data = []
        main_tree = data_source["main_tree"]
        main_filter = data_source.get("main_filter", None)
        main_headers = data_source.get("main_headers")

        if main_headers is None:
            main_headers = [main_tree.heading(col, "text") or "" for col in main_tree["columns"]]

        # 用于去重的集合，存储已经添加过的项目
        added_items = set()
        for item in main_tree.get_children():
            values = main_tree.item(item, "values")
            if main_filter:
                if main_filter(values):
                    # 去重：如果是键值对格式，确保每个项目只出现一次
                    if len(values) >= 2 and values[0] != "":
                        item_key = values[0]
                        if item_key not in added_items:
                            added_items.add(item_key)
                            main_data.append(values)
                    else:
                        main_data.append(values)
            elif values:
                # 去重：如果是键值对格式，确保每个项目只出现一次
                if len(values) >= 2 and values[0] != "":
                    item_key = values[0]
                    if item_key not in added_items:
                        added_items.add(item_key)
                        main_data.append(values)
                else:
                    main_data.append(values)

        # 二次去重：确保所有数据行都是唯一的，解决切分段信息重复的问题
        unique_main_data = []
        seen_rows = set()
        for row in main_data:
            # 将行转换为可哈希的元组
            row_tuple = tuple(row)
            if row_tuple not in seen_rows:
                seen_rows.add(row_tuple)
                unique_main_data.append(row)
        main_data = unique_main_data

        # 准备剩余数据
        remaining_tree = data_source["remaining_tree"]
        remaining_headers = [remaining_tree.heading(col, "text") or "" for col in remaining_tree["columns"]]
        remaining_data = []
        for item in remaining_tree.get_children():
            values = remaining_tree.item(item, "values")
            if values:
                remaining_data.append(dict(zip(remaining_headers, values)))

        return main_data, main_headers, remaining_data, remaining_headers

    def _export_data(self, data_source, title, success_msg, failure_msg):
        """通用数据导出函数

        Args:
            data_source: 字典，包含导出数据的源信息
                - main_tree: 主数据表格控件
                - main_headers: 主数据表格标题（可选）
                - main_name: 主数据名称
                - main_filter: 主数据过滤函数（可选）
                - remaining_tree: 剩余数据表格控件
                - remaining_name: 剩余数据名称
                - pdf_title: PDF文档标题
                - main_table_cols: PDF主表格列宽（可选）
                - remaining_table_cols: PDF剩余表格列宽（可选）
            title: 文件对话框标题
            success_msg: 成功消息格式字符串
            failure_msg: 失败消息格式字符串
        """
        try:
            # 先显示文件选择对话框，不准备数据
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[
                    ("CSV文件", "*.csv"),
                    ("JSON文件", "*.json"),
                    ("文本文件", "*.txt"),
                    ("PDF文件", "*.pdf"),
                    ("Excel文件", "*.xlsx"),
                    ("所有文件", "*.*"),
                ],
                title=title,
                initialdir="",
            )

            if not file_path:
                return

            # 用户确认文件路径后，再准备数据
            success, message, data = self.export_utils.export_data(data_source, title, success_msg, failure_msg)

            if not success:
                self.show_error("提示", message)
                return

            main_data, main_headers, remaining_data, remaining_headers = data

            # 使用导出工具导出到文件
            success, message = self.export_utils.export_to_file(
                file_path, data_source, main_data, main_headers, remaining_data, remaining_headers
            )

            if success:
                self.show_result(success_msg.format(file_path=file_path), keep_data=True)
            else:
                self.show_result(message, error=True)

        except Exception as e:
            error_msg = f"{failure_msg.format(error=str(e))}\n堆栈跟踪：{traceback.format_exc()}"
            self.show_result(error_msg, error=True)

    def export_result(self):
        """导出子网切分结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
        data_source = {
            "main_tree": self.split_tree,
            "main_name": "切分段信息",
            "main_filter": lambda values: values[0] not in ["提示", "错误", "-", "切分段信息", "剩余网段信息"],
            "main_headers": ["项目", "值"],
            "remaining_tree": self.remaining_tree,
            "remaining_name": "剩余网段信息",
            "pdf_title": "子网规划师 - 计算结果",
            "main_table_cols": None,  # 使用默认列宽
            "remaining_table_cols": [40, 80, 80, 100, 90, 80, 50],  # 剩余网段表格列宽
            "chart_data": getattr(self, 'chart_data', None),  # 添加网段分布图数据
        }

        self._export_data(data_source, "保存子网切分结果", "结果已成功导出到: {file_path}", "导出失败: {error}")

    def export_planning_result(self):
        """导出子网规划结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
        data_source = {
            "main_tree": self.allocated_tree,
            "main_name": "已分配子网信息",
            "main_filter": None,  # 不需要过滤，直接导出所有数据
            "main_headers": None,  # 自动从表格获取
            "remaining_tree": self.planning_remaining_tree,
            "remaining_name": "剩余网段信息",
            "pdf_title": "子网规划师 - 子网规划结果",
            "main_table_cols": [10, 100, 90, 30, 40, 80, 110, 80],  # 已分配子网表格列宽
            "remaining_table_cols": [40, 90, 80, 110, 80, 60],  # 剩余网段表格列宽
        }

        self._export_data(data_source, "保存子网规划结果", "规划结果已成功导出到: {file_path}", "导出失败: {error}")

    def clear_result(self):
        """清空结果表格和图表"""
        # 清空切分段信息表格
        self.clear_tree_items(self.split_tree)
        # 添加提示行
        self.split_tree.insert("", tk.END, values=("提示", "点击'执行切分'按钮开始操作..."), tags=('odd',))
        # 更新切分段表格的斑马条纹标签
        self.update_table_zebra_stripes(self.split_tree)

        # 清空剩余网段表表格
        self.clear_tree_items(self.remaining_tree)
        # 更新剩余网段表的斑马条纹标签
        self.update_table_zebra_stripes(self.remaining_tree)

        # 处理剩余网段表的滚动条，确保清空结果时滚动条隐藏
        if hasattr(self, 'remaining_scroll_v'):
            # 重置滚动条位置
            self.remaining_scroll_v.set(0.0, 1.0)
            # 隐藏滚动条
            self.remaining_scroll_v.grid_remove()

        # 清空图表
        self.chart_canvas.delete("all")
        self.chart_data = None

        # 更新Canvas滚动区域，设置为不可滚动状态
        self.chart_canvas.config(scrollregion=(0, 0, self.chart_canvas.winfo_width(), 100))

        # 调用滚动条回调函数，确保滚动条隐藏
        # 模拟内容不可滚动的情况，让滚动条隐藏
        if hasattr(self, 'chart_scrollbar'):
            self.chart_scrollbar.set(0.0, 1.0)
            # 使用grid_remove()直接隐藏滚动条
            self.chart_scrollbar.grid_remove()

    def create_about_link(self):
        """在主窗体标题栏右侧（红框位置）创建关于链接按钮和钉住按钮"""
        # 直接在root窗口创建关于链接，不使用框架
        # 使用普通tk.Label直接控制样式，确保悬停效果可靠

        # 获取窗口背景色以确保完全一致
        self.bg_color = self.root.cget("background")
        self.hover_bg_color = "#e0e0e0"  # 更浅的灰色背景，柔和过渡
        self.hover_fg_color = "#333333"  # 深灰色文字，保持可读性
        self.normal_fg_color = "#666666"
        border_color = "#cccccc"  # 更浅的灰色边框，视觉上更细

        # 初始化窗口置顶状态
        self.is_pinned = False

        # 使用普通tk.Label创建关于标签，直接设置所有样式属性，高度与信息框一致
        self.about_label = tk.Label(
            self.root,
            text="关于…",
            font=('微软雅黑', 10, 'bold'),  # 字体与子网标签激活状态一致，加粗
            fg=self.normal_fg_color,  # 文字颜色调淡为浅灰色
            bg=self.bg_color,  # 背景色与窗口完全一致
            padx=12,  # 水平内边距，与子网标签一致
            pady=4.4,  # 调整垂直内边距，高度调小1px
            bd=0,  # 取消默认边框
            relief="flat",  # 平坦样式
            highlightthickness=1,  # 高亮边框宽度，模拟边框
            highlightbackground=border_color,  # 边框颜色
            highlightcolor=border_color,  # 边框颜色（确保一致性）
            cursor="hand2",  # 鼠标指针为手形
        )

        # 放置在窗口标题栏右侧位置，y坐标调整为与信息框垂直对齐，与标签页按钮底部对齐
        self.about_label.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-24, y=22)  # y=22，向下移动1px，与信息栏顶部对齐
        self.about_label.bind("<Button-1>", lambda e: self.show_about_dialog())

        # 绑定鼠标事件实现悬停效果
        self.about_label.bind("<Enter>", self.on_about_link_enter)
        self.about_label.bind("<Leave>", self.on_about_link_leave)

        # 创建钉住按钮，使用扁平化风格，直接添加到root窗口，高度与信息框一致
        self.pin_label = tk.Label(
            self.root,
            text="📌",
            font=('微软雅黑', 10, 'bold'),  # 字体与子网标签激活状态一致，加粗
            fg=self.normal_fg_color,  # 文字颜色调淡为浅灰色
            bg=self.bg_color,  # 背景色与窗口完全一致
            padx=4.4,  # 水平内边距，调整为与pady一致，使其宽度与高度相同
            pady=4.4,  # 调整垂直内边距，高度调小1px
            bd=0,  # 无边框，扁平化风格
            relief="flat",  # 平坦样式，扁平化风格
            highlightthickness=1,  # 高亮边框宽度，模拟边框
            highlightbackground=border_color,  # 边框颜色
            highlightcolor=border_color,  # 边框颜色（确保一致性）
            cursor="hand2",  # 鼠标指针为手形
        )

        # 放置钉住按钮在橙色标题栏右侧，关于按钮左侧且不重叠，y坐标与信息框对齐，与标签页按钮底部对齐
        self.pin_label.place(
            relx=1.0, rely=0.0, anchor=tk.NE, x=-94, y=22
        )  # x=-94，向左移动5个像素，y=22，向下移动1px，与信息栏顶部对齐
        self.pin_label.bind("<Button-1>", lambda e: self.toggle_pin_window())

        # 绑定鼠标事件实现悬停效果
        self.pin_label.bind("<Enter>", self.on_about_link_enter)
        self.pin_label.bind("<Leave>", self.on_about_link_leave)

    def on_about_link_enter(self, event):
        """鼠标进入关于链接或钉住按钮时的处理函数"""
        # 获取事件源，判断是哪个标签触发的事件
        widget = event.widget

        # 修改标签的前景色和背景色
        if widget == self.about_label:
            self.about_label.config(fg=self.hover_fg_color, bg=self.hover_bg_color)
        elif widget == self.pin_label:
            self.pin_label.config(fg="#333333", bg=self.hover_bg_color)

    def on_about_link_leave(self, event):
        """鼠标离开关于链接或钉住按钮时的处理函数"""
        # 获取事件源，判断是哪个标签触发的事件
        widget = event.widget

        # 恢复标签的默认前景色和背景色
        if widget == self.about_label:
            self.about_label.config(fg=self.normal_fg_color, bg=self.bg_color)
        elif widget == self.pin_label:
            # 根据当前状态设置合适的颜色（扁平化风格，无relief属性）
            if self.is_pinned:
                self.pin_label.config(fg="#333333", bg="#e0e0e0")  # 深灰色文字，浅灰色背景
            else:
                self.pin_label.config(fg=self.normal_fg_color, bg=self.bg_color)  # 浅灰色文字，原始背景

    def toggle_pin_window(self):
        """切换窗口置顶状态"""
        # 切换置顶状态
        self.is_pinned = not self.is_pinned

        # 设置窗口置顶属性
        self.root.attributes("-topmost", self.is_pinned)

        # 更新钉住按钮的视觉效果（扁平化风格，使用颜色变化表示状态）
        if self.is_pinned:
            # 置顶状态：深色图标和文字
            self.pin_label.config(fg="#333333", bg="#e0e0e0")  # 深灰色文字，浅灰色背景
        else:
            # 非置顶状态：浅色图标和文字
            self.pin_label.config(fg=self.normal_fg_color, bg=self.bg_color)  # 浅灰色文字，原始背景

    def show_about_dialog(self):
        """显示关于对话框"""
        # 创建对话框窗口
        about_window = tk.Toplevel(self.root)
        about_window.title(f"关于 {self.app_name}")
        about_window.resizable(False, False)

        # 确保对话框在主窗口之上
        about_window.transient(self.root)
        about_window.grab_set()

        # 先隐藏对话框，避免定位过程中的闪现
        about_window.withdraw()

        # 获取主窗口的位置和尺寸
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        # 设置对话框尺寸
        dialog_width = 350
        dialog_height = 220

        # 计算对话框在主窗口中心的位置
        dialog_x = main_x + (main_width // 2) - (dialog_width // 2)
        dialog_y = main_y + (main_height // 2) - (dialog_height // 2)

        # 一次性设置对话框的尺寸和位置
        about_window.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")

        # 显示对话框
        about_window.deiconify()

        # 创建内容框架，移除所有边框和焦点指示
        content_frame = ttk.Frame(about_window, padding=(15, 0, 15, 0), relief="flat", borderwidth=0)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 创建上下占位框架实现内容垂直居中
        top_spacer = ttk.Frame(content_frame)
        top_spacer.pack(side="top", expand=True, fill="y")

        # 创建内部框架放置实际内容
        inner_frame = ttk.Frame(content_frame)
        inner_frame.pack(side="top", fill="both")

        bottom_spacer = ttk.Frame(content_frame)
        bottom_spacer.pack(side="top", expand=True, fill="y")

        # 移除对话框的焦点指示
        about_window.focus_set()
        about_window.bind("<FocusIn>", lambda e: None)
        about_window.bind("<FocusOut>", lambda e: None)

        # 为关于对话框中的标签和按钮添加焦点样式，移除虚线
        # 创建对话框专用的样式，避免影响主窗口
        self.style.configure("About.TLabel", focuscolor="none")
        self.style.configure("About.TButton", focuscolor="none", focuswidth=0)
        self.style.map("About.TButton", focuscolor=[("focus", "none")], focuswidth=[("focus", 0)])

        # 标题区域
        title_frame = ttk.Frame(inner_frame)
        title_frame.pack(pady=(10, 8))

        # 添加应用名称作为主要标题
        app_name_label = ttk.Label(title_frame, text=self.app_name, font=("微软雅黑", 16, "bold"), style="About.TLabel")
        app_name_label.pack()

        # 添加版本号
        version_label = ttk.Label(
            title_frame, text=f"版本 {self.app_version}", font=("微软雅黑", 10), style="About.TLabel"
        )
        version_label.pack(pady=(1, 0))

        # 信息区域
        info_frame = ttk.Frame(inner_frame)
        info_frame.pack(pady=(0, 8))

        # 添加作者信息
        author_label = ttk.Label(info_frame, text="作者：Ejones", font=("微软雅黑", 10), style="About.TLabel")
        author_label.pack(pady=(0, 1))

        # 添加联系方式
        email_label = ttk.Label(
            info_frame, text="邮箱：ejones.cn@hotmail.com", font=("微软雅黑", 10), style="About.TLabel"
        )
        email_label.pack()

        # 直接在内容框架中添加确定按钮和版权信息，不使用额外的底部框架
        # 添加确定按钮
        ok_button = ttk.Button(inner_frame, text="确定", command=about_window.destroy, width=12, style="About.TButton")
        ok_button.pack(pady=(0, 2))

        # 添加版权信息
        copyright_label = ttk.Label(
            inner_frame, text="© 2025 IP 子网分割工具", font=("微软雅黑", 8), style="About.TLabel"
        )
        copyright_label.pack(pady=(2, 10))


if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()

    # 设置窗口初始大小 - 调整高度以确保子网需求和规划结果两个表格都显示5行
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 700  # 调整窗口高度，确保两个表格都能显示5行

    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口居中的坐标
    window_x = (screen_width - WINDOW_WIDTH) // 2
    window_y = (screen_height - WINDOW_HEIGHT) // 2

    # 设置窗口大小和位置
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{window_x}+{window_y}")

    # 设置窗口固定宽度，高度可调整
    root.minsize(800, 700)
    root.maxsize(800, 10000)  # 设置最大宽度为800，最大高度设为一个很大的值

    # 只允许调整窗口高度，不允许调整宽度
    root.resizable(width=False, height=True)

    # 设置窗口图标
    try:
        # 尝试加载图标文件
        # 在开发环境中，图标文件位于当前目录
        # 在打包后的程序中，使用PyInstaller的资源路径

        # 获取图标文件路径
        icon_path = None
        if hasattr(sys, "_MEIPASS"):
            # 打包后的路径
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")  # pylint: disable=protected-access
        else:
            # 开发环境路径
            icon_path = "icon.ico"

        # 确保图标文件存在
        if os.path.exists(icon_path):
            # Windows系统上设置图标的最佳实践
            # 使用iconbitmap设置窗口标题栏图标
            root.iconbitmap(default=icon_path)

            # 额外尝试：使用PhotoImage和iconphoto作为备选
            try:
                # 注意：PhotoImage可能无法直接处理.ico文件，需要转换
                # 这里先尝试直接加载，如果失败则忽略
                photo_icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, photo_icon)
            except tk.TclError:
                pass  # 如果PhotoImage方法失败，继续执行
    except (tk.TclError, OSError) as e:
        print(f"设置窗口图标失败: {e}")

    # 创建应用实例并运行
    IPSubnetSplitterApp(root)
    root.mainloop()
