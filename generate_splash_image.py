#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成子网规划师启动画面图片
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys

# 添加当前目录到路径，确保能导入i18n模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i18n import _


def create_splash_image():
    """创建子网规划师启动画面"""
    width, height = 500, 450  # 调整为程序显示的尺寸，避免变形

    img = Image.new('RGB', (width, height), color='#0F172A')
    draw = ImageDraw.Draw(img)

    primary = '#1E293B'
    secondary = '#334155'
    accent = '#22C55E'
    text_color = '#F8FAFC'
    muted = '#94A3B8'

    draw.rectangle([0, 0, width, height], fill='#0F172A')

    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill='#1E293B', width=1)
    for i in range(0, height, 40):
        draw.line([(0, i), (width, i)], fill='#1E293B', width=1)

    center_x, center_y = width // 2, height // 2

    for layer in range(3, 0, -1):
        radius = 40 + layer * 35  # 调整半径以适应新尺寸
        alpha = 40 - layer * 10
        color = f'#{alpha:02x}{alpha:02x}{alpha:02x}'
        draw.ellipse(
            [center_x - radius, center_y - radius,
             center_x + radius, center_y + radius],
            fill=color,
            outline='#334155'
        )

    nodes = [
        (center_x, center_y),
        (center_x - 90, center_y - 50),
        (center_x + 90, center_y - 50),
        (center_x - 90, center_y + 50),
        (center_x + 90, center_y + 50),
        (center_x - 160, center_y),
        (center_x + 160, center_y),
        (center_x, center_y - 90),
        (center_x, center_y + 90),
    ]

    connections = [
        (0, 1), (0, 2), (0, 3), (0, 4),
        (1, 2), (3, 4),
        (1, 5), (2, 6),
        (3, 7), (4, 8),
        (5, 7), (6, 8),
    ]

    for start, end in connections:
        draw.line(
            [nodes[start], nodes[end]],
            fill='#334155',
            width=2
        )

    for i, (x, y) in enumerate(nodes):
        node_color = accent if i == 0 else '#475569'
        node_size = 12 if i == 0 else 8  # 调整节点大小
        draw.ellipse(
            [x - node_size, y - node_size,
             x + node_size, y + node_size],
            fill=node_color,
            outline='#64748B'
        )

    ip_labels = [
        ('192.168.1.0/24', center_x, center_y + 70),
        ('10.0.0.0/16', center_x - 110, center_y - 60),
        ('172.16.0.0/12', center_x + 110, center_y - 60),
    ]

    try:
        # 尝试使用支持中文的字体，优先使用黑体
        font_candidates = ["simhei.ttf", "msyh.ttf", "simsun.ttc", "arial.ttf"]
        font = None
        for font_name in font_candidates:
            try:
                font = ImageFont.truetype(font_name, 14)
                break
            except:
                continue
        if not font:
            font = ImageFont.load_default()
        
        font_large = None
        for font_name in font_candidates:
            try:
                font_large = ImageFont.truetype(font_name, 28)
                break
            except:
                continue
        if not font_large:
            font_large = font
        
        font_title = None
        for font_name in font_candidates:
            try:
                font_title = ImageFont.truetype(font_name, 42)
                break
            except:
                continue
        if not font_title:
            font_title = font
    except:
        font = ImageFont.load_default()
        font_large = font
        font_title = font

    for text, x, y in ip_labels:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.rectangle(
            [x - text_width // 2 - 10, y - 12,
             x + text_width // 2 + 10, y + 12],
            fill='#1E293B',
            outline='#334155'
        )
        draw.text(
            (x - text_width // 2, y - 10),
            text,
            fill=accent,
            font=font
        )

    try:
        font_subtitle = None
        for font_name in font_candidates:
            try:
                font_subtitle = ImageFont.truetype(font_name, 20)
                break
            except:
                continue
        if not font_subtitle:
            font_subtitle = font
    except:
        font_subtitle = font_title

    # 移除标题和进度条，只保留网络拓扑图
    # 不需要标题文字，因为启动画面已经有标题
    # 不需要进度条，因为加载过程很快

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'splash_image.png')
    img.save(output_path, 'PNG', quality=95)
    print(f"启动图片已生成: {output_path}")
    return output_path


if __name__ == '__main__':
    create_splash_image()
