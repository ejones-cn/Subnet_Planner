#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子网规划师应用程序 - 主窗口 (高清版本)
支持高清显示器自适应缩放
"""

# 所有导入语句放在最顶部
import tkinter as tk
import datetime
import re
from tkinter import ttk, filedialog
import tkinter.font as tkfont
import sys
import os
import traceback
import csv
import ipaddress
import base64
from io import BytesIO
from PIL import Image, ImageTk
from openpyxl import Workbook, load_workbook  # type: ignore
from openpyxl.styles import Font, Alignment  # type: ignore

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
    handle_ip_subnet_error,
)

# 导出工具模块
from export_utils import ExportUtils

# 图表工具模块
from chart_utils import draw_text_with_stroke, draw_distribution_chart

# 版本管理模块
from version import get_version

# 导入Base64编码的图标
from icon_base64 import APP_ICON_BASE64

# 全局变量定义 - 增强版DPI缩放因子
SCALE_FACTOR = 1.0  # DPI缩放因子，默认1.0（96 DPI）
BASE_DPI = 96       # 标准DPI值
MAX_SCALE_FACTOR = 3.0  # 最大缩放限制，防止过度缩放
MIN_SCALE_FACTOR = 0.5  # 最小缩放限制，防止过小缩放


def load_icon():
    """
    从Base64编码加载图标

    Returns:
        ImageTk.PhotoImage对象
    """
    try:
        icon_data = base64.b64decode(APP_ICON_BASE64)
        icon_stream = BytesIO(icon_data)
        icon = Image.open(icon_stream)
        return ImageTk.PhotoImage(icon)
    except Exception as e:
        print(f"加载图标失败: {e}")
        return None


def get_scaled_value(value, scale_factor=None):
    """
    根据缩放因子缩放值

    Args:
        value: 要缩放的值（整数）
        scale_factor: 缩放因子，如果未提供则使用全局SCALE_FACTOR

    Returns:
        缩放后的整数值
    """
    if scale_factor is None:
        scale_factor = SCALE_FACTOR
    
    # 确保缩放因子在合理范围内
    scale_factor = max(MIN_SCALE_FACTOR, min(MAX_SCALE_FACTOR, scale_factor))
    
    # 返回四舍五入的整数
    return max(1, int(value * scale_factor))


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
        
        # 计算缩放因子，并限制在合理范围内
        SCALE_FACTOR = dpi_x / BASE_DPI
        SCALE_FACTOR = max(MIN_SCALE_FACTOR, min(MAX_SCALE_FACTOR, SCALE_FACTOR))
        print(f"✅ Windows DPI设置: {dpi_x}x{dpi_y} DPI, 缩放因子: {SCALE_FACTOR:.2f}, 模式: {DPI_MODE}")
        
    except Exception as e:
        print(f"⚠️ 设置DPI感知失败: {e}")
        # 定义默认缩放因子
        SCALE_FACTOR = 1.0


# 自定义的ColoredNotebook类，支持每个标签不同颜色和高清缩放
class ColoredNotebook(ttk.Frame):
    """自定义的ColoredNotebook组件，用于显示带有颜色的标签页
    支持高清显示器自适应缩放

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
        
        # 应用高清缩放
        self.apply_dpi_scaling()
    
    def apply_dpi_scaling(self):
        """应用DPI缩放因子到标签页样式"""
        # 缩放标签页内边距
        tab_padding = (get_scaled_value(15), get_scaled_value(6))
        
        # 设置Notebook的基本样式
        self.style.configure("TNotebook", background="#ffffff")

        # 使用默认边框样式，移除深灰色边框
        self.style.configure("TLabelframe")
        
        # 增大LabelFrame标题的字体大小
        self.style.configure(
            "TLabelframe.Label", 
            borderwidth=0, 
            relief="flat", 
            font=("微软雅黑", get_scaled_value(12))
        )


class IPSubnetSplitterApp:
    """子网规划师主应用程序类（高清版本）

    这个类实现了一个子网规划的GUI应用程序，支持高清显示器自适应缩放，
    支持子网分割、子网规划、IP信息查询等功能。
    
    高清版本新增功能：
    - DPI感知和自适应缩放
    - 基于缩放因子的UI元素动态调整
    - 高分辨率显示器优化显示
    """
    def __init__(self, main_window):
        # 应用程序信息
        self.app_name = "子网规划师（高清版）"
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

        # 图表相关属性（预声明，避免Attribute-defined-outside-init警告）
        self.chart_canvas = None
        self.chart_image = None
        self.distribution_image = None

        # 主窗口引用
        self.root = main_window

        # 初始化ttk样式
        self.style = ttk.Style()
        
        # 应用DPI缩放设置
        self.apply_dpi_scaling()

        # 初始化应用程序
        self.init_ui()

    def apply_dpi_scaling(self):
        """应用DPI缩放因子到整个应用程序"""
        print(f"🔍 高清版本应用DPI缩放: {SCALE_FACTOR:.2f}")
        
        # 根据缩放因子调整默认字体大小
        base_font_size = max(8, int(9 * SCALE_FACTOR))
        self.base_font = ("微软雅黑", base_font_size)
        self.small_font = ("微软雅黑", max(7, int(8 * SCALE_FACTOR)))
        self.large_font = ("微软雅黑", max(10, int(12 * SCALE_FACTOR)))
        self.title_font = ("微软雅黑", max(12, int(14 * SCALE_FACTOR)), "bold")

        # 缩放基础尺寸
        self.base_padding = get_scaled_value(10)
        self.small_padding = get_scaled_value(5)
        self.large_padding = get_scaled_value(15)
        self.border_width = get_scaled_value(1)
        
        # 计算窗口尺寸
        window_width = get_scaled_value(1200)
        window_height = get_scaled_value(800)
        
        # 设置窗口最小尺寸
        self.root.minsize(window_width, window_height)
        
        # 设置窗口初始大小和居中显示
        self.root.geometry(f"{window_width}x{window_height}")
        self.center_window()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题
        self.root.title(f"子网规划师 v{self.app_version}")

        # 设置样式
        self.style = ttk.Style()

        # 使用默认主题
        self.style.theme_use("vista")

        # 统一设置基本控件的字体样式，使用缩放后的字体
        self.style.configure("TLabel", font=self.base_font)
        self.style.configure("TEntry", font=self.base_font)
        # 按钮除了基本字体外还有额外的样式配置
        self.style.configure("TButton", font=self.base_font, focuscolor="#888888", focuswidth=get_scaled_value(1))

        # 设置滚动条宽度一致 - 针对Windows平台的特殊处理
        # 恢复默认滚动条布局，包含完整的箭头元素
        # 当滚动条未激活时，通过回调函数隐藏整个滚动条
        scrollbar_width = get_scaled_value(5)
        for scrollbar_type in ["TScrollbar", "Vertical.TScrollbar", "Horizontal.TScrollbar"]:
            self.style.configure(scrollbar_type, width=scrollbar_width)

        # 为按钮添加焦点样式映射，进一步控制焦点效果
        self.style.map(
            "TButton",
            focuscolor=[("focus", "#888888"), ("!focus", "#888888")],
        )

        # 设置主应用容器
        main_container = ttk.Frame(self.root, padding=self.base_padding)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 创建主标签页容器
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(self.small_padding, 0))

        # 创建菜单栏
        self.create_menu_bar(main_container)

        # 创建各个标签页
        self.create_main_tabs()

        # 设置应用程序图标
        self.setup_app_icon()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def apply_dpi_scaling(self):
        """应用DPI缩放因子到整个应用程序"""
        print(f"🔍 高清版本应用DPI缩放: {SCALE_FACTOR:.2f}")
        
        # 根据缩放因子调整默认字体大小
        base_font_size = max(8, int(9 * SCALE_FACTOR))
        self.base_font = ("微软雅黑", base_font_size)
        self.small_font = ("微软雅黑", max(7, int(8 * SCALE_FACTOR)))
        self.large_font = ("微软雅黑", max(10, int(12 * SCALE_FACTOR)))
        self.title_font = ("微软雅黑", max(12, int(14 * SCALE_FACTOR)), "bold")

        # 缩放基础尺寸
        self.base_padding = get_scaled_value(10)
        self.small_padding = get_scaled_value(5)
        self.large_padding = get_scaled_value(15)
        self.border_width = get_scaled_value(1)
        
        # 计算窗口尺寸
        window_width = get_scaled_value(1200)
        window_height = get_scaled_value(800)
        
        # 设置窗口最小尺寸
        self.root.minsize(window_width, window_height)
        
        # 设置窗口初始大小和居中显示
        self.root.geometry(f"{window_width}x{window_height}")
        self.center_window()

    def center_window(self):
        """将窗口居中显示在屏幕上"""
        self.root.update_idletasks()
        
        # 获取窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"+{x}+{y}")

    def init_ui(self):
        """初始化用户界面"""
        # 创建主容器框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=self.base_padding, pady=self.base_padding)

        # 创建样式配置
        self.setup_styles()

        # 创建菜单栏
        self.create_menu_bar(main_frame)

        # 创建标签页容器
        self.create_notebook(main_frame)

    def setup_styles(self):
        """配置应用程序样式"""
        # 设置ttk样式
        self.style.theme_use('clam')
        
        # 配置Treeview样式
        self.style.configure("Treeview", 
                           font=self.base_font,
                           rowheight=get_scaled_value(22),
                           borderwidth=get_scaled_value(1))
        self.style.configure("Treeview.Heading", 
                           font=self.title_font,
                           borderwidth=get_scaled_value(1),
                           relief="raised")
        
        # 配置按钮样式
        self.style.configure("TButton", 
                           font=self.base_font,
                           padding=(self.base_padding, self.small_padding),
                           borderwidth=get_scaled_value(1))
        
        # 配置标签样式
        self.style.configure("TLabel", 
                           font=self.base_font)
        
        # 配置Entry样式
        self.style.configure("TEntry", 
                           font=self.base_font,
                           padding=(self.small_padding, self.small_padding),
                           borderwidth=get_scaled_value(1))
        
        # 配置LabelFrame样式
        self.style.configure("TLabelframe",
                           font=self.base_font,
                           borderwidth=get_scaled_value(1),
                           relief="groove")
        self.style.configure("TLabelframe.Label",
                           font=self.title_font,
                           borderwidth=0)
        
        # 配置滚动条样式
        self.style.configure("TScrollbar",
                           width=get_scaled_value(12),
                           arrowsize=get_scaled_value(12))
        
        # 配置框架样式
        self.style.configure("TFrame",
                           borderwidth=0)
        
        # 配置Radiobutton样式
        self.style.configure("TRadiobutton",
                           font=self.base_font)
        
        # 配置Checkbutton样式
        self.style.configure("TCheckbutton",
                           font=self.base_font)
        
        # 配置Scale样式
        self.style.configure("TScale",
                           font=self.base_font)
        
        # 配置Spinbox样式
        self.style.configure("TSpinbox",
                           font=self.base_font,
                           arrowsize=get_scaled_value(12))
        
        # 配置Menu样式
        self.style.configure("TMenu",
                           font=self.small_font)

    def create_menu_bar(self, parent):
        """创建菜单栏"""
        # 暂时使用基本的ttk.Frame，因为菜单栏功能比较复杂
        menu_frame = ttk.Frame(parent)
        menu_frame.pack(fill=tk.X, pady=(0, self.base_padding))

        # 创建简单的菜单按钮
        menu_button = ttk.Button(menu_frame, text="文件(F)")
        menu_button.pack(side=tk.LEFT, padx=(0, self.small_padding))

        edit_button = ttk.Button(menu_frame, text="编辑(E)")
        edit_button.pack(side=tk.LEFT, padx=(0, self.small_padding))

        tools_button = ttk.Button(menu_frame, text="工具(T)")
        tools_button.pack(side=tk.LEFT, padx=(0, self.small_padding))

        help_button = ttk.Button(menu_frame, text="帮助(H)")
        help_button.pack(side=tk.LEFT)

    def create_main_tabs(self):
        """创建主标签页"""
        # 创建子网规划标签页
        planning_frame = ttk.Frame(self.notebook, padding=self.base_padding)
        self.notebook.add(planning_frame, text="子网规划")
        self.setup_planning_tab(planning_frame)

        # 创建子网切分标签页
        split_frame = ttk.Frame(self.notebook, padding=self.base_padding)
        self.notebook.add(split_frame, text="子网切分")
        self.setup_split_tab(split_frame)

        # 创建高级工具标签页
        advanced_frame = ttk.Frame(self.notebook, padding=self.base_padding)
        self.notebook.add(advanced_frame, text="高级工具")
        self.setup_advanced_tab(advanced_frame)

    def setup_planning_tab(self, parent):
        """设置子网规划标签页"""
        # 标题
        title_label = ttk.Label(parent, text="子网规划工具", font=self.title_font)
        title_label.pack(pady=(0, self.large_padding))

        # 输入区域
        input_frame = ttk.LabelFrame(parent, text="规划设置", padding=self.base_padding)
        input_frame.pack(fill=tk.X, pady=(0, self.base_padding))

        # CIDR网络输入
        cidr_frame = ttk.Frame(input_frame)
        cidr_frame.pack(fill=tk.X, pady=self.small_padding)

        ttk.Label(cidr_frame, text="网络地址:", font=self.base_font).pack(side=tk.LEFT)
        self.planning_cidr_entry = ttk.Entry(cidr_frame, font=self.base_font, width=get_scaled_value(20))
        self.planning_cidr_entry.pack(side=tk.LEFT, padx=(self.small_padding, 0))

        # 子网数量输入
        subnet_count_frame = ttk.Frame(input_frame)
        subnet_count_frame.pack(fill=tk.X, pady=self.small_padding)

        ttk.Label(subnet_count_frame, text="子网数量:", font=self.base_font).pack(side=tk.LEFT)
        self.subnet_count_entry = ttk.Entry(subnet_count_frame, font=self.base_font, width=get_scaled_value(10))
        self.subnet_count_entry.pack(side=tk.LEFT, padx=(self.small_padding, 0))

        # 规划按钮
        plan_button = ttk.Button(input_frame, text="开始规划", command=self.start_planning)
        plan_button.pack(pady=(self.base_padding, 0))

        # 结果显示区域
        result_frame = ttk.LabelFrame(parent, text="规划结果", padding=self.base_padding)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # 创建结果表格
        columns = ("网络地址", "子网掩码", "可用地址", "网络范围")
        self.planning_tree = ttk.Treeview(result_frame, columns=columns, show="headings", font=self.base_font)

        # 设置列标题和宽度
        for col in columns:
            self.planning_tree.heading(col, text=col, font=self.title_font)
            self.planning_tree.column(col, width=get_scaled_value(150), anchor=tk.CENTER)

        # 添加滚动条
        planning_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.planning_tree.yview)
        self.planning_tree.configure(yscrollcommand=planning_scrollbar.set)

        # 布局表格和滚动条
        self.planning_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        planning_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_split_tab(self, parent):
        """设置子网切分标签页"""
        # 设置网格布局
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=0)
        parent.grid_rowconfigure(1, weight=1)

        # 左侧：输入参数面板
        input_frame = ttk.LabelFrame(parent, text="输入参数", padding=self.base_padding)
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, get_scaled_value(5)))
        
        # 右侧：历史记录面板
        history_frame = ttk.LabelFrame(parent, text="历史记录", padding=self.base_padding)
        history_frame.grid(row=0, column=1, sticky="nsew", padx=(get_scaled_value(5), 0))

        # 配置 input_frame 的 grid 行列
        input_frame.grid_columnconfigure(0, minsize=get_scaled_value(30), weight=0)
        input_frame.grid_columnconfigure(1, minsize=0, weight=1)
        input_frame.grid_columnconfigure(2, weight=0)
        input_frame.grid_rowconfigure(0, weight=0, minsize=0)
        input_frame.grid_rowconfigure(1, weight=0)
        input_frame.grid_rowconfigure(2, weight=0)
        input_frame.grid_rowconfigure(3, weight=0, minsize=0)

        # 父网段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text="父网段", anchor="w", font=self.base_font).grid(
            row=1, column=0, sticky=tk.W + tk.N + tk.S, pady=self.small_padding, padx=(self.base_padding, 0)
        )
        
        # 初始化子网切分的历史记录列表
        self.split_parent_networks = ["10.0.0.0/8"]  # 子网切分的父网段历史记录
        self.split_networks = ["10.21.60.0/23"]  # 子网切分的切分段历史记录

        # 父网段 - 使用Combobox，支持下拉选择和即时验证
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, self.parent_entry)), '%P')
        self.parent_entry = ttk.Combobox(
            input_frame,
            values=self.split_parent_networks,
            font=self.base_font,
            validate='all',
            validatecommand=vcmd,
        )
        self.parent_entry.grid(row=1, column=1, padx=get_scaled_value(10), pady=self.small_padding, sticky=tk.EW + tk.N + tk.S)
        self.parent_entry.insert(0, "10.0.0.0/8")  # 默认值
        self.parent_entry.config(state="normal")  # 允许手动输入

        # 切分段 - 统一pady、sticky和字体，确保与文本框垂直对齐
        ttk.Label(input_frame, text="切分段", anchor="w", font=self.base_font).grid(
            row=2, column=0, sticky=tk.W + tk.N + tk.S, pady=self.small_padding, padx=(self.base_padding, 0)
        )
        vcmd = (self.root.register(lambda text: self.validate_cidr(text, self.split_entry)), '%P')
        self.split_entry = ttk.Combobox(
            input_frame,
            values=self.split_networks,
            font=self.base_font,
            validate='all',
            validatecommand=vcmd,
        )
        self.split_entry.grid(row=2, column=1, padx=get_scaled_value(10), pady=self.small_padding, sticky=tk.EW + tk.N + tk.S)
        self.split_entry.insert(0, "10.21.60.0/23")  # 默认值
        self.split_entry.config(state="normal")  # 允许手动输入

        # 执行按钮 - 跨四行的方形样式，使用grid布局
        self.execute_btn = ttk.Button(input_frame, text="执行切分", command=self.start_split, width=get_scaled_value(10))
        # 使用grid布局，通过rowspan=4实现跨四行效果，形成方形按钮
        self.execute_btn.grid(row=0, column=2, rowspan=4, padx=(0, 0), pady=0, sticky=tk.NSEW)

        # 结果显示区域
        result_frame = ttk.LabelFrame(parent, text="切分结果", padding=self.base_padding)
        result_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 0))

        # 配置 result_frame 的 grid 布局
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        # 创建结果表格
        columns = ("item", "value")
        self.split_tree = ttk.Treeview(result_frame, columns=columns, show="headings", font=self.base_font)

        # 设置列标题和宽度
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        self.split_tree.column("item", width=get_scaled_value(120), anchor=tk.W)
        self.split_tree.column("value", width=get_scaled_value(400), anchor=tk.W)

        # 添加滚动条
        split_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.split_tree.yview)
        self.split_tree.configure(yscrollcommand=split_scrollbar.set)

        # 布局表格和滚动条
        self.split_tree.grid(row=0, column=0, sticky="nsew")
        split_scrollbar.grid(row=0, column=1, sticky="ns")

    def setup_advanced_tab(self, parent):
        """设置高级工具标签页"""
        # 标题
        title_label = ttk.Label(parent, text="高级网络工具", font=self.title_font)
        title_label.pack(pady=(0, self.large_padding))

        # IPv4查询区域
        ipv4_frame = ttk.LabelFrame(parent, text="IPv4地址查询", padding=self.base_padding)
        ipv4_frame.pack(fill=tk.X, pady=(0, self.base_padding))

        ipv4_input_frame = ttk.Frame(ipv4_frame)
        ipv4_input_frame.pack(fill=tk.X, pady=self.small_padding)

        ttk.Label(ipv4_input_frame, text="IP地址:", font=self.base_font).pack(side=tk.LEFT)
        self.ipv4_entry = ttk.Entry(ipv4_input_frame, font=self.base_font, width=get_scaled_value(20))
        self.ipv4_entry.pack(side=tk.LEFT, padx=(self.small_padding, 0))

        query_button = ttk.Button(ipv4_input_frame, text="查询", command=self.query_ipv4)
        query_button.pack(side=tk.LEFT, padx=(self.small_padding, 0))

        # IPv4结果显示
        self.ipv4_result = tk.Text(ipv4_frame, height=get_scaled_value(8), font=self.base_font, wrap=tk.WORD)
        self.ipv4_result.pack(fill=tk.X, pady=self.small_padding)

    def setup_app_icon(self):
        """设置应用程序图标"""
        try:
            # 从Base64数据加载图标
            icon_data = base64.b64decode(APP_ICON_BASE64)
            image = Image.open(BytesIO(icon_data))
            self.app_icon = ImageTk.PhotoImage(image)
            self.root.iconphoto(True, self.app_icon)
        except Exception as e:
            print(f"设置图标时出错: {e}")

    # 以下是基本的事件处理方法，需要根据实际功能进一步完善
    def start_planning(self):
        """开始子网规划"""
        cidr = self.planning_cidr_entry.get().strip()
        count_text = self.subnet_count_entry.get().strip()
        
        if not cidr or not count_text:
            tk.messagebox.showwarning("警告", "请输入网络地址和子网数量")
            return
            
        try:
            count = int(count_text)
            # TODO: 实现实际的规划逻辑
            print(f"规划网络 {cidr} 为 {count} 个子网")
        except ValueError:
            tk.messagebox.showerror("错误", "子网数量必须是数字")

    def start_split(self):
        """开始子网切分"""
        parent = self.parent_entry.get().strip()
        mask = self.split_entry.get().strip()
        
        if not parent or not mask:
            tk.messagebox.showwarning("警告", "请输入父网络和子网掩码")
            return
            
        try:
            # TODO: 实现实际的切分逻辑
            print(f"切分网络 {parent}/{mask}")
        except Exception as e:
            tk.messagebox.showerror("错误", f"切分失败: {e}")

    def query_ipv4(self):
        """查询IPv4信息"""
        ip = self.ipv4_entry.get().strip()
        
        if not ip:
            tk.messagebox.showwarning("警告", "请输入IP地址")
            return
            
        try:
            # TODO: 实现实际的IP查询逻辑
            info = f"IP地址: {ip}\n网络类型: 私有网络\n子网掩码: 255.255.255.0"
            self.ipv4_result.delete(1.0, tk.END)
            self.ipv4_result.insert(1.0, info)
        except Exception as e:
            tk.messagebox.showerror("错误", f"查询失败: {e}")

    def validate_cidr(self, text, entry=None, style_based=False):
        """通用CIDR验证函数"""
        text = text.strip()
        is_valid = bool(re.match(self.cidr_pattern, text)) if text else True

        if entry:
            if style_based:
                entry.config(style='Valid.TEntry' if is_valid else 'Invalid.TEntry')
            else:
                entry.config(foreground='black' if is_valid else 'red')

        return "1" if entry else is_valid

    def create_notebook(self, parent):
        """创建主标签页容器"""
        # 创建标签页容器
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 应用DPI缩放到标签页
        self.apply_notebook_dpi_scaling()

    def apply_notebook_dpi_scaling(self):
        """应用DPI缩放到标签页样式"""
        # 缩放标签页内边距
        tab_padding = (get_scaled_value(15), get_scaled_value(6))
        
        # 设置Notebook的基本样式
        self.style.configure("TNotebook", background="#ffffff")
        
        # 使用默认边框样式，移除深灰色边框
        self.style.configure("TLabelframe")
        
        # 增大LabelFrame标题的字体大小
        self.style.configure(
            "TLabelframe.Label", 
            borderwidth=0, 
            relief="flat", 
            font=("微软雅黑", get_scaled_value(12))
        )

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

    def show_info(self, title, message):
        """显示信息对话框"""
        self.show_custom_dialog(title, message, "info")

    def show_error(self, title, message):
        """显示错误对话框"""
        self.show_custom_dialog(title, message, "error")

    def show_warning(self, title, message):
        """显示警告对话框"""
        self.show_custom_dialog(title, message, "warning")

    def show_custom_dialog(self, title, message, dialog_type="info"):
        """显示自定义的居中对话框，支持高清缩放"""
        result = None

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

        # 根据DPI缩放设置对话框大小
        dialog_width = get_scaled_value(350)
        dialog_height = get_scaled_value(180)
        dialog.minsize(width=dialog_width, height=dialog_height)

        # 设置对话框内容
        frame = ttk.Frame(dialog, padding=self.large_padding)
        frame.pack(fill=tk.BOTH, expand=True)

        # 设置frame的grid布局
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=1)

        # 添加消息文本，居中显示，根据缩放调整wraplength
        wrap_length = int(dialog_width * 0.8)
        msg_label = ttk.Label(frame, text=message, wraplength=wrap_length, font=self.base_font)
        msg_label.grid(row=0, column=0, sticky="nsew", pady=(0, self.base_padding))

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
            # 只有确定按钮，使用高清缩放的样式
            ok_btn = ttk.Button(btn_frame, text="确定", command=on_ok, 
                              style="Dialog.TButton")
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

        # 显示对话框并设置焦点
        dialog.deiconify()

        # 在对话框显示后强制设置焦点
        def set_focus():
            dialog.lift()  # 确保对话框在最上层
            dialog.focus_force()  # 强制设置对话框为焦点

        # 使用after_idle确保在所有事件处理完成后再设置焦点
        dialog.after_idle(set_focus)

        # 等待对话框关闭
        self.root.wait_window(dialog)

        return result

    def show_result(self, message, keep_data=False):
        """显示结果消息"""
        # 这里可以添加结果显示逻辑，比如状态栏或者弹出消息
        print(f"结果: {message}")

    def get_scaled_font(self, base_size, weight="normal"):
        """获取缩放后的字体

        Args:
            base_size: 基础字体大小
            weight: 字体粗细 ("normal", "bold")

        Returns:
            缩放后的字体元组
        """
        scaled_size = max(8, int(base_size * SCALE_FACTOR))
        return ("微软雅黑", scaled_size, weight)

    def get_scaled_padding(self, base_padding):
        """获取缩放后的内边距

        Args:
            base_padding: 基础内边距

        Returns:
            缩放后的内边距
        """
        return get_scaled_value(base_padding)

        # 为蓝色标签页样式
        self.style.configure(
            "Blue.TNotebook.Tab",
            background="#e3f2fd",  # 浅蓝色背景
            foreground="#1976d2",  # 深蓝色文字
            padding=tab_padding,  # 应用缩放后的内边距
            relief="flat",  # 边框样式
            font=("微软雅黑", get_scaled_value(10)),
        )

        # 蓝色标签选中状态
        self.style.map(
            "Blue.TNotebook.Tab",
            background=[
                ("selected", "#2196f3"),  # 选中时使用更鲜艳的蓝色
                ("!selected", "#e3f2fd"),
            ],  # 非选中时的背景色
            foreground=[
                ("selected", "white"), 
                ("!selected", "#1976d2")
            ],  # 选中时白色文字
            font=[
                ("selected", ("微软雅黑", get_scaled_value(10), "bold")),
                ("!selected", ("微软雅黑", get_scaled_value(10), "normal")),
            ],  # 选中时加粗，非选中时正常
        )
        
        # 类似地处理其他颜色的标签页样式
        # 绿色标签样式
        self.style.configure(
            "Green.TNotebook.Tab",
            background="#e8f5e9",  # 浅绿色背景
            foreground="#388e3c",  # 深绿色文字
            padding=tab_padding,  # 应用缩放后的内边距
            relief="flat",  # 边框样式
            font=("微软雅黑", get_scaled_value(10)),
        )
        
        self.style.map(
            "Green.TNotebook.Tab",
            background=[
                ("selected", "#4caf50"),  # 选中时使用更鲜艳的绿色
                ("!selected", "#e8f5e9"),
            ],  # 非选中时的背景色
            foreground=[
                ("selected", "white"), 
                ("!selected", "#388e3c")
            ],  # 选中时白色文字
            font=[
                ("selected", ("微软雅黑", get_scaled_value(10), "bold")),
                ("!selected", ("微软雅黑", get_scaled_value(10), "normal")),
            ],  # 选中时加粗，非选中时正常
        )
        
        # 橙色标签样式
        self.style.configure(
            "Orange.TNotebook.Tab",
            background="#fff3e0",  # 浅橙色背景
            foreground="#f57c00",  # 深橙色文字
            padding=tab_padding,  # 应用缩放后的内边距
            relief="flat",  # 边框样式
            font=("微软雅黑", get_scaled_value(10)),
        )
        
        self.style.map(
            "Orange.TNotebook.Tab",
            background=[
                ("selected", "#ff9800"),  # 选中时使用更鲜艳的橙色
                ("!selected", "#fff3e0"),
            ],  # 非选中时的背景色
            foreground=[
                ("selected", "white"), 
                ("!selected", "#f57c00")
            ],  # 选中时白色文字
            font=[
                ("selected", ("微软雅黑", get_scaled_value(10), "bold")),
                ("!selected", ("微软雅黑", get_scaled_value(10), "normal")),
            ],  # 选中时加粗，非选中时正常
        )
        
        # 紫色标签样式
        self.style.configure(
            "Purple.TNotebook.Tab",
            background="#f3e5f5",  # 浅紫色背景
            foreground="#7b1fa2",  # 深紫色文字
            padding=tab_padding,  # 应用缩放后的内边距
            relief="flat",  # 边框样式
            font=("微软雅黑", get_scaled_value(10)),
        )
        
        self.style.map(
            "Purple.TNotebook.Tab",
            background=[
                ("selected", "#9c27b0"),  # 选中时使用更鲜艳的紫色
                ("!selected", "#f3e5f5"),
            ],  # 非选中时的背景色
            foreground=[
                ("selected", "white"), 
                ("!selected", "#7b1fa2")
            ],  # 选中时白色文字
            font=[
                ("selected", ("微软雅黑", get_scaled_value(10), "bold")),
                ("!selected", ("微软雅黑", get_scaled_value(10), "normal")),
            ],  # 选中时加粗，非选中时正常
        )
        
        # 粉色标签样式
        self.style.configure(
            "Pink.TNotebook.Tab",
            background="#fce4ec",  # 浅粉色背景
            foreground="#c2185b",  # 深粉色文字
            padding=tab_padding,  # 应用缩放后的内边距
            relief="flat",  # 边框样式
            font=("微软雅黑", get_scaled_value(10)),
        )
        
        self.style.map(
            "Pink.TNotebook.Tab",
            background=[
                ("selected", "#e91e63"),  # 选中时使用更鲜艳的粉色
                ("!selected", "#fce4ec"),
            ],  # 非选中时的背景色
            foreground=[
                ("selected", "white"), 
                ("!selected", "#c2185b")
            ],  # 选中时白色文字
            font=[
                ("selected", ("微软雅黑", get_scaled_value(10), "bold")),
                ("!selected", ("微软雅黑", get_scaled_value(10), "normal")),
            ],  # 选中时加粗，非选中时正常
        )
        
        # 青色标签样式
        self.style.configure(
            "Cyan.TNotebook.Tab",
            background="#e0f2f1",  # 浅青色背景
            foreground="#00796b",  # 深青色文字
            padding=tab_padding,  # 应用缩放后的内边距
            relief="flat",  # 边框样式
            font=("微软雅黑", get_scaled_value(10)),
        )
        
        self.style.map(
            "Cyan.TNotebook.Tab",
            background=[
                ("selected", "#009688"),  # 选中时使用更鲜艳的青色
                ("!selected", "#e0f2f1"),
            ],  # 非选中时的背景色
            foreground=[
                ("selected", "white"), 
                ("!selected", "#00796b")
            ],  # 选中时白色文字
            font=[
                ("selected", ("微软雅黑", get_scaled_value(10), "bold")),
                ("!selected", ("微软雅黑", get_scaled_value(10), "normal")),
            ],  # 选中时加粗，非选中时正常
        )


if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    
    # 创建应用程序实例
    app = IPSubnetSplitterApp(root)
    
    # 启动GUI主循环
    root.mainloop()
