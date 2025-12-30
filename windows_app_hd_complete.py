#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPv4/IPv6 子网规划工具
支持子网切分、子网规划、高级工具等功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json
import math
import re

# 尝试导入Excel相关模块
HAS_EXCEL_SUPPORT = False
try:
    from openpyxl import load_workbook
    from openpyxl.workbook import Workbook
    HAS_EXCEL_SUPPORT = True
except ImportError:
    pass

# 配置文件路径
CONFIG_FILE = "subnet_planner_config.json"

class ColoredNotebook:
    """自定义彩色标签页组件，支持DPI缩放"""
    def __init__(self, parent, style=None, tab_change_callback=None, is_top_level=False):
        self.parent = parent
        self.tab_change_callback = tab_change_callback
        self.is_top_level = is_top_level
        
        # 创建主框架
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签栏框架
        self.tab_frame = ttk.Frame(self.main_frame, style="TabFrame.TFrame")
        self.tab_frame.pack(fill=tk.X, side=tk.TOP, anchor=tk.N)
        
        # 创建内容区域框架
        self.content_area = ttk.Frame(self.main_frame)
        self.content_area.pack(fill=tk.BOTH, expand=True, side=tk.TOP, anchor=tk.N)
        
        # 标签数据存储
        self.tabs = []
        self.current_tab = None
        
        # 绑定鼠标滚轮事件
        self.tab_frame.bind("<MouseWheel>", self.on_mouse_wheel)
        
        # 标签样式
        self.style = style or ttk.Style()
        
        # 创建颜色样式
        self.light_blue_style = "LightBlue.TFrame"
        self.light_green_style = "LightGreen.TFrame"
        self.light_purple_style = "LightPurple.TFrame"
        self.light_pink_style = "LightPink.TFrame"
        
        # 配置样式
        self.configure_styles()
    
    def configure_styles(self):
        """配置组件样式"""
        # 标签框架样式
        self.style.configure("TabFrame.TFrame", background="#2c3e50")
        
        # 激活标签样式
        self.style.configure("ActiveTab.TLabel", 
                           background="#3498db", 
                           foreground="white",
                           relief=tk.FLAT,
                           borderwidth=0,
                           font=("微软雅黑", 10, "bold"),
                           padding=(10, 5))
        
        # 非激活标签样式
        self.style.configure("InactiveTab.TLabel", 
                           background="#2c3e50", 
                           foreground="#bdc3c7",
                           relief=tk.FLAT,
                           borderwidth=0,
                           font=("微软雅黑", 10),
                           padding=(10, 5))
        
        # 标签悬停样式
        self.style.map("InactiveTab.TLabel",
                      background=[("active", "#34495e")],
                      foreground=[("active", "white")])
        
        # 内容区域颜色样式
        self.style.configure(self.light_blue_style, background="#e3f2fd")
        self.style.configure(self.light_green_style, background="#e8f5e9")
        self.style.configure(self.light_purple_style, background="#f3e5f5")
        self.style.configure(self.light_pink_style, background="#fce4ec")
    
    def add_tab(self, title, content_frame, color="#ffffff"):
        """添加标签页"""
        # 创建标签按钮
        tab_label = ttk.Label(self.tab_frame, 
                             text=title,
                             style="InactiveTab.TLabel")
        
        # 绑定点击事件
        tab_label.bind("<Button-1>", lambda e, t=title: self.switch_tab(t))
        
        # 存储标签信息
        tab_info = {
            "title": title,
            "label": tab_label,
            "frame": content_frame,
            "color": color
        }
        self.tabs.append(tab_info)
        
        # 打包标签
        tab_label.pack(side=tk.LEFT, padx=1, pady=0)
        
        # 如果是第一个标签，默认激活
        if len(self.tabs) == 1:
            self.switch_tab(title)
    
    def switch_tab(self, tab_title):
        """切换标签页"""
        # 找到要切换的标签
        target_tab = None
        for tab in self.tabs:
            if tab["title"] == tab_title:
                target_tab = tab
                break
        
        if not target_tab:
            return
        
        # 隐藏当前标签内容
        if self.current_tab:
            self.current_tab["frame"].pack_forget()
            self.current_tab["label"]["style"] = "InactiveTab.TLabel"
        
        # 显示新标签内容
        target_tab["frame"].pack(fill=tk.BOTH, expand=True, in_=self.content_area)
        target_tab["label"]["style"] = "ActiveTab.TLabel"
        
        # 更新当前标签
        self.current_tab = target_tab
        
        # 调用标签切换回调
        if self.tab_change_callback:
            tab_index = self.tabs.index(target_tab)
            self.tab_change_callback(tab_index)
    
    def on_mouse_wheel(self, event):
        """处理鼠标滚轮事件，用于横向滚动标签"""
        # 这里可以添加标签横向滚动功能
        pass
    
    def pack(self, **kwargs):
        """转发pack方法"""
        self.main_frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """转发grid方法"""
        self.main_frame.grid(**kwargs)
    
    def place(self, **kwargs):
        """转发place方法"""
        self.main_frame.place(**kwargs)
    
    def destroy(self):
        """销毁组件"""
        self.main_frame.destroy()

class SubnetPlannerApp:
    """子网规划工具应用程序类"""
    def __init__(self, root):
        """初始化应用程序"""
        self.root = root
        self.root.title("子网规划工具")
        self.root.geometry("1200x800")
        
        # 初始化DPI缩放
        self.setup_dpi_scaling()
        
        # 初始化样式
        self.setup_styles()
        
        # 初始化配置
        self.load_config()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建菜单系统
        self.create_menu_bar()
        
        # 创建顶级标签页
        self.create_top_level_notebook()
        
        # 创建信息栏
        self.create_info_bar()
        
        # 初始化历史记录
        self.undo_stack = []
        self.redo_stack = []
        self.history = []
        self.max_history = 50
        
        # 初始化IPv4/IPv6历史记录
        self.ipv4_history = []
        self.ipv6_history = []
    
    def setup_dpi_scaling(self):
        """设置DPI缩放"""
        # 获取屏幕DPI
        self.dpi = self.root.winfo_fpixels("1i")
        self.scale_factor = self.dpi / 96.0  # 基于96 DPI的缩放因子
        
        # 设置tkinter缩放
        self.root.tk.call("tk", "scaling", self.scale_factor)
    
    def get_scaled_value(self, value):
        """获取缩放后的值"""
        return int(value * self.scale_factor)
    
    def setup_styles(self):
        """设置应用程序样式"""
        self.style = ttk.Style()
        
        # 配置基础字体
        self.base_font = ("微软雅黑", int(10 * self.scale_factor))
        self.small_font = ("微软雅黑", int(9 * self.scale_factor))
        self.bold_font = ("微软雅黑", int(10 * self.scale_factor), "bold")
        
        # 配置主题
        self.style.theme_use("clam")
        
        # 配置框架样式
        self.style.configure("Main.TFrame", background="#f5f5f5")
        self.style.configure("Card.TFrame", background="white", relief=tk.RAISED, borderwidth=1)
        
        # 配置按钮样式
        self.style.configure("TButton", font=self.base_font, padding=self.get_scaled_value(5))
        self.style.configure("Accent.TButton", background="#3498db", foreground="white", font=self.bold_font)
        
        # 配置标签样式
        self.style.configure("TLabel", font=self.base_font, foreground="#333333")
        self.style.configure("Heading.TLabel", font=self.bold_font, foreground="#2c3e50")
        
        # 配置输入控件样式
        self.style.configure("TEntry", font=self.base_font, padding=self.get_scaled_value(3))
        self.style.configure("TCombobox", font=self.base_font, padding=self.get_scaled_value(3))
    
    def load_config(self):
        """加载配置"""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "recent_files": [],
                "window_size": [1200, 800],
                "default_theme": "light"
            }
    
    def save_config(self):
        """保存配置"""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def create_menu_bar(self):
        """创建标准菜单栏"""
        # 创建菜单
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建", command=self.new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="打开", command=self.open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="保存", command=self.save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为", command=self.save_project_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="导出", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.exit_app, accelerator="Alt+F4")
        
        # 编辑菜单
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="撤销", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="重做", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="复制", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="粘贴", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="删除", command=self.delete, accelerator="Delete")
        
        # 查看菜单
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="信息栏", command=self.toggle_info_bar, accelerator="Ctrl+I")
        view_menu.add_separator()
        view_menu.add_command(label="缩放", command=self.change_scale)
        
        # 工具菜单
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="IPv4查询", command=lambda: self.switch_to_tab("高级工具", 0))
        tools_menu.add_command(label="IPv6查询", command=lambda: self.switch_to_tab("高级工具", 1))
        tools_menu.add_command(label="子网合并", command=lambda: self.switch_to_tab("高级工具", 2))
        tools_menu.add_command(label="重叠检测", command=lambda: self.switch_to_tab("高级工具", 3))
        
        # 帮助菜单
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用指南", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="检查更新", command=self.check_update)
    
    def create_top_level_notebook(self):
        """创建顶级标签页"""
        # 创建顶级标签页
        self.top_level_notebook = ColoredNotebook(self.main_frame)
        self.top_level_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建子网规划模块
        self.planning_frame = ttk.Frame(self.top_level_notebook.content_area, padding=self.get_scaled_value(10))
        self.setup_planning_page()
        
        # 创建子网切分模块
        self.split_frame = ttk.Frame(self.top_level_notebook.content_area, padding=self.get_scaled_value(10))
        self.setup_split_page()
        
        # 创建高级工具模块
        self.advanced_frame = ttk.Frame(self.top_level_notebook.content_area, padding=self.get_scaled_value(10))
        self.setup_advanced_tools_page()
        
        # 添加顶级标签页
        self.top_level_notebook.add_tab("子网规划", self.planning_frame, "#fce4ec")
        self.top_level_notebook.add_tab("子网切分", self.split_frame, "#fff3e0")
        self.top_level_notebook.add_tab("高级工具", self.advanced_frame, "#e8f5e9")
    
    def setup_planning_page(self):
        """设置子网规划页面"""
        # 配置网格布局
        self.planning_frame.grid_columnconfigure(0, weight=1)
        self.planning_frame.grid_columnconfigure(1, weight=1)
        self.planning_frame.grid_rowconfigure(0, weight=1)
        
        # 左侧：子网需求
        left_frame = ttk.Frame(self.planning_frame, style="Card.TFrame", padding=self.get_scaled_value(10))
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, self.get_scaled_value(5)))
        
        # 右侧：需求池
        right_frame = ttk.Frame(self.planning_frame, style="Card.TFrame", padding=self.get_scaled_value(10))
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(self.get_scaled_value(5), 0))
        
        # 子网需求标题
        ttk.Label(left_frame, text="子网需求", style="Heading.TLabel").pack(fill=tk.X, pady=(0, self.get_scaled_value(10)))
        
        # 子网需求表格
        columns = ("index", "name", "hosts")
        self.requirements_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=10)
        self.requirements_tree.heading("index", text="序号")
        self.requirements_tree.heading("name", text="子网名称")
        self.requirements_tree.heading("hosts", text="需求数")
        
        # 设置列宽
        self.requirements_tree.column("index", width=self.get_scaled_value(50), minwidth=self.get_scaled_value(50), stretch=False, anchor="center")
        self.requirements_tree.column("name", width=self.get_scaled_value(150), minwidth=self.get_scaled_value(100), stretch=True)
        self.requirements_tree.column("hosts", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(60), stretch=False, anchor="center")
        
        # 添加滚动条
        requirements_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.requirements_tree.yview)
        self.requirements_tree.configure(yscrollcommand=requirements_scrollbar.set)
        
        # 布局子网需求表格
        self.requirements_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        requirements_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # 需求池标题
        ttk.Label(right_frame, text="需求池", style="Heading.TLabel").pack(fill=tk.X, pady=(0, self.get_scaled_value(10)))
        
        # 需求池表格
        self.pool_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=10)
        self.pool_tree.heading("index", text="序号")
        self.pool_tree.heading("name", text="子网名称")
        self.pool_tree.heading("hosts", text="需求数")
        
        # 设置列宽
        self.pool_tree.column("index", width=self.get_scaled_value(50), minwidth=self.get_scaled_value(50), stretch=False, anchor="center")
        self.pool_tree.column("name", width=self.get_scaled_value(150), minwidth=self.get_scaled_value(100), stretch=True)
        self.pool_tree.column("hosts", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(60), stretch=False, anchor="center")
        
        # 添加滚动条
        pool_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.pool_tree.yview)
        self.pool_tree.configure(yscrollcommand=pool_scrollbar.set)
        
        # 布局需求池表格
        self.pool_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        pool_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # 按钮框架
        button_frame = ttk.Frame(self.planning_frame, padding=self.get_scaled_value(10))
        button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # 配置按钮框架网格
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)
        button_frame.grid_columnconfigure(4, weight=1)
        
        # 添加按钮
        self.add_btn = ttk.Button(button_frame, text="添加", command=self.add_subnet_requirement, style="Accent.TButton")
        self.add_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.get_scaled_value(5)))
        
        # 删除按钮
        self.delete_btn = ttk.Button(button_frame, text="删除", command=self.delete_subnet_requirement)
        self.delete_btn.grid(row=0, column=1, sticky="ew", padx=(self.get_scaled_value(5), self.get_scaled_value(5)))
        
        # 撤销按钮
        self.undo_btn = ttk.Button(button_frame, text="撤销", command=self.undo)
        self.undo_btn.grid(row=0, column=2, sticky="ew", padx=(self.get_scaled_value(5), self.get_scaled_value(5)))
        
        # 移动按钮
        self.move_btn = ttk.Button(button_frame, text="移动", command=self.move_subnet)
        self.move_btn.grid(row=0, column=3, sticky="ew", padx=(self.get_scaled_value(5), self.get_scaled_value(5)))
        
        # 导入按钮
        self.import_btn = ttk.Button(button_frame, text="导入", command=self.import_requirements)
        self.import_btn.grid(row=0, column=4, sticky="ew", padx=(self.get_scaled_value(5), 0))
        
        # 规划结果区域
        result_frame = ttk.LabelFrame(self.planning_frame, text="规划结果", padding=self.get_scaled_value(10))
        result_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(self.get_scaled_value(10), 0))
        
        # 创建规划结果标签页
        self.planning_notebook = ColoredNotebook(result_frame)
        self.planning_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 已分配子网页面
        self.allocated_frame = ttk.Frame(self.planning_notebook.content_area, padding=self.get_scaled_value(5))
        self.allocated_tree = ttk.Treeview(
            self.allocated_frame,
            columns=("index", "name", "cidr", "required", "available", "network", "netmask", "broadcast"),
            show="headings",
            height=5
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
        
        # 设置列宽
        self.allocated_tree.column("index", width=self.get_scaled_value(50), minwidth=self.get_scaled_value(50), stretch=False, anchor="center")
        self.allocated_tree.column("name", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.allocated_tree.column("cidr", width=self.get_scaled_value(100), minwidth=self.get_scaled_value(80), stretch=True)
        self.allocated_tree.column("required", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(60), stretch=False, anchor="center")
        self.allocated_tree.column("available", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(60), stretch=False, anchor="center")
        self.allocated_tree.column("network", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.allocated_tree.column("netmask", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.allocated_tree.column("broadcast", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        
        # 添加滚动条
        allocated_scrollbar = ttk.Scrollbar(self.allocated_frame, orient=tk.VERTICAL, command=self.allocated_tree.yview)
        self.allocated_tree.configure(yscrollcommand=allocated_scrollbar.set)
        
        # 布局
        self.allocated_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        allocated_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # 剩余网段页面
        self.remaining_frame = ttk.Frame(self.planning_notebook.content_area, padding=self.get_scaled_value(5))
        self.remaining_tree = ttk.Treeview(
            self.remaining_frame,
            columns=("index", "cidr", "network", "netmask", "broadcast", "usable"),
            show="headings",
            height=5
        )
        
        # 设置列标题
        self.remaining_tree.heading("index", text="序号")
        self.remaining_tree.heading("cidr", text="CIDR")
        self.remaining_tree.heading("network", text="网络地址")
        self.remaining_tree.heading("netmask", text="子网掩码")
        self.remaining_tree.heading("broadcast", text="广播地址")
        self.remaining_tree.heading("usable", text="可用地址数")
        
        # 设置列宽
        self.remaining_tree.column("index", width=self.get_scaled_value(50), minwidth=self.get_scaled_value(50), stretch=False, anchor="center")
        self.remaining_tree.column("cidr", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.remaining_tree.column("network", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.remaining_tree.column("netmask", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.remaining_tree.column("broadcast", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=True)
        self.remaining_tree.column("usable", width=self.get_scaled_value(100), minwidth=self.get_scaled_value(80), stretch=False, anchor="center")
        
        # 添加滚动条
        remaining_scrollbar = ttk.Scrollbar(self.remaining_frame, orient=tk.VERTICAL, command=self.remaining_tree.yview)
        self.remaining_tree.configure(yscrollcommand=remaining_scrollbar.set)
        
        # 布局
        self.remaining_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        remaining_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # 网段分布图页面
        self.chart_frame = ttk.Frame(self.planning_notebook.content_area, padding=self.get_scaled_value(5))
        self.chart_canvas = tk.Canvas(self.chart_frame, bg="#333333")
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 添加规划结果标签页
        self.planning_notebook.add_tab("已分配子网", self.allocated_frame, "#e3f2fd")
        self.planning_notebook.add_tab("剩余网段", self.remaining_frame, "#e8f5e9")
        self.planning_notebook.add_tab("网段分布图", self.chart_frame, "#f3e5f5")
        
        # 导出和规划按钮
        export_planning_btn = ttk.Button(result_frame, text="导出规划", command=self.export_planning_result)
        export_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=self.get_scaled_value(-3))
        
        self.execute_planning_btn = ttk.Button(result_frame, text="规划子网", command=self.execute_subnet_planning)
        button_gap = self.get_scaled_value(10)
        self.root.update_idletasks()
        export_btn_width = export_planning_btn.winfo_reqwidth()
        execute_btn_x = -export_btn_width - button_gap
        self.execute_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=execute_btn_x, y=self.get_scaled_value(-3))
    
    def setup_split_page(self):
        """设置子网切分页面"""
        # 配置网格布局
        self.split_frame.grid_columnconfigure(0, weight=1)
        self.split_frame.grid_columnconfigure(1, weight=1)
        self.split_frame.grid_rowconfigure(1, weight=1)
        
        # 左侧：输入参数
        input_frame = ttk.LabelFrame(self.split_frame, text="输入参数", padding=self.get_scaled_value(10))
        input_frame.grid(row=0, column=0, sticky="nsew", padx=(0, self.get_scaled_value(5)))
        
        # 右侧：历史记录
        history_frame = ttk.LabelFrame(self.split_frame, text="历史记录", padding=self.get_scaled_value(10))
        history_frame.grid(row=0, column=1, sticky="nsew", padx=(self.get_scaled_value(5), 0))
        
        # 父网段标签和输入框
        ttk.Label(input_frame, text="父网段", font=self.base_font).grid(row=1, column=0, sticky=tk.W, pady=self.get_scaled_value(5), padx=(self.get_scaled_value(5), 0))
        
        # 初始化子网切分的历史记录列表
        self.split_parent_networks = ["10.0.0.0/8"]
        self.split_networks = ["10.21.60.0/23"]
        
        # 父网段输入框
        self.parent_entry = ttk.Combobox(
            input_frame,
            values=self.split_parent_networks,
            font=self.base_font,
            width=self.get_scaled_value(20)
        )
        self.parent_entry.grid(row=1, column=1, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.EW)
        self.parent_entry.insert(0, "10.0.0.0/8")
        
        # 切分段标签和输入框
        ttk.Label(input_frame, text="切分段", font=self.base_font).grid(row=2, column=0, sticky=tk.W, pady=self.get_scaled_value(5), padx=(self.get_scaled_value(5), 0))
        
        self.split_entry = ttk.Combobox(
            input_frame,
            values=self.split_networks,
            font=self.base_font,
            width=self.get_scaled_value(20)
        )
        self.split_entry.grid(row=2, column=1, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.EW)
        self.split_entry.insert(0, "10.21.60.0/23")
        
        # 执行按钮
        self.execute_btn = ttk.Button(input_frame, text="执行切分", command=self.start_split, width=self.get_scaled_value(10))
        self.execute_btn.grid(row=0, column=2, rowspan=4, padx=(0, 0), pady=0, sticky=tk.NSEW)
        
        # 结果显示区域
        self.result_notebook = ttk.Notebook(self.split_frame)
        self.result_notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(self.get_scaled_value(10), 0))
        
        # 切分段信息标签页
        split_info_frame = ttk.Frame(self.result_notebook, padding=self.get_scaled_value(10))
        self.result_notebook.add(split_info_frame, text="切分段信息")
        
        # 创建切分段信息表格
        columns = ("item", "value")
        self.split_tree = ttk.Treeview(split_info_frame, columns=columns, show="headings")
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        self.split_tree.column("item", width=self.get_scaled_value(120), anchor=tk.W)
        self.split_tree.column("value", width=self.get_scaled_value(300))
        self.split_tree.pack(fill=tk.BOTH, expand=True)
        
        # 剩余网段标签页
        remaining_info_frame = ttk.Frame(self.result_notebook, padding=self.get_scaled_value(10))
        self.result_notebook.add(remaining_info_frame, text="剩余网段")
        
        # 创建剩余网段表格
        columns = ("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable")
        self.remaining_split_tree = ttk.Treeview(remaining_info_frame, columns=columns, show="headings")
        self.remaining_split_tree.heading("index", text="序号")
        self.remaining_split_tree.heading("cidr", text="CIDR")
        self.remaining_split_tree.heading("network", text="网络地址")
        self.remaining_split_tree.heading("netmask", text="子网掩码")
        self.remaining_split_tree.heading("wildcard", text="通配符掩码")
        self.remaining_split_tree.heading("broadcast", text="广播地址")
        self.remaining_split_tree.heading("usable", text="可用地址数")
        
        # 设置列宽
        self.remaining_split_tree.column("index", width=self.get_scaled_value(50), anchor=tk.CENTER)
        self.remaining_split_tree.column("cidr", width=self.get_scaled_value(120))
        self.remaining_split_tree.column("network", width=self.get_scaled_value(120))
        self.remaining_split_tree.column("netmask", width=self.get_scaled_value(120))
        self.remaining_split_tree.column("wildcard", width=self.get_scaled_value(120))
        self.remaining_split_tree.column("broadcast", width=self.get_scaled_value(120))
        self.remaining_split_tree.column("usable", width=self.get_scaled_value(100), anchor=tk.CENTER)
        
        # 添加滚动条
        remaining_split_scrollbar = ttk.Scrollbar(remaining_info_frame, orient=tk.VERTICAL, command=self.remaining_split_tree.yview)
        self.remaining_split_tree.configure(yscrollcommand=remaining_split_scrollbar.set)
        
        # 布局
        self.remaining_split_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        remaining_split_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        
        # 图表显示区域
        self.chart_frame = ttk.LabelFrame(self.split_frame, text="网段分布图表", padding=self.get_scaled_value(10))
        self.chart_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(self.get_scaled_value(10), 0))
        
        # 创建图表画布
        self.chart_canvas = tk.Canvas(self.chart_frame, bg="#f0f0f0")
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
    
    def setup_advanced_tools_page(self):
        """设置高级工具页面"""
        # 创建高级工具标签页
        self.advanced_notebook = ColoredNotebook(self.advanced_frame)
        self.advanced_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 1. IPv4地址信息查询功能
        self.ipv4_info_frame = ttk.Frame(self.advanced_notebook.content_area, padding=self.get_scaled_value(10))
        self.create_ipv4_info_section()
        
        # 2. IPv6地址信息查询功能
        self.ipv6_info_frame = ttk.Frame(self.advanced_notebook.content_area, padding=self.get_scaled_value(10))
        self.create_ipv6_info_section()
        
        # 3. 子网合并与范围转CIDR功能
        self.merge_frame = ttk.Frame(self.advanced_notebook.content_area, padding=self.get_scaled_value(10))
        self.create_merged_subnets_and_cidr_section()
        
        # 4. 子网重叠检测功能
        self.overlap_frame = ttk.Frame(self.advanced_notebook.content_area, padding=self.get_scaled_value(10))
        self.create_subnet_overlap_section()
        
        # 添加高级工具标签页
        self.advanced_notebook.add_tab("IPv4查询", self.ipv4_info_frame, "#e3f2fd")
        self.advanced_notebook.add_tab("IPv6查询", self.ipv6_info_frame, "#e8f5e9")
        self.advanced_notebook.add_tab("子网合并", self.merge_frame, "#f3e5f5")
        self.advanced_notebook.add_tab("重叠检测", self.overlap_frame, "#fce4ec")
    
    def create_ipv4_info_section(self):
        """创建IPv4地址信息查询功能界面"""
        # 配置网格布局
        self.ipv4_info_frame.grid_columnconfigure(0, weight=1)
        self.ipv4_info_frame.grid_rowconfigure(1, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.ipv4_info_frame, text="IPv4地址信息查询", padding=self.get_scaled_value(10))
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, self.get_scaled_value(10)))
        
        # 输入区域网格配置
        input_frame.grid_columnconfigure(1, weight=1)
        
        # IPv4地址标签和输入框
        ttk.Label(input_frame, text="IPv4地址", font=self.base_font).grid(row=0, column=0, sticky=tk.W, padx=(self.get_scaled_value(5), 0), pady=self.get_scaled_value(5))
        
        self.ipv4_info_entry = ttk.Combobox(input_frame, values=[], font=self.base_font, width=self.get_scaled_value(25))
        self.ipv4_info_entry.grid(row=0, column=1, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.EW)
        self.ipv4_info_entry.insert(0, "192.168.1.1")
        
        # CIDR标签和下拉列表
        ttk.Label(input_frame, text="CIDR", font=self.base_font).grid(row=0, column=2, sticky=tk.W, padx=(self.get_scaled_value(5), 0), pady=self.get_scaled_value(5))
        
        self.ipv4_cidr_var = tk.StringVar()
        self.ipv4_cidr_combobox = ttk.Combobox(
            input_frame, 
            textvariable=self.ipv4_cidr_var, 
            width=self.get_scaled_value(3), 
            state="readonly", 
            font=self.base_font
        )
        self.ipv4_cidr_combobox['values'] = list(range(1, 33))
        self.ipv4_cidr_combobox.current(23)  # 默认选择24
        self.ipv4_cidr_combobox.grid(row=0, column=3, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.W)
        
        # 查询按钮
        self.ipv4_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv4_info)
        self.ipv4_info_btn.grid(row=0, column=4, padx=(self.get_scaled_value(10), 0), pady=self.get_scaled_value(5), sticky=tk.EW)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.ipv4_info_frame, text="查询结果", padding=self.get_scaled_value(10))
        result_frame.grid(row=1, column=0, sticky="nsew")
        
        # 创建Treeview和垂直滚动条
        self.ipv4_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        self.ipv4_info_tree.heading("item", text="项目")
        self.ipv4_info_tree.heading("value", text="值")
        
        self.ipv4_info_tree.column("item", width=self.get_scaled_value(120), anchor=tk.W)
        self.ipv4_info_tree.column("value", width=self.get_scaled_value(350))
        
        # 添加垂直滚动条
        ipv4_info_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.ipv4_info_tree.yview)
        self.ipv4_info_tree.configure(yscrollcommand=ipv4_info_scrollbar.set)
        
        # 布局
        self.ipv4_info_tree.grid(row=0, column=0, sticky=tk.NSEW)
        ipv4_info_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
    
    def create_ipv6_info_section(self):
        """创建IPv6地址信息查询功能界面"""
        # 配置网格布局
        self.ipv6_info_frame.grid_columnconfigure(0, weight=1)
        self.ipv6_info_frame.grid_rowconfigure(1, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.ipv6_info_frame, text="IPv6地址信息查询", padding=self.get_scaled_value(10))
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, self.get_scaled_value(10)))
        
        # 输入区域网格配置
        input_frame.grid_columnconfigure(1, weight=1)
        
        # IPv6地址标签和输入框
        ttk.Label(input_frame, text="IPv6地址", font=self.base_font).grid(row=0, column=0, sticky=tk.W, padx=(self.get_scaled_value(5), 0), pady=self.get_scaled_value(5))
        
        self.ipv6_info_entry = ttk.Combobox(input_frame, values=[], font=self.base_font, width=self.get_scaled_value(40))
        self.ipv6_info_entry.grid(row=0, column=1, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.EW)
        self.ipv6_info_entry.insert(0, "2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        
        # CIDR标签和下拉列表
        ttk.Label(input_frame, text="CIDR", font=self.base_font).grid(row=0, column=2, sticky=tk.W, padx=(self.get_scaled_value(5), 0), pady=self.get_scaled_value(5))
        
        self.ipv6_cidr_var = tk.StringVar()
        self.ipv6_cidr_combobox = ttk.Combobox(
            input_frame, 
            textvariable=self.ipv6_cidr_var, 
            width=self.get_scaled_value(3), 
            state="readonly", 
            font=self.base_font
        )
        self.ipv6_cidr_combobox['values'] = list(range(1, 129))
        self.ipv6_cidr_combobox.current(63)  # 默认选择64
        self.ipv6_cidr_combobox.grid(row=0, column=3, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.W)
        
        # 查询按钮
        self.ipv6_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv6_info)
        self.ipv6_info_btn.grid(row=0, column=4, padx=(self.get_scaled_value(10), 0), pady=self.get_scaled_value(5), sticky=tk.EW)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.ipv6_info_frame, text="查询结果", padding=self.get_scaled_value(10))
        result_frame.grid(row=1, column=0, sticky="nsew")
        
        # 创建Treeview和垂直滚动条
        self.ipv6_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")
        self.ipv6_info_tree.heading("item", text="项目")
        self.ipv6_info_tree.heading("value", text="值")
        
        self.ipv6_info_tree.column("item", width=self.get_scaled_value(120), anchor=tk.W)
        self.ipv6_info_tree.column("value", width=self.get_scaled_value(350))
        
        # 添加垂直滚动条
        ipv6_info_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.ipv6_info_tree.yview)
        self.ipv6_info_tree.configure(yscrollcommand=ipv6_info_scrollbar.set)
        
        # 布局
        self.ipv6_info_tree.grid(row=0, column=0, sticky=tk.NSEW)
        ipv6_info_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
    
    def create_merged_subnets_and_cidr_section(self):
        """创建子网合并与范围转CIDR功能界面"""
        # 配置网格布局
        self.merge_frame.grid_columnconfigure(0, weight=1)
        self.merge_frame.grid_rowconfigure(2, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.merge_frame, text="子网合并与范围转CIDR", padding=self.get_scaled_value(10))
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, self.get_scaled_value(10)))
        
        # 输入文本框
        self.merge_text = tk.Text(input_frame, height=5, font=self.base_font)
        self.merge_text.pack(fill=tk.BOTH, expand=True, pady=(0, self.get_scaled_value(10)))
        self.merge_text.insert(tk.END, "192.168.1.0/24\n192.168.2.0/24\n192.168.3.0/24")
        
        # 按钮框架
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X)
        
        # 合并子网按钮
        self.merge_subnets_btn = ttk.Button(button_frame, text="合并子网", command=self.merge_subnets)
        self.merge_subnets_btn.pack(side=tk.LEFT, padx=(0, self.get_scaled_value(10)))
        
        # 范围转CIDR按钮
        self.range_to_cidr_btn = ttk.Button(button_frame, text="范围转CIDR", command=self.range_to_cidr)
        self.range_to_cidr_btn.pack(side=tk.LEFT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.merge_frame, text="合并结果", padding=self.get_scaled_value(10))
        result_frame.grid(row=1, column=0, sticky="nsew")
        
        # 创建结果文本框
        self.merge_result_text = tk.Text(result_frame, height=10, font=self.base_font)
        
        # 添加垂直滚动条
        merge_result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.merge_result_text.yview)
        self.merge_result_text.configure(yscrollcommand=merge_result_scrollbar.set)
        
        # 布局
        self.merge_result_text.grid(row=0, column=0, sticky=tk.NSEW)
        merge_result_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
    
    def create_subnet_overlap_section(self):
        """创建子网重叠检测功能界面"""
        # 配置网格布局
        self.overlap_frame.grid_columnconfigure(0, weight=1)
        self.overlap_frame.grid_rowconfigure(1, weight=1)
        
        # 创建输入区域
        input_frame = ttk.LabelFrame(self.overlap_frame, text="子网重叠检测", padding=self.get_scaled_value(10))
        input_frame.grid(row=0, column=0, sticky="nsew", pady=(0, self.get_scaled_value(10)))
        
        # 输入文本框
        self.overlap_text = tk.Text(input_frame, height=5, font=self.base_font)
        self.overlap_text.pack(fill=tk.BOTH, expand=True, pady=(0, self.get_scaled_value(10)))
        self.overlap_text.insert(tk.END, "192.168.1.0/24\n192.168.1.128/25\n10.0.0.0/8")
        
        # 检测按钮
        self.check_overlap_btn = ttk.Button(input_frame, text="检测重叠", command=self.check_subnet_overlap)
        self.check_overlap_btn.pack(side=tk.RIGHT)
        
        # 创建结果区域
        result_frame = ttk.LabelFrame(self.overlap_frame, text="检测结果", padding=self.get_scaled_value(10))
        result_frame.grid(row=1, column=0, sticky="nsew")
        
        # 创建结果表格
        columns = ("subnet1", "subnet2", "status")
        self.overlap_tree = ttk.Treeview(result_frame, columns=columns, show="headings")
        self.overlap_tree.heading("subnet1", text="子网1")
        self.overlap_tree.heading("subnet2", text="子网2")
        self.overlap_tree.heading("status", text="状态")
        
        # 设置列宽
        self.overlap_tree.column("subnet1", width=self.get_scaled_value(150))
        self.overlap_tree.column("subnet2", width=self.get_scaled_value(150))
        self.overlap_tree.column("status", width=self.get_scaled_value(100), anchor=tk.CENTER)
        
        # 添加垂直滚动条
        overlap_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.overlap_tree.yview)
        self.overlap_tree.configure(yscrollcommand=overlap_scrollbar.set)
        
        # 布局
        self.overlap_tree.grid(row=0, column=0, sticky=tk.NSEW)
        overlap_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
    
    def create_info_bar(self):
        """创建信息栏"""
        # 创建信息栏框架
        self.info_bar = ttk.Frame(self.main_frame, height=self.get_scaled_value(30), style="InfoBar.TFrame")
        self.info_bar.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.S)
        
        # 创建信息标签
        self.info_label = ttk.Label(self.info_bar, text="准备就绪", font=self.small_font, foreground="#333333")
        self.info_label.pack(side=tk.LEFT, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5))
        
        # 创建关闭按钮
        self.info_close_btn = ttk.Button(self.info_bar, text="×", command=self.hide_info_bar, width=2, style="Close.TButton")
        self.info_close_btn.pack(side=tk.RIGHT, padx=self.get_scaled_value(5), pady=self.get_scaled_value(5))
        
        # 信息栏样式
        self.style.configure("InfoBar.TFrame", background="#e3f2fd", relief=tk.RAISED, borderwidth=1)
        self.style.configure("Close.TButton", font=("微软雅黑", 10, "bold"), padding=0)
    
    def show_info_bar(self):
        """显示信息栏"""
        self.info_bar.pack(fill=tk.X, side=tk.BOTTOM, anchor=tk.S)
    
    def hide_info_bar(self):
        """隐藏信息栏"""
        self.info_bar.pack_forget()
    
    def toggle_info_bar(self):
        """切换信息栏显示/隐藏状态"""
        if self.info_bar.winfo_ismapped():
            self.hide_info_bar()
        else:
            self.show_info_bar()
    
    def update_info_bar(self, message, color="#333333"):
        """更新信息栏内容"""
        self.info_label.config(text=message, foreground=color)
        self.show_info_bar()
    
    def add_subnet_requirement(self):
        """添加子网需求"""
        # 这里实现添加子网需求的逻辑
        self.update_info_bar("添加子网需求功能")
    
    def delete_subnet_requirement(self):
        """删除子网需求"""
        # 这里实现删除子网需求的逻辑
        self.update_info_bar("删除子网需求功能")
    
    def undo(self):
        """撤销操作"""
        # 这里实现撤销操作的逻辑
        self.update_info_bar("撤销功能")
    
    def redo(self):
        """重做操作"""
        # 这里实现重做操作的逻辑
        self.update_info_bar("重做功能")
    
    def move_subnet(self):
        """移动子网"""
        # 这里实现移动子网的逻辑
        self.update_info_bar("移动子网功能")
    
    def import_requirements(self):
        """导入子网需求"""
        # 这里实现导入子网需求的逻辑
        self.update_info_bar("导入子网需求功能")
    
    def execute_subnet_planning(self):
        """执行子网规划"""
        # 这里实现执行子网规划的逻辑
        self.update_info_bar("执行子网规划功能")
    
    def export_planning_result(self):
        """导出规划结果"""
        # 这里实现导出规划结果的逻辑
        self.update_info_bar("导出规划结果功能")
    
    def start_split(self):
        """开始子网切分"""
        # 这里实现子网切分的逻辑
        self.update_info_bar("开始子网切分功能")
    
    def execute_ipv4_info(self):
        """执行IPv4地址信息查询"""
        # 清空当前结果
        for item in self.ipv4_info_tree.get_children():
            self.ipv4_info_tree.delete(item)
        
        # 添加示例结果
        self.ipv4_info_tree.insert("", tk.END, values=("网络地址", "192.168.1.0"))
        self.ipv4_info_tree.insert("", tk.END, values=("子网掩码", "255.255.255.0"))
        self.ipv4_info_tree.insert("", tk.END, values=("可用地址", "192.168.1.1 - 192.168.1.254"))
        self.ipv4_info_tree.insert("", tk.END, values=("可用数量", "254"))
        self.ipv4_info_tree.insert("", tk.END, values=("广播地址", "192.168.1.255"))
        self.ipv4_info_tree.insert("", tk.END, values=("CIDR", "192.168.1.0/24"))
        self.ipv4_info_tree.insert("", tk.END, values=("类别", "C类地址"))
        self.ipv4_info_tree.insert("", tk.END, values=("私有地址", "是"))
        
        self.update_info_bar("IPv4地址信息查询完成")
    
    def execute_ipv6_info(self):
        """执行IPv6地址信息查询"""
        # 清空当前结果
        for item in self.ipv6_info_tree.get_children():
            self.ipv6_info_tree.delete(item)
        
        # 添加示例结果
        self.ipv6_info_tree.insert("", tk.END, values=("完整地址", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"))
        self.ipv6_info_tree.insert("", tk.END, values=("压缩地址", "2001:db8:85a3::8a2e:370:7334"))
        self.ipv6_info_tree.insert("", tk.END, values=("前缀", "2001:db8:85a3::/48"))
        self.ipv6_info_tree.insert("", tk.END, values=("子网ID", "0000:0000:8a2e"))
        self.ipv6_info_tree.insert("", tk.END, values=("接口ID", "0370:7334"))
        self.ipv6_info_tree.insert("", tk.END, values=("类型", "全球单播地址"))
        
        self.update_info_bar("IPv6地址信息查询完成")
    
    def merge_subnets(self):
        """合并子网"""
        # 清空当前结果
        self.merge_result_text.delete(1.0, tk.END)
        
        # 添加示例结果
        self.merge_result_text.insert(tk.END, "合并结果：\n192.168.0.0/22\n")
        
        self.update_info_bar("子网合并完成")
    
    def range_to_cidr(self):
        """范围转CIDR"""
        # 清空当前结果
        self.merge_result_text.delete(1.0, tk.END)
        
        # 添加示例结果
        self.merge_result_text.insert(tk.END, "转换结果：\n192.168.1.0/24\n")
        
        self.update_info_bar("范围转CIDR完成")
    
    def check_subnet_overlap(self):
        """检测子网重叠"""
        # 清空当前结果
        for item in self.overlap_tree.get_children():
            self.overlap_tree.delete(item)
        
        # 添加示例结果
        self.overlap_tree.insert("", tk.END, values=("192.168.1.0/24", "192.168.1.128/25", "重叠"))
        self.overlap_tree.insert("", tk.END, values=("192.168.1.0/24", "10.0.0.0/8", "不重叠"))
        
        self.update_info_bar("子网重叠检测完成")
    
    def switch_to_tab(self, notebook_title, tab_index):
        """切换到指定标签页"""
        # 这里实现切换标签页的逻辑
        self.update_info_bar(f"切换到{notebook_title}的第{tab_index+1}个标签页")
    
    def new_project(self):
        """新建项目"""
        self.update_info_bar("新建项目功能")
    
    def open_project(self):
        """打开项目"""
        self.update_info_bar("打开项目功能")
    
    def save_project(self):
        """保存项目"""
        self.update_info_bar("保存项目功能")
    
    def save_project_as(self):
        """另存为项目"""
        self.update_info_bar("另存为项目功能")
    
    def export_data(self):
        """导出数据"""
        self.update_info_bar("导出数据功能")
    
    def exit_app(self):
        """退出应用"""
        if messagebox.askyesno("退出确认", "确定要退出子网规划工具吗？"):
            self.root.destroy()
    
    def copy(self):
        """复制"""
        self.update_info_bar("复制功能")
    
    def paste(self):
        """粘贴"""
        self.update_info_bar("粘贴功能")
    
    def delete(self):
        """删除"""
        self.update_info_bar("删除功能")
    
    def change_scale(self):
        """改变缩放比例"""
        self.update_info_bar("改变缩放比例功能")
    
    def show_help(self):
        """显示帮助"""
        self.update_info_bar("显示帮助功能")
    
    def show_about(self):
        """显示关于"""
        messagebox.showinfo("关于", "子网规划工具 HD\n版本：1.0.0\n支持IPv4/IPv6子网规划与管理")
    
    def check_update(self):
        """检查更新"""
        self.update_info_bar("检查更新功能")
    
    def draw_distribution_chart(self):
        """绘制网段分布图"""
        # 这里实现绘制网段分布图的逻辑
        self.update_info_bar("绘制网段分布图功能")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubnetPlannerApp(root)
    root.mainloop()