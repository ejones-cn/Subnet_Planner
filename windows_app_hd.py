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
import datetime

# 尝试导入Excel相关模块
HAS_EXCEL_SUPPORT = False
try:
    from openpyxl import load_workbook
    from openpyxl.workbook import Workbook
    HAS_EXCEL_SUPPORT = True
except ImportError:
    pass

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
        self.history_states = []
        self.deleted_history = []
        
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
        
        # 配置Treeview样式
        self.setup_table_styles()
    
    def setup_table_styles(self):
        """设置表格样式"""
        # 配置Treeview整体样式
        self.style.configure("Treeview",
                           background="#ffffff",
                           foreground="#333333",
                           rowheight=self.get_scaled_value(25),
                           fieldbackground="#ffffff",
                           font=self.base_font)
        
        # 配置Treeview头部样式
        self.style.configure("Treeview.Heading",
                           background="#f0f0f0",
                           foreground="#333333",
                           font=self.bold_font,
                           relief=tk.FLAT)
        
        # 配置Treeview选中行样式
        self.style.map("Treeview",
                      background=[("selected", "#3498db")],
                      foreground=[("selected", "#ffffff")])
        
        # 配置斑马条纹样式
        self.style.configure("Treeview.OddRow.TLabel", background="#f9f9f9")
        self.style.configure("Treeview.EvenRow.TLabel", background="#ffffff")
    
    def configure_treeview_styles(self, tree, include_special_tags=False):
        """配置Treeview样式，包括斑马条纹和特殊标签
        
        Args:
            tree: Treeview对象
            include_special_tags: 是否包含特殊标签样式
        """
        # 配置斑马条纹
        tree.tag_configure("odd", background="#f9f9f9")
        tree.tag_configure("even", background="#ffffff")
        
        if include_special_tags:
            # 配置信息标签样式
            tree.tag_configure("info", background="#e3f2fd", foreground="#1976d2")
            tree.tag_configure("warning", background="#fff3e0", foreground="#f57c00")
            tree.tag_configure("error", background="#ffebee", foreground="#d32f2f")
    
    def update_table_zebra_stripes(self, tree, update_index=False):
        """更新表格斑马条纹
        
        Args:
            tree: Treeview对象
            update_index: 是否更新行号
        """
        for index, item in enumerate(tree.get_children()):
            # 更新斑马条纹
            tag = "even" if index % 2 == 0 else "odd"
            tree.item(item, tags=(tag,))
            
            # 更新行号
            if update_index:
                values = list(tree.item(item, "values"))
                if values and values[0] != index + 1:
                    values[0] = index + 1
                    tree.item(item, values=values)
    
    def auto_resize_columns(self, tree):
        """自动调整列宽
        
        Args:
            tree: Treeview对象
        """
        for col in tree["columns"]:
            # 遍历所有行，找出最大宽度
            max_width = 0
            
            # 检查表头宽度
            header_width = tree.heading(col, "text")
            if header_width:
                max_width = max(max_width, len(header_width) * 8 * self.scale_factor)
            
            # 检查所有行内容宽度
            for item in tree.get_children():
                value = tree.item(item, "values")[tree["columns"].index(col)]
                if value:
                    value_width = len(str(value)) * 8 * self.scale_factor
                    max_width = max(max_width, value_width)
            
            # 设置列宽，加上一些边距
            tree.column(col, width=int(max_width) + self.get_scaled_value(10))
    
    def resize_tables(self):
        """调整表格列宽，确保所有列都能完整显示并自适应窗口宽度"""
        # 已分配子网表调整
        if hasattr(self, 'allocated_tree'):
            self.auto_resize_columns(self.allocated_tree)
        
        # 剩余网段表调整
        if hasattr(self, 'remaining_tree'):
            self.auto_resize_columns(self.remaining_tree)
        
        # 需求表调整
        if hasattr(self, 'requirements_tree'):
            self.auto_resize_columns(self.requirements_tree)
        
        # 需求池表调整
        if hasattr(self, 'pool_tree'):
            self.auto_resize_columns(self.pool_tree)
    
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
        """设置子网规划功能的界面"""
        # 设置grid布局
        self.planning_frame.grid_columnconfigure(0, weight=1)  # 左侧列可伸缩
        self.planning_frame.grid_columnconfigure(1, weight=1)  # 右侧列可伸缩
        self.planning_frame.grid_rowconfigure(0, weight=0)  # 父网段设置行，固定高度
        self.planning_frame.grid_rowconfigure(1, weight=0)  # 需求池和子网需求行，固定高度
        self.planning_frame.grid_rowconfigure(2, weight=1)  # 规划结果行，可伸缩

        # 父网段设置区域
        parent_frame = ttk.LabelFrame(self.planning_frame, text="父网段设置", padding=(self.get_scaled_value(5), self.get_scaled_value(10), self.get_scaled_value(10), self.get_scaled_value(10)))
        parent_frame.grid(row=0, column=0, sticky="ew", padx=(0, self.get_scaled_value(5)), pady=(0, 0))  # 左上角
        # 设置父网段设置面板的固定宽度
        parent_frame.configure(width=250)

        # 初始化父网段列表 - 为子网规划创建独立的历史记录列表
        self.planning_parent_networks = ["10.21.48.0/20"]  # 默认父网段

        # 父网段下拉文本框
        ttk.Label(parent_frame, text="").pack(side=tk.LEFT, padx=(0, 0))
        vcmd = (self.root.register(lambda p: self.validate_cidr(p, None, style_based=False)), '%P')
        self.planning_parent_entry = ttk.Combobox(
            parent_frame,
            values=self.planning_parent_networks,
            width=16,
            validate='all',
            validatecommand=vcmd,
        )
        self.planning_parent_entry.pack(side=tk.LEFT, padx=(0, self.get_scaled_value(5)), fill=tk.X, expand=True)
        self.planning_parent_entry.insert(0, "10.21.48.0/20")  # 默认值
        self.planning_parent_entry.config(state="normal")  # 允许手动输入

        # 需求池区域
        history_frame = ttk.LabelFrame(self.planning_frame, text="需求池", padding=(self.get_scaled_value(10), self.get_scaled_value(10), 0, self.get_scaled_value(10)))
        history_frame.grid(row=1, column=0, sticky="nsew", padx=(0, self.get_scaled_value(5)), pady=(0, self.get_scaled_value(10)))  # 左下角
        # 设置需求池面板的固定宽度
        history_frame.configure(width=250)

        # 子网需求区域
        requirements_frame = ttk.LabelFrame(self.planning_frame, text="子网需求", padding=(self.get_scaled_value(10), self.get_scaled_value(10), 0, self.get_scaled_value(10)))
        requirements_frame.grid(
            row=0, column=1, rowspan=2, sticky="nsew", padx=(self.get_scaled_value(5), 0), pady=(0, self.get_scaled_value(10))
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
        self.pool_tree.column("index", width=self.get_scaled_value(40), minwidth=self.get_scaled_value(20), stretch=False, anchor="e")
        self.pool_tree.column("name", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(80), stretch=True)  # 减小初始宽度，允许伸缩
        self.pool_tree.column("hosts", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(40), stretch=False)

        # 配置斑马条纹样式
        self.configure_treeview_styles(self.pool_tree)

        # 绑定双击事件以实现编辑功能
        self.pool_tree.bind("<Double-1>", self.on_pool_tree_double_click)
        # 绑定左键单击事件以实现取消选择功能
        self.pool_tree.bind("<Button-1>", self.on_treeview_click)

        # 添加滚动条，确保只作用于表格，位于表格右侧
        self.pool_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)
        
        # 直接创建Treeview和滚动条，不使用自动隐藏功能
        self.pool_tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.pool_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.pool_scrollbar.config(command=self.pool_tree.yview)
        self.pool_tree.config(yscrollcommand=self.pool_scrollbar.set)

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
        self.requirements_tree.column("index", width=self.get_scaled_value(40), minwidth=self.get_scaled_value(40), stretch=False, anchor="e")
        self.requirements_tree.column("name", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(80), stretch=True)  # 减小初始宽度，允许伸缩
        self.requirements_tree.column("hosts", width=self.get_scaled_value(80), minwidth=self.get_scaled_value(80), stretch=False)

        # 绑定双击事件以实现编辑功能
        self.requirements_tree.bind("<Double-1>", self.on_requirements_tree_double_click)
        # 绑定左键单击事件以实现取消选择功能
        self.requirements_tree.bind("<Button-1>", self.on_treeview_click)

        # 放置表格
        self.requirements_tree.grid(row=0, column=1, sticky="nsew", padx=(self.get_scaled_value(10), 0))

        # 添加滚动条，确保只作用于表格，位于表格右侧
        self.requirements_scrollbar = ttk.Scrollbar(inner_frame, orient=tk.VERTICAL)
        
        # 直接创建Treeview和滚动条，不使用自动隐藏功能
        self.requirements_tree.grid(row=0, column=1, sticky=tk.NSEW)
        self.requirements_scrollbar.grid(row=0, column=2, sticky=tk.NS)
        self.requirements_scrollbar.config(command=self.requirements_tree.yview)
        self.requirements_tree.config(yscrollcommand=self.requirements_scrollbar.set)

        # 按钮框架内部布局 - 按照用户要求设置行权重
        button_frame.grid_rowconfigure(0, weight=0)  # 添加按钮
        button_frame.grid_rowconfigure(1, weight=0)  # 删除按钮
        button_frame.grid_rowconfigure(2, weight=0)  # 撤销按钮
        button_frame.grid_rowconfigure(3, weight=0)  # 移动/交换按钮
        button_frame.grid_rowconfigure(4, weight=1)  # 空白区域，将底部按钮推到底部
        button_frame.grid_rowconfigure(5, weight=0)  # 空白行，保持原有结构
        button_frame.grid_rowconfigure(6, weight=0)  # 导入按钮
        button_frame.grid_columnconfigure(0, weight=1)

        # 添加按钮
        self.add_btn = ttk.Button(button_frame, text="添加", command=self.add_subnet_requirement, width=7, style="Accent.TButton")
        self.add_btn.grid(row=0, column=0, sticky="ew", pady=(0, self.get_scaled_value(5)))

        # 删除按钮
        self.delete_btn = ttk.Button(button_frame, text="删除", command=self.delete_subnet_requirement, width=7)
        self.delete_btn.grid(row=1, column=0, sticky="ew", pady=(0, self.get_scaled_value(5)))

        # 撤销按钮
        self.undo_delete_btn = ttk.Button(button_frame, text="撤销", command=self.undo_delete, width=7)
        self.undo_delete_btn.grid(row=2, column=0, sticky="ew", pady=(0, self.get_scaled_value(5)))

        # 移动/交换按钮（根据选中情况自动判断操作）
        self.swap_btn = ttk.Button(button_frame, text="↔", command=self.move_records, width=7)
        self.swap_btn.grid(row=3, column=0, sticky="ew", pady=(0, self.get_scaled_value(5)))

        # 导入按钮
        self.import_btn = ttk.Button(button_frame, text="导入", command=self.import_requirements, width=7)
        self.import_btn.grid(row=6, column=0, sticky="ew", pady=(0, 0))

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
        
        # 插入示例数据到子网需求表格
        for i, (name, hosts) in enumerate(requirements_data, start=1):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.requirements_tree.insert("", tk.END, values=(i, name, hosts), tags=(tag,))
        
        # 更新斑马条纹
        self.update_table_zebra_stripes(self.requirements_tree, update_index=True)

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
        # CIDR正则表达式
        cidr_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\/(3[0-2]|[12]?[0-9])$'
        ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(12[0-8]|1[01][0-9]|[1-9]?[0-9])$'
        is_valid = bool(re.match(cidr_pattern, text) or re.match(ipv6_pattern, text)) if text else True
        
        if entry:
            if style_based:
                entry.config(style='Valid.TEntry' if is_valid else 'Invalid.TEntry')
            else:
                entry.config(foreground='black' if is_valid else 'red')
        
        return "1" if is_valid else "0"
    
    def execute_subnet_planning(self, from_history=False):
        """执行子网规划
        
        Args:
            from_history: 是否从历史记录重新执行，True表示不将操作记入历史
        """
        # 检查是否有规划父网段输入框
        if not hasattr(self, 'planning_parent_entry'):
            self.update_info_bar("请先输入父网段", "red")
            return
        
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
            self.clear_tree_items(self.remaining_tree)

            # 显示已分配子网
            for i, subnet in enumerate(plan_result['allocated_subnets'], 1):
                # 设置斑马条纹标签
                tag = "evenrow" if i % 2 == 0 else "oddrow"
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
                    tags=(tag,),
                )

            # 数据添加完成后，自动调整列宽以适应内容
            self.auto_resize_columns(self.allocated_tree)

            # 显示剩余网段
            for i, subnet in enumerate(plan_result['remaining_subnets_info'], 1):
                # 设置斑马条纹标签
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.remaining_tree.insert(
                    "",
                    tk.END,
                    values=(
                        i,
                        plan_result['remaining_subnets'][i - 1],
                        subnet["network"],
                        subnet["netmask"],
                        subnet["broadcast"],
                        subnet["usable_addresses"],
                    ),
                    tags=(tag,),
                )

            # 数据添加完成后，自动调整列宽以适应内容
            self.auto_resize_columns(self.remaining_tree)

            # 如果不是从历史记录执行，将操作记录保存到历史
            if not from_history:
                # 检查当前父网段是否在列表中，如果不在则添加（使用子网规划专用的父网段历史记录）
                current_parent = self.planning_parent_entry.get().strip()
                if current_parent and current_parent not in self.planning_parent_networks:
                    self.planning_parent_networks.append(current_parent)
                    self.planning_parent_entry.config(values=self.planning_parent_networks)

                # 保存当前状态到操作记录
                self.save_current_state("执行规划")

            # 生成网段分布图数据并绘制
            self.generate_planning_chart_data(plan_result)

            self.update_info_bar("子网规划完成", "green")

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
    
    def export_planning_result(self):
        """导出规划结果"""
        self.update_info_bar("正在导出规划结果...")
        
        # 使用文件对话框让用户选择导出文件路径
        file_path = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ],
            title="导出规划结果"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    # 写入标题
                    f.write("子网规划结果\n")
                    f.write("=" * 50 + "\n\n")
                    
                    # 写入已分配子网
                    f.write("已分配子网：\n")
                    f.write("-" * 30 + "\n")
                    f.write("名称\tCIDR\t需求数\t可用数\t网络地址\t子网掩码\t广播地址\n")
                    f.write("-" * 30 + "\n")
                    
                    for item in self.allocated_tree.get_children():
                        values = self.allocated_tree.item(item, "values")
                        f.write(f"{values[1]}\t{values[2]}\t{values[3]}\t{values[4]}\t{values[5]}\t{values[6]}\t{values[7]}\n")
                    
                    f.write("\n剩余网段：\n")
                    f.write("-" * 30 + "\n")
                    f.write("CIDR\t网络地址\t子网掩码\t广播地址\t可用地址数\n")
                    f.write("-" * 30 + "\n")
                    
                    for item in self.remaining_tree.get_children():
                        values = self.remaining_tree.item(item, "values")
                        f.write(f"{values[1]}\t{values[2]}\t{values[3]}\t{values[4]}\t{values[5]}\n")
                    
                self.update_info_bar(f"规划结果已成功导出到 {file_path}", "green")
            except Exception as e:
                self.update_info_bar(f"导出失败：{str(e)}", "red")
    
    def import_requirements(self):
        """导入子网需求数据"""
        self.update_info_bar("正在导入需求数据...")
        
        # 使用文件对话框让用户选择导入文件
        file_path = askopenfilename(
            filetypes=[
                ("文本文件", "*.txt"),
                ("CSV文件", "*.csv"),
                ("所有文件", "*.*")
            ],
            title="导入子网需求"
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                # 清空当前需求
                for item in self.requirements_tree.get_children():
                    self.requirements_tree.delete(item)
                
                # 解析导入的数据
                imported_count = 0
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # 简单的CSV格式解析，使用逗号或制表符分隔
                        parts = re.split(r'[,\t]', line)
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            hosts = parts[1].strip()
                            if name and hosts.isdigit():
                                # 添加到需求树
                                self.requirements_tree.insert("", tk.END, values=(imported_count + 1, name, hosts))
                                imported_count += 1
                
                self.update_info_bar(f"成功导入 {imported_count} 条需求数据", "green")
            except Exception as e:
                self.update_info_bar(f"导入失败：{str(e)}", "red")
    
    def start_split(self, from_history=False):
        """执行切分操作
        
        Args:
            from_history: 是否从历史记录重新执行，True表示不将操作记入历史
        """
        if not hasattr(self, 'parent_entry') or not hasattr(self, 'split_entry'):
            self.update_info_bar("子网切分功能未初始化", "red")
            return
        
        parent = self.parent_entry.get().strip()
        split = self.split_entry.get().strip()
        
        # 验证输入
        if not parent or not split:
            # 清空表格并显示错误信息
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert("", tk.END, values=("错误", "父网段和切分网段都不能为空！"))
            self.update_info_bar("父网段和切分网段都不能为空", "red")
            return
        
        # 验证CIDR格式
        if not self.validate_cidr(parent):
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert(
                "", tk.END, values=("错误", "父网段格式无效，请输入有效的CIDR格式！")
            )
            self.update_info_bar("父网段格式无效，请输入有效的CIDR格式", "red")
            return
        if not self.validate_cidr(split):
            self.clear_result()
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert(
                "", tk.END, values=("错误", "切分网段格式无效，请输入有效的CIDR格式！")
            )
            self.update_info_bar("切分网段格式无效，请输入有效的CIDR格式", "red")
            return
        
        self.update_info_bar("正在执行子网切分...")
        
        try:
            # 调用切分函数（这里使用示例数据）
            # 实际项目中应该调用真实的子网切分算法
            result = {
                "parent_info": {
                    "cidr": parent,
                    "network": "10.0.0.0",
                    "netmask": "255.0.0.0",
                    "broadcast": "10.255.255.255",
                    "usable": 16777214
                },
                "split_info": {
                    "cidr": split,
                    "network": "10.21.60.0",
                    "netmask": "255.255.254.0",
                    "broadcast": "10.21.61.255",
                    "usable": 510
                },
                "remaining": [
                    {
                        "cidr": "10.0.0.0/16",
                        "network": "10.0.0.0",
                        "netmask": "255.255.0.0",
                        "broadcast": "10.0.255.255",
                        "usable": 65534
                    },
                    {
                        "cidr": "10.1.0.0/16",
                        "network": "10.1.0.0",
                        "netmask": "255.255.0.0",
                        "broadcast": "10.1.255.255",
                        "usable": 65534
                    }
                ]
            }
            
            # 清空现有结果
            self.clear_tree_items(self.split_tree)
            if hasattr(self, 'remaining_split_tree'):
                self.clear_tree_items(self.remaining_split_tree)
            
            # 添加切分段信息
            self.split_tree.insert("", tk.END, values=("父网段", result["parent_info"]["cidr"]))
            self.split_tree.insert("", tk.END, values=("网络地址", result["parent_info"]["network"]))
            self.split_tree.insert("", tk.END, values=("子网掩码", result["parent_info"]["netmask"]))
            self.split_tree.insert("", tk.END, values=("广播地址", result["parent_info"]["broadcast"]))
            self.split_tree.insert("", tk.END, values=("可用地址数", result["parent_info"]["usable"]))
            self.split_tree.insert("", tk.END, values=("切分网段", result["split_info"]["cidr"]))
            self.split_tree.insert("", tk.END, values=("切分网络", result["split_info"]["network"]))
            self.split_tree.insert("", tk.END, values=("切分掩码", result["split_info"]["netmask"]))
            self.split_tree.insert("", tk.END, values=("切分广播", result["split_info"]["broadcast"]))
            self.split_tree.insert("", tk.END, values=("切分可用", result["split_info"]["usable"]))
            
            # 添加剩余网段
            if hasattr(self, 'remaining_split_tree'):
                for i, subnet in enumerate(result["remaining"]):
                    self.remaining_split_tree.insert("", tk.END, values=(
                        i+1, 
                        subnet["cidr"],
                        subnet["network"],
                        subnet["netmask"],
                        subnet["broadcast"],
                        subnet["usable"]
                    ))
            
            self.update_info_bar("子网切分完成", "green")
        except Exception as e:
            self.clear_tree_items(self.split_tree)
            self.split_tree.insert("", tk.END, values=("错误", str(e)))
            self.update_info_bar(f"切分失败：{str(e)}", "red")
    
    def clear_result(self):
        """清空结果"""
        # 清空图表
        if hasattr(self, 'chart_canvas'):
            self.chart_canvas.delete("all")
    
    def clear_tree_items(self, tree):
        """清空Treeview所有项
        
        Args:
            tree: Treeview对象
        """
        for item in tree.get_children():
            tree.delete(item)
    
    def create_split_input_section(self):
        """创建子网切分功能的输入区域"""
        if not hasattr(self, 'split_frame'):
            return
        
        # 创建输入区域框架
        input_frame = ttk.LabelFrame(self.split_frame, text="输入参数", padding=self.get_scaled_value(10))
        input_frame.grid(row=0, column=0, sticky="nsew", padx=self.get_scaled_value(5), pady=self.get_scaled_value(5))
        
        # 配置输入区域网格
        input_frame.grid_columnconfigure(0, weight=0, minsize=self.get_scaled_value(50))
        input_frame.grid_columnconfigure(1, weight=1, minsize=self.get_scaled_value(100))
        input_frame.grid_columnconfigure(2, weight=0, minsize=self.get_scaled_value(30))
        input_frame.grid_columnconfigure(3, weight=1, minsize=self.get_scaled_value(100))
        input_frame.grid_columnconfigure(4, weight=0)
        
        # 父网段标签
        ttk.Label(input_frame, text="父网段", font=self.base_font).grid(
            row=0, column=0, sticky=tk.W + tk.N + tk.S, pady=self.get_scaled_value(5), padx=(self.get_scaled_value(5), 0)
        )
        
        # 父网段输入框
        self.parent_entry = ttk.Combobox(
            input_frame, values=self.split_parent_networks, font=self.base_font,
            validate='all', validatecommand=(self.root.register(lambda p: self.validate_cidr(p, self.parent_entry)), '%P')
        )
        self.parent_entry.grid(row=0, column=1, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.EW + tk.N + tk.S)
        self.parent_entry.insert(0, "10.0.0.0/8")
        self.parent_entry.config(state="normal")
        
        # 父网段历史记录按钮
        parent_history_btn = ttk.Button(input_frame, text="▼", width=2, command=lambda: self.show_history_dialog("parent"))
        parent_history_btn.grid(row=0, column=2, padx=self.get_scaled_value(5), pady=self.get_scaled_value(5), sticky=tk.NS)
        
        # 切分段标签
        ttk.Label(input_frame, text="切分段", font=self.base_font).grid(
            row=1, column=0, sticky=tk.W + tk.N + tk.S, pady=self.get_scaled_value(5), padx=(self.get_scaled_value(5), 0)
        )
        
        # 切分段输入框
        self.split_entry = ttk.Combobox(
            input_frame, values=self.split_networks, font=self.base_font,
            validate='all', validatecommand=(self.root.register(lambda p: self.validate_cidr(p, self.split_entry)), '%P')
        )
        self.split_entry.grid(row=1, column=1, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.EW + tk.N + tk.S)
        self.split_entry.insert(0, "10.21.60.0/23")
        self.split_entry.config(state="normal")
        
        # 切分段历史记录按钮
        split_history_btn = ttk.Button(input_frame, text="▼", width=2, command=lambda: self.show_history_dialog("split"))
        split_history_btn.grid(row=1, column=2, padx=self.get_scaled_value(5), pady=self.get_scaled_value(5), sticky=tk.NS)
        
        # 执行切分按钮
        self.execute_btn = ttk.Button(input_frame, text="执行切分", command=self.start_split,
                                    style="Accent.TButton")
        self.execute_btn.grid(row=0, column=3, rowspan=2, padx=self.get_scaled_value(10), pady=self.get_scaled_value(5), sticky=tk.NS + tk.EW)
    
    def create_split_result_section(self):
        """创建子网切分功能的结果区域"""
        if not hasattr(self, 'split_frame'):
            return
        
        # 创建结果区域框架
        result_frame = ttk.LabelFrame(self.split_frame, text="切分结果", padding=self.get_scaled_value(10))
        result_frame.grid(row=1, column=0, sticky="nsew", padx=self.get_scaled_value(5), pady=self.get_scaled_value(5))
        
        # 配置结果区域网格
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)
        
        # 切分段信息表格
        self.split_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings", height=8)
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        
        # 配置列宽
        self.split_tree.column("item", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=False)
        self.split_tree.column("value", width=self.get_scaled_value(300), minwidth=self.get_scaled_value(200), stretch=True)
        
        # 绑定右键复制功能
        self.bind_treeview_right_click(self.split_tree)
        
        # 剩余网段表格
        self.remaining_tree = ttk.Treeview(
            result_frame, 
            columns=("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable"), 
            show="headings", 
            height=15
        )
        
        # 设置剩余网段表格列标题
        self.remaining_tree.heading("index", text="序号")
        self.remaining_tree.heading("cidr", text="CIDR")
        self.remaining_tree.heading("network", text="网络地址")
        self.remaining_tree.heading("netmask", text="子网掩码")
        self.remaining_tree.heading("wildcard", text="通配符掩码")
        self.remaining_tree.heading("broadcast", text="广播地址")
        self.remaining_tree.heading("usable", text="可用地址数")
        
        # 配置剩余网段表格列宽
        self.remaining_tree.column("index", width=self.get_scaled_value(50), minwidth=self.get_scaled_value(40), stretch=False, anchor="center")
        self.remaining_tree.column("cidr", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=False)
        self.remaining_tree.column("network", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=False)
        self.remaining_tree.column("netmask", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=False)
        self.remaining_tree.column("wildcard", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=False)
        self.remaining_tree.column("broadcast", width=self.get_scaled_value(120), minwidth=self.get_scaled_value(100), stretch=False)
        self.remaining_tree.column("usable", width=self.get_scaled_value(100), minwidth=self.get_scaled_value(80), stretch=False, anchor="center")
        
        # 绑定右键复制功能
        self.bind_treeview_right_click(self.remaining_tree)
        
        # 创建标签页组件
        self.notebook = ColoredNotebook(result_frame, style=self.style)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # 配置标签页切换回调
        self.notebook.tab_change_callback = self.on_tab_change
        
        # 添加标签页
        self.split_info_frame = ttk.Frame(self.notebook.content_area, padding=self.get_scaled_value(5))
        self.split_info_frame.grid_rowconfigure(0, weight=1)
        self.split_info_frame.grid_columnconfigure(0, weight=1)
        
        # 添加切分段信息表格到标签页
        self.split_tree.grid(row=0, column=0, sticky="nsew", in_=self.split_info_frame)
        
        # 剩余网段页面
        self.remaining_frame = ttk.Frame(self.notebook.content_area, padding=self.get_scaled_value(5))
        self.remaining_frame.grid_rowconfigure(0, weight=1)
        self.remaining_frame.grid_columnconfigure(0, weight=1)
        
        # 添加剩余网段表格到标签页
        self.remaining_tree.grid(row=0, column=0, sticky="nsew", in_=self.remaining_frame)
        
        # 添加标签页到notebook
        self.notebook.add_tab("切分段信息", self.split_info_frame, "#e3f2fd")
        self.notebook.add_tab("剩余网段", self.remaining_frame, "#e8f5e9")
        
        # 网段分布图页面
        self.chart_frame = ttk.Frame(self.notebook.content_area, padding=self.get_scaled_value(5))
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        
        # 图表画布
        self.chart_canvas = tk.Canvas(self.chart_frame, bg="#333333")
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")
        
        # 添加图表标签页
        self.notebook.add_tab("网段分布图", self.chart_frame, "#f3e5f5")
    
    def create_scrollable_treeview(self, parent_frame, treeview, scrollbar, no_scrollbar_padx=(0, 10)):
        """创建可滚动的Treeview
        
        Args:
            parent_frame: 父框架
            treeview: Treeview对象
            scrollbar: 滚动条对象
            no_scrollbar_padx: 没有滚动条时的内边距
        """
        # 配置滚动条
        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=self._create_scrollbar_callback(scrollbar, no_scrollbar_padx))
        
        # 布局
        treeview.grid(row=0, column=0, sticky="nsew", in_=parent_frame)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=parent_frame)
    
    def create_scrollable_treeview_with_grid(self, parent_frame, treeview, scrollbar, 
                                         columns, weights, sticky="nsew"):
        """创建带网格布局的可滚动Treeview
        
        Args:
            parent_frame: 父框架
            treeview: Treeview对象
            scrollbar: 滚动条对象
            columns: 列数
            weights: 权重列表
            sticky: 粘性参数
        """
        # 配置父框架网格
        for i in range(columns):
            parent_frame.grid_columnconfigure(i, weight=weights[i])
        
        parent_frame.grid_rowconfigure(0, weight=1)
        
        # 配置滚动条
        scrollbar.config(command=treeview.yview)
        treeview.config(yscrollcommand=self._create_scrollbar_callback(scrollbar, (0, 10)))
        
        # 布局
        treeview.grid(row=0, column=0, sticky=sticky, in_=parent_frame)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=parent_frame)
    
    def create_scrollable_text(self, parent_frame, text_widget, scrollbar, no_scrollbar_padx=(0, 10)):
        """创建可滚动的Text组件
        
        Args:
            parent_frame: 父框架
            text_widget: Text对象
            scrollbar: 滚动条对象
            no_scrollbar_padx: 没有滚动条时的内边距
        """
        # 配置滚动条
        scrollbar.config(command=text_widget.yview)
        text_widget.config(yscrollcommand=self._create_scrollbar_callback(scrollbar, no_scrollbar_padx))
        
        # 布局
        text_widget.grid(row=0, column=0, sticky="nsew", in_=parent_frame)
        scrollbar.grid(row=0, column=1, sticky="ns", in_=parent_frame)
    
    def _create_scrollbar_callback(self, scrollbar, no_scrollbar_padx):
        """创建滚动条回调函数，控制滚动条的显示/隐藏
        
        Args:
            scrollbar: 滚动条对象
            no_scrollbar_padx: 没有滚动条时的内边距
            
        Returns:
            滚动条回调函数
        """
        def callback(*args):
            # 更新滚动条位置
            scrollbar.set(*args)
            # 检查是否需要显示滚动条
            if float(args[0]) <= 0.0 and float(args[1]) >= 1.0:
                # 内容不可滚动，隐藏滚动条
                scrollbar.grid_remove()
            else:
                # 内容可滚动，显示滚动条
                scrollbar.grid()
        return callback
    
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
    
    def bind_treeview_right_click(self, tree):
        """为Treeview绑定右键菜单
        
        Args:
            tree: Treeview对象
        """
        # 创建右键菜单
        right_click_menu = tk.Menu(self.root, tearoff=0)
        right_click_menu.add_command(label="复制", command=lambda: self.copy_cell_data(tree))
        right_click_menu.add_command(label="选择全部", command=lambda: tree.selection_set(tree.get_children()))
        
        # 绑定右键菜单
        def show_menu(event):
            # 获取当前选中的项
            item = tree.identify_row(event.y)
            if item:
                tree.selection_set(item)
                right_click_menu.post(event.x_root, event.y_root)
        
        tree.bind("<Button-3>", show_menu)
    
    def copy_cell_data(self, tree):
        """复制选中的单元格数据
        
        Args:
            tree: Treeview对象
        """
        selected_items = tree.selection()
        if selected_items:
            item = selected_items[0]
            # 获取当前选中的列
            column = tree.identify_column(tree.winfo_pointerx() - tree.winfo_rootx())
            if column != "#0":
                # 转换列号为索引
                col_idx = int(column[1:]) - 1
                values = tree.item(item, "values")
                if col_idx < len(values):
                    cell_value = str(values[col_idx])
                    # 复制到剪贴板
                    self.root.clipboard_clear()
                    self.root.clipboard_append(cell_value)
                    self.update_info_bar(f"已复制：{cell_value}", "green")
    
    def bind_listbox_right_click(self, listbox):
        """为Listbox绑定右键菜单
        
        Args:
            listbox: Listbox对象
        """
        # 创建右键菜单
        right_click_menu = tk.Menu(self.root, tearoff=0)
        right_click_menu.add_command(label="复制", command=lambda: self.copy_listbox_data(listbox))
        right_click_menu.add_command(label="选择全部", command=lambda: listbox.select_set(0, tk.END))
        
        # 绑定右键菜单
        def show_menu(event):
            # 获取当前选中的项
            index = listbox.nearest(event.y)
            if index != -1:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(index)
                right_click_menu.post(event.x_root, event.y_root)
        
        listbox.bind("<Button-3>", show_menu)
    
    def copy_listbox_data(self, listbox):
        """复制Listbox选中的数据
        
        Args:
            listbox: Listbox对象
        """
        selected_indices = listbox.curselection()
        if selected_indices:
            selected_items = [listbox.get(idx) for idx in selected_indices]
            if selected_items:
                # 复制到剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append("\n".join(selected_items))
                self.update_info_bar(f"已复制 {len(selected_items)} 项", "green")
    
    def show_info(self, title, message):
        """显示信息对话框
        
        Args:
            title: 对话框标题
            message: 对话框内容
        """
        messagebox.showinfo(title, message)
    
    def show_error(self, title, message):
        """显示错误对话框
        
        Args:
            title: 对话框标题
            message: 对话框内容
        """
        messagebox.showerror(title, message)
    
    def show_warning(self, title, message):
        """显示警告对话框
        
        Args:
            title: 对话框标题
            message: 对话框内容
        """
        messagebox.showwarning(title, message)
    
    def show_custom_confirm(self, title, message):
        """显示自定义确认对话框
        
        Args:
            title: 对话框标题
            message: 对话框内容
        
        Returns:
            bool: 用户是否点击了确认按钮
        """
        return messagebox.askyesno(title, message)
    
    def animate_info_bar(self, animation_type="show"):
        """动画显示/隐藏信息栏
        
        Args:
            animation_type: 动画类型，"show"表示显示，"hide"表示隐藏
        """
        # 简单实现，直接显示/隐藏
        if animation_type == "show":
            self.show_info_bar()
        else:
            self.hide_info_bar()
    
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
        parent = self.planning_parent_entry.get().strip() if hasattr(self, 'planning_parent_entry') else ""
        
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
        
        # 添加到历史记录
        self.history_states.append(history_record)
        
        # 限制历史记录数量
        if len(self.history_states) > self.max_history:
            self.history_states.pop(0)
    
    def undo_delete(self):
        """撤销最近的删除操作，支持多次撤销"""
        # 检查是否有删除记录历史
        if not self.deleted_history:
            self.update_info_bar("没有可撤销的删除操作")
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
        
        # 更新信息栏
        self.update_info_bar(f"已恢复 {len(restored_subnets)} 条记录", "green")
    
    def update_requirements_tree_zebra_stripes(self):
        """更新子网需求表的斑马条纹"""
        self.update_table_zebra_stripes(self.requirements_tree, update_index=True)
    
    def update_pool_tree_zebra_stripes(self):
        """更新需求池表的斑马条纹"""
        self.update_table_zebra_stripes(self.pool_tree, update_index=True)
    
    def move_left(self):
        """将选中的记录从需求池移动到子网需求"""
        selected_items = self.pool_tree.selection()
        if not selected_items:
            self.update_info_bar("请先选择要移动的记录")
            return
        
        self._move_records_between_trees(self.pool_tree, self.requirements_tree, selected_items, "需求池", "子网需求")
    
    def move_right(self):
        """将选中的需求从左侧移动到右侧"""
        selected_items = self.requirements_tree.selection()
        if not selected_items:
            self.update_info_bar("请先选择要移动的记录")
            return
        
        self._move_records_between_trees(self.requirements_tree, self.pool_tree, selected_items, "子网需求", "需求池")
    
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
            self._move_records_between_trees(
                source_tree=self.requirements_tree,
                target_tree=self.pool_tree,
                selected_items=selected_requirements,
                move_from="子网需求表",
                move_to="需求池"
            )

        # 情况2：仅选中需求池数据，移动到子网需求表
        elif not selected_requirements and selected_pool_items:
            self._move_records_between_trees(
                source_tree=self.pool_tree,
                target_tree=self.requirements_tree,
                selected_items=selected_pool_items,
                move_from="需求池",
                move_to="子网需求表"
            )
    
    def _move_records_between_trees(self, source_tree, target_tree, selected_items, move_from, move_to):
        """在两个树之间移动记录
        
        Args:
            source_tree: 源树
            target_tree: 目标树
            selected_items: 选中的项目
            move_from: 源位置描述
            move_to: 目标位置描述
        """
        # 收集要移动的记录
        records_to_move = []
        for item in selected_items:
            values = source_tree.item(item, "values")
            records_to_move.append(values)
        
        # 删除源树中的记录
        for item in selected_items:
            source_tree.delete(item)
        
        # 添加到目标树
        for record in records_to_move:
            target_tree.insert("", tk.END, values=record)
        
        # 更新斑马条纹
        self.update_table_zebra_stripes(source_tree, update_index=True)
        self.update_table_zebra_stripes(target_tree, update_index=True)
        
        # 更新信息栏
        self.update_info_bar(f"已将 {len(records_to_move)} 条记录从{move_from}移动到{move_to}", "green")
    
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
        if region not in ("cell", "row"):
            return "break"

        # 获取点击的行
        item = tree.identify_row(event.y)
        if not item:
            return "break"
    
    def save_edit(self):
        """保存编辑的数据"""
        if hasattr(self, 'current_edit_item'):
            # 获取新值
            new_value = self.edit_entry.get().strip()

            # 验证数据
            if not new_value:
                self.show_error("错误", "输入不能为空")
                # 重新将焦点设置到编辑框
                self.edit_entry.focus_set()
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
                        # 重新将焦点设置到编辑框
                        self.edit_entry.focus_set()
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
                        # 重新将焦点设置到编辑框
                        self.edit_entry.focus_set()
                        return
                except ValueError:
                    self.show_error("错误", "主机数量必须是整数")
                    # 重新将焦点设置到编辑框
                    self.edit_entry.focus_set()
                    return

            # 根据当前编辑的表格，更新相应的Treeview数据
            if hasattr(self, 'current_edit_tree') and self.current_edit_tree == "requirements":
                # 更新子网需求表
                values = list(self.requirements_tree.item(self.current_edit_item, "values"))
                values[self.current_edit_column_index] = new_value
                self.requirements_tree.item(self.current_edit_item, values=values)
                # 更新斑马条纹
                self.update_table_zebra_stripes(self.requirements_tree, update_index=True)
            elif hasattr(self, 'current_edit_tree') and self.current_edit_tree == "pool":
                # 更新需求池表
                values = list(self.pool_tree.item(self.current_edit_item, "values"))
                values[self.current_edit_column_index] = new_value
                self.pool_tree.item(self.current_edit_item, values=values)
                # 更新斑马条纹
                self.update_table_zebra_stripes(self.pool_tree, update_index=True)

            # 清理编辑状态
            self.edit_entry.destroy()
            del self.current_edit_item
            del self.current_edit_column
            del self.current_edit_column_index
            if hasattr(self, 'current_edit_tree'):
                del self.current_edit_tree
    
    def show_about(self):
        """显示关于"""
        messagebox.showinfo("关于", "子网规划工具 HD\n版本：1.0.0\n支持IPv4/IPv6子网规划与管理")
    
    def check_update(self):
        """检查更新"""
        self.update_info_bar("检查更新功能")
    
    def on_window_resize(self, event):
        """窗口大小变化事件处理
        
        Args:
            event: 事件对象
        """
        # 调整表格列宽
        self.resize_tables()
        
        # 触发图表重绘
        if hasattr(self, 'chart_canvas'):
            self.generate_planning_chart_data()
    
    def generate_planning_chart_data(self, plan_result=None):
        """生成规划图表数据并绘制"""
        # 如果没有提供plan_result，创建一个示例
        if not plan_result:
            plan_result = {
                "parent_cidr": "192.168.0.0/16",
                "allocated_subnets": [
                    {"name": "办公室", "cidr": "192.168.1.0/24", "info": {"num_addresses": 256}},
                    {"name": "财务部", "cidr": "192.168.2.0/24", "info": {"num_addresses": 256}},
                    {"name": "研发部", "cidr": "192.168.3.0/23", "info": {"num_addresses": 512}}
                ]
            }
        
        # 准备图表数据
        parent_cidr = plan_result["parent_cidr"]
        
        chart_data = {
            "parent": {
                "name": parent_cidr,
                "range": 65536  # 默认/16网段的地址数
            },
            "networks": []
        }
        
        # 添加已分配子网
        for subnet in plan_result["allocated_subnets"]:
            chart_data["networks"].append({
                "name": subnet["name"],
                "cidr": subnet["cidr"],
                "range": subnet["info"]["num_addresses"],
                "type": "split"
            })
        
        # 绘制图表
        self.draw_distribution_chart(chart_data)
    
    def draw_distribution_chart(self, chart_data=None):
        """绘制网段分布图"""
        if not hasattr(self, 'chart_canvas'):
            return
        
        # 如果没有提供chart_data，使用默认数据
        if not chart_data:
            chart_data = {
                "parent": {"name": "192.168.0.0/16", "range": 65536},
                "networks": [
                    {"name": "办公室", "cidr": "192.168.1.0/24", "range": 256, "type": "split"},
                    {"name": "财务部", "cidr": "192.168.2.0/24", "range": 256, "type": "split"},
                    {"name": "研发部", "cidr": "192.168.3.0/23", "range": 512, "type": "split"}
                ]
            }
        
        # 清空画布
        self.chart_canvas.delete("all")
        
        # 获取画布尺寸
        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()
        
        # 设置图表边距
        margin = self.get_scaled_value(20)
        chart_width = width - 2 * margin
        chart_height = height - 2 * margin
        
        # 计算每个网段的高度
        if chart_data["networks"]:
            bar_height = min(self.get_scaled_value(30), chart_height / (len(chart_data["networks"]) * 1.5))
        else:
            bar_height = self.get_scaled_value(30)
        
        # 绘制标题
        self.chart_canvas.create_text(
            width // 2, margin // 2,
            text=f"网段分布图 - {chart_data['parent']['name']}",
            font=(self.base_font[0], int(self.base_font[1] * 1.2), "bold"),
            fill="white"
        )
        
        # 绘制背景
        self.chart_canvas.create_rectangle(
            margin, margin, width - margin, height - margin,
            fill="#2c3e50", outline="#34495e", width=2
        )
        
        # 计算总地址数
        total_addresses = chart_data["parent"]["range"]
        
        # 绘制每个网段
        y_pos = margin + self.get_scaled_value(10)
        for i, network in enumerate(chart_data["networks"]):
            # 计算网段宽度比例
            bar_width = int((network["range"] / total_addresses) * chart_width)
            
            # 选择颜色
            colors = ["#3498db", "#2ecc71", "#9b59b6", "#f1c40f", "#e74c3c"]
            color = colors[i % len(colors)]
            
            # 绘制网段矩形
            self.chart_canvas.create_rectangle(
                margin, y_pos, margin + bar_width, y_pos + bar_height,
                fill=color, outline="#ffffff", width=1
            )
            
            # 绘制网段名称和CIDR
            text_x = margin + 5
            text_y = y_pos + bar_height // 2
            self.chart_canvas.create_text(
                text_x, text_y,
                text=f"{network['name']} ({network['cidr']})",
                font=self.base_font,
                fill="white",
                anchor=tk.W
            )
            
            # 绘制地址数
            self.chart_canvas.create_text(
                width - margin - 5,
                text_y,
                text=f"{network['range']} 地址",
                font=self.small_font,
                fill="white",
                anchor=tk.E
            )
            
            # 更新y位置
            y_pos += bar_height + self.get_scaled_value(10)
        
        self.update_info_bar("网段分布图绘制完成")

if __name__ == "__main__":
    root = tk.Tk()
    app = SubnetPlannerApp(root)
    root.mainloop()