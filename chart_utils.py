# -*- coding: utf-8 -*-
"""通用图表工具模块

提供网段分布图等图表的绘制功能，支持子网切分和子网规划等功能。
"""

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


def draw_text_with_stroke(canvas, text, x, y, font, anchor=tk.W, fill="#ffffff",
                          stroke_color="#666666", stroke_width=1):
    """绘制带描边的文字

    Args:
        canvas: tk.Canvas 对象
        text: 要绘制的文字
        x: 起始x坐标
        y: 起始y坐标
        font: 字体设置
        anchor: 文字锚点
        fill: 文字颜色
        stroke_color: 描边颜色（灰色）
        stroke_width: 描边宽度
    """
    if stroke_width > 0:
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            canvas.create_text(
                x + dx * stroke_width, y + dy * stroke_width,
                text=text,
                font=font,
                anchor=anchor,
                fill=stroke_color
            )

    canvas.create_text(
        x, y,
        text=text,
        font=font,
        anchor=anchor,
        fill=fill
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

        parent_width = parent_frame.winfo_width() if parent_frame else 800
        width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        if width < 10 or width > parent_width:
            width = parent_width - 30
        if canvas_height < 10:
            canvas_height = 400

        margin_left = 50
        margin_right = 80
        margin_top = 50
        chart_width = width - margin_left - margin_right

        parent_info = chart_data.get("parent", {})
        parent_range = parent_info.get("range", 1)

        networks = chart_data.get("networks", [])
        if not networks:
            canvas.create_text(width / 2, canvas_height / 2, text="无网段数据", font=("微软雅黑", 12))
            return

        log_max = math.log10(parent_range)
        log_min = 3
        min_bar_width = 50

        bar_height = 30
        padding = 10
        x = margin_left
        y = margin_top

        required_height = (
            y
            + (bar_height + padding)
            + (bar_height + padding)
            + 40
            + (len(networks) * (bar_height + padding))
            + 80
        )

        background_height = max(required_height, canvas_height)
        canvas.create_rectangle(0, 0, width, background_height, fill="#333333", outline="", width=0)

        actual_width = canvas.winfo_width()
        if actual_width < 10:
            actual_width = width

        canvas.config(scrollregion=(0, 0, actual_width, background_height))
        canvas.config(xscrollcommand=None)

        parent_range = parent_info.get("range", 1)
        log_value = max(log_min, math.log10(parent_range))
        bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
        bar_width = min(bar_width, chart_width)

        color = PARENT_COLOR
        canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

        usable_addresses = parent_range - 2 if parent_range > 2 else parent_range
        parent_cidr = parent_info.get("name", "")
        segment_text = f"父网段: {parent_cidr}"
        text_x = x + 15
        text_y = y + bar_height / 2
        font = ("微软雅黑", 11, "bold")
        draw_text_with_stroke(canvas, segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

        address_text = f"可用地址数: {usable_addresses:,}"
        text_x = x + 250
        draw_text_with_stroke(canvas, address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

        y += bar_height + padding

        split_networks = [net for net in networks if net.get("type") == "split"]
        
        if chart_type == "plan":
            # 子网规划：需求网段
            # 父网段与需求网段之间添加虚线分割
            canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)
            y += 20
            
            # 添加需求网段标题（和剩余网段一样的格式）
            demand_count = len(split_networks)
            canvas.create_text(
                x,
                y,
                text=f"需求网段 ({demand_count} 个):",
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

                # 为需求网段分配彩色
                color_index = i % len(SUBNET_COLORS)
                color = SUBNET_COLORS[color_index]
                canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

                name = network.get("name", "")
                cidr = network.get("cidr", "")
                usable_addresses = network_range - 2 if network_range > 2 else network_range

                # 需求网段：添加序号和CIDR，使用与剩余网段相同的字体大小
                segment_text = f"网段 {i + 1}: {name}  {cidr}"
                text_x = x + 15
                text_y = y + bar_height / 2
                font = ("微软雅黑", 9, "bold")  # 与剩余网段相同的字号
                draw_text_with_stroke(canvas, segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                address_text = f"可用地址数: {usable_addresses:,}"
                text_x = x + 250
                draw_text_with_stroke(canvas, address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                y += bar_height + padding
                
                # 需求网段之间不添加虚线分割
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

                # 切分网段：不需要序号，使用与父网段相同的字体大小
                segment_text = f"切分网段: {name}"
                text_x = x + 15
                text_y = y + bar_height / 2
                font = ("微软雅黑", 11, "bold")  # 与父网段相同的字号
                draw_text_with_stroke(canvas, segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                address_text = f"可用地址数: {usable_addresses:,}"
                text_x = x + 250
                draw_text_with_stroke(canvas, address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

                y += bar_height + padding

                # 添加切分网段和剩余网段之间的虚线分割
                canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)

        # 需求网段与剩余网段之间添加虚线分割（仅在子网规划中需要）
        if chart_type == "plan":
            canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)
        
        y += 20
        title_font = ("微软雅黑", 11)
        remaining_count = len([n for n in networks if n.get("type") != "split"])
        canvas.create_text(
            x, y,
            text=f"剩余网段 ({remaining_count} 个):",
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

            segment_text = f"网段 {i + 1}: {name}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = ("微软雅黑", 9, "bold")
            draw_text_with_stroke(canvas, segment_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

            address_text = f"可用地址数: {usable_addresses:,}"
            text_x = x + 250
            draw_text_with_stroke(canvas, address_text, text_x, text_y, font, anchor=tk.W, fill="#ffffff")

            y += bar_height + padding

        canvas.create_line(x, y, x + chart_width, y, fill="#cccccc", dash=(5, 2), width=1)

        legend_y = y + 15
        canvas.create_text(x, legend_y, text="图例:", font=("微软雅黑", 11), anchor=tk.W, fill="#ffffff")

        legend_items_y = legend_y + 25

        canvas.create_rectangle(x, legend_items_y, x + 20, legend_items_y + 12, fill=PARENT_COLOR)
        canvas.create_text(
            x + 30,
            legend_items_y + 6,
            text="父网段",
            font=("微软雅黑", 9),
            anchor=tk.W,
            fill="#ffffff",
        )

        if chart_type == "plan":
            # 子网规划：需求网段（多色）
            # 使用多个彩色方块表示多色
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
                text="需求网段(多色)",
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
                    remaining_start_x + j * 20 + 20,
                    legend_items_y + 12,
                    fill=color,
                )
            canvas.create_text(
                remaining_start_x + 100,
                legend_items_y + 6,
                text="剩余网段(多色)",
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
                text="切分网段",
                font=("微软雅黑", 9),
                anchor=tk.W,
                fill="#ffffff",
            )

            # 剩余网段图例
            for j, color in enumerate(LEGEND_COLORS):
                canvas.create_rectangle(
                    x + 230 + j * 25,
                    legend_items_y,
                    x + 250 + j * 25,
                    legend_items_y + 12,
                    fill=color,
                )

            canvas.create_text(
                x + 340,
                legend_items_y + 6,
                text="剩余网段(多色)",
                font=("微软雅黑", 9),
                anchor=tk.W,
                fill="#ffffff",
            )

        canvas.update_idletasks()

    except (tk.TclError, ValueError, TypeError) as e:
        canvas.delete("all")
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 400
        title_font = ("微软雅黑", 12, "bold")
        canvas.create_text(
            width / 2, height / 2, text=f"图表绘制失败: {str(e)}", font=title_font, fill="red"
        )
