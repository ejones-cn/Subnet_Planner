#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子网计算器应用程序 - 主窗口
"""

# 所有导入语句放在最顶部
import tkinter as tk
import math
import re
import ipaddress
from tkinter import ttk, filedialog, messagebox

# 导入自定义模块
from ip_subnet_calculator import split_subnet, ip_to_int, get_subnet_info, suggest_subnet_planning


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

        # 创建标签栏容器，使用ttk.Frame并继承默认样式
        self.tab_bar_container = ttk.Frame(self)
        self.tab_bar_container.pack(side="top", fill="x")

        # 创建标签栏 - 使用ttk.Frame并继承默认样式
        self.tab_bar = ttk.Frame(self.tab_bar_container)
        self.tab_bar.pack(side="left", fill="y")

        # 创建一个占位Frame，使用ttk.Frame并继承默认样式
        self.tab_bar_spacer = ttk.Frame(self.tab_bar_container)
        self.tab_bar_spacer.pack(side="left", fill="both", expand=True)

        # 创建内容区域 - 移除箭头指向的灰色框线
        self.content_area = ttk.Frame(self, borderwidth=0, relief="flat")
        self.content_area.pack(side="top", fill="both", expand=True, padx=0, pady=0)
        
        # 确保content_area能完全填充笔记本控件的空间
        self.content_area.pack_propagate(True)
        self.content_area.grid_propagate(True)
  
        # 标签配置
        self.tabs = []
        self.active_tab = None
    
    def get_tab_bar_container(self):
        """获取标签栏容器"""
        return self.tab_bar_container
    
    def get_tab_bar_right_buttons(self):
        """获取右侧按钮容器"""
        return self.tab_bar_right_buttons
        
    def get_light_blue_style(self):
        """获取浅蓝色样式名称"""
        return self.light_blue_style
        
    def get_light_green_style(self):
        """获取浅绿色样式名称"""
        return self.light_green_style
        
    def get_light_orange_style(self):
        """获取浅橙色样式名称"""
        return self.light_orange_style
        
    def get_light_purple_style(self):
        """获取浅紫色样式名称"""
        return self.light_purple_style
    
    def get_light_pink_style(self):
        """获取淡粉色样式名称"""
        return self.light_pink_style
    
    def on_configure(self, event):
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
            
            # 更新背景色以匹配result_frame
            self._update_background_to_result_frame_color()

    def _update_background_color(self):
        """更新标签栏背景色以匹配父容器"""
        # 获取标签栏容器的父组件（result_frame）的背景色
        # 由于ttk组件的背景色获取方式与tk组件不同，我们需要特殊处理
        try:
            # 使用self.master获取父容器对象
            if hasattr(self.master, "winfo_bg"):
                bg_color = self.master.winfo_bg()
            else:
                # 如果是ttk组件，尝试使用style.lookup获取背景色
                bg_color = self.style.lookup(self.master.winfo_class(), "background")

            # 如果获取的是系统默认颜色名称，转换为实际颜色值
            if not bg_color or bg_color.startswith("system."):
                bg_color = self.winfo_toplevel().cget("bg")

        except Exception as e:
            # 如果获取失败，尝试获取窗口背景色作为备选
            bg_color = self.winfo_toplevel().cget("bg")

        # 将背景色应用到所有相关组件
        self.tab_bar_container.config(bg=bg_color)
        self.tab_bar.config(bg=bg_color)
        self.tab_bar_spacer.config(bg=bg_color)

    def _on_tab_mouse_down(self, button, color):
        """当鼠标按下标签页时，更新内容区域背景色为按下状态颜色"""
        # 只有当前按下的标签页是激活标签页时才更新内容区域背景色
        if hasattr(self, "active_tab") and button.tab_index == self.active_tab:
            # 根据标签颜色设置内容区域背景色为按下状态颜色（使用之前的激活颜色，较暗）
            if color == "#e3f2fd":  # 蓝色标签
                active_color = "#bbdefb"  # 按下状态颜色（较暗）
                self.style.configure(self.light_blue_style, background=active_color)
            elif color == "#e8f5e9":  # 绿色标签
                active_color = "#c8e6c9"  # 按下状态颜色（较暗）
                self.style.configure(self.light_green_style, background=active_color)
            elif color == "#fff3e0":  # 橙色标签
                active_color = "#ffe0b2"  # 按下状态颜色（较暗）
                self.style.configure(self.light_orange_style, background=active_color)
            elif color == "#f3e5f5":  # 紫色标签
                active_color = "#e1bee7"  # 按下状态颜色（较暗）
                self.style.configure(self.light_purple_style, background=active_color)
            elif color == "#fce4ec":  # 粉色标签
                active_color = "#f8bbd0"  # 按下状态颜色（较暗）
                self.style.configure(self.light_pink_style, background=active_color)
            elif color == "#e0f2f1":  # 青色标签
                active_color = "#b2dfdb"  # 按下状态颜色（较暗）
                self.style.configure(self.light_blue_style, background=active_color)

    def _on_tab_mouse_up(self, button, color):
        """当鼠标释放标签页时，恢复内容区域背景色为激活状态颜色"""
        # 只有当前释放的标签页是激活标签页时才更新内容区域背景色
        if hasattr(self, "active_tab") and button.tab_index == self.active_tab:
            # 根据标签颜色设置内容区域背景色为激活状态颜色（使用更亮的颜色）
            if color == "#e3f2fd":  # 蓝色标签
                active_color = "#90caf9"  # 激活状态颜色（更亮）
                self.style.configure(self.light_blue_style, background=active_color)
            elif color == "#e8f5e9":  # 绿色标签
                active_color = "#a5d6a7"  # 激活状态颜色（更亮）
                self.style.configure(self.light_green_style, background=active_color)
            elif color == "#fff3e0":  # 橙色标签
                active_color = "#ffcc80"  # 激活状态颜色（更亮）
                self.style.configure(self.light_orange_style, background=active_color)
            elif color == "#f3e5f5":  # 紫色标签
                active_color = "#ce93d8"  # 激活状态颜色（更亮）
                self.style.configure(self.light_purple_style, background=active_color)
            elif color == "#fce4ec":  # 粉色标签
                active_color = "#f48fb1"  # 激活状态颜色（更亮）
                self.style.configure(self.light_pink_style, background=active_color)
            elif color == "#e0f2f1":  # 青色标签
                active_color = "#80deea"  # 激活状态颜色（更亮）
                self.style.configure(self.light_blue_style, background=active_color)

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
                    except:
                        continue
            
            # 如果无法从子组件获取背景色，尝试直接从父容器获取
            if not bg_color or bg_color.startswith("system."):
                try:
                    bg_color = self.master.cget("background")
                except:
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

        except Exception as e:
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
            "width": 10  # 设置固定宽度，确保所有标签宽度一致
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
            if color == "#e3f2fd":  # 蓝色标签
                button_params["activebackground"] = "#bbdefb"  # 之前的激活状态颜色
            elif color == "#e8f5e9":  # 绿色标签
                button_params["activebackground"] = "#c8e6c9"  # 之前的激活状态颜色
            elif color == "#fff3e0":  # 橙色标签
                button_params["activebackground"] = "#ffe0b2"  # 之前的激活状态颜色
            elif color == "#f3e5f5":  # 紫色标签
                button_params["activebackground"] = "#e1bee7"  # 之前的激活状态颜色
            elif color == "#fce4ec":  # 粉色标签
                button_params["activebackground"] = "#f8bbd0"  # 之前的激活状态颜色
            elif color == "#e0f2f1":  # 青色标签
                button_params["activebackground"] = "#b2dfdb"  # 之前的激活状态颜色
            else:  # 默认
                button_params["activebackground"] = "#e1bee7"  # 之前的激活状态颜色
            button_params["activeforeground"] = "#333333"  # 深灰色文字
        
        button = tk.Button(self.tab_bar, **button_params)
        
        # 保存按钮对应的标签索引和颜色信息，以便在事件处理中使用
        button.tab_index = len(self.tabs)
        button.tab_color = color
        
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
        
        # 更新背景色以匹配result_frame
        self._update_background_to_result_frame_color()

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
                foreground="#000000"  # 黑色文字
            )
        else:
            # 内部标签页激活状态：使用更亮的颜色（之前的鼠标按下颜色）
            if selected_tab["color"] == "#e3f2fd":  # 蓝色标签
                selected_color = "#90caf9"  # 更亮的颜色
            elif selected_tab["color"] == "#e8f5e9":  # 绿色标签
                selected_color = "#a5d6a7"  # 更亮的颜色
            elif selected_tab["color"] == "#fff3e0":  # 橙色标签
                selected_color = "#ffcc80"  # 更亮的颜色
            elif selected_tab["color"] == "#f3e5f5":  # 紫色标签
                selected_color = "#ce93d8"  # 更亮的颜色
            elif selected_tab["color"] == "#fce4ec":  # 粉色标签
                selected_color = "#f48fb1"  # 更亮的颜色
            elif selected_tab["color"] == "#e0f2f1":  # 青色标签
                selected_color = "#80deea"  # 更亮的颜色
            else:  # 默认
                selected_color = "#ce93d8"  # 更亮的颜色

            selected_tab["button"].config(
                relief="flat", bg=selected_color, font=("微软雅黑", 10, "bold"), foreground="#000000"
            )

        # 更新对应内容框架样式的背景色，使其与选中标签的颜色保持一致
        # 只有内部标签页需要更新样式，顶级标签页不需要
        if not self.is_top_level:
            if selected_tab["color"] == "#e3f2fd":  # 蓝色标签
                self.style.configure(self.light_blue_style, background=selected_color)
            elif selected_tab["color"] == "#e8f5e9":  # 绿色标签
                self.style.configure(self.light_green_style, background=selected_color)
            elif selected_tab["color"] == "#fff3e0":  # 橙色标签
                self.style.configure(self.light_orange_style, background=selected_color)
            elif selected_tab["color"] == "#f3e5f5":  # 紫色标签
                self.style.configure(self.light_purple_style, background=selected_color)
            elif selected_tab["color"] == "#fce4ec":  # 粉色标签
                self.style.configure(self.light_pink_style, background=selected_color)

        self.active_tab = tab_index

        # 更新背景色以匹配result_frame
        self._update_background_to_result_frame_color()

        # 调用标签页切换回调函数
        if self.tab_change_callback:
            self.tab_change_callback(tab_index)

    def add(self, frame, text=""):
        """模拟ttk.Notebook的add方法"""
        # 这里我们不使用这个方法，而是使用add_tab方法
        pass


class IPSubnetSplitterApp:
    def validate_split_cidr(self, text):
        text = text.strip()
        if not text:
            self.split_entry.config(style='Valid.TEntry')
            return True
        try:
            ipaddress.IPv4Network(text, strict=False)
            self.split_entry.config(style='Valid.TEntry')
            return True
        except ImportError:
            # 回退到正则表达式验证
            cidr_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/([0-9]|[1-2][0-9]|3[0-2])$'
            is_valid = bool(re.match(cidr_pattern, text))
            self.split_entry.config(foreground='black' if is_valid else 'red')
            return "1"
        except ValueError:
            self.split_entry.config(style='Invalid.TEntry')
            return False

    def __init__(self, root):
        # 创建自定义样式
        self.style = ttk.Style()
        self.style.configure('Valid.TEntry', foreground='black')
        self.style.configure('Invalid.TEntry', foreground='red')
        # 导入版本管理模块
        import sys
        import os

        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from version import get_version

        # 应用程序信息
        self.app_name = "IP子网切分工具"
        self.app_version = get_version()
        
        # CIDR格式验证正则表达式
        self.cidr_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/([0-9]|[1-2][0-9]|3[0-2])$'

        self.root = root
        self.root.title(f"IP子网切分工具 v{self.app_version}")
        # 所有窗口大小、位置和限制设置都由主程序入口统一管理
        # 这里只设置窗口标题

        # 设置样式
        self.style = ttk.Style()

        # 检查当前主题
        current_theme = self.style.theme_use()

        # 添加更详细的调试信息
        try:
            # 获取当前可用的主题
            available_themes = self.style.theme_names()
            # 尝试设置为clam主题（这个主题通常支持更多自定义样式）
            self.style.theme_use("clam")
            # 验证主题是否设置成功
            current_theme = self.style.theme_use()
        except Exception as e:
            pass

        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TButton", font=("微软雅黑", 10), focuscolor="#888888", focuswidth=1)
        self.style.configure("TEntry", font=("微软雅黑", 10))

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
            # 设置Notebook的基本样式，使用更细的边框
            self.style.configure("TNotebook", background="#ffffff", borderwidth=1, relief="groove")

            # 使用更细的边框，确保区域分割清晰但不突兀
            self.style.configure("TLabelframe", borderwidth=1, relief="groove")
            # 增大LabelFrame标题的字体大小
            self.style.configure(
                "TLabelframe.Label", borderwidth=0, relief="flat", font=("微软雅黑", 12)
            )

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
                font=[("selected", ("微软雅黑", 10, "bold")), ("!selected", ("微软雅黑", 10, "normal"))]  # 选中时加粗，非选中时正常
            )  # 非选中时的文字颜色

            # 绿色标签样式 - 剩余网段列表
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
                font=[("selected", ("微软雅黑", 10, "bold")), ("!selected", ("微软雅黑", 10, "normal"))]  # 选中时加粗，非选中时正常
            )  # 非选中时的文字颜色

            # 紫色标签样式 - 网段分布图表
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
                font=[("selected", ("微软雅黑", 10, "bold")), ("!selected", ("微软雅黑", 10, "normal"))]  # 选中时加粗，非选中时正常
            )  # 非选中时的文字颜色

            # 添加内容框架样式，使内容区域颜色与激活标签保持一致
            self.style.configure("LightBlue.TFrame", background="#f5f9ff")  # 更浅的蓝色背景
            self.style.configure("LightGreen.TFrame", background="#f5fff7")  # 更浅的绿色背景
            self.style.configure("LightPurple.TFrame", background="#fcf5ff")  # 更浅的紫色背景

            print("标签样式设置完成")

        except Exception as e:
            pass

        # 为不同标签页的内容区域设置不同的背景色
        self.style.configure("LightBlue.TFrame", background="#e3f2fd")  # 浅蓝色 - 切分网段信息
        self.style.configure("LightGreen.TFrame", background="#e8f5e9")  # 浅绿色 - 剩余网段列表
        self.style.configure("LightPurple.TFrame", background="#f3e5f5")  # 浅紫色 - 网段分布图表

        # 为Treeview添加表格线样式配置 - Windows系统专用解决方案
        # 在Windows上强制显示表格线的最终解决方案
        
        # 使用最基本、最兼容的样式设置
        # 在Windows系统上，简单的样式设置反而更可靠
        
        # 1. 基础Treeview样式设置 - 修复表格线显示问题
        # 将background设置为与偶数行相同的颜色，这样当没有足够的行时，
        # 背景色看起来就像是斑马条纹的延续，解决斑马条纹不能充满空白区域的问题
        self.style.configure(
            "TTreeview",
            background="#e0e0e0",  # 设置与偶数行相同的背景色
            fieldbackground="#ffffff",  # 单元格背景设为白色
            foreground="black",  # 文本颜色
            rowheight=28,  # 行高
            padding=(1, 1),  # 1px内边距，让边框显示
            bordercolor="#c0c0c0",
            borderwidth=1
        )
        
        # 2. 表头样式设置
        self.style.configure(
            "TTreeview.Heading",
            background="#1976d2",
            foreground="white",
            font=("微软雅黑", 10, "bold"),
            padding=(5, 3)
        )

        # 3. 选中状态设置
        self.style.map(
            "TTreeview",
            background=[("selected", "#2196f3")],
            foreground=[("selected", "white")]
        )

        # 4. 输入框样式配置 - 用于CIDR验证颜色反馈
        self.style.configure("Valid.TEntry", foreground="black")
        self.style.configure("Invalid.TEntry", foreground="red")

        # 5. 斑马条纹样式配置
        # 在Treeview中通过标签(tags)实现斑马条纹效果
        # 注意：ttk.Style不直接支持斑马条纹，需要在插入行时使用tags
        print("Treeview表格线样式设置完成")

        # 先在右上角添加关于链接按钮，确保它显示在标题栏右侧
        self.create_about_link()

        # 创建主框架 - 调整内边距使其更加紧凑
        self.main_frame = ttk.Frame(root, padding="15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 再次提升关于链接的层级，确保在主框架之上
        self.about_label.lift()

        # 创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块
        self.create_top_level_notebook()

        # 初始化图表数据
        self.chart_data = None



    def validate_parent_cidr(self, text):
        text = text.strip()
        is_valid = bool(re.match(self.cidr_pattern, text)) if text else True
        self.parent_entry.config(foreground='black' if is_valid else 'red')
        return "1"

    def validate_split_cidr_local(self, text):
        text = text.strip()
        is_valid = bool(re.match(self.cidr_pattern, text)) if text else True
        self.split_entry.config(foreground='black' if is_valid else 'red')
        return "1"

    def create_split_input_section(self):
        """创建子网切分功能的输入区域"""
        input_frame = ttk.LabelFrame(self.split_main_container, text="输入参数", padding="10")  # 减小内边距
        input_frame.pack(fill=tk.X, pady=(0, 8))  # 减少底部外边距

        # 父网段
        ttk.Label(input_frame, text="父网段", anchor="w", width=6).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=(0, 5)
        )
        def validate_cidr(text, entry):
            is_valid = bool(re.match(self.cidr_pattern, text)) if text else True
            if is_valid:
                entry.config(foreground='black')
            else:
                entry.config(foreground='red')
            return is_valid

        vcmd = (self.root.register(lambda p: validate_cidr(p, self.parent_entry)), '%P')
        self.parent_entry = ttk.Entry(input_frame, width=32, font=("微软雅黑", 10),
            validate='focusout', validatecommand=vcmd)
        self.parent_entry.grid(row=0, column=1, padx=0, pady=5, sticky=tk.W)
        self.parent_entry.insert(0, "10.0.0.0/8")  # 默认值

        # 切分段
        ttk.Label(input_frame, text="切分段", anchor="w", width=6).grid(
            row=1, column=0, sticky=tk.W, pady=3, padx=(0, 5)
        )
        vcmd = (self.root.register(lambda p: self.validate_split_cidr_local(p)), '%P')
        self.split_entry = ttk.Entry(input_frame, width=32, font=("微软雅黑", 10),
            validate='focusout', validatecommand=vcmd)
        self.split_entry.grid(row=1, column=1, padx=0, pady=3, sticky=tk.W)
        self.split_entry.insert(0, "10.21.60.0/23")  # 默认值

        # 按钮区域
        # 执行按钮
        self.execute_btn = ttk.Button(
            input_frame, text="执行切分", command=self.execute_split, width=12
        )
        self.execute_btn.grid(
            row=0, column=2, padx=(15, 8), pady=5, sticky=tk.N + tk.S + tk.E + tk.W
        )

        # 清空按钮
        self.clear_btn = ttk.Button(
            input_frame, text="清空结果", command=self.clear_result, width=12
        )
        self.clear_btn.grid(row=1, column=2, padx=(15, 8), pady=3, sticky=tk.N + tk.S + tk.E + tk.W)

        # 导出按钮 - 调整高度，使其与执行切分和清空结果按钮总的显示高度一致
        self.export_btn = ttk.Button(
            input_frame, text="导出结果", command=self.export_result, width=14
        )
        self.export_btn.grid(
            row=0, column=3, rowspan=2, padx=(0, 0), pady=(5, 3), sticky=tk.N + tk.S + tk.E + tk.W
        )

    def create_button_section(self):
        """创建按钮区域 (已合并到输入区域中)"""
        pass

    def adjust_remaining_tree_width(self):
        """调整剩余网段列表表格的宽度，使其自适应窗口大小"""
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
        # 如果切换到剩余网段列表标签页（索引为1），触发表格自适应
        if tab_index == 1:
            # 确保界面更新后再调整宽度
            self.remaining_tree.update_idletasks()
            # 调用完整的表格宽度调整方法
            self.adjust_remaining_tree_width()
        # 如果切换到网段分布图表标签页（索引为2），触发图表自适应
        elif tab_index == 2:
            # 确保图表Canvas已初始化再绘制
            if hasattr(self, 'chart_canvas'):
                self.draw_distribution_chart()

    def create_top_level_notebook(self):
        """创建顶级标签页控件，用于切换子网切分和子网规划两大功能模块"""
        # 创建一个自定义的笔记本控件来显示不同的功能模块
        self.top_level_notebook = ColoredNotebook(
            self.main_frame, style=self.style, is_top_level=True
        )
        self.top_level_notebook.pack(fill=tk.BOTH, expand=True)

        # 子网切分模块 - 使用默认样式以继承主窗体底色
        self.split_frame = ttk.Frame(
            self.top_level_notebook.content_area
        )
        
        # 添加一个完全占满页面的主容器，与子网规划页面一致的内边距
        self.split_main_container = ttk.Frame(self.split_frame, padding="10")
        self.split_main_container.pack(fill=tk.BOTH, expand=True)

        # 创建子网切分功能的输入区域
        self.create_split_input_section()

        # 创建子网切分功能的结果区域
        self.create_split_result_section()

        # 子网规划模块
        self.planning_frame = ttk.Frame(
            self.top_level_notebook.content_area, style=self.top_level_notebook.get_light_pink_style()
        )

        # 设置子网规划功能的界面
        self.setup_planning_page()

        # 添加顶级标签页 - 使用不同颜色
        self.top_level_notebook.add_tab("子网切分", self.split_frame, "#fff3e0")  # 浅橙色
        self.top_level_notebook.add_tab("子网规划", self.planning_frame, "#fce4ec")  # 淡粉色



    def create_split_result_section(self):
        """创建子网切分功能的结果显示区域"""
        result_frame = ttk.LabelFrame(self.split_main_container, text="切分结果", padding="10")
        # 调整底部外边距，将结果区域与窗体下边距缩小
        result_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 0), pady=(0, 5))

        # 创建一个自定义的笔记本控件来显示不同的结果页面
        self.notebook = ColoredNotebook(
            result_frame, style=self.style, tab_change_callback=self.on_tab_change
        )
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 切分网段信息页面
        self.split_info_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_blue_style()
        )

        # 创建切分网段信息表格
        self.split_tree = ttk.Treeview(
            self.split_info_frame, columns=("item", "value"), show="headings", height=5
        )
        self.split_tree.heading("item", text="项目")
        self.split_tree.heading("value", text="值")
        # 设置合适的列宽
        self.split_tree.column("item", width=100, minwidth=100, stretch=False)
        self.split_tree.column("value", width=250)
        self.split_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 配置斑马条纹样式和信息标签样式
        self.configure_treeview_styles(self.split_tree, include_special_tags=True)

        # 剩余网段列表页面
        self.remaining_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_green_style()
        )

        # 创建剩余网段信息表格
        self.remaining_tree = ttk.Treeview(
            self.remaining_frame,
            columns=("index", "cidr", "network", "netmask", "wildcard", "broadcast", "usable"),
            show="headings",
            height=5
        )
        self.remaining_tree.heading("index", text="序号")
        self.remaining_tree.heading("cidr", text="CIDR")
        self.remaining_tree.heading("network", text="网络地址")
        self.remaining_tree.heading("netmask", text="子网掩码")
        self.remaining_tree.heading("wildcard", text="通配符掩码")
        self.remaining_tree.heading("broadcast", text="广播地址")
        self.remaining_tree.heading("usable", text="可用地址数")

        # 设置列宽，使用minwidth替代width，让列可以自适应
        self.remaining_tree.column("index", minwidth=35, width=35, stretch=False)
        self.remaining_tree.column("cidr", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("network", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("netmask", minwidth=100, width=120, stretch=True)
        self.remaining_tree.column("wildcard", minwidth=100, width=120, stretch=True)
        
        # 配置斑马条纹样式
        self.configure_treeview_styles(self.remaining_tree)

        # 网段分布图表页面
        self.chart_frame = ttk.Frame(
            self.notebook.content_area, padding="5", style=self.notebook.get_light_purple_style()
        )

        # 添加标签页，每个标签页设置不同的颜色
        self.notebook.add_tab("切分网段信息", self.split_info_frame, "#e3f2fd")  # 浅蓝色
        self.notebook.add_tab("剩余网段列表", self.remaining_frame, "#e8f5e9")  # 浅绿色
        self.notebook.add_tab("网段分布图表", self.chart_frame, "#f3e5f5")  # 浅紫色

        # 创建滚动容器
        scroll_frame = ttk.Frame(self.chart_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        # 添加滚动条
        self.chart_scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL)
        self.chart_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 创建Canvas用于绘制柱状图，移除pady边距以避免显示灰色背景
        self.chart_canvas = tk.Canvas(
            scroll_frame, bg="white", yscrollcommand=self.chart_scrollbar.set
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True, pady=0)

        # 配置滚动条
        self.chart_scrollbar.config(command=self.chart_canvas.yview)

        # 绑定窗口大小变化事件，实现图表自适应
        self.chart_canvas.bind("<Configure>", self.on_chart_resize)
        # 绑定鼠标滚轮事件
        self.chart_canvas.bind("<MouseWheel>", self.on_chart_mousewheel)
        self.chart_frame.bind("<Enter>", lambda e: self.chart_canvas.focus_set())

        # 调整列宽，确保所有列都能完整显示并自适应窗口宽度
        self.remaining_tree.column("broadcast", minwidth=100, width=130, stretch=True)
        self.remaining_tree.column("usable", minwidth=100, width=110, stretch=True)

        # 添加垂直滚动条
        self.remaining_scroll_v = ttk.Scrollbar(
            self.remaining_frame, orient=tk.VERTICAL, command=self.remaining_tree.yview
        )
        self.remaining_tree.configure(yscrollcommand=self.remaining_scroll_v.set)

        # 设置布局：Treeview在左，垂直滚动条在右，都填满整个可用空间
        self.remaining_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=5)
        self.remaining_scroll_v.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # 绑定窗口大小变化事件，实现表格自适应
        self.root.bind("<Configure>", self.on_window_resize)

        # 初始提示
        self.clear_result()
        
        # Treeview表格线样式已在初始化时设置
        
        # 在窗口完全渲染后再调用动态计算方法，确保获取准确的高度
        self.root.after(100, self.initial_table_setup)

    def setup_planning_page(self):
        """设置子网规划功能的界面"""
        # 创建主框架
        main_planning_frame = ttk.Frame(self.planning_frame, padding="10")
        main_planning_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # 父网段输入区域
        parent_frame = ttk.LabelFrame(main_planning_frame, text="父网段设置", padding="10")
        parent_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        ttk.Label(parent_frame, text="父网段 (CIDR格式):").pack(side=tk.LEFT, padx=(0, 10))
        vcmd = (self.root.register(lambda p: validate_cidr(p, self.planning_parent_entry)), '%P')
        self.planning_parent_entry = ttk.Entry(parent_frame, width=20,
            validate='focusout', validatecommand=vcmd)
        self.planning_parent_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.planning_parent_entry.insert(0, "10.21.48.0/20")  # 默认值
        


        # 子网需求区域
        requirements_frame = ttk.LabelFrame(main_planning_frame, text="子网需求", padding="10")
        requirements_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))  # 改为垂直和水平填充，允许扩展

        # 内部容器框架，用于组织表格和按钮
        inner_frame = ttk.Frame(requirements_frame)
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置grid布局
        inner_frame.grid_rowconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(0, weight=1)
        inner_frame.grid_columnconfigure(1, weight=0)
        inner_frame.grid_columnconfigure(2, weight=0)

        # 子网需求表格
        self.requirements_tree = ttk.Treeview(
            inner_frame, columns=("index", "name", "hosts"), show="headings", height=5  # 设置为5行高度，添加序号列
        )
        self.requirements_tree.heading("index", text="序号")
        self.requirements_tree.heading("name", text="子网名称")
        self.requirements_tree.heading("hosts", text="主机数量")
        # 字段宽度设置
        self.requirements_tree.column("index", width=50, minwidth=50, stretch=False)
        self.requirements_tree.column("name", width=125, minwidth=100, stretch=True)
        self.requirements_tree.column("hosts", width=125, minwidth=100, stretch=True)
        
        # 绑定双击事件以实现编辑功能
        self.requirements_tree.bind("<Double-1>", self.on_requirements_tree_double_click)
        
        # 放置表格
        self.requirements_tree.grid(row=0, column=0, sticky="nsew", padx=(0, 0))

        # 添加滚动条，确保只作用于表格
        requirements_scrollbar = ttk.Scrollbar(
            inner_frame, orient=tk.VERTICAL, command=self.requirements_tree.yview
        )
        self.requirements_tree.configure(yscroll=requirements_scrollbar.set)
        
        # 放置滚动条
        requirements_scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 10))

        # 子网需求操作按钮框架
        button_frame = ttk.Frame(inner_frame)
        button_frame.grid(row=0, column=2, sticky="nsew")
        # 设置按钮框架的最小宽度，确保两个按钮大小一致
        button_frame.configure(width=70)
        
        # 按钮框架内部布局
        button_frame.grid_rowconfigure(0, weight=0)
        button_frame.grid_rowconfigure(1, weight=0)
        button_frame.grid_rowconfigure(2, weight=1)  # 中间空白区域，用于将执行按钮推到底部
        button_frame.grid_rowconfigure(3, weight=0)
        button_frame.grid_columnconfigure(0, weight=1)

        # 添加按钮
        add_btn = ttk.Button(button_frame, text="添加", command=self.add_subnet_requirement)
        add_btn.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # 删除按钮
        delete_btn = ttk.Button(button_frame, text="删除", command=self.delete_subnet_requirement)
        delete_btn.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # 空白填充
        ttk.Frame(button_frame).grid(row=2, column=0, sticky="nsew")
        
        # 执行子网规划按钮，位于底部
        self.execute_planning_btn = ttk.Button(
            button_frame, text="规划子网", command=self.execute_subnet_planning
        )
        self.execute_planning_btn.grid(row=3, column=0, sticky="ew", pady=(0, 0))

        # 添加示例数据 - 带斑马条纹标签
        # 先插入不带序号的数据
        self.requirements_tree.insert("", tk.END, values=("", "办公区", "200"), tags=("odd",))
        self.requirements_tree.insert("", tk.END, values=("", "服务器区", "50"), tags=("even",))
        self.requirements_tree.insert("", tk.END, values=("", "研发部", "100"), tags=("odd",))
        # 调用方法更新序号
        self.update_requirements_tree_zebra_stripes()
        
        # 配置斑马条纹样式
        self.configure_treeview_styles(self.requirements_tree)

        # 删除原来的执行规划按钮容器
        # 按钮已移动到删除按钮下方

        # 规划结果区域
        result_frame = ttk.LabelFrame(main_planning_frame, text="规划结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # 创建笔记本控件显示规划结果
        self.planning_notebook = ColoredNotebook(result_frame, style=self.style)
        self.planning_notebook.pack(fill=tk.BOTH, expand=True)

        # 导出规划按钮 - 使用 place 布局手动控制位置
        export_planning_btn = ttk.Button(
            result_frame, text="导出规划", command=self.export_planning_result
        )
        # 手动指定按钮位置：右上角，距离右边0像素，距离顶部-3像素
        export_planning_btn.place(relx=1.0, rely=0.0, anchor=tk.NE, x=0, y=-3)

        # 已分配子网页面
        self.allocated_frame = ttk.Frame(
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.get_light_blue_style()
        )
        self.allocated_tree = ttk.Treeview(
            self.allocated_frame,
            columns=("index", "name", "cidr", "required", "available", "network", "netmask", "broadcast"),
            show="headings",
            height=5  # 设置为5行高度
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
        self.allocated_tree.column("index", width=0, minwidth=10, stretch=True)  # 序号列自动宽度
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
        
        # 配置表格使用滚动条（仅垂直）
        self.allocated_tree.configure(
            yscrollcommand=allocated_v_scrollbar.set
        )

        # 重新布局表格和滚动条，使用grid布局实现自适应
        self.allocated_frame.grid_rowconfigure(0, weight=1)
        self.allocated_frame.grid_columnconfigure(0, weight=1)
        
        self.allocated_tree.grid(row=0, column=0, sticky="nsew")
        allocated_v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置斑马条纹样式
        self.configure_treeview_styles(self.allocated_tree)

        # 剩余网段页面
        self.planning_remaining_frame = ttk.Frame(
            self.planning_notebook.content_area, padding="5", style=self.planning_notebook.get_light_green_style()
        )
        self.planning_remaining_tree = ttk.Treeview(
            self.planning_remaining_frame,
            columns=(
                "index", "cidr", "network", "netmask", "broadcast", "usable"
            ),
            show="headings",
            height=5  # 设置为5行高度
        )

        # 设置列标题
        self.planning_remaining_tree.heading("index", text="序号")
        self.planning_remaining_tree.heading("cidr", text="CIDR")
        self.planning_remaining_tree.heading("network", text="网络地址")
        self.planning_remaining_tree.heading("netmask", text="子网掩码")
        self.planning_remaining_tree.heading("broadcast", text="广播地址")
        self.planning_remaining_tree.heading("usable", text="可用地址数")

        # 设置列宽，所有列都启用拉伸以实现自适应
        self.planning_remaining_tree.column("index", width=40, minwidth=30, stretch=True)
        self.planning_remaining_tree.column("cidr", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("network", width=80, minwidth=70, stretch=True)  # 调小网络地址列宽并启用拉伸
        self.planning_remaining_tree.column("netmask", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("broadcast", width=120, minwidth=100, stretch=True)
        self.planning_remaining_tree.column("usable", width=80, minwidth=60, stretch=True)

        # 添加垂直滚动条
        remaining_v_scrollbar = ttk.Scrollbar(
            self.planning_remaining_frame,
            orient=tk.VERTICAL,
            command=self.planning_remaining_tree.yview,
        )
        
        # 配置表格使用滚动条（仅垂直）
        self.planning_remaining_tree.configure(
            yscrollcommand=remaining_v_scrollbar.set
        )

        # 重新布局表格和滚动条，使用grid布局实现自适应
        self.planning_remaining_frame.grid_rowconfigure(0, weight=1)
        self.planning_remaining_frame.grid_columnconfigure(0, weight=1)
        
        self.planning_remaining_tree.grid(row=0, column=0, sticky="nsew")
        remaining_v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 配置斑马条纹样式
        self.configure_treeview_styles(self.planning_remaining_tree)

        # 添加标签页 - 使用与切分结果一致的颜色
        self.planning_notebook.add_tab("已分配子网", self.allocated_frame, "#e3f2fd")  # 浅蓝色
        self.planning_notebook.add_tab(
            "剩余网段", self.planning_remaining_frame, "#e8f5e9"
        )  # 浅绿色
        
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
        except Exception as e:
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
            
            # 如果需要，配置错误和信息标签
            if include_special_tags:
                tree.tag_configure("error", foreground="red")
                tree.tag_configure("info", foreground="blue")
        except Exception as e:
            # 如果发生错误，不影响程序运行
            pass

    def update_table_zebra_stripes(self, tree):
        """更新表格的斑马条纹标签（仅更新行标签，不重新配置样式）
        
        Args:
            tree: 要处理的Treeview对象
        """
        try:
            # 只更新行标签，样式已在初始化时配置
            for index, item in enumerate(tree.get_children(), start=1):
                tag = "even" if index % 2 == 0 else "odd"
                current_tags = tree.item(item, "tags")
                if tag not in current_tags:
                    tree.item(item, tags=(tag,))
        except Exception as e:
            # 如果发生错误，不影响程序运行
            pass
    
    def auto_resize_columns(self, tree):
        """自动调整表格列宽以适应内容
        
        Args:
            tree: 要调整列宽的Treeview对象
        """
        # 创建一个临时标签用于测量文本宽度（使用默认字体或从root获取字体）
        temp_label = tk.Label(self.root)
        
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
            '大小': 80
        }
        
        # 调整列宽以适应表头
        for col in tree['columns']:
            # 获取表头文本
            header = tree.heading(col, 'text')
            
            # 设置临时标签文本并测量宽度
            temp_label.config(text=header)
            header_width = temp_label.winfo_reqwidth() + 20  # 增加一些边距
            
            # 获取列中内容的最大宽度
            max_width = header_width
            for item in tree.get_children():
                value = tree.item(item, 'values')
                if value and len(value) > list(tree['columns']).index(col):
                    cell_value = str(value[list(tree['columns']).index(col)])
                    # 设置临时标签文本并测量宽度
                    temp_label.config(text=cell_value)
                    cell_width = temp_label.winfo_reqwidth() + 20  # 增加一些边距
                    if cell_width > max_width:
                        max_width = cell_width
            
            # 应用默认最小宽度，如果计算出的宽度小于默认值
            if header in default_min_widths and max_width < default_min_widths[header]:
                max_width = default_min_widths[header]
            
            # 设置列宽
            tree.column(col, width=max_width, stretch=True)
        
        # 销毁临时标签
        temp_label.destroy()
    
    def resize_tables(self):
        """调整表格列宽以适应容器大小并更新空行数"""
        try:
            # 动态更新所有表格的空行数
            if hasattr(self, 'split_tree'):
                self.update_table_zebra_stripes(self.split_tree)
            if hasattr(self, 'remaining_tree'):
                self.update_table_zebra_stripes(self.remaining_tree)
            if hasattr(self, 'allocated_tree'):
                self.update_table_zebra_stripes(self.allocated_tree)
            if hasattr(self, 'planning_remaining_tree'):
                self.update_table_zebra_stripes(self.planning_remaining_tree)
                
            # 仅调整规划结果区域的表格列宽，不影响子网需求区域
            if hasattr(self, 'planning_notebook') and hasattr(self.planning_notebook, 'content_area'):
                # 调整已分配子网表格，根据内容自动调整列宽
                if hasattr(self, 'allocated_tree'):
                    self.auto_resize_columns(self.allocated_tree)
                
                # 调整剩余网段表格，根据内容自动调整列宽
                if hasattr(self, 'planning_remaining_tree'):
                    self.auto_resize_columns(self.planning_remaining_tree)
        except Exception as e:
            # 忽略调整过程中的错误
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

        # 计算居中位置（相对于主窗口，不包含标题栏）
        window_width = 320
        window_height = 220
        # 获取主窗口的位置和尺寸
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        # 计算对话框的居中位置（不包含主窗口标题栏）
        # 通常标题栏高度约为30像素，可以调整
        title_bar_height = 30
        x = root_x + (root_width - window_width) // 2
        y = root_y + title_bar_height + (root_height - title_bar_height - window_height) // 2
        
        # 一次性设置对话框的尺寸和位置
        temp_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
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
        # 添加回车绑定
        name_entry.bind("<Return>", lambda event: save_requirement())
        # 自动获得焦点，方便直接输入
        name_entry.focus_set()

        # 主机数量 - 标签在中间列左侧，输入框在中间列右侧
        ttk.Label(main_frame, text="主机数量:").grid(row=1, column=1, sticky=tk.E, pady=15, padx=(10, 10))
        hosts_var = tk.StringVar()
        hosts_entry = ttk.Entry(main_frame, textvariable=hosts_var, width=20)
        hosts_entry.grid(row=1, column=2, sticky=tk.W, pady=15, padx=(0, 10))
        # 添加回车绑定
        hosts_entry.bind("<Return>", lambda event: save_requirement())

        # 按钮框架 - 横跨所有列，确保按钮组居中
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=20)

        def save_requirement():
            """保存子网需求"""
            name = name_var.get().strip()
            hosts = hosts_var.get().strip()

            if not name:
                messagebox.showerror("错误", "请输入子网名称")
                return

            if not hosts.isdigit() or int(hosts) <= 0:
                messagebox.showerror("错误", "请输入有效的主机数量")
                return

            # 添加到表格 - 带斑马条纹标签
            # 获取当前表格中的行数，计算新行的索引（从1开始）
            current_rows = len(self.requirements_tree.get_children())
            new_index = current_rows + 1
            tag = "even" if new_index % 2 == 0 else "odd"
            self.requirements_tree.insert("", tk.END, values=(new_index, name, hosts), tags=(tag,))
            
            # 重新应用所有行的斑马条纹，确保一致性
            self.update_requirements_tree_zebra_stripes()
            
            temp_window.destroy()

        # 创建按钮并在按钮框架中居中
        save_button = ttk.Button(button_frame, text="保存", command=save_requirement, width=10)
        cancel_button = ttk.Button(button_frame, text="取消", command=temp_window.destroy, width=10)
        
        # 使用pack布局让按钮在按钮框架中居中显示
        save_button.pack(side=tk.LEFT, padx=(0, 15))
        cancel_button.pack(side=tk.LEFT)

    def delete_subnet_requirement(self):
        """删除选中的子网需求，并重新应用斑马条纹"""
        selected_items = self.requirements_tree.selection()
        if not selected_items:
            messagebox.showwarning("提示", "请先选择要删除的子网需求")
            return

        for item in selected_items:
            self.requirements_tree.delete(item)
        
        # 删除后重新应用斑马条纹
        self.update_requirements_tree_zebra_stripes()
    
    def update_requirements_tree_zebra_stripes(self):
        """更新子网需求表的斑马条纹和序号"""
        for index, item in enumerate(self.requirements_tree.get_children(), start=1):
            tag = "even" if index % 2 == 0 else "odd"
            # 获取当前行的值
            values = list(self.requirements_tree.item(item, "values"))
            # 更新序号
            values[0] = index
            # 设置新的值和标签
            self.requirements_tree.item(item, values=values, tags=(tag,))
    
    def on_requirements_tree_double_click(self, event):
        """双击Treeview单元格时触发编辑功能"""
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
        self.edit_entry = ttk.Entry(self.requirements_tree, width=width//10)  # 估算字符宽度
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # 放置编辑框在单元格上
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        
        # 保存当前编辑的信息
        self.current_edit_item = item
        self.current_edit_column = column_name
        self.current_edit_column_index = column_index
        
        # 绑定事件
        self.edit_entry.bind("<FocusOut>", self.on_edit_focus_out)
        self.edit_entry.bind("<Return>", self.on_edit_enter)
        self.edit_entry.bind("<Escape>", self.on_edit_escape)    
    
    def on_edit_focus_out(self, event):
        """编辑框失去焦点时保存数据"""
        self.save_edit()
    
    def on_edit_enter(self, event):
        """按下Enter键时保存数据"""
        self.save_edit()
    
    def on_edit_escape(self, event):
        """按下Escape键时取消编辑"""
        self.edit_entry.destroy()
        del self.current_edit_item
        del self.current_edit_column
        del self.current_edit_column_index
    
    def save_edit(self):
        """保存编辑的数据"""
        if hasattr(self, 'current_edit_item'):
            # 获取新值
            new_value = self.edit_entry.get().strip()
            
            # 验证数据
            if not new_value:
                messagebox.showerror("错误", "输入不能为空")
                return
            
            if self.current_edit_column == "hosts":
                try:
                    hosts = int(new_value)
                    if hosts <= 0:
                        messagebox.showerror("错误", "主机数量必须大于0")
                        return
                except ValueError:
                    messagebox.showerror("错误", "主机数量必须是整数")
                    return
            
            # 更新Treeview数据
            values = list(self.requirements_tree.item(self.current_edit_item, "values"))
            values[self.current_edit_column_index] = new_value
            self.requirements_tree.item(self.current_edit_item, values=values)
            
            # 销毁编辑框
            self.edit_entry.destroy()
            
            # 清理临时属性
            del self.current_edit_item
            del self.current_edit_column
            del self.current_edit_column_index

    def execute_subnet_planning(self):
        """执行子网规划"""
        global re
        # 获取父网段
        parent_cidr = self.planning_parent_entry.get().strip()
        if not parent_cidr:
            messagebox.showerror("错误", "请输入父网段")
            return

        if not re.match(self.cidr_pattern, parent_cidr):
            messagebox.showerror("错误", "父网段格式不正确，请输入有效的CIDR格式（例如：192.168.1.0/24）")
            return

        # 获取子网需求
        subnet_requirements = []
        for item in self.requirements_tree.get_children():
            values = self.requirements_tree.item(item, "values")
            subnet_requirements.append((values[1], int(values[2])))

        if not subnet_requirements:
            messagebox.showerror("错误", "请添加至少一个子网需求")
            return

        try:
            # 执行子网规划
            # 转换子网需求格式以匹配函数参数要求
            formatted_requirements = [{'name': name, 'hosts': hosts} for name, hosts in subnet_requirements]
            
            # 调用子网规划函数
            plan_result = suggest_subnet_planning(parent_cidr, formatted_requirements)
            
            # 检查是否有错误
            if 'error' in plan_result:
                messagebox.showerror("错误", f"子网规划失败: {plan_result['error']}")
                return

            # 清空结果表格
            for item in self.allocated_tree.get_children():
                self.allocated_tree.delete(item)

            for item in self.planning_remaining_tree.get_children():
                self.planning_remaining_tree.delete(item)

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
                    tags=tags
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
                        plan_result['remaining_subnets'][i-1],
                        subnet["network"],
                        subnet["netmask"],
                        subnet["broadcast"],
                        subnet["usable_addresses"],  # 修正为正确的字段名
                    ),
                    tags=tags
                )
            # 斑马条纹样式已在初始化时配置
            
            # 数据添加完成后，自动调整列宽以适应内容
            self.auto_resize_columns(self.planning_remaining_tree)

            # 子网规划完成，不显示对话框提示

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
            messagebox.showerror("错误", message)
        except Exception as e:
            messagebox.showerror("错误", f"子网规划失败: 发生未知错误 - {str(e)}")

    def execute_split(self):
        """执行切分操作"""
        global re
        parent = self.parent_entry.get().strip()
        split = self.split_entry.get().strip()

        # 验证输入
        if not parent or not split:
            # 清空表格并显示错误信息
            self.clear_result()
            self.split_tree.delete(*self.split_tree.get_children())
            self.split_tree.insert(
                "", tk.END, values=("错误", "父网段和切分网段都不能为空！"), tags=("error",)
            )
            return

        # 验证CIDR格式
        if not re.match(self.cidr_pattern, parent):
            self.clear_result()
            self.split_tree.delete(*self.split_tree.get_children())
            self.split_tree.insert(
                "", tk.END, values=("错误", "父网段格式无效，请输入有效的CIDR格式！"), tags=("error",)
            )
            messagebox.showerror("输入错误", "父网段格式无效，请输入有效的CIDR格式（如: 10.0.0.0/8）")
            return
        if not re.match(self.cidr_pattern, split):
            self.clear_result()
            self.split_tree.delete(*self.split_tree.get_children())
            self.split_tree.insert(
                "", tk.END, values=("错误", "切分网段格式无效，请输入有效的CIDR格式！"), tags=("error",)
            )
            messagebox.showerror("输入错误", "切分网段格式无效，请输入有效的CIDR格式（如: 10.21.60.0/23）")
            return

        try:
            # 调用切分函数
            result = split_subnet(parent, split)

            # 清空现有结果
            for item in self.split_tree.get_children():
                self.split_tree.delete(item)
            for item in self.remaining_tree.get_children():
                self.remaining_tree.delete(item)

            if "error" in result:
                # 显示错误信息
                self.split_tree.delete(*self.split_tree.get_children())
                self.split_tree.insert(
                    "", tk.END, values=("错误", result["error"]), tags=("error",)
                )
                return

            # 显示切分网段信息表格
            self.split_tree.delete(*self.split_tree.get_children())
            
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
            self.split_tree.insert(
                "", tk.END, values=("总地址数", split_info["num_addresses"]), tags=("even",)
            )
            self.split_tree.insert(
                "", tk.END, values=("可用地址数", split_info["usable_addresses"]), tags=("odd",)
            )
            self.split_tree.insert("", tk.END, values=("前缀长度", split_info["prefixlen"]), tags=("even",))
            self.split_tree.insert("", tk.END, values=("CIDR", split_info["cidr"]), tags=("odd",))
            


            # 显示剩余网段列表表格
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
                        tags=tags
                    )

            else:
                self.remaining_tree.insert("", tk.END, values=(1, "无", "无", "无", "无", "无"))

            # 让表格自适应窗口宽度
            self.adjust_remaining_tree_width()

            # 准备图表数据
            self.prepare_chart_data(result, split_info, result["remaining_subnets_info"])

            # 绘制图表
            self.draw_distribution_chart()

        except ValueError as e:
            error_msg = str(e)
            if "not permitted" in error_msg and "Octet" in error_msg:
                import re
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

    def show_result(self, text, error=False, keep_data=False):
        """显示结果"""
        # 只有在不保留数据且显示错误信息时才清空表格
        if not keep_data and error:
            self.clear_result()

        # 在切分网段表格中显示信息
        if error:
            self.split_tree.insert("", tk.END, values=("错误", text), tags=("error",))
        else:
            self.split_tree.insert("", tk.END, values=("信息", text), tags=("info",))

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
            for i, subnet in enumerate(remaining_subnets):
                subnet_start = ip_to_int(subnet.get("network", "0.0.0.0"))
                subnet_end = ip_to_int(subnet.get("broadcast", "0.0.0.0"))
                self.chart_data["networks"].append(
                    {
                        "start": subnet_start,
                        "end": subnet_end,
                        "range": subnet_end - subnet_start + 1,
                        "name": subnet.get("cidr", ""),
                        "color": colors[i % len(colors)],  # 循环使用颜色
                        "type": "remaining",
                    }
                )

            # 按起始地址排序
            self.chart_data["networks"].sort(key=lambda x: x["start"])
        except Exception as e:
            # 如果出现任何错误，就不绘制图表
            self.chart_data = None

    def on_chart_resize(self, event):
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
        stroke="#000000",
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
            stroke: 描边颜色（为了兼容性保留此参数）
            stroke_width: 描边宽度（为了兼容性保留此参数）
            letter_spacing: 字间距（为了兼容性保留此参数）
        """
        try:
            # 使用4个方向的基础描边，平衡性能和可读性
            stroke_color = "#000000"
            offset = 1  # 描边偏移量

            # 绘制4个方向的描边
            self.chart_canvas.create_text(
                x - offset, y, text=text, font=font, anchor=anchor, fill=stroke_color
            )
            self.chart_canvas.create_text(
                x + offset, y, text=text, font=font, anchor=anchor, fill=stroke_color
            )
            self.chart_canvas.create_text(
                x, y - offset, text=text, font=font, anchor=anchor, fill=stroke_color
            )
            self.chart_canvas.create_text(
                x, y + offset, text=text, font=font, anchor=anchor, fill=stroke_color
            )

            # 绘制主文字
            self.chart_canvas.create_text(x, y, text=text, font=font, anchor=anchor, fill=fill)
        except Exception as e:
            # 出错时直接绘制文字，不添加描边
            self.chart_canvas.create_text(x, y, text=text, font=font, anchor=anchor, fill=fill)

    def draw_text_without_stroke(self, text, x, y, font, anchor=tk.W, fill="#ffffff"):
        """高效绘制不带描边的文字

        Args:
            text: 要绘制的文字
            x: 起始x坐标
            y: 起始y坐标
            font: 字体设置
            anchor: 文字锚点
            fill: 文字颜色
        """
        # 直接绘制文字，不添加描边
        self.chart_canvas.create_text(x, y, text=text, font=font, anchor=anchor, fill=fill)

    def draw_distribution_chart(self):
        """绘制网段分布柱状图 - 参考Web版本的呈现方式"""
        # 检查chart_data属性是否存在且不为None
        if not hasattr(self, 'chart_data') or not self.chart_data:
            return

        try:
            # 清空Canvas
            self.chart_canvas.delete("all")

            # 获取Canvas尺寸
            width = self.chart_canvas.winfo_width()
            canvas_height = self.chart_canvas.winfo_height()

            # 如果Canvas还没有渲染完成，使用默认尺寸
            if width < 10:
                width = self.chart_frame.winfo_width() - 30  # 使用父框架宽度减去边距
            if canvas_height < 10:
                canvas_height = 400

            # 设置边距（参考Web版布局）
            margin_left = 50
            margin_right = 80
            margin_top = 50
            margin_bottom = 80

            # 计算可用绘图区域宽度
            chart_width = width - margin_left - margin_right

            # 获取父网段信息
            parent_info = self.chart_data.get("parent", {})
            parent_cidr = parent_info.get("name", "")
            parent_range = parent_info.get("range", 1)

            # 获取网段列表
            networks = self.chart_data.get("networks", [])
            if not networks:
                # 没有网段时显示提示
                self.chart_canvas.create_text(
                    width / 2, canvas_height / 2, text="无网段数据", font=("微软雅黑", 12)
                )
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
            self.chart_canvas.create_rectangle(
                0, 0, width, background_height, fill="#333333", outline="", width=0
            )

            # 设置Canvas滚动区域
            self.chart_canvas.config(scrollregion=(0, 0, width, background_height))

            # 绘制父网段
            parent_range = parent_info.get("range", 1)
            log_value = max(log_min, math.log10(parent_range))
            bar_width = max(
                min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width
            )

            # 绘制父网段条（使用明显的深灰色）
            color = "#636e72"  # 明显的深灰色
            self.chart_canvas.create_rectangle(
                x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0
            )

            # 绘制父网段信息
            usable_addresses = parent_range - 2 if parent_range > 2 else parent_range

            # 网段信息 - 使用带描边的文字绘制，提高可见度
            segment_text = f"父网段: {parent_cidr}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = ("微软雅黑", 11, "bold")  # 使用粗体提高可读性
            # 使用带描边的文字绘制方法
            self.draw_text_with_stroke(
                segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff"
            )

            # 可用地址数 - 使用带描边的文字绘制，提高可见度
            address_text = f"可用地址数: {usable_addresses:,}"
            text_x = x + 250
            # 使用带描边的文字绘制方法
            self.draw_text_with_stroke(
                address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff"
            )

            y += bar_height + padding

            # 绘制切分网段
            split_networks = [net for net in networks if net.get("type") == "split"]
            for i, network in enumerate(split_networks):
                # 使用对数比例尺计算宽度（参考Web版）
                network_range = network.get("range", 1)
                log_value = max(log_min, math.log10(network_range))
                bar_width = max(
                    min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width
                )

                # 绘制切分网段条（明显的蓝色）
                color = "#4a7eb4"  # 明显的蓝色
                self.chart_canvas.create_rectangle(
                    x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0
                )

                # 绘制网段信息（参考Web版布局）
                name = network.get("name", "")
                usable_addresses = network_range - 2 if network_range > 2 else network_range

                # 网段信息 - 使用带描边的文字绘制，提高可见度
                segment_text = f"切分网段: {name}"
                text_x = x + 15
                text_y = y + bar_height / 2
                font = ("微软雅黑", 11, "bold")  # 使用粗体提高可读性
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(
                    segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff"
                )

                # 可用地址数 - 使用带描边的文字绘制，提高可见度
                address_text = f"可用地址数: {usable_addresses:,}"
                text_x = x + 250
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(
                    address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff"
                )

                y += bar_height + padding

                # 添加切分网段和剩余网段之间的虚线分割
                self.chart_canvas.create_line(
                    x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1
                )

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
                bar_width = max(
                    min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width
                )

                # 为每个剩余网段选择不同颜色（参考Web版）
                color_index = i % len(subnet_colors)
                color = subnet_colors[color_index]

                # 绘制剩余网段条
                self.chart_canvas.create_rectangle(
                    x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0
                )

                # 绘制网段信息
                name = network.get("name", "")
                usable_addresses = network_range - 2 if network_range > 2 else network_range

                # 网段信息 - 使用带描边的文字绘制，提高可见度
                segment_text = f"网段 {i + 1}: {name}"
                text_x = x + 15
                text_y = y + bar_height / 2
                font = ("微软雅黑", 9, "bold")  # 使用粗体提高可读性
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(
                    segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff"
                )

                # 可用地址数 - 使用带描边的文字绘制，提高可见度
                address_text = f"可用地址数: {usable_addresses:,}"
                text_x = x + 250
                # 使用带描边的文字绘制方法
                self.draw_text_with_stroke(
                    address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff"
                )

                y += bar_height + padding

            # 添加剩余网段和图例之间的虚线分割
            self.chart_canvas.create_line(
                x, y, x + chart_width, y, fill="#cccccc", dash=(5, 2), width=1
            )

            # 绘制图例（参考Web版）
            legend_y = y + 15
            self.chart_canvas.create_text(
                x, legend_y, text="图例:", font=("微软雅黑", 11), anchor=tk.W, fill="#ffffff"
            )

            # 增加图例文字与图例图形之间的间距
            legend_items_y = legend_y + 25

            # 父网段图例
            self.chart_canvas.create_rectangle(
                x, legend_items_y, x + 20, legend_items_y + 15, fill="#636e72"
            )
            self.chart_canvas.create_text(
                x + 30,
                legend_items_y + 6,
                text="父网段",
                font=("微软雅黑", 9),
                anchor=tk.W,
                fill="#ffffff",
            )

            # 切分网段图例
            self.chart_canvas.create_rectangle(
                x + 100, legend_items_y, x + 120, legend_items_y + 12, fill="#4a7eb4"
            )
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

    def on_window_resize(self, event):
        """窗口大小变化时的处理函数，实现表格和图表自适应"""
        # 确保表格能够自适应窗口宽度
        self.remaining_tree.update_idletasks()
        self.adjust_remaining_tree_width()
        
        # 窗口大小变化时不需要重新配置斑马条纹，样式已在初始化时设置
        # 图表将在 on_chart_resize 中单独处理，避免重复绘制
        # 重新绘制所有Treeview的表格线 - 使用ttk样式方案不需要手动绘制


    
    def export_result(self):
        """导出结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
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
                title="保存子网切分结果",
                initialdir="",
            )

            if not file_path:
                return  # 用户取消了保存

            # 获取文件扩展名
            import os

            file_ext = os.path.splitext(file_path)[1].lower()

            # 准备数据
            split_data = []
            for item in self.split_tree.get_children():
                values = self.split_tree.item(item, "values")
                if values[0] not in ["提示", "错误", "-", "切分网段信息", "剩余网段信息"]:
                    split_data.append(values)

            remaining_data = []
            headers = [
                self.remaining_tree.heading(col, "text") for col in self.remaining_tree["columns"]
            ]
            for item in self.remaining_tree.get_children():
                values = self.remaining_tree.item(item, "values")
                if values:
                    remaining_data.append(dict(zip(headers, values)))

            # 根据文件扩展名选择导出格式
            if file_ext == ".json":
                # JSON格式导出
                import json

                export_data = {"split_info": dict(split_data), "remaining_subnets": remaining_data}
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

            elif file_ext == ".txt":
                # 文本格式导出
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("切分网段信息\n")
                    f.write("=" * 50 + "\n")
                    for item in self.split_tree.get_children():
                        values = self.split_tree.item(item, "values")
                        f.write(f"{values[0]:<20}: {values[1]}\n")

                    f.write("\n\n剩余网段信息\n")
                    f.write("=" * 50 + "\n")

                    # 写入列标题
                    for header in headers:
                        f.write(f"{header:<15}")
                    f.write("\n")
                    f.write("-" * 50 + "\n")

                    # 写入数据
                    for item in self.remaining_tree.get_children():
                        values = self.remaining_tree.item(item, "values")
                        for value in values:
                            f.write(f"{str(value):<15}")
                        f.write("\n")

            elif file_ext == ".pdf":
                # PDF格式导出
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Table,
                    TableStyle,
                    Paragraph,
                    Spacer,
                    PageBreak,
                )
                from reportlab.lib import colors
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                from reportlab.lib.units import cm
                from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
                import os
                import sys
                import time

                # 注册中文字体函数
                # 注册中文字体
                self.has_chinese_font = self.register_chinese_fonts()

                # 创建PDF文档，设置页边距
                page_width, page_height = A4
                margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)  # 左、右、上、下
                doc = SimpleDocTemplate(
                    file_path, 
                    pagesize=A4,
                    leftMargin=margins[0],
                    rightMargin=margins[1],
                    topMargin=margins[2],
                    bottomMargin=margins[3],
                    showBoundary=False
                )
                elements = []
                styles = getSampleStyleSheet()

                # 创建支持中文的标题样式
                title_style = ParagraphStyle(
                    "ChineseTitle",
                    parent=styles["Title"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica-Bold",
                    fontSize=20,
                    textColor=colors.HexColor("#2c3e50"),  # 深蓝灰色
                    alignment=TA_CENTER,  # 居中对齐
                    spaceAfter=20,
                )

                # 创建支持中文的一级标题样式
                heading2_style = ParagraphStyle(
                    "ChineseHeading2",
                    parent=styles["Heading2"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica-Bold",
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
                    fontName="ChineseFont" if has_chinese_font else "Helvetica",
                    fontSize=11,
                    textColor=colors.HexColor("#34495e"),  # 深灰色
                    spaceAfter=5,
                )

                # 创建支持中文的表格文本样式
                table_text_style = ParagraphStyle(
                    "ChineseTableText",
                    parent=styles["Normal"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica",
                    fontSize=10,
                    alignment=TA_CENTER,  # 居中对齐
                )

                # 添加标题
                elements.append(Paragraph("IP子网分割工具 - 计算结果", title_style))
                elements.append(Spacer(1, 10))

                # 添加导出时间信息
                export_time = time.strftime("%Y年%m月%d日 %H:%M:%S")
                elements.append(Paragraph(f"导出时间: {export_time}", normal_style))
                elements.append(Spacer(1, 15))

                # 添加切分网段信息
                elements.append(Paragraph("切分网段信息", heading2_style))
                split_table_data = [["项目", "值"]]
                for item in self.split_tree.get_children():
                    values = self.split_tree.item(item, "values")
                    if values[0] not in ["提示", "错误", "-", "切分网段信息", "剩余网段信息"]:
                        # 将表格中的中文文本用Paragraph包裹，使用支持中文的样式
                        split_table_data.append([
                            Paragraph(values[0], table_text_style),
                            Paragraph(values[1], table_text_style)
                        ])

                if len(split_table_data) > 1:
                    # 计算表格宽度（页宽减去左右边距）
                    table_width = page_width - margins[0] - margins[1]
                    # 设置列宽比例（项目列占30%，值列占70%）
                    col_widths = [table_width * 0.3, table_width * 0.7]
                    
                    split_table = Table(split_table_data, colWidths=col_widths)
                    split_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),  # 蓝色表头
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (0, -1), "LEFT"),  # 第一列左对齐
                                ("ALIGN", (1, 0), (-1, -1), "CENTER"),  # 其他列居中对齐
                                ("FONTNAME", (0, 0), (-1, 0), "ChineseFont" if has_chinese_font else "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 12),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("TOPPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3498db")),  # 蓝色外框
                                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),  # 交替行颜色
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 垂直居中
                                ("LEFTPADDING", (0, 0), (-1, -1), 10),  # 左内边距
                                ("RIGHTPADDING", (0, 0), (-1, -1), 10),  # 右内边距
                                ("TOPPADDING", (0, 1), (-1, -1), 6),  # 上内边距
                                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),  # 下内边距
                            ]
                        )
                    )
                    elements.append(split_table)
                else:
                    elements.append(Paragraph("无切分网段信息", normal_style))

                elements.append(Spacer(1, 20))

                # 添加剩余网段信息
                elements.append(Paragraph("剩余网段信息", heading2_style))
                
                # 调整表格文本样式，使用更小的字号以避免内容分行
                small_table_text_style = ParagraphStyle(
                    "ChineseSmallTableText",
                    parent=styles["Normal"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica",
                    fontSize=9,  # 稍微减小字号
                    alignment=TA_CENTER,  # 居中对齐
                )
                
                # 使用新的小字号样式创建表格数据
                remaining_table_data = [[Paragraph(h, small_table_text_style) for h in headers]]
                for item in self.remaining_tree.get_children():
                    values = self.remaining_tree.item(item, "values")
                    if values:
                        # 将表格中的中文文本用Paragraph包裹，使用支持中文的样式
                        remaining_table_data.append([
                            Paragraph(str(v), small_table_text_style) for v in values
                        ])

                if len(remaining_table_data) > 1:
                    # 计算表格宽度（页宽减去左右边距）
                    table_width = page_width - margins[0] - margins[1]
                    # 调整列宽：序号和可用地址数列宽度调小，其他列适当分配
                    # 序号列: 40pt, CIDR: 80pt, 网络地址: 80pt, 子网掩码: 100pt, 通配符掩码: 90pt, 广播地址: 80pt, 可用地址数: 50pt
                    col_widths = [40, 80, 80, 100, 90, 80, 50]
                    
                    remaining_table = Table(remaining_table_data, colWidths=col_widths)
                    remaining_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),  # 绿色表头
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 所有列居中对齐
                                ("FONTNAME", (0, 0), (-1, 0), "ChineseFont" if has_chinese_font else "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 11),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("TOPPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#27ae60")),  # 绿色外框
                                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),  # 交替行颜色
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
                    elements.append(Paragraph("无剩余网段信息", styles["Normal"]))

                # 生成PDF，添加页脚
                doc.build(elements, onFirstPage=self.add_footer, onLaterPages=self.add_footer)

            elif file_ext == ".xlsx":
                # Excel格式导出
                from openpyxl import Workbook
                from openpyxl.styles import Font, Alignment

                # 创建Excel工作簿
                wb = Workbook()

                # 添加切分网段信息工作表
                ws1 = wb.active
                ws1.title = "切分网段信息"

                # 添加切分网段表头
                ws1.append(["项目", "值"])

                # 设置表头样式
                for cell in ws1[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加切分网段数据
                for item in self.split_tree.get_children():
                    values = self.split_tree.item(item, "values")
                    if values[0] not in ["提示", "错误", "-", "切分网段信息", "剩余网段信息"]:
                        ws1.append(list(values))

                # 调整列宽
                ws1.column_dimensions["A"].width = 20
                ws1.column_dimensions["B"].width = 50

                # 添加剩余网段信息工作表
                ws2 = wb.create_sheet(title="剩余网段信息")

                # 添加剩余网段表头
                ws2.append(headers)

                # 设置表头样式
                for cell in ws2[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加剩余网段数据
                for item in self.remaining_tree.get_children():
                    values = self.remaining_tree.item(item, "values")
                    if values:
                        ws2.append([str(v) for v in values])

                # 调整列宽
                for col, header in enumerate(headers, 1):
                    ws2.column_dimensions[chr(64 + col)].width = 20

                # 保存Excel文件
                wb.save(file_path)

            else:  # 默认CSV格式
                # CSV格式导出，使用utf-8-sig编码解决中文乱码问题
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    # 写入切分网段信息
                    f.write("切分网段信息,\n")
                    f.write("项目,值\n")

                    for item in self.split_tree.get_children():
                        values = self.split_tree.item(item, "values")
                        f.write(",".join(map(str, values)) + "\n")

                    # 写入一个空行作为分隔
                    f.write("\n")

                    # 写入剩余网段信息
                    f.write("剩余网段信息,\n")

                    # 获取剩余网段表格的列标题
                    headers = [
                        self.remaining_tree.heading(col, "text")
                        for col in self.remaining_tree["columns"]
                    ]
                    f.write(",".join(headers) + "\n")

                    for item in self.remaining_tree.get_children():
                        values = self.remaining_tree.item(item, "values")
                        f.write(",".join(map(str, values)) + "\n")

            # 显示导出成功信息，保留原有数据
            self.show_result(f"结果已成功导出到: {file_path}", keep_data=True)

        except Exception as e:
            # 显示导出错误信息
            self.show_result(f"导出失败: {str(e)}", error=True)

    def export_planning_result(self):
        """导出子网规划结果为多种格式（CSV、JSON、TXT、PDF、Excel）"""
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
                title="保存子网规划结果",
                initialdir="",
            )

            if not file_path:
                return  # 用户取消了保存

            # 获取文件扩展名
            import os

            file_ext = os.path.splitext(file_path)[1].lower()

            # 准备数据
            # 获取已分配子网的列标题
            allocated_headers = [
                self.allocated_tree.heading(col, "text") for col in self.allocated_tree["columns"]
            ]
            allocated_data = []
            for item in self.allocated_tree.get_children():
                values = self.allocated_tree.item(item, "values")
                if values:
                    allocated_data.append(dict(zip(allocated_headers, values)))

            # 获取剩余网段的列标题
            remaining_headers = [
                self.planning_remaining_tree.heading(col, "text") for col in self.planning_remaining_tree["columns"]
            ]
            remaining_data = []
            for item in self.planning_remaining_tree.get_children():
                values = self.planning_remaining_tree.item(item, "values")
                if values:
                    remaining_data.append(dict(zip(remaining_headers, values)))

            # 根据文件扩展名选择导出格式
            if file_ext == ".json":
                # JSON格式导出
                import json

                export_data = {
                    "allocated_subnets": allocated_data,
                    "remaining_subnets": remaining_data
                }
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)

            elif file_ext == ".txt":
                # 文本格式导出
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("已分配子网信息\n")
                    f.write("=" * 80 + "\n")

                    # 写入已分配子网列标题
                    for header in allocated_headers:
                        f.write(f"{header:<15}")
                    f.write("\n")
                    f.write("-" * 80 + "\n")

                    # 写入已分配子网数据
                    for item in self.allocated_tree.get_children():
                        values = self.allocated_tree.item(item, "values")
                        for value in values:
                            f.write(f"{str(value):<15}")
                        f.write("\n")

                    f.write("\n\n剩余网段信息\n")
                    f.write("=" * 80 + "\n")

                    # 写入剩余网段列标题
                    for header in remaining_headers:
                        f.write(f"{header:<15}")
                    f.write("\n")
                    f.write("-" * 80 + "\n")

                    # 写入剩余网段数据
                    for item in self.planning_remaining_tree.get_children():
                        values = self.planning_remaining_tree.item(item, "values")
                        for value in values:
                            f.write(f"{str(value):<15}")
                        f.write("\n")

            elif file_ext == ".pdf":
                # PDF格式导出
                from reportlab.lib.pagesizes import A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import (
                    SimpleDocTemplate,
                    Table,
                    TableStyle,
                    Paragraph,
                    Spacer,
                    PageBreak,
                )
                from reportlab.lib import colors
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                from reportlab.lib.units import cm
                from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
                import sys
                import time

                # 注册中文字体函数
                # 注册中文字体
                self.has_chinese_font = self.register_chinese_fonts()

                # 创建PDF文档，设置页边距
                page_width, page_height = A4
                margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)  # 左、右、上、下
                doc = SimpleDocTemplate(
                    file_path, 
                    pagesize=A4,
                    leftMargin=margins[0],
                    rightMargin=margins[1],
                    topMargin=margins[2],
                    bottomMargin=margins[3],
                    showBoundary=False
                )
                elements = []
                styles = getSampleStyleSheet()

                # 创建支持中文的标题样式
                title_style = ParagraphStyle(
                    "ChineseTitle",
                    parent=styles["Title"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica-Bold",
                    fontSize=20,
                    textColor=colors.HexColor("#2c3e50"),  # 深蓝灰色
                    alignment=TA_CENTER,  # 居中对齐
                    spaceAfter=20,
                )

                # 创建支持中文的一级标题样式
                heading2_style = ParagraphStyle(
                    "ChineseHeading2",
                    parent=styles["Heading2"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica-Bold",
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
                    fontName="ChineseFont" if has_chinese_font else "Helvetica",
                    fontSize=11,
                    textColor=colors.HexColor("#34495e"),  # 深灰色
                    spaceAfter=5,
                )

                # 创建支持中文的表格文本样式
                table_text_style = ParagraphStyle(
                    "ChineseTableText",
                    parent=styles["Normal"],
                    fontName="ChineseFont" if has_chinese_font else "Helvetica",
                    fontSize=10,
                    alignment=TA_CENTER,  # 居中对齐
                )

                # 添加标题
                elements.append(Paragraph("IP子网分割工具 - 子网规划结果", title_style))
                elements.append(Spacer(1, 10))

                # 添加导出时间信息
                export_time = time.strftime("%Y年%m月%d日 %H:%M:%S")
                elements.append(Paragraph(f"导出时间: {export_time}", normal_style))
                elements.append(Spacer(1, 15))

                # 添加已分配子网信息
                elements.append(Paragraph("已分配子网信息", heading2_style))
                allocated_table_data = [[Paragraph(h, table_text_style) for h in allocated_headers]]
                for item in self.allocated_tree.get_children():
                    values = self.allocated_tree.item(item, "values")
                    if values:
                        # 将表格中的中文文本用Paragraph包裹，使用支持中文的样式
                        allocated_table_data.append([
                            Paragraph(str(v), table_text_style) for v in values
                        ])

                if len(allocated_table_data) > 1:
                    # 计算表格宽度（页宽减去左右边距）
                    table_width = page_width - margins[0] - margins[1]
                    # 根据数据长度调整各列宽度，避免换行
                    # 序号 | 子网名称 | CIDR | 需求数 | 可用数 | 网络地址 | 子网掩码 | 广播地址
                    col_widths = [10, 100, 90, 30, 40, 80, 110, 80]  # 单位：pt (序号列宽10pt, 需求数列宽30pt, 可用数列宽40pt)
                    
                    allocated_table = Table(allocated_table_data, colWidths=col_widths)
                    allocated_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),  # 蓝色表头
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 所有列居中对齐
                                ("FONTNAME", (0, 0), (-1, 0), "ChineseFont" if has_chinese_font else "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 11),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("TOPPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3498db")),  # 蓝色外框
                                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),  # 交替行颜色
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # 垂直居中
                                ("LEFTPADDING", (0, 0), (-1, -1), 8),  # 左内边距
                                ("RIGHTPADDING", (0, 0), (-1, -1), 8),  # 右内边距
                                ("TOPPADDING", (0, 1), (-1, -1), 6),  # 上内边距
                                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),  # 下内边距
                            ]
                        )
                    )
                    elements.append(allocated_table)
                else:
                    elements.append(Paragraph("无已分配子网信息", normal_style))

                elements.append(Spacer(1, 20))

                # 添加剩余网段信息
                elements.append(Paragraph("剩余网段信息", heading2_style))
                remaining_table_data = [[Paragraph(h, table_text_style) for h in remaining_headers]]
                for item in self.planning_remaining_tree.get_children():
                    values = self.planning_remaining_tree.item(item, "values")
                    if values:
                        # 将表格中的中文文本用Paragraph包裹，使用支持中文的样式
                        remaining_table_data.append([
                            Paragraph(str(v), table_text_style) for v in values
                        ])

                if len(remaining_table_data) > 1:
                    # 计算表格宽度（页宽减去左右边距）
                    table_width = page_width - margins[0] - margins[1]
                    # 根据数据长度调整各列宽度，避免换行
                    # 序号 | CIDR | 网络地址 | 子网掩码 | 广播地址 | 可用地址数
                    col_widths = [40, 90, 80, 110, 80, 60]  # 单位：pt (增加CIDR列宽到90pt)
                    
                    remaining_table = Table(remaining_table_data, colWidths=col_widths)
                    remaining_table.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),  # 绿色表头
                                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 所有列居中对齐
                                ("FONTNAME", (0, 0), (-1, 0), "ChineseFont" if has_chinese_font else "Helvetica-Bold"),
                                ("FONTSIZE", (0, 0), (-1, 0), 11),
                                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                ("TOPPADDING", (0, 0), (-1, 0), 8),
                                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#27ae60")),  # 绿色外框
                                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),  # 交替行颜色
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
                    elements.append(Paragraph("无剩余网段信息", normal_style))

                # 生成PDF，添加页脚
                doc.build(elements, onFirstPage=self.add_footer, onLaterPages=self.add_footer)

            elif file_ext == ".xlsx":
                # Excel格式导出
                from openpyxl import Workbook
                from openpyxl.styles import Font, Alignment

                # 创建Excel工作簿
                wb = Workbook()

                # 添加已分配子网工作表
                ws1 = wb.active
                ws1.title = "已分配子网"

                # 添加已分配子网表头
                ws1.append(allocated_headers)

                # 设置表头样式
                for cell in ws1[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加已分配子网数据
                for item in self.allocated_tree.get_children():
                    values = self.allocated_tree.item(item, "values")
                    if values:
                        ws1.append(list(values))

                # 调整列宽
                for col, header in enumerate(allocated_headers, 1):
                    ws1.column_dimensions[chr(64 + col)].width = 20

                # 添加剩余网段工作表
                ws2 = wb.create_sheet(title="剩余网段")

                # 添加剩余网段表头
                ws2.append(remaining_headers)

                # 设置表头样式
                for cell in ws2[1]:
                    cell.font = Font(bold=True)
                    cell.alignment = Alignment(horizontal="center")

                # 添加剩余网段数据
                for item in self.planning_remaining_tree.get_children():
                    values = self.planning_remaining_tree.item(item, "values")
                    if values:
                        ws2.append([str(v) for v in values])

                # 调整列宽
                for col, header in enumerate(remaining_headers, 1):
                    ws2.column_dimensions[chr(64 + col)].width = 20

                # 保存Excel文件
                wb.save(file_path)

            else:  # 默认CSV格式
                # CSV格式导出，使用utf-8-sig编码解决中文乱码问题
                with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                    # 写入已分配子网信息
                    f.write("已分配子网信息,\n")
                    f.write(",".join(allocated_headers) + "\n")

                    for item in self.allocated_tree.get_children():
                        values = self.allocated_tree.item(item, "values")
                        if values:
                            f.write(",".join(map(str, values)) + "\n")

                    # 写入一个空行作为分隔
                    f.write("\n")

                    # 写入剩余网段信息
                    f.write("剩余网段信息,\n")
                    f.write(",".join(remaining_headers) + "\n")

                    for item in self.planning_remaining_tree.get_children():
                        values = self.planning_remaining_tree.item(item, "values")
                        if values:
                            f.write(",".join(map(str, values)) + "\n")

            # 显示导出成功信息
            self.show_result(f"规划结果已成功导出到: {file_path}", keep_data=True)

        except Exception as e:
            # 显示导出错误信息
            self.show_result(f"导出失败: {str(e)}", error=True)

    def clear_result(self):
        """清空结果表格和图表"""
        # 清空切分网段信息表格
        for item in self.split_tree.get_children():
            self.split_tree.delete(item)
        # 添加提示行
        self.split_tree.insert("", tk.END, values=("提示", "点击'执行切分'按钮开始操作..."), tags=('odd',))
        # 更新切分网段表格的斑马条纹标签
        self.update_table_zebra_stripes(self.split_tree)

        # 清空剩余网段列表表格
        for item in self.remaining_tree.get_children():
            self.remaining_tree.delete(item)
        # 更新剩余网段列表的斑马条纹标签
        self.update_table_zebra_stripes(self.remaining_tree)

        # 清空图表
        self.chart_canvas.delete("all")
        self.chart_data = None

    def register_chinese_fonts(self):
        """注册中文字体供PDF导出使用"""
        # 尝试查找系统中的中文字体
        font_path = None
        font_name = None

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
                for font_file, font_family in font_candidates:
                    potential_path = os.path.join(font_dir, font_file)
                    if os.path.exists(potential_path):
                        font_path = potential_path
                        font_name = font_family
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

    def add_footer(self, canvas, doc):
        """在PDF文档中添加页脚"""
        canvas.saveState()
        # 设置页脚字体
        if getattr(self, 'has_chinese_font', False):
            canvas.setFont("ChineseFont", 9)
        else:
            canvas.setFont("Helvetica", 9)
        # 添加页脚文本
        footer_text = f"导出时间: {time.strftime('%Y-%m-%d %H:%M:%S')} | 第 {doc.page} 页"
        canvas.drawString(2.5 * cm, 1.5 * cm, footer_text)
        canvas.restoreState()

    def create_about_link(self):
        """在主窗体标题栏右侧（红框位置）创建关于链接按钮"""
        # 直接在root窗口创建关于链接，不使用框架
        # 使用普通tk.Label直接控制样式，确保悬停效果可靠
        
        # 获取窗口背景色以确保完全一致
        self.bg_color = self.root.cget("background")
        self.hover_bg_color = "#e0e0e0"  # 更浅的灰色背景，柔和过渡
        self.hover_fg_color = "#333333"  # 深灰色文字，保持可读性
        self.normal_fg_color = "#666666"
        border_color = "#cccccc"  # 更浅的灰色边框，视觉上更细
        
        # 使用普通tk.Label创建标签，直接设置所有样式属性
        self.about_label = tk.Label(
            self.root,
            text="关于……",
            font=('微软雅黑', 10, 'bold'),  # 字体加粗
            fg=self.normal_fg_color,  # 文字颜色调淡为浅灰色
            bg=self.bg_color,  # 背景色与窗口完全一致
            padx=10,  # 水平内边距
            pady=5,  # 垂直内边距
            bd=0,  # 取消默认边框
            relief="flat",  # 平坦样式
            highlightthickness=1,  # 高亮边框宽度，模拟边框
            highlightbackground=border_color,  # 边框颜色
            highlightcolor=border_color,  # 边框颜色（确保一致性）
            cursor="hand2"  # 鼠标指针为手形
        )
        
        # 放置在窗口标题栏右侧位置
        self.about_label.place(relx=1.0, rely=0.0, anchor=tk.NE, x=-30, y=15)
        self.about_label.bind("<Button-1>", lambda e: self.show_about_dialog())
        
        # 绑定鼠标事件实现悬停效果
        self.about_label.bind("<Enter>", self.on_about_link_enter)
        self.about_label.bind("<Leave>", self.on_about_link_leave)
        
    def on_about_link_enter(self, event):
        """鼠标进入关于链接时的处理函数"""
        # 直接修改标签的前景色和背景色
        self.about_label.config(fg=self.hover_fg_color, bg=self.hover_bg_color)
        
    def on_about_link_leave(self, event):
        """鼠标离开关于链接时的处理函数"""
        # 恢复标签的默认前景色和背景色
        self.about_label.config(fg=self.normal_fg_color, bg=self.bg_color)


    
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
        content_frame = ttk.Frame(
            about_window, padding=(15, 0, 15, 0), relief="flat", borderwidth=0
        )
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

    # 禁止调整窗口宽度，但允许调整高度
    root.resizable(width=False, height=True)

    # 设置窗口图标
    try:
        # 尝试加载图标文件
        # 在开发环境中，图标文件位于当前目录
        # 在打包后的程序中，使用PyInstaller的资源路径
        import os
        import sys
        import tkinter as tk

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

    # 创建应用实例
    app = IPSubnetSplitterApp(root)

    # 运行应用
    root.mainloop()
