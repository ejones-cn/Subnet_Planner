#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子网规划师应用程序 - 主窗口
"""

# 标准库
import base64
import csv
import datetime
import os
import re
import sys
import traceback
from collections import deque
from io import BytesIO

# 第三方库
import ipaddress
import tkinter as tk
import tkinter.font as tkfont
from openpyxl import Workbook, load_workbook  # type: ignore
from openpyxl.styles import Font, Alignment  # type: ignore
from PIL import Image, ImageTk
from tkinter import ttk, filedialog

# 本地模块
from ip_subnet_calculator import (
    split_subnet,
    ip_to_int,
    get_subnet_info,
    suggest_subnet_planning,
    merge_subnets,
    get_ip_info,
    range_to_cidr,
    check_subnet_overlap,
    handle_ip_subnet_error,
)
from export_utils import ExportUtils
from chart_utils import draw_text_with_stroke, draw_distribution_chart
from version import get_version
from i18n import _, set_language, get_language  # _ 是翻译函数，用于国际化

# 样式管理器 - 统一导入,避免运行时导入
from style_manager import (
    init_style_manager,
    update_styles,
    get_current_font_settings,
    get_style_manager,
)

# 全局变量定义
SCALE_FACTOR = 1.0  # DPI缩放因子，默认1.0（96 DPI）


if sys.platform == 'win32':
    try:
        import ctypes

        PROCESS_DPI_UNAWARE = 0
        PROCESS_SYSTEM_DPI_AWARE = 1
        PROCESS_PER_MONITOR_DPI_AWARE = 2
        PROCESS_PER_MONITOR_DPI_AWARE_V2 = 3

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE_V2)
            DPI_MODE = "PROCESS_PER_MONITOR_DPI_AWARE_V2"
        except AttributeError:
            ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
            DPI_MODE = "PROCESS_PER_MONITOR_DPI_AWARE"
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
            DPI_MODE = "SetProcessDPIAware"
        
        # 获取当前DPI和缩放因子
        hdc = ctypes.windll.user32.GetDC(None)
        LOGPIXELSX = 88  # 水平DPI
        LOGPIXELSY = 90  # 垂直DPI
        dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
        dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, LOGPIXELSY)
        ctypes.windll.user32.ReleaseDC(None, hdc)
        
        # 计算缩放因子
        SCALE_FACTOR = dpi_x / 96.0
        print(f"✅ Windows DPI设置: {dpi_x}x{dpi_y} DPI, 缩放因子: {SCALE_FACTOR:.2f}, 模式: {DPI_MODE}")
        
    except Exception as e:
        print(f"⚠️ 设置DPI感知失败: {e}")
        # 定义默认缩放因子
        SCALE_FACTOR = 1.0


# 自定义的ColoredNotebook类，支持每个标签不同颜色
class ColoredNotebook(ttk.Frame):
    """自定义的ColoredNotebook组件，用于显示带有颜色的标签页

    这个组件扩展了ttk.Frame，实现了类似Notebook的标签页功能，
    支持为不同标签页设置不同的背景颜色，提供更好的视觉区分。

    参数:
        master: 父容器
        style: 样式对象
        tab_change_callback: 标签页切换回调函数
        is_top_level: 是否为顶级标签页
        **kwargs: 传递给ttk.Frame的其他参数
    """
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
        unique_id = self.unique_id
        self.light_blue_style = f"LightBlue{unique_id}.TFrame"
        self.light_green_style = f"LightGreen{unique_id}.TFrame"
        self.light_orange_style = f"LightOrange{unique_id}.TFrame"
        self.light_purple_style = f"LightPurple{unique_id}.TFrame"
        self.light_pink_style = f"LightPink{unique_id}.TFrame"

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

    def on_configure(self, event):
        """当笔记本控件大小变化时调用，确保内容区域能正确调整大小"""
        if hasattr(self, 'content_area'):
            # 更新content_area的布局，确保它能完全填充笔记本控件的空间
            self.content_area.pack_configure(fill='both', expand=True)

            # 如果有选中的标签，确保其内容框架也能正确调整大小
            if hasattr(self, 'active_tab') and self.active_tab is not None and 0 <= self.active_tab < len(self.tabs):
                selected_tab = self.tabs[self.active_tab]
                selected_tab["content"].pack_configure(fill='both', expand=True)

    def _on_tab_mouse_down(self, button, color):
        """当鼠标按下标签页时，更新内容区域背景色为按下状态颜色"""
        if hasattr(self, "active_tab") and button.tab_index == self.active_tab:
            self.mouse_down_colors.get(color, "#e1bee7")

    def _on_tab_mouse_up(self, button, color):
        """当鼠标释放标签页时，恢复内容区域背景色为激活状态颜色"""
        if hasattr(self, "active_tab") and button.tab_index == self.active_tab:
            self.mouse_up_colors.get(color, "#ce93d8")

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

        # 从样式管理器获取当前字体设置
        font_family, font_size = get_current_font_settings()
        style_manager = get_style_manager()
        tab_width = style_manager.get_tab_width() if style_manager else 10

        button_params = {
            "text": label,
            "bg": color,
            "relief": "flat",
            "borderwidth": 0,
            "padx": 5,
            "pady": 5,
            "font": (font_family, font_size, "normal"),
            "width": tab_width,  # 从样式管理器获取标签宽度
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

        font_family, font_size = get_current_font_settings()

        # 隐藏所有内容
        for tab in self.tabs:
            tab["content"].pack_forget()

            # 根据是否为顶级标签页应用不同的非激活样式
            if self.is_top_level:
                # 顶级标签页非激活状态：灰底深灰色文字不加粗
                tab["button"].config(
                    relief="flat",
                    bg="#808080",  # 灰色背景
                    font=(font_family, font_size, "normal"),
                    foreground="#fcfcfc",  # 白色文字
                )
            else:
                # 内部标签页非激活状态：保持原有背景色，深灰色文字
                tab["button"].config(
                    relief="flat",
                    bg=tab["color"],
                    font=(font_family, font_size, "normal"),
                    foreground="#808080",  # 默认深灰色文字
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
                font=(font_family, font_size, "normal"),  # 加粗字体
                foreground="#000000",  # 黑色文字
            )
        else:
            # 内部标签页激活状态：使用更亮的颜色（之前的鼠标按下颜色）
            selected_color = self.mouse_up_colors.get(selected_tab["color"], "#ce93d8")

            selected_tab["button"].config(
                relief="flat", bg=selected_color, font=(font_family, font_size, "normal"), foreground="#000000"
            )

        # 更新对应内容框架样式的背景色，使其与选中标签的颜色保持一致
        # 只有内部标签页需要更新样式，顶级标签页不需要
        if not self.is_top_level:
            style_name = self.color_styles.get(selected_tab["color"], self.light_blue_style)
            self.style.configure(style_name, background=selected_color)

        # 更新背景色以匹配result_frame
        self._update_background_to_result_frame_color()

        # 调用标签页切换回调函数
        if self.tab_change_callback:
            self.tab_change_callback(tab_index)


class IPSubnetSplitterApp:
    """子网规划师主应用程序类

    这个类实现了一个子网规划的GUI应用程序，
    支持子网分割、子网规划、IP信息查询等功能。
    """
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
        self.app_name = _("app_name")
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
        self.ipv4_history = ["192.168.1.1", "10.0.0.1"]  # IPv4地址查询历史，两条初始记录
        self.ipv6_history = ["2001:0db8:85a3:0000:0000:8a2e:0370:7334", "fe80::1"]  # IPv6地址查询历史，两条初始记录

        # 图表相关属性（预声明，避免Attribute-defined-outside-init警告）
        self.planning_chart_frame = None
        self.planning_chart_canvas = None
        self.planning_chart_v_scrollbar = None
        self.planning_chart_data = None

        # 窗口背景色（预声明，动态更新）
        self.bg_color = None
        self.range_start_history = ["192.168.0.1", "10.0.0.1"]  # IP范围起始地址历史，两条初始记录
        self.range_end_history = ["192.168.30.254", "10.0.0.254"]  # IP范围结束地址历史，两条初始记录

        # 切分子网相关属性 - 使用deque优化历史记录管理
        self.split_parent_networks = deque(maxlen=100)
        self.split_networks = deque(maxlen=100)
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

        # 网段规划相关属性 - 使用deque优化历史记录管理
        self.planning_parent_networks = deque(maxlen=100)
        self.planning_parent_entry = None
        self.pool_tree = None
        self.pool_scrollbar = None
        self.requirements_tree = None
        self.requirements_scrollbar = None

        # 功能调试面板相关属性
        self.test_dialog = None  # 用于存储调试面板的引用，确保只能打开一个
        self.undo_delete_btn = None
        self.swap_btn = None
        self.planning_notebook = None
        self.execute_planning_btn = None
        self.allocated_frame = None
        self.allocated_tree = None
        self.planning_remaining_frame = None
        self.planning_remaining_tree = None

        # 窗口锁定相关属性
        self.width_locked = True  # 默认锁定窗口横向尺寸
        self.width_lock_var = None  # 初始化width_lock_var属性

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
        self.root.title(f"{_("app_name")} v{self.app_version}")
        # 设置应用图标
        try:
            # 使用PIL加载高分辨率图标
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Subnet_Planner.ico")
            if os.path.exists(icon_path):
                from PIL import Image, ImageTk
                # 打开图标文件
                icon_image = Image.open(icon_path)
                # 转换为PhotoImage对象
                photo = ImageTk.PhotoImage(icon_image)
                # 设置应用图标
                self.root.iconphoto(True, photo)
                # 保存引用，防止被GC回收
                self._icon_photo = photo
        except Exception as e:
            print(f"设置图标失败: {e}")
            # 降级方案：使用传统iconbitmap方法
            try:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Subnet_Planner.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
            except Exception as fallback_e:
                print(f"降级方案也失败: {fallback_e}")
        # 所有窗口大小、位置和限制设置都由主程序入口统一管理
        # 这里只设置窗口标题

        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use("vista")

        # 初始化样式管理器
        self.style_manager = init_style_manager(self.root)
        update_styles()

        # 初始化历史记录相关属性 - 使用deque提升性能
        self.history_states = deque(maxlen=20)
        self.current_history_index = -1
        self.planning_history_records = []

        # 添加组合键绑定，用于测试信息栏（彩蛋功能）
        self.root.bind('<Control-Shift-Key-I>', self.toggle_test_info_bar)
        self.test_info_bar_enabled = False

        # 创建主框架 - 调整内边距使其更加紧凑
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建信息栏 spacer - 固定高度的占位空间
        self.info_spacer = ttk.Frame(self.main_frame, style="Placeholder.TFrame")
        self.info_spacer.pack(side="bottom", fill="x")
        self.info_spacer.pack_forget()
        self.info_spacer.configure(height=30)

        # 创建信息栏框架 - 放在 spacer 内，使用 place 布局
        self.info_bar_frame = ttk.Frame(self.info_spacer, style="InfoBar.TFrame")
        # 初始时不显示，等待需要时才显示
        self.info_bar_frame.place_forget()

        # 创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块
        self.create_top_level_notebook()

        # 在右上角添加关于链接按钮和钉住按钮，确保它们显示在标题栏右侧
        self.create_about_link()

        # 绑定窗口大小变化事件，动态调整右上角按钮位置
        self.root.bind('<Configure>', self.on_window_configure, add='+')

        # 确保信息栏框架的grid布局配置正确
        self.info_bar_frame.grid_rowconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(1, weight=0)

        # 获取当前语言的字体设置
        font_family, font_size = get_current_font_settings()

        self.style.configure(
            "InfoBarCloseButton.TButton",
            padding=(2, 0),
            foreground="#9E9E9E",
            font=(font_family, 8),
            width=2,
        )

        self.info_bar_frame.grid_rowconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(1, weight=0)

        # 使用Text组件替代Label，以支持更灵活的文本布局
        self.info_label = tk.Text(
            self.info_bar_frame, wrap="none", padx=3, pady=0, height=0,
            borderwidth=0, relief="flat", state="disabled",
            font=(font_family, font_size),  # 使用与原Label相同的字体
            takefocus=False,  # 不接受焦点
            cursor="arrow",  # 显示普通箭头光标
            selectbackground="#f0f0f0",  # 选中背景与组件背景相同
            selectforeground="#000000",  # 选中前景与普通文本相同
            insertbackground="#f0f0f0",  # 插入光标颜色与背景相同
            highlightthickness=0  # 移除焦点高亮边框
        )
        # 设置左对齐
        self.info_label.tag_configure("justify", justify="left")
        self.info_label.grid(row=0, column=0, sticky="ew", padx=(0, 0), pady=2)
        # 禁用文本选择
        self.info_label.bind("<Button-1>", lambda e: "break")
        self.info_label.bind("<Double-1>", lambda e: "break")
        self.info_label.bind("<Triple-1>", lambda e: "break")
        self.info_label.bind("<B1-Motion>", lambda e: "break")
        self.info_label.bind("<Control-a>", lambda e: "break")

        self.info_close_btn = ttk.Button(
            self.info_bar_frame,
            text="✕",
            command=self.hide_info_bar,
            style="InfoBarCloseButton.TButton",
            cursor="hand2",
        )
        self.info_close_btn.grid(row=0, column=1, padx=(0, 3), pady=1, sticky="se")

        self.info_auto_hide_id = None
        self.info_auto_hide_scheduled_time = None  # 记录定时器设置的时间
        self.info_bar_animating = False

        # 初始化时获取并保存参考宽度
        self.root.update_idletasks()
        self.info_bar_ref_width = max(self.main_frame.winfo_width() - 20, 100)

        self.info_label.lift(self.info_close_btn)

        # 初始化图表数据
        self.chart_data = None

        # 初始化历史记录
        self.history_records = []

        # 创建临时标签用于测量文本宽度，避免重复创建和销毁
        if not hasattr(self, '_temp_label'):
            self._temp_label = tk.Label(self.root)
            self._temp_label.pack_forget()

        # 信息栏相关常量
        self.info_bar_left_offset = 235
        self.info_bar_right_offset = 136
        self.info_bar_padding = 3
        self.min_info_bar_width = 300
        self.close_btn_width = 30
        self.min_pixel_width = 50
        self.info_bar_place_left = 238
        self.info_bar_place_right = 136
        self.info_bar_place_y = 21.5
        self.info_bar_place_height = 30
        self.min_info_bar_place_width = 300

        """验证CIDR格式是否有效

        Args:
            cidr: 要验证的CIDR字符串

        Returns:
            bool: 如果CIDR格式有效则返回True，否则返回False
        """

    def update_history_listbox(self):
        """更新历史记录列表"""
        try:
            # 清空现有历史记录
            self.history_listbox.delete(0, tk.END)

            # 重新插入所有历史记录
            for index, history_record in enumerate(self.history_records, 1):
                # 格式化为: 1.  10.0.0.8/5 | 10.21.50.0/23
                formatted_record = f"{index}. {history_record['parent']}  |  {history_record['split']}"
                self.history_listbox.insert(tk.END, formatted_record)

            # 应用斑马条纹效果
            for index in range(self.history_listbox.size()):
                bg_color = "#d8d8d8" if (index + 1) % 2 == 0 else "#ffffff"
                self.history_listbox.itemconfigure(index, bg=bg_color)
        except (tk.TclError, AttributeError) as e:
            # 错误处理，确保GUI更新失败不会导致程序崩溃
            print(f"更新历史记录列表失败: {str(e)}")

    def reexecute_split(self):
        """从历史记录重新执行切分操作"""
        # 获取选中的历史记录索引
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            self.show_info(_("hint"), _("please_select_a_history_record"))
            return

        # 获取选中项的索引
        selected_index = selected_indices[0]

        # 获取对应索引的历史记录
        if selected_index >= len(self.history_records):
            return

        history_record = self.history_records[selected_index]
        parent = history_record['parent']
        split = history_record['split']

        # 填充到输入框
        self.parent_entry.delete(0, tk.END)
        self.parent_entry.insert(0, parent)
        self.split_entry.delete(0, tk.END)
        self.split_entry.insert(0, split)

        # 执行切分，设置from_history=True，不记入历史
        self.execute_split(from_history=True)

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

        # 获取当前需求池
        pool_requirements = []
        for item in self.pool_tree.get_children():
            values = self.pool_tree.item(item, "values")
            pool_requirements.append((values[1], int(values[2])))

        # 获取当前父网段
        parent = self.planning_parent_entry.get().strip()

        # 格式化需求信息
        req_str = ", ".join([f"{name}({hosts})" for name, hosts in subnet_requirements])
        pool_str = ", ".join([f"{name}({hosts})" for name, hosts in pool_requirements])

        # 创建操作记录
        history_record = {
            'action_type': action_type,
            'parent': parent,
            'requirements': subnet_requirements,
            'pool': pool_requirements,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'req_str': req_str,
            'pool_str': pool_str,
        }

        # 检查当前状态是否与上一个状态相同，如果相同则不保存
        if self.history_states:
            last_state = self.history_states[-1]
            # 比较子网需求、需求池和父网段
            if (last_state['requirements'] == subnet_requirements
                    and last_state['pool'] == pool_requirements
                    and last_state['parent'] == parent):
                return

        # 如果当前不是最新状态，截断历史记录
        if self.current_history_index < len(self.history_states) - 1:
            self.history_states = self.history_states[: self.current_history_index + 1]
            self.planning_history_records = self.planning_history_records[: self.current_history_index + 1]

        # 添加新状态(deque会自动管理大小,无需手动pop)
        self.history_states.append(history_record)
        self.planning_history_records.append(history_record)
        self.current_history_index += 1

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
            self.show_info(_("hint"), _("please_select_records_to_move").format(record_type=move_from))
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
                    self.show_error(_("error"), f"{move_to}{_("record_already_exists", name=name)}")
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
        self.update_planning_tables_zebra_stripes()

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
        if new_items:
            self.save_current_state("移动记录：从子网需求表到需求池")

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
        if new_items:
            self.save_current_state("移动记录：从需求池到子网需求表")

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
            if new_items:
                self.save_current_state("移动记录：从子网需求表到需求池")

        # 情况2：仅选中需求池数据，移动到子网需求表
        elif not selected_requirements and selected_pool_items:
            new_items = self._move_records_between_trees(
                source_tree=self.pool_tree,
                target_tree=self.requirements_tree,
                selected_items=selected_pool_items,
                move_from="需求池",
                move_to="子网需求表"
            )
            if new_items:
                self.save_current_state("移动记录：从需求池到子网需求表")

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
                    self.show_error(_("error"), f"{_("requirements_pool")}{_("record_already_exists", name=name)}")
                    return

            # 检查子网需求表
            all_req_names = []
            for item in self.requirements_tree.get_children():
                if item not in selected_requirements:
                    values = self.requirements_tree.item(item, "values")
                    all_req_names.append(values[1])

            for name in pool_names_to_swap:
                if name in all_req_names:
                    self.show_error(_("error"), f"{_("subnet_requirements")}{_("record_already_exists", name=name)}")
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
            self.update_planning_tables_zebra_stripes()

            # 保存交换操作到历史记录
            self.save_current_state("交换记录：子网需求表和需求池")

        # 情况4：未选中任何记录
        else:
            self.show_info(_("hint"), _("please_select_record_to_move_or_swap"))
            return

    def swap_records(self):
        """交换两个表格中选中的记录（支持多条记录，完全交换所有选中记录）"""
        selected_requirements = self.requirements_tree.selection()
        selected_pool_items = self.pool_tree.selection()

        # 检查是否同时选中了两个表格中的记录
        if not selected_requirements or not selected_pool_items:
            self.show_info(_("hint"), _("please_select_records_to_swap"))
            return

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
                self.show_error(_("error"), f"{_("requirements_pool")}{_("record_already_exists", name=name)}")
                return

        # 检查子网需求表：要交换到子网需求表的pool_names是否与子网需求表中已有的名称冲突（排除当前选中的req_items）
        all_req_names = []
        for item in self.requirements_tree.get_children():
            if item not in selected_requirements:
                values = self.requirements_tree.item(item, "values")
                all_req_names.append(values[1])

        for name in pool_names_to_swap:
            if name in all_req_names:
                self.show_error(_("error"), f"{_("subnet_requirements")}{_("record_already_exists", name=name)}")
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

        self.update_planning_tables_zebra_stripes()

        # 保存交换操作到历史记录
        action_type = (
            f"交换记录: 子网需求表 {len(selected_requirements)} 条记录 ↔ 需求池 {len(selected_pool_items)} 条记录"
        )
        self.save_current_state(action_type)

    def create_split_input_section(self):
        """创建子网切分功能的输入区域"""
        # 设置 split_frame 的 grid 布局，实现两列等宽
        self.split_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        self.split_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        self.split_frame.grid_rowconfigure(0, weight=0)
        self.split_frame.grid_rowconfigure(1, weight=1)

        # 左侧：输入参数面板
        input_frame = ttk.LabelFrame(
            self.split_frame, text=_("input_parameters"), padding=(10, 10, 10, 10)
        )
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))

        # 右侧：历史记录面板
        history_frame = ttk.LabelFrame(self.split_frame, text=_("history"), padding=(10, 10, 10, 10))
        history_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))

        # 配置 input_frame 的 grid 行列
        input_frame.grid_columnconfigure(0, minsize=30, weight=0)
        input_frame.grid_columnconfigure(1, minsize=0, weight=1)
        input_frame.grid_columnconfigure(2, weight=0)
        input_frame.grid_rowconfigure(0, weight=0, minsize=0)
        input_frame.grid_rowconfigure(1, weight=0)
        input_frame.grid_rowconfigure(2, weight=0)
        input_frame.grid_rowconfigure(3, weight=0, minsize=0)

        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()

        # 父网段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text=_("parent_network"), anchor="w", font=(font_family, font_size)).grid(
            row=1, column=0, sticky=tk.W + tk.N + tk.S, pady=8, padx=(10, 0)
        )
        # 初始化子网切分的历史记录列表
        self.split_parent_networks = ["10.0.0.0/8", "172.16.0.0/12"]  # 提供两条初始记录，改善宽度计算
        self.split_networks = ["10.21.50.0/23", "192.168.1.0/24"]  # 提供两条初始记录，改善宽度计算

        # 父网段 - 使用Combobox，支持下拉选择和即时验证
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.parent_entry)), '%P')
        self.parent_entry = ttk.Combobox(
            input_frame,
            values=self.split_parent_networks,  # 使用包含两条记录的列表
            font=(font_family, font_size),
            validate='all',
            validatecommand=vcmd,
        )
        self.parent_entry.grid(row=1, column=1, padx=10, pady=8, sticky=tk.EW + tk.N + tk.S)
        default_parent = "10.0.0.0/8"  # 默认父网段
        self.parent_entry.insert(0, default_parent)  # 默认值
        self.parent_entry.config(state="normal")  # 允许手动输入

        # 切分段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text=_("split_segments"), anchor="w", font=(font_family, font_size)).grid(
            row=2, column=0, sticky=tk.W + tk.N + tk.S, pady=8, padx=(10, 0)
        )
        vcmd = (self.root.register(lambda text: self.validate_cidr(text, self.split_entry)), '%P')
        self.split_entry = ttk.Combobox(
            input_frame,
            values=self.split_networks,  # 使用包含两条记录的列表
            font=(font_family, font_size),
            validate='all',
            validatecommand=vcmd,
        )
        self.split_entry.grid(row=2, column=1, padx=10, pady=8, sticky=tk.EW + tk.N + tk.S)
        default_split = "10.21.50.0/23"  # 默认切分段
        self.split_entry.insert(0, default_split)  # 默认值
        self.split_entry.config(state="normal")  # 允许手动输入

        # 按钮区域 - 执行按钮，跨四行的方形样式
        self.execute_btn = ttk.Button(input_frame, text=_("execute_split"), command=self.execute_split, width=10)
        self.execute_btn.grid(row=0, column=2, rowspan=4, padx=(0, 0), pady=0, sticky=tk.NSEW)

        # 配置 history_frame 的 grid 布局
        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)
        history_frame.grid_columnconfigure(0, weight=1)  # 表格列
        history_frame.grid_columnconfigure(1, weight=0)  # 滚动条列
        history_frame.grid_columnconfigure(2, weight=0)  # 按钮列

        # 创建历史记录列表 - 撑满整个框架
        self.history_listbox = tk.Listbox(
            history_frame, height=3, font=(font_family, font_size),
            highlightthickness=1, highlightbackground="#999999", highlightcolor="#999999",
            bd=0, selectbackground="#0078D7", selectforeground="white", takefocus=False
        )
        self.history_listbox.configure(activestyle="none")
        self.history_listbox.grid(row=0, column=0, sticky="nsew", rowspan=2)

        # 添加垂直滚动条
        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)

        # 使用通用滚动条配置
        self._setup_scrollbar(history_scroll, self.history_listbox, initial_hidden=True)

        # 绑定右键菜单
        self.bind_listbox_right_click(self.history_listbox)

        # 创建重新切分按钮 - 与执行切分按钮样式一致
        self.reexecute_btn = ttk.Button(
            history_frame, text=_("reexecute_split"), command=self.reexecute_split, width=10
        )
        self.reexecute_btn.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(5, 0))

    def adjust_remaining_tree_width(self):
        """调整剩余网段表表格的宽度，使其自适应窗口大小"""
        self.remaining_tree.update_idletasks()
        frame_width = self.remaining_frame.winfo_width()
        self.remaining_tree.column("index", width=40)

        items = self.remaining_tree.get_children()
        columns = ["cidr", "network", "netmask", "wildcard", "broadcast", "usable"]

        if not items and frame_width > 0:
            # 表格为空时均分宽度
            total_columns = 6
            available_width = frame_width - 70
            column_width = max(100, available_width // total_columns)
            for col in columns:
                self.remaining_tree.column(col, width=column_width)
        elif items:
            # 表格有数据时自适应内容
            for col in columns:
                self.remaining_tree.column(col, width="0")
                self.remaining_tree.update_idletasks()
                auto_width = self.remaining_tree.column(col, "width")
                self.remaining_tree.column(col, width=max(100, auto_width))

    def on_tab_change(self, tab_index):
        """标签页切换时的处理函数"""
        if tab_index == 2 and hasattr(self, 'chart_canvas'):
            self.draw_distribution_chart()

    def on_top_level_tab_change(self, tab_index):
        """顶级标签页切换时的处理函数"""
        # 检查是否有正在编辑的状态，有的话保存并清理
        if hasattr(self, 'current_edit_item') and self.current_edit_item is not None:
            # 直接销毁编辑框并清理状态，不保存
            if hasattr(self, 'edit_entry') and self.edit_entry:
                self.edit_entry.destroy()
            self._cleanup_edit_state()
        
    def _create_requirements_tree(self, parent, height=5, columns=("index", "name", "hosts"),
                                double_click_handler=None):
        """创建需求表格（子网需求表或需求池表）的通用方法

        Args:
            parent: 父容器
            height: 表格高度（行数）
            columns: 列名列表
            double_click_handler: 双击事件处理器

        Returns:
            ttk.Treeview: 创建的表格对象
        """
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        self.bind_treeview_right_click(tree)

        # 设置表头
        tree.heading("index", text=_("index"))
        tree.heading("name", text=_("subnet_name"))
        tree.heading("hosts", text=_("host_count"))

        # 设置列宽
        tree.column("index", width=40, minwidth=20, stretch=False, anchor="e")
        tree.column("name", width=80, minwidth=80, stretch=True)
        tree.column("hosts", width=80, minwidth=40, stretch=False)

        self.configure_treeview_styles(tree)

        # 绑定事件
        if double_click_handler:
            tree.bind("<Double-1>", double_click_handler)
        tree.bind("<Button-1>", self.on_treeview_click)

        return tree

    def create_top_level_notebook(self):
        """创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块"""
        self.top_level_notebook = ColoredNotebook(self.main_frame, style=self.style,
                                                 is_top_level=True, tab_change_callback=self.on_top_level_tab_change)
        self.top_level_notebook.pack(fill=tk.BOTH, expand=True)

        # 子网切分模块
        self.split_frame = ttk.Frame(self.top_level_notebook.content_area, padding="10")
        self.create_split_input_section()
        self.create_split_result_section()

        # 子网规划模块
        self.planning_frame = ttk.Frame(self.top_level_notebook.content_area, padding="10")
        self.setup_planning_page()

        # 高级工具模块
        self.advanced_frame = ttk.Frame(self.top_level_notebook.content_area, padding="10")
        self.setup_advanced_tools_page()

        # 添加顶级标签页
        self.top_level_notebook.add_tab(_("subnet_planning"), self.planning_frame, "#fce4ec")
        self.top_level_notebook.add_tab(_("subnet_split"), self.split_frame, "#fff3e0")
        self.top_level_notebook.add_tab(_("advanced_tools"), self.advanced_frame, "#e8f5e9")

    def create_split_result_section(self):
        """创建子网切分功能的结果显示区域"""
        result_frame = ttk.LabelFrame(self.split_frame, text=_("split_result"), padding="10")
        result_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=(0, 0), pady=(0, 0))

        # 配置 result_frame 的 grid 布局
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        # 导出结果按钮
        style_manager = get_style_manager()
        btn_width, __ = style_manager.get_button_size("export_result") if style_manager else (10, 25)
        self.export_btn = ttk.Button(result_frame, text=_("export_result"), command=self.export_result, width=btn_width)
        self.export_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 创建自定义笔记本控件
        self.notebook = ColoredNotebook(result_frame, style=self.style, tab_change_callback=self.on_tab_change)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.export_btn.lift()

        # 切分段信息页面
        self.split_info_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_blue_style)
        
        # 创建切分段信息表格
        self.split_tree = ttk.Treeview(self.split_info_frame, columns=("item", "value"), show="headings", height=5)
        # 添加右键复制功能
        self.bind_treeview_right_click(self.split_tree)
        self.split_tree.heading("item", text=_("item"))
        self.split_tree.heading("value", text=_("value"))
        # 设置合适的列宽
        self.split_tree.column("item", width=120, minwidth=120, stretch=False)
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
        self.bind_treeview_right_click(self.remaining_tree)
        self.remaining_tree.heading("index", text=_("index"))
        self.remaining_tree.heading("cidr", text=_("cidr"))
        self.remaining_tree.heading("network", text=_("network_address"))
        self.remaining_tree.heading("netmask", text=_("subnet_mask"))
        self.remaining_tree.heading("wildcard", text=_("wildcard_mask"))
        self.remaining_tree.heading("broadcast", text=_("broadcast_address"))
        self.remaining_tree.heading("usable", text=_("usable_address_count"))

        # 设置列宽，使用minwidth替代width，让列可以自适应
        self.remaining_tree.column("index", minwidth=40, width=40, stretch=False, anchor="e")
        self.remaining_tree.column("cidr", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("network", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("netmask", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("wildcard", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("broadcast", minwidth=100, width=130, stretch=True)
        self.remaining_tree.column("usable", minwidth=100, width=110, stretch=True)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.remaining_tree)

        # 网段分布图页面
        self.chart_frame = ttk.Frame(self.notebook.content_area, padding="5", style=self.notebook.light_purple_style)

        # 添加标签页，每个标签页设置不同的颜色
        self.notebook.add_tab(_("split_segment_info"), self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab(_("remaining_subnets"), self.remaining_frame, "#e8f5e9")  # 浅绿色
        self.notebook.add_tab(_("distribution_chart"), self.chart_frame, "#f3e5f5")  # 浅紫色

        # 配置chart_frame的grid布局
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(1, weight=0)

        # 添加滚动条
        self.chart_scrollbar = ttk.Scrollbar(self.chart_frame, orient=tk.VERTICAL)

        # 创建Canvas用于绘制柱状图，设置背景色为深灰色以匹配图表背景
        # 禁止水平滚动，只允许垂直滚动
        self.chart_canvas = tk.Canvas(self.chart_frame, bg="#333333", highlightthickness=0)
        self.chart_canvas.grid(row=0, column=0, sticky=tk.NSEW, pady=0)

        # 使用通用滚动条配置
        self._setup_scrollbar(self.chart_scrollbar, self.chart_canvas, initial_hidden=False, widget_command=self.chart_canvas.yview)
        self.chart_canvas.config(xscrollcommand=None)
        self.chart_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 绑定窗口大小变化事件，实现图表自适应
        self.chart_canvas.bind("<Configure>", self.on_chart_resize)
        # 绑定鼠标滚轮事件
        self.chart_canvas.bind("<MouseWheel>", self.on_chart_mousewheel)

        # 配置remaining_frame的grid布局
        self.remaining_frame.grid_rowconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(1, weight=0)

        self.remaining_scroll_v = ttk.Scrollbar(
            self.remaining_frame, orient=tk.VERTICAL, command=self.remaining_tree.yview
        )

        # 使用通用滚动条配置
        self._setup_scrollbar(self.remaining_scroll_v, self.remaining_tree, initial_hidden=False)
        self.remaining_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)

        # 绑定窗口大小变化事件，实现表格自适应
        self.root.bind("<Configure>", self.on_window_resize, add='+')

        # 初始提示
        self.clear_result()

        # Treeview表格线样式已在初始化时设置

        # 在窗口完全渲染后再调用动态计算方法，确保获取准确的高度
        self.root.after(100, self.setup_table_styles)

    def setup_table_styles(self):
        """设置表格样式"""
        # 图表滚动条已在初始化时配置，此处仅需要确保滚动条可见
        self.chart_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        self.chart_canvas.bind("<Configure>", self.on_chart_resize)
        self.chart_canvas.bind("<MouseWheel>", self.on_chart_mousewheel)

    def _add_result_tabs(self):
        """添加标签页到笔记本"""
        self.notebook.add_tab(_("split_segment_info"), self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab(_("remaining_subnets"), self.remaining_frame, "#e8f5e9")  # 浅绿色
        self.notebook.add_tab(_("distribution_chart"), self.chart_frame, "#f3e5f5")  # 浅紫色

    def _setup_scrollbars(self):
        """配置滚动条"""
        self.remaining_frame.grid_rowconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(1, weight=0)

        self.remaining_scroll_v = ttk.Scrollbar(
            self.remaining_frame, orient=tk.VERTICAL, command=self.remaining_tree.yview
        )

        def remaining_scrollbar_callback(*args):
            self.remaining_scroll_v.set(*args)
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                self.remaining_scroll_v.grid_remove()
            else:
                self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)

        self.remaining_tree.configure(yscrollcommand=remaining_scrollbar_callback)

        self.remaining_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)
        remaining_scrollbar_callback(0.0, 1.0)

    def _setup_initial_state(self):
        """设置初始状态"""
        self.root.bind("<Configure>", self.on_window_resize, add='+')
        self.clear_result()
        self.root.after(100, self.setup_table_styles)

    def setup_planning_page(self):
        """设置子网规划功能的界面"""
        # 直接使用self.planning_frame，移除中间层main_planning_frame

        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 设置grid布局
        self.planning_frame.grid_columnconfigure(0, weight=1)  # 左侧列可伸缩
        self.planning_frame.grid_columnconfigure(1, weight=1)  # 右侧列可伸缩
        self.planning_frame.grid_rowconfigure(0, weight=0)  # 父网段设置行，固定高度
        self.planning_frame.grid_rowconfigure(1, weight=0)  # 需求池和子网需求行，固定高度
        self.planning_frame.grid_rowconfigure(2, weight=1)  # 规划结果行，可伸缩

        # 父网段设置区域
        parent_frame = ttk.LabelFrame(self.planning_frame, text=_("parent_network_settings"), padding=(5, 10, 10, 10))
        parent_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=(0, 0))  # 左上角
        # 设置父网段设置面板的固定宽度
        parent_frame.configure(width=250)

        # 初始化父网段列表 - 为子网规划创建独立的历史记录列表
        self.planning_parent_networks = ["10.21.48.0/20", "192.168.0.0/16"]  # 提供两条初始记录，改善宽度计算

        # 父网段下拉文本框
        ttk.Label(parent_frame, text="").pack(side=tk.LEFT, padx=(0, 0))
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.planning_parent_entry)), '%P')
        self.planning_parent_entry = ttk.Combobox(
            parent_frame,
            values=self.planning_parent_networks,  # 使用包含两条记录的列表
            width=16,
            font=(font_family, font_size),
            validate='all',
            validatecommand=vcmd,
        )
        self.planning_parent_entry.pack(side=tk.LEFT, padx=(0, 5), fill=tk.X, expand=True)
        default_parent = "10.21.48.0/20"  # 默认父网段
        self.planning_parent_entry.insert(0, default_parent)  # 默认值
        self.planning_parent_entry.config(state="normal")  # 允许手动输入

        # 需求池区域
        history_frame = ttk.LabelFrame(self.planning_frame, text=_("requirements_pool"), padding=(10, 10, 0, 10))
        history_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))  # 左下角
        # 设置需求池面板的固定宽度
        history_frame.configure(width=250)

        # 子网需求区域
        requirements_frame = ttk.LabelFrame(self.planning_frame, text=_("subnet_requirements"), padding=(10, 10, 0, 10))
        requirements_frame.grid(
            row=0, column=1, rowspan=2, sticky="nsew", padx=(5, 0), pady=(0, 10)
        )  # 右侧跨两行
        # 设置子网需求面板的固定宽度
        requirements_frame.configure(width=250)

        # 内部容器框架，用于组织表格和按钮
        inner_frame = ttk.Frame(requirements_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        history_frame.grid_rowconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=0)
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_columnconfigure(1, weight=0)

        # 创建需求池表格
        self.pool_tree = self._create_requirements_tree(
            history_frame, height=6, double_click_handler=self.on_pool_tree_double_click
        )


        # 添加滚动条，确保只作用于表格，位于表格右侧
        self.pool_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)

        # 直接创建Treeview和滚动条
        self.pool_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.pool_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.pool_scrollbar.config(command=self.pool_tree.yview)
        self.pool_tree.config(yscrollcommand=self.pool_scrollbar.set)

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
        self.requirements_tree = self._create_requirements_tree(
            inner_frame, height=5, double_click_handler=self.on_requirements_tree_double_click
        )


        # 放置表格
        self.requirements_tree.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.requirements_scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL)

        # self.create_scrollable_treeview_with_grid(
        #     inner_frame, self.requirements_tree, self.requirements_scrollbar,
        #     tree_row=0, tree_column=1, scrollbar_row=0, scrollbar_column=2,
        #     tree_padx=(10, 0), scrollbar_padx=(0, 0)
        # )

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
        add_btn = ttk.Button(button_frame, text=_("add"), command=self.add_subnet_requirement, width=7)
        add_btn.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # 删除按钮
        delete_btn = ttk.Button(button_frame, text=_("delete"), command=self.delete_subnet_requirement, width=7)
        delete_btn.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        # 撤销按钮
        self.undo_delete_btn = ttk.Button(button_frame, text=_('undo'), command=self.undo, width=7)
        self.undo_delete_btn.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # 移动/交换按钮（根据选中情况自动判断操作）
        # 交换记录按钮 - 使用交换图标
        self.swap_btn = ttk.Button(button_frame, text=_("move_records"), command=self.move_records, width=7)
        self.swap_btn.grid(row=3, column=0, sticky="ew", pady=(0, 5))

        # 导入按钮
        import_btn = ttk.Button(button_frame, text=_("import"), command=self.import_requirements, width=7)
        import_btn.grid(row=6, column=0, sticky="ew", pady=(0, 0))


        # 添加示例数据 - 带斑马条纹标签
        requirements_data = [
            ("office", "20"),
            ("hr_department", "10"),
            ("finance_department", "10"),
            ("planning_department", "30"),
            ("legal", "10"),
            ("procurement", "10"),
            ("security", "10"),
            ("party", "20"),
            ("discipline", "10"),
            ("it_department", "20"),
            ("engineering", "20"),
            ("sales", "20"),
            ("rd", "15"),
            ("production", "100"),
            ("transportation", "20"),
        ]
        for index, (name_key, hosts) in enumerate(requirements_data, 1):
            tag = "even" if index % 2 == 0 else "odd"
            self.requirements_tree.insert("", tk.END, values=("", _(name_key), hosts), tags=(tag,))

        # 调用方法更新序号
        self.update_requirements_tree_zebra_stripes()

        self.configure_treeview_styles(self.requirements_tree)
        self.configure_treeview_styles(self.pool_tree)  # 配置需求池表格样式

        # 设置表格选择模式为多选，允许一次选择多条记录
        self.requirements_tree.configure(selectmode=tk.EXTENDED)
        self.pool_tree.configure(selectmode=tk.EXTENDED)

        # 删除原来的执行规划按钮容器
        # 按钮已移动到删除按钮下方

        # 规划结果区域 - 使用grid布局，跨两列显示
        result_frame = ttk.LabelFrame(self.planning_frame, text=_("planning_result"), padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky="nwse", pady=(0, 0))

        # 创建笔记本控件显示规划结果
        self.planning_notebook = ColoredNotebook(result_frame, style=self.style)
        self.planning_notebook.pack(fill=tk.BOTH, expand=True)

        # 保存初始状态到历史记录
        self.save_current_state("初始状态")

        # 设置统一的按钮宽度，使用合适的宽度确保文字完全显示
        style_manager = get_style_manager()
        button_width, __ = style_manager.get_button_size("export_planning") if style_manager else (10, 25)

        # 导出规划按钮 - 使用 place 布局手动控制位置，使用默认TButton样式
        export_planning_btn = ttk.Button(
            result_frame, text=_('export_planning'), command=self.export_planning_result, width=button_width
        )
        export_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 使用通用方法配置按钮样式
        self._setup_accent_button_style("Accent.TButton", "#1565c0", "#0d47a1", "#0d47a1")
        self._setup_accent_button_style("RedAccent.TButton", "#2e7d32", "#1b5e20", "#1b5e20")

        # 规划子网按钮 - 使用 place 布局，位于导出规划按钮左方，大小相同，使用默认TButton样式
        execute_btn_width, __ = style_manager.get_button_size("execute_planning") if style_manager else (10, 25)
        self.execute_planning_btn = ttk.Button(
            result_frame, text=_("execute_planning"), command=self.execute_subnet_planning, width=execute_btn_width
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

        self.bind_treeview_right_click(self.allocated_tree)

        # 设置列标题
        self.allocated_tree.heading("index", text=_("index"))
        self.allocated_tree.heading("name", text=_("subnet_name"))
        self.allocated_tree.heading("cidr", text=_("cidr"))
        self.allocated_tree.heading("required", text=_("required_count"))
        self.allocated_tree.heading("available", text=_("available_count"))
        self.allocated_tree.heading("network", text=_("network_address"))
        self.allocated_tree.heading("netmask", text=_("subnet_mask"))
        self.allocated_tree.heading("broadcast", text=_("broadcast_address"))

        # 设置列宽为自动，根据内容自动调整宽度
        self.allocated_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")  # 序号列固定宽度40
        self.allocated_tree.column("name", width=0, minwidth=100, stretch=True)  # 子网名称列自动宽度
        self.allocated_tree.column("cidr", width=0, minwidth=90, stretch=True)  # CIDR列自动宽度
        self.allocated_tree.column("required", width=0, minwidth=30, stretch=True)  # 需求数列自动宽度
        self.allocated_tree.column("available", width=0, minwidth=40, stretch=True)  # 可用数列自动宽度
        self.allocated_tree.column("network", width=0, minwidth=70, stretch=True)  # 网络地址列自动宽度
        self.allocated_tree.column("netmask", width=0, minwidth=100, stretch=True)  # 子网掩码列自动宽度
        self.allocated_tree.column("broadcast", width=0, minwidth=100, stretch=True)  # 广播地址列自动宽度

        allocated_v_scrollbar = ttk.Scrollbar(
            self.allocated_frame, orient=tk.VERTICAL
        )

        # 使用通用滚动条配置
        self._setup_scrollbar(allocated_v_scrollbar, self.allocated_tree, initial_hidden=False)
        self.allocated_frame.grid_rowconfigure(0, weight=1)
        self.allocated_frame.grid_columnconfigure(0, weight=1)
        self.allocated_tree.grid(row=0, column=0, sticky="nsew")
        allocated_v_scrollbar.grid(row=0, column=1, sticky="ns")

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

        self.bind_treeview_right_click(self.planning_remaining_tree)

        self.planning_remaining_tree.heading("index", text=_("index"))
        self.planning_remaining_tree.heading("cidr", text=_("cidr"))
        self.planning_remaining_tree.heading("network", text=_("network_address"))
        self.planning_remaining_tree.heading("netmask", text=_("subnet_mask"))
        self.planning_remaining_tree.heading("broadcast", text=_("broadcast_address"))
        self.planning_remaining_tree.heading("usable", text=_("usable_address_count"))

        # 设置列宽，所有列都启用拉伸以实现自适应
        self.planning_remaining_tree.column("index", width=40, minwidth=40, stretch=False, anchor="e")
        self.planning_remaining_tree.column("cidr", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column(
            "network", width=80, minwidth=70, stretch=True
        )  # 调小网络地址列宽并启用拉伸
        self.planning_remaining_tree.column("netmask", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("broadcast", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("usable", width=80, minwidth=60, stretch=True)

        remaining_v_scrollbar = ttk.Scrollbar(
            self.planning_remaining_frame,
            orient=tk.VERTICAL,
        )

        # 使用通用滚动条配置
        self._setup_scrollbar(remaining_v_scrollbar, self.planning_remaining_tree, initial_hidden=False)
        self.planning_remaining_frame.grid_rowconfigure(0, weight=1)
        self.planning_remaining_frame.grid_columnconfigure(0, weight=1)
        self.planning_remaining_tree.grid(row=0, column=0, sticky="nsew")
        remaining_v_scrollbar.grid(row=0, column=1, sticky="ns")

        self.configure_treeview_styles(self.planning_remaining_tree)

        # 添加标签页 - 使用与切分结果一致的颜色
        self.planning_notebook.add_tab(_("allocated_subnets"), self.allocated_frame, "#e3f2fd")  # 浅蓝色
        self.planning_notebook.add_tab(_("remaining_subnets"), self.planning_remaining_frame, "#e8f5e9")  # 浅绿色

        self.planning_chart_frame = ttk.Frame(
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.light_purple_style
        )
        
        # 创建Canvas用于绘制图表
        self.planning_chart_canvas = tk.Canvas(
            self.planning_chart_frame,
            bg="#333333",
            highlightthickness=0
        )
        
        self.planning_chart_v_scrollbar = ttk.Scrollbar(
            self.planning_chart_frame,
            orient=tk.VERTICAL,
        )

        # 使用通用滚动条配置
        self._setup_scrollbar(self.planning_chart_v_scrollbar, self.planning_chart_canvas, initial_hidden=False, widget_command=self.planning_chart_canvas.yview)

        # 使用grid布局
        self.planning_chart_frame.grid_rowconfigure(0, weight=1)
        self.planning_chart_frame.grid_columnconfigure(0, weight=1)

        self.planning_chart_canvas.grid(row=0, column=0, sticky="nsew")
        self.planning_chart_v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 添加鼠标滚轮事件支持
        self.planning_chart_canvas.bind("<MouseWheel>", self.on_planning_chart_mousewheel)
        
        # 添加resize事件支持，确保图表能自适应窗口大小
        self.planning_chart_canvas.bind("<Configure>", self.on_planning_chart_resize)
        
        # 为规划模块添加图表标签页
        self.planning_notebook.add_tab(_("distribution_chart"), self.planning_chart_frame, "#f3e5f5")

        # 添加窗口大小变化事件处理，确保表格能自适应宽度
        self.planning_notebook.content_area.bind('<Configure>', lambda e: self.resize_tables())

        # 为规划模块表格添加空行或示例数据，显示斑马条纹效果
        for item in self.allocated_tree.get_children():
            self.allocated_tree.delete(item)
        for item in self.planning_remaining_tree.get_children():
            self.planning_remaining_tree.delete(item)

    def setup_table_zebra_styles(self):
        """在窗口完全渲染后初始化表格斑马纹样式"""
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

    def update_all_zebra_stripes(self):
        """批量更新所有表格的斑马条纹

        此方法统一更新所有需要斑马条纹效果的表格,
        避免重复调用 update_table_zebra_stripes 方法。
        """
        trees_to_update = []

        # 收集所有需要更新的表格
        if hasattr(self, 'split_tree'):
            trees_to_update.append(self.split_tree)
        if hasattr(self, 'remaining_tree'):
            trees_to_update.append(self.remaining_tree)
        if hasattr(self, 'allocated_tree'):
            trees_to_update.append(self.allocated_tree)
        if hasattr(self, 'planning_remaining_tree'):
            trees_to_update.append(self.planning_remaining_tree)

        # 批量更新所有表格
        for tree in trees_to_update:
            self.update_table_zebra_stripes(tree)

    def update_requirements_tree_zebra_stripes(self):
        """更新子网需求表的斑马条纹"""
        if hasattr(self, 'requirements_tree'):
            self.update_table_zebra_stripes(self.requirements_tree, update_index=True)

    def update_pool_tree_zebra_stripes(self):
        """更新需求池的斑马条纹"""
        if hasattr(self, 'pool_tree'):
            self.update_table_zebra_stripes(self.pool_tree, update_index=True)

    def update_planning_tables_zebra_stripes(self):
        """批量更新子网需求表和需求池的斑马条纹

        此方法统一更新规划模块的两个表格,减少重复代码。
        """
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()

    def auto_resize_columns(self, tree):
        """自动调整表格列宽以适应内容

        Args:
            tree: 要调整列宽的Treeview对象
        """

        # 为每列设置一个合理的默认最小宽度（基于列类型）
        default_min_widths = {
            'index': 60,
            'name': 120,
            'cidr': 80,
            'required': 70,
            'available': 70,
            'network': 100,
            'netmask': 100,
            'broadcast': 100,
            'wildcard': 100,
            'usable': 100,
            'size': 80,
        }

        # 调整列宽以适应表头
        for col in tree['columns']:
            # 获取表头文本
            header = tree.heading(col, 'text') or ''  # 确保header不是None

            # 跳过序号列，保持固定宽度
            if col == 'index':
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
        temp_window.title(_('add_subnet_requirement'))
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
        ttk.Label(main_frame, text=_("subnet_name") + ":").grid(row=0, column=1, sticky=tk.E, pady=15, padx=(10, 10))
        name_var = tk.StringVar()
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=20)
        name_entry.grid(row=0, column=2, sticky=tk.W, pady=15, padx=(0, 10))
        # 自动获得焦点，方便直接输入
        name_entry.focus_set()

        # 为子网名称添加验证
        def validate_name(text):
            is_valid = bool(text.strip())
            if name_entry.winfo_exists():
                name_entry.config(foreground='black' if is_valid else 'red')
            return "1"  # 始终允许输入，只做视觉提示
        name_entry.config(validate="all", validatecommand=(temp_window.register(validate_name), "%P"))

        # 主机数量 - 标签在中间列左侧，输入框在中间列右侧
        ttk.Label(main_frame, text=_("host_count") + ":").grid(row=1, column=1, sticky=tk.E, pady=15, padx=(10, 10))
        hosts_var = tk.StringVar()
        hosts_entry = ttk.Entry(main_frame, textvariable=hosts_var, width=20)
        hosts_entry.grid(row=1, column=2, sticky=tk.W, pady=15, padx=(0, 10))

        # 为主机数量添加验证
        def validate_hosts(text):
            # 允许空输入，只验证非空时是否为正整数
            if not text:
                if hosts_entry.winfo_exists():
                    hosts_entry.config(foreground='black')
                return "1"
            is_valid = text.isdigit() and int(text) > 0
            if hosts_entry.winfo_exists():
                hosts_entry.config(foreground='black' if is_valid else 'red')
            return "1"  # 始终允许输入，只做视觉提示
        hosts_entry.config(validate="all", validatecommand=(temp_window.register(validate_hosts), "%P"))

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
                self.show_error(_("error"), _("please_enter_subnet_name"))
                # 重新将焦点设置到子网名称输入框
                name_entry.focus_set()
                return

            if not hosts.isdigit() or int(hosts) <= 0:
                self.show_error(_("error"), _("please_enter_valid_host_count"))
                # 重新将焦点设置到主机数量输入框
                hosts_entry.focus_set()
                return

            # 检查是否存在相同名称的子网，同时检查子网需求表和需求池表
            for item in self.requirements_tree.get_children():
                values = self.requirements_tree.item(item, "values")
                existing_name = values[1]  # 子网名称在第二列
                if existing_name == name:
                    self.show_error(_("error"), _("subnet_already_exists", name=name))
                    name_entry.focus_set()
                    return

            for item in self.pool_tree.get_children():
                values = self.pool_tree.item(item, "values")
                existing_name = values[1]  # 子网名称在第二列
                if existing_name == name:
                    self.show_error(_("error"), f"{name}{_("msg_already_exists", name=name)}")
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
                current_rows = len(self.pool_tree.get_children())
                new_index = current_rows + 1
                tag = "even" if new_index % 2 == 0 else "odd"
                self.pool_tree.insert("", tk.END, values=(new_index, name, hosts), tags=(tag,))

                self.update_pool_tree_zebra_stripes()

            # 保存当前状态到操作记录，包含添加的子网信息
            self.save_current_state(f"添加子网: {name}({hosts})")

            temp_window.destroy()

        # 创建按钮并在按钮框架中居中
        save_requirement_btn = ttk.Button(
            button_frame, text=_('save_requirement'), command=lambda: save_requirement("requirements"), width=15
        )
        save_to_pool_btn = ttk.Button(button_frame, text=_('save_to_pool'), command=lambda: save_requirement("pool"), width=15)

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
            self.show_warning(_("hint"), _("please_select_record_to_delete"))
            return

        # 显示自定义的居中确认对话框
        confirm = self.show_custom_confirm(_("confirm_delete"), _("delete_confirmation_message"))
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
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 显示导入选项对话框
        dialog = tk.Toplevel(self.root)
        dialog.title(_("import_data"))
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.withdraw()

        # 计算居中位置，调整高度确保取消按钮能完整显示
        window_width = 350
        window_height = 280  # 适度增加高度以确保取消按钮显示完整
        self.center_window(dialog, window_width, window_height)

        dialog.deiconify()

        # 设置对话框为焦点
        dialog.focus_force()

        # 创建主内容框架
        main_frame = ttk.Frame(dialog, padding="20 20 20 0")  # 减少底部padding，确保所有控件能完整显示
        main_frame.pack(fill=tk.BOTH, expand=True)

        dialog.focus_force()

        # 说明文本
        info_text = _("choose_import_method")
        ttk.Label(main_frame, text=info_text, font=(font_family, font_size)).pack(pady=(0, 15))

        # 按钮框架 - 纵向排列，居中放置
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=0)

        # 导入文件按钮
        import_file_btn = ttk.Button(button_frame, text=_("import_from_file"),
                                    command=lambda: self._import_from_file(dialog),
                                    width=18)
        import_file_btn.pack(pady=15)

        # 将焦点聚焦到第一个按钮上
        import_file_btn.focus_force()

        # 下载Excel模板按钮
        download_excel_btn = ttk.Button(
            button_frame,
            text=_("download_excel_template"),
            command=lambda: self._generate_template("excel"),
            width=18
        )
        download_excel_btn.pack(pady=0)

        # 下载CSV模板按钮
        download_csv_btn = ttk.Button(
            button_frame,
            text=_("download_csv_template"),
            command=lambda: self._generate_template("csv"),
            width=18
        )
        download_csv_btn.pack(pady=5)

        # 取消按钮 - 直接放在主框架中，使用pack布局
        cancel_btn = ttk.Button(main_frame, text=_("cancel"), command=dialog.destroy, width=12)  # 增加宽度以确保"取消"文字完整显示
        cancel_btn.pack(pady=(20, 15), side=tk.RIGHT, padx=10)

    def _import_from_file(self, parent_dialog):
        """从文件导入数据

        Args:
            parent_dialog: 父对话框
        """
        parent_dialog.destroy()

        # 选择文件
        file_path = filedialog.askopenfilename(
            title=_("select_file_to_import"),
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
        except (ValueError, IOError, UnicodeDecodeError, TypeError) as e:
            self.show_error(_("error"), f"{_("msg_file_parse_failed")}: {str(e)}")
            return

        if not data_list:
            self.show_info(_("hint"), _("no_valid_data_found"))
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
                raise ValueError("无法识别文件编码，请确保文件使用UTF-8或GBK编码")

            for row_idx, row in enumerate(csv_data[1:], start=2):
                if row and len(row) >= 2:
                    name = str(row[0]).strip() if row[0] else ""
                    hosts = str(row[1]).strip() if row[1] else ""
                    if name and hosts:
                        data_list.append({"name": name, "hosts": hosts, "row": row_idx})

        else:
            raise ValueError("不支持的文件格式，请使用Excel (.xlsx) 或CSV (.csv) 文件")

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

        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item, "values")
            existing_names.add(values[1])

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
                              "error": _("subnet_already_exists", name=name)})
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
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        dialog = tk.Toplevel(self.root)
        dialog.title(_("import_data"))
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.withdraw()

        # 计算居中位置
        window_width = 750
        window_height = 500
        self.center_window(dialog, window_width, window_height)

        dialog.deiconify()

        dialog.focus_force()

        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 统计信息
        error_count = len(errors)
        total_count = len(data_list)
        valid_count = total_count - error_count

        summary_text = _("data_import_summary").format(total_count=total_count, valid_count=valid_count, error_count=error_count)
        ttk.Label(main_frame, text=summary_text, font=(font_family, font_size, 'bold')).pack(pady=(0, 10))

        # 创建表格显示所有数据
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        result_tree = ttk.Treeview(tree_frame, columns=("row", "name", "hosts", "status"),
                                  show="headings", height=12)
        result_tree.bind("<Button-3>", lambda event, t=result_tree: self.copy_cell_data(event, t))
        result_tree.heading("row", text=_("row_number"))
        result_tree.heading("name", text=_("subnet_name"))
        result_tree.heading("hosts", text=_("host_count"))
        result_tree.heading("status", text=_("status"))

        result_tree.column("row", width=40, minwidth=20, anchor="e")
        result_tree.column("name", width=100, minwidth=80)
        result_tree.column("hosts", width=60, minwidth=20)
        result_tree.column("status", width=400, minwidth=80)

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
                status = _("valid")
                # 有效数据用绿色标签
                tag = "valid"

            result_tree.insert("", tk.END, values=(row, name, hosts, status), tags=(tag,))

        # 配置标签样式
        result_tree.tag_configure("valid", foreground="green")
        result_tree.tag_configure("invalid", foreground="red")

        result_tree.tag_configure("even", background="#d8d8d8")
        result_tree.tag_configure("odd", background="#ffffff")

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
        import_pool_btn = ttk.Button(button_frame, text=_("import_requirements_pool"),
                                     command=lambda: self._import_valid_data(valid_data, "pool", dialog),
                                     width=15)
        import_pool_btn.pack(side=tk.LEFT, padx=5)

        # 导入到子网需求表按钮
        import_req_btn = ttk.Button(button_frame, text=_("import_subnet_requirements"),
                                    command=lambda: self._import_valid_data(valid_data, "requirements", dialog),
                                    width=15)
        import_req_btn.pack(side=tk.LEFT, padx=5)

        # 取消按钮 - 靠右显示，与其他按钮并排
        cancel_btn = ttk.Button(button_frame, text=_("cancel"), command=dialog.destroy, width=10)
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def _import_valid_data(self, valid_data, target_table, dialog=None):
        """导入有效数据

        Args:
            valid_data: 有效数据列表
            target_table: 目标表
            dialog: 对话框（可选）
        """
        if not valid_data:
            self.show_info(_("hint"), _("no_data_to_import"))
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
        self.show_info(_("success"), f"{_("successfully_imported")} {len(valid_data)} {_("records_to")}{target_name}")

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
            title=_("save_template"),
            defaultextension=default_ext,
            filetypes=filetypes,
            initialfile=f"{_("subnet_requirement_import_template")}{default_ext}",
            initialdir=""
        )

        if not file_path:
            return

        try:
            if template_type == "excel":
                # 生成Excel模板
                wb = Workbook()
                ws = wb.active
                ws.title = _("subnet_requirements")

                # 设置表头
                headers = [_("subnet_name"), _("host_count")]
                for col_idx, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col_idx, value=header)
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加示例数据
                example_data = [
                    [_("office"), "20"],
                    [_("hr_department"), "10"],
                    [_("finance_department"), "10"],
                    [_("planning_department"), "30"],
                    [_("it_department"), "20"],
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
                    writer.writerow([_("subnet_name"), _("host_count")])
                    # 写入示例数据
                    writer.writerow([_("office"), "20"])
                    writer.writerow([_("hr_department"), "10"])
                    writer.writerow([_("finance_department"), "10"])
                    writer.writerow([_("planning_department"), "30"])
                    writer.writerow([_("it_department"), "20"])

            self.show_info(_("success"), _("template_saved_to").format(file_path=file_path))

        except (IOError, ValueError, TypeError) as e:
            self.show_error(_("error"), f"{_("msg_template_generation_failed")}: {str(e)}")

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
        self.show_result(_("copied_to_clipboard"), keep_data=True)

    def bind_treeview_right_click(self, tree):
        """为Treeview绑定右键复制功能"""
        # 绑定右键菜单事件
        tree.bind("<Button-3>", lambda event, t=tree: self.copy_cell_data(event, t))

    def bind_listbox_right_click(self, listbox):
        """为Listbox绑定右键复制功能"""
        listbox.bind("<Button-3>", lambda event, lb=listbox: self.copy_listbox_data(event, lb))

    def copy_listbox_data(self, event, listbox):
        """复制Listbox选中项到剪贴板"""
        # 禁用事件，防止列表框捕获事件
        listbox.selection_clear(0, tk.END)
        # 获取鼠标点击位置的索引
        index = listbox.nearest(event.y)
        if index >= 0 and index < listbox.size():
            # 选中该项
            listbox.selection_set(index)
            # 获取数据
            cell_data = listbox.get(index)
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(cell_data)
            self.show_result(_("copied_to_clipboard"), keep_data=True)

    def _center_dialog(self, dialog):
        """将对话框居中显示在主窗口中"""
        dialog.update_idletasks()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()

        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2

        dialog.geometry(f"+{dialog_x}+{dialog_y}")
        dialog.deiconify()

    def _set_dialog_focus(self, dialog, ok_btn):
        """设置对话框焦点"""
        def set_focus():
            dialog.lift()
            dialog.focus_force()
            if ok_btn:
                ok_btn.focus_force()
        dialog.after_idle(set_focus)

    def show_custom_dialog(self, title, message, dialog_type="info"):
        """显示自定义的居中对话框，支持info、error、warning类型"""
        result = None

        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 确保主窗口完全初始化，先更新主窗口布局
        self.root.update_idletasks()

        # 获取当前焦点窗口，作为新对话框的父窗口
        parent_window = self.root.focus_get()
        if not parent_window or parent_window == self.root:
            parent_window = self.root

        # 创建Toplevel窗口，将父窗口设置为当前焦点窗口
        dialog = tk.Toplevel(parent_window)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(parent_window)  # 设置为父窗口的子窗口
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
        msg_label = ttk.Label(frame, text=message, wraplength=250, font=(font_family, font_size))
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
            ok_btn = ttk.Button(btn_frame, text=_("ok"), command=on_ok)
            ok_btn.pack(side=tk.RIGHT)

            # 绑定回车键和Esc键
            dialog.bind('<Return>', lambda e: on_ok())
            dialog.bind('<Escape>', lambda e: on_ok())

            # 设置对话框为焦点，并将焦点聚焦到确定按钮上
            dialog.focus_set()
            ok_btn.focus_set()

        # 计算并设置对话框居中位置
        self._center_dialog(dialog)

        # 在对话框显示后强制设置焦点
        self._set_dialog_focus(dialog, ok_btn)

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

    def _create_modal_dialog(self, title, width=500, height=150, parent_window=None, resizable=False):
        """创建模态对话框并居中显示

        Args:
            title: 对话框标题
            width: 对话框宽度（可选）
            height: 对话框高度（可选）
            parent_window: 父窗口（可选，默认为当前焦点窗口或主窗口）
            resizable: 是否允许调整大小（可选，默认为False）

        Returns:
            tk.Toplevel: 创建的对话框对象
        """
        self.root.update_idletasks()

        if not parent_window:
            parent_window = self.root.focus_get()
            if not parent_window or parent_window == self.root:
                parent_window = self.root

        dialog = tk.Toplevel(parent_window)
        dialog.title(title)
        dialog.resizable(resizable, resizable)
        dialog.transient(parent_window)
        dialog.grab_set()

        # 先隐藏对话框，避免定位过程中的闪现
        dialog.withdraw()

        # 设置对话框最小尺寸
        dialog.minsize(width=width, height=height)

        # 计算居中位置
        parent_width = parent_window.winfo_width()
        parent_height = parent_window.winfo_height()
        parent_x = parent_window.winfo_rootx()
        parent_y = parent_window.winfo_rooty()

        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2

        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.deiconify()

        return dialog

    def show_custom_confirm(self, title, message):
        """显示自定义的居中确认对话框"""
        result = None

        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        self.root.update_idletasks()

        parent_window = self.root.focus_get()
        if not parent_window or parent_window == self.root:
            parent_window = self.root

        dialog = tk.Toplevel(parent_window)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(parent_window)  # 设置为父窗口的子窗口
        dialog.grab_set()  # 模态对话框

        # 设置对话框最小宽度和高度
        dialog.minsize(width=500, height=150)

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # 设置frame的grid布局，让按钮垂直居中
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(2, weight=1)

        # 添加消息文本，居中显示，使用合适的wraplength
        msg_label = ttk.Label(frame, text=message, wraplength=450, font=(font_family, font_size))
        msg_label.grid(row=0, column=0, sticky="nsew", pady=(0, 20))

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, sticky="e")

        # 取消按钮
        def on_cancel():
            nonlocal result
            result = False
            dialog.destroy()

        cancel_btn = ttk.Button(btn_frame, text=_("cancel"), command=on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 确定按钮，使用默认样式
        def on_ok():
            nonlocal result
            result = True
            dialog.destroy()

        ok_btn = ttk.Button(btn_frame, text=_("ok"), command=on_ok)
        ok_btn.pack(side=tk.RIGHT)

        # 按钮创建后立即设置焦点
        ok_btn.focus_force()

        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())

        # 计算并设置对话框居中位置
        self._center_dialog(dialog)

        # 在对话框显示后强制设置焦点
        self._set_dialog_focus(dialog, ok_btn)

        self.root.wait_window(dialog)

        return result

    def undo(self):
        """撤销最近的操作，支持多次撤销，包括删除、移动、导入等操作"""
        # 检查是否有可撤销的操作
        if self.current_history_index <= 0:
            self.show_info(_("hint"), _("no_undoable_operation"))
            return

        # 回到上一个状态
        self.current_history_index -= 1
        # 获取上一个状态
        previous_state = self.history_states[self.current_history_index]

        # 清空当前的子网需求表和需求池表
        for item in self.requirements_tree.get_children():
            self.requirements_tree.delete(item)
        for item in self.pool_tree.get_children():
            self.pool_tree.delete(item)

        # 恢复子网需求表
        for req in previous_state['requirements']:
            name, hosts = req
            self.requirements_tree.insert("", tk.END, values=("", name, hosts))

        # 恢复需求池表
        for pool_item in previous_state['pool']:
            name, hosts = pool_item
            self.pool_tree.insert("", tk.END, values=("", name, hosts))

        # 更新序号和斑马条纹
        self.update_requirements_tree_zebra_stripes()
        self.update_pool_tree_zebra_stripes()

        # 显示成功提示
        # 获取当前状态的 action_type，即被撤销的操作类型
        current_state = self.history_states[self.current_history_index + 1] if self.current_history_index + 1 < len(self.history_states) else {"action_type": "未知操作"}
        self.show_info(_("success"), f"{_("successfully_undone")} {current_state['action_type']}")

    def undo_delete(self):
        """撤销最近的删除操作，支持多次撤销"""
        # 检查是否有删除记录历史
        if not self.deleted_history:
            self.show_info(_("hint"), _("no_undoable_delete_operation"))
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
        self.show_info(_("success"), f"{_("successfully_restored")} {len(deleted_records)} {_("records")}")

    def _on_treeview_double_click(self, tree, tree_name, event):
        """通用的双击Treeview单元格编辑处理函数

        Args:
            tree: Treeview组件
            tree_name: 表格名称标识
            event: 事件对象
        """
        region = tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)

        if not item or not column:
            return

        column_index = int(column[1:]) - 1
        if column_index == 0:  # 不允许编辑序号列
            return
        column_name = tree["columns"][column_index]

        current_value = tree.item(item, "values")[column_index]

        try:
            cell_x, cell_y, width, height = tree.bbox(item, column)
        except tk.TclError:
            return

        self.edit_entry = ttk.Entry(tree, width=width // 10)
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()

        def validate_edit(text):
            if column_index == 1:  # 子网名称列
                is_valid = bool(text.strip())
            elif column_index == 2:  # 主机数量列
                is_valid = text.isdigit() and int(text) > 0 if text else True
            else:
                is_valid = True
            if hasattr(self, 'edit_entry') and self.edit_entry is not None:
                self.edit_entry.config(foreground='black' if is_valid else 'red')
            return "1"
        self.edit_entry.config(validate="all", validatecommand=(self.root.register(validate_edit), "%P"))

        self.edit_entry.place(x=cell_x, y=cell_y, width=width, height=height)

        self.current_edit_item = item
        self.current_edit_column = column_name
        self.current_edit_column_index = column_index
        self.current_edit_tree = tree_name

        self.edit_entry.bind("<FocusOut>", self.on_edit_focus_out)
        self.edit_entry.bind("<Return>", self.on_edit_enter)
        self.edit_entry.bind("<Escape>", self.on_edit_escape)

    def on_requirements_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能（子网需求表）"""
        self._on_treeview_double_click(self.requirements_tree, "requirements", event)

    def on_pool_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能（需求池表）"""
        self._on_treeview_double_click(self.pool_tree, "pool", event)

    def on_edit_focus_out(self, event):
        """编辑框失去焦点时保存数据"""
        if hasattr(self, 'edit_entry') and self.edit_entry:
            # 获取当前编辑框的值
            new_value = self.edit_entry.get().strip()
            
            # 保存原始值，用于验证失败时恢复
            if self.current_edit_tree == "requirements":
                tree = self.requirements_tree
            else:
                tree = self.pool_tree
            original_value = tree.item(self.current_edit_item, "values")[self.current_edit_column_index]
            
            # 简单验证：如果值为空，使用原始值
            if not new_value:
                # 直接销毁编辑框并清理状态，不显示错误
                self.edit_entry.destroy()
                self._cleanup_edit_state()
                return
            
            # 验证新值
            validation_error = self._validate_edit_value(new_value)
            if validation_error:
                # 验证失败，直接销毁编辑框并清理状态，不显示错误
                self.edit_entry.destroy()
                self._cleanup_edit_state()
                return
            
            # 验证通过，调用save_edit保存，并标记是从焦点丢失事件调用
            self.save_edit(from_focus_out=True)

    def on_edit_enter(self, event):
        """按下Enter键时保存数据"""
        if hasattr(self, 'edit_entry') and self.edit_entry:
            self.save_edit()

    def on_edit_escape(self, event):
        """按下Escape键时取消编辑"""
        if hasattr(self, 'edit_entry') and self.edit_entry:
            self.edit_entry.destroy()
        self._cleanup_edit_state()

    def on_treeview_click(self, event):
        """处理Treeview左键单击事件，实现取消选择功能"""
        # 检查是否有正在编辑的状态
        if hasattr(self, 'current_edit_item') and self.current_edit_item is not None:
            # 获取当前编辑的表格
            if self.current_edit_tree == "requirements":
                current_tree = self.requirements_tree
            else:
                current_tree = self.pool_tree
            
            # 保存当前编辑
            self.save_edit(from_focus_out=True)
        
        # 获取点击位置的信息
        tree = event.widget
        region = tree.identify_region(event.x, event.y)
        if region not in ("cell", "row"):
            return "break"

        # 获取点击的行
        item = tree.identify_row(event.y)
        if not item:
            return "break"

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

    def save_edit(self, from_focus_out=False):
        """保存编辑的数据
        
        Args:
            from_focus_out: 是否从焦点丢失事件调用，True表示不要重新设置焦点
        """
        if not hasattr(self, 'current_edit_item'):
            return

        new_value = self.edit_entry.get().strip()

        # 获取原始值
        if self.current_edit_tree == "requirements":
            tree = self.requirements_tree
            original_value = tree.item(self.current_edit_item, "values")[self.current_edit_column_index]
        else:
            tree = self.pool_tree
            original_value = tree.item(self.current_edit_item, "values")[self.current_edit_column_index]

        # 如果值没有变化，直接更新并清理
        if new_value == original_value:
            self._update_tree_and_cleanup(tree)
            return

        # 验证数据
        if not new_value:
            if not from_focus_out:
                self.show_error(_("error"), _("input_cannot_be_empty"))
                self.edit_entry.focus_set()
            else:
                # 从焦点丢失事件调用，直接销毁编辑框并清理
                self.edit_entry.destroy()
                self._cleanup_edit_state()
            return

        # 验证新值
        validation_error = self._validate_edit_value(new_value)
        if validation_error:
            if not from_focus_out:
                self.show_error(_("error"), validation_error)
                self.edit_entry.focus_set()
            else:
                # 从焦点丢失事件调用，直接销毁编辑框并清理
                self.edit_entry.destroy()
                self._cleanup_edit_state()
            return

        # 更新数据
        values = list(tree.item(self.current_edit_item, "values"))
        values[self.current_edit_column_index] = new_value
        tree.item(self.current_edit_item, values=values)

        # 更新斑马条纹
        if self.current_edit_tree == "requirements":
            self.update_requirements_tree_zebra_stripes()
        else:
            self.update_pool_tree_zebra_stripes()

        # 销毁编辑框并清理
        self.edit_entry.destroy()
        self._cleanup_edit_state()

    def _update_tree_and_cleanup(self, tree):
        """更新Treeview数据并清理编辑状态"""
        values = list(tree.item(self.current_edit_item, "values"))
        tree.item(self.current_edit_item, values=values)
        self.update_table_zebra_stripes(tree)
        self.edit_entry.destroy()
        self._cleanup_edit_state()

    def _validate_edit_value(self, new_value):
        """验证编辑的值

        Args:
            new_value: 新值

        Returns:
            str or None: 错误消息，如果验证通过则返回None
        """
        if self.current_edit_column == "name":
            # 检查是否存在相同名称的子网
            for tree, tree_name in [(self.requirements_tree, "requirements"), (self.pool_tree, "pool")]:
                for item in tree.get_children():
                    # 排除当前编辑的行
                    if tree_name == self.current_edit_tree and item == self.current_edit_item:
                        continue
                    values = tree.item(item, "values")
                    if values[1] == new_value:  # 子网名称在第二列
                        return _("subnet_already_exists", name=new_value)

        elif self.current_edit_column == "hosts":
            try:
                hosts = int(new_value)
                if hosts <= 0:
                    return _("host_count_must_be_greater_than_0")
            except ValueError:
                return _("host_count_must_be_integer")

        return None

    def _cleanup_edit_state(self):
        """清理编辑状态"""
        if hasattr(self, 'current_edit_item'):
            del self.current_edit_item
        if hasattr(self, 'current_edit_column'):
            del self.current_edit_column
        if hasattr(self, 'current_edit_column_index'):
            del self.current_edit_column_index
        if hasattr(self, 'current_edit_tree'):
            del self.current_edit_tree
        if hasattr(self, 'edit_entry'):
            del self.edit_entry
        self.edit_entry = None

    def execute_subnet_planning(self, from_history=False):
        """执行子网规划

        Args:
            from_history: 是否从历史记录重新执行，True表示不将操作记入历史
        """
        # 获取父网段
        parent = self.planning_parent_entry.get().strip()

        # 验证输入
        validation_result = self._validate_planning_input(parent)
        if not validation_result['valid']:
            self.show_error(_("error"), validation_result['error'])
            return

        # 获取子网需求
        subnet_requirements = []
        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item, "values")
            subnet_requirements.append((values[1], int(values[2])))

        if not subnet_requirements:
            self.show_error(_("error"), _("please_add_at_least_one_requirement"))
            return

        try:
            # 执行子网规划
            # 转换子网需求格式以匹配函数参数要求
            formatted_requirements = [{'name': name, 'hosts': hosts} for name, hosts in subnet_requirements]

            # 调用子网规划函数
            plan_result = suggest_subnet_planning(parent, formatted_requirements)

            # 检查是否有错误
            if 'error' in plan_result:
                self.show_error(_("error"), f"{_("subnet_planning_failed")}: {plan_result['error']}")
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

            self.auto_resize_columns(self.planning_remaining_tree)

            # 子网规划完成，不显示对话框提示

            # 如果不是从历史记录执行，将操作记录保存到历史
            if not from_history:
                # 使用通用方法更新父网段历史记录
                current_parent = self.planning_parent_entry.get().strip()
                self._update_history_entry(current_parent, self.planning_parent_networks, self.planning_parent_entry)

                # 保存当前状态到操作记录
                self.save_current_state("执行规划")

            # 生成网段分布图数据并绘制
            self.generate_planning_chart_data(plan_result)

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
            self.show_error(_("error"), message)
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_error(_("error"), f"{_("subnet_planning_failed")}: {_("unknown_error_occurred")} - {str(e)}")

    def generate_planning_chart_data(self, plan_result):
        """生成规划图表数据并绘制"""
        # 准备图表数据
        parent_cidr = plan_result["parent_cidr"]
        parent_info = get_subnet_info(parent_cidr)
        
        chart_data = {
            "parent": {
                "name": parent_cidr,
                "range": parent_info["num_addresses"]
            },
            "networks": [],
            "type": "plan"  # 添加图表类型字段，确保导出PDF时能正确识别
        }
        
        # 添加已分配子网（作为split类型）
        for subnet in plan_result["allocated_subnets"]:
            chart_data["networks"].append({
                "name": subnet["name"],
                "cidr": subnet["cidr"],
                "range": subnet["info"]["num_addresses"],
                "type": "split"
            })
        
        # 添加剩余子网（作为remaining类型）
        for i, subnet in enumerate(plan_result["remaining_subnets_info"]):
            chart_data["networks"].append({
                "name": plan_result["remaining_subnets"][i],
                "range": subnet["num_addresses"],
                "type": "remaining"
            })
        
        # 保存图表数据为实例属性，方便resize事件使用
        self.planning_chart_data = chart_data
        
        # 调用通用图表绘制函数
        draw_distribution_chart(self.planning_chart_canvas, chart_data, self.planning_chart_frame, chart_type="plan")

    def _create_scrollbar_callback(self, scrollbar, treeview=None, padx_adjust=0):
        """创建滚动条回调函数，实现自动隐藏功能

        Args:
            scrollbar: 滚动条组件
            treeview: Treeview组件（可选），用于调整padx
            padx_adjust: 滚动条隐藏时Treeview的右边距调整量

        Returns:
            function: 滚动条回调函数
        """
        def scrollbar_callback(*args):
            scrollbar.set(*args)
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                scrollbar.grid_remove()
                if treeview and padx_adjust:
                    try:
                        treeview.grid_configure(padx=padx_adjust)
                    except (tk.TclError, AttributeError):
                        pass
            else:
                scrollbar.grid()
                if treeview and padx_adjust:
                    try:
                        treeview.grid_configure(padx=0)
                    except (tk.TclError, AttributeError):
                        pass
        return scrollbar_callback

    def _validate_split_input(self, parent, split):
        """验证子网切分输入

        Args:
            parent: 父网段CIDR
            split: 切分段CIDR

        Returns:
            dict: 包含验证结果的字典 {'valid': bool, 'error': str or None}
        """
        # 验证输入不为空
        if not parent or not split:
            return {
                'valid': False,
                'error': _("parent_and_split_cidr_cannot_be_empty"),
                'error_code': 'empty_input'
            }

        # 验证父网段CIDR格式
        if not self.validate_cidr(parent):
            return {
                'valid': False,
                'error': _("invalid_parent_network_cidr"),
                'error_code': 'invalid_parent'
            }

        # 验证切分段CIDR格式
        if not self.validate_cidr(split):
            return {
                'valid': False,
                'error': _("invalid_split_segment_cidr"),
                'error_code': 'invalid_split'
            }

        return {'valid': True, 'error': None, 'error_code': None}

    def _validate_planning_input(self, parent):
        """验证子网规划输入

        Args:
            parent: 父网段CIDR

        Returns:
            dict: 包含验证结果的字典 {'valid': bool, 'error': str or None}
        """
        # 验证父网段不为空
        if not parent:
            return {
                'valid': False,
                'error': _("please_enter_parent_network"),
                'error_code': 'empty_parent'
            }

        # 验证父网段CIDR格式
        if not self.validate_cidr(parent):
            return {
                'valid': False,
                'error': _("invalid_parent_network_format"),
                'error_code': 'invalid_parent'
            }

        return {'valid': True, 'error': None, 'error_code': None}

    def _update_history_entry(self, value, history_container, entry_widget):
        """通用历史记录更新方法

        Args:
            value: 要添加的历史记录值
            history_container: 历史记录容器（deque或list）
            entry_widget: 关联的输入框组件
        """
        if value and value not in history_container:
            history_container.append(value)
            # 如果是deque，需要转换为list；如果是list，直接使用
            values_list = list(history_container) if isinstance(history_container, deque) else history_container
            entry_widget.config(values=values_list)

    def _setup_scrollbar(self, scrollbar, widget, initial_hidden=True, widget_command=None, padx_adjust=0):
        """通用的滚动条配置方法

        Args:
            scrollbar: 滚动条组件
            widget: 关联的组件（Treeview/Canvas/Listbox等）
            initial_hidden: 初始时是否隐藏滚动条
            widget_command: 滚动条回调命令（如widget.yview）
            padx_adjust: 隐藏滚动条时widget的padx调整量
        """
        # 设置滚动条的命令
        if widget_command:
            scrollbar.config(command=widget_command)
        widget.configure(yscrollcommand=scrollbar.set)

        # 创建滚动条回调
        scrollbar_callback = self._create_scrollbar_callback(scrollbar, widget, padx_adjust)
        widget.configure(yscrollcommand=scrollbar_callback)

        # 初始隐藏或显示滚动条
        if initial_hidden:
            scrollbar.grid_forget()
        scrollbar_callback(0.0, 1.0)

    def _setup_accent_button_style(self, style_name, background_color, active_color, pressed_color):
        """配置强调按钮样式

        Args:
            style_name: 样式名称（如 "Accent.TButton"）
            background_color: 背景颜色
            active_color: 悬停颜色
            pressed_color: 按下颜色
        """
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        self.style.configure(
            style_name,
            background=background_color,
            foreground="white",
            font=(font_family, font_size, "bold"),
            padding=6,
        )
        self.style.map(
            style_name,
            background=[
                ("active", active_color),
                ("!active", background_color),
                ("pressed", pressed_color),
            ],
            foreground=[("active", "white"), ("!active", "white"), ("pressed", "white")],
        )

    def execute_split(self, from_history=False):
        """执行切分操作

        Args:
            from_history: 是否从历史记录重新执行，True表示不将操作记入历史
        """
        parent = self.parent_entry.get().strip()
        split = self.split_entry.get().strip()

        # 验证输入
        validation_result = self._validate_split_input(parent, split)
        if not validation_result['valid']:
            # 清空表格并显示错误信息
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert("", tk.END, values=(_("error"), validation_result['error']), tags=("error",))
            self.show_error(_("input_error"), validation_result['error'])
            return

        try:
            # 调用切分函数
            result = split_subnet(parent, split)

            # 清空现有结果
            self.clear_tree_items(self.split_tree)
            self.clear_tree_items(self.remaining_tree)

            if "error" in result:
                # 显示错误信息
                self.split_tree.insert("", tk.END, values=(_("error"), result["error"]), tags=("error",))
                return

            # 添加切分段信息，同时设置斑马条纹标签
            row_index = 0
            self.split_tree.insert("", tk.END, values=(_("parent_network"), result["parent_info"]["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            
            # 切分网段
            self.split_tree.insert("", tk.END, values=(_("split_segment"), result["split_info"]["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(("-" * 10), ("-" * 20)), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1

            # 添加切分后的网段信息
            split_info = result["split_info"]
            self.split_tree.insert("", tk.END, values=(_("network_address"), split_info["network"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("subnet_mask"), split_info["netmask"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("wildcard_mask"), split_info["wildcard"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("broadcast_address"), split_info["broadcast"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("start_address"), split_info["host_range_start"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("end_address"), split_info["host_range_end"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("total_addresses"), split_info["num_addresses"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("usable_addresses"), split_info["usable_addresses"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("prefix_length"), split_info["prefixlen"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            self.split_tree.insert("", tk.END, values=(_("cidr"), split_info["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))

            # 显示剩余网段表表格
            if result["remaining_subnets_info"]:
                for i, network in enumerate(result["remaining_subnets_info"], 1):
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
                self.remaining_tree.insert("", tk.END, values=(1, _("none"), _("none"), _("none"), _("none"), _("none")))

            # 不再手动调整表格宽度，依靠Tkinter的stretch=True自动处理

            # 优化滚动条状态更新，减少不必要的计算
            if hasattr(self, 'remaining_scroll_v'):
                # 获取当前滚动位置
                yview = self.remaining_tree.yview()
                need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

                # 只在状态变化时才更新UI，减少不必要的刷新
                current_state = self.remaining_scroll_v.winfo_ismapped()
                if need_scrollbar != current_state:
                    if need_scrollbar:
                        self.remaining_scroll_v.grid(row=0, column=1, sticky=tk.NS)
                        self.remaining_scroll_v.set(yview[0], yview[1])
                    else:
                        self.remaining_scroll_v.grid_remove()

            self.prepare_chart_data(result, split_info, result["remaining_subnets_info"])

            # 绘制图表
            self.draw_distribution_chart()

            # 如果不是从历史记录重新执行，则将操作记录到历史列表
            if not from_history:
                # 使用通用方法更新父网段历史记录
                self._update_history_entry(parent, self.split_parent_networks, self.parent_entry)
                # 使用通用方法更新切分段历史记录
                self._update_history_entry(split, self.split_networks, self.split_entry)

                # 检查是否已存在相同的记录
                duplicate_exists = any(
                    record['parent'] == parent and record['split'] == split for record in self.history_records
                )

                # 如果不存在相同记录，则添加到历史记录
                if not duplicate_exists:
                    split_record = {'parent': parent, 'split': split}
                    self.history_records.append(split_record)

                    # 更新历史记录列表
                    self.update_history_listbox()

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
            self.split_tree.insert("", tk.END, values=(_("error"), message), tags=("error",))
        except (tk.TclError, AttributeError, TypeError) as e:
            self.clear_result()
            self.split_tree.insert("", tk.END, values=(_("error"), f"{_("unknown_error_occurred")}: {str(e)}"), tags=("error",))

    def clear_tree_items(self, tree):
        """清空表格中的所有项

        Args:
            tree: 要清空的Treeview对象
        """
        # 批量删除所有子项，减少UI更新次数
        children = tree.get_children()
        if children:
            tree.delete(*children)

    def animate_info_bar(self, animation_type):
        """通用信息栏动画函数

        Args:
            animation_type: 动画类型，'show' 或 'hide'
        """
        # 如果已经在动画中，则跳过
        if self.info_bar_animating:
            return

        # 取消之前的自动隐藏定时器
        if self.info_auto_hide_id:
            self.root.after_cancel(self.info_auto_hide_id)
            self.info_auto_hide_id = None

        # 如果是隐藏动画且信息栏未映射，则跳过
        if animation_type == 'hide' and not self.info_bar_frame.winfo_ismapped():
            return

        self.info_bar_animating = True

        # 获取主窗口宽度
        main_width = self.main_frame.winfo_width()
        bar_x = 10
        bar_width = int(main_width * 1) - 50

        # 确保宽度在合理范围内
        bar_width = max(bar_width, 100)
        bar_width = min(bar_width, main_width - 20)

        # 动画参数配置
        animation_config = {
            'show': {
                'current_y': 30,
                'target_y': 0,
                'step': 1,
                'delay': 15,
                'condition': lambda y, t: y <= t,
                'update_y': lambda y, s: y - s,
                'on_complete': lambda: self._on_show_animation_complete(bar_x, bar_width)
            },
            'hide': {
                'current_y': 0,
                'target_y': 30,
                'step': 2,
                'delay': 10,
                'condition': lambda y, t: y >= t,
                'update_y': lambda y, s: y + s,
                'on_complete': lambda: self._on_hide_animation_complete(bar_x, bar_width)
            }
        }

        config = animation_config[animation_type]
        current_y = config['current_y']
        target_y = config['target_y']
        step = config['step']
        delay = config['delay']
        condition = config['condition']
        update_y = config['update_y']
        on_complete = config['on_complete']

        def animate():
            nonlocal current_y
            current_y = update_y(current_y, step)
            if condition(current_y, target_y):
                current_y = target_y
                on_complete()
            else:
                # 确保 spacer 在显示动画时可见
                if animation_type == 'show' and not self.info_spacer.winfo_ismapped():
                    self.info_spacer.pack(side="bottom", fill="x")
                self.info_bar_frame.place(x=bar_x, y=current_y, width=bar_width, height=30)
                self.root.after(delay, animate)

        animate()

    def _on_show_animation_complete(self, bar_x, bar_width):
        """显示动画完成后的回调"""
        import time
        self.info_bar_frame.place(x=bar_x, y=0, width=bar_width, height=30)
        self.info_bar_animating = False
        # 设置5秒后自动隐藏
        self.info_auto_hide_id = self.root.after(5000, lambda: self.hide_info_bar(from_timer=True))
        self.info_auto_hide_scheduled_time = time.time()

    def _on_hide_animation_complete(self, _bar_x, _bar_width):
        """隐藏动画完成后的回调"""
        self.info_bar_frame.place_forget()
        self.info_spacer.pack_forget()
        self.info_bar_animating = False

    def hide_info_bar(self, from_timer=False):
        """隐藏信息栏"""
        import time
        
        # 如果是从定时器调用的，检查时间戳
        if from_timer and self.info_auto_hide_scheduled_time:
            current_time = time.time()
            if (current_time - self.info_auto_hide_scheduled_time) < 4.5:
                return
        
        self.animate_info_bar('hide')
        
    def toggle_info_bar_expand(self, event=None):
        """切换信息栏文本显示状态（完整/截断）"""
        if not hasattr(self, '_info_truncated') or not self._info_truncated:
            return
            
        # 切换显示状态
        self._info_currently_expanded = not self._info_currently_expanded
        
        if self._info_currently_expanded:
            # 获取当前字体设置
            from style_manager import get_current_font_settings
            font_family, _ = get_current_font_settings()
            font = tkfont.Font(family=font_family, size=10)
            
            # 获取当前信息栏宽度（保持不变）
            current_width = self.info_bar_frame.winfo_width()
            
            # 智能换行算法（符合中日英韩文字习惯）
            def smart_wrap_text(text, max_width):
                """智能文本换行算法，支持中日英韩文字的混合排版"""
                if not text:
                    return ""
                
                import re
                
                lines = []
                current_line = ""
                current_word = ""
                
                # 定义字符类型
                def get_char_type(char):
                    code = ord(char)
                    # CJK统一表意文字（中日韩）
                    if (0x4E00 <= code <= 0x9FFF or  # CJK统一表意文字
                        0x3400 <= code <= 0x4DBF or  # CJK扩展A
                        0x20000 <= code <= 0x2A6DF or  # CJK扩展B
                        0x2A700 <= code <= 0x2B73F or  # CJK扩展C
                        0x2B740 <= code <= 0x2B81F or  # CJK扩展D
                        0x2B820 <= code <= 0x2CEAF or  # CJK扩展E
                        0x2CEB0 <= code <= 0x2EBEF or  # CJK扩展F
                        0x30000 <= code <= 0x3134F or  # CJK扩展G
                        0x31350 <= code <= 0x323AF):  # CJK扩展H
                        return 'cjk'
                    # 日文假名
                    elif (0x3040 <= code <= 0x309F or  # 平假名
                          0x30A0 <= code <= 0x30FF):  # 片假名
                        return 'cjk'
                    # 韩文音节
                    elif 0xAC00 <= code <= 0xD7AF:
                        return 'cjk'
                    # CJK标点符号
                    elif (0x3000 <= code <= 0x303F or  # CJK标点
                          0xFF00 <= code <= 0xFFEF):  # 全角字符
                        return 'cjk_punct'
                    # 英文字母
                    elif char.isalpha():
                        return 'alpha'
                    # 数字
                    elif char.isdigit():
                        return 'digit'
                    # 空格
                    elif char.isspace():
                        return 'space'
                    # 其他标点符号
                    else:
                        return 'punct'
                
                # 判断是否可以在字符后换行
                def can_break_after(char_type, char):
                    if char_type == 'cjk':
                        return True
                    elif char_type == 'cjk_punct':
                        return True
                    elif char_type == 'space':
                        return True
                    elif char_type == 'punct':
                        return True
                    return False
                
                # 判断是否可以在字符前换行
                def can_break_before(char_type, char):
                    if char_type == 'cjk':
                        return True
                    elif char_type == 'cjk_punct':
                        return True
                    elif char_type == 'punct':
                        return True
                    return False
                
                i = 0
                while i < len(text):
                    char = text[i]
                    char_type = get_char_type(char)
                    
                    if char_type in ['alpha', 'digit']:
                        # 英文单词或数字，累积整个单词
                        current_word += char
                        i += 1
                        # 检查下一个字符是否是单词的一部分
                        while i < len(text):
                            next_char = text[i]
                            next_type = get_char_type(next_char)
                            if next_type in ['alpha', 'digit']:
                                current_word += next_char
                                i += 1
                            else:
                                break
                        
                        # 尝试添加单词到当前行
                        test_line = current_line + current_word
                        test_width = font.measure(test_line)
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            # 如果当前行不为空，先换行
                            if current_line:
                                lines.append(current_line)
                                current_line = current_word
                            else:
                                # 单词本身超过最大宽度，需要拆分
                                word_chars = list(current_word)
                                temp_line = ""
                                for wc in word_chars:
                                    test_w = temp_line + wc
                                    if font.measure(test_w) <= max_width:
                                        temp_line = test_w
                                    else:
                                        if temp_line:
                                            lines.append(temp_line)
                                        temp_line = wc
                                current_line = temp_line
                        current_word = ""
                    
                    elif char_type == 'cjk':
                        # CJK字符，可以单独换行
                        test_line = current_line + char
                        test_width = font.measure(test_line)
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = char
                        i += 1
                    
                    elif char_type == 'cjk_punct':
                        # CJK标点符号
                        test_line = current_line + char
                        test_width = font.measure(test_line)
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            # 标点符号不应该单独出现在行首
                            # 如果当前行不为空且回退一个字符后仍有内容，则回退换行
                            if current_line and len(current_line) > 0:
                                # 回退到前一个字符位置换行
                                lines.append(current_line[:-1])
                                current_line = current_line[-1] + char
                            elif current_line:
                                # 当前行只有一个字符，直接换行
                                lines.append(current_line)
                                current_line = char
                            else:
                                # 如果当前行为空，标点符号单独成行
                                lines.append(char)
                                current_line = ""
                        i += 1
                    
                    elif char_type == 'space':
                        # 空格，尝试添加到当前行
                        test_line = current_line + char
                        test_width = font.measure(test_line)
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            # 空格会导致超出宽度，先换行
                            if current_line:
                                lines.append(current_line)
                            current_line = ""
                        i += 1
                    
                    elif char_type == 'punct':
                        # 英文标点符号
                        test_line = current_line + char
                        test_width = font.measure(test_line)
                        
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            # 标点符号不应该单独出现在行首
                            # 如果当前行不为空且回退一个字符后仍有内容，则回退换行
                            if current_line and len(current_line) > 0:
                                # 回退到前一个字符位置换行
                                lines.append(current_line[:-1])
                                current_line = current_line[-1] + char
                            elif current_line:
                                # 当前行只有一个字符，直接换行
                                lines.append(current_line)
                                current_line = char
                            else:
                                # 如果当前行为空，标点符号单独成行
                                lines.append(char)
                                current_line = ""
                        i += 1
                
                # 添加最后一行
                if current_line:
                    lines.append(current_line)
                
                return '\n'.join(lines)
            # 显示完整文本，首行加上图标
            # 先将图标添加到文本开头
            text_with_icon = self._info_icon + self._full_info_text
            
            # 计算最大行宽（不包括额外边距）
            max_line_width = current_width - 34  # 减去左右内边距
            
            # 对带图标的完整文本进行智能换行处理
            final_text = smart_wrap_text(text_with_icon, max_line_width)
            
            # 使用Text组件的方法设置文本
            self.info_label.configure(state="normal")
            self.info_label.delete(1.0, tk.END)
            self.info_label.insert(tk.END, final_text, "justify")
            
            # 根据消息类型设置文本颜色
            if "Error" in self._info_label_style:
                self.info_label.configure(fg="#c62828")  # 错误信息显示红色
            else:
                self.info_label.configure(fg="#424242")  # 正确信息显示灰色
            
            self.info_label.configure(state="disabled")
            
            # 计算需要显示的行数
            line_count = final_text.count('\n') + 1
            self.info_label.configure(height=line_count)
            
            # 强制更新布局，让label计算出正确的高度
            self.root.update_idletasks()
            
            # 获取label的实际高度
            label_height = self.info_label.winfo_reqheight()
            
            # 计算新的信息栏高度，添加额外的上下边距以确保文本完整显示
            # 给最后一行文字留出足够空间，添加4px额外高度
            new_height = label_height + 4  # 额外添加4px高度，确保最后一行完整显示
            new_height = max(new_height, 30)  # 最小高度30px
            
            # 更新信息栏框架高度
            self.info_bar_frame.place_configure(height=new_height)
            
            # 更新spacer高度，确保有足够空间显示
            self.info_spacer.configure(height=new_height)
            
            # 展开时停止自动消失计时
            if hasattr(self, 'info_auto_hide_id') and self.info_auto_hide_id:
                self.root.after_cancel(self.info_auto_hide_id)
                self.info_auto_hide_id = None
        else:
            # 显示截断文本
            # 重新计算截断文本
            def calculate_pixel_width(text):
                from style_manager import get_current_font_settings
                font_family, _ = get_current_font_settings()
                font = tkfont.Font(family=font_family, size=10)
                return font.measure(text)
            
            def truncate_text_by_pixel(text, icon, max_pixel_width):
                icon_width = calculate_pixel_width(icon)
                available_width = max_pixel_width - icon_width
                full_text_with_icon = icon + text
                full_width = calculate_pixel_width(full_text_with_icon)
                
                if full_width <= max_pixel_width:
                    return text
                
                ellipsis_width = calculate_pixel_width("...")
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
                
                truncated = text[:best_length]
                while best_length > 0:
                    truncated = text[:best_length]
                    truncated_width = calculate_pixel_width(truncated) + ellipsis_width + icon_width
                    if truncated_width <= max_pixel_width:
                        return truncated + "..."
                    best_length -= 1
                
                return "..."
            
            truncated_text = truncate_text_by_pixel(self._full_info_text, self._info_icon, self._info_max_pixel_width)
            
            # 使用Text组件的方法设置文本
            self.info_label.configure(state="normal")
            self.info_label.delete(1.0, tk.END)
            self.info_label.insert(tk.END, self._info_icon + truncated_text, "justify")
            
            # 根据消息类型设置文本颜色
            if "Error" in self._info_label_style:
                self.info_label.configure(fg="#c62828")  # 错误信息显示红色
            else:
                self.info_label.configure(fg="#424242")  # 正确信息显示灰色
            
            self.info_label.configure(state="disabled")
            
            # 恢复单行显示
            self.info_label.configure(height=1)
            
            # 恢复原始高度，宽度保持不变
            original_height = 30
            self.info_bar_frame.place_configure(height=original_height)
            self.info_spacer.configure(height=original_height)
            
            # 收起时重新开始自动消失计时
            if hasattr(self, 'root'):
                self.info_auto_hide_id = self.root.after(5000, lambda: self.hide_info_bar(from_timer=True))

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
        self.advanced_notebook.add_tab(_("ipv4_query"), self.ipv4_info_frame, "#e3f2fd")  # 浅蓝色
        self.advanced_notebook.add_tab(_("ipv6_query"), self.ipv6_info_frame, "#e8f5e9")  # 浅绿色
        self.advanced_notebook.add_tab(_("subnet_merge"), self.merge_frame, "#f3e5f5")  # 浅紫色
        self.advanced_notebook.add_tab(_("overlap_detection"), self.overlap_frame, "#fce4ec")  # 淡粉色

    def create_ipv6_info_section(self):
        """创建IPv6地址信息查询功能界面"""
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 在ipv6_info_frame中增加中间容器，内边距10
        content_container = ttk.Frame(self.ipv6_info_frame, padding="10")
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建输入区域
        input_frame = ttk.LabelFrame(content_container, text=_("ipv6_address_info"), padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # IPv6地址输入 - 使用Combobox，支持下拉选择和记忆功能
        ttk.Label(input_frame, text=_("ipv6_address")).pack(side=tk.LEFT, padx=(0, 5))
        self.ipv6_info_entry = ttk.Combobox(input_frame, values=self.ipv6_history, width=48, font=(font_family, font_size))
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
        ttk.Label(input_frame, text=_("cidr")).pack(side=tk.LEFT, padx=(0, 5))
        self.ipv6_cidr_var = tk.StringVar()
        self.ipv6_cidr_combobox = ttk.Combobox(
            input_frame, textvariable=self.ipv6_cidr_var, width=3, state="readonly", font=(font_family, font_size)
        )
        self.ipv6_cidr_combobox['values'] = list(range(1, 129))
        self.ipv6_cidr_combobox.current(63)  # 默认选择64
        self.ipv6_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))

        self.ipv6_info_btn = ttk.Button(input_frame, text=_("query_info"), command=self.execute_ipv6_info)
        self.ipv6_info_btn.pack(side=tk.RIGHT)

        # 创建结果区域
        result_frame = ttk.LabelFrame(content_container, text=_("query_result"), padding=(10, 10, 0, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview和垂直滚动条
        self.ipv6_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        self.bind_treeview_right_click(self.ipv6_info_tree)
        self.ipv6_info_tree.heading("item", text=_("project"))
        self.ipv6_info_tree.heading("value", text=_("value"))

        self.ipv6_info_tree.column("item", width=185, minwidth=185, stretch=False)
        self.ipv6_info_tree.column("value", width=200)

        ipv6_info_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)

        self.create_scrollable_treeview(result_frame, self.ipv6_info_tree, ipv6_info_scrollbar)

        self.configure_treeview_styles(self.ipv6_info_tree, include_special_tags=True)

    def create_merged_subnets_and_cidr_section(self):
        """创建子网合并和范围转CIDR功能界面"""
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
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
        subnet_frame = ttk.LabelFrame(left_frame, text=_("merge_subnets"), padding=(10, 10, 0, 10))
        subnet_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        # 配置左侧面板的grid布局
        left_frame.grid_rowconfigure(0, weight=1)  # 子网列表面板随窗体变化
        left_frame.grid_rowconfigure(1, weight=0)  # IP地址范围面板固定高度
        left_frame.grid_columnconfigure(0, weight=1)  # 第一列占满宽度

        # 子网合并列表输入文本框
        self.subnet_merge_text = tk.Text(subnet_frame, height=8, width=17, font=(font_family, font_size))

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
        self.merge_btn = ttk.Button(subnet_frame, text=_("merge_subnet"), command=self.execute_merge_subnets)
        self.merge_btn.grid(row=1, column=0, columnspan=1, sticky="w", pady=(5, 0), padx=(0, 10))

        # 左侧下方：IP地址范围 - 使用grid布局
        range_frame = ttk.LabelFrame(left_frame, text=_("ip_address_range"), padding="10")
        range_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))  # 仅水平填充，固定高度

        # 起始IP - 使用Combobox，支持下拉选择和记忆功能
        start_frame = ttk.Frame(range_frame)
        start_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(start_frame, text=_("start")).pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_start_entry = ttk.Combobox(
            start_frame, values=self.range_start_history, width=13, font=(font_family, font_size)
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
            entry.config(foreground='black' if is_valid else 'red')
            return "1"

        # 为起始IP添加验证
        def validate_start_ip(text):
            return validate_range_ip(text, self.range_start_entry)
        self.range_start_entry.config(validate="all", validatecommand=(self.range_start_entry.register(validate_start_ip), "%P"))

        validate_start_ip(self.range_start_entry.get())

        # 结束IP - 使用Combobox，支持下拉选择和记忆功能
        end_frame = ttk.Frame(range_frame)
        end_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(end_frame, text=_("end")).pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        self.range_end_entry = ttk.Combobox(end_frame, values=self.range_end_history, width=13, font=(font_family, font_size))
        self.range_end_entry.pack(side=tk.LEFT, pady=(0, 5))
        self.range_end_entry.insert(0, "192.168.30.254")
        self.range_end_entry.config(state="normal")  # 允许手动输入

        # 为结束IP添加验证
        def validate_end_ip(text):
            return validate_range_ip(text, self.range_end_entry)
        self.range_end_entry.config(validate="all", validatecommand=(self.range_end_entry.register(validate_end_ip), "%P"))

        validate_end_ip(self.range_end_entry.get())

        # 范围转CIDR按钮 - 靠左放置
        self.range_to_cidr_btn = ttk.Button(range_frame, text=_("convert_to_cidr"), command=self.execute_range_to_cidr)
        self.range_to_cidr_btn.pack(side=tk.LEFT, pady=(5, 0))

        # 右侧：CIDR结果
        self.merge_result_frame = ttk.LabelFrame(right_frame, text=_("cidr_result"), padding=(10, 10, 0, 10))
        self.merge_result_frame.pack(fill=tk.BOTH, expand=True)

        # 创建正常的结果树（非转置）
        columns = [_("cidr"), _("network_address"), _("subnet_mask"), _("broadcast_address"), _("host_count")]
        self.merge_result_tree = ttk.Treeview(self.merge_result_frame, columns=columns, show="headings")
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

        def scrollbar_callback(*args):
            scrollbar.set(*args)

            yview = treeview.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            if need_scrollbar:
                scrollbar.grid(row=scrollbar_row, column=scrollbar_column, sticky=tk.NS, padx=scrollbar_padx)
                treeview.grid_configure(row=tree_row, column=tree_column, sticky=tk.NSEW, padx=tree_padx)

                # 如果是需求池表或子网需求表，减小name列宽度为滚动条留出空间
                if treeview in [getattr(self, 'pool_tree', None), getattr(self, 'requirements_tree', None)]:
                    try:
                        treeview.column("name", width=110)  # 减小name列宽度
                    except tk.TclError:
                        pass  # 如果列不存在则忽略
            else:
                scrollbar.grid_remove()
                adjusted_padx = (tree_padx[0], tree_padx[1] + no_scrollbar_padx[1]) if tree_padx else no_scrollbar_padx
                treeview.grid_configure(row=tree_row, column=tree_column, sticky=tk.NSEW, padx=adjusted_padx)

        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=scrollbar_callback)

        treeview.grid(row=tree_row, column=tree_column, sticky=tk.NSEW, padx=tree_padx)
        scrollbar.grid(row=scrollbar_row, column=scrollbar_column, sticky=tk.NS, padx=scrollbar_padx)

        parent_frame.grid_rowconfigure(tree_row, weight=1)
        parent_frame.grid_columnconfigure(tree_column, weight=1)

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

        def scrollbar_callback(*args):
            scrollbar.set(*args)

            yview = text_widget.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            # 根据是否需要滚动条调整Text组件的右边距
            if need_scrollbar:
                scrollbar.grid(row=0, column=1, sticky=tk.NS)
                # 调整Text组件的grid配置，移除右边距
                text_widget.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=0)
            else:
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

        scrollbar_callback(0.0, 1.0)

    def create_ipv4_info_section(self):
        """创建IPv4地址信息查询功能界面"""
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 在ipv4_info_frame中增加中间容器
        content_container = ttk.Frame(self.ipv4_info_frame, padding="10")
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        input_frame = ttk.LabelFrame(content_container, text=_("ipv4_address_info"), padding="10")
        input_frame.pack(fill=tk.X, pady=(0, 10))

        # IP地址输入 - 使用Combobox，支持下拉选择和记忆功能
        ttk.Label(input_frame, text=_("ipv4_address")).pack(side=tk.LEFT, padx=(0, 5))
        self.ip_info_entry = ttk.Combobox(input_frame, values=self.ipv4_history, width=21, font=(font_family, font_size))
        self.ip_info_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.ip_info_entry.insert(0, "192.168.1.1")
        self.ip_info_entry.config(state="normal")  # 允许手动输入

        # IPv4地址验证函数
        def validate_ipv4(text):
            """验证IPv4地址格式"""
            text = text.strip()
            ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            is_valid = bool(re.match(ipv4_pattern, text)) if text else True
            if hasattr(self, 'ip_info_entry') and self.ip_info_entry.winfo_exists():
                self.ip_info_entry.config(foreground='black' if is_valid else 'red')
            return "1"

        self.ip_info_entry.config(validate="all", validatecommand=(self.root.register(validate_ipv4), "%P"))

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
        ttk.Label(input_frame, text=_("subnet_mask")).pack(side=tk.LEFT, padx=(0, 5))
        self.ip_mask_var = tk.StringVar()
        self.ip_mask_combobox = ttk.Combobox(
            input_frame, textvariable=self.ip_mask_var, width=15, state="readonly", font=(font_family, font_size)
        )
        self.ip_mask_combobox['values'] = list(self.subnet_mask_cidr_map.keys())
        self.ip_mask_combobox.current(list(self.subnet_mask_cidr_map.keys()).index("255.255.255.0"))
        self.ip_mask_combobox.pack(side=tk.LEFT, padx=(0, 10))
        # 绑定子网掩码选择事件
        self.ip_mask_combobox.bind("<<ComboboxSelected>>", self.on_subnet_mask_change)

        # CIDR下拉列表
        ttk.Label(input_frame, text="CIDR").pack(side=tk.LEFT, padx=(0, 5))
        self.ip_cidr_var = tk.StringVar()
        self.ip_cidr_combobox = ttk.Combobox(
            input_frame, textvariable=self.ip_cidr_var, width=3, state="readonly", font=(font_family, font_size)
        )
        self.ip_cidr_combobox['values'] = list(range(1, 33))
        self.ip_cidr_combobox.current(23)  # 默认选择24
        self.ip_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))
        # 绑定CIDR选择事件
        self.ip_cidr_combobox.bind("<<ComboboxSelected>>", self.on_cidr_change)

        self.ip_info_btn = ttk.Button(input_frame, text=_("query_info"), command=self.execute_ipv4_info)
        self.ip_info_btn.pack(side=tk.RIGHT)

        result_frame = ttk.LabelFrame(content_container, text=_("query_result"), padding=(10, 10, 0, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.ip_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        self.bind_treeview_right_click(self.ip_info_tree)
        self.ip_info_tree.heading("item", text=_("project"))
        self.ip_info_tree.heading("value", text=_("value"))

        self.ip_info_tree.column("item", width=185, minwidth=185, stretch=False)
        self.ip_info_tree.column("value", width=200)

        ip_info_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)
        ip_info_scrollbar.config(command=self.ip_info_tree.yview)

        def scrollbar_callback(*args):
            ip_info_scrollbar.set(*args)

            yview = self.ip_info_tree.yview()
            need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)

            if need_scrollbar:
                ip_info_scrollbar.grid(row=0, column=1, sticky=tk.NS)
                self.ip_info_tree.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=0)
            else:
                ip_info_scrollbar.grid_remove()
                self.ip_info_tree.grid_configure(row=0, column=0, sticky=tk.NSEW, padx=(0, 10))

        self.ip_info_tree.config(yscrollcommand=scrollbar_callback)

        self.ip_info_tree.grid(row=0, column=0, sticky=tk.NSEW)
        ip_info_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        scrollbar_callback(0.0, 1.0)

        self.configure_treeview_styles(self.ip_info_tree, include_special_tags=True)

    def create_subnet_overlap_section(self):
        """创建子网重叠检测功能界面"""
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 在overlap_frame中增加中间容器，内边距10
        content_container = ttk.Frame(self.overlap_frame, padding="10")
        content_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 创建左右两列框架
        left_frame = ttk.Frame(content_container)
        right_frame = ttk.Frame(content_container)

        content_container.grid_columnconfigure(0, minsize=191, weight=0)  # 固定左侧宽度，参考子网合并页面
        content_container.grid_columnconfigure(1, weight=1)  # 右侧自适应
        content_container.grid_rowconfigure(0, weight=1)  # 确保行能够撑满高度

        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # 左侧：子网列表
        input_frame = ttk.LabelFrame(left_frame, text=_("merge_subnets"), padding=(10, 10, 0, 10))
        input_frame.pack(fill=tk.BOTH, expand=True)

        # 子网输入文本框和滚动条
        text_frame = ttk.Frame(input_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.overlap_text = tk.Text(text_frame, height=10, width=17, font=(font_family, font_size))
        self.overlap_text.insert(tk.END, "192.168.0.0/24\n192.168.0.128/25\n10.0.0.0/16\n10.0.0.128/25\n10.0.10.0/20\n10.10.0.0/23")

        # 添加垂直滚动条，并使用通用方法创建带自动隐藏滚动条的Text组件
        overlap_text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL)

        self.create_scrollable_text(text_frame, self.overlap_text, overlap_text_scrollbar)

        # 检测重叠按钮 - 靠左放置
        self.overlap_btn = ttk.Button(input_frame, text=_("check_overlap"), command=self.execute_check_overlap)
        self.overlap_btn.pack(side=tk.LEFT, pady=(5, 0), padx=(0, 10))

        # 右侧：检测结果
        result_frame = ttk.LabelFrame(right_frame, text=_("detection_result"), padding=(10, 10, 0, 10))
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.overlap_result_tree = ttk.Treeview(result_frame, columns=("status", "message"), show="headings", height=5)
        self.bind_treeview_right_click(self.overlap_result_tree)
        self.overlap_result_tree.heading("status", text=_("status"))
        self.overlap_result_tree.heading("message", text=_("description"))

        self.overlap_result_tree.column("status", width=60, minwidth=60, stretch=True)
        self.overlap_result_tree.column("message", width=400, minwidth=400, stretch=True)

        overlap_result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL)

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
            columns = ["cidr", "network_address", "subnet_mask", "broadcast_address", "host_count"]
            self.merge_result_tree.config(columns=columns)

            # 设置列标题和宽度
            for i, col_key in enumerate(columns):
                self.merge_result_tree.heading(col_key, text=_(col_key))
                if i == 0:  # CIDR列
                    self.merge_result_tree.column(col_key, minwidth=120, stretch=True)
                elif i == 1:  # 网络地址列
                    self.merge_result_tree.column(col_key, minwidth=100, stretch=True)
                elif i == 2:  # 子网掩码列
                    self.merge_result_tree.column(col_key, minwidth=120, stretch=True)
                elif i == 3:  # 广播地址列
                    self.merge_result_tree.column(col_key, minwidth=100, stretch=True)
                elif i == 4:  # 主机数列
                    self.merge_result_tree.column(col_key, minwidth=40, stretch=True)

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
                self.show_info(_("hint"), _("enter_subnet_merge_list"))
                return

            # 解析子网合并列表
            subnets = [line.strip() for line in subnets_text.splitlines() if line.strip()]

            # 执行合并
            result = merge_subnets(subnets)

            if isinstance(result, dict) and "error" in result:
                self.show_info(_("error"), result["error"])
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

            self.auto_resize_columns(self.merge_result_tree)

            # 操作成功完成，添加到历史记录
            self.update_range_start_history()
            self.update_range_end_history()

        except ValueError as e:
            self.show_info(_("error"), f"{_("merge_subnet")}{_("failed")}: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info(_("error"), f"{_("operation_failed")}: {str(e)}")

    def execute_ipv6_info(self):
        """执行IPv6地址信息查询"""
        try:
            for item in self.ipv6_info_tree.get_children():
                self.ipv6_info_tree.delete(item)

            ipv6_full = self.ipv6_info_entry.get().strip()
            if not ipv6_full:
                self.show_info(_("hint"), _("enter_ipv6_address"))
                return

            # 移除CIDR前缀，获取纯IPv6地址
            ipv6 = ipv6_full.split('/')[0]
            cidr = self.ipv6_cidr_var.get()

            # 验证IPv6地址格式
            try:
                ipaddress.IPv6Address(ipv6)
            except ValueError as e:
                try:
                    # 使用handle_ip_subnet_error函数获取友好的错误信息
                    self.show_info(_("error"), handle_ip_subnet_error(e)["error"])
                    return
                except ValueError:
                    # 如果handle_ip_subnet_error失败，使用通用错误信息
                    self.show_info(_("error"), f"{_("ipv6_address")}{_("invalid_ip_format")}")
                    return

            # 构建网络字符串
            network_str = f"{ipv6}/{cidr}"
            ipv6_info = get_ip_info(network_str)
            original_ip_info = get_ip_info(ipv6)

            # 插入基本信息
            self.ipv6_info_tree.insert("", tk.END, values=(_("ip_address"), ipv6_info.get("ip_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("version"), ipv6_info.get("version", "")))
            ip_address = ipv6_info.get("ip_address", "")
            address_type = _("unknown")
            if ipv6_info.get("is_loopback"):
                address_type = _("loopback_address")
            elif ipv6_info.get("is_unspecified"):
                address_type = _("unspecified_address")
            elif ipv6_info.get("is_multicast"):
                address_type = _("multicast_address")
            elif ipv6_info.get("is_link_local"):
                address_type = _("link_local_unicast_address")
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                address_type = _("unique_local_unicast_address")
            elif ip_address.startswith("2001:0db8:"):
                address_type = _("documentation_test_address")
            elif ip_address.startswith("2000:"):
                address_type = _("global_unicast_address")
            elif "::ffff:" in ip_address:
                address_type = _("ipv4_mapped_ipv6_address")
            self.ipv6_info_tree.insert("", tk.END, values=(_("address_type"), address_type))
            self.ipv6_info_tree.insert("", tk.END, values=(_("cidr_prefix"), ipv6_info.get("cidr", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("prefix_length"), ipv6_info.get("prefix_length", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("network_address"), ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("broadcast_address"), ipv6_info.get("broadcast_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("subnet_mask"), ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("first_usable_host"), ipv6_info.get("first_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("last_usable_host"), ipv6_info.get("last_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("total_hosts"), ipv6_info.get("total_hosts", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("usable_hosts"), ipv6_info.get("usable_hosts", "")))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("address_format"), ""), tags=("section",))
            self.ipv6_info_tree.insert("", tk.END, values=(_("compressed_format"), ipv6_info.get("compressed", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("expanded_format"), ipv6_info.get("exploded", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("reverse_dns_format"), ipv6_info.get("reverse_dns", "")))

            if "::ffff:" in ip_address:
                mapped_ipv4 = ip_address.split("::ffff:")[-1]
                self.ipv6_info_tree.insert("", tk.END, values=(_("mapped_ipv4_address"), mapped_ipv4))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("address_properties"), ""), tags=("section",))
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_global_routable"), _("yes") if ipv6_info.get("is_global") else _("no"))
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_private_address"), _("yes") if ipv6_info.get("is_private") else _("no"))
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_link_local"), _("yes") if ipv6_info.get("is_link_local") else _("no"))
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_loopback"), _("yes") if ipv6_info.get("is_loopback") else _("no"))
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_multicast"), _("yes") if ipv6_info.get("is_multicast") else _("no"))
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_unspecified"), _("yes") if ipv6_info.get("is_unspecified") else _("no"))
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=(_("is_reserved"), _("yes") if ipv6_info.get("is_reserved") else _("no"))
            )
            self.ipv6_info_tree.insert("", tk.END, values=(_("is_ipv4_mapped"), _("yes") if "::ffff:" in ip_address else _("no")))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("address_structure_analysis"), ""), tags=("section",))

            prefix_analysis = ""
            if ipv6_info.get("is_multicast"):
                prefix_analysis = _("multicast_prefix")
                if ip_address.startswith("ff01:"):
                    prefix_analysis += _("interface_local_multicast")
                elif ip_address.startswith("ff02:"):
                    prefix_analysis += _("link_local_multicast")
                elif ip_address.startswith("ff05:"):
                    prefix_analysis += _("site_local_multicast")
                elif ip_address.startswith("ff0e:"):
                    prefix_analysis += _("global_multicast")
                else:
                    prefix_analysis += _("other_multicast_type")
            elif ip_address.startswith("fe80:"):
                prefix_analysis = _("link_local_prefix")
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                prefix_analysis = _("unique_local_prefix")
            elif ip_address.startswith("2000:") or ip_address.startswith("2001:") or ip_address.startswith("2002:"):
                prefix_analysis = _("global_unicast_prefix")
            elif ip_address.startswith("::ffff:"):
                prefix_analysis = _("ipv4_mapped_prefix")
            elif ip_address.startswith("64:ff9b::"):
                prefix_analysis = _("ipv4_ipv6_translation_prefix")
            elif ip_address.startswith("2001:db8::"):
                prefix_analysis = _("documentation_prefix")
            elif ip_address == "::1":
                prefix_analysis = _("loopback_address")
            elif ip_address == "::":
                prefix_analysis = _("unspecified_address")
            elif ip_address.startswith("100::"):
                prefix_analysis = _("blackhole_prefix")
            elif ip_address.startswith("2001:10::"):
                prefix_analysis = _("orchid_prefix")
            elif ip_address.startswith("fec0:"):
                prefix_analysis = _("deprecated_site_local_prefix")
            else:
                if ipv6_info.get("is_global"):
                    prefix_analysis = _("global_unicast_prefix_generic")
                elif ipv6_info.get("is_private"):
                    prefix_analysis = _("private_prefix")
                elif ipv6_info.get("is_link_local"):
                    prefix_analysis = _("link_local_prefix_generic")
                else:
                    prefix_analysis = _("unknown_prefix")
            user_cidr = ipv6_info.get("prefix_length", ipv6_info.get("cidr", 128))

            full_prefix_analysis = f"{prefix_analysis} {_('network_prefix')}：/{user_cidr}"
            self.ipv6_info_tree.insert("", tk.END, values=(_("prefix_analysis"), full_prefix_analysis))

            # 使用原始IP地址的展开格式计算段数（总是8段）
            segments_count = original_ip_info.get("exploded", "").split(":")
            if len(segments_count) > 1:
                self.ipv6_info_tree.insert("", tk.END, values=(_("address_segment_count"), f"{len(segments_count)}"))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("binary_representation"), ""), tags=("section",))
            self.ipv6_info_tree.insert("", tk.END, values=(_("ip_address"), ipv6_info.get("binary", "")))

            if ipv6_info.get("subnet_mask"):
                subnet_mask_value = ipv6_info["subnet_mask"]
                subnet_bin_value = subnet_mask_value.replace(':', '').zfill(32)
                subnet_bin_grouped = ' '.join([subnet_bin_value[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=(_("subnet_mask"), subnet_bin_grouped))

            if ipv6_info.get("network_address"):
                network_addr_value = ipv6_info["network_address"]
                network_bin_value = network_addr_value.replace(':', '').zfill(32)
                network_bin_grouped = ' '.join([network_bin_value[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=(_("network_address"), network_bin_grouped))

            if ipv6_info.get("broadcast_address"):
                broadcast_addr_value = ipv6_info["broadcast_address"]
                broadcast_bin_value = broadcast_addr_value.replace(':', '').zfill(32)
                broadcast_bin_grouped = ' '.join([broadcast_bin_value[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=(_("broadcast_address"), broadcast_bin_grouped))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("hexadecimal_representation"), ""), tags=("section",))
            self.ipv6_info_tree.insert("", tk.END, values=(_("ip_address"), ipv6_info.get("hexadecimal", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("subnet_mask"), ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("network_address"), ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=(_("broadcast_address"), ipv6_info.get("broadcast_address", "")))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("decimal_value_representation"), ""), tags=("section",))
            if "integer" in ipv6_info:
                self.ipv6_info_tree.insert("", tk.END, values=(_("ip_address"), ipv6_info["integer"]))

            if ipv6_info.get("subnet_mask"):
                subnet_mask = ipv6_info["subnet_mask"]
                subnet_int = int(ipaddress.IPv6Address(subnet_mask))
                self.ipv6_info_tree.insert("", tk.END, values=(_("subnet_mask"), subnet_int))

            if ipv6_info.get("network_address"):
                network_addr = ipv6_info["network_address"]
                network_int = int(ipaddress.IPv6Address(network_addr))
                self.ipv6_info_tree.insert("", tk.END, values=(_("network_address"), network_int))

            if ipv6_info.get("broadcast_address"):
                broadcast_addr = ipv6_info["broadcast_address"]
                broadcast_int = int(ipaddress.IPv6Address(broadcast_addr))
                self.ipv6_info_tree.insert("", tk.END, values=(_("broadcast_address"), broadcast_int))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("address_segment_details"), ""), tags=("section",))
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
                        values=(_("segment_index").format(i + 1), _("segment_value").format(segment, dec_value, bin_value)),
                    )
                else:
                    self.ipv6_info_tree.insert(
                        "", tk.END, values=(_("segment_index").format(i + 1), _("segment_value_zero"))
                    )

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("network_scale_and_usage"), ""), tags=("section",))

            prefix_length = ipv6_info.get("prefix_length", ipv6_info.get("cidr", 128))
            size_desc = ""
            if prefix_length == 128:
                size_desc = _("single_host_address")
            elif prefix_length == 64:
                size_desc = _("small_network")
            elif prefix_length == 48:
                size_desc = _("medium_network")
            elif 40 <= prefix_length <= 47:
                size_desc = _("regional_network").format(prefix_length)
            elif 32 < prefix_length <= 39:
                size_desc = _("large_network").format(prefix_length)
            elif prefix_length <= 32:
                size_desc = _("extra_large_network")
            else:
                size_desc = _("special_network").format(prefix_length)
            self.ipv6_info_tree.insert("", tk.END, values=(_("subnet_size"), size_desc))

            usage_desc = ""
            if ipv6_info.get("is_loopback"):
                usage_desc = _("purpose_loopback_ipv6")
            elif ipv6_info.get("is_link_local"):
                usage_desc = _("purpose_link_local")
            elif ipv6_info.get("is_multicast"):
                usage_desc = _("purpose_multicast_ipv6")
            elif "::ffff:" in ip_address:
                usage_desc = _("purpose_ipv4_mapped")
            elif ip_address.startswith("64:ff9b::"):
                usage_desc = _("purpose_ipv4_ipv6_translation")
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                usage_desc = _("purpose_ula")
            elif ip_address.startswith("2000:") or ip_address.startswith("2001:") or ip_address.startswith("2002:"):
                usage_desc = _("purpose_global_unicast")
            elif ip_address.startswith("2001:db8::"):
                usage_desc = _("purpose_documentation")
            elif ip_address.startswith("100::"):
                usage_desc = _("purpose_blackhole")
            elif ip_address.startswith("2001:10::"):
                usage_desc = _("purpose_orchid")
            elif ip_address == "::":
                usage_desc = _("purpose_unspecified")
            elif ip_address.startswith("fec0:"):
                usage_desc = _("purpose_deprecated_site_local")
            elif ipv6_info.get("is_global"):
                usage_desc = _("purpose_global_unicast")
            elif ipv6_info.get("is_private"):
                usage_desc = _("purpose_ula")
            else:
                usage_desc = _("purpose_specific")
            self.ipv6_info_tree.insert("", tk.END, values=(_("main_usage"), usage_desc))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("configuration_advice"), ""), tags=("section",))

            advice = ""
            if ipv6_info.get("is_global"):
                advice = _("advice_global_routable")
            elif ipv6_info.get("is_private"):
                advice = _("advice_private_network")
            if ipv6_info.get("prefix_length", 0) < 64:
                advice += _("advice_prefix_length")
            self.ipv6_info_tree.insert("", tk.END, values=(_("network_configuration"), advice))

            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=(_("rfc_standards_reference"), ""), tags=("section",))

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
            self.ipv6_info_tree.insert("", tk.END, values=(_("related_rfc"), rfc_ref))

            if ip_address.startswith("::ffff:"):
                ipv4_mapped = ip_address.replace("::ffff:", "")
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=(_("extended_information"), ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=(_("ipv4_mapped_address"), ipv4_mapped))

            elif ip_address.startswith("2001:0db8:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=(_("extended_information"), ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=(_("address_usage"), "文档/测试地址 (RFC 3849)"))
                self.ipv6_info_tree.insert("", tk.END, values=(_("rfc_specification"), "RFC 3849 - IPv6文档地址分配"))
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=(_("extended_information"), ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=(_("address_usage"), "唯一本地地址 (ULA)"))
                self.ipv6_info_tree.insert("", tk.END, values=(_("rfc_specification"), "RFC 4193 - IPv6唯一本地地址"))
            elif ip_address.startswith("fe80:"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=(_("extended_information"), ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=(_("address_usage"), "链路本地地址"))
                self.ipv6_info_tree.insert("", tk.END, values=(_("rfc_specification"), "RFC 4291 - IPv6寻址架构"))
            elif ipv6_info.get("is_multicast"):
                self.ipv6_info_tree.insert("", tk.END, values=())
                self.ipv6_info_tree.insert("", tk.END, values=(_("extended_information"), ""), tags=("section",))
                self.ipv6_info_tree.insert("", tk.END, values=(_("address_usage"), "组播地址"))
                self.ipv6_info_tree.insert("", tk.END, values=(_("rfc_specification"), "RFC 4291 - IPv6寻址架构"))

            self.update_ipv6_history()

        except ValueError as e:
            self.show_info(_("error"), f"{_("query_failed")}: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info(_("error"), f"{_("operation_failed")}: {str(e)}")

    def execute_ipv4_info(self):
        """执行IPv4地址信息查询"""
        try:
            for item in self.ip_info_tree.get_children():
                self.ip_info_tree.delete(item)

            ip = self.ip_info_entry.get().strip()
            if not ip:
                self.show_info(_("hint"), _("enter_ip_address"))
                return

            # 验证IPv4地址格式
            try:
                ipaddress.IPv4Address(ip)
            except ValueError as e:
                try:
                    error_info = handle_ip_subnet_error(e)
                    self.show_info(_("error"), error_info["error"])
                    return
                except ValueError:
                    self.show_info(_("error"), f"{_("ipv4_address")}{_("invalid_ip_format")}")
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
                self.ip_info_tree.insert("", tk.END, values=(_("ip_address"), ip))
                self.ip_info_tree.insert("", tk.END, values=(_("subnet_mask"), subnet_info["netmask"]))
                wildcard_mask = '.'.join(str(255 - int(octet)) for octet in subnet_info["netmask"].split('.'))
                self.ip_info_tree.insert("", tk.END, values=(_("wildcard_mask"), wildcard_mask))
                self.ip_info_tree.insert("", tk.END, values=(_("cidr"), subnet_info["cidr"]))
                # 网络类别
                network_class = info.get("class", "")
                class_text = _(f"class_{network_class.lower()}") if network_class else ""
                self.ip_info_tree.insert("", tk.END, values=(_("network_class"), class_text))
                self.ip_info_tree.insert("", tk.END, values=(_("default_netmask"), info.get("default_netmask", "")))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_address_range"), ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=(_("network_address"), subnet_info["network"]))
                self.ip_info_tree.insert("", tk.END, values=(_("broadcast_address"), subnet_info["broadcast"]))
                self.ip_info_tree.insert("", tk.END, values=(_("first_usable_address"), subnet_info["host_range_start"]))
                self.ip_info_tree.insert("", tk.END, values=(_("last_usable_address"), subnet_info["host_range_end"]))
                self.ip_info_tree.insert("", tk.END, values=(_("usable_hosts"), subnet_info["usable_addresses"]))
                self.ip_info_tree.insert("", tk.END, values=(_("total_hosts"), subnet_info["num_addresses"]))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_binary_representation"), ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=(_("ip_address"), info["binary"]))
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(_("subnet_mask"), '.'.join(f'{int(octet):08b}' for octet in subnet_info["netmask"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(
                        _("wildcard_mask"),
                        '.'.join(f'{255 - int(octet):08b}' for octet in subnet_info["netmask"].split('.')),
                    ),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(_("network_address"), '.'.join(f'{int(octet):08b}' for octet in subnet_info["network"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(_("broadcast_address"), '.'.join(f'{int(octet):08b}' for octet in subnet_info["broadcast"].split('.'))),
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_hexadecimal_representation"), ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=(_("ip_address"), info["hexadecimal"]))
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(_("subnet_mask"), '.'.join(f'{int(octet):02x}' for octet in subnet_info["netmask"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(
                        _("wildcard_mask"),
                        '.'.join(f'{255 - int(octet):02x}' for octet in subnet_info["netmask"].split('.')),
                    ),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(_("network_address"), '.'.join(f'{int(octet):02x}' for octet in subnet_info["network"].split('.'))),
                )
                self.ip_info_tree.insert(
                    "",
                    tk.END,
                    values=(_("broadcast_address"), '.'.join(f'{int(octet):02x}' for octet in subnet_info["broadcast"].split('.'))),
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_decimal_representation"), ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=(_("ip_address"), info["integer"]))
                self.ip_info_tree.insert("", tk.END, values=(_("subnet_mask"), str(ip_to_int(subnet_info["netmask"]))))
                wildcard_int = ip_to_int('.'.join(str(255 - int(octet)) for octet in subnet_info["netmask"].split('.')))
                self.ip_info_tree.insert("", tk.END, values=(_("wildcard_mask"), str(wildcard_int)))
                self.ip_info_tree.insert("", tk.END, values=(_("network_address"), str(ip_to_int(subnet_info["network"]))))
                self.ip_info_tree.insert("", tk.END, values=(_("broadcast_address"), str(ip_to_int(subnet_info["broadcast"]))))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_ip_properties"), ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=(_("version"), info["version"]))
                self.ip_info_tree.insert("", tk.END, values=(_("is_private"), _("yes") if info["is_private"] else _("no")))
                self.ip_info_tree.insert("", tk.END, values=(_("is_reserved"), _("yes") if info["is_reserved"] else _("no")))
                self.ip_info_tree.insert("", tk.END, values=(_("is_loopback"), _("yes") if info["is_loopback"] else _("no")))
                self.ip_info_tree.insert("", tk.END, values=(_("is_multicast"), _("yes") if info["is_multicast"] else _("no")))
                self.ip_info_tree.insert("", tk.END, values=(_("is_global"), _("yes") if info["is_global"] else _("no")))
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_link_local"), _("yes") if info["is_link_local"] else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_unspecified"), _("yes") if info["is_unspecified"] else _("no"))
                )

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_extended_info"), ""), tags=("section",))

                # IP地址用途
                if info["is_loopback"]:
                    ip_purpose = _("purpose_loopback")
                elif info["is_private"]:
                    ip_purpose = _("purpose_private")
                elif info["is_multicast"]:
                    ip_purpose = _("purpose_multicast")
                elif info["is_reserved"]:
                    ip_purpose = _("purpose_reserved")
                elif info["is_global"]:
                    ip_purpose = _("purpose_global")
                else:
                    ip_purpose = _("purpose_unknown")
                self.ip_info_tree.insert("", tk.END, values=(_("ip_purpose"), ip_purpose))

                # 子网规模
                subnet_size = subnet_info["usable_addresses"]
                if subnet_size <= 254:
                    size_desc = _("size_small")
                elif subnet_size <= 65534:
                    size_desc = _("size_medium")
                else:
                    size_desc = _("size_large")
                self.ip_info_tree.insert("", tk.END, values=(_("subnet_size"), size_desc))

                # 配置建议
                if subnet_size > 65534:
                    config_advice = _("advice_large_subnet")
                elif info["is_private"]:
                    config_advice = _("advice_private_network")
                else:
                    config_advice = _("advice_public_network")
                self.ip_info_tree.insert("", tk.END, values=(_("configuration_advice"), config_advice))
            else:
                # 基本信息模式
                self.ip_info_tree.insert("", tk.END, values=(_("ip_address"), info.get("ip_address", ip)))
                self.ip_info_tree.insert("", tk.END, values=(_("version"), info.get("version", "")))
                network_class = info.get("class", "")
                class_text = _(f"class_{network_class.lower()}") if network_class else ""
                self.ip_info_tree.insert("", tk.END, values=(_("network_class"), class_text))
                self.ip_info_tree.insert("", tk.END, values=(_("default_netmask"), info.get("default_netmask", "")))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("value_representation"), ""), tags=("section",))
                self.ip_info_tree.insert("", tk.END, values=(_("binary_representation"), info.get("binary", "")))
                self.ip_info_tree.insert("", tk.END, values=(_("hexadecimal_representation"), info.get("hexadecimal", "")))
                self.ip_info_tree.insert("", tk.END, values=(_("integer_representation"), info.get("integer", "")))

                self.ip_info_tree.insert("", tk.END, values=())
                self.ip_info_tree.insert("", tk.END, values=(_("section_ip_properties"), ""), tags=("section",))
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_private"), _("yes") if info.get("is_private", False) else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_reserved"), _("yes") if info.get("is_reserved", False) else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_loopback"), _("yes") if info.get("is_loopback", False) else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_multicast"), _("yes") if info.get("is_multicast", False) else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_global_routable"), _("yes") if info.get("is_global", False) else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_link_local"), _("yes") if info.get("is_link_local", False) else _("no"))
                )
                self.ip_info_tree.insert(
                    "", tk.END, values=(_("is_unspecified"), _("yes") if info.get("is_unspecified", False) else _("no"))
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

            self.update_ipv4_history()

        except ValueError as e:
            self.show_info(_("error"), f"{_("query_failed")}: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info(_("error"), f"{_("operation_failed")}: {str(e)}")

    def execute_range_to_cidr(self):
        """执行IP地址范围转CIDR操作"""
        try:
            for item in self.merge_result_tree.get_children():
                self.merge_result_tree.delete(item)

            # 获取输入的IP范围
            start_ip = self.range_start_entry.get().strip()
            end_ip = self.range_end_entry.get().strip()

            if not start_ip or not end_ip:
                self.show_info(_("hint"), "请输入完整的IP范围")
                return

            # 执行转换
            result = range_to_cidr(start_ip, end_ip)

            if isinstance(result, dict) and "error" in result:
                self.show_info(_("error"), result["error"])
                return

            cidr_list = result.get("cidr_list", [])

            # 转置表格：清空并重新创建列
            for item in self.merge_result_tree.get_children():
                self.merge_result_tree.delete(item)

            for col in self.merge_result_tree["columns"]:
                self.merge_result_tree.heading(col, text="")
            self.merge_result_tree.config(columns=())

            if not cidr_list:
                return

            # 创建转置后的列：第一列为属性名称，后续每列为一个CIDR
            columns = [_("attribute")] + cidr_list
            self.merge_result_tree.config(columns=columns)

            for i, col in enumerate(columns):
                self.merge_result_tree.heading(col, text=col)
                if i == 0:  # 第一列（属性列）
                    self.merge_result_tree.column(col, width=140, minwidth=140, stretch=False)  # 增大一半并固定
                else:  # 其他列
                    self.merge_result_tree.column(col, width=200)

            if hasattr(self, 'merge_result_scrollbar'):
                self.create_scrollable_treeview(
                    self.merge_result_frame,
                    self.merge_result_tree,
                    self.merge_result_scrollbar
                )

            # 定义要显示的属性列表
            properties = [
                ("cidr", lambda info, cidr: cidr),
                ("network_address", lambda info, cidr: info["network"]),
                ("subnet_mask", lambda info, cidr: info["netmask"]),
                ("broadcast_address", lambda info, cidr: info["broadcast"]),
                ("usable_addresses", lambda info, cidr: info["usable_addresses"]),
            ]

            # 填充转置后的数据
            row_index = 0
            for prop_key, prop_func in properties:
                row_values = [_(prop_key)]
                for cidr in cidr_list:
                    info = get_subnet_info(cidr)
                    row_values.append(prop_func(info, cidr))
                tag = "odd" if row_index % 2 == 0 else "even"
                self.merge_result_tree.insert("", tk.END, values=row_values, tags=(tag,))
                row_index += 1

            self.update_range_start_history()
            self.update_range_end_history()

        except ValueError as e:
            self.show_info(_("error"), f"{_("conversion_failed")}: {str(e)}")
        except (tk.TclError, AttributeError, TypeError) as e:
            self.show_info(_("error"), f"{_("operation_failed")}: {str(e)}")

    def execute_check_overlap(self):
        """执行子网重叠检测操作"""
        try:
            for item in self.overlap_result_tree.get_children():
                self.overlap_result_tree.delete(item)

            # 获取输入的子网列表
            subnets_text = self.overlap_text.get(1.0, tk.END).strip()
            if not subnets_text:
                self.show_info(_("hint"), _("enter_subnet_list"))
                return

            # 解析子网列表
            subnets = [line.strip() for line in subnets_text.splitlines() if line.strip()]

            # 执行重叠检测
            result = check_subnet_overlap(subnets)

            if isinstance(result, dict) and "error" in result:
                self.show_info(_("error"), result["error"])
                return

            overlaps = result.get("overlaps", [])
            row_index = 0

            # 如果没有重叠，显示无重叠信息
            if not overlaps:
                tag = "odd" if row_index % 2 == 0 else "even"
                self.overlap_result_tree.insert("", tk.END, values=(_("no_overlap"), _("no_subnet_overlap_detected")), tags=(tag,))
            else:
                # 显示所有重叠信息
                for overlap in overlaps:
                    status = _("overlap")
                    overlap_type = _(overlap['type'])
                    description = f"{overlap['subnet1']} {_('with')} {overlap['subnet2']} ({overlap_type})"
                    tag = "odd" if row_index % 2 == 0 else "even"
                    self.overlap_result_tree.insert("", tk.END, values=(status, description), tags=(tag,))
                    row_index += 1
            
            self.auto_resize_columns(self.overlap_result_tree)

        except (ValueError, tk.TclError, AttributeError, TypeError) as e:
            self.show_info(_("error"), f"{_("execute_subnet_overlap_detection_failed")}: {str(e)}")

    def _update_history(self, entry, history_list, value=None, max_items=10):
        """通用的历史记录更新方法

        Args:
            entry: Combobox或Entry组件
            history_list: 历史记录列表
            value: 要添加的值（可选，默认从entry获取）
            max_items: 最大历史记录数量（默认10）
        """
        if value is None:
            value = entry.get().strip()
        if value and value not in history_list:
            history_list.insert(0, value)
            if len(history_list) > max_items:
                history_list.pop()
            if hasattr(entry, 'configure'):
                entry['values'] = history_list

    def update_ipv4_history(self, event=None):
        """更新IPv4地址查询历史记录"""
        self._update_history(self.ip_info_entry, self.ipv4_history)

    def update_ipv6_history(self, event=None):
        """更新IPv6地址查询历史记录"""
        self._update_history(self.ipv6_info_entry, self.ipv6_history)

    def update_range_start_history(self, event=None):
        """更新IP范围起始地址历史记录"""
        self._update_history(self.range_start_entry, self.range_start_history)

    def update_range_end_history(self, event=None):
        """更新IP范围结束地址历史记录"""
        self._update_history(self.range_end_entry, self.range_end_history)

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

    def toggle_test_info_bar(self, event=None):
        """打开功能调试对话框（彩蛋功能）
        快捷键：Ctrl+Shift+I
        """
        # 检查调试面板是否已经存在
        if hasattr(self, 'test_dialog') and self.test_dialog is not None:
            try:
                # 尝试将对话框显示在最上层并设置焦点
                self.test_dialog.lift()
                self.test_dialog.focus_force()
                return
            except tk.TclError:
                # 如果对话框已被销毁，忽略错误并创建新对话框
                self.test_dialog = None

        # 创建功能调试对话框
        self.test_dialog = tk.Toplevel(self.root)
        self.test_dialog.title(_("function_debug"))
        self.test_dialog.resizable(False, False)  # 固定对话框大小，不可调节
        self.test_dialog.transient(self.root)

        # 绑定关闭事件，确保对话框关闭时更新状态
        self.test_dialog.protocol("WM_DELETE_WINDOW", self.close_test_dialog)

        self.test_dialog.focus_force()

        # 计算对话框居中显示的位置（相对于主窗口）
        dialog_width = 500  # 加大窗体宽度，适应不同语言
        dialog_height = 550  # 增加对话框高度，确保所有控件能完整显示

        # 获取主窗口的位置和大小
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # 计算对话框居中位置
        dialog_x = root_x + (root_width - dialog_width) // 2
        dialog_y = root_y + (root_height - dialog_height) // 2

        # 设置对话框大小和位置
        self.test_dialog.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")

        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()

        # 创建对话框内容框架
        content_frame = ttk.Frame(self.test_dialog, padding="15")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 使用grid布局管理器来精确控制各个组件的位置
        content_frame.grid_rowconfigure(0, weight=0)  # 标题行不扩展
        content_frame.grid_rowconfigure(1, weight=0)  # 说明行不扩展
        content_frame.grid_rowconfigure(2, weight=1)  # 按钮矩阵行扩展，用于垂直居中
        content_frame.grid_rowconfigure(3, weight=0)  # 主题切换行不扩展
        content_frame.grid_rowconfigure(4, weight=0)  # 窗口锁定行不扩展
        content_frame.grid_rowconfigure(5, weight=0)  # 关闭按钮行不扩展
        content_frame.grid_columnconfigure(0, weight=1)  # 唯一列扩展

        # 添加标题标签
        title_label = ttk.Label(content_frame, text=_("function_debug_panel"), font=(font_family, 12, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 15))

        # 添加说明标签
        desc_label = ttk.Label(content_frame, text=_("test_info_display_effect"))
        desc_label.grid(row=1, column=0, pady=(0, 15))

        # 创建按钮框架（使用grid布局实现3x2矩阵）
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=2, column=0, sticky=tk.NS)  # 垂直居中对齐

        # 按钮样式
        button_style = "TButton"
        button_width = 20  # 其他按钮宽度小一些
        original_button_width = 15  # 应用主题和关闭按钮保持原来宽度

        # 第一行按钮
        success_btn = ttk.Button(
            button_frame,
            text=_("test_success_message"),
            width=button_width,
            style=button_style,
            command=lambda: self.show_result(_("test_success_content"), error=False),
        )
        success_btn.grid(row=0, column=0, padx=5, pady=5)

        success_btn.focus_force()

        error_btn = ttk.Button(
            button_frame,
            text=_("test_error_message"),
            width=button_width,
            style=button_style,
            command=lambda: self.show_result(_("test_error_content"), error=True, keep_data=True),
        )
        error_btn.grid(row=0, column=1, padx=5, pady=5)

        # 第二行按钮
        long_text = _("test_long_text_content") * 5
        long_text_btn = ttk.Button(
            button_frame,
            text=_("test_long_text_message"),
            width=button_width,
            style=button_style,
            command=lambda: self.show_result(long_text, error=False),
        )
        long_text_btn.grid(row=1, column=0, padx=5, pady=5)

        # 中英文混排长文本测试按钮
        mixed_text = (
            (_("test_mixed_text_content") + "This is a long text with mixed " + _("db_language") + " and English characters. "
             ) * 5
        )
        mixed_text_btn = ttk.Button(
            button_frame,
            text=_("test_mixed_language"),
            width=button_width,
            style=button_style,
            command=lambda: self.show_result(mixed_text, error=False),
        )
        mixed_text_btn.grid(row=1, column=1, padx=5, pady=5)

        # 添加第三行按钮：隐藏信息栏和清空结果
        hide_info_btn = ttk.Button(
            button_frame, text=_(
            "hide_info_bar"), width=button_width, style=button_style, command=self.hide_info_bar
        )
        hide_info_btn.grid(row=2, column=0, padx=5, pady=5)

        clear_result_btn = ttk.Button(
            button_frame, text=_(
            "clear_subnet_split"), width=button_width, style=button_style, command=self.clear_result
        )
        clear_result_btn.grid(row=2, column=1, padx=5, pady=5)

        # 添加一键导出按钮
        one_click_export_btn = ttk.Button(
            button_frame, text=_("one_click_export"), width=button_width, style=button_style, command=self.one_click_export
        )
        one_click_export_btn.grid(row=3, column=0, padx=5, pady=5)
        
        # 添加一键PDF按钮
        one_click_pdf_btn = ttk.Button(
            button_frame, text=_("one_click_pdf"), width=button_width, style=button_style, command=self.one_click_pdf
        )
        one_click_pdf_btn.grid(row=3, column=1, padx=5, pady=5)

        # 主题切换部分
        theme_frame = ttk.LabelFrame(content_frame, text=_("theme_switch"), padding="10")
        theme_frame.grid(row=3, column=0, sticky=tk.EW, pady=(15, 10))

        # 配置主题切换框架的列
        theme_frame.grid_columnconfigure(0, weight=0)  # 标签列
        theme_frame.grid_columnconfigure(1, weight=1)  # 下拉列表列
        theme_frame.grid_columnconfigure(2, weight=0)  # 按钮列

        # 主题选择标签
        theme_label = ttk.Label(theme_frame, text=_("select_theme") + ":")
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
                        font=(font_family, 8),  # 使用统一的字体设置，大小为8
                        foreground="#9E9E9E",
                        width=2,  # 字符宽度，配合padding使用
                        sticky="se",
                    )

                    # 重新配置信息栏标签样式，确保错误信息颜色正确
                    base_info_label_style = {"font": (font_family, font_size), "relief": "flat"}
                    self.style.configure("Success.TLabel", foreground="#424242", **base_info_label_style)
                    self.style.configure("Error.TLabel", foreground="#c62828", **base_info_label_style)
                    self.style.configure("Info.TLabel", foreground="#424242", **base_info_label_style)

                    # 重新配置信息栏框架样式 - 所有信息栏框架使用相同的基础样式
                    info_bar_frame_style = {"borderwidth": 1, "relief": "solid", "bordercolor": "#F5F5F5"}
                    for frame_style in ["InfoBar.TFrame", "SuccessInfoBar.TFrame", "ErrorInfoBar.TFrame", "InfoInfoBar.TFrame"]:
                        self.style.configure(frame_style, **info_bar_frame_style)
            except (tk.TclError, AttributeError) as e:
                print(f"主题切换出错: {e}")
                # 出错时恢复到默认主题
                self.style.theme_use("vista")

        # 创建应用主题按钮 - 使用原来宽度
        theme_switch_btn = ttk.Button(
            theme_frame, text=_('apply_theme'), width=original_button_width, style=button_style, command=switch_theme
        )
        theme_switch_btn.grid(row=0, column=2, padx=(10, 0), pady=5)

        # 窗口横向锁定控制部分
        lock_frame = ttk.LabelFrame(content_frame, text=_("window_lock"), padding="10")
        lock_frame.grid(row=4, column=0, sticky=tk.EW, pady=(15, 10))

        # 配置锁定框架的列
        lock_frame.grid_columnconfigure(0, weight=1)

        # 窗口横向锁定复选框
        self.width_lock_var = tk.BooleanVar(value=self.width_locked)
        width_lock_cb = ttk.Checkbutton(
            lock_frame,
            text=_('lock_window_width'),
            variable=self.width_lock_var,
            command=self.toggle_width_lock
        )
        width_lock_cb.grid(row=0, column=0, sticky=tk.W, pady=5)

        # 关闭按钮框架
        close_frame = ttk.Frame(content_frame)
        close_frame.grid(row=5, column=0, sticky=tk.EW, pady=(15, 0))
        close_frame.grid_columnconfigure(0, weight=1)  # 左侧空白区域扩展

        # 添加关闭按钮到右下角 - 使用原来宽度
        close_btn = ttk.Button(
            close_frame, text=_('close'), width=original_button_width, style=button_style, command=self.close_test_dialog
        )
        close_btn.grid(row=0, column=1, padx=5)

    def close_test_dialog(self):
        """关闭功能调试对话框并更新状态"""
        if hasattr(self, 'test_dialog') and self.test_dialog is not None:
            try:
                self.test_dialog.destroy()
            finally:
                # 确保无论如何都将test_dialog设置为None
                self.test_dialog = None

    def toggle_width_lock(self):
        """切换窗口横向锁定状态"""
        self.width_locked = self.width_lock_var.get()

        if self.width_locked:
            self.root.resizable(width=False, height=True)
            self.root.minsize(850, 750)
            self.root.maxsize(1100, 10000)
        else:
            self.root.resizable(width=True, height=True)
            self.root.minsize(850, 750)
            self.root.maxsize(10000, 10000)

    def show_result(self, text, error=False, keep_data=False):
        """显示结果

        Args:
            text: 要显示的文本
            error: 是否为错误信息
            keep_data: 是否保留数据
        """
        # 立即取消所有可能的自动隐藏定时器
        if self.info_auto_hide_id:
            self.root.after_cancel(self.info_auto_hide_id)
            self.info_auto_hide_id = None
        
        # 只有在不保留数据且显示错误信息时才清空表格
        if not keep_data and error:
            self.clear_result()

        # 显示在信息栏中
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
        # 使用主窗口宽度的88%作为信息栏宽度，放大截断位置
        info_bar_width = int(main_window_width * 1)
        # 确保不小于原始的最小宽度
        info_bar_width = max(info_bar_width, self.min_info_bar_width)

        # 确保info_bar_frame已经添加到父容器中
        # 使用place布局时winfo_manager()返回"place"，所以用not判断
        if not self.info_bar_frame.winfo_manager():
            # 先临时显示在隐藏位置，避免闪现
            self.info_spacer.pack(side="bottom", fill="x")
            self.info_bar_frame.place(x=10, y=30, width=max(self.info_bar_ref_width, 400), height=30)

        # 更新窗口，确保能获取到准确的宽度
        self.root.update_idletasks()

        # 设置最大像素宽度（考虑信息栏的实际宽度、关闭按钮宽度和内边距）
        # 可用宽度 = 信息栏宽度 - 内边距 - 关闭按钮宽度
        # 增加内边距减去值，确保能显示更多字符
        max_pixel_width = info_bar_width - 60 - self.close_btn_width  # 减去更小的内边距和关闭按钮宽度

        # 确保最大像素宽度为正数
        max_pixel_width = max(max_pixel_width, self.min_pixel_width)

        # 创建字体对象，用于测量文本宽度
        try:
            # 获取当前语言的字体设置
            from style_manager import get_current_font_settings
            font_family, _ = get_current_font_settings()
            font = tkfont.Font(family=font_family, size=10)
        except tk.TclError:
            font = tkfont.Font(family="Arial", size=10)

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

        # 保存完整文本和相关信息到实例变量
        self._full_info_text = text
        self._info_icon = icon
        self._info_label_style = label_style
        self._info_frame_style = frame_style
        self._info_max_pixel_width = max_pixel_width
        self._info_truncated = truncated_text != text
        self._info_currently_expanded = False
        
        # 显示截断文本（带有图标）
        # 使用Text组件的方法设置文本
        self.info_label.configure(state="normal")
        self.info_label.delete(1.0, tk.END)
        self.info_label.insert(tk.END, icon + truncated_text, "justify")
        self.info_label.configure(state="disabled")
        # Text组件不支持style参数，通过直接设置样式属性来实现
        self.info_label.configure(bg="#f0f0f0")  # 设置背景色
        
        # 根据消息类型设置文本颜色
        if error:
            self.info_label.configure(fg="#c62828")  # 错误信息显示红色
        else:
            self.info_label.configure(fg="#424242")  # 正确信息显示灰色
        self.info_bar_frame.configure(style=frame_style)
        
        # 确保点击事件能够正常触发展开/折叠功能
        # 先解绑可能存在的冲突绑定
        self.info_label.unbind("<Button-1>")
        # 重新绑定点击事件
        self.info_label.bind("<Button-1>", self.toggle_info_bar_expand)

        # 显示信息栏 - 使用高度动画实现滑入效果

        if self.info_bar_animating:
            return

        # 显示 spacer，固定高度30px
        self.info_spacer.pack(side="bottom", fill="x", before=self.top_level_notebook)
        self.info_spacer.configure(height=30)
        
        # 强制更新布局
        self.root.update_idletasks()

        # 延迟一下再获取宽度，让布局稳定
        def show_with_width():
            # 计算左边距和宽度
            bar_x = 10
            # 使用主窗口宽度的88%作为信息栏宽度，减去左右边距
            main_width = self.main_frame.winfo_width()
            bar_width = int(main_width * 0.88) - 20

            bar_width = max(bar_width, 100)
            bar_width = min(bar_width, main_width - 20)

            # 先强制更新布局，确保spacer已正确pack
            self.root.update_idletasks()

            # 先将 info_bar_frame 放在隐藏位置（y=30），避免闪现
            self.info_bar_frame.place(x=bar_x, y=30, width=bar_width, height=30)
            self.info_bar_frame.lift()

            # 使用通用动画函数执行显示动画
            self.animate_info_bar('show')

        self.root.after(50, show_with_width)

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
                "type": "split"  # 添加图表类型字段，确保导出PDF时能正确识别
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

    def on_chart_resize(self, event):
        """Canvas尺寸变化时重新绘制图表"""
        # 当Canvas尺寸变化时重新绘制图表
        self.draw_distribution_chart()

    def on_planning_chart_resize(self, event):
        """规划图表尺寸变化时重新绘制"""
        # 检查是否有规划结果数据
        if hasattr(self, 'planning_chart_data') and self.planning_chart_data:
            # 如果有当前图表数据，重新绘制
            draw_distribution_chart(self.planning_chart_canvas, self.planning_chart_data, self.planning_chart_frame, chart_type="plan")
        
    def on_chart_mousewheel(self, event):
        """处理鼠标滚轮事件"""
        self.chart_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_planning_chart_mousewheel(self, event):
        """处理规划图表的鼠标滚轮事件"""
        self.planning_chart_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def draw_text_with_stroke(
        self,
        text,
        x,
        y,
        font,
        anchor=tk.W,
        fill="#ffffff",
        stroke_color="#666666",
        stroke_width=2,
    ):
        """绘制带描边的文字（包装通用函数）"""
        draw_text_with_stroke(
            self.chart_canvas, text, x, y, font,
            anchor=anchor, fill=fill,
            stroke_color=stroke_color, stroke_width=stroke_width
        )

    def draw_distribution_chart(self):
        """绘制网段分布柱状图（包装通用函数）"""
        if hasattr(self, 'chart_data') and self.chart_data:
            draw_distribution_chart(self.chart_canvas, self.chart_data, self.chart_frame)

    def on_window_resize(self, event):
        """窗口大小变化时的处理函数，实现表格和图表自适应"""

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
            # 先准备默认文件名
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 根据数据类型生成默认文件名前缀
            if data_source["main_name"] == _("split_segment_info"):
                # 子网切分结果
                default_file_name = f"{_("subnet_split")}_{timestamp}"
            else:
                # 子网规划结果
                default_file_name = f"{_("subnet_planning")}_{timestamp}"
            
            # 先显示文件选择对话框，不准备数据
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[
                    ("PDF文件", "*.pdf"),
                    ("CSV文件", "*.csv"),
                    ("JSON文件", "*.json"),
                    ("文本文件", "*.txt"),
                    ("Excel文件", "*.xlsx"),
                    ("所有文件", "*.*"),
                ],
                title=title,
                initialdir="",
                initialfile=default_file_name
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

        except (IOError, ValueError, TypeError, PermissionError) as e:
            error_msg = f"{failure_msg.format(error=str(e))}\n堆栈跟踪：{traceback.format_exc()}"
            self.show_result(error_msg, error=True)

    def export_result(self):
        """导出子网切分结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
        data_source = {
            "main_tree": self.split_tree,
            "main_name": _("split_segment_info"),
            "main_filter": lambda values: values[0] not in [_("hint"), _("error"), "-", _("split_segment_info"), _("remaining_segment_info")],
            "main_headers": [_("item"), _("value")],
            "remaining_tree": self.remaining_tree,
            "remaining_name": _("remaining_segment_info"),
            "pdf_title": f"{_("subnet_planner")} - {_("split_result")}",
            "main_table_cols": None,  # 使用默认列宽
            "remaining_table_cols": [40, 80, 80, 100, 90, 80, 50],  # 剩余网段表格列宽
            "chart_data": getattr(self, 'chart_data', None),  # 添加网段分布图数据
        }

        self._export_data(data_source, _("save_subnet_split_result"), _("result_successfully_exported"), _("export_failed"))

    def export_planning_result(self):
        """导出子网规划结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
        data_source = {
            "main_tree": self.allocated_tree,
            "main_name": _("allocated_subnets"),
            "main_filter": None,  # 不需要过滤，直接导出所有数据
            "main_headers": None,  # 自动从表格获取
            "remaining_tree": self.planning_remaining_tree,
            "remaining_name": _("remaining_segment_info"),
            "pdf_title": f"{_("subnet_planner")} - {_("planning_result")}",
            "main_table_cols": [10, 100, 90, 30, 40, 80, 110, 80],  # 已分配子网表格列宽
            "remaining_table_cols": [40, 90, 80, 110, 80, 60],  # 剩余网段表格列宽
            "chart_data": getattr(self, 'planning_chart_data', None),  # 添加网段分布图数据
        }

        self._export_data(data_source, _("save_subnet_planning_result"), _("result_successfully_exported"), _("export_failed"))

    def clear_result(self):
        """清空结果表格和图表"""
        # 清空切分段信息表格
        self.clear_tree_items(self.split_tree)
        # 添加提示行
        self.split_tree.insert("", tk.END, values=(_("hint"), _("click_execute_split_to_start")), tags=('odd',))
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
    
    def one_click_export(self):
        """一键导出功能：自动执行规划和切分，然后导出所有格式的结果"""
        try:
            # 1. 自动执行规划
            self.execute_subnet_planning(from_history=True)
            
            # 2. 自动执行切分
            self.execute_split(from_history=True)
            
            # 3. 让用户选择导出目录
            export_dir = filedialog.askdirectory(title=_("select_export_directory"))
            if not export_dir:
                return
            
            # 4. 导出所有格式的结果
            self.batch_export_all_formats(export_dir)
            
            # 5. 显示成功消息
            self.show_result(_("one_click_export_success").format(dir=export_dir), keep_data=True)
        except Exception as e:
            self.show_result(_("one_click_export_failed").format(error=str(e)), error=True)
    
    def one_click_pdf(self):
        """一键PDF功能：自动执行规划和切分，然后只导出PDF格式的结果"""
        try:
            # 1. 自动执行规划
            self.execute_subnet_planning(from_history=True)
            
            # 2. 自动执行切分
            self.execute_split(from_history=True)
            
            # 3. 让用户选择导出目录
            export_dir = filedialog.askdirectory(title=_("select_export_directory"))
            if not export_dir:
                return
            
            # 4. 只导出PDF格式的结果
            self.batch_export_all_formats(export_dir, formats=['.pdf'])
            
            # 5. 显示成功消息
            self.show_result(_("one_click_pdf_success").format(dir=export_dir), keep_data=True)
        except Exception as e:
            self.show_result(_("one_click_pdf_failed").format(error=str(e)), error=True)
    
    def batch_export_all_formats(self, export_dir, formats=None):
        """批量导出所有支持的格式或指定格式
        
        Args:
            export_dir: 导出目录路径
            formats: 要导出的格式列表，默认为所有支持的格式
        """
        import os
        from datetime import datetime
        
        # 获取当前时间作为文件名前缀
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 支持的导出格式
        default_formats = ['.pdf', '.csv', '.json', '.txt', '.xlsx']
        export_formats = formats if formats is not None else default_formats
        
        # 导出子网切分结果
        for fmt in export_formats:
            # 准备数据
            split_data_source = {
                "main_tree": self.split_tree,
                "main_name": _("split_segment_info"),
                "main_filter": lambda values: values[0] not in [_("hint"), _("error"), "-", _("split_segment_info"), _("remaining_segment_info")],
                "main_headers": [_("item"), _("value")],
                "remaining_tree": self.remaining_tree,
                "remaining_name": _("remaining_segment_info"),
                "pdf_title": f"{_("subnet_planner")} - {_("split_result")}",
                "main_table_cols": None,
                "remaining_table_cols": [40, 80, 80, 100, 90, 80, 50],
                "chart_data": getattr(self, 'chart_data', None),
            }
            
            # 准备文件名 - 使用翻译后的名称
            split_file_name = _("subnet_split")
            split_file_path = os.path.join(export_dir, f"{split_file_name}_{timestamp}{fmt}")
            
            # 导出数据
            self._export_data_to_format(split_file_path, split_data_source)
        
        # 导出子网规划结果
        for fmt in export_formats:
            # 准备数据
            planning_data_source = {
                "main_tree": self.allocated_tree,
                "main_name": _("allocated_subnets"),
                "main_filter": None,
                "main_headers": None,
                "remaining_tree": self.planning_remaining_tree,
                "remaining_name": _("remaining_segment_info"),
                "pdf_title": f"{_("subnet_planner")} - {_("planning_result")}",
                "main_table_cols": [10, 100, 90, 30, 40, 80, 110, 80],
                "remaining_table_cols": [40, 90, 80, 110, 80, 60],
                "chart_data": getattr(self, 'planning_chart_data', None),
            }
            
            # 准备文件名 - 使用翻译后的名称
            planning_file_name = _("subnet_planning")
            planning_file_path = os.path.join(export_dir, f"{planning_file_name}_{timestamp}{fmt}")
            
            # 导出数据
            self._export_data_to_format(planning_file_path, planning_data_source)
    
    def _export_data_to_format(self, file_path, data_source):
        """导出数据到指定格式文件
        
        Args:
            file_path: 导出文件路径
            data_source: 数据源字典
        """
        try:
            # 准备数据
            success, message, data = self.export_utils.export_data(data_source, "", "", "")
            if not success:
                raise Exception(message)
            
            main_data, main_headers, remaining_data, remaining_headers = data
            
            # 使用导出工具导出到文件
            success, message = self.export_utils.export_to_file(
                file_path, data_source, main_data, main_headers, remaining_data, remaining_headers
            )
            
            if not success:
                raise Exception(message)
        except Exception as e:
            # 记录错误但继续导出其他格式
            print(f"导出失败 {file_path}: {e}")

    def create_about_link(self):
        """在主窗体标题栏右侧（红框位置）创建关于链接按钮和钉住按钮"""
        # 直接在root窗口创建关于链接，不使用框架
        # 使用普通tk.Label直接控制样式，确保悬停效果可靠

        # 获取窗口背景色以确保完全一致
        self.bg_color = self.root.cget("background")
        self.hover_bg_color = "#e0e0e0"  # 更浅的灰色背景，柔和过渡
        self.hover_fg_color = "#333333"  # 深灰色文字，保持可读性
        self.normal_fg_color = "#666666"
        # 使用系统默认控件边框颜色，与ttk.Combobox边框颜色一致
        border_color = "#a9a9a9"  # 系统默认灰色边框，与ttk.Combobox一致

        # 初始化窗口置顶状态
        self.is_pinned = False

        # 创建语言选择下拉菜单
        self.language_var = tk.StringVar()
        # 设置当前语言
        current_lang = get_language()
        if current_lang == "zh":
            self.language_var.set("简体中文")
        elif current_lang == "zh_tw":
            self.language_var.set("繁體中文")
        elif current_lang == "en":
            self.language_var.set("English")
        elif current_lang == "ja":
            self.language_var.set("日本語")
        elif current_lang == "ko":
            self.language_var.set("한국어")
        
        # 使用ttk.Combobox创建语言选择控件
        self.language_combobox = ttk.Combobox(
            self.root,
            textvariable=self.language_var,
            values=["简体中文", "繁體中文", "English", "日本語", "한국어"],
            state="readonly",
            width=14
        )
        
        # 绑定语言切换事件
        self.language_combobox.bind("<<ComboboxSelected>>", self.on_language_change)

        # 使用普通tk.Label创建关于标签，直接设置所有样式属性，高度与信息框一致
        # 获取当前字体设置
        from style_manager import get_current_font_settings
        font_family, font_size = get_current_font_settings()
        
        self.about_label = tk.Label(
            self.root,
            text=_('about') + '…',
            font=(font_family, font_size, 'bold'),  # 使用统一的字体设置，加粗
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
        # 使用固定像素尺寸，确保高度和宽度设置起作用
        self.about_label.place(
            relx=1.0, rely=0.0, anchor=tk.NE, 
            x=-25, y=22, 
            width=88,   # 固定宽度80px，足够显示各种语言的"关于"文本
            height=26   # 固定高度26px，与钉住按钮高度一致
        )  # y=22，向下移动1px，与信息栏顶部对齐
        self.about_label.bind("<Button-1>", lambda e: self.show_about_dialog())

        # 绑定鼠标事件实现悬停效果
        self.about_label.bind("<Enter>", self.on_about_link_enter)
        self.about_label.bind("<Leave>", self.on_about_link_leave)

        # 创建钉住按钮，使用扁平化风格，直接添加到root窗口，高度与信息框一致
        self.pin_label = tk.Label(
            self.root,
            text="📌",
            font=(font_family, font_size, 'bold'),  # 使用统一的字体设置，加粗
            fg=self.normal_fg_color,  # 文字颜色调淡为浅灰色
            bg=self.bg_color,  # 背景色与窗口完全一致
            padx=4.4,  # 适当的水平内边距
            pady=4.4,  # 适当的垂直内边距
            bd=0,  # 无边框，扁平化风格
            relief="flat",  # 平坦样式，扁平化风格
            highlightthickness=1,  # 高亮边框宽度，模拟边框
            highlightbackground=border_color,  # 边框颜色
            highlightcolor=border_color,  # 边框颜色（确保一致性）
            cursor="hand2",  # 鼠标指针为手形
        )
        self.pin_label.bind("<Button-1>", lambda e: self.toggle_pin_window())

        self.pin_label.bind("<Enter>", self.on_about_link_enter)
        self.pin_label.bind("<Leave>", self.on_about_link_leave)
        
        # 动态计算并放置钉住按钮在关于按钮左侧，紧靠着关于按钮
        self.root.update_idletasks()  # 更新界面以获取准确的组件尺寸
        about_width = self.about_label.winfo_width()  # 获取关于按钮的实际宽度
        pin_x = -25 - about_width - 5  # 计算钉住按钮的x坐标：关于按钮x坐标 - 关于按钮宽度 - 5px间距
        # 使用固定像素尺寸，确保显示为1:1比例
        self.pin_label.place(
            relx=1.0, rely=0.0, anchor=tk.NE, 
            x=pin_x, y=22, 
            width=28,  # 固定宽度28px
            height=26   # 固定高度26px，确保1:1比例
        )  # 动态放置在关于按钮左侧，紧靠着关于按钮
        
        # 动态计算并放置语言选择框在钉住按钮左侧，紧靠着钉住按钮
        self.root.update_idletasks()  # 更新界面以获取准确的组件尺寸
        pin_width = self.pin_label.winfo_width()  # 获取钉住按钮的实际宽度
        combobox_x = pin_x - pin_width - 5  # 计算语言选择框的x坐标：钉住按钮x坐标 - 钉住按钮宽度 - 5px间距
        # 设置固定高度，与其他两个按钮保持一致，并调整y坐标使其垂直对齐
        self.language_combobox.place(
            relx=1.0, rely=0.0, anchor=tk.NE, 
            x=combobox_x, 
            y=22,  # 调整y坐标为22，与其他两个按钮垂直对齐
            height=26  # 设置固定高度26px，与其他两个按钮保持一致
        )  # 动态放置在钉住按钮左侧，紧靠着钉住按钮，垂直对齐

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
    
    def on_language_change(self, event):
        """语言选择变化时的处理函数"""
        selected_language = self.language_var.get()
        if selected_language == "简体中文":
            lang_code = "zh"
        elif selected_language == "繁體中文":
            lang_code = "zh_tw"
        elif selected_language == "English":
            lang_code = "en"
        elif selected_language == "日本語":
            lang_code = "ja"
        else:  # 한국어
            lang_code = "ko"
        
        # 设置当前语言
        set_language(lang_code)
        
        # 更新应用程序名称
        self.app_name = _("app_name")
        self.root.title(f"{self.app_name} v{self.app_version}")
        
        # 更新样式，确保新创建的UI元素使用正确的样式
        from style_manager import update_styles
        update_styles()
        
        # 重新创建所有UI元素，实现语言更新
        self.destroy_all_widgets()
        self.recreate_ui()
    
    def destroy_all_widgets(self):
        """销毁所有子组件"""
        # 关闭功能调试面板，如果它是打开的
        if hasattr(self, 'test_dialog') and self.test_dialog is not None:
            self.test_dialog.destroy()
            self.test_dialog = None
        
        # 销毁主框架，如果存在的话
        if hasattr(self, 'main_frame'):
            self.main_frame.destroy()
        
        # 销毁右上角的控件
        if hasattr(self, 'about_label'):
            self.about_label.destroy()
        if hasattr(self, 'pin_label'):
            self.pin_label.destroy()
        if hasattr(self, 'language_combobox'):
            self.language_combobox.destroy()
        
        # 销毁信息栏相关控件
        if hasattr(self, 'info_spacer'):
            self.info_spacer.destroy()
        if hasattr(self, 'info_bar_frame'):
            self.info_bar_frame.destroy()
        if hasattr(self, 'info_close_btn'):
            self.info_close_btn.destroy()
        if hasattr(self, 'info_label'):
            self.info_label.destroy()
    
    def recreate_ui(self):
        """重新创建UI元素"""
        # 重新初始化所有必要的组件属性
        self.initialize_component_properties()
        
        # 获取当前字体设置
        font_family, font_size = get_current_font_settings()
        
        # 重新创建主框架
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 重新创建信息栏 spacer
        self.info_spacer = ttk.Frame(self.main_frame, style="Placeholder.TFrame")
        self.info_spacer.pack(side="bottom", fill="x")
        self.info_spacer.pack_forget()
        self.info_spacer.configure(height=30)
        
        # 重新创建信息栏框架
        self.info_bar_frame = ttk.Frame(self.info_spacer, style="InfoBar.TFrame")
        self.info_bar_frame.place_forget()
        
        # 重新创建顶级标签页控件
        self.create_top_level_notebook()
        
        # 重新创建右上角的关于链接按钮和钉住按钮
        self.create_about_link()
        
        self.info_bar_frame.grid_rowconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(0, weight=1)
        self.info_bar_frame.grid_columnconfigure(1, weight=0)
        
        # 重新创建信息栏关闭按钮
        self.info_close_btn = ttk.Button(
            self.info_bar_frame,
            text="✕",
            command=self.hide_info_bar,
            style="InfoBarCloseButton.TButton",
            cursor="hand2",
        )
        self.info_close_btn.grid(row=0, column=1, padx=(0, 3), pady=1, sticky="se")
        
        # 重新创建信息标签（使用Text组件替代Label，以支持更灵活的文本布局）
        self.info_label = tk.Text(
            self.info_bar_frame, wrap="none", padx=3, pady=2, height=1,
            borderwidth=0, relief="flat", state="disabled",
            font=(font_family, font_size),
            takefocus=False,  # 不接受焦点
            cursor="arrow",  # 显示普通箭头光标
            selectbackground="#f0f0f0",  # 选中背景与组件背景相同
            selectforeground="#000000",  # 选中前景与普通文本相同
            insertbackground="#f0f0f0",  # 插入光标颜色与背景相同
            highlightthickness=0  # 移除焦点高亮边框
        )
        # 设置左对齐
        self.info_label.tag_configure("justify", justify="left")
        self.info_label.grid(row=0, column=0, sticky="ew", padx=(0, 0), pady=0)
        self.info_label.lift(self.info_close_btn)
        # 禁用文本选择，但保留点击事件以支持展开/折叠
        self.info_label.bind("<Double-1>", lambda e: "break")
        self.info_label.bind("<Triple-1>", lambda e: "break")
        self.info_label.bind("<B1-Motion>", lambda e: "break")
        self.info_label.bind("<Control-a>", lambda e: "break")
        
        # 重新初始化图表数据
        self.chart_data = None
        
        # 重新初始化历史记录
        self.history_records = []
        
        self.root.update_idletasks()
        self.info_bar_ref_width = max(self.main_frame.winfo_width() - 20, 100)
    
    def initialize_component_properties(self):
        """重新初始化所有必要的组件属性"""
        self.planning_parent_networks = []
        self.planning_parent_entry = None
        self.pool_tree = None
        self.pool_scrollbar = None
        self.requirements_tree = None
        self.requirements_scrollbar = None
        
        # 重新初始化export_utils，确保使用当前语言的字体
        from export_utils import ExportUtils
        self.export_utils = ExportUtils()
        
        self.test_dialog = None  # 用于存储调试面板的引用，确保只能打开一个
        self.undo_delete_btn = None
        self.swap_btn = None
        self.planning_notebook = None
        self.execute_planning_btn = None
        self.allocated_frame = None
        self.allocated_tree = None
        self.planning_remaining_frame = None
        self.planning_remaining_tree = None
        
        self.edit_entry = None
        self.current_edit_item = None
        self.current_edit_column = None
        self.current_edit_column_index = None
        self.current_edit_tree = None
        
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
    
    def on_window_configure(self, event):
        """窗口大小变化时动态调整右上角按钮位置"""
        # 窗口大小变化时重新获取窗口背景色，确保按钮背景色与窗口一致
        self.bg_color = self.root.cget("background")
        
        # 更新按钮背景色，先检查控件是否存在
        if hasattr(self, 'about_label') and self.about_label.winfo_exists():
            self.about_label.config(bg=self.bg_color)
        if hasattr(self, 'pin_label') and self.pin_label.winfo_exists():
            if not self.is_pinned:
                # Check if normal_fg_color is set before accessing it
                if hasattr(self, 'normal_fg_color'):
                    self.pin_label.config(bg=self.bg_color)
                else:
                    # If normal_fg_color isn't set yet, just update the background
                    self.pin_label.config(bg=self.bg_color)
        
        # 这里不需要调整按钮位置，因为按钮使用了相对定位（relx=1.0）
        # 窗口大小变化时，按钮会自动保持在右上角位置
    
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
        about_window.title(f"{_("about")} {self.app_name}")
        about_window.resizable(False, False)
        about_window.configure(bg="#ffffff")  # 设置背景色为白色

        # 确保对话框在主窗口之上
        about_window.transient(self.root)
        about_window.grab_set()

        about_window.withdraw()

        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()

        # 设置对话框尺寸，适当增大以容纳更丰富的内容，确保所有语言下都能完整显示
        dialog_width = 400
        dialog_height = 300

        # 计算对话框在主窗口中心的位置
        dialog_x = main_x + (main_width // 2) - (dialog_width // 2)
        dialog_y = main_y + (main_height // 2) - (dialog_height // 2)

        about_window.geometry(f"{dialog_width}x{dialog_height}+{dialog_x}+{dialog_y}")

        about_window.deiconify()

        # 创建内容框架，移除所有边框和焦点指示
        content_frame = ttk.Frame(about_window, padding=(20, 20, 20, 15), relief="flat", borderwidth=0)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 创建内部框架放置实际内容，不使用占位符框架
        inner_frame = ttk.Frame(content_frame)
        inner_frame.pack(side="top", fill="both", expand=True)
        inner_frame.configure(style="About.TFrame")

        # 移除可能影响焦点的事件绑定
        about_window.unbind("<FocusIn>")
        about_window.unbind("<FocusOut>")

        # 为关于对话框中的标签和按钮添加焦点样式，移除虚线
        # 创建对话框专用的样式，避免影响主窗口
        # 只在样式未配置时才配置，避免重复配置
        try:
            self.style.configure("About.TLabel", focuscolor="none")
            self.style.configure("About.TButton",
                               focuscolor="none",
                               focuswidth=0,
                               padding=(10, 5))
            self.style.map("About.TButton",
                          focuscolor=[("focus", "none")],
                          focuswidth=[("focus", 0)])
        except tk.TclError:
            pass  # 样式已配置或配置失败，忽略错误

        # 获取当前字体设置，确保与应用程序其他部分一致
        from style_manager import get_current_font_settings
        font_family, __ = get_current_font_settings()
        
        # 标题区域
        title_frame = ttk.Frame(inner_frame)
        title_frame.pack(pady=(10, 8))

        # 添加应用名称作为主要标题，使用蓝色主题色
        app_name_label = ttk.Label(title_frame, 
                                 text=self.app_name, 
                                 font=(font_family, 18, "bold"), 
                                 style="About.TLabel",
                                 foreground="#1976d2")
        app_name_label.pack(anchor=tk.CENTER)

        # 添加版本号，使用灰色调
        version_label = ttk.Label(
            title_frame, 
            text=f"{_("version")} {self.app_version}", 
            font=(font_family, 11, "bold"), 
            style="About.TLabel",
            foreground="#666666"
        )
        version_label.pack(anchor=tk.CENTER, pady=(5, 0))

        # 添加分隔线，增强视觉层次
        separator = ttk.Separator(title_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(5, 0))

        # 添加应用描述，使用翻译函数确保多语言适配
        desc_label = ttk.Label(
            title_frame, 
            text=_("app_description"), 
            font=(font_family, 11), 
            style="About.TLabel",
            foreground="#555555"
        )
        desc_label.pack(anchor=tk.CENTER, pady=(5, 0))

        # 信息区域
        info_frame = ttk.Frame(inner_frame)
        info_frame.pack(pady=(10, 5))
        
        # 添加作者信息
        # 使用ttk.Label与其他标签保持一致
        author_label = ttk.Label(
            info_frame, 
            text=f"{_("author")}：Ejones", 
            font=(font_family, 10), 
            style="About.TLabel",
            foreground="#444444"
        )
        author_label.pack(anchor=tk.CENTER, pady=(2, 0))

        # 添加联系方式，使用蓝色调，可点击复制
        # 使用ttk.Label与其他标签保持一致
        email_label = ttk.Label(
            info_frame, 
            text=f"{_("email")}：ejones.cn@hotmail.com", 
            font=(font_family, 10), 
            style="About.TLabel",
            foreground="#1976d2",
            cursor="hand2"
        )
        email_label.pack(anchor=tk.CENTER, pady=(0, 0))
        
        # 为邮箱添加点击事件，启动邮件客户端
        import webbrowser

        def open_email_client():
            webbrowser.open("mailto:ejones.cn@hotmail.com")
        email_label.bind("<Button-1>", lambda e: open_email_client())

        # 直接在内容框架中添加确定按钮和版权信息，不使用额外的底部框架
        # 添加确定按钮，使用更大的宽度和更好的居中效果
        ok_button = ttk.Button(inner_frame, 
                             text=_("ok"), 
                             command=about_window.destroy, 
                             width=10,
                             style="About.TButton")
        ok_button.pack(anchor=tk.CENTER, pady=(2, 1))

        # 将焦点聚焦到确定按钮上，使用更可靠的方式
        about_window.after_idle(ok_button.focus_set)
        about_window.after_idle(ok_button.focus_force)

        # 绑定回车键事件，确保按回车键能关闭对话框
        about_window.bind('<Return>', lambda e: ok_button.invoke())
        about_window.bind('<Escape>', lambda e: ok_button.invoke())

        # 添加版权信息，使用动态字体设置，灰色调
        copyright_label = ttk.Label(
            inner_frame, 
            text=_("copyright").format(app_name=self.app_name), 
            font=(font_family, 8),  # 使用动态字体，保持9号大小
            style="About.TLabel",
            foreground="#888888"
        )
        copyright_label.pack(anchor=tk.CENTER, pady=(5, 10))




if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    
    # 获取DPI缩放因子（如果未定义则默认为1.0）
    # 全局变量已在文件开头定义，无需再次声明
    try:
        pass  # SCALE_FACTOR已在文件开头定义
    except NameError:
        SCALE_FACTOR = 1.0
    
    # 设置窗口初始大小 - 根据DPI缩放因子调整
    BASE_WIDTH = 850
    BASE_HEIGHT = 750
    
    # 使用原始窗口大小，不进行额外缩放
    WINDOW_WIDTH = int(BASE_WIDTH)
    WINDOW_HEIGHT = int(BASE_HEIGHT)
    
    print(f"📏 窗口尺寸: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口居中的坐标
    window_x = (screen_width - WINDOW_WIDTH) // 2
    window_y = (screen_height - WINDOW_HEIGHT) // 2

    # 设置窗口大小和位置
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{window_x}+{window_y}")

    # 设置窗口固定宽度，高度可调整
    root.minsize(BASE_WIDTH, BASE_HEIGHT)
    root.maxsize(10000, 10000)  # 设置最大宽度为1100，最大高度设为一个很大的值

    # 只允许调整窗口高度，不允许调整宽度
    root.resizable(width=False, height=True)
    # 创建应用实例并运行
    IPSubnetSplitterApp(root)
    root.mainloop()
