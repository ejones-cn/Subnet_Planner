# -*- coding: utf-8 -*-
"""通用图表工具模块

提供网段分布图等图表的绘制功能，支持子网切分和子网规划等功能
"""

from i18n import _
import tkinter as tk
import math

SUBNET_COLORS = (
    "#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8",
    "#5b8fd9", "#3c70d8", "#e68838", "#a04132",
    "#6a9da8", "#87c569", "#6d8de8", "#c16fa0",
    "#a99bc6", "#a44d69", "#b9d0f8", "#5d4ea5",
    "#f5ad8c", "#5b8fd9", "#db6679", "#a6c589",
)

LEGEND_COLORS = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]

PARENT_COLOR = "#636e72"
SPLIT_COLOR = "#4a7eb4"


def draw_text_with_stroke(canvas, text, x, y, style):
    """绘制带描边效果的文本
    
    Args:
        canvas: tk.Canvas 对象
        text: 要绘制的文本
        x: x坐标
        y: y坐标
        style: 样式字典，包含font、anchor、fill等参数
    """
    # 绘制描边
    for dx in [-1, 1]:
        for dy in [-1, 1]:
            canvas.create_text(
                x + dx, y + dy,
                text=text,
                font=style.get("font", ("微软雅黑", 12)),
                anchor=style.get("anchor", tk.CENTER),
                fill="#000000"
            )
    # 绘制主文本
    canvas.create_text(
        x, y,
        text=text,
        font=style.get("font", ("微软雅黑", 12)),
        anchor=style.get("anchor", tk.CENTER),
        fill=style.get("fill", "#ffffff")
    )


def _init_canvas(canvas, parent_frame):
    """初始化画布并计算尺寸
    
    Args:
        canvas: tk.Canvas 对象
        parent_frame: 父框架
    
    Returns:
        tuple: (width, canvas_height, margin_left, margin_right, margin_top, chart_width)
    """
    parent_width = parent_frame.winfo_width() if parent_frame else 800
    width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    if width < 10 or width > parent_width:
        width = parent_width - 30
    if canvas_height < 10:
        canvas_height = 400

    margin_left = 50
    margin_right = 40  # 减小右侧边距，从80改为40
    margin_top = 50
    chart_width = width - margin_left - margin_right
    
    return width, canvas_height, margin_left, margin_right, margin_top, chart_width


def _draw_parent_segment(canvas, parent_info, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding):
    """绘制父网段
    
    Args:
        canvas: tk.Canvas 对象
        parent_info: 父网段信息
        x: x坐标
        y: y坐标
        chart_width: 图表宽度
        log_min: 最小对数
        log_max: 最大对数
        min_bar_width: 最小柱状图宽度
        bar_height: 柱状图高度
        padding: 内边距
    
    Returns:
        int: 新的y坐标
    """
    parent_range = parent_info.get("range", 1)
    log_value = max(log_min, math.log10(parent_range))
    bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
    bar_width = min(bar_width, chart_width)

    color = PARENT_COLOR
    canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

    usable_addresses = parent_range - 2 if parent_range > 2 else parent_range
    parent_cidr = parent_info.get("name", "")
    segment_text = f"{_("parent_network")}: {parent_cidr}"
    text_x = x + 15
    text_y = y + bar_height / 2
    font = ("微软雅黑", 11, "bold")
    draw_text_with_stroke(canvas, segment_text, text_x, text_y, {
        "font": font,
        "anchor": tk.W,
        "fill": "#ffffff"
    })

    # 父网段：可用地址数
    address_text = f"{_("usable_addresses")}: {usable_addresses:,}"
    # 计算合适的x坐标，将文本向左偏移50像素
    text_x = min(x + 400, x + chart_width - 200)  # 向左偏移50像素
    draw_text_with_stroke(canvas, address_text, text_x, text_y, {
        "font": font,
        "anchor": tk.W,
        "fill": "#ffffff"
    })

    return y + bar_height + padding


def _draw_network_segments(canvas, split_networks, chart_type, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding):
    """绘制网络网段
    
    Args:
        canvas: tk.Canvas 对象
        split_networks: 分割网段列表
        chart_type: 图表类型
        x: x坐标
        y: y坐标
        chart_width: 图表宽度
        log_min: 最小对数
        log_max: 最大对数
        min_bar_width: 最小柱状图宽度
        bar_height: 柱状图高度
        padding: 内边距
    
    Returns:
        int: 新的y坐标
    """
    if chart_type == "plan":
        # 子网规划：需求网段
        canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)
        y += 20
        
        # 添加需求网段标题
        demand_count = len(split_networks)
        canvas.create_text(
            x,
            y,
            text=f"{_("allocated_subnets")} ({demand_count} {_("pieces")}):",
            font=("微软雅黑", 11),
            anchor=tk.W,
            fill="#ffffff",
        )
        y += 15
        
        for i, network in enumerate(split_networks):
            network_range = network.get("range", 1)
            log_value = max(log_min, math.log10(network_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
            bar_width = min(bar_width, chart_width)

            # 为需求网段分配颜色
            color_index = i % len(SUBNET_COLORS)
            color = SUBNET_COLORS[color_index]
            canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

            name = network.get("name", "")
            usable_addresses = network_range - 2 if network_range > 2 else network_range

            # 需求网段：添加序号和CIDR
            segment_text = f"{_("segment")} {i + 1}: {name} {network.get('cidr', '')}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = ("微软雅黑", 9, "bold")
            draw_text_with_stroke(canvas, segment_text, text_x, text_y, {
                "font": font,
                "anchor": tk.W,
                "fill": "#ffffff"
            })

            # 需求网段：可用地址数
            address_text = f"{_("usable_addresses")}: {usable_addresses:,}"
            # 计算合适的x坐标，将文本向右移动更多
            text_x = min(x + 450, x + chart_width - 150)  # 增加x坐标值，向右移动
            draw_text_with_stroke(canvas, address_text, text_x, text_y, {
                "font": font,
                "anchor": tk.W,
                "fill": "#ffffff"
            })

            y += bar_height + padding
    else:
        # 子网切分：切分网段
        for i, network in enumerate(split_networks):
            network_range = network.get("range", 1)
            log_value = max(log_min, math.log10(network_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
            bar_width = min(bar_width, chart_width)

            # 切分网段：使用蓝色
            color = SPLIT_COLOR
            canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

            name = network.get("name", "")
            usable_addresses = network_range - 2 if network_range > 2 else network_range

            # 切分网段：不需要序号
            segment_text = f"{_("split_segment")}: {name}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = ("微软雅黑", 11, "bold")
            draw_text_with_stroke(canvas, segment_text, text_x, text_y, {
                "font": font,
                "anchor": tk.W,
                "fill": "#ffffff"
            })

            # 切分网段：可用地址数
            address_text = f"{_("usable_addresses")}: {usable_addresses:,}"
            # 计算合适的x坐标，将文本向右移动更多
            text_x = min(x + 450, x + chart_width - 150)  # 增加x坐标值，向右移动
            draw_text_with_stroke(canvas, address_text, text_x, text_y, {
                "font": font,
                "anchor": tk.W,
                "fill": "#ffffff"
            })

            y += bar_height + padding

            # 添加切分网段和剩余网段之间的虚线分割
            canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)
    
    # 需求网段与剩余网段之间添加虚线分割（仅在子网规划中需要）
    if chart_type == "plan":
        canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)
    
    return y


def _draw_remaining_segments(canvas, networks, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding):
    """绘制剩余网段
    
    Args:
        canvas: tk.Canvas 对象
        networks: 所有网段列表
        x: x坐标
        y: y坐标
        chart_width: 图表宽度
        log_min: 最小对数
        log_max: 最大对数
        min_bar_width: 最小柱状图宽度
        bar_height: 柱状图高度
        padding: 内边距
    
    Returns:
        int: 新的y坐标
    """
    y += 20
    title_font = ("微软雅黑", 11)
    remaining_count = len([n for n in networks if n.get("type") != "split"])
    canvas.create_text(
        x, y,
        text=f"{_("remaining_subnets")} ({remaining_count} {_("pieces")}):",
        font=title_font,
        anchor=tk.W,
        fill="#ffffff",
    )
    y += 15

    remaining_networks = [net for net in networks if net.get("type") != "split"]
    for i, network in enumerate(remaining_networks):
        network_range = network.get("range", 1)
        log_value = max(log_min, math.log10(network_range))
        bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
        bar_width = min(bar_width, chart_width)

        color_index = i % len(SUBNET_COLORS)
        color = SUBNET_COLORS[color_index]

        canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

        name = network.get("name", "")
        usable_addresses = network_range - 2 if network_range > 2 else network_range

        segment_text = f"{_("segment")} {i + 1}: {name}"
        text_x = x + 15
        text_y = y + bar_height / 2
        font = ("微软雅黑", 9, "bold")
        draw_text_with_stroke(canvas, segment_text, text_x, text_y, {
            "font": font,
            "anchor": tk.W,
            "fill": "#ffffff"
        })

        # 剩余网段：可用地址数
        address_text = f"{_("usable_addresses")}: {usable_addresses:,}"
        # 计算合适的x坐标，将文本向右移动更多
        text_x = min(x + 450, x + chart_width - 150)  # 增加x坐标值，向右移动
        draw_text_with_stroke(canvas, address_text, text_x, text_y, {
            "font": font,
            "anchor": tk.W,
            "fill": "#ffffff"
        })

        y += bar_height + padding
    
    canvas.create_line(x, y, x + chart_width, y, fill="#cccccc", dash=(5, 2), width=1)
    
    return y


def _draw_legend(canvas, chart_type, x, y):
    """绘制图例
    
    Args:
        canvas: tk.Canvas 对象
        chart_type: 图表类型
        x: x坐标
        y: y坐标
    """
    legend_y = y + 15
    canvas.create_text(x, legend_y, text=f"{_("legend")}:", font=("微软雅黑", 11), anchor=tk.W, fill="#ffffff")

    legend_items_y = legend_y + 25

    canvas.create_rectangle(x, legend_items_y, x + 20, legend_items_y + 12, fill=PARENT_COLOR)
    canvas.create_text(
        x + 30,
        legend_items_y + 6,
        text=f"{_("parent_network")}",
        font=("微软雅黑", 9),
        anchor=tk.W,
        fill="#ffffff",
    )

    if chart_type == "plan":
        # 子网规划：需求网段（多色）
        for j, color in enumerate(LEGEND_COLORS):
            canvas.create_rectangle(
                x + 100 + j * 20,
                legend_items_y,
                x + 120 + j * 20,
                legend_items_y + 12,
                fill=color,
            )
        canvas.create_text(
            x + 200,
            legend_items_y + 6,
            text=f"{_("allocated_subnets")}",
            font=("微软雅黑", 9),
            anchor=tk.W,
            fill="#ffffff",
        )
        
        # 剩余网段图例排在需求网段后面，使用多色表达
        remaining_start_x = x + 300
        for j, color in enumerate(LEGEND_COLORS):
            canvas.create_rectangle(
                remaining_start_x + j * 20,
                legend_items_y,
                remaining_start_x + 20 + j * 20,
                legend_items_y + 12,
                fill=color,
            )
        canvas.create_text(
            remaining_start_x + 100,
            legend_items_y + 6,
            text=f"{_("remaining_subnets")}",
            font=("微软雅黑", 9),
            anchor=tk.W,
            fill="#ffffff",
        )
    else:
        # 子网切分：切分网段（蓝色）
        canvas.create_rectangle(x + 100, legend_items_y, x + 120, legend_items_y + 12, fill=SPLIT_COLOR)
        canvas.create_text(
            x + 130,
            legend_items_y + 6,
            text=f"{_("split_segment")}",
            font=("微软雅黑", 9),
            anchor=tk.W,
            fill="#ffffff",
        )
        
        # 剩余网段图例
        remaining_start_x = x + 200
        for j, color in enumerate(LEGEND_COLORS):
            canvas.create_rectangle(
                remaining_start_x + j * 20,
                legend_items_y,
                remaining_start_x + 20 + j * 20,
                legend_items_y + 12,
                fill=color,
            )
        canvas.create_text(
            remaining_start_x + 100,
            legend_items_y + 6,
            text=f"{_("remaining_subnets")}",
            font=("微软雅黑", 9),
            anchor=tk.W,
            fill="#ffffff",
        )


def draw_distribution_chart(canvas, chart_data, parent_frame=None, chart_type="split"):
    """绘制网段分布柱状图

    Args:
        canvas: tk.Canvas 对象
        chart_data: 图表数据，格式为 {"parent": {...}, "networks": [...], "type": "split"}
        parent_frame: 父框架（用于获取宽度），可选
        chart_type: 图表类型，"split"表示子网切分，"plan"表示子网规划
    """
    if not chart_data:
        return

    try:
        canvas.delete("all")
        
        # 初始化画布和计算尺寸
        width, canvas_height, margin_left, _, margin_top, chart_width = _init_canvas(canvas, parent_frame)
        
        # 获取数据
        parent_info = chart_data.get("parent", {})
        parent_range = parent_info.get("range", 1)
        networks = chart_data.get("networks", [])
        
        if not networks:
            canvas.create_text(width / 2, canvas_height / 2, text=f"{_("no_segment_data")}", font=("微软雅黑", 12))
            return
        
        # 计算对数参数
        log_max = math.log10(parent_range)
        log_min = 3
        min_bar_width = 50
        bar_height = 30
        padding = 10
        x = margin_left
        y = margin_top
        
        # 计算所需高度
        required_height = (
            y
            + (bar_height + padding)
            + (bar_height + padding)
            + 40
            + (len(networks) * (bar_height + padding))
            + 80
        )
        background_height = max(required_height, canvas_height)
        
        # 绘制背景
        canvas.create_rectangle(0, 0, width, background_height, fill="#333333", outline="", width=0)
        
        # 配置画布滚动区域
        actual_width = canvas.winfo_width()
        if actual_width < 10:
            actual_width = width
        canvas.config(scrollregion=(0, 0, actual_width, background_height))
        canvas.config(xscrollcommand=None)
        
        # 绘制父网段
        y = _draw_parent_segment(canvas, parent_info, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding)
        
        # 绘制网络网段
        split_networks = [net for net in networks if net.get("type") == "split"]
        y = _draw_network_segments(canvas, split_networks, chart_type, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding)
        
        # 绘制剩余网段
        y = _draw_remaining_segments(canvas, networks, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding)
        
        # 绘制图例
        _draw_legend(canvas, chart_type, x, y)
        
        canvas.update_idletasks()

    except (tk.TclError, ValueError, TypeError) as e:
        canvas.delete("all")
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 400
        title_font = ("微软雅黑", 12, "bold")
        canvas.create_text(
            width / 2, height / 2, text=f"{_("chart_drawing_failed")}: {str(e)}", font=title_font, fill="red"
        )