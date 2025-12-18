#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证多网段情况下PDF导出图表完整性
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

# 测试动态高度计算

def test_dynamic_height():
    """测试动态高度计算"""
    print("=== 测试动态高度计算 ===")
    
    # 模拟数据：23个网段
    networks = []
    for i in range(23):
        networks.append({
            "name": f"10.0.{i}.0/{24-i%12}",
            "range": 1000000 // (i+1),
            "type": "split" if i < 2 else "other"
        })
    
    # 动态计算图表所需的总高度
    high_res_width = 2480
    high_res_height = 3508
    
    # 基础高度：标题、父网段、切分网段、剩余网段标题、图例等
    base_height = 280 + 100 + 100 + 150 + 200  # 基础元素高度
    
    # 计算所有网段所需的总高度
    split_networks = [net for net in networks if net.get("type") == "split"]
    remaining_networks = [net for net in networks if net.get("type") != "split"]
    total_networks = len(split_networks) + len(remaining_networks)
    
    # 每个网段占用的高度：bar_height + padding
    bar_height = 100
    padding = 34
    segment_height = bar_height + padding
    
    # 计算总高度
    required_height = base_height + total_networks * segment_height
    
    # 确保高度至少为原始A4高度
    dynamic_high_res_height = max(high_res_height, required_height)
    
    print(f"网段数量: {total_networks}")
    print(f"基础高度: {base_height} px")
    print(f"每个网段高度: {segment_height} px")
    print(f"所需总高度: {required_height} px")
    print(f"原始A4高度: {high_res_height} px")
    print(f"动态计算高度: {dynamic_high_res_height} px")
    print(f"是否需要扩展高度: {dynamic_high_res_height > high_res_height}")
    
    # 创建测试图像
    print("\n=== 创建测试图像 ===")
    test_image = Image.new('RGB', (high_res_width, dynamic_high_res_height), color='#333333')
    draw = ImageDraw.Draw(test_image)
    
    # 加载字体
    font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'simhei.ttf')
    if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, 36)
        bold_font = ImageFont.truetype(font_path, 40)
    else:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # 绘制标题
    title = "测试多网段分布图"
    title_bbox = draw.textbbox((0, 0), title, font=bold_font)
    title_x = (high_res_width - (title_bbox[2] - title_bbox[0])) // 2
    title_y = 100
    draw.text((title_x, title_y), title, fill="#ffffff", font=bold_font)
    
    # 绘制网段
    y = 280
    for i, net in enumerate(networks):
        # 绘制条状图
        color = f"#{i*10:02x}{i*5:02x}{255-i*10:02x}"
        draw.rectangle([180, y, 180 + 500, y + bar_height], fill=color)
        
        # 绘制网段文本
        segment_text = f"网段 {i+1}: {net['name']}"
        segment_bbox = draw.textbbox((0, 0), segment_text, font=font)
        draw.text((210, y + bar_height // 2 - 20), segment_text, fill="#ffffff", font=font)
        
        y += segment_height
    
    # 绘制图例
    draw.text((180, y + 50), "图例说明", fill="#ffffff", font=bold_font)
    
    # 保存测试图像
    temp_file = tempfile.mktemp(suffix='.png')
    test_image.save(temp_file, 'PNG', dpi=(300, 300))
    print(f"测试图像保存到: {temp_file}")
    print(f"测试图像尺寸: {test_image.size}")
    print(f"测试图像DPI: 300")
    
    return temp_file

if __name__ == "__main__":
    temp_file = test_dynamic_height()
    print(f"\n测试完成！生成的测试图像文件: {temp_file}")
