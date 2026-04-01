#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化模块
实现网络拓扑图和IP地址分配可视化功能

模块说明：
- NetworkTopologyVisualizer: 网络拓扑可视化类，支持单一综合性网络拓扑图
- IPAllocationVisualizer: IP地址分配可视化类

使用示例：
```python
# 创建可视化器
visualizer = NetworkTopologyVisualizer(parent_frame)

# 设置数据回调函数
def get_network_data():
    # 返回网络拓扑数据
    return network_data

visualizer.set_data_callback(get_network_data)

# 绘制拓扑图
visualizer.draw_topology(network_data)

# 开始自动更新
visualizer.start_auto_update(interval=60000)  # 60秒刷新一次

# 手动刷新
visualizer.refresh_data()

# 设置过滤级别
visualizer.set_filter_level(2)  # 只显示2级及以下节点
```
"""

import tkinter as tk
from tkinter import Canvas, Frame, Scrollbar, Label, Toplevel
import math
import ipaddress
from style_manager import get_current_font_settings
from i18n import _ as translate

# 模块版本
__version__ = "1.0.0"


# 模块接口定义
class VisualizationError(Exception):
    """可视化模块异常"""
    pass


# 定义颜色常量
NODE_COLOR = "#4a7eb4"
NODE_BORDER_COLOR = "#2c3e50"
LINK_COLOR = "#7f8c8d"
TEXT_COLOR = "#ecf0f1"
BACKGROUND_COLOR = "#34495e"
HIGHLIGHT_COLOR = "#e74c3c"

# 定义节点大小
NODE_WIDTH = 150
NODE_HEIGHT = 80
NODE_SPACING = 200

# 定义网段类型颜色
SUBNET_TYPE_COLORS = {
    "default": "#4a7eb4",
    "server": "#e74c3c",
    "client": "#27ae60",
    "network": "#f39c12",
    "management": "#9b59b6"
}

# 定义设备类型形状
DEVICE_SHAPES = {
    "default": "rectangle",
    "router": "diamond",
    "switch": "ellipse",
    "server": "rectangle",
    "client": "triangle"
}


class NetworkTopologyVisualizer:
    """网络拓扑可视化类"""
    
    def __init__(self, parent):
        """初始化可视化器
        
        Args:
            parent: 父容器
        """
        self.parent = parent
        self.canvas_frame = Frame(parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        self.v_scrollbar = Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        self.h_scrollbar = Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL)
        
        # 创建画布
        self.canvas = Canvas(
            self.canvas_frame,
            bg=BACKGROUND_COLOR,
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # 配置滚动条
        self.v_scrollbar.config(command=self.canvas.yview)
        self.h_scrollbar.config(command=self.canvas.xview)
        
        # 放置组件
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 初始化数据
        self.nodes = {}
        self.links = []
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # 拖拽状态
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.last_x = 0
        self.last_y = 0
        
        # 缩放因子
        self.scale = 1.0
        
        # 节点悬停状态
        self.hovered_node = None
        self.tooltip = None
        self.tooltip_timer = None  # 延迟显示定时器
        self.last_mouse_x = 0  # 记录鼠标位置
        self.last_mouse_y = 0
        
        # 数据更新相关
        self.update_interval = 30000  # 默认30秒刷新一次
        self.update_timer = None
        self.data_callback = None
        self.auto_update = False
        
        # 性能优化相关
        self.batch_drawing = True  # 启用批量绘制
        self.max_nodes = 500  # 最大节点数
        self.filter_level = 10  # 过滤级别，0表示显示所有节点
        self.visible_nodes = set()  # 可见节点集合
        
    def start_drag(self, event):
        """开始拖拽"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.last_x = event.x
        self.last_y = event.y
    
    def drag(self, event):
        """拖拽操作"""
        if self.dragging:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.canvas.move(tk.ALL, dx, dy)
            self.last_x = event.x
            self.last_y = event.y
    
    def stop_drag(self, event):
        """停止拖拽"""
        self.dragging = False
    
    def on_mouse_wheel(self, event):
        """鼠标滚轮缩放"""
        # 计算缩放因子
        if event.delta > 0:
            new_scale = self.scale * 1.1
        else:
            new_scale = self.scale * 0.9
        
        # 限制缩放范围
        new_scale = max(0.3, min(new_scale, 3.0))
        
        # 计算缩放比例
        scale_factor = new_scale / self.scale
        self.scale = new_scale
        
        # 缩放画布内容
        self.canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)
    
    def create_node_shape(self, x, y, width, height, shape="rectangle", fill=NODE_COLOR, outline=NODE_BORDER_COLOR, border_width=2):
        """创建不同形状的节点
        
        Args:
            x: x坐标
            y: y坐标
            width: 宽度
            height: 高度
            shape: 形状类型
            fill: 填充颜色
            outline: 边框颜色
            border_width: 边框宽度
        
        Returns:
            int: 形状ID
        """
        if shape == "rectangle":
            return self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
        elif shape == "ellipse":
            return self.canvas.create_oval(
                x, y, x + width, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
        elif shape == "diamond":
            return self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height / 2,
                x + width / 2, y + height,
                x, y + height / 2,
                fill=fill,
                outline=outline,
                width=border_width
            )
        elif shape == "triangle":
            return self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height,
                x, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
        else:
            return self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
    
    def add_node(self, name, subnet, level=0, subnet_type="default", device_type="default", ip_info=None):
        """添加节点
        
        Args:
            name: 节点名称
            subnet: 子网信息
            level: 层级
            subnet_type: 网段类型
            device_type: 设备类型
            ip_info: IP地址信息
        
        Returns:
            str: 节点ID
        """
        node_id = f"node_{len(self.nodes)}"
        
        # 计算节点位置（使用分层布局）
        x = 100 + level * NODE_SPACING
        y = 100 + (len(self.nodes) % 10) * (NODE_HEIGHT + 50)
        
        # 根据网段类型获取颜色
        node_color = SUBNET_TYPE_COLORS.get(subnet_type, NODE_COLOR)
        
        # 根据设备类型获取形状
        node_shape = DEVICE_SHAPES.get(device_type, "rectangle")
        
        # 创建节点形状
        shape_id = self.create_node_shape(
            x, y, NODE_WIDTH, NODE_HEIGHT, 
            shape=node_shape, 
            fill=node_color,
            outline=NODE_BORDER_COLOR,
            border_width=2
        )
        
        # 获取字体设置
        font_family, font_size = get_current_font_settings()
        
        # 创建节点文本
        text_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT / 4,
            text=name,
            font=(font_family, font_size, "bold"),
            fill=TEXT_COLOR
        )
        
        # 创建子网文本
        subnet_text = str(subnet)
        if len(subnet_text) > 20:
            subnet_text = subnet_text[:17] + "..."
        
        subnet_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT / 2,
            text=subnet_text,
            font=(font_family, font_size - 2),
            fill=TEXT_COLOR
        )
        
        # 创建IP信息文本
        ip_info_text = ""
        if ip_info:
            total_ips = ip_info.get("total", 0)
            allocated = ip_info.get("allocated", 0)
            reserved = ip_info.get("reserved", 0)
            used_ips = allocated + reserved
            ip_info_text = f"{used_ips}/{total_ips}"
        
        ip_info_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT * 3 / 4,
            text=ip_info_text,
            font=(font_family, font_size - 3),
            fill=TEXT_COLOR
        )
        
        # 存储节点信息
        self.nodes[node_id] = {
            "id": node_id,
            "name": name,
            "subnet": subnet,
            "subnet_type": subnet_type,
            "device_type": device_type,
            "ip_info": ip_info,
            "shape": shape_id,
            "text": text_id,
            "subnet_text": subnet_id,
            "ip_info_text": ip_info_id,
            "x": x,
            "y": y,
            "level": level
        }
        
        return node_id
    
    def add_link(self, source_node_id, target_node_id):
        """添加连接
        
        Args:
            source_node_id: 源节点ID
            target_node_id: 目标节点ID
        """
        if source_node_id in self.nodes and target_node_id in self.nodes:
            source = self.nodes[source_node_id]
            target = self.nodes[target_node_id]
            
            # 计算连接线坐标
            x1 = source["x"] + NODE_WIDTH
            y1 = source["y"] + NODE_HEIGHT / 2
            x2 = target["x"]
            y2 = target["y"] + NODE_HEIGHT / 2
            
            # 创建连接线
            link_id = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=LINK_COLOR,
                width=2,
                arrow=tk.LAST
            )
            
            # 存储连接信息
            self.links.append({
                "id": link_id,
                "source": source_node_id,
                "target": target_node_id
            })
    
    def clear(self):
        """清空画布"""
        self.canvas.delete(tk.ALL)
        self.nodes = {}
        self.links = []
        self.visible_nodes = set()
        self.scale = 1.0
    
    def draw_topology(self, network_data):
        """绘制综合网络拓扑图
        
        Args:
            network_data: 网络数据，包含所有网络结构信息
        """
        self.clear()
        
        # 存储节点ID映射
        node_id_map = {}
        
        # 过滤节点
        filtered_data = self._filter_nodes(network_data)
        
        # 限制节点数量
        if len(filtered_data) > self.max_nodes:
            filtered_data = filtered_data[:self.max_nodes]
        
        # 批量绘制
        if self.batch_drawing:
            self.canvas.update_idletasks()
            self.canvas.config(scrollregion=(0, 0, 1, 1))
        
        # 遍历网络数据，构建节点和连接
        for network in filtered_data:
            # 检查节点级别是否在过滤范围内
            if network.get("level", 0) <= self.filter_level or self.filter_level == 0:
                # 添加网络节点
                node_id = self.add_node(
                    network.get("name", "Network"),
                    network.get("cidr", ""),
                    level=network.get("level", 0),
                    subnet_type=network.get("type", "default"),
                    device_type=network.get("device_type", "default"),
                    ip_info=network.get("ip_info", {})
                )
                node_id_map[network.get("id", node_id)] = node_id
                self.visible_nodes.add(node_id)
        
        # 添加连接
        for network in filtered_data:
            node_id = node_id_map.get(network.get("id"))
            if node_id and node_id in self.visible_nodes:
                for child_id in network.get("children", []):
                    if child_id in node_id_map and node_id_map[child_id] in self.visible_nodes:
                        self.add_link(node_id, node_id_map[child_id])
        
        # 批量绘制完成
        if self.batch_drawing:
            self.canvas.update_idletasks()
        
        # 更新滚动区域
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(tk.ALL)
        if bbox:
            self.canvas.config(scrollregion=bbox)
    
    def _filter_nodes(self, network_data):
        """过滤节点
        
        Args:
            network_data: 网络数据
        
        Returns:
            list: 过滤后的节点列表
        """
        # 这里可以实现更复杂的过滤逻辑
        # 例如根据节点类型、状态等进行过滤
        return network_data
    
    def set_filter_level(self, level):
        """设置过滤级别
        
        Args:
            level: 过滤级别，0表示显示所有节点，1表示只显示一级节点，以此类推
        """
        self.filter_level = level
        if self.data_callback:
            self.refresh_data()
    
    def set_max_nodes(self, max_nodes):
        """设置最大节点数
        
        Args:
            max_nodes: 最大节点数
        """
        self.max_nodes = max_nodes
        if self.data_callback:
            self.refresh_data()
    
    def on_mouse_move(self, event):
        """鼠标移动事件，用于显示节点悬停详情"""
        # 将窗口坐标转换为画布坐标（考虑滚动）
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 查找鼠标下方的节点
        hovered_node = None
        
        # 使用 find_overlapping 查找与鼠标位置重叠的所有对象
        overlapping = self.canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
        
        # 从重叠的对象中找到节点形状（从后往前，找到最上层的）
        for item_id in reversed(list(overlapping)):
            for node_id, node in self.nodes.items():
                if node["shape"] == item_id:
                    hovered_node = node
                    break
            if hovered_node:
                break
        
        # 如果悬停的节点发生变化
        if hovered_node != self.hovered_node:
            # 取消之前的定时器
            if self.tooltip_timer:
                try:
                    self.canvas.after_cancel(self.tooltip_timer)
                except Exception:
                    pass
                self.tooltip_timer = None
            
            # 隐藏之前的提示
            self.hide_tooltip()
            
            # 更新悬停状态
            self.hovered_node = hovered_node
            
            # 如果有新的悬停节点，延迟显示提示（防抖）
            if hovered_node:
                self.last_mouse_x = event.x_root
                self.last_mouse_y = event.y_root
                # 延迟 100ms 显示提示，避免频繁创建窗口
                self.tooltip_timer = self.canvas.after(100, self._delayed_show_tooltip)
    
    def _delayed_show_tooltip(self):
        """延迟显示提示窗口"""
        self.tooltip_timer = None
        if self.hovered_node:
            self.show_tooltip(self.last_mouse_x, self.last_mouse_y, self.hovered_node)
    
    def show_tooltip(self, x_root, y_root, node):
        """显示节点悬停提示
        
        Args:
            x_root: 鼠标在屏幕上的 x 坐标
            y_root: 鼠标在屏幕上的 y 坐标
            node: 节点信息
        """
        # 创建提示窗口
        self.tooltip = tk.Toplevel(self.parent)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x_root + 15}+{y_root + 10}")
        
        # 创建提示内容
        frame = tk.Frame(self.tooltip, bg="#333", padx=10, pady=5)
        frame.pack()
        
        # 获取字体设置
        font_family, font_size = get_current_font_settings()
        
        # 添加提示文本
        tk.Label(
            frame, 
            text=node["name"], 
            font=(font_family, font_size, "bold"), 
            fg="#fff", 
            bg="#333"
        ).pack(anchor=tk.W)
        
        tk.Label(
            frame, 
            text=str(node["subnet"]), 
            font=(font_family, font_size - 1), 
            fg="#ddd", 
            bg="#333"
        ).pack(anchor=tk.W)
        
        if node["ip_info"]:
            allocated = node["ip_info"].get("allocated", 0)
            reserved = node["ip_info"].get("reserved", 0)
            available = node["ip_info"].get("available", 0)
            total = node["ip_info"].get("total", 0)
            # 计算剩余IP数：总IP数 - 网络地址和广播地址 - 已分配IP - 已保留IP
            # 网络地址和广播地址各占1个IP
            network_broadcast = 2 if total > 2 else 0
            remaining = max(0, total - network_broadcast - allocated - reserved)
            tk.Label(
                frame, 
                text=f"已分配: {allocated}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"已保留: {reserved}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"已释放: {available}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"剩余IP: {remaining}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"总IP: {total}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
    
    def hide_tooltip(self):
        """隐藏提示窗口"""
        # 取消定时器
        if self.tooltip_timer:
            try:
                self.canvas.after_cancel(self.tooltip_timer)
            except Exception:
                pass
            self.tooltip_timer = None
        
        # 销毁提示窗口
        if self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None
    

    
    def set_data_callback(self, callback):
        """设置数据回调函数
        
        Args:
            callback: 数据回调函数，返回网络拓扑数据
        """
        self.data_callback = callback
    
    def start_auto_update(self, interval=None):
        """开始自动更新
        
        Args:
            interval: 更新间隔（毫秒），默认30秒
        """
        if interval:
            self.update_interval = interval
        
        self.auto_update = True
        self._schedule_update()
    
    def stop_auto_update(self):
        """停止自动更新"""
        self.auto_update = False
        if self.update_timer:
            try:
                self.canvas.after_cancel(self.update_timer)
            except Exception:
                pass
            self.update_timer = None
    
    def refresh_data(self):
        """手动刷新数据"""
        if self.data_callback:
            try:
                network_data = self.data_callback()
                self.draw_topology(network_data)
            except Exception as e:
                print(f"刷新数据失败: {e}")
    
    def _schedule_update(self):
        """安排下一次更新"""
        if self.auto_update:
            self.refresh_data()
            self.update_timer = self.canvas.after(self.update_interval, self._schedule_update)


class IPAllocationVisualizer:
    """IP地址分配可视化类"""
    
    def __init__(self, parent):
        """初始化可视化器
        
        Args:
            parent: 父容器
        """
        self.parent = parent
        self.canvas_frame = Frame(parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建滚动条
        self.v_scrollbar = Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        
        # 创建画布
        self.canvas = Canvas(
            self.canvas_frame,
            bg=BACKGROUND_COLOR,
            yscrollcommand=self.v_scrollbar.set
        )
        
        # 配置滚动条
        self.v_scrollbar.config(command=self.canvas.yview)
        
        # 放置组件
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def draw_ip_allocation(self, network, ip_list):
        """绘制IP地址分配可视化
        
        Args:
            network: 网络地址
            ip_list: IP地址列表
        """
        self.canvas.delete(tk.ALL)
        
        # 获取字体设置
        font_family, font_size = get_current_font_settings()
        
        # 计算画布尺寸
        width = self.canvas.winfo_width() or 800
        height = 50 + len(ip_list) * 30
        
        # 绘制标题
        self.canvas.create_text(
            width / 2, 20,
            text=f"{translate('ip_allocation_visualization')}: {network}",
            font=(font_family, font_size, "bold"),
            fill=TEXT_COLOR
        )
        
        # 绘制IP地址列表
        for i, ip_info in enumerate(ip_list):
            y = 60 + i * 30
            
            # 根据状态设置颜色
            if ip_info["status"] == "allocated":
                color = "#27ae60"
            elif ip_info["status"] == "reserved":
                color = "#f39c12"
            else:
                color = "#95a5a6"
            
            # 绘制IP地址条
            self.canvas.create_rectangle(
                50, y, width - 50, y + 25,
                fill=color,
                outline="#34495e",
                width=1
            )
            
            # 绘制IP地址文本
            self.canvas.create_text(
                70, y + 12,
                text=ip_info["ip_address"],
                font=(font_family, font_size - 1),
                fill=TEXT_COLOR,
                anchor=tk.W
            )
            
            # 绘制主机名和描述
            if ip_info.get("hostname"):
                hostname = ip_info["hostname"]
                if len(hostname) > 20:
                    hostname = hostname[:17] + "..."
                
                self.canvas.create_text(
                    200, y + 12,
                    text=hostname,
                    font=(font_family, font_size - 1),
                    fill=TEXT_COLOR,
                    anchor=tk.W
                )
            
            # 绘制状态
            self.canvas.create_text(
                width - 70, y + 12,
                text=ip_info["status"],
                font=(font_family, font_size - 1),
                fill=TEXT_COLOR,
                anchor=tk.E
            )
        
        # 更新滚动区域
        self.canvas.config(scrollregion=(0, 0, width, height))
