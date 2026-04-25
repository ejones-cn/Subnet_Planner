# -*- coding: utf-8 -*-
"""通用图表工具模块

提供网段分布图等图表的绘制功能，支持子网切分和子网规划两种场景
"""

from typing import Any, Literal
import tkinter as tk
from tkinter import Canvas, Frame
import math
import ipaddress
from style_manager import get_current_font_settings, get_canvas_font_settings
from version import get_version

# 直接从 i18n 模块导入翻译函数，并重命名为 translate 以避免与局部变量冲突
from i18n import _ as translate  # type: ignore
from ip_subnet_calculator import format_large_number

# 定义一个别名 _trans 用于翻译，避免与局部变量 _ 冲突
_trans = translate

# 模块版本号
__version__ = get_version()

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


def _get_font_settings() -> tuple[str, int]:
    """获取当前语言的Canvas字体设置

    Canvas create_text 使用 Tk 内置文本渲染引擎，不会像 ttk 控件那样
    在字体回退时进行度量同步。因此需要使用具有全面 CJK 覆盖的字体，
    避免因字体回退导致的字符粗细大小不一致问题。

    Returns:
        tuple: (字体名称, 字体大小)
    """
    return get_canvas_font_settings()


def _calculate_bar_width(network_range: float, log_min: float, log_max: float, chart_width: float, min_bar_width: float) -> float:
    """计算柱状图宽度

    Args:
        network_range: 网络范围
        log_min: 最小对数
        log_max: 最大对数
        chart_width: 图表宽度
        min_bar_width: 最小柱状图宽度

    Returns:
        float: 计算后的柱状图宽度
    """
    log_value = max(log_min, math.log10(network_range))
    bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
    return min(bar_width, chart_width)


def _calculate_usable_addresses(network_range: int, is_ipv6: bool = False) -> int:
    """计算可用地址数

    Args:
        network_range: 网络范围
        is_ipv6: 是否为IPv6地址

    Returns:
        int: 可用地址数
    """
    if is_ipv6:
        # IPv6没有广播地址
        if network_range == 1:
            # /128子网，只有一个地址，可用地址数为1
            return 1
        elif network_range == 2:
            # /127子网，有2个地址，都可用
            return 2
        else:
            # 其他IPv6子网，可用地址数 = 总地址数 - 1（仅减去网络地址）
            return network_range - 1
    else:
        # IPv4计算方式
        if network_range == 1:
            # /32子网，只有一个地址，可用地址数为1
            return 1
        elif network_range == 2:
            # /31子网，只有网络地址和广播地址，没有可用主机地址
            return 0
        else:
            # 其他情况，可用地址数 = 总地址数 - 2（网络地址和广播地址）
            return network_range - 2


def _optimize_ipv6_display(ipv6_address: str) -> str:
    """优化IPv6地址的显示格式
    
    对于长IPv6地址，使用更紧凑的显示方式，便于在图表中显示
    
    Args:
        ipv6_address: 完整的IPv6地址
        
    Returns:
        str: 优化后的IPv6地址显示
    """
    try:
        # 使用ipaddress模块解析IPv6地址，自动处理零压缩
        ip_obj = ipaddress.ip_address(ipv6_address.split('/')[0])
        compressed_ip = str(ip_obj)
        
        # 如果是CIDR格式，保留前缀长度
        if '/' in ipv6_address:
            prefix = ipv6_address.split('/')[1]
            compressed_ip = f"{compressed_ip}/{prefix}"
        
        # 对于特别长的IPv6地址，考虑进一步优化显示
        # 例如：2001:0db8:85a3:0000:0000:8a2e:0370:7334/64 -> 2001:db8:85a3::8a2e:370:7334/64
        # 注意：ipaddress模块已经会自动进行零压缩，所以这里主要是处理其他情况
        
        return compressed_ip
        
    except ValueError:
        # 如果解析失败，返回原始地址
        return ipv6_address





def _draw_segment_text(canvas: Canvas, text: str, x: float, y: float, font: tuple[str, int, str]) -> None:
    """绘制网段文本

    Args:
        canvas: Canvas对象
        text: 要绘制的文本
        x: x坐标
        y: y坐标
        font: 字体元组
    """
    draw_text_with_stroke(canvas, text, x, y, {
        "font": font,
        "anchor": tk.W,
        "fill": "#ffffff"
    })


def draw_text_with_stroke(canvas: Canvas, text: str, x: float, y: float, style: dict[str, Any]) -> None:
    """绘制带描边效果的文本

    Args:
        canvas: tk.Canvas 对象
        text: 要绘制的文本
        x: x坐标
        y: y坐标
        style: 样式字典，包含font、anchor、fill等参数
    """
    font_family = _get_font_settings()[0]

    for dx in (-1, 1):
        for dy in (-1, 1):
            canvas.create_text(
                x + dx, y + dy,
                text=text,
                font=style.get("font", (font_family, 12)),
                anchor=style.get("anchor", tk.CENTER),
                fill="#000000"
            )
    canvas.create_text(
        x, y,
        text=text,
        font=style.get("font", (font_family, 12)),
        anchor=style.get("anchor", tk.CENTER),
        fill=style.get("fill", "#ffffff")
    )


def _init_canvas(canvas: Canvas, parent_frame: Frame | None) -> tuple[int, int, int, int, int, int]:
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
    margin_right = 40
    margin_top = 50
    chart_width = width - margin_left - margin_right

    return width, canvas_height, margin_left, margin_right, margin_top, chart_width


def _draw_parent_segment(
    canvas: Canvas,
    parent_info: dict[str, Any],
    x: float,
    y: float,
    chart_width: float,
    log_min: float,
    log_max: float,
    min_bar_width: float,
    bar_height: float,
    padding: float,
    is_ipv6: bool = False
) -> int:
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
        is_ipv6: 是否为IPv6地址

    Returns:
        int: 新的y坐标
    """
    parent_range = parent_info.get("range", 1)
    bar_width = _calculate_bar_width(parent_range, log_min, log_max, chart_width, min_bar_width)
    font_family = _get_font_settings()[0]

    color = PARENT_COLOR
    canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

    usable_addresses = _calculate_usable_addresses(parent_range, is_ipv6)
    parent_cidr = parent_info.get("name", "")
    
    # 优化IPv6地址显示
    if is_ipv6:
        parent_cidr = _optimize_ipv6_display(parent_cidr)
    
    segment_text = f"{translate("parent_network")}: {parent_cidr}"
    text_x = x + 15
    text_y = y + bar_height / 2
    font = (font_family, 11, "bold")
    _draw_segment_text(canvas, segment_text, text_x, text_y, font)

    address_text = f"{translate("usable_addresses")}: {format_large_number(usable_addresses)}"
    text_x = min(x + 450, x + chart_width - 150)
    _draw_segment_text(canvas, address_text, text_x, text_y, font)

    return int(y + bar_height + padding)


def _draw_network_segments(
    canvas: Canvas,
    split_networks: list[dict[str, Any]],
    chart_type: Literal["split", "plan"],
    x: float,
    y: float,
    chart_width: float,
    log_min: float,
    log_max: float,
    min_bar_width: float,
    bar_height: float,
    padding: float,
    is_ipv6: bool = False
) -> int:
    """绘制网络网段

    Args:
        canvas: tk.Canvas 对象
        split_networks: 切分网段列表
        chart_type: 图表类型
        x: x坐标
        y: y坐标
        chart_width: 图表宽度
        log_min: 最小对数
        log_max: 最大对数
        min_bar_width: 最小柱状图宽度
        bar_height: 柱状图高度
        padding: 内边距
        is_ipv6: 是否为IPv6地址

    Returns:
        int: 新的y坐标
    """
    font_family = _get_font_settings()[0]

    if chart_type == "plan":
        canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)
        y += 20

        demand_count = len(split_networks)
        canvas.create_text(
            x,
            y,
            text=f"{translate('allocated_subnets')} ({demand_count} {translate('pieces')}):",
            font=(font_family, 11),
            anchor=tk.W,
            fill="#ffffff",
        )
        y += 15

        for i, network in enumerate(split_networks):
            network_range = network.get("range", 1)
            bar_width = _calculate_bar_width(network_range, log_min, log_max, chart_width, min_bar_width)

            color_index = i % len(SUBNET_COLORS)
            color = SUBNET_COLORS[color_index]
            canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

            name = network.get("name", "")
            usable_addresses = _calculate_usable_addresses(network_range, is_ipv6)
            
            # 获取并优化IPv6地址显示
            cidr = network.get('cidr', '')
            if is_ipv6 and cidr:
                cidr = _optimize_ipv6_display(cidr)
            
            segment_text = f"{translate("segment")} {i + 1}: {name} {cidr}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = (font_family, 9, "bold")
            _draw_segment_text(canvas, segment_text, text_x, text_y, font)

            address_text = f"{translate("usable_addresses")}: {format_large_number(usable_addresses)}"
            text_x = min(x + 450, x + chart_width - 150)
            _draw_segment_text(canvas, address_text, text_x, text_y, font)

            y += bar_height + padding
    else:
        for i, network in enumerate(split_networks):
            network_range = network.get("range", 1)
            bar_width = _calculate_bar_width(network_range, log_min, log_max, chart_width, min_bar_width)

            color = SPLIT_COLOR
            canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

            name = network.get("name", "")
            usable_addresses = _calculate_usable_addresses(network_range, is_ipv6)

            segment_text = f"{translate("split_segment")}: {name}"
            text_x = x + 15
            text_y = y + bar_height / 2
            font = (font_family, 11, "bold")
            _draw_segment_text(canvas, segment_text, text_x, text_y, font)

            address_text = f"{translate("usable_addresses")}: {format_large_number(usable_addresses)}"
            text_x = min(x + 450, x + chart_width - 150)
            _draw_segment_text(canvas, address_text, text_x, text_y, font)

            y += bar_height + padding

            canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)

    if chart_type == "plan":
        canvas.create_line(x, y + 5, x + chart_width, y + 5, fill="#cccccc", dash=(5, 2), width=1)

    return int(y)


def _draw_remaining_segments(
    canvas: Canvas,
    networks: list[dict[str, Any]],
    x: float,
    y: float,
    chart_width: float,
    log_min: float,
    log_max: float,
    min_bar_width: float,
    bar_height: float,
    padding: float,
    is_ipv6: bool = False
) -> int:
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
        is_ipv6: 是否为IPv6地址

    Returns:
        int: 新的y坐标
    """
    font_family = _get_font_settings()[0]

    y += 20
    title_font = (font_family, 11)
    remaining_count = len([n for n in networks if n.get("type") != "split"])
    canvas.create_text(
        x,
        y,
        text=f"{translate('remaining_subnets')} ({remaining_count} {translate('pieces')}):",
        font=title_font,
        anchor=tk.W,
        fill="#ffffff",
    )
    y += 15

    remaining_networks = [net for net in networks if net.get("type") != "split"]
    for i, network in enumerate(remaining_networks):
        network_range = network.get("range", 1)
        bar_width = _calculate_bar_width(network_range, log_min, log_max, chart_width, min_bar_width)
        color_index = i % len(SUBNET_COLORS)
        color = SUBNET_COLORS[color_index]
        canvas.create_rectangle(x, y, x + bar_width, y + bar_height, fill=color, outline="", width=0)

        name = network.get("name", "")
        usable_addresses = _calculate_usable_addresses(network_range, is_ipv6)
        
        # 优化IPv6地址显示
        if is_ipv6 and name:
            name = _optimize_ipv6_display(name)
        
        segment_text = f"{translate("segment")} {i + 1}: {name}"
        text_x = x + 15
        text_y = y + bar_height / 2
        font = (font_family, 9, "bold")
        _draw_segment_text(canvas, segment_text, text_x, text_y, font)

        address_text = f"{translate("usable_addresses")}: {format_large_number(usable_addresses)}"
        text_x = min(x + 450, x + chart_width - 150)
        _draw_segment_text(canvas, address_text, text_x, text_y, font)

        y += bar_height + padding

    canvas.create_line(x, y, x + chart_width, y, fill="#cccccc", dash=(5, 2), width=1)

    return int(y)


def _draw_legend(canvas: Canvas, chart_type: Literal["split", "plan"], x: float, y: float) -> None:
    """绘制图例

    Args:
        canvas: tk.Canvas 对象
        chart_type: 图表类型
        x: x坐标
        y: y坐标
    """
    font_family = _get_font_settings()[0]

    legend_y = y + 35
    canvas.create_text(x, legend_y, text=f"{translate("legend")}:", font=(font_family, 11), anchor=tk.W, fill="#ffffff")

    legend_items_y = legend_y + 20

    canvas.create_rectangle(x, legend_items_y, x + 20, legend_items_y + 12, fill=PARENT_COLOR)
    canvas.create_text(
        x + 31,
        legend_items_y + 6,
        text=f"{translate("parent_network")}",
        font=(font_family, 9),
        anchor=tk.W,
        fill="#ffffff",
    )

    if chart_type == "plan":
        for j, color in enumerate(LEGEND_COLORS):
            canvas.create_rectangle(
                x + 140 + j * 20,
                legend_items_y,
                x + 160 + j * 20,
                legend_items_y + 12,
                fill=color,
            )
        canvas.create_text(
            x + 233,
            legend_items_y + 6,
            text=f"{translate("allocated_subnets")}",
            font=(font_family, 9),
            anchor=tk.W,
            fill="#ffffff",
        )

        remaining_start_x = x + 370
        for j, color in enumerate(LEGEND_COLORS):
            canvas.create_rectangle(
                remaining_start_x + j * 20,
                legend_items_y,
                remaining_start_x + 20 + j * 20,
                legend_items_y + 12,
                fill=color,
            )
        canvas.create_text(
            remaining_start_x + 94,
            legend_items_y + 6,
            text=f"{translate("remaining_subnets")}",
            font=(font_family, 9),
            anchor=tk.W,
            fill="#ffffff",
        )
    else:
        canvas.create_rectangle(x + 180, legend_items_y, x + 200, legend_items_y + 12, fill=SPLIT_COLOR)
        canvas.create_text(
            x + 210,
            legend_items_y + 6,
            text=f"{translate("split_segment")}",
            font=(font_family, 9),
            anchor=tk.W,
            fill="#ffffff",
        )

        remaining_start_x = x + 370
        for j, color in enumerate(LEGEND_COLORS):
            canvas.create_rectangle(
                remaining_start_x + j * 20,
                legend_items_y,
                remaining_start_x + 20 + j * 20,
                legend_items_y + 12,
                fill=color,
            )
        canvas.create_text(
            remaining_start_x + 94,
            legend_items_y + 6,
            text=f"{translate("remaining_subnets")}",
            font=(font_family, 9),
            anchor=tk.W,
            fill="#ffffff",
        )


def draw_distribution_chart(
    canvas: Canvas,
    chart_data: dict[str, Any] | None,
    parent_frame: Frame | None = None,
    chart_type: Literal["split", "plan"] = "split"
) -> None:
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

        width, canvas_height, margin_left, _, margin_top, chart_width = _init_canvas(canvas, parent_frame)

        parent_info = chart_data.get("parent", {})
        parent_range = parent_info.get("range", 1)
        networks = chart_data.get("networks", [])

        if not networks:
            font_family = _get_font_settings()[0]
            no_data_text = translate("no_segment_data") or "无网段数据"
            canvas.create_text(width / 2, canvas_height / 2, text=no_data_text, font=(font_family, 12))
            return

        # 判断是否为IPv6
        parent_cidr = parent_info.get("name", "")
        is_ipv6 = False
        try:
            network = ipaddress.ip_network(parent_cidr)
            is_ipv6 = network.version == 6
        except ValueError:
            # 如果无法解析为网络地址，尝试解析为IP地址
            try:
                address = ipaddress.ip_address(parent_cidr)
                is_ipv6 = address.version == 6
            except ValueError:
                # 无法解析，默认为IPv4
                is_ipv6 = False

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

        y = _draw_parent_segment(canvas, parent_info, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding, is_ipv6)

        split_networks = [net for net in networks if net.get("type") == "split"]
        y = _draw_network_segments(canvas, split_networks, chart_type, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding, is_ipv6)

        y = _draw_remaining_segments(canvas, networks, x, y, chart_width, log_min, log_max, min_bar_width, bar_height, padding, is_ipv6)

        _draw_legend(canvas, chart_type, x, y)

        canvas.update_idletasks()

    except (tk.TclError, ValueError, TypeError) as e:
        canvas.delete("all")
        width = canvas.winfo_width() or 600
        height = canvas.winfo_height() or 400
        font_family = _get_font_settings()[0]
        title_font = (font_family, 12, "bold")
        error_text = translate("chart_drawing_failed") or "图表绘制失败"
        canvas.create_text(
            width / 2, height / 2, text=error_text + ": " + str(e), font=title_font, fill="red")
