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


# 定义颜色常量 - 优雅配色方案
NODE_COLOR = "#4a6fa5"
NODE_BORDER_COLOR = "#2c3e50"
LINK_COLOR = "#6c757d"
TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#2c3e50"
HIGHLIGHT_COLOR = "#3498db"

# 定义节点大小
NODE_WIDTH = 180
NODE_HEIGHT = 90
NODE_SPACING = 280  # 增加节点间距，减少拥挤

# 定义网段类型颜色 - 丰富配色方案
SUBNET_TYPE_COLORS = {
    "default": "#4a6fa5",      # 主蓝色
    "server": "#e76f51",        # 暖橙色（服务器）
    "client": "#2a9d8f",        # 青绿色（客户端）
    "network": "#f4a261",        # 柔和橙色（网络）
    "management": "#9c89b8",      # 柔和紫色（管理）
    "large": "#00b4d8",         # 亮青色（大网段）
    "medium": "#0077b6",        # 深蓝色（中等网段）
    "small": "#9333ea",         # 紫色（小网段）
    "extra_large": "#ef4444",    # 红色（超大网段）
    "wireless": "#8b5cf6",       # 紫色（无线网段）
    "office": "#10b981",         # 绿色（办公网段）
    "production": "#f59e0b",     # 橙色（生产网段）
    "test": "#8b5cf6",           # 紫色（测试网段）
    "dmz": "#ec4899",            # 粉色（DMZ网段）
    "storage": "#f97316",         # 橙色（存储网段）
    "backup": "#22c55e"          # 绿色（备份网段）
}

# 定义设备类型形状
DEVICE_SHAPES = {
    "default": "rectangle",
    "router": "diamond",
    "switch": "ellipse",
    "switch2": "rounded_rectangle",
    "switch3": "rectangle",
    "server": "rectangle",
    "client": "triangle",
    "wireless": "hexagon",
    "office": "pentagon",
    "production": "octagon",
    "test": "circle",
    "dmz": "star",
    "storage": "trapezoid",
    "backup": "parallelogram"
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
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        
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
        self._hover_poll_job = None  # 悬停轮询检测定时器
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
            tuple: (shape_id, gradient_items) shape_id 是边框对象的ID，gradient_items 是所有渐变填充层的ID列表
        """
        # 收集所有创建的渐变填充层对象ID
        gradient_items = []
        
        # 添加阴影效果 - 统一所有形状的阴影渲染方法
        shadow_offset = 3
        
        # 使用三层阴影，每层使用不同的偏移量，增强立体感
        # 移除 stipple 参数，使用纯黑阴影，与椭圆阴影效果一致
        for i in range(3):
            shadow_x = x + shadow_offset * (i + 1)
            shadow_y = y + shadow_offset * (i + 1)
            
            # 为所有形状创建相同效果的阴影
            if shape == "rectangle":
                # 矩形使用圆角矩形阴影（与主形状一致）
                radius = 10
                self.canvas.create_polygon(
                    shadow_x + radius, shadow_y,
                    shadow_x + width - radius, shadow_y,
                    shadow_x + width, shadow_y + radius,
                    shadow_x + width, shadow_y + height - radius,
                    shadow_x + width - radius, shadow_y + height,
                    shadow_x + radius, shadow_y + height,
                    shadow_x, shadow_y + height - radius,
                    shadow_x, shadow_y + radius,
                    fill="#000000",
                    outline="",
                    smooth=True
                )
            elif shape == "rounded_rectangle":
                # 圆角矩形使用圆角矩形阴影
                radius = 15
                self.canvas.create_polygon(
                    shadow_x + radius, shadow_y,
                    shadow_x + width - radius, shadow_y,
                    shadow_x + width, shadow_y + radius,
                    shadow_x + width, shadow_y + height - radius,
                    shadow_x + width - radius, shadow_y + height,
                    shadow_x + radius, shadow_y + height,
                    shadow_x, shadow_y + height - radius,
                    shadow_x, shadow_y + radius,
                    fill="#000000",
                    outline="",
                    smooth=True
                )
            elif shape == "ellipse" or shape == "circle":
                # 椭圆和圆形使用椭圆阴影
                self.canvas.create_oval(
                    shadow_x, shadow_y, shadow_x + width, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
            elif shape == "diamond":
                # 菱形使用菱形阴影
                self.canvas.create_polygon(
                    shadow_x + width / 2, shadow_y,
                    shadow_x + width, shadow_y + height / 2,
                    shadow_x + width / 2, shadow_y + height,
                    shadow_x, shadow_y + height / 2,
                    fill="#000000",
                    outline=""
                )
            elif shape == "triangle":
                # 三角形使用三角形阴影
                self.canvas.create_polygon(
                    shadow_x + width / 2, shadow_y,
                    shadow_x + width, shadow_y + height,
                    shadow_x, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
            elif shape == "hexagon":
                # 六边形使用六边形阴影
                points = []
                for j in range(6):
                    angle = math.pi / 3 * j
                    px = shadow_x + width / 2 + width / 2 * math.cos(angle)
                    py = shadow_y + height / 2 + height / 2 * math.sin(angle)
                    points.extend([px, py])
                self.canvas.create_polygon(
                    *points,
                    fill="#000000",
                    outline=""
                )
            elif shape == "pentagon":
                # 五边形使用五边形阴影
                points = []
                for j in range(5):
                    angle = math.pi * 2 / 5 * j - math.pi / 2
                    px = shadow_x + width / 2 + width / 2 * math.cos(angle)
                    py = shadow_y + height / 2 + height / 2 * math.sin(angle)
                    points.extend([px, py])
                self.canvas.create_polygon(
                    *points,
                    fill="#000000",
                    outline=""
                )
            elif shape == "octagon":
                # 八边形使用八边形阴影
                points = []
                for j in range(8):
                    angle = math.pi / 4 * j
                    px = shadow_x + width / 2 + width / 2 * math.cos(angle)
                    py = shadow_y + height / 2 + height / 2 * math.sin(angle)
                    points.extend([px, py])
                self.canvas.create_polygon(
                    *points,
                    fill="#000000",
                    outline=""
                )
            elif shape == "star":
                # 星形使用星形阴影
                points = []
                for j in range(10):
                    angle = math.pi * 2 / 10 * j - math.pi / 2
                    radius = width / 2 if j % 2 == 0 else width / 4
                    px = shadow_x + width / 2 + radius * math.cos(angle)
                    py = shadow_y + height / 2 + radius * math.sin(angle)
                    points.extend([px, py])
                self.canvas.create_polygon(
                    *points,
                    fill="#000000",
                    outline=""
                )
            elif shape == "trapezoid":
                # 梯形使用梯形阴影
                top_width = width * 0.7
                bottom_width = width
                self.canvas.create_polygon(
                    shadow_x + (width - top_width) / 2, shadow_y,
                    shadow_x + (width + top_width) / 2, shadow_y,
                    shadow_x + width, shadow_y + height,
                    shadow_x, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
            elif shape == "parallelogram":
                # 平行四边形使用平行四边形阴影
                skew = width * 0.2
                self.canvas.create_polygon(
                    shadow_x + skew, shadow_y,
                    shadow_x + width, shadow_y,
                    shadow_x + width - skew, shadow_y + height,
                    shadow_x, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
            else:
                # 默认使用椭圆阴影
                self.canvas.create_oval(
                    shadow_x, shadow_y, shadow_x + width, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
        
        # 创建主形状
        if shape == "rectangle":
            # 创建圆角矩形
            radius = 10
            # 创建渐变效果（使用多层叠加）
            for i in range(3):
                alpha = 0.3 + i * 0.2
                gradient_fill = fill
                if i > 0:
                    # 稍微亮一点的颜色作为渐变
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + radius, y + i,
                    x + width - radius, y + i,
                    x + width - i, y + radius,
                    x + width - i, y + height - radius,
                    x + width - radius, y + height - i,
                    x + radius, y + height - i,
                    x + i, y + height - radius,
                    x + i, y + radius,
                    fill=gradient_fill,
                    outline="",
                    smooth=True
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                x + radius, y,
                x + width - radius, y,
                x + width, y + radius,
                x + width, y + height - radius,
                x + width - radius, y + height,
                x + radius, y + height,
                x, y + height - radius,
                x, y + radius,
                fill="",
                outline=outline,
                width=border_width + 1,
                smooth=True
            )
            return shape_id, gradient_items
        elif shape == "ellipse":
            # 创建渐变效果 - 填充层先创建
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_oval(
                    x + i, y + i, x + width - i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 边框层最后创建，并提升到最顶层，确保鼠标事件优先命中边框
            shape_id = self.canvas.create_oval(
                x, y, x + width, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            # 关键：将边框提升到所有填充层之上，解决椭圆内部无法触发悬停的问题
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "diamond":
            # 创建渐变效果 - 填充层先创建
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + width / 2, y + i,
                    x + width - i, y + height / 2,
                    x + width / 2, y + height - i,
                    x + i, y + height / 2,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 边框层最后创建并提升到最顶层
            shape_id = self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height / 2,
                x + width / 2, y + height,
                x, y + height / 2,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "triangle":
            # 创建渐变效果 - 填充层先创建
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + width / 2, y + i,
                    x + width - i, y + height - i,
                    x + i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 边框层最后创建并提升到最顶层
            shape_id = self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height,
                x, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "rounded_rectangle":
            # 创建圆角矩形
            radius = 15
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + radius, y + i,
                    x + width - radius, y + i,
                    x + width - i, y + radius,
                    x + width - i, y + height - radius,
                    x + width - radius, y + height - i,
                    x + radius, y + height - i,
                    x + i, y + height - radius,
                    x + i, y + radius,
                    fill=gradient_fill,
                    outline="",
                    smooth=True
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                x + radius, y,
                x + width - radius, y,
                x + width, y + radius,
                x + width, y + height - radius,
                x + width - radius, y + height,
                x + radius, y + height,
                x, y + height - radius,
                x, y + radius,
                fill="",
                outline=outline,
                width=border_width + 1,
                smooth=True
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "hexagon":
            # 创建六边形
            points = []
            for i in range(6):
                angle = math.pi / 3 * i
                px = x + width / 2 + width / 2 * math.cos(angle)
                py = y + height / 2 + height / 2 * math.sin(angle)
                points.extend([px, py])
            
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "pentagon":
            # 创建五边形
            points = []
            for i in range(5):
                angle = math.pi * 2 / 5 * i - math.pi / 2
                px = x + width / 2 + width / 2 * math.cos(angle)
                py = y + height / 2 + height / 2 * math.sin(angle)
                points.extend([px, py])
            
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "octagon":
            # 创建八边形
            points = []
            for i in range(8):
                angle = math.pi / 4 * i
                px = x + width / 2 + width / 2 * math.cos(angle)
                py = y + height / 2 + height / 2 * math.sin(angle)
                points.extend([px, py])
            
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "circle":
            # 创建圆形
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_oval(
                    x + i, y + i, x + width - i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_oval(
                x, y, x + width, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "star":
            # 创建星形
            points = []
            for i in range(10):
                angle = math.pi * 2 / 10 * i - math.pi / 2
                radius = width / 2 if i % 2 == 0 else width / 4
                px = x + width / 2 + radius * math.cos(angle)
                py = y + height / 2 + radius * math.sin(angle)
                points.extend([px, py])
            
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "trapezoid":
            # 创建梯形
            top_width = width * 0.7
            bottom_width = width
            
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + (width - top_width) / 2 + i, y + i,
                    x + (width + top_width) / 2 - i, y + i,
                    x + width - i, y + height - i,
                    x + i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                x + (width - top_width) / 2, y,
                x + (width + top_width) / 2, y,
                x + width, y + height,
                x, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        elif shape == "parallelogram":
            # 创建平行四边形
            skew = width * 0.2
            
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + skew + i, y + i,
                    x + width + i, y + i,
                    x + width - skew - i, y + height - i,
                    x - i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 创建边框
            shape_id = self.canvas.create_polygon(
                x + skew, y,
                x + width, y,
                x + width - skew, y + height,
                x, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items
        else:
            shape_id = self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
            return shape_id, gradient_items
    
    def add_node(self, name, subnet, level=0, subnet_type="default", device_type="default", ip_info=None, parent_id=None):
        """添加节点
        
        Args:
            name: 节点名称
            subnet: 子网信息
            level: 层级
            subnet_type: 网段类型
            device_type: 设备类型
            ip_info: IP地址信息
            parent_id: 父节点ID
        
        Returns:
            str: 节点ID
        """
        node_id = f"node_{len(self.nodes)}"
        
        # 计算节点位置（使用改进的树形布局）
        if parent_id and parent_id in self.nodes:
            # 如果有父节点，基于父节点位置计算
            parent_node = self.nodes[parent_id]
            x = parent_node["x"] + NODE_SPACING  # 水平间距
            # 计算父节点的子节点数量，确保子节点均匀分布
            child_count = sum(1 for n in self.nodes.values() if n.get("parent_id") == parent_id)
            # 计算子节点的垂直位置，确保父节点居中
            y = parent_node["y"] + (child_count - 1) * (NODE_HEIGHT + 60) - (child_count * (NODE_HEIGHT + 60)) / 2 + NODE_HEIGHT / 2
        else:
            # 根节点或没有父节点的节点
            x = 100 + level * NODE_SPACING  # 水平间距
            # 计算同一层级节点的数量
            same_level_nodes = len([n for n in self.nodes.values() if n.get("level") == level])
            # 计算垂直位置，确保节点垂直分布
            y = 100 + same_level_nodes * (NODE_HEIGHT + 40)  # 适当的垂直间距
        
        # 根据网段类型获取颜色
        node_color = SUBNET_TYPE_COLORS.get(subnet_type, NODE_COLOR)
        
        # 根据设备类型获取形状
        node_shape = DEVICE_SHAPES.get(device_type, "rectangle")
        
        # 创建节点形状
        shape_id, gradient_items = self.create_node_shape(
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
        
        # 关键：将所有属于该节点的画布对象绑定到统一的 tag
        # 包括：形状边框层 + 渐变填充层 + 文本对象
        # 这样无论鼠标碰到节点的哪个部分（形状/填充/文本），都能正确识别
        all_node_items = [shape_id, text_id, subnet_id, ip_info_id] + gradient_items
        for item_id in all_node_items:
            self.canvas.itemconfig(item_id, tags=(node_id,))
        
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
            "level": level,
            "parent_id": parent_id
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
            
            # 创建连接线，添加箭头和动画效果
            link_id = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=LINK_COLOR,
                width=2,
                arrow=tk.LAST,
                arrowshape=(10, 15, 5),  # 箭头形状：(箭头长度, 箭头宽度, 箭头角度)
                smooth=True
            )
            
            # 存储连接信息
            self.links.append({
                "id": link_id,
                "source": source_node_id,
                "target": target_node_id
            })
            
            # 将连接线置于节点下方
            self.canvas.tag_lower(link_id)

    def clear(self):
        """清空画布"""
        # 停止轮询检测
        self._stop_hover_polling()
        
        self.canvas.delete(tk.ALL)
        self.nodes = {}
        self.links = []
        self.visible_nodes = set()
        self.scale = 1.0
        self.hovered_node = None
    
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
        
        # 构建网络层次结构，先处理父节点，再处理子节点
        # 按层级排序网络数据
        sorted_data = sorted(filtered_data, key=lambda x: x.get("level", 0))
        
        # 遍历网络数据，构建节点和连接
        for network in sorted_data:
            # 检查节点级别是否在过滤范围内
            if network.get("level", 0) <= self.filter_level or self.filter_level == 0:
                # 查找父节点ID
                parent_network_id = network.get("parent_id")
                parent_node_id = node_id_map.get(parent_network_id) if parent_network_id else None
                
                # 添加网络节点
                node_id = self.add_node(
                    network.get("name", "Network"),
                    network.get("cidr", ""),
                    level=network.get("level", 0),
                    subnet_type=network.get("subnet_type", network.get("type", "default")),
                    device_type=network.get("device_type", "default"),
                    ip_info=network.get("ip_info", {}),
                    parent_id=parent_node_id
                )
                node_id_map[network.get("id", node_id)] = node_id
                self.visible_nodes.add(node_id)
        
        # 添加连接
        for network in sorted_data:
            node_id = node_id_map.get(network.get("id"))
            if node_id and node_id in self.visible_nodes:
                # 遍历子节点，获取子节点ID
                for child in network.get("children", []):
                    if isinstance(child, dict):
                        child_id = child.get("id")
                        if child_id in node_id_map and node_id_map[child_id] in self.visible_nodes:
                            self.add_link(node_id, node_id_map[child_id])
                    elif isinstance(child, str):
                        # 如果子节点是字符串ID，直接查找
                        if child in node_id_map and node_id_map[child] in self.visible_nodes:
                            self.add_link(node_id, node_id_map[child])
        
        # 重新计算所有节点的位置，确保父节点垂直居中在子节点中间
        self._reposition_all_nodes()
        
        # 强制更新画布
        self.canvas.update()
        
        # 更新滚动区域
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(tk.ALL)
        if bbox:
            # 扩展边界框，确保所有节点都能被看到
            x1, y1, x2, y2 = bbox
            padding = 100  # 增加边距
            self.canvas.config(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))
            
            # 滚动到画布左上角，确保用户可以从开始查看
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
        else:
            # 如果没有节点，设置默认滚动区域
            self.canvas.config(scrollregion=(0, 0, 1000, 800))
    
    def _reposition_all_nodes(self):
        """重新计算所有节点的位置，确保父节点垂直居中在子节点中间"""
        # 首先计算每个层级的节点数量
        level_nodes = {}
        for node_id, node in self.nodes.items():
            level = node.get("level", 0)
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node)
        
        # 按层级从低到高排序
        sorted_levels = sorted(level_nodes.keys())
        
        # 计算每个层级的水平位置
        level_x = {}
        for level in sorted_levels:
            level_x[level] = 100 + level * NODE_SPACING
        
        # 重新计算每个节点的位置
        for level in sorted_levels:
            nodes = level_nodes[level]
            # 计算每个节点的垂直位置
            for i, node in enumerate(nodes):
                node["x"] = level_x[level]
                # 暂时设置一个初始垂直位置
                node["y"] = 100 + i * (NODE_HEIGHT + 40)
        
        # 调整父节点位置，确保垂直居中在子节点中间
        self._adjust_parent_positions()
    
    def _adjust_parent_positions(self):
        """调整父节点位置，确保垂直居中在子节点中间"""
        # 收集所有父节点
        parent_nodes = {}
        for node_id, node in self.nodes.items():
            parent_id = node.get("parent_id")
            if parent_id:
                if parent_id not in parent_nodes:
                    parent_nodes[parent_id] = []
                parent_nodes[parent_id].append(node)
        
        # 按层级从高到低排序父节点，确保先调整深层级的父节点
        # 这样上层父节点的调整不会影响下层父节点的位置
        sorted_parents = []
        for parent_id in parent_nodes:
            if parent_id in self.nodes:
                level = self.nodes[parent_id].get("level", 0)
                sorted_parents.append((level, parent_id))
        sorted_parents.sort(reverse=True, key=lambda x: x[0])
        
        # 调整每个父节点的位置
        for level, parent_id in sorted_parents:
            children = parent_nodes[parent_id]
            if parent_id in self.nodes:
                parent_node = self.nodes[parent_id]
                if children:
                    # 计算子节点的垂直范围，考虑子节点的高度
                    min_y = min(child["y"] for child in children)
                    max_y = max(child["y"] + NODE_HEIGHT for child in children)
                    # 计算子节点的垂直中心
                    center_y = (min_y + max_y) / 2 - NODE_HEIGHT / 2
                    # 调整父节点的垂直位置
                    parent_node["y"] = center_y
        
        # 重新绘制所有节点和连接线
        self._redraw_all_nodes()
        self._redraw_all_links()
    
    def _redraw_all_nodes(self):
        """重新绘制所有节点"""
        # 删除所有旧的节点
        for node in self.nodes.values():
            self.canvas.delete(node["shape"])
            self.canvas.delete(node["text"])
            self.canvas.delete(node["subnet_text"])
            self.canvas.delete(node["ip_info_text"])
        
        # 重新绘制所有节点
        for node_id, node in self.nodes.items():
            # 确定节点形状和颜色
            shape_type = DEVICE_SHAPES.get(node["device_type"], "rectangle")
            node_color = SUBNET_TYPE_COLORS.get(node["subnet_type"], NODE_COLOR)
            
            # 绘制节点形状
            shape_tuple = self.create_node_shape(
                node["x"],
                node["y"],
                NODE_WIDTH,
                NODE_HEIGHT,
                shape_type,
                node_color
            )
            # 只取形状ID，忽略渐变填充层ID列表
            shape = shape_tuple[0]
            
            # 绘制节点文本
            text = self.canvas.create_text(
                node["x"] + NODE_WIDTH / 2,
                node["y"] + NODE_HEIGHT / 2 - 20,
                text=node["name"],
                fill="white",
                font=("微软雅黑", 10, "bold"),
                tags=("node_text", f"node_{node_id}")
            )
            
            # 绘制网段信息
            cidr = node.get("subnet", "")
            subnet_text = self.canvas.create_text(
                node["x"] + NODE_WIDTH / 2,
                node["y"] + NODE_HEIGHT / 2,
                text=cidr,
                fill="white",
                font=("微软雅黑", 9),
                tags=("node_text", f"node_{node_id}")
            )
            
            # 绘制IP数量信息
            ip_info_dict = node.get("ip_info", {})
            allocated = ip_info_dict.get("allocated", 0)
            reserved = ip_info_dict.get("reserved", 0)
            total = ip_info_dict.get("total", 0)
            used_ips = allocated + reserved
            ip_info_text = f"{used_ips}/{total}"
            ip_info_text_item = self.canvas.create_text(
                node["x"] + NODE_WIDTH / 2,
                node["y"] + NODE_HEIGHT * 3 / 4,
                text=ip_info_text,
                fill="white",
                font=("微软雅黑", 8),
                tags=("node_text", f"node_{node_id}")
            )
            
            # 更新节点信息
            node["shape"] = shape
            node["text"] = text
            node["subnet_text"] = subnet_text
            node["ip_info_text"] = ip_info_text_item
    
    def _redraw_all_links(self):
        """重新绘制所有连接线"""
        # 先删除所有旧的连接线
        for item in self.canvas.find_withtag("link"):
            self.canvas.delete(item)
        
        # 清空 links 列表
        self.links = []
        
        # 重新绘制所有连接线
        for node_id, node in self.nodes.items():
            parent_id = node.get("parent_id")
            if parent_id and parent_id in self.nodes:
                source_node = self.nodes[parent_id]
                target_node = node
                line = self.canvas.create_line(
                    source_node["x"] + NODE_WIDTH / 2,
                    source_node["y"] + NODE_HEIGHT / 2,
                    target_node["x"] + NODE_WIDTH / 2,
                    target_node["y"] + NODE_HEIGHT / 2,
                    arrow=tk.LAST,
                    width=2,
                    fill="#CCCCCC",
                    tags="link"
                )
                self.links.append({
                    "source": parent_id,
                    "target": node_id,
                    "line": line
                })
    
    def auto_scale_to_fit(self):
        """自动缩放画布以适应所有节点"""
        bbox = self.canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        # 确保画布已完全初始化
        self.canvas.update_idletasks()
        
        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 如果画布尺寸还没有正确获取，使用默认值
        if canvas_width <= 1 or canvas_height <= 1:
            # 使用父容器的尺寸
            if self.canvas_frame:
                canvas_width = self.canvas_frame.winfo_width()
                canvas_height = self.canvas_frame.winfo_height()
            else:
                # 使用默认尺寸
                canvas_width = 800
                canvas_height = 600
        
        # 计算所有节点的边界框
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        
        if content_width <= 0 or content_height <= 0:
            return
        
        # 计算缩放比例，考虑边距
        margin = 50
        scale_x = (canvas_width - 2 * margin) / content_width
        scale_y = (canvas_height - 2 * margin) / content_height
        scale_factor = min(scale_x, scale_y)
        
        # 限制缩放范围
        scale_factor = max(0.1, min(scale_factor, 2.0))
        
        # 应用缩放
        if scale_factor != 1.0:
            # 计算缩放中心（内容中心）
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # 缩放所有内容
            self.canvas.scale(tk.ALL, center_x, center_y, scale_factor, scale_factor)
            
            # 更新缩放因子
            self.scale *= scale_factor
        
        # 重新计算边界框并更新滚动区域
        self.canvas.update_idletasks()
        new_bbox = self.canvas.bbox(tk.ALL)
        if new_bbox:
            nx1, ny1, nx2, ny2 = new_bbox
            padding = 50
            self.canvas.config(scrollregion=(nx1 - padding, ny1 - padding, nx2 + padding, ny2 + padding))
        
        # 滚动到合适位置，确保所有节点都能看到
        # 计算内容中心
        if bbox:
            content_center_x = (x1 + x2) / 2
            content_center_y = (y1 + y2) / 2
            
            # 计算滚动位置
            scroll_x = (content_center_x - canvas_width / 2) / (content_width * scale_factor)
            scroll_y = (content_center_y - canvas_height / 2) / (content_height * scale_factor)
            
            # 限制滚动位置在合理范围内
            scroll_x = max(0, min(scroll_x, 1))
            scroll_y = max(0, min(scroll_y, 1))
            
            # 设置滚动位置
            self.canvas.xview_moveto(scroll_x)
            self.canvas.yview_moveto(scroll_y)
    
    def _filter_nodes(self, network_data):
        """过滤节点
        
        Args:
            network_data: 网络数据
        
        Returns:
            list: 过滤后的节点列表
        """
        def collect_nodes(data):
            """递归收集所有节点"""
            nodes = []
            nodes.append(data)
            if "children" in data and data["children"]:
                for child in data["children"]:
                    if isinstance(child, dict):
                        child["parent_id"] = data["id"]  # 添加父节点ID
                        nodes.extend(collect_nodes(child))
            return nodes
        
        # 收集所有节点
        nodes = []
        if isinstance(network_data, list):
            # 如果network_data是列表，遍历每个元素
            for item in network_data:
                if isinstance(item, dict):
                    nodes.extend(collect_nodes(item))
        elif isinstance(network_data, dict):
            # 如果network_data是字典，直接收集
            nodes = collect_nodes(network_data)
        
        # 这里可以实现更复杂的过滤逻辑
        # 例如根据节点类型、状态等进行过滤
        return nodes
    
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
        """鼠标移动事件，用于显示节点悬停详情和悬停效果"""
        # 将窗口坐标转换为画布坐标（考虑滚动）
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 查找鼠标下方的节点
        hovered_node = None
        
        # 使用 find_overlapping 查找与鼠标位置重叠的所有对象
        overlapping = self.canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
        
        # 通过 tag 匹配节点（不再只依赖 shape 对象）
        # 因为椭圆等形状的边框层 fill="" 无法覆盖内部区域，
        # 所以改用统一 tag 来识别鼠标所在的节点
        for item_id in reversed(list(overlapping)):
            tags = self.canvas.gettags(item_id)
            for tag in tags:
                if tag in self.nodes:  # tag 就是 node_id（如 "node_0"）
                    hovered_node = self.nodes[tag]
                    break
            if hovered_node:
                break
        
        # 只在悬停节点发生变化时才处理样式切换
        if hovered_node != self.hovered_node:
            # 恢复之前所有节点的原始样式
            self._restore_all_hover_styles()
            
            # 停止旧的轮询定时器
            self._stop_hover_polling()
            
            # 更新悬停状态
            self.hovered_node = hovered_node
            
            if hovered_node:
                # 应用新节点的悬停样式
                self._apply_hover_style(hovered_node)
                self.last_mouse_x = event.x_root
                self.last_mouse_y = event.y_root
                
                # 延迟显示提示
                if self.tooltip_timer:
                    try:
                        self.canvas.after_cancel(self.tooltip_timer)
                    except Exception:
                        pass
                self.tooltip_timer = self.canvas.after(100, self._delayed_show_tooltip)
                
                # 启动轮询检测定时器（关键：解决鼠标停在空白处不触发Motion的问题）
                self._start_hover_polling()
            else:
                # 鼠标不在任何节点上，隐藏提示
                if self.tooltip_timer:
                    try:
                        self.canvas.after_cancel(self.tooltip_timer)
                    except Exception:
                        pass
                self.tooltip_timer = None
                self.hide_tooltip()

    def _start_hover_polling(self):
        """启动悬停轮询检测定时器
        
        每50ms检测一次鼠标是否仍在当前悬停节点上，
        解决鼠标停在画布空白处不再触发Motion事件导致高亮残留的问题
        """
        self._stop_hover_polling()
        self._hover_poll_job = self.canvas.after(50, self._check_hover_state)

    def _stop_hover_polling(self):
        """停止悬停轮询检测定时器"""
        if self._hover_poll_job:
            try:
                self.canvas.after_cancel(self._hover_poll_job)
            except Exception:
                pass
            self._hover_poll_job = None

    def _check_hover_state(self):
        """轮询检测当前鼠标位置是否仍在悬停节点上
        
        如果鼠标已离开当前悬停节点，立即恢复样式并隐藏tooltip
        """
        if not self.hovered_node:
            return
        
        try:
            # 获取当前鼠标在画布上的坐标
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            
            # 转换为画布坐标
            canvas_x = self.canvas.canvasx(x)
            canvas_y = self.canvas.canvasy(y)
            
            # 检查鼠标是否仍在当前悬停节点上（通过 tag 匹配）
            overlapping = self.canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
            still_on_node = False
            for item_id in overlapping:
                tags = self.canvas.gettags(item_id)
                if self.hovered_node["id"] in tags:  # 检查 tag 是否包含当前节点的 node_id
                    still_on_node = True
                    break
            
            if not still_on_node:
                # 鼠标已离开节点，恢复所有样式
                self._restore_all_hover_styles()
                self.hovered_node = None
                self.hide_tooltip()
                return
            
            # 仍在节点上，继续轮询
            self._hover_poll_job = self.canvas.after(50, self._check_hover_state)
        except (tk.TclError, Exception):
            # 画布可能已被销毁，停止轮询
            pass

    def _restore_all_hover_styles(self):
        """恢复所有处于悬停状态的节点的原始样式"""
        for node_id, node in list(self.nodes.items()):
            if "original_style" in node:
                self._restore_node_style(node)

    def _apply_hover_style(self, node):
        """应用节点悬停样式
        
        Args:
            node: 节点信息
        """
        # 保存原始样式
        if "original_style" not in node:
            # 获取宽度值，处理空字符串和浮点数情况
            width_str = self.canvas.itemcget(node["shape"], "width")
            try:
                line_width = int(float(width_str)) if width_str else 2
            except (ValueError, TypeError):
                line_width = 2
            node["original_style"] = {
                "outline": self.canvas.itemcget(node["shape"], "outline"),
                "line_width": line_width
            }
        
        # 更改节点样式 - 仅修改边框和宽度
        self.canvas.itemconfig(node["shape"], 
                             outline="#ffffff", 
                             width=3)
        
        # 提升节点到顶层
        self.canvas.tag_raise(node["shape"])
        self.canvas.tag_raise(node["text"])
        self.canvas.tag_raise(node["subnet_text"])
        self.canvas.tag_raise(node["ip_info_text"])

    def _restore_node_style(self, node):
        """恢复节点原始样式
        
        Args:
            node: 节点信息
        """
        if "original_style" in node:
            original = node["original_style"]
            
            # 恢复节点样式
            self.canvas.itemconfig(node["shape"], 
                                 outline=original["outline"], 
                                 width=original["line_width"])
            
            # 删除原始样式属性
            del node["original_style"]
    
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
        # 先销毁旧的tooltip
        self.hide_tooltip()
        
        # 创建提示窗口
        self.tooltip = tk.Toplevel(self.parent)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x_root + 15}+{y_root + 10}")
        
        # 创建提示内容
        frame = tk.Frame(self.tooltip, bg="#333", padx=10, pady=5)
        frame.pack()
        
        # 绑定tooltip的Leave事件：当鼠标离开tooltip时也恢复样式
        def on_tooltip_leave(event):
            self._restore_all_hover_styles()
            self.hovered_node = None
            self.hide_tooltip()
            self._stop_hover_polling()
        
        self.tooltip.bind("<Leave>", on_tooltip_leave)
        
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
        if hasattr(self, 'tooltip') and self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None
    
    def on_canvas_leave(self, event):
        """鼠标离开画布事件处理"""
        # 停止轮询检测
        self._stop_hover_polling()
        
        # 恢复所有节点的原始样式
        self._restore_all_hover_styles()
        
        # 隐藏提示窗口
        self.hide_tooltip()
        
        # 重置悬停状态
        self.hovered_node = None
    

    
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
