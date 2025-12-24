#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子网计算器应用程序 - 主窗口
"""

# 所有导入语句放在最顶部
import tkinter as tk
import math
import re
import datetime
from tkinter import ttk, filedialog
import tkinter.font as tkfont
import sys
import os
import traceback
import json
import time
from io import BytesIO
import ipaddress

# 外部库导入
from PIL import Image, ImageDraw, ImageFont
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import reportlab.lib.colors as colors
from reportlab.lib.colors import black, white, lightgrey, grey, darkgrey, blue, lightblue, red, green, yellow
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage, PageBreak, BaseDocTemplate, Frame, PageTemplate, NextPageTemplate

# 导入自定义模块
from ip_subnet_calculator import (
    split_subnet, ip_to_int, get_subnet_info, suggest_subnet_planning,
    merge_subnets, ipv4_to_ipv6, ipv6_to_ipv4, get_ip_info,
    range_to_cidr, check_subnet_overlap
)


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

    def get_light_blue_style(self):
        """获取浅蓝色样式名称"""
        return self.light_blue_style

    def get_light_green_style(self):
        """获取浅绿色样式名称"""
        return self.light_green_style

    def get_light_purple_style(self):
        """获取浅紫色样式名称"""
        return self.light_purple_style
        
    def get_light_orange_style(self):
        """获取浅橙色样式名称"""
        return self.light_orange_style
        
    def get_light_pink_style(self):
        """获取淡粉色样式名称"""
        return self.light_pink_style

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
                    # 尝试从子组件获取背景色
                    try:
                        if hasattr(child, 'cget'):
                            child_bg = child.cget("background")
                            if child_bg and not child_bg.startswith("system."):
                                bg_color = child_bg
                                break
                    except Exception:
                        continue

            # 如果无法从子组件获取背景色，尝试直接从父容器获取
            if not bg_color or bg_color.startswith("system."):
                try:
                    bg_color = self.master.cget("background")
                except Exception:
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

        except Exception:
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

        # 对于validatecommand，返回"1"表示有效
        return "1" if is_valid else False

    def __init__(self, root):
        # 导入版本管理模块



        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from version import get_version

        # 应用程序信息
        self.app_name = "IP子网切分工具"
        self.app_version = get_version()

        # CIDR格式验证正则表达式
        self.cidr_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}' + \
            r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/' + \
            r'([0-9]|[1-2][0-9]|3[0-2])$'

        # 存储删除记录历史，支持多次撤销
        self.deleted_history = []
        
        # 高级工具历史记录列表
        self.ipv4_history = ["192.168.1.1"]  # IPv4地址查询历史
        self.ipv6_history = ["2001:0db8:85a3:0000:0000:8a2e:0370:7334"]  # IPv6地址查询历史
        self.range_start_history = ["192.168.0.1"]  # IP范围起始地址历史
        self.range_end_history = ["192.168.0.254"]  # IP范围结束地址历史

        self.root = root
        self.root.title(f"IP子网切分工具 v{self.app_version}")
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
            # 蓝色标签样式 - 切分网段信息
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

        except Exception:
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
            selectbackground=[
                ("focus", "#4A6984"),
                ("!focus", "#4A6984")
            ],
            selectforeground=[
                ("focus", "white"),
                ("!focus", "white")
            ]
        )

        # 7. 信息栏样式配置 - 紧凑设计，调大字体
        # 统一使用#DCDAD5背景色，仅保留文字颜色区分，增大字体大小
        self.style.configure(
            "Success.TLabel", foreground="#424242", font=("微软雅黑", 9), relief="flat"
        )
        self.style.configure(
            "Error.TLabel", foreground="#c62828", font=("微软雅黑", 9), relief="flat"
        )
        self.style.configure(
            "Info.TLabel", foreground="#424242", font=("微软雅黑", 9), relief="flat"
        )

        # 信息栏框架样式 - 使用极淡灰色边框
        self.style.configure(
            "InfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5"
        )
        self.style.configure(
            "SuccessInfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5"
        )
        self.style.configure(
            "ErrorInfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5"
        )
        self.style.configure(
            "InfoInfoBar.TFrame", borderwidth=1, relief="solid", bordercolor="#F5F5F5"
        )

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
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块
        self.create_top_level_notebook()

        # 在右上角添加关于链接按钮和钉住按钮，确保它们显示在标题栏右侧
        self.create_about_link()

        # 创建信息栏框架 - 直接放置在root窗口，位于顶部标签栏右侧红框位置
        self.info_bar_frame = ttk.Frame(root, style="InfoBar.TFrame")
        # 默认隐藏
        self.info_bar_frame.place_forget()

        # 信息栏高度统一为30px，与place布局一致
        self.info_bar_frame.configure(height=10)  # 调整高度与标签页按钮一致

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

    def validate_split_cidr_local(self, text):
        return self.validate_cidr(text, self.split_entry)
    
    def is_valid_cidr(self, cidr):
        """验证CIDR格式是否有效
        
        Args:
            cidr: 要验证的CIDR字符串
            
        Returns:
            bool: 如果CIDR格式有效则返回True，否则返回False
        """
        return bool(re.match(self.cidr_pattern, cidr.strip())) if cidr.strip() else False
    
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
                self.history_tree.insert(
                    "", 
                    tk.END, 
                    values=(formatted_record,),
                    tags=tags
                )
        except Exception as e:
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
            'req_str': req_str
        }
        
        # 检查当前状态是否与上一个状态相同，如果相同则不保存
        # 只有当连续两次都是"执行规划"操作且状态相同时才跳过
        if self.history_states and action_type == "执行规划" and self.history_states[-1]['action_type'] == "执行规划":
            last_state = self.history_states[-1]
            if (last_state['requirements'] == subnet_requirements 
                    and last_state['parent'] == parent):
                return
        
        # 如果当前不是最新状态，截断历史记录
        if self.current_history_index < len(self.history_states) - 1:
            self.history_states = self.history_states[:self.current_history_index + 1]
            self.planning_history_records = self.planning_history_records[:self.current_history_index + 1]
        
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
        
    def update_undo_redo_buttons_state(self):
        """更新撤销/重做按钮的状态"""
        # 撤销按钮：如果当前索引大于0，则可以撤销
        self.undo_btn.config(state=tk.NORMAL if self.current_history_index > 0 else tk.DISABLED)
        
        # 重做按钮：如果当前索引小于历史记录长度-1，则可以重做
        self.redo_btn.config(state=tk.NORMAL if self.current_history_index < len(self.history_states) - 1 else tk.DISABLED)  
        
        # 移除不存在的方法调用
        
    def move_left(self):
        """向左移：从子网需求表向需求池移动记录（支持多条记录，移动后保持选中）"""
        # 获取选中的子网需求记录
        selected_items = self.requirements_tree.selection()
        if not selected_items:
            self.show_info("提示", "请先选择要移动的子网需求记录")
            return
        
        # 先检查所有选中记录是否都可以移动
        # 同时收集要移动的记录数据
        items_to_move = []
        for selected_item in selected_items:
            values = self.requirements_tree.item(selected_item, "values")
            name = values[1]
            hosts = values[2]
            items_to_move.append({"name": name, "hosts": hosts})
            
            # 检查需求池中是否已存在相同名称的记录
            for item in self.pool_tree.get_children():
                pool_values = self.pool_tree.item(item, "values")
                if pool_values[1] == name:
                    self.show_error("错误", f"需求池中已存在名称为 '{name}' 的记录")
                    return
        
        # 执行移动操作，并保存新插入记录的ID
        new_pool_items = []
        for selected_item in selected_items:
            # 从子网需求表删除记录
            self.requirements_tree.delete(selected_item)
        
        # 插入记录到需求池，并保存新记录的ID
        for data in items_to_move:
            new_item_id = self.pool_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
            new_pool_items.append(new_item_id)
        
        # 更新序号和斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()
        
        # 移动完成后，在需求池中选中刚刚移动的记录
        if new_pool_items:
            self.pool_tree.selection_set(*new_pool_items)
        
    def move_right(self):
        """向右移：从需求池向子网需求表移动记录（支持多条记录，移动后保持选中）"""
        # 获取选中的需求池记录
        selected_items = self.pool_tree.selection()
        if not selected_items:
            self.show_info("提示", "请先选择要移动的需求池记录")
            return
        
        # 先检查所有选中记录是否都可以移动
        # 同时收集要移动的记录数据
        items_to_move = []
        for selected_item in selected_items:
            values = self.pool_tree.item(selected_item, "values")
            name = values[1]
            hosts = values[2]
            items_to_move.append({"name": name, "hosts": hosts})
            
            # 检查子网需求表中是否已存在相同名称的记录
            for item in self.requirements_tree.get_children():
                req_values = self.requirements_tree.item(item, "values")
                if req_values[1] == name:
                    self.show_error("错误", f"子网需求表中已存在名称为 '{name}' 的记录")
                    return
        
        # 执行移动操作，并保存新插入记录的ID
        new_req_items = []
        for selected_item in selected_items:
            # 从需求池删除记录
            self.pool_tree.delete(selected_item)
        
        # 插入记录到子网需求表，并保存新记录的ID
        for data in items_to_move:
            new_item_id = self.requirements_tree.insert("", tk.END, values=("", data["name"], data["hosts"]))
            new_req_items.append(new_item_id)
        
        # 更新序号和斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()
        
        # 移动完成后，在子网需求表中选中刚刚移动的记录
        if new_req_items:
            self.requirements_tree.selection_set(*new_req_items)
    
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
        action_type = f"交换记录: 子网需求表 {len(selected_requirements)} 条记录 ↔ 需求池 {len(selected_pool_items)} 条记录"
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
        
        # 父网段 - 使用Combobox，支持下拉选择
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.parent_entry)), '%P')
        self.parent_entry = ttk.Combobox(
            input_frame, values=self.split_parent_networks, width=22, font=(
            "微软雅黑", 10), validate='focusout', validatecommand=vcmd
        )
        self.parent_entry.grid(row=1, column=1, padx=0, pady=8, sticky=tk.W + tk.N + tk.S)
        self.parent_entry.insert(0, "10.0.0.0/8")  # 默认值
        self.parent_entry.config(state="normal")  # 允许手动输入

        # 切分段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text="切分段", anchor="w", font=("微软雅黑", 10)).grid(
            row=2, column=0, sticky=tk.W + tk.N + tk.S, pady=8, padx=(0, 5)
        )
        vcmd = (self.root.register(self.validate_split_cidr_local), '%P')
        self.split_entry = ttk.Combobox(
            input_frame, values=self.split_networks, width=22, font=(
            "微软雅黑", 10), validate='focusout', validatecommand=vcmd
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
        
        # 创建历史记录列表，去掉表头，显示4行
        self.history_tree = ttk.Treeview(history_frame, columns=('record'), show='', height=4)
        
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
        self.style.configure("CompactText.TButton", 
                            font=("微软雅黑", 10),
                            padding=(2, 0, 2, 0))  # 减小垂直内边距
        
        # 创建重新切分按钮，宽度与历史记录表一致
        self.reexecute_btn = ttk.Button(history_frame, text="重新切分", 
                                       command=self.reexecute_split, 
                                       width=10, 
                                       style="TButton")
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
        self.top_level_notebook.add_tab("子网切分", self.split_frame, "#fff3e0")  # 浅橙色
        self.top_level_notebook.add_tab("子网规划", self.planning_frame, "#fce4ec")  # 淡粉色
        self.top_level_notebook.add_tab("高级工具", self.advanced_frame, "#e8f5e9")  # 浅绿色

    def create_split_result_section(self):
        """创建子网切分功能的结果显示区域"""
        result_frame = ttk.LabelFrame(self.split_frame, text="切分结果", padding="10")
        # 调整底部外边距，将结果区域与窗体下边距缩小
        result_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 0))

        # 导出结果按钮 - 使用 place 布局手动控制位置，使用默认TButton样式
        self.export_btn = ttk.Button(result_frame, text="导出结果", 
                                    command=self.export_result, 
                                    width=10)
        # 手动指定按钮位置：右上角，距离右边0像素，距离顶部-3像素
        self.export_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 创建一个自定义的笔记本控件来显示不同的结果页面
        self.notebook = ColoredNotebook(result_frame, style=self.style, tab_change_callback=self.on_tab_change)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 将导出结果按钮提升到最上层，避免被遮挡
        self.export_btn.lift()

        # 切分网段信息页面
        self.split_info_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_blue_style()
        )

        # 创建切分网段信息表格
        self.split_tree = ttk.Treeview(self.split_info_frame, columns=("item", "value"), show="headings", height=5)
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        # 设置合适的列宽
        self.split_tree.column("item", width=100, minwidth=100, stretch=False)
        self.split_tree.column("value", width=250)
        self.split_tree.pack(fill=tk.BOTH, expand=True, pady=0)

        # 配置斑马条纹样式和信息标签样式
        self.configure_treeview_styles(self.split_tree, include_special_tags=True)

        # 剩余网段表页面
        self.remaining_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_green_style()
        )

        # 创建剩余网段信息表格
        self.remaining_tree = ttk.Treeview(
            self.remaining_frame,
            columns=("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable"),
            show="headings",
            height=5,
        )
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
        self.chart_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_purple_style()
        )

        # 添加标签页，每个标签页设置不同的颜色
        self.notebook.add_tab("切分网段信息", self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab("剩余网段表", self.remaining_frame, "#e8f5e9")  # 浅绿色
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
        self.export_btn = ttk.Button(parent_frame, text="导出结果", 
                                    command=self.export_result, 
                                    width=10)
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
        """创建切分网段信息页面"""
        # 切分网段信息页面
        self.split_info_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_blue_style()
        )

        # 创建切分网段信息表格
        self.split_tree = ttk.Treeview(self.split_info_frame, columns=("item", "value"), show="headings", height=5)
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
        self.remaining_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_green_style()
        )

        # 创建剩余网段信息表格
        self.remaining_tree = ttk.Treeview(
            self.remaining_frame,
            columns=("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable"),
            show="headings",
            height=5,
        )
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
        self.notebook.add_tab("切分网段信息", self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab("剩余网段表", self.remaining_frame, "#e8f5e9")  # 浅绿色
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
        self.planning_frame.grid_columnconfigure(0, weight=1)  # 增加权重，让需求池面板和子网需求面板平均分配宽度
        self.planning_frame.grid_columnconfigure(1, weight=1)  # 增加权重，让子网需求面板和规划结果面板占据更多宽度
        self.planning_frame.grid_rowconfigure(0, weight=0)
        self.planning_frame.grid_rowconfigure(1, weight=0)
        self.planning_frame.grid_rowconfigure(2, weight=1)

        # 父网段设置区域
        parent_frame = ttk.LabelFrame(self.planning_frame, text="父网段设置", padding="10")
        parent_frame.grid(row=0, column=0, sticky="nwse", pady=(0, 0))
        
        # 初始化父网段列表 - 为子网规划创建独立的历史记录列表
        self.planning_parent_networks = ["10.21.48.0/20"]  # 默认父网段
        
        # 父网段下拉文本框
        ttk.Label(parent_frame, text="父网段").pack(side=tk.LEFT, padx=(0, 10))
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.planning_parent_entry)), '%P')
        self.planning_parent_entry = ttk.Combobox(
            parent_frame, values=self.planning_parent_networks, width=16, font=(
            "微软雅黑", 10), validate='focusout', validatecommand=vcmd
        )
        self.planning_parent_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        self.planning_parent_entry.insert(0, "10.21.48.0/20")  # 默认值
        self.planning_parent_entry.config(state="normal")  # 允许手动输入
        
        # 需求池区域
        history_frame = ttk.LabelFrame(self.planning_frame, text="需求池", padding=(10, 10, 0, 10))
        history_frame.grid(row=1, column=0, sticky="nwse", pady=(0, 10))  # 靠左放置

        # 子网需求区域
        requirements_frame = ttk.LabelFrame(self.planning_frame, text="子网需求", padding=(10, 10, 0, 10))
        requirements_frame.grid(row=0, column=1, rowspan=2, sticky="nwse", padx=(10, 0), pady=(0, 10))  # 跨两行，靠右放置

        # 内部容器框架，用于组织表格和按钮
        inner_frame = ttk.Frame(requirements_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置grid布局
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_columnconfigure(1, weight=0)
        
        # 创建需求池表格，结构与子网需求表相同
        self.pool_tree = ttk.Treeview(history_frame, columns=("index", "name", "hosts"), show="headings", height=8)
        self.pool_tree.heading("index", text="序号")
        self.pool_tree.heading("name", text="子网名称")
        self.pool_tree.heading("hosts", text="主机数量")
        
        # 设置列宽，与子网需求表保持一致
        self.pool_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")
        self.pool_tree.column("name", width=140, minwidth=140, stretch=True)
        self.pool_tree.column("hosts", width=30, minwidth=30, stretch=True)
        
        # 配置斑马条纹样式
        self.configure_treeview_styles(self.pool_tree)
        
        # 绑定双击事件以实现编辑功能
        self.pool_tree.bind("<Double-1>", self.on_pool_tree_double_click)
        
        # 添加滚动条，确保只作用于表格，位于表格右侧
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.pool_tree.yview)
        
        # 创建滚动条回调函数，始终显示滚动条
        def pool_scrollbar_callback(*args):
            # 只更新滚动条位置，不隐藏滚动条
            history_scrollbar.set(*args)
        
        self.pool_tree.configure(yscroll=pool_scrollbar_callback)
        
        # 放置需求池表格和滚动条
        self.pool_tree.grid(row=0, column=0, sticky="nsew")
        history_scrollbar.grid(row=0, column=1, sticky="ns")
        pool_scrollbar_callback(0.0, 1.0)
        
        # 移除双击事件绑定，用户不能直接选择历史记录，只能通过撤销/重做按钮操作
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
        self.requirements_tree.heading("index", text="序号")
        self.requirements_tree.heading("name", text="子网名称")
        self.requirements_tree.heading("hosts", text="主机数量")
        # 字段宽度设置
        self.requirements_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")
        self.requirements_tree.column("name", width=140, minwidth=140, stretch=True)
        self.requirements_tree.column("hosts", width=30, minwidth=30, stretch=True)

        # 绑定双击事件以实现编辑功能
        self.requirements_tree.bind("<Double-1>", self.on_requirements_tree_double_click)

        # 放置表格
        self.requirements_tree.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # 添加滚动条，确保只作用于表格，位于表格右侧
        requirements_scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL, command=self.requirements_tree.yview)
        
        # 创建滚动条回调函数，始终显示滚动条
        def requirements_scrollbar_callback(*args):
            # 只更新滚动条位置，不隐藏滚动条
            requirements_scrollbar.set(*args)
        
        self.requirements_tree.configure(yscroll=requirements_scrollbar_callback)

        # 放置滚动条在表格右侧
        requirements_scrollbar.grid(row=0, column=2, sticky="ns", padx=(0, 0))
        requirements_scrollbar_callback(0.0, 1.0)
        
        # 允许同时选择两张表中的记录，移除选择事件绑定

        # 按钮框架内部布局 - 按照用户要求设置行权重
        button_frame.grid_rowconfigure(0, weight=0)  # 添加按钮
        button_frame.grid_rowconfigure(1, weight=0)  # 删除按钮
        button_frame.grid_rowconfigure(2, weight=0)  # 撤销按钮
        button_frame.grid_rowconfigure(3, weight=1)  # 空白区域，将底部三个按钮推到底部
        button_frame.grid_rowconfigure(4, weight=0)  # 向左移按钮
        button_frame.grid_rowconfigure(5, weight=0)  # 交换记录按钮
        button_frame.grid_rowconfigure(6, weight=0)  # 向右移按钮
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

        # 向左移按钮 - 使用向左箭头，位于底部三个按钮的最上方
        self.undo_btn = ttk.Button(button_frame, text="←", command=self.move_left, width=7)
        self.undo_btn.grid(row=4, column=0, sticky="ew", pady=(0, 5))

        # 交换记录按钮 - 使用交换图标，位于向左移和向右移按钮中间
        self.swap_btn = ttk.Button(button_frame, text="↔", command=self.swap_records, width=7)
        self.swap_btn.grid(row=5, column=0, sticky="ew", pady=(0, 5))

        # 向右移按钮 - 使用向右箭头，位于交换按钮下方
        self.redo_btn = ttk.Button(button_frame, text="→", command=self.move_right, width=7)
        self.redo_btn.grid(row=6, column=0, sticky="ew", pady=(0, 5))

        # 规划子网按钮已移动到规划结果区域，此处不再显示

        # 添加示例数据 - 带斑马条纹标签
        # 先插入不带序号的数据
        self.requirements_tree.insert("", tk.END, values=("", "办公室", "20"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "人事部", "10"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "财务部", "10"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "规划部", "30"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "法务部", "10"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "采购部", "10"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "安管办", "10"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "党群部", "20"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "纪委办", "10"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "信息部", "20"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "工程部", "20"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "销售部", "20"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "研发部", "15"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "生产部", "100"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "运输部", "20"), tags=("odd",))

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
        result_frame.grid(row=2, column=0, columnspan=2, sticky="nwse", pady=(0, 5))

        # 创建笔记本控件显示规划结果
        self.planning_notebook = ColoredNotebook(result_frame, style=self.style)
        self.planning_notebook.pack(fill=tk.BOTH, expand=True)

        # 设置统一的按钮宽度，使用合适的宽度确保文字完全显示
        button_width = 10
        
        # 导出规划按钮 - 使用 place 布局手动控制位置，使用默认TButton样式
        export_planning_btn = ttk.Button(result_frame, text="导出规划", 
                                        command=self.export_planning_result, 
                                        width=button_width)
        # 手动指定按钮位置：右上角，距离右边0像素，距离顶部-3像素
        export_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)
        
        # 创建醒目的按钮样式，使用更深的蓝色系，确保文字清晰显示
        self.style.configure("Accent.TButton", 
                           background="#1565c0",  # 深蓝色，确保白色文字清晰显示
                           foreground="white",  # 白色文字
                           font=("微软雅黑", 10, "bold"),
                           padding=6)
        
        # 配置蓝色按钮的鼠标悬停效果
        self.style.map("Accent.TButton", 
                      background=[("active", "#0d47a1"),  # 鼠标悬停时使用更深的蓝色
                                 ("!active", "#1565c0"),  # 正常状态
                                 ("pressed", "#0d47a1")],  # 按下状态
                      foreground=[("active", "white"),
                                 ("!active", "white"),
                                 ("pressed", "white")])
        
        # 创建醒目的按钮样式，使用更深的绿色系，确保文字清晰显示
        self.style.configure("RedAccent.TButton", 
                           background="#2e7d32",  # 深绿色，确保白色文字清晰显示
                           foreground="white",  # 白色文字
                           font=("微软雅黑", 10, "bold"),
                           padding=6)
        
        # 配置绿色按钮的鼠标悬停效果
        self.style.map("RedAccent.TButton", 
                      background=[("active", "#1b5e20"),  # 鼠标悬停时使用更深的绿色
                                 ("!active", "#2e7d32"),  # 正常状态
                                 ("pressed", "#1b5e20")],  # 按下状态
                      foreground=[("active", "white"),
                                 ("!active", "white"),
                                 ("pressed", "white")])
        
        # 规划子网按钮 - 使用 place 布局，位于导出规划按钮左方，大小相同，使用默认TButton样式
        self.execute_planning_btn = ttk.Button(result_frame, text="规划子网", 
                                             command=self.execute_subnet_planning, 
                                             width=button_width)
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
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.get_light_blue_style()
        )
        self.allocated_tree = ttk.Treeview(
            self.allocated_frame,
            columns=("index", "name", "cidr", "required", "available", "network", "netmask", "broadcast"),
            show="headings",
            height=5,  # 设置为5行高度
        )

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
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.get_light_green_style()
        )
        self.planning_remaining_tree = ttk.Treeview(
            self.planning_remaining_frame,
            columns=("index", "cidr", "network", "netmask", "broadcast", "usable"),
            show="headings",
            height=5,  # 设置为5行高度
        )

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
        except Exception:
            pass



    def configure_treeview_styles(self, tree, include_special_tags=False):
        """配置Treeview控件的基本样式（斑马条纹、错误和信息标签）

        Args:
            tree: 要配置的Treeview对象
            include_special_tags: 是否包含错误和信息标签配置
        """
        try:
            # 配置斑马条纹样式
            tree.tag_configure("even", background="#d8d8d8")
            tree.tag_configure("odd", background="#ffffff")

            # 配置当前操作标签样式：使用加粗字体和颜色变化，避免与斑马条纹冲突
            tree.tag_configure("current", font=tree.cget("font") + ("bold",), foreground="#0066cc")

            # 如果需要，配置错误和信息标签
            if include_special_tags:
                tree.tag_configure("error", foreground="red")
                tree.tag_configure("info", foreground="blue")
        except Exception:
            # 如果发生错误，不影响程序运行
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
        except Exception as e:
            # 如果发生其他错误，不影响程序运行
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
                    if cell_width > max_width:
                        max_width = cell_width

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
        except AttributeError as e:
            # 忽略属性不存在的错误
            pass
        except ValueError as e:
            # 忽略值错误
            pass
        except Exception as e:
            # 忽略其他错误
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

        # 主机数量 - 标签在中间列左侧，输入框在中间列右侧
        ttk.Label(main_frame, text="主机数量:").grid(row=1, column=1, sticky=tk.E, pady=15, padx=(10, 10))
        hosts_var = tk.StringVar()
        hosts_entry = ttk.Entry(main_frame, textvariable=hosts_var, width=20)
        hosts_entry.grid(row=1, column=2, sticky=tk.W, pady=15, padx=(0, 10))
        
        # 定义回车键事件处理函数
        def on_return_key(event):
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
        save_requirement_btn = ttk.Button(button_frame, text="保存需求", command=lambda: save_requirement("requirements"), width=10)
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
        x = root_x + (root_width - width) // 2
        y = root_y + title_bar_height + (root_height - title_bar_height - height) // 2

        # 一次性设置对话框的尺寸和位置
        window.geometry(f"{width}x{height}+{x}+{y}")

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
            deleted_records.append({
                "tree": "requirements",
                "values": tuple(values),
                "item": item
            })
            self.requirements_tree.delete(item)
        
        # 删除需求池表中的选中记录
        for item in selected_pool_items:
            values = self.pool_tree.item(item, "values")
            deleted_subnets.append(f"{values[1]}({values[2]})")
            # 保存详细记录，包括表格类型和记录数据
            deleted_records.append({
                "tree": "pool",
                "values": tuple(values),
                "item": item
            })
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
        
    def show_custom_dialog(self, title, message, dialog_type="info"):
        """显示自定义的居中对话框，支持info、error、warning类型"""
        result = None
        
        # 创建Toplevel窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)  # 设置为父窗口的子窗口
        dialog.grab_set()  # 模态对话框，阻止父窗口接收事件
        
        # 设置对话框最小高度
        dialog.minsize(width=300, height=150)
        
        # 设置对话框内容
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置frame的grid布局，让按钮垂直居中
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        
        # 添加消息文本，居中显示
        msg_label = ttk.Label(frame, text=message, wraplength=300, font=('微软雅黑', 10))
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
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        
        # 设置对话框位置
        dialog.geometry(f"+{x}+{y}")
        
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
        
        # 创建Toplevel窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)  # 设置为父窗口的子窗口
        dialog.grab_set()  # 模态对话框
        
        # 设置对话框最小高度
        dialog.minsize(width=300, height=150)
        
        # 设置对话框内容
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置frame的grid布局，让按钮垂直居中
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        
        # 添加消息文本，居中显示
        msg_label = ttk.Label(frame, text=message, wraplength=300, font=('微软雅黑', 10))
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
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        
        # 设置对话框位置
        dialog.geometry(f"+{x}+{y}")
        
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
        x, y, width, height = self.requirements_tree.bbox(item, column)

        # 创建编辑框
        self.edit_entry = ttk.Entry(self.requirements_tree, width=width // 10)  # 估算字符宽度
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()

        # 放置编辑框在单元格上
        self.edit_entry.place(x=x, y=y, width=width, height=height)

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
        x, y, width, height = self.pool_tree.bbox(item, column)

        # 创建编辑框
        self.edit_entry = ttk.Entry(self.pool_tree, width=width // 10)  # 估算字符宽度
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()

        # 放置编辑框在单元格上
        self.edit_entry.place(x=x, y=y, width=width, height=height)

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
                original_value = self.requirements_tree.item(self.current_edit_item, "values")[self.current_edit_column_index]
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

        if not self.is_valid_cidr(parent):
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
        except Exception as e:
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
            self.split_tree.delete(*self.split_tree.get_children())
            self.split_tree.insert("", tk.END, values=("错误", "父网段和切分网段都不能为空！"), tags=("error",))
            return

        # 验证CIDR格式
        if not self.is_valid_cidr(parent):
            self.clear_result()
            self.split_tree.delete(*self.split_tree.get_children())
            self.split_tree.insert(
                "", tk.END, values=("错误", "父网段格式无效，请输入有效的CIDR格式！"), tags=("error",)
            )
            self.show_error("输入错误", "父网段格式无效，请输入有效的CIDR格式（如: 10.0.0.0/8）")
            return
        if not self.is_valid_cidr(split):
            self.clear_result()
            self.split_tree.delete(*self.split_tree.get_children())
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

            # 添加切分网段信息，同时设置斑马条纹标签
            self.split_tree.insert("", tk.END, values=("父网段", result["parent_info"]["cidr"]), tags=("odd",))
            self.split_tree.insert("", tk.END, values=("切分网段", result["split_info"]["cidr"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("-" * 10, "-" * 20), tags=("odd",))

            # 添加切分后的网段信息
            split_info = result["split_info"]
            self.split_tree.insert("", tk.END, values=("网络地址", split_info["network"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("子网掩码", split_info["netmask"]), tags=("odd",))
            self.split_tree.insert("", tk.END, values=("通配符掩码", split_info["wildcard"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("广播地址", split_info["broadcast"]), tags=("odd",))
            self.split_tree.insert("", tk.END, values=("起始地址", split_info["host_range_start"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("结束地址", split_info["host_range_end"]), tags=("odd",))
            self.split_tree.insert("", tk.END, values=("总地址数", split_info["num_addresses"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("可用地址数", split_info["usable_addresses"]), tags=("odd",))
            self.split_tree.insert("", tk.END, values=("前缀长度", split_info["prefixlen"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("CIDR", split_info["cidr"]), tags=("odd",))

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
                duplicate_exists = any(record['parent'] == parent and record['split'] == split for record in self.history_records)
                
                # 如果不存在相同记录，则添加到历史记录
                if not duplicate_exists:
                    split_record = {
                        'parent': parent,
                        'split': split
                    }
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
        except Exception as e:
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
        self.info_bar_frame.place_forget()
        
    def setup_advanced_tools_page(self):
        """设置高级工具功能的界面"""
        # 创建一个笔记本控件来显示不同的高级工具功能
        self.advanced_notebook = ColoredNotebook(self.advanced_frame, style=self.style)
        self.advanced_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 1. IPv4地址信息查询功能 - 浅蓝色
        self.ipv4_info_frame = ttk.Frame(
            self.advanced_notebook.content_area, 
            padding="10", 
            style=self.advanced_notebook.get_light_blue_style()
        )
        self.create_ipv4_info_section()
        
        # 2. IPv6地址信息查询功能 - 浅绿色
        self.ipv6_info_frame = ttk.Frame(
            self.advanced_notebook.content_area, 
            padding="10", 
            style=self.advanced_notebook.get_light_green_style()
        )
        self.create_ipv6_info_section()
        
        # 3. 子网合并与范围转CIDR功能 - 浅紫色
        self.merge_frame = ttk.Frame(
            self.advanced_notebook.content_area, 
            padding="10", 
            style=self.advanced_notebook.get_light_purple_style()
        )
        self.create_merged_subnets_and_cidr_section()
        
        # 5. 子网重叠检测功能 - 淡粉色
        self.overlap_frame = ttk.Frame(
            self.advanced_notebook.content_area, 
            padding="10", 
            style=self.advanced_notebook.get_light_pink_style()
        )
        self.create_subnet_overlap_section()
        
        # 添加高级工具标签页
        self.advanced_notebook.add_tab("IPv4查询", self.ipv4_info_frame, "#e3f2fd")  # 浅蓝色
        self.advanced_notebook.add_tab("IPv6查询", self.ipv6_info_frame, "#e8f5e9")  # 浅绿色
        self.advanced_notebook.add_tab("子网合并", self.merge_frame, "#f3e5f5")  # 浅紫色
        self.advanced_notebook.add_tab("重叠检测", self.overlap_frame, "#fce4ec")  # 淡粉色
        
    def create_merge_subnets_section(self):
        """创建子网合并功能界面"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.merge_frame, text="子网列表", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 子网输入文本框
        self.merge_text = tk.Text(input_frame, height=8, width=60, font=("微软雅黑", 10))
        self.merge_text.pack(fill=tk.BOTH, expand=True)
        self.merge_text.insert(tk.END, "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24")
        
        # 创建按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.merge_btn = ttk.Button(button_frame, text="合并子网", command=self.execute_merge_subnets)
        self.merge_btn.pack(side=tk.LEFT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.merge_frame, text="合并结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.merge_result_tree = ttk.Treeview(result_frame, columns=("cidr", "network", "netmask", "broadcast", "hosts"), show="headings")
        self.merge_result_tree.heading("cidr", text="CIDR")
        self.merge_result_tree.heading("network", text="网络地址")
        self.merge_result_tree.heading("netmask", text="子网掩码")
        self.merge_result_tree.heading("broadcast", text="广播地址")
        self.merge_result_tree.heading("hosts", text="可用主机数")
        
        self.merge_result_tree.column("cidr", width=120)
        self.merge_result_tree.column("network", width=120)
        self.merge_result_tree.column("netmask", width=120)
        self.merge_result_tree.column("broadcast", width=120)
        self.merge_result_tree.column("hosts", width=100, anchor="e")
        
        self.merge_result_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_styles(self.merge_result_tree)
        
    def create_ipv6_info_section(self):
        """创建IPv6地址信息查询功能界面"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.ipv6_info_frame, text="IPv6地址信息查询", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IPv6地址输入 - 使用Combobox，支持下拉选择和记忆功能
        ttk.Label(input_frame, text="IPv6地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.ipv6_info_entry = ttk.Combobox(input_frame, values=self.ipv6_history, width=51, font=("微软雅黑", 10))
        self.ipv6_info_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.ipv6_info_entry.insert(0, "2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        self.ipv6_info_entry.config(state="normal")  # 允许手动输入
        # 绑定事件，在输入完成后更新历史记录
        self.ipv6_info_entry.bind("<FocusOut>", self.update_ipv6_history)
        self.ipv6_info_entry.bind("<Return>", self.update_ipv6_history)
        
        # CIDR下拉列表（IPv6支持1-128）
        ttk.Label(input_frame, text="CIDR:").pack(side=tk.LEFT, padx=(0, 5))
        self.ipv6_cidr_var = tk.StringVar()
        self.ipv6_cidr_combobox = ttk.Combobox(input_frame, textvariable=self.ipv6_cidr_var, width=3, state="readonly", font=("微软雅黑", 10))
        self.ipv6_cidr_combobox['values'] = list(range(1, 129))
        self.ipv6_cidr_combobox.current(63)  # 默认选择64
        self.ipv6_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))
        
        self.ipv6_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv6_info)
        self.ipv6_info_btn.pack(side=tk.LEFT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.ipv6_info_frame, text="查询结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ipv6_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        self.ipv6_info_tree.heading("item", text="项目")
        self.ipv6_info_tree.heading("value", text="值")
        
        self.ipv6_info_tree.column("item", width=200)
        self.ipv6_info_tree.column("value", width=350)
        
        self.ipv6_info_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_styles(self.ipv6_info_tree, include_special_tags=True)
        
    def create_merged_subnets_and_cidr_section(self):
        """创建子网合并和范围转CIDR功能界面"""
        # 创建输入部分的容器，包含所有组件
        input_container = ttk.Frame(self.merge_frame)
        input_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 创建两列框架，放置在输入容器中
        left_frame = ttk.Frame(input_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5))
        
        right_frame = ttk.Frame(input_container)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10))
        
        # 左侧：子网列表
        subnet_frame = ttk.LabelFrame(left_frame, text="子网列表", padding="10")
        subnet_frame.pack(fill=tk.BOTH, expand=True)
        
        # 子网输入文本框
        self.merge_text = tk.Text(subnet_frame, height=8, width=30, font=("微软雅黑", 10))
        self.merge_text.pack(fill=tk.BOTH, expand=True)
        self.merge_text.insert(tk.END, "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24")
        
        # 子网合并按钮
        self.merge_btn = ttk.Button(subnet_frame, text="合并子网", command=self.execute_merge_subnets)
        self.merge_btn.pack(side=tk.LEFT, pady=(5, 0))
        
        # 右侧：IP地址范围
        range_frame = ttk.LabelFrame(right_frame, text="IP地址范围", padding="10")
        range_frame.pack(fill=tk.BOTH, expand=True)
        
        # 起始IP - 使用Combobox，支持下拉选择和记忆功能
        start_frame = ttk.Frame(range_frame)
        start_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(start_frame, text="起始IP:").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_start_entry = ttk.Combobox(start_frame, values=self.range_start_history, width=20, font=("微软雅黑", 10))
        self.range_start_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_start_entry.insert(0, "192.168.0.1")
        self.range_start_entry.config(state="normal")  # 允许手动输入
        # 绑定事件，在输入完成后更新历史记录
        self.range_start_entry.bind("<FocusOut>", self.update_range_start_history)
        self.range_start_entry.bind("<Return>", self.update_range_start_history)
        
        # 结束IP - 使用Combobox，支持下拉选择和记忆功能
        end_frame = ttk.Frame(range_frame)
        end_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(end_frame, text="结束IP:").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_end_entry = ttk.Combobox(end_frame, values=self.range_end_history, width=20, font=("微软雅黑", 10))
        self.range_end_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_end_entry.insert(0, "192.168.0.254")
        self.range_end_entry.config(state="normal")  # 允许手动输入
        # 绑定事件，在输入完成后更新历史记录
        self.range_end_entry.bind("<FocusOut>", self.update_range_end_history)
        self.range_end_entry.bind("<Return>", self.update_range_end_history)
        
        # 范围转CIDR按钮
        self.range_to_cidr_btn = ttk.Button(range_frame, text="转换为CIDR", command=self.execute_range_to_cidr)
        self.range_to_cidr_btn.pack(side=tk.LEFT, pady=(5, 0))
        
        # 创建结果区域，移到input_container中，位于两列下方
        result_frame = ttk.LabelFrame(input_container, text="CIDR结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 0))
        
        # 创建共用的结果树
        self.merge_result_tree = ttk.Treeview(result_frame, columns=("cidr", "network", "netmask", "broadcast", "hosts"), show="headings")
        self.merge_result_tree.heading("cidr", text="CIDR")
        self.merge_result_tree.heading("network", text="网络地址")
        self.merge_result_tree.heading("netmask", text="子网掩码")
        self.merge_result_tree.heading("broadcast", text="广播地址")
        self.merge_result_tree.heading("hosts", text="可用主机数")
        
        self.merge_result_tree.column("cidr", width=120)
        self.merge_result_tree.column("network", width=120)
        self.merge_result_tree.column("netmask", width=120)
        self.merge_result_tree.column("broadcast", width=120)
        self.merge_result_tree.column("hosts", width=100, anchor="e")
        
        self.merge_result_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_styles(self.merge_result_tree)
    
    def create_ipv4_info_section(self):
        """创建IPv4地址信息查询功能界面"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.ipv4_info_frame, text="IPv4地址信息查询", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP地址输入 - 使用Combobox，支持下拉选择和记忆功能
        ttk.Label(input_frame, text="IPv4地址:").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_info_entry = ttk.Combobox(input_frame, values=self.ipv4_history, width=21, font=("微软雅黑", 10))
        self.ip_info_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.ip_info_entry.insert(0, "192.168.1.1")
        self.ip_info_entry.config(state="normal")  # 允许手动输入
        # 绑定事件，在输入完成后更新历史记录
        self.ip_info_entry.bind("<FocusOut>", self.update_ipv4_history)
        self.ip_info_entry.bind("<Return>", self.update_ipv4_history)
        
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
            "255.255.255.255": "32"
        }
        
        # 创建反向映射，用于从CIDR获取子网掩码
        self.cidr_subnet_mask_map = {v: k for k, v in self.subnet_mask_cidr_map.items()}
        
        # 子网掩码下拉列表
        ttk.Label(input_frame, text="子网掩码:").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_mask_var = tk.StringVar()
        self.ip_mask_combobox = ttk.Combobox(input_frame, textvariable=self.ip_mask_var, width=18, state="readonly", font=("微软雅黑", 10))
        self.ip_mask_combobox['values'] = list(self.subnet_mask_cidr_map.keys())
        self.ip_mask_combobox.current(list(self.subnet_mask_cidr_map.keys()).index("255.255.255.0"))
        self.ip_mask_combobox.pack(side=tk.LEFT, padx=(0, 10))
        # 绑定子网掩码选择事件
        self.ip_mask_combobox.bind("<<ComboboxSelected>>", self.on_subnet_mask_change)
        
        # CIDR下拉列表
        ttk.Label(input_frame, text="CIDR:").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_cidr_var = tk.StringVar()
        self.ip_cidr_combobox = ttk.Combobox(input_frame, textvariable=self.ip_cidr_var, width=3, state="readonly", font=("微软雅黑", 10))
        self.ip_cidr_combobox['values'] = list(range(1, 33))
        self.ip_cidr_combobox.current(23)  # 默认选择24
        self.ip_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))
        # 绑定CIDR选择事件
        self.ip_cidr_combobox.bind("<<ComboboxSelected>>", self.on_cidr_change)
        
        self.ip_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv4_info)
        self.ip_info_btn.pack(side=tk.LEFT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.ipv4_info_frame, text="查询结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ip_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        self.ip_info_tree.heading("item", text="项目")
        self.ip_info_tree.heading("value", text="值")
        
        self.ip_info_tree.column("item", width=150)
        self.ip_info_tree.column("value", width=250)
        
        self.ip_info_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_styles(self.ip_info_tree, include_special_tags=True)
        
    def create_range_to_cidr_section(self):
        """创建IP地址范围转CIDR功能界面"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.range_to_cidr_frame, text="IP地址范围", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 开始IP
        start_frame = ttk.Frame(input_frame)
        start_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(start_frame, text="起始IP:").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_start_entry = ttk.Entry(start_frame, width=30)
        self.range_start_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_start_entry.insert(0, "192.168.0.1")
        
        # 结束IP
        end_frame = ttk.Frame(input_frame)
        end_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(end_frame, text="结束IP:").pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_end_entry = ttk.Entry(end_frame, width=30)
        self.range_end_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_end_entry.insert(0, "192.168.0.254")
        
        # 转换按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.range_to_cidr_btn = ttk.Button(button_frame, text="转换为CIDR", command=self.execute_range_to_cidr)
        self.range_to_cidr_btn.pack(side=tk.LEFT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.range_to_cidr_frame, text="CIDR结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.range_result_tree = ttk.Treeview(result_frame, columns=("cidr", "network", "netmask", "broadcast", "hosts"), show="headings")
        self.range_result_tree.heading("cidr", text="CIDR")
        self.range_result_tree.heading("network", text="网络地址")
        self.range_result_tree.heading("netmask", text="子网掩码")
        self.range_result_tree.heading("broadcast", text="广播地址")
        self.range_result_tree.heading("hosts", text="可用主机数")
        
        self.range_result_tree.column("cidr", width=120)
        self.range_result_tree.column("network", width=120)
        self.range_result_tree.column("netmask", width=120)
        self.range_result_tree.column("broadcast", width=120)
        self.range_result_tree.column("hosts", width=100, anchor="e")
        
        self.range_result_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_styles(self.range_result_tree)
        
    def create_subnet_overlap_section(self):
        """创建子网重叠检测功能界面"""
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.overlap_frame, text="子网列表", padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 子网输入文本框
        self.overlap_text = tk.Text(input_frame, height=8, width=60, font=("微软雅黑", 10))
        self.overlap_text.pack(fill=tk.BOTH, expand=True)
        self.overlap_text.insert(tk.END, "192.168.0.0/24\n192.168.0.128/25\n10.0.0.0/16")
        
        # 创建按钮区域
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.overlap_btn = ttk.Button(button_frame, text="检测重叠", command=self.execute_check_overlap)
        self.overlap_btn.pack(side=tk.LEFT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.overlap_frame, text="检测结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.overlap_result_tree = ttk.Treeview(result_frame, columns=("status", "message"), show="headings")
        self.overlap_result_tree.heading("status", text="状态")
        self.overlap_result_tree.heading("message", text="描述")
        
        self.overlap_result_tree.column("status", width=100)
        self.overlap_result_tree.column("message", width=400)
        
        self.overlap_result_tree.pack(fill=tk.BOTH, expand=True)
        self.configure_treeview_styles(self.overlap_result_tree)
        
    def execute_merge_subnets(self):
        """执行子网合并操作"""
        try:
            # 清空结果树
            for item in self.merge_result_tree.get_children():
                self.merge_result_tree.delete(item)
            
            # 获取输入的子网列表
            subnets_text = self.merge_text.get(1.0, tk.END).strip()
            if not subnets_text:
                self.show_info("提示", "请输入子网列表")
                return
            
            # 解析子网列表
            subnets = [line.strip() for line in subnets_text.splitlines() if line.strip()]
            
            # 执行合并
            result = merge_subnets(subnets)
            
            # 检查是否有错误
            if isinstance(result, dict) and "error" in result:
                self.show_info("错误", result["error"])
                return
            
            # 显示结果
            merged_subnets = result.get("merged_subnets", [])
            for subnet in merged_subnets:
                # 获取子网信息
                info = get_subnet_info(subnet)
                self.merge_result_tree.insert("", tk.END, values=(
                    subnet,
                    info["network"],
                    info["netmask"],
                    info["broadcast"],
                    info["usable_addresses"]
                ))
                

            
        except ValueError as e:
            self.show_info("错误", f"合并失败: {str(e)}")
        except Exception as e:
            self.show_info("错误", f"操作失败: {str(e)}")
        
    def execute_ipv6_info(self):
        """执行IPv6地址信息查询"""
        try:
            # 清空结果树
            for item in self.ipv6_info_tree.get_children():
                self.ipv6_info_tree.delete(item)
            
            ipv6 = self.ipv6_info_entry.get().strip()
            if not ipv6:
                self.show_info("提示", "请输入IPv6地址")
                return
            
            # 获取CIDR
            cidr = self.ipv6_cidr_var.get()
            
            # 构造网络地址
            network_str = f"{ipv6}/{cidr}"
            
            # 获取IPv6信息
            ipv6_info = get_ip_info(network_str)
            
            # 分组显示结果
            # 1. 基本信息
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("ip_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("IP版本", ipv6_info.get("version", "")))
            # 分析IPv6地址类型
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
            # 添加IPv4映射地址检测
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
            
            # 2. 地址格式
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址格式", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("压缩格式", ipv6_info.get("compressed", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("展开格式", ipv6_info.get("exploded", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("反向DNS格式", ipv6_info.get("reverse_dns", "")))
            
            # 添加IPv4映射地址转换（如果适用）
            if "::ffff:" in ip_address:
                ipv4_part = ip_address.split("::ffff:")[-1]
                self.ipv6_info_tree.insert("", tk.END, values=("映射的IPv4地址", ipv4_part))
            
            # 3. 地址属性
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址属性", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("是否全局可路由", "是" if ipv6_info.get("is_global") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否私有地址", "是" if ipv6_info.get("is_private") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否链路本地", "是" if ipv6_info.get("is_link_local") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否回环地址", "是" if ipv6_info.get("is_loopback") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否组播地址", "是" if ipv6_info.get("is_multicast") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否未指定地址", "是" if ipv6_info.get("is_unspecified") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否保留地址", "是" if ipv6_info.get("is_reserved") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否IPv4映射", "是" if "::ffff:" in ip_address else "否"))
            
            # 4. 地址结构分析
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址结构分析", ""))
            
            # 分析前缀类型
            prefix_analysis = ""
            if ipv6_info.get("is_multicast"):
                prefix_analysis = "多播地址前缀"
                # 进一步分析多播地址类型
                if ip_address.startswith("ff01:"):
                    prefix_analysis += " (接口本地多播)"
                elif ip_address.startswith("ff02:"):
                    prefix_analysis += " (链路本地多播)"
                elif ip_address.startswith("ff05:"):
                    prefix_analysis += " (站点本地多播)"
                elif ip_address.startswith("ff0e:"):
                    prefix_analysis += " (全球多播)"
            elif ip_address.startswith("fe80:"):
                prefix_analysis = "链路本地前缀 (fe80::/10)"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                prefix_analysis = "唯一本地地址前缀 (fc00::/7)"
            elif ip_address.startswith("2000:"):
                prefix_analysis = "全球单播地址前缀 (2000::/3)"
            elif ip_address == "::1":
                prefix_analysis = "回环地址 (::1/128)"
            elif ip_address == "::":
                prefix_analysis = "未指定地址 (::/128)"
            self.ipv6_info_tree.insert("", tk.END, values=("前缀分析", prefix_analysis))
            
            # 分析地址结构
            segments = ip_address.split(":")
            if len(segments) > 1:
                self.ipv6_info_tree.insert("", tk.END, values=("地址段数量", f"{len(segments)}"))
            
            # 5. 二进制表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("二进制表示", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("binary", "")))
            
            # 计算并显示子网掩码的二进制表示
            if ipv6_info.get("subnet_mask"):
                subnet_mask = ipv6_info["subnet_mask"]
                subnet_bin = subnet_mask.replace(':', '').zfill(32)
                subnet_bin_grouped = ' '.join([subnet_bin[i:i+4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", subnet_bin_grouped))
            
            # 计算并显示网络地址的二进制表示
            if ipv6_info.get("network_address"):
                network_addr = ipv6_info["network_address"]
                network_bin = network_addr.replace(':', '').zfill(32)
                network_bin_grouped = ' '.join([network_bin[i:i+4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("网络地址", network_bin_grouped))
            
            # 计算并显示广播地址的二进制表示
            if ipv6_info.get("broadcast_address"):
                broadcast_addr = ipv6_info["broadcast_address"]
                broadcast_bin = broadcast_addr.replace(':', '').zfill(32)
                broadcast_bin_grouped = ' '.join([broadcast_bin[i:i+4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("广播地址", broadcast_bin_grouped))
            
            # 6. 十六进制表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("十六进制表示", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("hexadecimal", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("网络地址", ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("广播地址", ipv6_info.get("broadcast_address", "")))
            
            # 7. 十进制数值表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("十进制数值表示", ""))
            if "integer" in ipv6_info:
                self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info["integer"]))
            
            # 计算并显示子网掩码的十进制数值
            if ipv6_info.get("subnet_mask"):
                subnet_mask = ipv6_info["subnet_mask"]
                subnet_int = int(ipaddress.IPv6Address(subnet_mask))
                self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", subnet_int))
            
            # 计算并显示网络地址的十进制数值
            if ipv6_info.get("network_address"):
                network_addr = ipv6_info["network_address"]
                network_int = int(ipaddress.IPv6Address(network_addr))
                self.ipv6_info_tree.insert("", tk.END, values=("网络地址", network_int))
            
            # 计算并显示广播地址的十进制数值
            if ipv6_info.get("broadcast_address"):
                broadcast_addr = ipv6_info["broadcast_address"]
                broadcast_int = int(ipaddress.IPv6Address(broadcast_addr))
                self.ipv6_info_tree.insert("", tk.END, values=("广播地址", broadcast_int))
            
            # 8. 地址段详情
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址段详情", ""))
            exploded = ipv6_info.get("exploded", "")
            if exploded:
                segments = exploded.split(":")
            else:
                # 处理全0压缩的情况
                segments = ["0000"] * 8
            
            for i, segment in enumerate(segments):
                if segment:  # 跳过空段（压缩的0）
                    # 十六进制到十进制转换
                    dec_value = int(segment, 16)
                    # 十六进制到二进制转换，补全16位
                    bin_value = f"{dec_value:016b}"
                    self.ipv6_info_tree.insert("", tk.END, values=(f"第{i+1}段", f"{segment} (十六进制) = {dec_value} (十进制) = {bin_value} (二进制)"))
                else:
                    # 处理空段（压缩的0）
                    self.ipv6_info_tree.insert("", tk.END, values=(f"第{i+1}段", f"0000 (十六进制) = 0 (十进制) = 0000000000000000 (二进制)"))
            
            # 6. 网络规模与用途
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("网络规模与用途", ""))
            
            # 子网规模描述
            total_hosts = ipv6_info.get("total_hosts", 0)
            size_desc = ""
            if total_hosts <= 1:
                size_desc = "单主机地址（/128前缀）"
            elif total_hosts <= 65536:
                size_desc = "小型网络（/64前缀）"
            elif total_hosts <= 4294967296:
                size_desc = "中型网络（/48前缀）"
            else:
                size_desc = "大型网络（/32或更短前缀）"
            self.ipv6_info_tree.insert("", tk.END, values=("子网规模", size_desc))
            
            # IP地址用途描述
            usage_desc = ""
            if ipv6_info.get("is_loopback"):
                usage_desc = "用于本地主机测试和诊断"
            elif ipv6_info.get("is_link_local"):
                usage_desc = "用于同一链路内的设备通信，无需路由器"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                usage_desc = "用于内部网络通信，不可路由到公网"
            elif ip_address.startswith("2000:"):
                usage_desc = "可在全球范围内路由，用于公网通信"
            elif ipv6_info.get("is_multicast"):
                usage_desc = "用于一对多通信，支持组播应用"
            elif "::ffff:" in ip_address:
                usage_desc = "用于在IPv6网络中表示IPv4地址"
            self.ipv6_info_tree.insert("", tk.END, values=("主要用途", usage_desc))
            
            # 7. 配置建议
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("配置建议", ""))
            
            advice = ""
            if ipv6_info.get("is_global"):
                advice = "建议配置防火墙规则，限制不必要的入站访问"
            elif ipv6_info.get("is_private"):
                advice = "建议使用SLAAC或DHCPv6自动分配地址"
            if ipv6_info.get("prefix_length", 0) < 64:
                advice += "\n建议为终端设备分配/64前缀，符合IPv6最佳实践"
            self.ipv6_info_tree.insert("", tk.END, values=("网络配置", advice))
            
            # 8. RFC标准参考
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("RFC标准参考", ""))
            
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
            
            # 6. 扩展信息
            has_extended_info = False
            
            # 检查是否为IPv4映射地址
            if ip_address.startswith("::ffff:"):
                ipv4_mapped = ip_address.replace("::ffff:", "")
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""))
                self.ipv6_info_tree.insert("", tk.END, values=("IPv4映射地址", ipv4_mapped))
                has_extended_info = True
            # 检查是否为文档/测试地址
            elif ip_address.startswith("2001:0db8:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "文档/测试地址 (RFC 3849)"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 3849 - IPv6文档地址分配"))
                has_extended_info = True
            # 检查是否为唯一本地地址 (ULA)
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "唯一本地地址 (ULA)"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 4193 - IPv6唯一本地地址"))
                has_extended_info = True
            # 检查是否为链路本地地址
            elif ip_address.startswith("fe80:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "链路本地地址"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 4291 - IPv6寻址架构"))
                has_extended_info = True
            # 检查是否为组播地址
            elif ipv6_info.get("is_multicast"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=("扩展信息", ""))
                self.ipv6_info_tree.insert("", tk.END, values=("地址用途", "组播地址"))
                self.ipv6_info_tree.insert("", tk.END, values=("RFC规范", "RFC 4291 - IPv6寻址架构"))
                has_extended_info = True
            
        except ValueError as e:
            self.show_info("错误", f"查询失败: {str(e)}")
        except Exception as e:
            self.show_info("错误", f"操作失败: {str(e)}")
    def execute_ipv4_info(self):
        """执行IPv4地址信息查询"""
        try:
            # 清空结果树
            for item in self.ip_info_tree.get_children():
                self.ip_info_tree.delete(item)
            
            ip = self.ip_info_entry.get().strip()
            if not ip:
                self.show_info("提示", "请输入IP地址")
                return
            
            # 获取子网掩码和CIDR
            subnet_mask = self.ip_mask_var.get()
            cidr = self.ip_cidr_var.get()
            
            # 优先使用CIDR，如果没有则使用子网掩码
            network_str = None
            if cidr:
                try:
                    network_str = f"{ip}/{cidr}"
                except:
                    pass
            
            if not network_str and subnet_mask:
                try:
                    # 转换子网掩码为CIDR
                    mask_int = ip_to_int(subnet_mask)
                    prefix_len = bin(mask_int).count('1')
                    network_str = f"{ip}/{prefix_len}"
                except:
                    pass
            
            # 如果无法构造网络地址，只显示基本IP信息
            basic_info = True
            subnet_info = None
            
            if network_str:
                try:
                    # 获取子网信息
                    subnet_info = get_subnet_info(network_str)
                    basic_info = False
                except:
                    pass
            
            # 获取基本IP信息
            info = get_ip_info(ip)
            
            # 显示结果
            if not basic_info and subnet_info:
                # 显示子网相关信息 - 采用分组显示
                # 1. 基本网络信息
                self.ip_info_tree.insert("", tk.END, values=("IP地址", ip))
                self.ip_info_tree.insert("", tk.END, values=("子网掩码", subnet_info["netmask"]))
                # 添加通配符掩码
                wildcard_mask = '.'.join(str(255 - int(octet)) for octet in subnet_info["netmask"].split('.'))
                self.ip_info_tree.insert("", tk.END, values=("通配符掩码", wildcard_mask))
                self.ip_info_tree.insert("", tk.END, values=("CIDR", subnet_info["cidr"]))
                self.ip_info_tree.insert("", tk.END, values=("网络类别", info.get("class", "") + "类"))
                self.ip_info_tree.insert("", tk.END, values=("默认子网掩码", info.get("default_netmask", "")))
                
                # 2. 地址范围信息
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("地址范围", ""))
                self.ip_info_tree.insert("", tk.END, values=("网络地址", subnet_info["network"]))
                self.ip_info_tree.insert("", tk.END, values=("广播地址", subnet_info["broadcast"]))
                self.ip_info_tree.insert("", tk.END, values=("第一个可用地址", subnet_info["host_range_start"]))
                self.ip_info_tree.insert("", tk.END, values=("最后一个可用地址", subnet_info["host_range_end"]))
                self.ip_info_tree.insert("", tk.END, values=("可用主机数", subnet_info["usable_addresses"]))
                self.ip_info_tree.insert("", tk.END, values=("总主机数", subnet_info["num_addresses"]))
                
                # 二进制表示
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("二进制表示", ""))
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info["binary"]))
                self.ip_info_tree.insert("", tk.END, values=("子网掩码", '.'.join(f'{int(octet):08b}' for octet in subnet_info["netmask"].split('.'))))
                self.ip_info_tree.insert("", tk.END, values=("通配符掩码", '.'.join(f'{255 - int(octet):08b}' for octet in subnet_info["netmask"].split('.'))))
                self.ip_info_tree.insert("", tk.END, values=("网络地址", '.'.join(f'{int(octet):08b}' for octet in subnet_info["network"].split('.'))))
                self.ip_info_tree.insert("", tk.END, values=("广播地址", '.'.join(f'{int(octet):08b}' for octet in subnet_info["broadcast"].split('.'))))
                
                # 十六进制表示
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("十六进制表示", ""))
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info["hexadecimal"]))
                self.ip_info_tree.insert("", tk.END, values=("子网掩码", '.'.join(f'{int(octet):02x}' for octet in subnet_info["netmask"].split('.'))))
                self.ip_info_tree.insert("", tk.END, values=("通配符掩码", '.'.join(f'{255 - int(octet):02x}' for octet in subnet_info["netmask"].split('.'))))
                self.ip_info_tree.insert("", tk.END, values=("网络地址", '.'.join(f'{int(octet):02x}' for octet in subnet_info["network"].split('.'))))
                self.ip_info_tree.insert("", tk.END, values=("广播地址", '.'.join(f'{int(octet):02x}' for octet in subnet_info["broadcast"].split('.'))))
                
                # 6. 十进制数值表示
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("十进制数值表示", ""))
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info["integer"]))
                self.ip_info_tree.insert("", tk.END, values=("子网掩码", str(ip_to_int(subnet_info["netmask"]))))
                wildcard_int = ip_to_int('.'.join(str(255 - int(octet)) for octet in subnet_info["netmask"].split('.')))
                self.ip_info_tree.insert("", tk.END, values=("通配符掩码", str(wildcard_int)))
                self.ip_info_tree.insert("", tk.END, values=("网络地址", str(ip_to_int(subnet_info["network"]))))
                self.ip_info_tree.insert("", tk.END, values=("广播地址", str(ip_to_int(subnet_info["broadcast"]))))
                
                # 7. IP属性
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("IP属性", ""))
                self.ip_info_tree.insert("", tk.END, values=("IP版本", info["version"]))
                self.ip_info_tree.insert("", tk.END, values=("是否私有IP", "是" if info["is_private"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否保留IP", "是" if info["is_reserved"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否回环地址", "是" if info["is_loopback"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否组播地址", "是" if info["is_multicast"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否全局可路由", "是" if info["is_global"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否链路本地地址", "是" if info["is_link_local"] else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否未指定地址", "是" if info["is_unspecified"] else "否"))
                
                # 8. 扩展信息
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("扩展信息", ""))
                
                # IP地址用途描述
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
                
                # 子网大小描述
                subnet_size = subnet_info["usable_addresses"]
                size_desc = ""
                if subnet_size <= 254:
                    size_desc = "小型网络，适合家庭或小型办公室"
                elif subnet_size <= 65534:
                    size_desc = "中型网络，适合企业或校园网络"
                else:
                    size_desc = "大型网络，适合大型机构或运营商"
                self.ip_info_tree.insert("", tk.END, values=("子网规模", size_desc))
                
                # 网络配置建议
                config_advice = ""
                if subnet_size > 65534:
                    config_advice = "建议划分为多个子网，便于管理和减少广播域"
                elif info["is_private"]:
                    config_advice = "建议使用DHCP服务器自动分配IP地址"
                else:
                    config_advice = "建议配置静态路由和防火墙规则"
                self.ip_info_tree.insert("", tk.END, values=("配置建议", config_advice))
            else:
                # 只显示基本IP信息，采用分组显示
                # 1. 基本信息
                self.ip_info_tree.insert("", tk.END, values=("IP地址", info.get("ip_address", ip)))
                self.ip_info_tree.insert("", tk.END, values=("IP版本", info.get("version", "")))
                self.ip_info_tree.insert("", tk.END, values=("网络类别", info.get("class", "") + "类"))
                self.ip_info_tree.insert("", tk.END, values=("默认子网掩码", info.get("default_netmask", "")))
                
                # 2. 数值表示
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("数值表示", ""))
                self.ip_info_tree.insert("", tk.END, values=("二进制表示", info.get("binary", "")))
                self.ip_info_tree.insert("", tk.END, values=("十六进制表示", info.get("hexadecimal", "")))
                self.ip_info_tree.insert("", tk.END, values=("整数表示", info.get("integer", "")))
                
                # 3. IP属性
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("IP属性", ""))
                self.ip_info_tree.insert("", tk.END, values=("是否私有IP", "是" if info.get("is_private", False) else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否保留IP", "是" if info.get("is_reserved", False) else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否回环地址", "是" if info.get("is_loopback", False) else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否组播地址", "是" if info.get("is_multicast", False) else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否全局可路由", "是" if info.get("is_global", False) else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否链路本地地址", "是" if info.get("is_link_local", False) else "否"))
                self.ip_info_tree.insert("", tk.END, values=("是否未指定地址", "是" if info.get("is_unspecified", False) else "否"))
                
                # 4. 扩展信息
                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=("扩展信息", ""))
                
                # IP地址用途描述
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
                
                # 网络配置建议
                config_advice = ""
                if info.get("is_private", False):
                    config_advice = "建议使用DHCP服务器自动分配IP地址"
                else:
                    config_advice = "建议配置静态路由和防火墙规则"
                self.ip_info_tree.insert("", tk.END, values=("配置建议", config_advice))
                
        except ValueError as e:
            self.show_info("错误", f"查询失败: {str(e)}")
        except Exception as e:
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
            for cidr in cidr_list:
                # 获取子网信息
                info = get_subnet_info(cidr)
                self.merge_result_tree.insert("", tk.END, values=(
                    cidr,
                    info["network"],
                    info["netmask"],
                    info["broadcast"],
                    info["usable_addresses"]
                ))
                

            
        except ValueError as e:
            self.show_info("错误", f"转换失败: {str(e)}")
        except Exception as e:
            self.show_info("错误", f"操作失败: {str(e)}")
    
    def update_ipv4_history(self, event=None):
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
    
    def update_ipv6_history(self, event=None):
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
    
    def update_range_start_history(self, event=None):
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
    
    def update_range_end_history(self, event=None):
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
    
    def on_subnet_mask_change(self, event):
        """当子网掩码改变时，更新CIDR值"""
        selected_mask = self.ip_mask_var.get()
        if selected_mask in self.subnet_mask_cidr_map:
            cidr = self.subnet_mask_cidr_map[selected_mask]
            self.ip_cidr_var.set(cidr)
    
    def on_cidr_change(self, event):
        """当CIDR改变时，更新子网掩码值"""
        selected_cidr = self.ip_cidr_var.get()
        if selected_cidr in self.cidr_subnet_mask_map:
            subnet_mask = self.cidr_subnet_mask_map[selected_cidr]
            self.ip_mask_var.set(subnet_mask)
            
    def execute_check_overlap(self):
        """执行子网重叠检测"""
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
            if overlaps:
                for overlap in overlaps:
                    subnet1 = overlap.get("subnet1", "")
                    subnet2 = overlap.get("subnet2", "")
                    overlap_type = overlap.get("type", "重叠")
                    
                    self.overlap_result_tree.insert("", tk.END, values=(
                        "重叠",
                        f"{subnet1} 与 {subnet2} 发生 {overlap_type}"
                    ))

            else:
                self.overlap_result_tree.insert("", tk.END, values=(
                    "正常",
                    "所有子网之间没有重叠"
                ))

                
        except ValueError as e:
            self.show_info("错误", f"检测失败: {str(e)}")
        except Exception as e:
            self.show_info("错误", f"操作失败: {str(e)}")
        
    def toggle_test_info_bar(self, event=None):
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
        x = root_x + (root_width - dialog_width) // 2
        y = root_y + (root_height - dialog_height) // 2
        
        # 设置对话框大小和位置
        test_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
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
        success_btn = ttk.Button(button_frame, text="测试正确信息", width=button_width, 
                                style=button_style, command=lambda: self.show_result("测试正确信息：操作成功！", error=False))
        success_btn.grid(row=0, column=0, padx=5, pady=5)
        
        error_btn = ttk.Button(button_frame, text="测试错误信息", width=button_width, 
                              style=button_style, command=lambda: self.show_result("测试错误信息：操作失败！", error=True, keep_data=True))
        error_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # 第二行按钮
        long_text = "测试长文本信息：这是一条非常长的测试信息，用于测试信息栏的文本截断功能。" * 3
        long_text_btn = ttk.Button(button_frame, text="测试长文本信息", width=button_width, 
                                  style=button_style, command=lambda: self.show_result(long_text, error=False))
        long_text_btn.grid(row=1, column=0, padx=5, pady=5)
        
        # 中英文混排长文本测试按钮
        mixed_text = "中英文混排测试：This is a long text with mixed Chinese and English characters. 这是一条包含中英文混合的长文本，用于测试信息栏的截断功能。" * 2
        mixed_text_btn = ttk.Button(button_frame, text="测试中英文混排", width=button_width, 
                                  style=button_style, command=lambda: self.show_result(mixed_text, error=False))
        mixed_text_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # 添加第三行按钮：隐藏信息栏和清空结果
        hide_info_btn = ttk.Button(button_frame, text="隐藏信息栏", width=button_width, 
                                style=button_style, command=self.hide_info_bar)
        hide_info_btn.grid(row=2, column=0, padx=5, pady=5)
        
        clear_result_btn = ttk.Button(button_frame, text="清空子网切分", width=button_width, 
                                    style=button_style, command=self.clear_result)
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
        theme_combobox = ttk.Combobox(theme_frame, textvariable=self.theme_var, 
                                     values=theme_list, state="readonly")
        theme_combobox.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # 主题切换函数
        def switch_theme():
            new_theme = self.theme_var.get()
            try:
                # 使用系统内置主题切换，彻底移除sv-ttk，解决黑色底色问题
                self.style.theme_use(new_theme)
                # 重新配置Treeview样式，确保在新主题下表格线仍然可见
                tree_names = ['split_tree', 'remaining_tree', 'allocated_tree', 'planning_remaining_tree', 'pool_tree', 'requirements_tree', 'history_tree']
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
            except Exception as e:
                print(f"主题切换出错: {e}")
                # 出错时恢复到默认主题
                self.style.theme_use("vista")
        
        # 创建应用主题按钮
        theme_switch_btn = ttk.Button(theme_frame, text="应用主题", width=button_width, 
                                     style=button_style, command=switch_theme)
        theme_switch_btn.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # 关闭按钮框架
        close_frame = ttk.Frame(content_frame)
        close_frame.grid(row=4, column=0, sticky=tk.EW, pady=(15, 0))
        close_frame.grid_columnconfigure(0, weight=1)  # 左侧空白区域扩展
        
        # 添加关闭按钮到右下角
        close_btn = ttk.Button(close_frame, text="关闭", width=button_width, 
                              style=button_style, command=test_dialog.destroy)
        close_btn.grid(row=0, column=1, padx=5)

    def show_result(self, text, error=False, keep_data=False, message_type="info"):
        """显示结果
        
        Args:
            text: 要显示的文本
            error: 是否为错误信息
            keep_data: 是否保留数据
            message_type: 信息类型（info, success, error等）
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
        # 基于像素宽度的文本截断算法，解决英文不等宽问题
        # 使用tkinter的Font.measure方法计算实际显示宽度

        # 创建字体对象，用于测量文本宽度
        
        try:
            font = tkfont.Font(family="微软雅黑", size=9)
        except Exception:
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
            
            # 注释掉调试信息，避免在生产环境中显示
            # print(f"\n--- 文本截断调试信息 ---")
            # print(f"原始文本长度: {len(text)}")
            # print(f"图标宽度: {icon_width}px")
            # print(f"最大像素宽度: {max_pixel_width}px")
            # print(f"可用宽度: {available_width}px")
            # print(f"完整文本宽度: {full_width}px")
            # print(f"是否需要截断: {full_width > max_pixel_width}")
            
            if full_width <= max_pixel_width:
                return text

            # 二分查找合适的截断位置
            low = 0
            high = len(text)
            best_length = 0

            while low <= high:
                mid = (low + high) // 2
                current_text = text[:mid]
                current_width = calculate_pixel_width(current_text)

                if current_width <= available_width:
                    best_length = mid
                    low = mid + 1
                else:
                    high = mid - 1

            # 确保截断后的文本不会过长
            truncated = text[:best_length]
            # 计算省略号的宽度
            ellipsis_width = calculate_pixel_width("...")

            # 调整截断位置，确保加上省略号和图标后不会超过最大宽度
            while best_length > 0:
                truncated = text[:best_length]
                truncated_width = calculate_pixel_width(truncated) + ellipsis_width + icon_width
                if truncated_width <= max_pixel_width:
                    return truncated + "..."
                best_length -= 1

            return "..."

        # 获取信息栏的实际宽度
        root_width = self.root.winfo_width()
        
        info_bar_width = root_width - self.INFO_BAR_LEFT_OFFSET - self.INFO_BAR_RIGHT_OFFSET - self.INFO_BAR_PADDING  # 与信息栏宽度计算保持一致
        if info_bar_width < self.MIN_INFO_BAR_WIDTH:
            info_bar_width = self.MIN_INFO_BAR_WIDTH
        
        # 设置最大像素宽度（考虑信息栏的实际宽度、关闭按钮宽度和内边距）
        # 减少内边距预留，增加两个中文字符宽度（约32px），让文本可以多显示一些字符
        # 增加可用宽度，让文本可以多显示两个中文字符
        max_pixel_width = info_bar_width - 5 - self.CLOSE_BTN_WIDTH  # 减去5px内边距和关闭按钮宽度
        
        # 确保最大像素宽度为正数
        if max_pixel_width < self.MIN_PIXEL_WIDTH:
            max_pixel_width = self.MIN_PIXEL_WIDTH
            
        truncated_text = truncate_text_by_pixel(text, icon, max_pixel_width)

        # 显示完整文本（带有图标）
        self.info_label.config(text=icon + truncated_text, style=label_style)
        self.info_bar_frame.configure(style=frame_style)

        # 显示信息栏 - 使用place布局，放置在顶部标签栏右侧红框位置，宽度适配子网规划到钉住按钮的距离
        # 计算信息栏位置和宽度
        info_bar_width = root_width - self.INFO_BAR_PLACE_LEFT - self.INFO_BAR_PLACE_RIGHT  # 右侧偏移量改为136px
        # 增加最小宽度，确保信息栏不会过窄
        if info_bar_width < self.MIN_INFO_BAR_PLACE_WIDTH:  # 增加最小宽度为300px
            info_bar_width = self.MIN_INFO_BAR_PLACE_WIDTH
        
        if self.info_bar_frame.winfo_manager() == "":
            # 恢复原始位置：顶部标签栏右侧，y=21.5，高度30px，与标签页按钮底部对齐
            self.info_bar_frame.place(x=self.INFO_BAR_PLACE_LEFT, y=self.INFO_BAR_PLACE_Y, width=info_bar_width, height=self.INFO_BAR_PLACE_HEIGHT)
        else:
            # 如果已经显示，确保位置和宽度正确
            # 恢复原始高度和位置
            self.info_bar_frame.place_configure(x=self.INFO_BAR_PLACE_LEFT, y=self.INFO_BAR_PLACE_Y, width=info_bar_width, height=self.INFO_BAR_PLACE_HEIGHT)

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
            colors = [
                "#4caf50",
                "#ff9800",
                "#f44336",
                "#9c27b0",
                "#00bcd4",
                "#795548",
                "#ffeb3b",
                "#607d8b",
            ]  # 现代化颜色列表
            for index, subnet in enumerate(remaining_subnets):
                subnet_start = ip_to_int(subnet.get("network", "0.0.0.0"))
                subnet_end = ip_to_int(subnet.get("broadcast", "0.0.0.0"))
                self.chart_data["networks"].append(
                    {
                        "start": subnet_start,
                        "end": subnet_end,
                        "range": subnet_end - subnet_start + 1,
                        "name": subnet.get("cidr", ""),
                        "color": colors[index % len(colors)],  # 循环使用颜色
                        "type": "remaining",
                    }
                )

            # 按起始地址排序
            self.chart_data["networks"].sort(key=lambda x: x["start"])
        except Exception:
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
        stroke_width=1.5,
        letter_spacing=1.5,
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
            stroke_width: 描边宽度
            letter_spacing: 字间距
        """
        try:
            # 使用4个方向的基础描边，平衡性能和可读性
            offset = 1  # 描边偏移量

            # 绘制4个方向的描边
            self.chart_canvas.create_text(x - offset, y, text=text, font=font, anchor=anchor, fill=stroke_color)
            self.chart_canvas.create_text(x + offset, y, text=text, font=font, anchor=anchor, fill=stroke_color)
            self.chart_canvas.create_text(x, y - offset, text=text, font=font, anchor=anchor, fill=stroke_color)
            self.chart_canvas.create_text(x, y + offset, text=text, font=font, anchor=anchor, fill=stroke_color)

            # 绘制主文字
            self.chart_canvas.create_text(x, y, text=text, font=font, anchor=anchor, fill=fill)
        except (AttributeError, ValueError) as e:
            # 出错时直接绘制文字，不添加描边
            self.chart_canvas.create_text(x, y, text=text, font=font, anchor=anchor, fill=fill)



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
            parent_height = self.chart_frame.winfo_height()
            
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
            subnet_colors = [
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
            ]

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

        except Exception as e:
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
            # 使用文件对话框，支持多种格式
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
                return  # 用户取消了保存

            # 获取文件扩展名


            file_ext = os.path.splitext(file_path)[1].lower()

            # 准备数据
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
            
            # 二次去重：确保所有数据行都是唯一的，解决切分网段信息重复的问题
            print(f"main_data原始长度: {len(main_data)}")
            unique_main_data = []
            seen_rows = set()
            for row in main_data:
                # 将行转换为可哈希的元组
                row_tuple = tuple(row)
                if row_tuple not in seen_rows:
                    seen_rows.add(row_tuple)
                    unique_main_data.append(row)
            main_data = unique_main_data
            print(f"main_data去重后长度: {len(main_data)}")

            # 准备剩余数据
            remaining_tree = data_source["remaining_tree"]
            remaining_headers = [remaining_tree.heading(col, "text") or "" for col in remaining_tree["columns"]]
            remaining_data = []
            for item in remaining_tree.get_children():
                values = remaining_tree.item(item, "values")
                if values:
                    remaining_data.append(dict(zip(remaining_headers, values)))

            # 根据文件扩展名选择导出格式
            if file_ext == ".json":
                # JSON格式导出
    

                if data_source["main_name"] == "切分网段信息":
                    # 子网切分结果特殊处理
                    export_data = {"split_info": dict(main_data), "remaining_subnets": remaining_data}
                else:
                    # 子网规划结果格式
                    export_data = {
                        f"{data_source['main_name']}": [dict(zip(main_headers, item)) for item in main_data],
                        "remaining_subnets": remaining_data,
                    }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

            elif file_ext == ".txt":
                # 文本格式导出
                with open(file_path, "w", encoding="utf-8") as f:
                    # 写入主数据
                    f.write(f"{data_source['main_name']}\n")
                    f.write("=" * 80 + "\n")

                    # 如果是键值对格式（如切分网段信息）
                    if len(main_headers) == 2 and main_headers[0] == "项目" and main_headers[1] == "值":
                        for values in main_data:
                            f.write(f"{values[0]:<20}: {values[1]}\n")
                    else:
                        # 写入列标题
                        for header in main_headers:
                            f.write(f"{header:<15}")
                        f.write("\n")
                        f.write("-" * 80 + "\n")

                        # 写入数据
                        for values in main_data:
                            for value in values:
                                f.write(f"{str(value):<15}")
                            f.write("\n")

                    # 写入剩余数据
                    f.write(f"\n\n{data_source['remaining_name']}\n")
                    f.write("=" * 80 + "\n")

                    # 写入剩余数据列标题
                    for header in remaining_headers:
                        f.write(f"{header:<15}")
                    f.write("\n")
                    f.write("-" * 80 + "\n")

                    # 写入剩余数据
                    for item in remaining_tree.get_children():
                        values = remaining_tree.item(item, "values")
                        for value in values:
                            f.write(f"{str(value):<15}")
                        f.write("\n")

            elif file_ext == ".pdf":
                # PDF格式导出
                try:
                    print("\n=== PDF导出调试信息 ===")
                    print(f"文件路径: {file_path}")
                    print(f"文件扩展名: {file_ext}")
                    print("进入PDF导出分支")
    
    
                    from reportlab.platypus import (
                        Table,
                        TableStyle,
                        Paragraph,
                        Spacer,
                    )
    
    
    
    
    
                except ImportError as e:
                    # 处理reportlab库缺失的情况
                    error_msg = f"导出PDF失败: 缺少必要的库 '{e.name}'。请安装reportlab库后重试。\n\n安装命令: pip install reportlab --timeout 120"
                    self.show_result(error_msg, error=True)
                    return None

                # 注册中文字体
                print("调用register_chinese_fonts()")
                self.has_chinese_font = self.register_chinese_fonts()
                print(f"中文字体注册结果: {self.has_chinese_font}")

                # 创建PDF文档，使用BaseDocTemplate以支持多页面模板
                print("创建PDF文档对象")

                
                # 设置页面边距
                margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)  # 左、右、上、下
                
                # 创建BaseDocTemplate，默认使用横向A4
                doc = BaseDocTemplate(
                    file_path,
                    pagesize=landscape(A4),  # 默认横向
                    leftMargin=margins[0],
                    rightMargin=margins[1],
                    topMargin=margins[2],
                    bottomMargin=margins[3],
                    showBoundary=False,
                )
                print("PDF文档对象创建成功")
                
                # 创建页面模板
                # 1. 横向页面模板
                landscape_width, landscape_height = landscape(A4)
                landscape_frame = Frame(
                    margins[0],
                    margins[3],
                    landscape_width - margins[0] - margins[1],
                    landscape_height - margins[2] - margins[3],
                    id='landscape_frame'
                )
                landscape_template = PageTemplate(id='landscape', frames=[landscape_frame])
                
                # 2. 纵向页面模板
                portrait_width, portrait_height = A4  # A4默认纵向
                portrait_frame = Frame(
                    margins[0],
                    margins[3],
                    portrait_width - margins[0] - margins[1],
                    portrait_height - margins[2] - margins[3],
                    id='portrait_frame'
                )
                portrait_template = PageTemplate(id='portrait', frames=[portrait_frame], pagesize=A4)
                
                # 添加页面模板
                doc.addPageTemplates([landscape_template, portrait_template])
                
                # 定义页面宽度变量，初始使用横向页面尺寸
                page_width = landscape_width
                
                elements = []
                styles = getSampleStyleSheet()
                print("创建样式表成功")

                # 创建支持中文的标题样式
                title_style = ParagraphStyle(
                    "ChineseTitle",
                    parent=styles["Title"],
                    fontName="ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                    fontSize=20,
                    textColor=colors.HexColor("#2c3e50"),  # 深蓝灰色
                    alignment=TA_CENTER,  # 居中对齐
                    spaceAfter=20,
                )

                # 创建支持中文的一级标题样式
                heading2_style = ParagraphStyle(
                    "ChineseHeading2",
                    parent=styles["Heading2"],
                    fontName="ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                    fontSize=16,
                    textColor=colors.HexColor("#34495e"),  # 深灰色
                    alignment=TA_LEFT,
                    spaceBefore=20,
                    spaceAfter=12,
                )

                # 创建支持中文的正文样式
                normal_style = ParagraphStyle(
                    "ChineseNormal",
                    parent=styles["Normal"],
                    fontName="ChineseFont" if self.has_chinese_font else "Helvetica",
                    fontSize=11,
                    textColor=colors.HexColor("#34495e"),  # 深灰色
                    spaceAfter=5,
                )

                # 创建支持中文的表格文本样式
                table_text_style = ParagraphStyle(
                    "ChineseTableText",
                    parent=styles["Normal"],
                    fontName="ChineseFont" if self.has_chinese_font else "Helvetica",
                    fontSize=10,
                    alignment=TA_CENTER,  # 居中对齐
                )

                # 添加标题
                elements.append(Paragraph(data_source["pdf_title"], title_style))
                elements.append(Spacer(1, 10))

                # 添加导出时间信息
                export_time = time.strftime("%Y年%m月%d日 %H:%M:%S")
                elements.append(Paragraph(f"导出时间: {export_time}", normal_style))
                elements.append(Spacer(1, 15))

                # 添加主数据信息
                elements.append(Paragraph(data_source["main_name"], heading2_style))

                # 如果是键值对格式（如切分网段信息）
                if len(main_headers) == 2 and main_headers[0] == "项目" and main_headers[1] == "值":
                    main_table_data = [["项目", "值"]]
                    for values in main_data:
                        main_table_data.append(
                            [
                                Paragraph(str(values[0]) if values[0] is not None else "", table_text_style),
                                Paragraph(str(values[1]) if values[1] is not None else "", table_text_style),
                            ]
                        )
                else:
                    main_table_data = [[Paragraph(h, table_text_style) for h in main_headers]]
                    for values in main_data:
                        main_table_data.append(
                            [Paragraph(str(v) if v is not None else "", table_text_style) for v in values]
                        )

                if len(main_table_data) > 1:
                    # 计算表格宽度（页宽减去左右边距）
                    table_width = page_width - margins[0] - margins[1]

                    # 确定表格列数
                    table_cols = len(main_table_data[0])

                    # 使用指定的列宽或默认列宽
                    col_widths = data_source.get("main_table_cols")

                    # 处理字符串格式的列宽配置，如"1:1:1:1:1:1:1:1:1"
                    if isinstance(col_widths, str):
                        try:
                            # 尝试将字符串按冒号分割并转换为数字列表
                            col_ratios = [float(w) for w in col_widths.split(":")]
                            # 如果所有比例值都很小（< 10），将其解释为比例而不是直接宽度
                            if all(ratio < 10 for ratio in col_ratios):
                                # 计算总比例
                                total_ratio = sum(col_ratios)
                                if total_ratio > 0:
                                    # 根据比例分配实际宽度
                                    col_widths = [table_width * (ratio / total_ratio) for ratio in col_ratios]
                                else:
                                    # 如果总比例为0，使用默认列宽
                                    col_widths = None
                            else:
                                # 否则直接使用转换后的宽度
                                col_widths = col_ratios
                        except (ValueError, TypeError):
                            # 如果转换失败，使用默认列宽
                            col_widths = None

                    if not col_widths or len(col_widths) != table_cols:
                        if len(main_headers) == 2:  # 键值对格式
                            col_widths = [table_width * 0.3, table_width * 0.7]
                        else:
                            # 默认平均分配列宽
                            col_widths = [table_width / table_cols] * table_cols
                    else:
                        # 确保所有列宽值都是有效的数字且大于0
                        processed_col_widths = []
                        for width in col_widths:
                            try:
                                # 尝试将宽度转换为数字
                                numeric_width = float(width) if width is not None else table_width / table_cols
                                if numeric_width <= 10:  # 如果宽度太小，使用默认宽度
                                    numeric_width = table_width / table_cols
                                processed_col_widths.append(numeric_width)
                            except (ValueError, TypeError):
                                # 如果转换失败，使用默认宽度
                                processed_col_widths.append(table_width / table_cols)

                        # 确保列宽数组长度与表格列数一致
                        if len(processed_col_widths) != table_cols:
                            col_widths = [table_width / table_cols] * table_cols
                        else:
                            col_widths = processed_col_widths

                    # 计算自适应列宽
                    print("\n=== 计算自适应列宽 ===")
                    try:
                        # 使用自适应列宽替换现有列宽
                        print("  调用_calculate_auto_col_widths方法")
                        auto_col_widths = self._calculate_auto_col_widths(
                            main_table_data, table_width
                        )
                        print(f"自适应列宽: {auto_col_widths}")
                        # 使用自适应列宽
                        col_widths = auto_col_widths
                    except Exception as e:
                        print(f"  计算自适应列宽错误: {type(e).__name__}: {e}")
                        traceback.print_exc()
                        # 如果自适应列宽计算失败，使用默认列宽
                        col_widths = [table_width / table_cols] * table_cols
                        print(f"  回退到默认列宽: {col_widths}")

                    # 添加调试信息
                    print("\n=== 主要表格调试信息 ===")
                    print(f"表格数据行数: {len(main_table_data)}")
                    print(f"表格列数: {table_cols}")
                    print(f"原始列宽: {col_widths}")
                    print(f"表格宽度: {table_width}")
                    print(f"表头数量: {len(main_headers)}")

                    if not col_widths or len(col_widths) != table_cols:
                        if len(main_headers) == 2:
                            print("键值对格式，使用3:7比例分配列宽")
                        else:
                            print("列宽数量不匹配，使用默认平均分配列宽")
                    else:
                        print("使用指定列宽，替换None值")

                    print(f"最终列宽: {col_widths}")
                    print("=== 主要表格调试信息结束 ===")

                    # 添加详细的调试信息，检查Table构造函数的参数
                    print("\n=== Table构造函数调试信息 ===")
                    print(f"main_table_data类型: {type(main_table_data)}")
                    print(f"main_table_data长度: {len(main_table_data)}")
                    print(f"main_table_data[0]类型: {type(main_table_data[0])}")
                    print(f"main_table_data[0]长度: {len(main_table_data[0])}")
                    print(f"colWidths类型: {type(col_widths)}")
                    print(f"colWidths长度: {len(col_widths)}")
                    print(f"colWidths内容: {col_widths}")
                    print("每个列宽的值和类型:")
                    for i, width in enumerate(col_widths):
                        print(f"  列{i}: 值={width}, 类型={type(width)}, 是否为None={width is None}")

                    # 确保所有列宽都是有效的数字
                    valid_col_widths = []
                    for width in col_widths:
                        if width is None:
                            valid_col_widths.append(100)  # 使用默认宽度
                        elif not isinstance(width, (int, float)):
                            try:
                                valid_col_widths.append(float(width))
                            except Exception:
                                valid_col_widths.append(100)
                        elif width <= 0:
                            valid_col_widths.append(100)
                        else:
                            valid_col_widths.append(width)

                    print(f"有效列宽: {valid_col_widths}")

                    # 创建Table对象
                    main_table = Table(main_table_data, colWidths=valid_col_widths)
                    main_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),  # 蓝色表头
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 所有列居中对齐
                                (
                                    "FONTNAME",
                                    (0, 0),
                                    (-1, 0),
                                    "ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                                ),
                                ("FONTSIZE", (0, 0), (-1, 0), 11),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("TOPPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3498db")),  # 蓝色外框
                                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                (
                                    "ROWBACKGROUNDS",
                                    (0, 1),
                                    (-1, -1),
                                    [colors.white, colors.HexColor("#f0f4f8")],
                                ),  # 交替行颜色
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 垂直居中
                                ("LEFTPADDING", (0, 0), (-1, -1), 8),  # 左内边距
                                ("RIGHTPADDING", (0, 0), (-1, -1), 8),  # 右内边距
                                ("TOPPADDING", (0, 1), (-1, -1), 6),  # 上内边距
                                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),  # 下内边距
                            ]
                        )
                    )
                    elements.append(main_table)
                else:
                    elements.append(Paragraph(f"无{data_source['main_name']}", normal_style))

                elements.append(Spacer(1, 20))

                # 添加剩余网段信息
                elements.append(Paragraph(data_source["remaining_name"], heading2_style))
                remaining_table_data = [[Paragraph(h, table_text_style) for h in remaining_headers]]
                for item in remaining_tree.get_children():
                    values = remaining_tree.item(item, "values")
                    if values:
                        remaining_table_data.append(
                            [Paragraph(str(v) if v is not None else "", table_text_style) for v in values]
                        )

                if len(remaining_table_data) > 1:
                    # 计算表格宽度（页宽减去左右边距）
                    table_width = page_width - margins[0] - margins[1]

                    # 确定表格列数
                    table_cols = len(remaining_table_data[0])

                    # 使用指定的列宽或默认列宽
                    col_widths = data_source.get("remaining_table_cols")

                    # 处理字符串格式的列宽配置，如"1:1:1:1:1:1:1"
                    if isinstance(col_widths, str):
                        try:
                            # 尝试将字符串按冒号分割并转换为数字列表
                            col_ratios = [float(w) for w in col_widths.split(":")]
                            # 如果所有比例值都很小（< 10），将其解释为比例而不是直接宽度
                            if all(ratio < 10 for ratio in col_ratios):
                                # 计算总比例
                                total_ratio = sum(col_ratios)
                                if total_ratio > 0:
                                    # 根据比例分配实际宽度
                                    col_widths = [table_width * (ratio / total_ratio) for ratio in col_ratios]
                                else:
                                    # 如果总比例为0，使用默认列宽
                                    col_widths = None
                            else:
                                # 否则直接使用转换后的宽度
                                col_widths = col_ratios
                        except (ValueError, TypeError):
                            # 如果转换失败，使用默认列宽
                            col_widths = None

                    # 添加调试信息
                    print("\n=== 剩余表格调试信息 ===")
                    print(f"表格数据行数: {len(remaining_table_data)}")
                    print(f"表格列数: {table_cols}")
                    print(f"原始列宽: {col_widths}")
                    print(f"表格宽度: {table_width}")

                    if not col_widths or len(col_widths) != table_cols:
                        print("列宽数量不匹配，使用默认平均分配列宽")
                        # 默认平均分配列宽
                        col_widths = [table_width / table_cols] * table_cols
                    else:
                        print("使用指定列宽，替换无效值")
                        # 确保所有列宽值都是有效的数字且大于0
                        processed_col_widths = []
                        for width in col_widths:
                            try:
                                # 尝试将宽度转换为数字
                                numeric_width = float(width) if width is not None else table_width / table_cols
                                if numeric_width <= 10:  # 如果宽度太小，使用默认宽度
                                    numeric_width = table_width / table_cols
                                processed_col_widths.append(numeric_width)
                            except (ValueError, TypeError):
                                # 如果转换失败，使用默认宽度
                                processed_col_widths.append(table_width / table_cols)

                        # 确保列宽数组长度与表格列数一致
                        if len(processed_col_widths) != table_cols:
                            col_widths = [table_width / table_cols] * table_cols
                        else:
                            col_widths = processed_col_widths

                    # 计算自适应列宽
                    print("\n=== 计算剩余表格自适应列宽 ===")
                    try:
                        # 使用自适应列宽替换现有列宽
                        print("  调用_calculate_auto_col_widths方法")
                        auto_col_widths = self._calculate_auto_col_widths(
                            remaining_table_data, table_width
                        )
                        print(f"自适应列宽: {auto_col_widths}")
                        # 使用自适应列宽
                        col_widths = auto_col_widths
                    except Exception as e:
                        print(f"  计算剩余表格自适应列宽错误: {type(e).__name__}: {e}")

                        traceback.print_exc()
                        # 如果自适应列宽计算失败，使用默认列宽
                        col_widths = [table_width / table_cols] * table_cols
                        print(f"  回退到默认列宽: {col_widths}")

                    print(f"最终列宽: {col_widths}")
                    print("=== 剩余表格调试信息结束 ===")

                    # 添加详细的调试信息，检查Table构造函数的参数
                    print("\n=== 剩余表格Table构造函数调试信息 ===")
                    print(f"remaining_table_data类型: {type(remaining_table_data)}")
                    print(f"remaining_table_data长度: {len(remaining_table_data)}")
                    print(f"remaining_table_data[0]类型: {type(remaining_table_data[0])}")
                    print(f"remaining_table_data[0]长度: {len(remaining_table_data[0])}")
                    print(f"colWidths类型: {type(col_widths)}")
                    print(f"colWidths长度: {len(col_widths)}")
                    print(f"colWidths内容: {col_widths}")
                    print("每个列宽的值和类型:")
                    for i, width in enumerate(col_widths):
                        print(f"  列{i}: 值={width}, 类型={type(width)}, 是否为None={width is None}")

                    # 确保所有列宽都是有效的数字
                    valid_col_widths = []
                    for width in col_widths:
                        if width is None:
                            valid_col_widths.append(100)  # 使用默认宽度
                        elif not isinstance(width, (int, float)):
                            try:
                                valid_col_widths.append(float(width))
                            except Exception:
                                valid_col_widths.append(100)
                        elif width <= 0:
                            valid_col_widths.append(100)
                        else:
                            valid_col_widths.append(width)

                    print(f"有效列宽: {valid_col_widths}")

                    # 创建Table对象
                    remaining_table = Table(remaining_table_data, colWidths=valid_col_widths)
                    remaining_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),  # 绿色表头
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 所有列居中对齐
                                (
                                    "FONTNAME",
                                    (0, 0),
                                    (-1, 0),
                                    "ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                                ),
                                ("FONTSIZE", (0, 0), (-1, 0), 11),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("TOPPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#27ae60")),  # 绿色外框
                                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                (
                                    "ROWBACKGROUNDS",
                                    (0, 1),
                                    (-1, -1),
                                    [colors.white, colors.HexColor("#f0f4f8")],
                                ),  # 交替行颜色
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 垂直居中
                                ("LEFTPADDING", (0, 0), (-1, -1), 8),  # 左内边距
                                ("RIGHTPADDING", (0, 0), (-1, -1), 8),  # 右内边距
                                ("TOPPADDING", (0, 1), (-1, -1), 6),  # 上内边距
                                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),  # 下内边距
                            ]
                        )
                    )
                    elements.append(remaining_table)
                else:
                    elements.append(Paragraph(f"无{data_source['remaining_name']}", normal_style))

                # 检查是否有网段分布图数据
                print("=== 网段分布图调试信息 ===")
                print(f"hasattr(self, 'chart_data'): {hasattr(self, 'chart_data')}")
                print(f"self.chart_data: {self.chart_data if hasattr(self, 'chart_data') else '未定义'}")
                
                # 从导出数据中提取父网段和子网信息，生成chart_data
                chart_data = None
                
                # 只有在子网切分功能中导出时才生成网段分布图
                # 检查当前导出的主数据名称，如果是"切分网段信息"，则生成网段分布图
                if data_source["main_name"] == "切分网段信息":
                    # 检查是否已有chart_data
                    if hasattr(self, 'chart_data') and self.chart_data is not None and isinstance(self.chart_data, dict):
                        chart_data = self.chart_data
                    else:
                        print("没有找到chart_data，尝试从导出数据中生成")
                        
                        # 尝试从main_data中提取父网段信息
                        parent_cidr = None
                        print(f"main_data内容: {main_data}")
                        
                        # 遍历main_data查找父网段信息
                        for row in main_data:
                            print(f"检查行: {row}")
                            if len(row) >= 2:
                                if row[0] == "父网段":
                                    parent_cidr = row[1]
                                    break
                                # 检查其他可能的父网段字段名
                                elif "父网段" in str(row[0]) or "父网络" in str(row[0]):
                                    parent_cidr = row[1]
                                    break
                                # 检查第一行是否包含父网段信息
                                elif row[0] and isinstance(row[0], str) and "/" in str(row[0]):
                                    parent_cidr = row[0]
                                    break
                        
                        if parent_cidr:
                            print(f"从导出数据中提取到父网段: {parent_cidr}")
                        else:
                            # 如果直接找不到父网段，尝试从main_tree中获取
                            print("直接从main_data中找不到父网段，尝试从main_tree中获取")
                            for item in main_tree.get_children():
                                values = main_tree.item(item, "values")
                                print(f"检查树节点: {values}")
                                if values and len(values) >= 2:
                                    if values[0] == "父网段":
                                        parent_cidr = values[1]
                                        break
                            if parent_cidr:
                                print(f"从main_tree中提取到父网段: {parent_cidr}")
                            
                            # 从remaining_tree中提取剩余网段信息
                            remaining_networks = []
                            for item in remaining_tree.get_children():
                                values = remaining_tree.item(item, "values")
                                if values and len(values) >= 1:
                                    remaining_networks.append(values[0])
                            
                            # 从main_data中提取切分网段信息
                            split_networks = []
                            for row in main_data:
                                if len(row) >= 2 and row[0] == "切分网段":
                                    split_networks.append(row[1])
                            
                            print(f"提取到切分网段: {split_networks}")
                            print(f"提取到剩余网段: {remaining_networks}")
                            
                            # 生成chart_data
                            parent_info = get_subnet_info(parent_cidr)
                            if "error" not in parent_info:
                                parent_start = ip_to_int(parent_info.get("network", "0.0.0.0"))
                                parent_end = ip_to_int(parent_info.get("broadcast", "0.0.0.0"))
                                parent_range = parent_end - parent_start + 1
                                
                                chart_data = {
                                    "parent": {
                                        "start": parent_start,
                                        "end": parent_end,
                                        "range": parent_range,
                                        "name": parent_info.get("cidr", parent_cidr),
                                        "color": "#f3e5f5",
                                    },
                                    "networks": [],
                                }
                                
                                # 添加切分网段
                                for split_cidr in split_networks:
                                    split_info = get_subnet_info(split_cidr)
                                    if "error" not in split_info:
                                        split_start = ip_to_int(split_info.get("network", "0.0.0.0"))
                                        split_end = ip_to_int(split_info.get("broadcast", "0.0.0.0"))
                                        split_range = split_end - split_start + 1
                                        chart_data["networks"].append({
                                            "start": split_start,
                                            "end": split_end,
                                            "range": split_range,
                                            "name": split_info.get("cidr", split_cidr),
                                            "color": "#2196f3",
                                            "type": "split",
                                        })
                                
                                # 添加剩余网段
                                for remaining_cidr in remaining_networks:
                                    remaining_info = get_subnet_info(remaining_cidr)
                                    if "error" not in remaining_info:
                                        remaining_start = ip_to_int(remaining_info.get("network", "0.0.0.0"))
                                        remaining_end = ip_to_int(remaining_info.get("broadcast", "0.0.0.0"))
                                        remaining_range = remaining_end - remaining_start + 1
                                        chart_data["networks"].append({
                                            "start": remaining_start,
                                            "end": remaining_end,
                                            "range": remaining_range,
                                            "name": remaining_info.get("cidr", remaining_cidr),
                                            "color": "#5e9c6a",
                                            "type": "remaining",
                                        })
                                
                                print(f"成功生成chart_data，包含 {len(chart_data['networks'])} 个网段")
                else:
                    print("当前不是子网切分功能导出，跳过网段分布图生成")
                    chart_data = None
                
                # 简化检测条件，确保能正确检测到图表数据
                has_chart_data = chart_data is not None and isinstance(chart_data, dict)
                has_networks = has_chart_data and 'networks' in chart_data and len(chart_data['networks']) > 0
                
                print(f"has_chart_data: {has_chart_data}")
                print(f"has_networks: {has_networks}")
                
                if has_chart_data and has_networks:
                    print("检测到有效网段分布图数据，准备添加到PDF")
    

    

                    
                    try:
                        # 直接使用应用中已经绘制好的图表，而不是重新生成
                        print("直接使用应用中已经绘制好的网段分布图")
                        
                        # 确保图表已经绘制
                        self.draw_distribution_chart()
                        
                        # 处理图表页面，确保竖排A4
        
        
                        
                        # 1. 切换到纵向页面模板，准备添加图表
                        elements.append(NextPageTemplate('portrait'))
                        elements.append(PageBreak())
                        
                        # 2. 初始化pil_image
                        pil_image = None
                        high_res_width = 2480
                        high_res_height = 3508
                        
                        # 3. 尝试使用Canvas捕获方式（高质量）- 暂时禁用，确保使用PIL直接绘制
                        canvas_capture_success = False  # 强制使用PIL直接绘制，确保文字垂直居中对齐
                        
                        # 4. 直接使用PIL绘制图表，确保文字垂直居中对齐
                        if not canvas_capture_success:
                            print("使用PIL直接绘制图表作为备选方案")
            
                            
                            # 准备图表数据
                            parent_info = chart_data.get("parent", {})
                            parent_cidr = parent_info.get("name", "Parent Network")
                            parent_range = parent_info.get("range", 1)
                            networks = chart_data.get("networks", [])
                            
                            # 动态计算图表所需的总高度，根据网段数量调整
                            # 基础高度：标题、父网段、切分网段、剩余网段标题、图例等
                            # 增加基础高度，确保图例部分能够完整显示
                            base_height = 280 + 100 + 100 + 150 + 300  # 基础元素高度，增加100像素用于完整显示图例
                            
                            # 计算所有网段所需的总高度
                            split_networks = [net for net in networks if net.get("type") == "split"]
                            remaining_networks = [net for net in networks if net.get("type") != "split"]
                            total_networks = len(split_networks) + len(remaining_networks)
                            
                            # 每个网段占用的高度：bar_height + padding
                            segment_height = 100 + 34  # 100是bar_height，34是padding
                            
                            # 计算总高度
                            required_height = base_height + total_networks * segment_height
                            
                            # 确保高度至少为原始A4高度
                            dynamic_high_res_height = max(high_res_height, required_height)
                            
                            # 创建动态高度的高分辨率图像
                            pil_image = Image.new('RGB', (high_res_width, dynamic_high_res_height), color='#333333')
                            draw = ImageDraw.Draw(pil_image)
                            
                            # 确保中文正常显示，使用更可靠的字体加载逻辑
                            font = None
                            bold_font = None
                            font_loaded = False
                            
                            try:
                
                                system_font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                                
                                # 尝试多种中文字体，确保成功加载
                                font_candidates = [
                                    ('msyh.ttc', 36, '微软雅黑'),  # 增大字体大小
                                    ('simhei.ttf', 36, '黑体'),      # 增大字体大小
                                    ('simsun.ttc', 34, '宋体'),      # 增大字体大小
                                    ('simkai.ttf', 34, '楷体')       # 增大字体大小
                                ]
                                
                                for font_file, font_size, font_name in font_candidates:
                                    font_path = os.path.join(system_font_dir, font_file)
                                    if os.path.exists(font_path):
                                        try:
                                            font = ImageFont.truetype(font_path, font_size)
                                            bold_font = ImageFont.truetype(font_path, font_size + 4)
                                            font_loaded = True
                                            print(f"成功加载{font_name}字体: {font_path}，字号: {font_size}")
                                            break
                                        except Exception as e:
                                            print(f"尝试加载{font_name}失败: {e}")
                                            continue
                                
                                if not font_loaded:
                                    # 尝试使用PIL的默认中文字体支持
                                    font = ImageFont.load_default()
                                    bold_font = ImageFont.load_default()
                                    print("使用默认字体，可能不支持中文")
                            except Exception as e:
                                print(f"加载中文字体失败: {e}")
                                font = ImageFont.load_default()
                                bold_font = ImageFont.load_default()
                            
                            # 设置图表参数，根据用户要求调整
                            margin_left = 180  # 增加左边距，为文字留出更多空间
                            margin_right = 100
                            margin_top = 280  # 增加上边距，使标题与图表之间有一行字的距离

                            chart_width = high_res_width - margin_left - margin_right
                            chart_x = margin_left

                            
                            # 使用对数比例尺
                            log_max = math.log10(parent_range)
                            log_min = 3
                            
                            # 调整参数：
                            # 1. 柱状图宽度放大50% (80 → 120)
                            min_bar_width = 120
                            # 2. 间隔调小30% (48 → 34)
                            padding = 34  # 48 * 0.7 = 33.6，取整为34
                            # 3. 增加柱状图高度，为文字留出更多空间
                            bar_height = 100
                            
                            # 恢复网段分布图文字标题
                            title = "网段分布图"
                            # 创建合适大小的标题字体
                            title_font_size = 76  # 108 * 0.7 = 75.6，取整为76
                            title_font = None
                            try:
                
                                system_font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                                title_font_path = os.path.join(system_font_dir, 'msyh.ttc')
                                if os.path.exists(title_font_path):
                                    title_font = ImageFont.truetype(title_font_path, title_font_size)
                                else:
                                    title_font = bold_font
                            except Exception:
                                title_font = bold_font
                            
                            title_bbox = draw.textbbox((0, 0), title, font=title_font)
                            title_x = (high_res_width - (title_bbox[2] - title_bbox[0])) // 2
                            title_y = 100
                            draw.text((title_x, title_y), title, fill="#ffffff", font=title_font)
                            
                            y = margin_top
                            
                            # 绘制父网段
                            log_value = max(log_min, math.log10(parent_range))
                            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
                            parent_color = "#636e72"
                            draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=parent_color, outline=None, width=0)
                            
                            usable_addresses = parent_range - 2 if parent_range > 2 else parent_range
                            segment_text = f"父网段: {parent_cidr}"
                            address_text = f"可用地址数: {usable_addresses:,}"
                            
                            # 文字调整：放大1倍后再调小30% (72 → 50)
                            text_font_size = 50  # 72 * 0.7 = 50.4，取整为50
                            text_font = None
                            bold_text_font = None
                            try:
                                system_font_dir = os.path.join(os.environ['WINDIR'], 'Fonts')
                                font_path = os.path.join(system_font_dir, 'msyh.ttc')
                                if os.path.exists(font_path):
                                    text_font = ImageFont.truetype(font_path, text_font_size)
                                    bold_text_font = ImageFont.truetype(font_path, text_font_size + 6)  # 50 + 6 = 56
                                else:
                                    text_font = font
                                    bold_text_font = bold_font
                            except Exception:
                                text_font = font
                                bold_text_font = bold_font
                            
                            # 简单可靠的文字垂直居中算法，确保中文文字在视觉上居中
                            def get_centered_y(box_y, box_height, _, __):
                                """计算文字垂直居中的y坐标，确保中文文字在视觉上居中"""
                                # 用户反馈文字仍然偏低，调整为容器中心位置减去20像素，让文字继续往上移动
                                # 由于PIL的y轴向下递增，降低y值可以让文字上移
                                text_y = box_y + box_height // 2 - 38
                                return text_y
                            
                            # 可用地址数再往右移动5个中文字符的位置 (750 → 900)
                            # 每个中文字符宽度约为字体大小的0.5倍，5个中文字符约125px，总共移动10个字符
                            address_x = 900
                            
                            # 绘制父网段
                            log_value = max(log_min, math.log10(parent_range))
                            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
                            parent_color = "#636e72"
                            draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=parent_color, outline=None, width=0)
                            
                            usable_addresses = parent_range - 2 if parent_range > 2 else parent_range
                            segment_text = f"父网段: {parent_cidr}"
                            address_text = f"可用地址数: {usable_addresses:,}"
                            
                            # 父网段文字垂直居中
                            segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
                            segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
                            address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
                            address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)
                            
                            draw.text((chart_x + 30, segment_text_y), segment_text, fill="#ffffff", font=bold_text_font)
                            draw.text((address_x, address_text_y), address_text, fill="#ffffff", font=bold_text_font)
                            
                            y += bar_height + padding
                            
                            # 绘制切分网段
                            split_networks = [net for net in networks if net.get("type") == "split"]
                            for i, network in enumerate(split_networks):
                                network_range = network.get("range", 1)
                                log_value = max(log_min, math.log10(network_range))
                                bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
                                split_color = "#4a7eb4"
                                draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=split_color, outline=None, width=0)
                                
                                name = network.get("name", "")
                                usable_addresses = network_range - 2 if network_range > 2 else network_range
                                segment_text = f"切分网段: {name}"
                                address_text = f"可用地址数: {usable_addresses:,}"
                                
                                # 切分网段文字垂直居中
                                segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
                                segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
                                address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
                                address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)
                                
                                draw.text((chart_x + 30, segment_text_y), segment_text, fill="#ffffff", font=bold_text_font)
                                draw.text((address_x, address_text_y), address_text, fill="#ffffff", font=bold_text_font)
                                
                                y += bar_height + padding
                                
                                if i == len(split_networks) - 1:
                                    draw.line([chart_x, y + 20, chart_x + chart_width, y + 20], fill="#cccccc", width=4)
                            
                            # 绘制剩余网段标题 - 增加间距，防止被盖住
                            y += 80  # 增加间距，解决文字被盖住的问题
                            remaining_count = len([net for net in networks if net.get("type") != "split"])
                            title_text = f"剩余网段 ({remaining_count} 个):"
                            
                            # 剩余网段标题垂直居中
                            title_bbox = draw.textbbox((0, 0), title_text, font=bold_text_font)
                            title_text_y = get_centered_y(y, bar_height, title_bbox, bold_text_font)
                            draw.text((chart_x, title_text_y), title_text, fill="#ffffff", font=bold_text_font)
                            y += 100  # 增加间距，使剩余网段柱状图下移一行字的距离
                            
                            # 为剩余网段分配高区分度的柔和配色方案
                            subnet_colors = [
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
                            ]
                            
                            # 绘制剩余网段
                            remaining_networks = [net for net in networks if net.get("type") != "split"]
                            for i, network in enumerate(remaining_networks):
                                network_range = network.get("range", 1)
                                log_value = max(log_min, math.log10(network_range))
                                bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
                                color_index = i % len(subnet_colors)
                                color = subnet_colors[color_index]
                                draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=color, outline=None, width=0)
                                
                                name = network.get("name", "")
                                usable_addresses = network_range - 2 if network_range > 2 else network_range
                                segment_text = f"网段 {i + 1}: {name}"
                                address_text = f"可用地址数: {usable_addresses:,}"
                                
                                # 剩余网段文字垂直居中
                                segment_bbox = draw.textbbox((0, 0), segment_text, font=text_font)
                                segment_text_y = get_centered_y(y, bar_height, segment_bbox, text_font)
                                address_bbox = draw.textbbox((0, 0), address_text, font=text_font)
                                address_text_y = get_centered_y(y, bar_height, address_bbox, text_font)
                                
                                draw.text((chart_x + 30, segment_text_y), segment_text, fill="#ffffff", font=text_font)
                                draw.text((address_x, address_text_y), address_text, fill="#ffffff", font=text_font)
                                
                                y += bar_height + padding
                            
                            # 绘制图例
                            y += 80  # 减少间距，使图例上移
                            legend_title = "图例说明"
                            # 文字垂直居中
                            legend_title_bbox = draw.textbbox((0, 0), legend_title, font=bold_text_font)
                            legend_title_y = y + (bar_height - (legend_title_bbox[3] - legend_title_bbox[1])) // 2
                            draw.text((chart_x, legend_title_y), legend_title, fill="#ffffff", font=bold_text_font)
                            y += 100  # 减少间距，使图例项与标题保持更合适的距离
                            
                            legend_y = y
                            # 调整图例大小，适应文字大小变化
                            legend_item_height = 60  # 图例项高度


                            
                            # 彻底解决图例垂直对齐问题，考虑文字基线特性
                            legend_container_y = legend_y
                            legend_container_height = legend_item_height
                            
                            # 为中文优化的垂直居中函数，考虑文字基线
                            def get_centered_text_y(container_y, container_height, text_bbox):
                                """计算文字垂直居中的y坐标，考虑中文基线特性"""
                                text_height = text_bbox[3] - text_bbox[1]
                                # 中文基线大约在文字高度的0.8处，需要调整y坐标
                                # 计算容器中心
                                container_center = container_y + container_height // 2
                                # 文字垂直居中需要考虑基线，调整文字y坐标
                                # 根据实际效果，将文字上移30%，使视觉上垂直居中
                                text_y = container_center - text_height // 2 - int(text_height * 0.30)  # 上移30%
                                return text_y
                            
                            # 1. 父网段图例
                            parent_x = chart_x
                            parent_color = "#636e72"
                            parent_label = "父网段"
                            
                            # 父网段颜色块和文字垂直居中
                            parent_block_size = 40
                            parent_text_font = text_font
                            parent_label_bbox = draw.textbbox((0, 0), parent_label, font=parent_text_font)
                            
                            # 精确计算垂直居中位置
                            parent_block_y = legend_container_y + (legend_container_height - parent_block_size) // 2
                            parent_label_y = get_centered_text_y(legend_container_y, legend_container_height, parent_label_bbox)
                            
                            draw.rectangle([parent_x, parent_block_y, parent_x + parent_block_size, parent_block_y + parent_block_size], fill=parent_color, outline=None, width=0)
                            draw.text((parent_x + parent_block_size + 25, parent_label_y), parent_label, fill="#ffffff", font=parent_text_font)
                            
                            # 2. 切分网段图例
                            # 增大父网段与切分网段之间的间距
                            split_x = parent_x + 300  # 大幅增加间距
                            split_color = "#4a7eb4"
                            split_label = "切分网段"
                            
                            # 切分网段颜色块和文字垂直居中
                            split_block_size = 40
                            split_text_font = text_font
                            split_label_bbox = draw.textbbox((0, 0), split_label, font=split_text_font)
                            
                            # 精确计算垂直居中位置
                            split_block_y = legend_container_y + (legend_container_height - split_block_size) // 2
                            split_label_y = get_centered_text_y(legend_container_y, legend_container_height, split_label_bbox)
                            
                            draw.rectangle([split_x, split_block_y, split_x + split_block_size, split_block_y + split_block_size], fill=split_color, outline=None, width=0)
                            draw.text((split_x + split_block_size + 25, split_label_y), split_label, fill="#ffffff", font=split_text_font)
                            
                            # 3. 剩余网段图例（多色显示，匹配应用程序）
                            # 大幅增大切分网段与剩余网段之间的间距
                            remaining_x = split_x + 320  # 大幅增加间距，解决挤在一起的问题
                            remaining_label = "剩余网段(多色)"
                            
                            # 显示多彩示例，匹配高区分度配色方案
                            legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
                            remaining_block_size = 30  # 减小剩余网段彩色块大小，避免拥挤
                            remaining_block_gap = 25  # 增大剩余网段彩色块间距
                            
                            # 剩余网段彩色块和文字垂直居中
                            remaining_text_font = text_font
                            remaining_label_bbox = draw.textbbox((0, 0), remaining_label, font=remaining_text_font)
                            
                            # 精确计算垂直居中位置
                            remaining_block_y = legend_container_y + (legend_container_height - remaining_block_size) // 2
                            remaining_label_y = get_centered_text_y(legend_container_y, legend_container_height, remaining_label_bbox)
                            
                            # 绘制多个彩色块
                            for j, color in enumerate(legend_colors):
                                draw.rectangle([
                                    remaining_x + j * (remaining_block_size + remaining_block_gap),
                                    remaining_block_y,
                                    remaining_x + j * (remaining_block_size + remaining_block_gap) + remaining_block_size,
                                    remaining_block_y + remaining_block_size
                                ], fill=color, outline=None, width=0)
                            
                            # 绘制剩余网段文字，大幅增加彩色块与文字之间的间距（从30增加到40）
                            draw.text((
                                remaining_x + len(legend_colors) * (remaining_block_size + remaining_block_gap) + 40,
                                remaining_label_y
                            ), remaining_label, fill="#ffffff", font=text_font)
                            
                            
                            print("成功使用备选方案创建网段分布图")
                            
                            # 保存图像为高DPI PNG
                            img_byte_arr = BytesIO()
                            pil_image.save(img_byte_arr, format='PNG', dpi=(300, 300))
                            img_byte_arr.seek(0)  # 重置文件指针
                            print(f"成功保存高DPI PNG图像，尺寸: {pil_image.size}, DPI: 300")
                        
                        # 6. 计算图像在PDF中的合适尺寸
        
                        portrait_width, portrait_height = A4
                        
                        # 使用动态计算的图像高度
                        actual_image_height = dynamic_high_res_height if 'dynamic_high_res_height' in locals() else high_res_height
                        
                        # 计算图像在PDF中的最佳尺寸，保持宽高比
                        # 对于多网段图表，我们优先考虑可读性，适当调整图像大小
                        print(f"原始图像尺寸: {high_res_width}x{actual_image_height} px, DPI: 300")
                        
                        # 计算PDF可用空间，确保图像不超过页面框架
                        # 从错误信息看，可用框架高度约为688点，我们使用这个值作为参考
                        available_width = portrait_width - margins[0] - margins[1] - 20
                        available_height = 680  # 增加可用高度，确保图表能完整显示
                        
                        print(f"PDF可用空间: {available_width:.1f}x{available_height:.1f}点")
                        
                        # 计算PDF中图像的最佳尺寸，保持宽高比，确保图表能完整显示
                        image_ratio = high_res_width / actual_image_height
                        
                        # 优先考虑图表的可读性，使用更大的高度
                        final_pdf_height = available_height
                        final_pdf_width = final_pdf_height * image_ratio
                        
                        # 如果宽度超过可用宽度，则按宽度缩放
                        if final_pdf_width > available_width:
                            final_pdf_width = available_width
                            final_pdf_height = final_pdf_width / image_ratio
                        
                        # 计算实际DPI：1点=1/72英寸
                        actual_dpi = high_res_width / (final_pdf_width / 72.0)
                        
                        # 9. 只添加图像，不添加额外的标题文字
                        # 图表本身已经包含了"网段分布图"标题，所以不需要在PDF页面上重复显示
                        chart_elements = []
                        
                        # 对于高图表，我们允许其跨页显示，确保完整性
                        # 如果图像高度超过页面高度，ReportLab会自动将其拆分到多页
                        chart_elements.append(RLImage(img_byte_arr, width=final_pdf_width, height=final_pdf_height))
                        
                        # 不使用KeepTogether，允许图表跨页显示，确保完整性
                        elements.extend(chart_elements)
                        
                        # 10. 切换回横向页面模板，准备添加后续内容
                        elements.append(NextPageTemplate('landscape'))
                        elements.append(PageBreak())
                        
                        print("网段分布图成功添加到PDF")
                    except Exception as e:
                        print(f"添加网段分布图到PDF失败: {type(e).__name__}: {e}")
                        traceback.print_exc()
                    finally:
                        # 延迟清理临时文件，避免权限问题
                        print("延迟清理临时文件...")
                        # 不立即删除，避免ReportLab在使用中
                        # 在PDF生成后由系统自动清理
                else:
                    print("没有检测到有效网段分布图数据，跳过添加")
                    if has_chart_data:
                        print(f"chart_data内容: {self.chart_data}")
                    if hasattr(self, 'chart_data') and self.chart_data is not None:
                        print(f"networks数量: {len(self.chart_data['networks']) if 'networks' in self.chart_data else 0}")
                
                # 生成PDF
                print("开始生成PDF文档...")
                try:
                    # 确保中文支持
                    # 注册中文字体，确保与register_chinese_fonts方法一致
                    try:
                        # 使用已注册的ChineseFont，确保字体名称一致
                        print(f"使用已注册的中文字体，has_chinese_font: {self.has_chinese_font}")
                        if self.has_chinese_font:
                            # 确认ChineseFont已经注册
                            if 'ChineseFont' in pdfmetrics.getRegisteredFontNames():
                                print("ChineseFont已成功注册，使用该字体")
                                # 确保所有样式使用正确的字体名称
                                title_style.fontName = 'ChineseFont'
                                heading2_style.fontName = 'ChineseFont'
                                normal_style.fontName = 'ChineseFont'
                                table_text_style.fontName = 'ChineseFont'
                                print("已更新所有样式使用ChineseFont字体")
                            else:
                                print("ChineseFont未注册，重新注册")
                                # 重新注册中文字体
                                self.has_chinese_font = self.register_chinese_fonts()
                                if self.has_chinese_font:
                                    print("重新注册中文字体成功")
                        else:
                            print("未注册中文字体，尝试重新注册")
                            self.has_chinese_font = self.register_chinese_fonts()
                    except Exception as e:
                        print(f"处理中文字体失败: {e}")
                        traceback.print_exc()
                    
                    # 移除未定义的add_footer回调
                    doc.build(elements)
                    print("PDF文档生成成功")
                except Exception as e:
                    print(f"PDF文档生成失败: {type(e).__name__}: {e}")
                    traceback.print_exc()
                print("=== PDF导出调试信息结束 ===")

            elif file_ext == ".xlsx":
                # Excel格式导出



                # 创建Excel工作簿
                workbook = Workbook()

                # 添加主数据工作表
                main_sheet = workbook.active
                main_sheet.title = data_source["main_name"]

                # 添加主数据表头
                main_sheet.append(main_headers)

                # 设置表头样式
                for cell in main_sheet[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加主数据
                for row_data in main_data:
                    main_sheet.append(list(row_data))

                # 调整列宽
                for col_index, header in enumerate(main_headers, 1):
                    main_sheet.column_dimensions[chr(64 + col_index)].width = 20

                # 添加剩余数据工作表
                remaining_sheet = workbook.create_sheet(title=data_source["remaining_name"])

                # 添加剩余数据表头
                remaining_sheet.append(remaining_headers)

                # 设置表头样式
                for cell in remaining_sheet[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加剩余数据
                for tree_item in remaining_tree.get_children():
                    row_values = remaining_tree.item(tree_item, "values")
                    if row_values:
                        remaining_sheet.append([str(v) for v in row_values])

                # 调整列宽
                for col_index, header in enumerate(remaining_headers, 1):
                    remaining_sheet.column_dimensions[chr(64 + col_index)].width = 20

                # 保存Excel文件
                workbook.save(file_path)

            else:  # 默认CSV格式
                # CSV格式导出，使用utf-8-sig编码解决中文乱码问题
                with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
                    # 写入主数据
                    csv_file.write(f"{data_source['main_name']},\n")
                    csv_file.write(",".join(main_headers) + "\n")

                    for row_data in main_data:
                        csv_file.write(",".join(map(str, row_data)) + "\n")

                    # 写入一个空行作为分隔
                    csv_file.write("\n")

                    # 写入剩余数据
                    csv_file.write(f"{data_source['remaining_name']},\n")
                    csv_file.write(",".join(remaining_headers) + "\n")

                    for tree_item in remaining_tree.get_children():
                        row_values = remaining_tree.item(tree_item, "values")
                        csv_file.write(",".join(map(str, row_values)) + "\n")

            # 显示导出成功信息，保留原有数据
            self.show_result(success_msg.format(file_path=file_path), keep_data=True)
            return file_path  # 返回导出的文件路径

        except Exception as e:

            # 显示导出错误信息和堆栈跟踪
            error_msg = f"{failure_msg.format(error=str(e))}\n堆栈跟踪：{traceback.format_exc()}"
            self.show_result(error_msg, error=True)
            return None  # 导出失败时返回None

    def export_result(self):
        """导出子网切分结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
        data_source = {
            "main_tree": self.split_tree,
            "main_name": "切分网段信息",
            "main_filter": lambda values: values[0] not in ["提示", "错误", "-", "切分网段信息", "剩余网段信息"],
            "main_headers": ["项目", "值"],
            "remaining_tree": self.remaining_tree,
            "remaining_name": "剩余网段信息",
            "pdf_title": "IP子网分割工具 - 计算结果",
            "main_table_cols": None,  # 使用默认列宽
            "remaining_table_cols": [40, 80, 80, 100, 90, 80, 50],  # 剩余网段表格列宽
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
            "pdf_title": "IP子网分割工具 - 子网规划结果",
            "main_table_cols": [10, 100, 90, 30, 40, 80, 110, 80],  # 已分配子网表格列宽
            "remaining_table_cols": [40, 90, 80, 110, 80, 60],  # 剩余网段表格列宽
        }

        self._export_data(data_source, "保存子网规划结果", "规划结果已成功导出到: {file_path}", "导出失败: {error}")

    def _calculate_auto_col_widths(self, table_data, table_width):
        """根据内容计算自适应列宽

        Args:
            table_data: 表格数据，包含Paragraph对象的列表
            font_name: 字体名称
            font_size: 字体大小
            table_width: 表格可用宽度

        Returns:
            list: 每列的自适应宽度
        """
        # 初始化每列的最大宽度
        print(f"  表格数据行数: {len(table_data)}")
        table_cols = len(table_data[0]) if table_data else 0
        print(f"  表格列数: {table_cols}")
        max_col_widths = [0] * table_cols
        min_col_width = 50  # 最小列宽

        # 遍历所有行和列，计算每列的最大宽度
        for row in table_data:
            for col_idx, cell in enumerate(row):
                # 获取单元格文本内容
                if hasattr(cell, 'getPlainText'):
                    # 处理Paragraph对象，获取实际文本
                    text = cell.getPlainText()
                elif hasattr(cell, 'text'):
                    # 处理其他可能有text属性的对象
                    text = cell.text
                else:
                    # 直接转换为字符串
                    text = str(cell)

                print(f"  单元格内容: {text}, 长度: {len(text)}")

                # 计算文本宽度，中文和英文使用不同的宽度系数
                # 中文每个字符约12像素，英文每个字符约6像素
                text_width = 0
                for char in text:
                    if ord(char) > 127:  # 中文字符
                        text_width += 12
                    else:  # 英文字符
                        text_width += 6

                # 添加左右内边距（各8像素）
                text_width += 16

                print(f"  计算的文本宽度: {text_width}")

                # 更新该列的最大宽度
                if text_width > max_col_widths[col_idx]:
                    max_col_widths[col_idx] = text_width

        # 确保最小宽度
        for i in range(len(max_col_widths)):
            if max_col_widths[i] < min_col_width:
                max_col_widths[i] = min_col_width

        # 计算总宽度
        total_width = sum(max_col_widths)
        print(f"  计算总宽度: {total_width}, 可用表格宽度: {table_width}")

        # 如果总宽度超过页面宽度，按比例缩放
        if total_width > table_width:
            scale_factor = table_width / total_width
            print(f"  总宽度超过页面宽度，应用缩放因子: {scale_factor}")
            for i in range(len(max_col_widths)):
                max_col_widths[i] *= scale_factor

        print(f"  最终自适应列宽: {max_col_widths}")
        return max_col_widths

    def clear_result(self):
        """清空结果表格和图表"""
        # 清空切分网段信息表格
        self.clear_tree_items(self.split_tree)
        # 添加提示行
        self.split_tree.insert("", tk.END, values=("提示", "点击'执行切分'按钮开始操作..."), tags=('odd',))
        # 更新切分网段表格的斑马条纹标签
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

    def register_chinese_fonts(self):
        """注册中文字体供PDF导出使用"""
        # 导入所需模块
        import sys
        import os



        # 尝试查找系统中的中文字体
        font_path = None

        # Windows系统字体路径
        if sys.platform == "win32":
            font_dir = "C:\\Windows\\Fonts"
            if os.path.exists(font_dir):
                # 检查常用中文字体（包含.ttf和.ttc格式）
                font_candidates = [
                    ("simhei.ttf", "SimHei"),  # 黑体
                    ("simsun.ttc", "SimSun"),  # 宋体
                    ("msyh.ttf", "Microsoft YaHei"),  # 微软雅黑
                    ("msyhbd.ttf", "Microsoft YaHei Bold"),  # 微软雅黑粗体
                    ("msyhui.ttf", "Microsoft YaHei UI"),
                    ("stsong.ttf", "STSong"),  # 华文宋体
                    ("stheiti.ttf", "STHeiti"),  # 华文黑体
                    ("stkaiti.ttf", "STKaiti"),  # 华文楷体
                ]

                # 查找所有可用的字体，优先使用黑体
                for font_file, _ in font_candidates:
                    potential_path = os.path.join(font_dir, font_file)
                    if os.path.exists(potential_path):
                        font_path = potential_path

                        # 如果找到黑体，直接使用
                        if font_file.lower() == "simhei.ttf":
                            break

        # 如果找到中文字体，注册它
        if font_path:
            try:
                # 注册字体
                pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                return True
            except Exception as e:
                print(f"注册字体失败: {e}")
                return False
        else:
            print("未找到可用的中文字体")
            return False



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
        self.pin_label.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-94, y=22)  # x=-94，向左移动5个像素，y=22，向下移动1px，与信息栏顶部对齐
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
        x = main_x + (main_width // 2) - (dialog_width // 2)
        y = main_y + (main_height // 2) - (dialog_height // 2)

        # 一次性设置对话框的尺寸和位置
        about_window.geometry("{}x{}+{}+{}".format(dialog_width, dialog_height, x, y))

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
    import sys
    import os
    # 创建主窗口
    root = tk.Tk()

    # 设置窗口初始大小 - 调整高度以确保子网需求和规划结果两个表格都显示5行
    window_width = 800
    window_height = 700  # 调整窗口高度，确保两个表格都能显示5行

    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口居中的坐标
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    # 设置窗口大小和位置
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # 设置窗口最小大小 - 最小高度设为当前满意高度，只能拉大不能缩小
    root.minsize(800, 700)

    # 允许调整窗口宽度和高度
    root.resizable(width=True, height=True)

    # 设置窗口图标
    try:
        # 尝试加载图标文件
        # 在开发环境中，图标文件位于当前目录
        # 在打包后的程序中，使用PyInstaller的资源路径

        # 获取图标文件路径
        icon_path = None
        if hasattr(sys, "_MEIPASS"):
            # 打包后的路径
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")
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
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(True, icon)
            except Exception:
                pass  # 如果PhotoImage方法失败，继续执行
    except Exception as e:
        print(f"设置窗口图标失败: {e}")

    # 创建应用实例并运行
    IPSubnetSplitterApp(root)
    root.mainloop()
