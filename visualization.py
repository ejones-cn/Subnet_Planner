#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化模块
实现网络拓扑图和IP地址分配可视化功能
"""

import tkinter as tk
from tkinter import Canvas, Frame, Scrollbar
import math
import ipaddress
from style_manager import get_current_font_settings
from i18n import _ as translate

# 定义颜色常量
NODE_COLOR = "#4a7eb4"
NODE_BORDER_COLOR = "#2c3e50"
LINK_COLOR = "#7f8c8d"
TEXT_COLOR = "#ecf0f1"
BACKGROUND_COLOR = "#34495e"
HIGHLIGHT_COLOR = "#e74c3c"

# 定义节点大小
NODE_WIDTH = 120
NODE_HEIGHT = 60
NODE_SPACING = 150

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
        self.next_x = 100
        self.next_y = 100
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        
        # 拖拽状态
        self.dragging = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.last_x = 0
        self.last_y = 0
        
        # 缩放因子
        self.scale = 1.0
        
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
        new_scale = max(0.5, min(new_scale, 2.0))
        
        # 计算缩放比例
        scale_factor = new_scale / self.scale
        self.scale = new_scale
        
        # 缩放画布内容
        self.canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)
    
    def add_node(self, name, subnet, level=0):
        """添加节点
        
        Args:
            name: 节点名称
            subnet: 子网信息
            level: 层级
        
        Returns:
            str: 节点ID
        """
        node_id = f"node_{len(self.nodes)}"
        x = self.next_x + level * NODE_SPACING
        y = self.next_y
        
        # 创建节点矩形
        rect_id = self.canvas.create_rectangle(
            x, y, x + NODE_WIDTH, y + NODE_HEIGHT,
            fill=NODE_COLOR,
            outline=NODE_BORDER_COLOR,
            width=2
        )
        
        # 获取字体设置
        font_family, font_size = get_current_font_settings()
        
        # 创建节点文本
        text_id = self.canvas.create_text(
            x + NODE_WIDTH/2, y + NODE_HEIGHT/3,
            text=name,
            font=(font_family, font_size, "bold"),
            fill=TEXT_COLOR
        )
        
        # 创建子网文本
        subnet_text = str(subnet)
        if len(subnet_text) > 20:
            subnet_text = subnet_text[:17] + "..."
        
        subnet_id = self.canvas.create_text(
            x + NODE_WIDTH/2, y + NODE_HEIGHT*2/3,
            text=subnet_text,
            font=(font_family, font_size-2),
            fill=TEXT_COLOR
        )
        
        # 存储节点信息
        self.nodes[node_id] = {
            "id": node_id,
            "name": name,
            "subnet": subnet,
            "rect": rect_id,
            "text": text_id,
            "subnet_text": subnet_id,
            "x": x,
            "y": y,
            "level": level
        }
        
        # 更新下一个节点位置
        self.next_y += NODE_HEIGHT + 50
        if self.next_y > 500:
            self.next_y = 100
            self.next_x += NODE_WIDTH + NODE_SPACING
        
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
            y1 = source["y"] + NODE_HEIGHT/2
            x2 = target["x"]
            y2 = target["y"] + NODE_HEIGHT/2
            
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
        self.next_x = 100
        self.next_y = 100
        self.scale = 1.0
    
    def draw_topology(self, parent_cidr, allocated_subnets):
        """绘制网络拓扑图
        
        Args:
            parent_cidr: 父网段
            allocated_subnets: 已分配子网列表
        """
        self.clear()
        
        # 添加父节点
        parent_node = self.add_node("父网段", parent_cidr, level=0)
        
        # 添加子节点并创建连接
        for i, subnet in enumerate(allocated_subnets):
            subnet_node = self.add_node(
                subnet["name"],
                subnet["cidr"],
                level=1
            )
            self.add_link(parent_node, subnet_node)
        
        # 更新滚动区域
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(tk.ALL)
        if bbox:
            self.canvas.config(scrollregion=bbox)

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
            width/2, 20,
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
                50, y, width-50, y+25,
                fill=color,
                outline="#34495e",
                width=1
            )
            
            # 绘制IP地址文本
            self.canvas.create_text(
                70, y+12,
                text=ip_info["ip_address"],
                font=(font_family, font_size-1),
                fill=TEXT_COLOR,
                anchor=tk.W
            )
            
            # 绘制主机名和描述
            if ip_info.get("hostname"):
                hostname = ip_info["hostname"]
                if len(hostname) > 20:
                    hostname = hostname[:17] + "..."
                
                self.canvas.create_text(
                    200, y+12,
                    text=hostname,
                    font=(font_family, font_size-1),
                    fill=TEXT_COLOR,
                    anchor=tk.W
                )
            
            # 绘制状态
            self.canvas.create_text(
                width-70, y+12,
                text=ip_info["status"],
                font=(font_family, font_size-1),
                fill=TEXT_COLOR,
                anchor=tk.E
            )
        
        # 更新滚动区域
        self.canvas.config(scrollregion=(0, 0, width, height))
