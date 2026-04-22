#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
可视化模块
实现网络拓扑图和IP地址分配可视化功能

模块说明：
- NetworkTopologyVisualizer: 网络拓扑可视化类，支持单一综合性网络拓扑图

使用示例：
python
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

import ipaddress
import tkinter as tk
from tkinter import Canvas
from typing import Callable, Any
from style_manager import get_current_font_settings

# 模块版本
__version__ = "1.0.0"


# 模块接口定义
class VisualizationError(Exception):
    """可视化模块异常"""
    pass


# 定义颜色常量 - 优雅配色方案
NODE_COLOR = "#4a6fa5"
NODE_BORDER_COLOR = "#aaaaaa"
LINK_COLOR = "#6c757d"
TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#2c3e50"
HIGHLIGHT_COLOR = "#3498db"

# 定义节点大小
NODE_WIDTH = 150
NODE_HEIGHT = 70
NODE_SPACING = 230  # 调整节点间距，使布局更紧凑

# 定义网段类型颜色 - 丰富配色方案
SUBNET_TYPE_COLORS = {
    "default": "#f4a261",      # 柔和橙色（默认）
    "server": "#e76f51",        # 暖橙色（服务器）
    "client": "#2a9d8f",        # 青绿色（客户端）
    "network": "#f4a261",        # 柔和橙色（网络）
    "management": "#9c89b8",      # 柔和紫色（管理）
    "large": "#f97316",         # 橙色（大网段）
    "medium": "#f59e0b",        # 橙色（中等网段）
    "small": "#9333ea",         # 紫色（小网段）
    "extra_large": "#ef4444",    # 红色（超大网段）
    "wireless": "#8b5cf6",       # 紫色（无线网段）
    "office": "#10b981",         # 绿色（办公网段）
    "production": "#f59e0b",     # 橙色（生产网段）
    "test": "#ec4899",           # 粉色（测试网段）
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
    
    @staticmethod
    def _cidr_to_sort_key(cidr: str) -> tuple:
        """将CIDR转换为可用于排序的元组
        
        Args:
            cidr: CIDR字符串，如 "192.168.1.0/24" 或 "2001:db8::/32"
        
        Returns:
            tuple: 可用于排序的元组，IPv4如 (4, 192, 168, 1, 0)，IPv6如 (6, 8193, 3512, ...)
        """
        if not cidr:
            return ()
        try:
            net = ipaddress.ip_network(cidr, strict=False)
            return (net.version, int(net.network_address))
        except (ValueError, IndexError):
            return ()
    
    def __init__(self, parent: tk.BaseWidget) -> None:
        """初始化可视化器
        
        Args:
            parent: 父容器
        """
        self.parent: tk.BaseWidget = parent
        
        # 创建画布，直接放在父容器上（移除多余的 canvas_frame）
        self.canvas: Canvas = Canvas(
            parent,
            bg=BACKGROUND_COLOR,
            highlightthickness=0,
            bd=0,
            borderwidth=0,
            relief="flat"
        )
        
        # 放置组件
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 创建全屏按钮
        self._create_fullscreen_button()
        
        # 初始化数据
        self.nodes: dict[str, dict[str, Any]] = {}
        self.links: list[dict[str, Any]] = []
        
        # 双击检测相关
        self.last_click_time: int = 0
        self.last_click_x: int = 0
        self.last_click_y: int = 0
        try:
            self.double_click_threshold: int = int(self.canvas.tk.call('tk', 'getDoubleClickTime'))
        except Exception:
            self.double_click_threshold = 500
        self.double_click_distance: int = 5  # 双击位置距离阈值（像素）
        self.click_count: int = 0
        self.click_timer: int | None = None
        
        # 双击冷却相关
        self._in_double_click_cooldown: bool = False
        self._double_click_cooldown_timer: str | None = None
        self._last_double_click_scale: float = 1.0
        self._last_double_click_offset: tuple[float, float] = (0.0, 0.0)
        
        # 绑定事件（使用自定义双击检测）
        _ = self.canvas.bind("<Button-1>", self.on_click)
        _ = self.canvas.bind("<B1-Motion>", self.drag)
        _ = self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        _ = self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        _ = self.canvas.bind("<Motion>", self.on_mouse_move)
        _ = self.canvas.bind("<Leave>", self.on_canvas_leave)
        
        # 绑定配置事件，当父容器大小变化时调整画布大小
        _ = self.parent.bind("<Configure>", self.on_canvas_frame_configure)
        
        # 拖拽状态
        self.dragging: bool = False
        self.drag_start_x: int = 0
        self.drag_start_y: int = 0
        self.last_x: int = 0
        self.last_y: int = 0
        
        # 缩放因子
        self.scale: float = 1.0
        
        # 节点悬停状态
        self.hovered_node: dict[str, Any] | None = None
        self.tooltip: tk.Toplevel | None = None
        self.tooltip_timer: str | None = None  # 延迟显示定时器
        self._hover_poll_job: str | None = None  # 悬停轮询检测定时器
        self.last_mouse_x: int = 0  # 记录鼠标位置
        self.last_mouse_y: int = 0
        
        # 数据更新相关
        self.update_interval: int = 30000  # 默认 30 秒刷新一次
        self.update_timer: str | None = None
        self.data_callback: Callable[[], object] | None = None
        self.auto_update: bool = False
        
        # 性能优化相关
        self.batch_drawing: bool = True  # 启用批量绘制
        self.max_nodes: int = 500  # 最大节点数
        self.filter_level: int = 10  # 过滤级别，0 表示显示所有节点
        self.visible_nodes: set[str] = set()  # 可见节点集合
        
        # 拓扑数据相关
        self.network_data: object = None
        self._scaled: bool = False
        self._is_first_draw: bool = True  # 首次绘制标志，用于防闪现
        self._pending_initial_scale: bool = False  # 是否有待执行的初始缩放
        self._auto_scale_timer: str | None = None  # 延迟缩放定时器ID
        
        # 全屏相关
        self.is_fullscreen: bool = False
        self.original_scale: float = 1.0
        self.fullscreen_window: tk.Toplevel | None = None
        self.fullscreen_canvas: Canvas | None = None
        self.original_canvas: Canvas | None = None
        self.exit_fullscreen_button: tk.Button | None = None
        self.control_frame: tk.Frame | None = None
        self.zoom_in_button: tk.Button | None = None
        self.zoom_out_button: tk.Button | None = None
        self.reset_button: tk.Button | None = None
        self.scale_label: tk.Label | None = None
        self.original_nodes: dict[str, dict[str, Any]] | None = None
        
    def start_drag(self, event: tk.Event) -> None:
        """开始拖拽"""
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.last_x = event.x
        self.last_y = event.y
        
        # 停止悬停轮询和tooltip，避免拖拽期间的性能负担
        self._stop_hover_polling()
        self.hide_tooltip()
        self.hovered_node = None
    
    def drag(self, event: tk.Event) -> None:
        """拖拽操作"""
        if self.dragging:
            dx: int = event.x - self.last_x
            dy: int = event.y - self.last_y
            self.canvas.move(tk.ALL, dx, dy)
            self.last_x = event.x
            self.last_y = event.y
    
    def stop_drag(self, _event: tk.Event) -> None:
        """停止拖拽"""
        self.dragging = False
    
    def on_click(self, event: tk.Event) -> None:
        """自定义点击处理，实现双击检测 - 立即响应拖拽"""
        current_time = event.time
        current_x = event.x
        current_y = event.y
        
        # 检查是否处于双击冷却期（防止三击被误判为两次双击）
        if hasattr(self, '_in_double_click_cooldown') and self._in_double_click_cooldown:
            # 在冷却期内，只记录点击信息，不检测双击
            self.last_click_time = current_time
            self.last_click_x = current_x
            self.last_click_y = current_y
            self.start_drag(event)
            return
        
        # 检查是否是双击
        time_diff = current_time - self.last_click_time
        distance = ((current_x - self.last_click_x) ** 2 + (current_y - self.last_click_y) ** 2) ** 0.5
        
        if time_diff <= self.double_click_threshold and distance <= self.double_click_distance:
            # 是双击事件 - 停止拖拽并设置冷却期，防止三击被误判为两次双击
            self.dragging = False
            self._in_double_click_cooldown = True
            if self._double_click_cooldown_timer is not None:
                self.canvas.after_cancel(self._double_click_cooldown_timer)
                self._double_click_cooldown_timer = None
            self._double_click_cooldown_timer = self.canvas.after(
                self.double_click_threshold, 
                lambda: setattr(self, '_in_double_click_cooldown', False)
            )
            # 执行双击缩放
            self.on_double_click(event)
            
            # 重置点击状态
            self.last_click_time = 0
            self.click_count = 0
            
            return
        
        # 不是双击，记录点击信息
        self.last_click_time = current_time
        self.last_click_x = current_x
        self.last_click_y = current_y
        
        # 立即开始拖拽，不再等待双击检测
        self.start_drag(event)
    
    def reset_to_original(self):
        """重置到原始大小和位置，通过重新绘制避免缩放累积问题"""
        # 获取当前网络数据
        current_network_data = getattr(self, 'network_data', None)
        if current_network_data:
            # 清除画布
            self.canvas.delete(tk.ALL)
            self.nodes.clear()
            self.links.clear()
            
            # 重新绘制拓扑图
            self.draw_topology(current_network_data)
            
            # 更新缩放因子
            self.scale = 1.0
            
            # 更新缩放比例显示
            if hasattr(self, 'scale_label') and self.scale_label:
                self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def on_double_click(self, event):
        """双击缩放功能"""
        current_scale = getattr(self, 'scale', 1.0)
        
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 如果画布尺寸无效，尝试从父容器获取
        if canvas_width <= 1 or canvas_height <= 1:
            try:
                parent = self.canvas.nametowidget(self.canvas.winfo_parent())
                if parent:
                    parent.update_idletasks()
                    canvas_width = parent.winfo_width()
                    canvas_height = parent.winfo_height()
            except tk.TclError as e:
                print(f"无法获取父容器尺寸: {e}")
        
        if current_scale < 1.0:
            # 放大到100%，以鼠标点击位置为中心
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            scale_factor = 1.0 / current_scale
            
            self.canvas.scale(tk.ALL, canvas_x, canvas_y, scale_factor, scale_factor)
            
            center_canvas_x = self.canvas.canvasx(canvas_width / 2)
            center_canvas_y = self.canvas.canvasy(canvas_height / 2)
            
            dx = center_canvas_x - canvas_x
            dy = center_canvas_y - canvas_y
            self.canvas.move(tk.ALL, dx, dy)
            
            bbox = self.canvas.bbox(tk.ALL)
            if bbox:
                self.canvas.config(scrollregion=self._expanded_bbox(bbox))
            
            self.scale = 1.0
            if hasattr(self, 'scale_label') and self.scale_label:
                self.scale_label.config(text=f"{int(self.scale * 100)}%")
        else:
            # 缩小到50%
            bbox = self.canvas.bbox(tk.ALL)
            if not bbox:
                return
            
            x1, y1, x2, y2 = bbox
            content_width = x2 - x1
            content_height = y2 - y1
            scaled_width = content_width * 0.5
            scaled_height = content_height * 0.5
            margin = 30
            
            # 统一使用：先移到原点 → 缩放 → 再移到目标位置
            self.canvas.move(tk.ALL, -x1, -y1)
            self.canvas.scale(tk.ALL, 0, 0, 0.5, 0.5)
            
            # 水平和垂直方向独立判断位置
            if scaled_width <= canvas_width - margin * 2:
                target_x = (canvas_width - scaled_width) / 2
            else:
                target_x = margin
            
            if scaled_height <= canvas_height - margin * 2:
                target_y = (canvas_height - scaled_height) / 2
            else:
                target_y = margin
            
            self.canvas.move(tk.ALL, target_x, target_y)
            
            # 设置正确的滚动区域（从0,0开始）
            final_bbox = self.canvas.bbox(tk.ALL)
            if final_bbox:
                self.canvas.config(scrollregion=(
                    0, 0,
                    max(canvas_width, final_bbox[2] + margin),
                    max(canvas_height, final_bbox[3] + margin)
                ))
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
            
            self.scale = 0.5
            if hasattr(self, 'scale_label') and self.scale_label:
                self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _expanded_bbox(self, bbox, padding=60):
        """扩展边界框，添加内边距"""
        x1, y1, x2, y2 = bbox
        return (x1 - padding, y1 - padding, x2 + padding, y2 + padding)
    
    def on_mouse_wheel(self, event: tk.Event) -> None:
        """鼠标滚轮缩放 - 以鼠标位置为中心"""
        # 将窗口坐标转换为画布坐标（考虑滚动）
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 计算缩放因子
        if event.delta > 0:
            new_scale: float = self.scale * 1.1
        else:
            new_scale = self.scale * 0.9
        
        # 限制缩放范围
        new_scale = max(0.5, min(new_scale, 1.0))
        
        # 计算缩放比例
        scale_factor: float = new_scale / self.scale
        self.scale = new_scale
        
        # 缩放画布内容 - 以鼠标位置为中心
        self.canvas.scale(tk.ALL, canvas_x, canvas_y, scale_factor, scale_factor)
        
        # 更新缩放比例显示
        if hasattr(self, 'scale_label') and self.scale_label:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _create_shadow(self, points: list[float | int] | None, shadow_x: float, shadow_y: float, width: float, height: float, smooth: bool = False) -> int:
        """通用阴影创建方法
        
        Args:
            points: 顶点坐标列表（相对于 x, y 的偏移量，使用 0-1 之间的相对坐标）
            shadow_x: 阴影起始 x 坐标
            shadow_y: 阴影起始 y 坐标
            width: 宽度
            height: 高度
            smooth: 是否使用平滑（圆角）
        
        Returns:
            int: 阴影对象 ID
        """
        if points is None:
            points = [0.1, 0, 0.9, 0, 1, 0.1, 1, 0.9, 0.9, 1, 0.1, 1, 0, 0.9, 0, 0.1]
        
        shadow_points: list[float] = []
        for i in range(0, len(points), 2):
            px = shadow_x + float(points[i]) * width
            py = shadow_y + float(points[i + 1]) * height
            shadow_points.extend([px, py])
        
        if smooth:
            return self.canvas.create_polygon(*shadow_points, fill="#000000", outline="", smooth=True)
        else:
            return self.canvas.create_polygon(*shadow_points, fill="#000000", outline="")
    
    def create_node_shape(self, x: float, y: float, width: float, height: float, shape: str = "rectangle", 
                          fill: str = NODE_COLOR, outline: str = NODE_BORDER_COLOR, border_width: int = 2, 
                          node_tag: str | None = None) -> tuple[int, list[int], list[int]]:
        """创建不同形状的节点
        
        Args:
            x: x 坐标
            y: y 坐标
            width: 宽度
            height: 高度
            shape: 形状类型
            fill: 填充颜色
            outline: 边框颜色
            border_width: 边框宽度
            node_tag: 节点 tag，用于绑定阴影层
        
        Returns:
            tuple: (shape_id, gradient_items, shadow_items) shape_id 是边框对象的 ID，gradient_items 是所有渐变填充层的 ID 列表，shadow_items 是所有阴影层的 ID 列表
        """
        # 收集所有创建的渐变填充层对象 ID
        gradient_items = []
        # 定义各形状的顶点坐标（使用 0-1 的相对坐标）
        SHAPE_POINTS = {
            "rectangle": [0.1, 0, 0.9, 0, 1, 0.1, 1, 0.9, 0.9, 1, 0.1, 1, 0, 0.9, 0, 0.1],  # 圆角矩形近似
            "rounded_rectangle": [0.15, 0, 0.85, 0, 1, 0.15, 1, 0.85, 0.85, 1, 0.15, 1, 0, 0.85, 0, 0.15],
            "ellipse": None,  # 椭圆特殊处理
            "circle": None,  # 圆形特殊处理
            "diamond": [0.5, 0, 1, 0.5, 0.5, 1, 0, 0.5],
            "triangle": [0.5, 0, 1, 1, 0, 1],
            "hexagon": [0.5, 0, 1, 0.33, 1, 0.67, 0.5, 1, 0, 0.67, 0, 0.33],
            "pentagon": [0.5, 0, 1, 0.5, 0.8, 1, 0.2, 1, 0, 0.5],
            "octagon": [0.3, 0, 0.7, 0, 1, 0.3, 1, 0.7, 0.7, 1, 0.3, 1, 0, 0.7, 0, 0.3],
            "star": [0.5, 0, 0.75, 0.28, 1, 0.35, 0.88, 0.52, 1, 0.65, 0.75, 0.75, 0.5, 1, 0.25, 0.75, 0, 0.65, 0.12, 0.52, 0, 0.35, 0.25, 0.28],
            "trapezoid": [0.15, 0, 0.85, 0, 1, 1, 0, 1],
            "parallelogram": [0.2, 0, 1, 0, 0.8, 1, 0, 1]
        }
        
        # 收集所有创建的阴影层对象 ID
        shadow_items = []
        
        # 添加阴影效果
        shadow_offset = 3
        
        for i in range(3):
            shadow_x = x + shadow_offset * (i + 1)
            shadow_y = y + shadow_offset * (i + 1)
            
            # 使用通用方法创建阴影
            if shape in ["ellipse", "circle"]:
                # 椭圆和圆形特殊处理
                shadow_id = self.canvas.create_oval(
                    shadow_x, shadow_y, shadow_x + width, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
            elif shape in ["rectangle", "rounded_rectangle"]:
                # 矩形和圆角矩形需要平滑效果
                shadow_id = self._create_shadow(SHAPE_POINTS[shape], shadow_x, shadow_y, width, height, smooth=True)
            elif shape in SHAPE_POINTS:
                # 使用通用方法创建多边形阴影
                shadow_id = self._create_shadow(SHAPE_POINTS[shape], shadow_x, shadow_y, width, height)
            else:
                # 默认使用矩形
                shadow_id = self._create_shadow(SHAPE_POINTS.get("rectangle", []), shadow_x, shadow_y, width, height, smooth=True)
            
            shadow_items.append(shadow_id)
            # 如果提供了 node_tag，立即绑定
            if node_tag:
                self.canvas.itemconfig(shadow_id, tags=(node_tag,))
        
        # 创建主形状
        if shape == "rectangle":
            # 创建圆角矩形
            radius = 10
            # 创建渐变效果（使用多层叠加）
            gradient_items: list[int] = []
            shadow_items: list[int] = []
            for i in range(3):
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
                # 绑定 tag 到渐变层
                if node_tag:
                    self.canvas.itemconfig(item, tags=(node_tag,))
            
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
            # 绑定 tag 到边框
            if node_tag:
                self.canvas.itemconfig(shape_id, tags=(node_tag,))
            return shape_id, gradient_items, shadow_items
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
                # 绑定 tag 到渐变层
                if node_tag:
                    self.canvas.itemconfig(item, tags=(node_tag,))
            
            # 边框层最后创建，并提升到最顶层，确保鼠标事件优先命中边框
            shape_id = self.canvas.create_oval(
                x, y, x + width, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            # 关键：将边框提升到所有填充层之上，解决椭圆内部无法触发悬停的问题
            # 绑定 tag 到边框
            if node_tag:
                self.canvas.itemconfig(shape_id, tags=(node_tag,))
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "diamond":
            # 创建菱形 - 四个顶点分别在边界框的四边中点
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + width / 2, y,          # 上顶点
                    x + width, y + height / 2,  # 右顶点
                    x + width / 2, y + height,  # 下顶点
                    x, y + height / 2,          # 左顶点
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
                # 绑定 tag 到渐变层
                if node_tag:
                    self.canvas.itemconfig(item, tags=(node_tag,))
            
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
            # 绑定 tag 到边框
            if node_tag:
                self.canvas.itemconfig(shape_id, tags=(node_tag,))
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "triangle":
            # 创建三角形 - 顶点在边界框的上边中点和底边两角
            # 创建渐变效果
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + width / 2, y,              # 上顶点
                    x + width, y + height,          # 右下角
                    x, y + height,                  # 左下角
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
            return shape_id, gradient_items, shadow_items
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
            return shape_id, gradient_items, shadow_items
        elif shape == "hexagon":
            # 创建六边形 - 顶点在边界框的边缘
            # 左右顶点在左右边界上，确保与其他形状对齐
            points = [
                x + width / 2, y,                  # 上
                x + width, y + height / 3,         # 右上
                x + width, y + height * 2 / 3,     # 右下
                x + width / 2, y + height,         # 下
                x, y + height * 2 / 3,             # 左下
                x, y + height / 3                  # 左上
            ]
            
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
            return shape_id, gradient_items, shadow_items
        elif shape == "pentagon":
            # 创建五边形 - 顶点在边界框的边缘
            # 五边形：上顶点在上边中点，左右顶点在左右边中点，底部两个顶点在底边
            points = [
                x + width / 2, y,                  # 上
                x + width, y + height / 2,          # 右中
                x + width * 0.8, y + height,        # 右下
                x + width * 0.2, y + height,        # 左下
                x, y + height / 2                   # 左中
            ]
            
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
            return shape_id, gradient_items, shadow_items
        elif shape == "octagon":
            # 创建八边形 - 顶点在边界框边缘
            # 左右两侧有垂直的边，确保连接线可以对齐
            points = [
                x + width * 0.3, y,                # 上中左
                x + width * 0.7, y,                # 上中右
                x + width, y + height * 0.3,       # 右上
                x + width, y + height * 0.7,       # 右下
                x + width * 0.7, y + height,       # 下中右
                x + width * 0.3, y + height,       # 下中左
                x, y + height * 0.7,               # 左下
                x, y + height * 0.3                # 左上
            ]
            
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
            return shape_id, gradient_items, shadow_items
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
            return shape_id, gradient_items, shadow_items
        elif shape == "star":
            # 创建星形 - 外顶点不动，内点位置调整
            points = [
                x + width / 2, y,                         # 上顶点（保持顶部边缘）
                x + width * 0.75, y + height * 0.28,      # 右上内点（往外调一点）
                x + width, y + height * 0.35,             # 右顶点（保持右边缘）
                x + width * 0.88, y + height * 0.52,      # 右内点（往外，远离中心）
                x + width, y + height * 0.65,             # 右下顶点（保持右边缘）
                x + width * 0.75, y + height * 0.75,      # 下右内点（向外移动）
                x + width / 2, y + height,                # 下顶点（保持底部边缘）
                x + width * 0.25, y + height * 0.75,      # 下左内点（向外移动）
                x, y + height * 0.65,                     # 左下顶点（保持左边缘）
                x + width * 0.12, y + height * 0.52,      # 左内点（往外，远离中心）
                x, y + height * 0.35,                     # 左顶点（保持左边缘）
                x + width * 0.25, y + height * 0.28       # 左上内点（往外调一点）
            ]
            
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
            return shape_id, gradient_items, shadow_items
        elif shape == "trapezoid":
            # 创建梯形
            top_width = width * 0.7
            
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
            return shape_id, gradient_items, shadow_items
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
            return shape_id, gradient_items, shadow_items
        else:
            shape_id = self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
            return shape_id, gradient_items, shadow_items
    
    def add_node(self, name: str, subnet: str, level: int = 0, subnet_type: str = "default", device_type: str = "default", ip_info: dict[str, Any] | None = None, parent_id: str | None = None) -> str:
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
            x = float(parent_node["x"]) + NODE_SPACING  # 水平间距
            # 计算父节点的子节点数量，确保子节点均匀分布
            child_count = sum(1 for n in self.nodes.values() if n.get("parent_id") == parent_id)
            # 计算子节点的垂直位置，确保父节点居中
            y = float(parent_node["y"]) + (child_count - 1) * (NODE_HEIGHT + 60) - (child_count * (NODE_HEIGHT + 60)) / 2 + NODE_HEIGHT / 2
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
        shape_tuple = self.create_node_shape(
            x, y, NODE_WIDTH, NODE_HEIGHT, 
            shape=node_shape, 
            fill=node_color,
            outline=NODE_BORDER_COLOR,
            border_width=2,
            node_tag=node_id  # 传入 node_id，让阴影层也绑定 tag
        )
        shape_id = shape_tuple[0]
        gradient_items = shape_tuple[1] if len(shape_tuple) > 1 else []
        shadow_items = shape_tuple[2] if len(shape_tuple) > 2 else []
        
        # 获取字体设置
        font_family, font_size = get_current_font_settings()
        
        # 创建节点文本
        text_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT / 4,
            text=name,
            font=(font_family, font_size - 2, "bold"),
            fill=TEXT_COLOR
        )
        
        # 创建子网文本
        subnet_text = str(subnet)
        if len(subnet_text) > 20:
            subnet_text = subnet_text[:17] + "..."
        
        subnet_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT / 2,
            text=subnet_text,
            font=(font_family, font_size - 3),
            fill=TEXT_COLOR
        )
        
        # 创建IP信息文本
        ip_info_text = ""
        if ip_info:
            total_ips = ip_info.get("total", 0)
            allocated = ip_info.get("allocated", 0)
            reserved = ip_info.get("reserved", 0)
            used_ips = allocated + reserved
            
            from ip_subnet_calculator import format_large_number
            used_ips_str = format_large_number(used_ips, use_scientific=True)
            total_ips_str = format_large_number(total_ips, use_scientific=True)
            ip_info_text = f"{used_ips_str}/{total_ips_str}"
        
        ip_info_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT * 3 / 4,
            text=ip_info_text,
            font=(font_family, font_size - 4),
            fill=TEXT_COLOR
        )
        
        # 关键：将所有属于该节点的画布对象绑定到统一的 tag
        # 包括：形状边框层 + 渐变填充层 + 阴影层 + 文本对象
        all_node_items = [shape_id, text_id, subnet_id, ip_info_id] + gradient_items + shadow_items
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
    
    def add_link(self, source_node_id: str, target_node_id: str) -> None:
        """添加连接
        
        Args:
            source_node_id: 源节点ID
            target_node_id: 目标节点ID
        """
        if source_node_id in self.nodes and target_node_id in self.nodes:
            source = self.nodes[source_node_id]
            target = self.nodes[target_node_id]
            
            # 计算连接线坐标
            x1: float = float(source["x"]) + NODE_WIDTH
            y1: float = float(source["y"]) + NODE_HEIGHT / 2
            x2: float = float(target["x"])
            y2: float = float(target["y"]) + NODE_HEIGHT / 2
            
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
        # 保存网络数据供后续使用（如全屏模式）
        self.network_data = network_data
        
        # 重置缩放标志，允许新的自适应缩放
        self._scaled = False
        self._pending_initial_scale = False
        
        # 取消之前的延迟缩放定时器
        if self._auto_scale_timer is not None:
            self.canvas.after_cancel(self._auto_scale_timer)
            self._auto_scale_timer = None
        
        # 临时移除画布，防止绘制过程中的闪现
        self.canvas.pack_forget()
        
        self.clear()
        
        # 存储节点ID映射
        node_id_map = {}
        
        # 过滤节点
        filtered_data = self._filter_nodes(network_data)
        
        # 限制节点数量
        if len(filtered_data) > self.max_nodes:
            filtered_data = filtered_data[:self.max_nodes]
        
        # 构建网络层次结构，先处理父节点，再处理子节点
        # 按层级排序，同层级按 CIDR 排序
        sorted_data = sorted(filtered_data, key=lambda x: (x.get("level", 0), self._cidr_to_sort_key(x.get("cidr", ""))))
        
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
        
        # 更新滚动区域：使用update_idletasks()替代update()以避免不必要的重绘和视觉闪烁
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(tk.ALL)
        if bbox:
            x1, y1, x2, y2 = bbox
            content_width = x2 - x1
            content_height = y2 - y1
            padding = 30
            
            # 获取画布可视区域尺寸
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 如果画布尺寸未初始化，尝试从父容器获取
            if canvas_width <= 1 or canvas_height <= 1:
                parent = self.canvas.nametowidget(self.canvas.winfo_parent())
                if parent:
                    parent.update_idletasks()
                    canvas_width = parent.winfo_width()
                    canvas_height = parent.winfo_height()
            
            # 如果仍然无法获取有效尺寸，延迟重试
            if canvas_width <= 1 or canvas_height <= 1:
                self.canvas.config(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))
                self.canvas.xview_moveto(0)
                self.canvas.yview_moveto(0)
                # 标记需要初始缩放，等待画布可见时由on_canvas_frame_configure触发
                self._pending_initial_scale = True
                # 不在此处重新显示画布，避免未缩放内容闪现
                # 延迟执行缩放作为兜底（如果Configure事件未触发）
                self._auto_scale_timer = self.canvas.after(200, self._auto_scale_canvas)
                return
            
            # 计算缩放比例
            scale_x = (canvas_width - 2 * padding) / content_width if content_width > 0 else 1.0
            scale_y = (canvas_height - 2 * padding) / content_height if content_height > 0 else 1.0
            scale_factor = min(scale_x, scale_y)
            scale_factor = max(0.5, min(scale_factor, 1.0))
            
            # 应用缩放
            if scale_factor < 1.0:
                self.canvas.move(tk.ALL, -x1, -y1)
                self.canvas.scale(tk.ALL, 0, 0, scale_factor, scale_factor)
                
                scaled_width = content_width * scale_factor
                scaled_height = content_height * scale_factor
                
                if scaled_width <= canvas_width - 2 * padding:
                    target_x = (canvas_width - scaled_width) / 2
                else:
                    target_x = padding
                
                if scaled_height <= canvas_height - 2 * padding:
                    target_y = (canvas_height - scaled_height) / 2
                else:
                    target_y = padding
                
                self.canvas.move(tk.ALL, target_x, target_y)
                
                self.scale = scale_factor
                if hasattr(self, 'scale_label') and self.scale_label:
                    self.scale_label.config(text=f"{int(self.scale * 100)}%")
            else:
                # 不需要缩放，也要居中
                self.canvas.move(tk.ALL, -x1, -y1)
                
                if content_width <= canvas_width - 2 * padding:
                    target_x = (canvas_width - content_width) / 2
                else:
                    target_x = padding
                
                if content_height <= canvas_height - 2 * padding:
                    target_y = (canvas_height - content_height) / 2
                else:
                    target_y = padding
                
                self.canvas.move(tk.ALL, target_x, target_y)
            
            # 更新滚动区域
            final_bbox = self.canvas.bbox(tk.ALL)
            if final_bbox:
                self.canvas.config(scrollregion=(
                    0, 0,
                    max(canvas_width, final_bbox[2] + padding),
                    max(canvas_height, final_bbox[3] + padding)
                ))
            
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
        else:
            self.canvas.config(scrollregion=(0, 0, 1000, 800))
        
        # 重新显示画布
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 标记缩放已完成
        self._scaled = True
        self._pending_initial_scale = False
        if self._auto_scale_timer is not None:
            self.canvas.after_cancel(self._auto_scale_timer)
            self._auto_scale_timer = None
        
        # 重置首次绘制标志
        if self._is_first_draw:
            self._is_first_draw = False
    
    def _auto_scale_canvas(self):
        """画布初始化后延迟执行自适应缩放"""
        # 检查是否已经缩放过（避免重复缩放）
        if getattr(self, '_scaled', False):
            return
        
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            parent = self.canvas.nametowidget(self.canvas.winfo_parent())
            if parent:
                parent.update_idletasks()
                canvas_width = parent.winfo_width()
                canvas_height = parent.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self._auto_scale_timer = self.canvas.after(200, self._auto_scale_canvas)
            return
        
        bbox = self.canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        padding = 30
        
        if content_width <= 0 or content_height <= 0:
            return
        
        scale_x = (canvas_width - 2 * padding) / content_width
        scale_y = (canvas_height - 2 * padding) / content_height
        scale_factor = min(scale_x, scale_y)
        scale_factor = max(0.5, min(scale_factor, 1.0))
        
        # 先移动到原点
        self.canvas.move(tk.ALL, -x1, -y1)
        
        if scale_factor < 1.0:
            self.canvas.scale(tk.ALL, 0, 0, scale_factor, scale_factor)
            self.scale = scale_factor
            if hasattr(self, 'scale_label') and self.scale_label:
                self.scale_label.config(text=f"{int(self.scale * 100)}%")
            
            scaled_width = content_width * scale_factor
            scaled_height = content_height * scale_factor
        else:
            scaled_width = content_width
            scaled_height = content_height
        
        # 水平和垂直方向独立判断位置
        if scaled_width <= canvas_width - 2 * padding:
            target_x = (canvas_width - scaled_width) / 2
        else:
            target_x = padding
        
        if scaled_height <= canvas_height - 2 * padding:
            target_y = (canvas_height - scaled_height) / 2
        else:
            target_y = padding
        
        self.canvas.move(tk.ALL, target_x, target_y)
        
        final_bbox = self.canvas.bbox(tk.ALL)
        if final_bbox:
            self.canvas.config(scrollregion=(
                0, 0,
                max(canvas_width, final_bbox[2] + padding),
                max(canvas_height, final_bbox[3] + padding)
            ))
        
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        
        # 标记缩放已完成
        self._scaled = True
        self._pending_initial_scale = False
        self._auto_scale_timer = None
        
        # 确保画布已显示（如果之前因延迟缩放而隐藏）
        if not self.canvas.winfo_ismapped():
            self.canvas.pack(fill=tk.BOTH, expand=True)
    
    def _reposition_all_nodes(self):
        """重新计算所有节点的位置，实现树形层级布局
        
        布局规则:
        1. 根节点在最左侧
        2. 层级从左到右展开，每层 X 坐标固定
        3. 父节点与第一个子节点垂直对齐
        4. 同级节点垂直紧凑排列
        5. 使用直角折线连接
        """
        if not self.nodes:
            return
        
        # 构建父子关系映射
        parent_to_children = {}
        root_nodes = []
        
        for _node_id, node in self.nodes.items():
            parent_id = node.get("parent_id")
            if parent_id is None or parent_id not in self.nodes:
                root_nodes.append(node)
            else:
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(node)
        
        if not root_nodes:
            return
        
        root_nodes.sort(key=lambda x: self._cidr_to_sort_key(x.get("cidr", "")))
        
        for parent_id in parent_to_children:
            parent_to_children[parent_id].sort(key=lambda x: self._cidr_to_sort_key(x.get("cidr", "")))
        
        # 计算每个层级的水平位置
        level_x = {}
        max_level = max(int(node.get("level", 0)) for node in self.nodes.values())
        for level in range(max_level + 1):
            level_x[level] = 50 + level * NODE_SPACING
        
        vertical_spacing = 15  # 子节点之间的垂直间距
        
        # 获取节点的实际高度（考虑特殊形状）
        def get_node_height(node):
            _device_type = node.get("device_type", "default")
            base_height = NODE_HEIGHT
            # 所有形状的实际边界框高度都是 NODE_HEIGHT
            # 不需要额外空间，因为所有形状的顶点都在边界框边缘
            return base_height
        
        # 递归计算子树高度
        def calculate_subtree_height(node):
            children = parent_to_children.get(node["id"], [])
            if not children:
                return get_node_height(node)
            total = sum(calculate_subtree_height(child) for child in children)
            return total + vertical_spacing * (len(children) - 1)
        
        # 递归分配位置
        def assign_positions(node, start_y):
            node["x"] = level_x.get(node.get("level", 0), 100)
            children = parent_to_children.get(node["id"], [])
            node_height = get_node_height(node)
            
            if not children:
                # 叶子节点
                node["y"] = start_y
                return node_height
            
            # 有子节点：先计算所有子节点的位置
            current_y = start_y
            for i, child in enumerate(children):
                child_height = assign_positions(child, current_y)
                if i == 0:
                    # 父节点与第一个子节点对齐
                    node["y"] = current_y
                current_y += child_height + vertical_spacing
            
            return current_y - start_y
        
        # 从根节点开始布局
        current_y = 30
        for root in root_nodes:
            height = calculate_subtree_height(root)
            # 垂直居中 - 使用 800 作为画布高度，而不是 600
            start_y = current_y + (800 - height) / 2 if height < 800 else current_y
            assign_positions(root, start_y)
            current_y += height + 30
        
        # 移动节点到新位置
        self._move_all_nodes_to_new_positions()
    
    def _move_all_nodes_to_new_positions(self):
        """移动所有节点和连接线到新的位置"""
        # 删除所有连接线
        for link in self.links:
            link_id = link.get("id")
            if link_id is not None:
                self.canvas.delete(link_id)
        self.links = []
        
        # 移动每个节点到新位置
        for node_id, node in self.nodes.items():
            try:
                # 使用 bbox 获取边界框，而不是 coords（coords 返回的是顶点坐标，不是边界框）
                shape_id = node.get("shape")
                if shape_id is None:
                    continue
                bbox = self.canvas.bbox(shape_id)
                if bbox:
                    current_x = bbox[0]  # 左边界
                    current_y = bbox[1]  # 上边界
                else:
                    continue
            except (IndexError, TypeError, ValueError):
                continue
            dx: float = float(node["x"]) - current_x
            dy: float = float(node["y"]) - current_y
            # 添加 Y 轴偏移量，向上移动 3 像素，修正连接线位置
            dy -= 3
            # 移动所有绑定了 node_id tag 的对象
            items_to_move = self.canvas.find_withtag(node_id)
            for item in items_to_move:
                self.canvas.move(item, dx, dy)
        
        # 重新绘制连接线
        self._redraw_all_links()
    
    def _redraw_all_links(self):
        """重新绘制所有连接线（使用直角折线）"""
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
                
                # 计算连接点（从源节点右侧到目标节点左侧）
                # 所有形状的左右顶点都在边界框边缘，统一使用边界框坐标
                # 添加 3 像素偏移量，避免连接线穿入节点
                x1: float = float(source_node["x"]) + NODE_WIDTH + 13  # 源节点右侧 + 13 像素偏移
                y1: float = float(source_node["y"]) + NODE_HEIGHT / 2  # 垂直中心
                x2: float = float(target_node["x"])  # 目标节点左侧
                y2: float = float(target_node["y"]) + NODE_HEIGHT / 2  # 垂直中心
                
                # 创建直角折线
                mid_x = x1 + (x2 - x1) / 2  # 转折点 X 坐标
                
                # 绘制折线：水平 → 垂直 → 水平
                line = self.canvas.create_line(  # pyright: ignore[reportCallIssue]
                    x1, y1,
                    mid_x, y1,
                    mid_x, y2,
                    x2, y2,
                    arrow=tk.LAST,
                    width=2,
                    fill="#CCCCCC",
                    smooth=False,
                    tags="link"
                )
                self.links.append({
                    "source": parent_id,
                    "target": node_id,
                    "line": line
                })
        
        # 将所有连接线提升到最上层，确保连接线不被节点遮挡
        for link in self.links:
            self.canvas.tag_raise(link["line"])
        
        # 强制更新画布，确保所有内容都已渲染完成
        self.canvas.update_idletasks()
    
    def auto_scale_to_fit(self, retry_count=0, center_x=None, center_y=None):
        """自动缩放画布以适应所有节点
        
        Args:
            retry_count: 重试次数（内部使用）
            center_x: 缩放中心X坐标，如果为None则使用内容中心
            center_y: 缩放中心Y坐标，如果为None则使用内容中心
        """
        bbox = self.canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        # 确保画布已完全初始化
        self.canvas.update_idletasks()
        
        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 如果画布尺寸还没有正确获取，尝试从父容器获取
        if canvas_width <= 1 or canvas_height <= 1:
            # 先更新父容器
            if self.parent:
                self.parent.update_idletasks()
                canvas_width = self.parent.winfo_width()
                canvas_height = self.parent.winfo_height()
        
        # 如果还是没有正确获取尺寸，延迟重试（最多重试50次，每次50ms，共2.5秒）
        if canvas_width <= 1 or canvas_height <= 1:
            if retry_count < 50:
                # 延迟重试，等待GUI初始化完成
                self.canvas.after(50, lambda: self.auto_scale_to_fit(retry_count + 1, center_x, center_y))
                return
            else:
                # 多次重试后仍无法获取尺寸，记录日志并返回
                print(f"警告: 无法获取画布尺寸，重试次数: {retry_count}")
                return
        
        # 计算所有节点的边界框
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        
        if content_width <= 0 or content_height <= 0:
            return
        
        # 计算缩放比例，使用更小的边距以充分利用空间
        margin = 15  # 最小边距，让内容更大
        scale_x = (canvas_width - 2 * margin) / content_width
        scale_y = (canvas_height - 2 * margin) / content_height
        target_scale_factor = min(scale_x, scale_y)
        
        # 限制缩放范围（允许更大的缩放比例，最大可放大到原始的1倍）
        target_scale_factor = max(0.5, min(target_scale_factor, 1.0))
        
        # 计算实际缩放因子（相对于当前缩放）
        scale_factor = target_scale_factor / self.scale
        
        # 确定缩放中心
        if center_x is None or center_y is None:
            # 使用内容中心
            scale_center_x = (x1 + x2) / 2
            scale_center_y = (y1 + y2) / 2
        else:
            # 使用指定的缩放中心（鼠标点击位置）
            scale_center_x = center_x
            scale_center_y = center_y
        
        # 应用缩放
        if scale_factor != 1.0:
            # 缩放所有内容
            self.canvas.scale(tk.ALL, scale_center_x, scale_center_y, scale_factor, scale_factor)
        
        # 更新缩放因子（关键修复：之前没有更新self.scale）
        self.scale = target_scale_factor
        
        # 更新缩放比例显示
        if hasattr(self, 'scale_label') and self.scale_label:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
        
        # 更新滚动区域
        self.canvas.update_idletasks()
        new_bbox = self.canvas.bbox(tk.ALL)
        if new_bbox:
            x1, y1, x2, y2 = new_bbox
            
            # 获取画布实际尺寸
            actual_width = self.canvas.winfo_width()
            actual_height = self.canvas.winfo_height()
            
            # 计算内容实际占据的区域
            content_width = x2 - x1
            content_height = y2 - y1
            
            # 如果内容小于画布尺寸，不添加额外边距，避免显示滚动条
            if content_width < actual_width and content_height < actual_height:
                # 内容已经适合画布，使用最小边距，确保滚动区域不超过画布
                padding = 15
            else:
                # 内容超出画布，添加适当边距
                padding = 30
            
            self.canvas.config(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))
        
        # 滚动到画布左上角，确保用户可以从开始查看
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
    
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
        # 拖拽期间不处理悬停检测，避免性能问题
        if self.dragging:
            return
        
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
        canvas: Canvas = self.fullscreen_canvas if self.is_fullscreen and self.fullscreen_canvas else self.canvas
        self._hover_poll_job = canvas.after(50, self._check_hover_state)

    def _stop_hover_polling(self):
        """停止悬停轮询检测定时器"""
        if self._hover_poll_job:
            try:
                canvas: Canvas = self.fullscreen_canvas if self.is_fullscreen and self.fullscreen_canvas else self.canvas
                canvas.after_cancel(self._hover_poll_job)
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
            # 确定使用哪个画布
            canvas: Canvas = self.fullscreen_canvas if self.is_fullscreen and self.fullscreen_canvas else self.canvas
            
            # 获取当前鼠标在画布上的坐标
            x = canvas.winfo_pointerx() - canvas.winfo_rootx()
            y = canvas.winfo_pointery() - canvas.winfo_rooty()
            
            # 转换为画布坐标
            canvas_x = canvas.canvasx(x)
            canvas_y = canvas.canvasy(y)
            
            # 检查鼠标是否仍在当前悬停节点上（通过 tag 匹配）
            overlapping = canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
            still_on_node = False
            for item_id in overlapping:
                tags = canvas.gettags(item_id)
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
            self._hover_poll_job = canvas.after(50, self._check_hover_state)
        except (tk.TclError, Exception):
            # 画布可能已被销毁，停止轮询
            pass

    def _restore_all_hover_styles(self):
        """恢复所有处于悬停状态的节点的原始样式"""
        for _node_id, node in list(self.nodes.items()):
            if "original_style" in node:
                self._restore_node_style(node)

    def _apply_hover_style(self, node):
        """应用节点悬停样式
        
        Args:
            node: 节点信息
        """
        # 确定使用哪个画布
        canvas: Canvas = self.fullscreen_canvas if self.is_fullscreen and self.fullscreen_canvas is not None else self.canvas
        
        # 保存原始样式
        if "original_style" not in node:
            # 获取宽度值，处理空字符串和浮点数情况
            width_str = canvas.itemcget(node["shape"], "width")
            try:
                line_width = int(float(width_str)) if width_str else 2
            except (ValueError, TypeError):
                line_width = 2
            
            # 获取 outline，处理不支持该选项的节点类型
            outline = None
            try:
                outline = canvas.itemcget(node["shape"], "outline")
            except Exception:
                pass
            
            node["original_style"] = {
                "outline": outline,
                "line_width": line_width
            }
        
        # 更改节点样式 - 仅修改边框和宽度
        try:
            if node["original_style"]["outline"] is not None:
                canvas.itemconfig(node["shape"], outline="#ffffff", width=3)
            else:
                canvas.itemconfig(node["shape"], width=3)
        except Exception:
            pass
        
        # 提升节点到顶层
        try:
            canvas.tag_raise(node["shape"])
            canvas.tag_raise(node["text"])
            canvas.tag_raise(node["subnet_text"])
            canvas.tag_raise(node["ip_info_text"])
        except Exception:
            pass

    def _restore_node_style(self, node):
        """恢复节点原始样式
        
        Args:
            node: 节点信息
        """
        # 确定使用哪个画布
        canvas: Canvas = self.fullscreen_canvas if self.is_fullscreen and self.fullscreen_canvas is not None else self.canvas
        
        if "original_style" in node:
            original = node["original_style"]
            
            # 恢复节点样式
            canvas.itemconfig(node["shape"], 
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
        
        # 创建提示内容
        frame = tk.Frame(self.tooltip, bg="#333", padx=10, pady=5)
        frame.pack()
        
        # 绑定tooltip的Leave事件：当鼠标离开tooltip时也恢复样式
        def on_tooltip_leave(_event):
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
            from ip_subnet_calculator import format_large_number
            
            allocated = node["ip_info"].get("allocated", 0)
            reserved = node["ip_info"].get("reserved", 0)
            available = node["ip_info"].get("available", 0)
            total = node["ip_info"].get("total", 0)
            network_broadcast = 2 if total > 2 else 0
            remaining = max(0, total - network_broadcast - allocated - reserved)
            
            allocated_str = format_large_number(allocated, use_scientific=True)
            reserved_str = format_large_number(reserved, use_scientific=True)
            available_str = format_large_number(available, use_scientific=True)
            remaining_str = format_large_number(remaining, use_scientific=True)
            total_str = format_large_number(total, use_scientific=True)
            
            tk.Label(
                frame, 
                text=f"已分配: {allocated_str}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"已保留: {reserved_str}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"已释放: {available_str}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"剩余IP: {remaining_str}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"总IP: {total_str}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
        
        # 强制更新以获取实际尺寸
        self.tooltip.update_idletasks()
        
        # 获取tooltip实际尺寸
        tooltip_width = self.tooltip.winfo_width()
        tooltip_height = self.tooltip.winfo_height()
        
        # 获取父窗口的边界（考虑窗口模式和全屏模式）
        if self.is_fullscreen:
            # 全屏模式：使用屏幕边界
            screen_width = self.tooltip.winfo_screenwidth()
            screen_height = self.tooltip.winfo_screenheight()
            min_x = 0
            min_y = 0
        else:
            # 窗口模式：使用父窗口边界
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            screen_width = parent_x + parent_width
            screen_height = parent_y + parent_height
            min_x = parent_x
            min_y = parent_y
        
        # 默认显示在鼠标右下方
        tooltip_x = x_root + 15
        tooltip_y = y_root + 10
        
        # 如果tooltip右侧超出边界，显示在鼠标左侧
        if tooltip_x + tooltip_width > screen_width:
            tooltip_x = x_root - tooltip_width - 15
        
        # 如果tooltip底部超出边界，显示在鼠标上方
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = y_root - tooltip_height - 15
        
        # 确保不超出左侧和顶部边界
        tooltip_x = max(min_x, tooltip_x)
        tooltip_y = max(min_y, tooltip_y)
        
        # 设置最终位置
        self.tooltip.wm_geometry(f"+{tooltip_x}+{tooltip_y}")
    
    def hide_tooltip(self):
        """隐藏提示窗口"""
        # 取消定时器
        if self.tooltip_timer:
            try:
                canvas: Canvas = self.fullscreen_canvas if self.is_fullscreen and self.fullscreen_canvas else self.canvas
                canvas.after_cancel(self.tooltip_timer)
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
    
    def on_canvas_leave(self, _event):
        """鼠标离开画布事件处理"""
        # 停止轮询检测
        self._stop_hover_polling()
        
        # 恢复所有节点的原始样式
        self._restore_all_hover_styles()
        
        # 隐藏提示窗口
        self.hide_tooltip()
    
    def on_canvas_frame_configure(self, event):
        """当父容器大小变化时调整画布大小"""
        # 获取父容器的新大小
        width = event.width
        height = event.height
        
        # 调整画布大小
        self.canvas.config(width=width, height=height)
        
        # 重置悬停状态
        self.hovered_node = None
        
        # 更新全屏按钮位置
        self._update_fullscreen_button_position()
        
        # 如果内容尚未缩放且画布有有效尺寸，立即执行自适应缩放
        # 这解决了初次切换到拓扑页面时图案从大到小闪现的问题
        if getattr(self, '_pending_initial_scale', False) and width > 1 and height > 1 and self.nodes:
            # 取消延迟缩放定时器
            if getattr(self, '_auto_scale_timer', None) is not None:
                timer_id = self._auto_scale_timer
                assert timer_id is not None
                self.canvas.after_cancel(timer_id)
                self._auto_scale_timer = None
            
            # 重新显示画布并立即执行缩放
            self.canvas.pack(fill=tk.BOTH, expand=True)
            self._auto_scale_canvas()
            self._pending_initial_scale = False
    
    def _create_fullscreen_button(self):
        """创建全屏显示按钮"""
        self.fullscreen_button: tk.Button = tk.Button(
            self.canvas,
            text="⛶",
            command=self.toggle_fullscreen,
            bg="#3498db",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=4,
            pady=2,
            font=("Arial", 10),
            cursor="hand2"
        )
        self.fullscreen_button.place(relx=1.0, rely=0.0, x=-12, y=12, anchor=tk.NE)
        self.fullscreen_button.bind("<Enter>", lambda e: self.fullscreen_button.config(bg="#2980b9"))
        self.fullscreen_button.bind("<Leave>", lambda e: self.fullscreen_button.config(bg="#3498db"))
        
        # 全屏状态
        self.is_fullscreen = False
    
    def _update_fullscreen_button_position(self):
        """更新全屏按钮位置"""
        if hasattr(self, 'fullscreen_button'):
            self.fullscreen_button.place(relx=1.0, rely=0.0, x=-12, y=12, anchor=tk.NE)
    
    def toggle_fullscreen(self):
        """切换全屏显示状态"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """进入全屏显示模式"""
        # 保存当前缩放因子
        self.original_scale = self.scale
        
        # 创建全屏顶层窗口
        self.fullscreen_window = tk.Toplevel()
        self.fullscreen_window.title("网络拓扑图 - 全屏模式")
        self.fullscreen_window.attributes("-fullscreen", True)
        self.fullscreen_window.config(bg=BACKGROUND_COLOR, bd=0, highlightthickness=0)
        
        # 设置全屏窗口为最顶层并获取焦点
        self.fullscreen_window.lift()
        self.fullscreen_window.focus_set()
        
        # 创建新画布（无边框）
        self.fullscreen_canvas = Canvas(
            self.fullscreen_window,
            bg=BACKGROUND_COLOR,
            bd=0,
            highlightthickness=0
        )
        self.fullscreen_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 保存原始画布引用，用于退出时恢复
        self.original_canvas = self.canvas
        
        # 切换到全屏画布
        self.canvas = self.fullscreen_canvas
        
        # 延迟执行视图设置（包含绘制和缩放，避免闪现）
        self.canvas.after(100, self._apply_fullscreen_view)
    
    def _apply_fullscreen_view(self):
        """应用全屏视图设置"""
        assert self.fullscreen_canvas is not None
        # 临时移除画布，防止变换过程中的闪现
        self.fullscreen_canvas.pack_forget()
        
        # 绘制并缩放拓扑图
        self._redraw_and_fit_fullscreen()
        
        # 重新显示画布
        self.fullscreen_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 确保视图从左上角开始
        self.fullscreen_canvas.xview_moveto(0)
        self.fullscreen_canvas.yview_moveto(0)
        
        # 强制刷新
        self.fullscreen_canvas.update_idletasks()
        
        # 创建缩放控制面板
        self._create_fullscreen_controls()
        if self.scale_label is not None:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _redraw_and_fit_fullscreen(self):
        """重新绘制拓扑图并自适应缩放以适应全屏窗口"""
        assert self.fullscreen_canvas is not None
        
        # 确保画布已完全初始化
        self.fullscreen_canvas.update_idletasks()
        
        # 获取画布尺寸
        canvas_width = self.fullscreen_canvas.winfo_width()
        canvas_height = self.fullscreen_canvas.winfo_height()
        
        # 清空画布
        self.fullscreen_canvas.delete(tk.ALL)
        self.nodes.clear()
        self.links.clear()
        
        # 临时保存原始画布引用
        original_canvas = self.canvas
        
        # 设置全屏画布为当前画布
        self.canvas = self.fullscreen_canvas
        
        # 重置缩放标志，允许draw_topology执行缩放
        self._scaled = False
        
        # 绘制拓扑图（会自动执行自适应缩放）
        self.draw_topology(self.network_data)
        
        # 恢复原始画布引用
        self.canvas = original_canvas
        
        # 由于draw_topology已经执行了自适应缩放，这里不需要再执行缩放
        # 获取缩放后的边界框来设置滚动区域
        final_bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if final_bbox:
            # 设置滚动区域正好包含内容
            self.fullscreen_canvas.config(
                scrollregion=(
                    0, 0,
                    max(canvas_width, final_bbox[2] + 30),
                    max(canvas_height, final_bbox[3] + 30)
                )
            )
        else:
            self.fullscreen_canvas.config(scrollregion=(0, 0, canvas_width, canvas_height))
        
        # 强制刷新画布
        self.fullscreen_canvas.update_idletasks()
        
        # 添加退出全屏按钮
        self.exit_fullscreen_button = tk.Button(
            self.fullscreen_window,
            text="✕",
            command=self.exit_fullscreen,
            bg="#e74c3c",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=4,
            pady=2,
            font=("Arial", 10),
            cursor="hand2",
            activebackground="#c0392b"
        )
        self.exit_fullscreen_button.place(relx=1.0, rely=0.0, x=-12, y=12, anchor=tk.NE)
        self.exit_fullscreen_button.lift()
        
        # 绑定画布事件
        self.canvas.bind("<Button-1>", self.on_click_fullscreen)
        self.canvas.bind("<B1-Motion>", self.drag_fullscreen)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel_fullscreen)
        self.canvas.bind("<Motion>", self.on_mouse_move_fullscreen)
        self.canvas.bind("<Leave>", self.on_canvas_leave)
        
        # 绑定ESC键退出全屏
        if self.fullscreen_window is not None:
            self.fullscreen_window.bind("<Escape>", lambda e: self.exit_fullscreen())
        
        # 更新状态
        self.is_fullscreen = True
    
    def start_drag_fullscreen(self, event):
        """全屏模式下开始拖拽"""
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
    
    def drag_fullscreen(self, event):
        """全屏模式下拖拽操作"""
        assert self.fullscreen_canvas is not None
        if self.dragging:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.fullscreen_canvas.move(tk.ALL, dx, dy)
            self.last_x = event.x
            self.last_y = event.y
    
    def exit_fullscreen(self):
        """退出全屏显示模式"""
        if not self.is_fullscreen:
            return
        
        # 强制停止拖拽
        self.dragging = False
        
        # 停止悬停轮询和tooltip
        self._stop_hover_polling()
        self.hide_tooltip()
        self.hovered_node = None
        
        try:
            if self.fullscreen_window is not None:
                try:
                    if self.fullscreen_window.winfo_exists():
                        self.fullscreen_window.destroy()
                except Exception:
                    pass
                self.fullscreen_window = None
        except Exception:
            pass
        
        # 恢复原始画布引用
        if self.original_canvas is not None:
            self.canvas = self.original_canvas
            self.original_canvas = None
        
        # 恢复原始节点数据
        if self.original_nodes is not None:
            self.nodes = self.original_nodes
            self.original_nodes = None
        
        # 清理全屏相关的控件引用
        for attr_name in ['fullscreen_canvas', 
                          'exit_fullscreen_button', 'control_frame', 
                          'zoom_in_button', 'zoom_out_button', 'scale_label']:
            if hasattr(self, attr_name):
                try:
                    delattr(self, attr_name)
                except Exception:
                    pass
        
        # 恢复原始缩放因子
        if hasattr(self, 'original_scale'):
            self.scale = self.original_scale
        
        # 更新状态
        self.is_fullscreen = False
    
    def _copy_canvas_content(self, source_canvas, target_canvas):
        """复制画布内容（包含tag信息）"""
        # 清空目标画布
        target_canvas.delete(tk.ALL)
        
        # 获取源画布的所有项目
        items = source_canvas.find_all()
        
        for item in items:
            # 获取项目类型
            item_type = source_canvas.type(item)
            
            # 获取项目属性
            coords = source_canvas.coords(item)
            
            # 获取项目的tag信息（用于悬停检测）
            tags = source_canvas.gettags(item)
            
            if item_type == "polygon":
                fill = source_canvas.itemcget(item, "fill")
                outline = source_canvas.itemcget(item, "outline")
                smooth = source_canvas.itemcget(item, "smooth")
                width = source_canvas.itemcget(item, "width")
                target_canvas.create_polygon(*coords, fill=fill, outline=outline, smooth=smooth, width=width, tags=tags)
            elif item_type == "oval":
                fill = source_canvas.itemcget(item, "fill")
                outline = source_canvas.itemcget(item, "outline")
                width = source_canvas.itemcget(item, "width")
                target_canvas.create_oval(*coords, fill=fill, outline=outline, width=width, tags=tags)
            elif item_type == "line":
                fill = source_canvas.itemcget(item, "fill")
                width = source_canvas.itemcget(item, "width")
                arrow = source_canvas.itemcget(item, "arrow")
                arrowshape = source_canvas.itemcget(item, "arrowshape")
                # 解析arrowshape，它返回的是字符串格式如 "10 15 5"
                arrowshape_tuple = ()
                if arrowshape:
                    try:
                        arrowshape_tuple = tuple(map(int, arrowshape.split()))
                    except (ValueError, AttributeError):
                        arrowshape_tuple = (10, 15, 5)
                target_canvas.create_line(*coords, fill=fill, width=width, arrow=arrow, arrowshape=arrowshape_tuple, tags=tags)
            elif item_type == "text":
                text = source_canvas.itemcget(item, "text")
                fill = source_canvas.itemcget(item, "fill")
                font = source_canvas.itemcget(item, "font")
                anchor = source_canvas.itemcget(item, "anchor")
                target_canvas.create_text(*coords, text=text, fill=fill, font=font, anchor=anchor, tags=tags)
    
    def _create_fullscreen_controls(self):
        """创建全屏模式下的缩放控制面板"""
        assert self.fullscreen_canvas is not None
        # 创建控制面板框架
        self.control_frame = tk.Frame(self.fullscreen_canvas, bg="#34495e", bd=1, relief=tk.SUNKEN)
        self.control_frame.place(relx=0.99, rely=0.99, anchor=tk.SE)
        
        # 创建放大按钮
        zoom_in = tk.Button(
            self.control_frame,
            text="＋",
            command=lambda: self._zoom_fullscreen(1.1),
            bg="#27ae60",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )
        self.zoom_in_button = zoom_in
        zoom_in.grid(row=0, column=0, padx=2, pady=2)
        zoom_in.bind("<Enter>", lambda e: zoom_in.config(bg="#2ecc71"))
        zoom_in.bind("<Leave>", lambda e: zoom_in.config(bg="#27ae60"))
        
        # 创建缩小按钮
        zoom_out = tk.Button(
            self.control_frame,
            text="－",
            command=lambda: self._zoom_fullscreen(0.9),
            bg="#e67e22",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )
        self.zoom_out_button = zoom_out
        zoom_out.grid(row=1, column=0, padx=2, pady=2)
        zoom_out.bind("<Enter>", lambda e: zoom_out.config(bg="#f39c12"))
        zoom_out.bind("<Leave>", lambda e: zoom_out.config(bg="#e67e22"))
        
        # 创建重置按钮
        reset = tk.Button(
            self.control_frame,
            text="⟲",
            command=self._reset_fullscreen_view,
            bg="#95a5a6",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            font=("Arial", 12),
            cursor="hand2"
        )
        self.reset_button = reset
        reset.grid(row=2, column=0, padx=2, pady=2)
        reset.bind("<Enter>", lambda e: reset.config(bg="#bdc3c7"))
        reset.bind("<Leave>", lambda e: reset.config(bg="#95a5a6"))
        
        # 创建缩放比例显示（固定宽度，防止文字位数变化导致控件宽度变化）
        scale_lbl = tk.Label(
            self.control_frame,
            text=f"{int(self.scale * 100)}%",
            bg="#34495e",
            fg="white",
            font=("Arial", 10),
            padx=6,
            pady=2,
            width=4
        )
        self.scale_label = scale_lbl
        scale_lbl.grid(row=3, column=0, padx=2, pady=2)
    
    def _zoom_fullscreen(self, factor):
        """全屏模式下缩放图像"""
        assert self.fullscreen_canvas is not None
        new_scale = self.scale * factor
        new_scale = max(0.5, min(new_scale, 1.0))
        
        scale_factor = new_scale / self.scale
        self.scale = new_scale
        
        # 获取鼠标位置作为缩放中心（使用画布中心）
        bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if bbox:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            self.fullscreen_canvas.scale(tk.ALL, center_x, center_y, scale_factor, scale_factor)
        
        # 更新缩放比例显示
        if self.scale_label is not None:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _reset_fullscreen_view(self):
        """重置全屏视图到最佳显示状态"""
        assert self.fullscreen_canvas is not None
        
        # 临时移除画布，防止变换过程中的闪现
        self.fullscreen_canvas.pack_forget()
        
        # 重新绘制拓扑图并自适应缩放
        self._redraw_and_fit_fullscreen()
        
        # 重新显示画布
        self.fullscreen_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 确保视图从左上角开始
        self.fullscreen_canvas.xview_moveto(0)
        self.fullscreen_canvas.yview_moveto(0)
        
        # 更新缩放比例显示
        if hasattr(self, 'scale_label') and self.scale_label:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _auto_scale_to_fit_fullscreen(self):
        """全屏模式下自动缩放画布以适应全屏窗口，左上对齐"""
        assert self.fullscreen_canvas is not None
        # 确保画布已完全初始化
        self.fullscreen_canvas.update_idletasks()
        
        # 获取全屏画布尺寸
        canvas_width = self.fullscreen_canvas.winfo_width()
        canvas_height = self.fullscreen_canvas.winfo_height()
        
        # 如果画布尺寸还没有正确获取，尝试从父窗口获取
        if canvas_width <= 1 or canvas_height <= 1:
            parent = self.fullscreen_canvas.nametowidget(self.fullscreen_canvas.winfo_parent())
            if parent:
                parent.update_idletasks()
                canvas_width = parent.winfo_width()
                canvas_height = parent.winfo_height()
        
        # 如果还是没有正确获取尺寸，延迟重试并更新显示
        if canvas_width <= 1 or canvas_height <= 1:
            self.fullscreen_canvas.after(50, self._auto_scale_to_fit_fullscreen_and_update_label)
            return
        
        # 获取内容边界框
        bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        # 计算所有节点的边界框
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        
        if content_width <= 0 or content_height <= 0:
            return
        
        # 计算缩放比例，使用30像素边距
        margin = 30
        scale_x = (canvas_width - 2 * margin) / content_width
        scale_y = (canvas_height - 2 * margin) / content_height
        scale_factor = min(scale_x, scale_y)
        
        # 限制缩放范围
        scale_factor = max(0.5, min(scale_factor, 1.0))
        
        # 先将内容移动到原点位置
        self.fullscreen_canvas.move(tk.ALL, -x1, -y1)
        
        # 应用缩放（以原点为基准进行缩放）
        if scale_factor != 1.0:
            self.fullscreen_canvas.scale(tk.ALL, 0, 0, scale_factor, scale_factor)
        
        # 计算缩放后的尺寸
        scaled_content_width = content_width * scale_factor
        scaled_content_height = content_height * scale_factor
        
        # 水平和垂直方向独立判断位置
        if scaled_content_width <= canvas_width - 2 * margin:
            # 水平方向未超出容器，居中
            target_x = (canvas_width - scaled_content_width) / 2
        else:
            # 水平方向超出容器，靠左
            target_x = margin
        
        if scaled_content_height <= canvas_height - 2 * margin:
            # 垂直方向未超出容器，居中
            target_y = (canvas_height - scaled_content_height) / 2
        else:
            # 垂直方向超出容器，靠上
            target_y = margin
        
        # 将内容移动到目标位置
        self.fullscreen_canvas.move(tk.ALL, target_x, target_y)
        
        # 更新滚动区域
        self.fullscreen_canvas.config(
            scrollregion=(
                0, 
                0, 
                max(canvas_width, target_x + scaled_content_width + margin), 
                max(canvas_height, target_y + scaled_content_height + margin)
            )
        )
        
        # 确保视图在左上角
        self.fullscreen_canvas.xview_moveto(0)
        self.fullscreen_canvas.yview_moveto(0)
        
        # 更新缩放因子
        self.scale = scale_factor
    
    def _auto_scale_to_fit_fullscreen_and_update_label(self):
        """全屏模式下自动缩放并更新显示"""
        self._auto_scale_to_fit_fullscreen()
        # 更新缩放比例显示
        if hasattr(self, 'scale_label') and self.scale_label:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def on_mouse_wheel_fullscreen(self, event):
        """全屏模式下鼠标滚轮缩放 - 以鼠标位置为中心"""
        assert self.fullscreen_canvas is not None
        # 将窗口坐标转换为画布坐标
        canvas_x = self.fullscreen_canvas.canvasx(event.x)
        canvas_y = self.fullscreen_canvas.canvasy(event.y)
        
        if event.delta > 0:
            new_scale = self.scale * 1.1
        else:
            new_scale = self.scale * 0.9
        
        # 统一缩放范围：50%-100%
        new_scale = max(0.5, min(new_scale, 1.0))
        scale_factor = new_scale / self.scale
        self.scale = new_scale
        
        # 以鼠标位置为中心缩放
        self.fullscreen_canvas.scale(tk.ALL, canvas_x, canvas_y, scale_factor, scale_factor)
        
        # 更新缩放比例显示
        if hasattr(self, 'scale_label') and self.scale_label:
            self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def on_click_fullscreen(self, event):
        """全屏模式下自定义点击处理，实现双击检测"""
        assert self.fullscreen_canvas is not None
        current_time = event.time
        current_x = event.x
        current_y = event.y
        
        # 检查是否处于双击冷却期（防止三击被误判为两次双击）
        if hasattr(self, '_in_double_click_cooldown') and self._in_double_click_cooldown:
            # 在冷却期内，只记录点击信息，不检测双击
            self.last_click_time = current_time
            self.last_click_x = current_x
            self.last_click_y = current_y
            self.start_drag(event)
            return
        
        # 检查是否是双击
        time_diff = current_time - self.last_click_time
        distance = ((current_x - self.last_click_x) ** 2 + (current_y - self.last_click_y) ** 2) ** 0.5
        
        if time_diff <= self.double_click_threshold and distance <= self.double_click_distance:
            # 是双击事件 - 设置冷却期，防止三击被误判为两次双击
            self._in_double_click_cooldown = True
            if self._double_click_cooldown_timer is not None:
                self.fullscreen_canvas.after_cancel(self._double_click_cooldown_timer)
                self._double_click_cooldown_timer = None
            self._double_click_cooldown_timer = self.fullscreen_canvas.after(
                self.double_click_threshold, 
                lambda: setattr(self, '_in_double_click_cooldown', False)
            )
            # 执行双击缩放
            self.on_double_click_fullscreen(event)
            
            self.last_click_time = 0
            
            return
        
        # 不是双击，记录点击信息
        self.last_click_time = current_time
        self.last_click_x = current_x
        self.last_click_y = current_y
        
        # 立即开始拖拽
        self.start_drag(event)
    
    def on_double_click_fullscreen(self, event):
        """全屏模式下双击缩放功能"""
        assert self.fullscreen_canvas is not None
        current_scale = getattr(self, 'scale', 1.0)
        
        self.fullscreen_canvas.update_idletasks()
        canvas_width = self.fullscreen_canvas.winfo_width()
        canvas_height = self.fullscreen_canvas.winfo_height()
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        
        if current_scale < 1.0:
            # 放大到100%，确保容器中心始终在图形区域内
            window_x = event.x
            window_y = event.y
            
            scale_factor = 1.0 / current_scale
            
            # 获取缩放前的内容边界框
            bbox_before = self.fullscreen_canvas.bbox(tk.ALL)
            
            # 判断点击位置是否在图形区域内
            click_inside = False
            if bbox_before:
                bx1, by1, bx2, by2 = bbox_before
                if bx1 <= window_x <= bx2 and by1 <= window_y <= by2:
                    click_inside = True
            
            if click_inside:
                # 点击在图形内部：以点击位置为中心缩放
                self.fullscreen_canvas.scale(tk.ALL, window_x, window_y, scale_factor, scale_factor)
                dx = center_x - window_x
                dy = center_y - window_y
                self.fullscreen_canvas.move(tk.ALL, dx, dy)
            else:
                # 点击在图形外部：找到离鼠标最近的节点，居中放大
                target_x = window_x
                target_y = window_y
                
                min_dist = float('inf')
                for _node_id, node in self.nodes.items():
                    shape = node.get("shape")
                    if shape is None:
                        continue
                    coords = self.fullscreen_canvas.bbox(int(shape))
                    if coords:
                        node_cx = (coords[0] + coords[2]) / 2
                        node_cy = (coords[1] + coords[3]) / 2
                        dist = ((window_x - node_cx) ** 2 + (window_y - node_cy) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            target_x = node_cx
                            target_y = node_cy
                
                # 以目标位置为基准缩放
                self.fullscreen_canvas.scale(tk.ALL, target_x, target_y, scale_factor, scale_factor)
                dx = center_x - target_x
                dy = center_y - target_y
                self.fullscreen_canvas.move(tk.ALL, dx, dy)
            
            # 最终检查：确保容器中心在图形外框内部
            bbox = self.fullscreen_canvas.bbox(tk.ALL)
            if bbox:
                bx1, by1, bx2, by2 = bbox
                adjust_x = 0
                adjust_y = 0
                
                if center_x < bx1:
                    adjust_x = bx1 - center_x
                elif center_x > bx2:
                    adjust_x = bx2 - center_x
                
                if center_y < by1:
                    adjust_y = by1 - center_y
                elif center_y > by2:
                    adjust_y = by2 - center_y
                
                if adjust_x != 0 or adjust_y != 0:
                    self.fullscreen_canvas.move(tk.ALL, adjust_x, adjust_y)
            
            self.scale = 1.0
            if hasattr(self, 'scale_label') and self.scale_label:
                self.scale_label.config(text=f"{int(self.scale * 100)}%")
        else:
            # 缩小到50%
            window_x = event.x
            window_y = event.y
            
            bbox = self.fullscreen_canvas.bbox(tk.ALL)
            if not bbox:
                return
            
            x1, y1, x2, y2 = bbox
            content_width = x2 - x1
            content_height = y2 - y1
            scaled_width = content_width * 0.5
            scaled_height = content_height * 0.5
            margin = 30
            
            if scaled_width <= canvas_width - margin * 2 and scaled_height <= canvas_height - margin * 2:
                # 小图：整体缩小并居中
                self.fullscreen_canvas.move(tk.ALL, -x1, -y1)
                self.fullscreen_canvas.scale(tk.ALL, 0, 0, 0.5, 0.5)
                cx = (canvas_width - scaled_width) / 2
                cy = (canvas_height - scaled_height) / 2
                self.fullscreen_canvas.move(tk.ALL, cx, cy)
            else:
                # 大图：以点击位置为中心缩小
                self.fullscreen_canvas.scale(tk.ALL, window_x, window_y, 0.5, 0.5)
                dx = center_x - window_x
                dy = center_y - window_y
                self.fullscreen_canvas.move(tk.ALL, dx, dy)
            
            self.scale = 0.5
            if hasattr(self, 'scale_label') and self.scale_label:
                self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def on_mouse_move_fullscreen(self, event):
        """全屏模式下鼠标移动事件，用于显示节点悬停详情"""
        assert self.fullscreen_canvas is not None
        if self.dragging:
            return
        
        # 将窗口坐标转换为画布坐标
        canvas_x = self.fullscreen_canvas.canvasx(event.x)
        canvas_y = self.fullscreen_canvas.canvasy(event.y)
        
        # 查找鼠标下方的节点
        hovered_node = None
        overlapping = self.fullscreen_canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
        
        for item_id in reversed(list(overlapping)):
            tags = self.fullscreen_canvas.gettags(item_id)
            for tag in tags:
                if tag in self.nodes:
                    hovered_node = self.nodes[tag]
                    break
            if hovered_node:
                break
        
        if hovered_node != self.hovered_node:
            self._restore_all_hover_styles()
            self._stop_hover_polling()
            self.hovered_node = hovered_node
            
            if hovered_node:
                self._apply_hover_style(hovered_node)
                self.last_mouse_x = event.x_root
                self.last_mouse_y = event.y_root
                
                if self.tooltip_timer:
                    try:
                        self.fullscreen_canvas.after_cancel(self.tooltip_timer)
                    except Exception:
                        pass
                self.tooltip_timer = self.fullscreen_canvas.after(100, self._delayed_show_tooltip)
                self._start_hover_polling()
            else:
                if self.tooltip_timer:
                    try:
                        self.fullscreen_canvas.after_cancel(self.tooltip_timer)
                    except Exception:
                        pass
                self.tooltip_timer = None
                self.hide_tooltip()


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
