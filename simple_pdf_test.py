#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的PDF导出测试脚本

这个脚本用于直接测试PDF导出的核心功能，不依赖于主应用程序。
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 检查是否安装了ReportLab
print("=== 检查依赖库 ===")
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, Frame, PageTemplate, NextPageTemplate,
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        Image as RLImage, PageBreak, KeepTogether
    )
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    print("✓ 成功导入ReportLab库")
    has_reportlab = True
except ImportError as e:
    print(f"✗ 导入ReportLab库失败: {e}")
    has_reportlab = False
    sys.exit(1)

# 注册中文字体
def register_chinese_fonts():
    """注册中文字体"""
    try:
        # 尝试注册多种中文字体，提高兼容性
        font_files = [
            r"C:\Windows\Fonts\simsun.ttc",  # 宋体
            r"C:\Windows\Fonts\simhei.ttf",  # 黑体
            r"C:\Windows\Fonts\kaiu.ttf",    # 楷体
            r"C:\Windows\Fonts\msyh.ttf",    # 微软雅黑
        ]
        
        for font_path in font_files:
            if os.path.exists(font_path):
                # 注册字体
                font_name = "ChineseFont"
                if "simhei" in font_path:
                    font_name = "ChineseFont"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✓ 成功注册黑体字体: {font_path}")
                    return True
                elif "msyh" in font_path:
                    font_name = "ChineseFont"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✓ 成功注册微软雅黑字体: {font_path}")
                    return True
                elif "simsun" in font_path:
                    font_name = "ChineseFont"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✓ 成功注册宋体字体: {font_path}")
                    return True
                elif "kaiu" in font_path:
                    font_name = "ChineseFont"
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✓ 成功注册楷体字体: {font_path}")
                    return True
        
        print("✗ 未找到可用的中文字体文件")
        return False
        
    except Exception as e:
        print(f"✗ 注册中文字体失败: {e}")
        return False

# 创建测试图表
def create_test_chart(width=1600, height=900, dpi=300):
    """创建测试图表"""
    print(f"\n=== 创建测试图表 ({width}x{height}, {dpi} DPI) ===")
    
    # 创建图像
    image = Image.new('RGB', (width, height), color='#2c3e50')
    draw = ImageDraw.Draw(image)
    
    # 尝试加载中文字体
    font = None
    try:
        # 尝试加载多种中文字体
        font_files = [
            'simhei.ttf',
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\msyh.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
        ]
        
        for font_path in font_files:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 24)
                print(f"✓ 成功加载字体: {font_path}")
                break
        
        if font is None:
            font = ImageFont.load_default()
            print("✓ 使用默认字体")
    except Exception as e:
        font = ImageFont.load_default()
        print(f"✗ 加载字体失败，使用默认字体: {e}")
    
    # 绘制标题
    title = "网段分布图表"
    title_bbox = draw.textbbox((0, 0), title, font=font)
    title_x = (width - title_bbox[2] + title_bbox[0]) // 2
    title_y = 50
    draw.text((title_x, title_y), title, fill='#ffffff', font=font)
    
    # 绘制坐标轴
    margin = 100
    chart_width = width - 2 * margin
    chart_height = height - 2 * margin
    
    axis_color = '#bdc3c7'
    draw.line([(margin, margin), (margin, height - margin)], fill=axis_color, width=2)
    draw.line([(margin, height - margin), (width - margin, height - margin)], fill=axis_color, width=2)
    
    # 模拟图表数据
    parent_subnets = [
        {'label': '192.168.0.0/16', 'size': 65536, 'color': '#636e72'}
    ]
    split_subnets = [
        {'label': '192.168.1.0/24', 'size': 256, 'color': '#4a7eb4'},
        {'label': '192.168.2.0/24', 'size': 256, 'color': '#4a7eb4'},
        {'label': '192.168.3.0/24', 'size': 256, 'color': '#4a7eb4'}
    ]
    remaining_subnets = [
        {'label': '192.168.4.0/22', 'size': 1024, 'color': '#5e9c6a'},
        {'label': '192.168.8.0/21', 'size': 2048, 'color': '#db6679'},
        {'label': '192.168.16.0/20', 'size': 4096, 'color': '#f0ab55'},
        {'label': '192.168.32.0/19', 'size': 8192, 'color': '#8b6cb8'},
        {'label': '192.168.64.0/18', 'size': 16384, 'color': '#5e9c6a'},
        {'label': '192.168.128.0/17', 'size': 32768, 'color': '#db6679'}
    ]
    
    all_subnets = parent_subnets + split_subnets + remaining_subnets
    
    # 绘制柱状图
    bar_width = chart_width / len(all_subnets) * 0.8
    spacing = chart_width / len(all_subnets) * 0.2
    
    max_size = max(subnet['size'] for subnet in all_subnets)
    
    for i, subnet in enumerate(all_subnets):
        bar_x = margin + i * (bar_width + spacing)
        bar_height = (subnet['size'] / max_size) * chart_height
        bar_y = height - margin - bar_height
        
        # 绘制柱状图
        draw.rectangle([(bar_x, bar_y), (bar_x + bar_width, height - margin)], fill=subnet['color'])
        
        # 绘制标签
        label_font = ImageFont.truetype('simhei.ttf', 12) if os.path.exists('simhei.ttf') else ImageFont.load_default()
        label = f"{subnet['label']}"
        label_bbox = draw.textbbox((0, 0), label, font=label_font)
        label_x = bar_x + (bar_width - label_bbox[2] + label_bbox[0]) // 2
        label_y = bar_y - 10
        draw.text((label_x, label_y), label, fill='#ffffff', font=label_font)
    
    # 绘制图例
    legend_y = height - 150
    legend_x = margin
    
    # 图例说明文字垂直居中函数
    def get_centered_text_y(container_y, container_height, text_bbox):
        """计算文字垂直居中的y坐标，考虑中文基线特性"""
        text_height = text_bbox[3] - text_bbox[1]
        container_center = container_y + container_height // 2
        text_y = container_center - text_height // 2 + int(text_height * 0.05)
        return text_y
    
    # 父网段图例
    parent_color = "#636e72"
    parent_label = "父网段"
    
    parent_block_size = 40
    parent_text_font = ImageFont.truetype('simhei.ttf', 16) if os.path.exists('simhei.ttf') else ImageFont.load_default()
    parent_label_bbox = draw.textbbox((0, 0), parent_label, font=parent_text_font)
    
    parent_block_y = legend_y + (60 - parent_block_size) // 2
    parent_label_y = get_centered_text_y(legend_y, 60, parent_label_bbox)
    
    draw.rectangle([legend_x, parent_block_y, legend_x + parent_block_size, parent_block_y + parent_block_size], fill=parent_color, outline=None, width=0)
    draw.text((legend_x + parent_block_size + 25, parent_label_y), parent_label, fill="#ffffff", font=parent_text_font)
    
    # 切分网段图例
    split_x = legend_x + 300
    split_color = "#4a7eb4"
    split_label = "切分网段"
    
    split_block_size = 40
    split_text_font = ImageFont.truetype('simhei.ttf', 16) if os.path.exists('simhei.ttf') else ImageFont.load_default()
    split_label_bbox = draw.textbbox((0, 0), split_label, font=split_text_font)
    
    split_block_y = legend_y + (60 - split_block_size) // 2
    split_label_y = get_centered_text_y(legend_y, 60, split_label_bbox)
    
    draw.rectangle([split_x, split_block_y, split_x + split_block_size, split_block_y + split_block_size], fill=split_color, outline=None, width=0)
    draw.text((split_x + split_block_size + 25, split_label_y), split_label, fill="#ffffff", font=split_text_font)
    
    # 剩余网段图例
    remaining_x = split_x + 320
    remaining_label = "剩余网段(多色)"
    
    legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
    remaining_block_size = 30
    remaining_block_gap = 25
    
    remaining_text_font = ImageFont.truetype('simhei.ttf', 16) if os.path.exists('simhei.ttf') else ImageFont.load_default()
    remaining_label_bbox = draw.textbbox((0, 0), remaining_label, font=remaining_text_font)
    
    remaining_block_y = legend_y + (60 - remaining_block_size) // 2
    remaining_label_y = get_centered_text_y(legend_y, 60, remaining_label_bbox)
    
    # 绘制多个彩色块
    for j, color in enumerate(legend_colors):
        draw.rectangle([
            remaining_x + j * (remaining_block_size + remaining_block_gap),
            remaining_block_y,
            remaining_x + j * (remaining_block_size + remaining_block_gap) + remaining_block_size,
            remaining_block_y + remaining_block_size
        ], fill=color, outline=None, width=0)
    
    draw.text((remaining_x + 5 * remaining_block_size, remaining_label_y), remaining_label, fill="#ffffff", font=remaining_text_font)
    
    # 保存图像
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    image.save(temp_file, 'PNG', dpi=(dpi, dpi))
    temp_file.close()
    
    print(f"✓ 成功创建测试图表: {temp_file.name}")
    return temp_file.name

# 测试PDF导出
def test_pdf_export():
    """测试PDF导出功能"""
    print("\n=== 测试PDF导出功能 ===")
    
    # 注册中文字体
    has_chinese_font = register_chinese_fonts()
    print(f"中文字体注册结果: {has_chinese_font}")
    
    # 创建测试图表
    chart_file = create_test_chart(width=1600, height=900, dpi=300)
    
    try:
        # 设置页面边距
        margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)  # 左、右、上、下
        
        # 创建PDF文件
        pdf_file = 'simple_test_export.pdf'
        
        # 创建BaseDocTemplate，默认使用横向A4
        doc = BaseDocTemplate(
            pdf_file,
            pagesize=landscape(A4),
            leftMargin=margins[0],
            rightMargin=margins[1],
            topMargin=margins[2],
            bottomMargin=margins[3],
            showBoundary=False,
        )
        
        # 创建页面模板
        # 1. 横向页面模板
        landscape_width, landscape_height = landscape(A4)
        landscape_frame = Frame(
            margins[0],
            margins[3],
            landscape_width - margins[0] - margins[1],
            landscape_height - margins[2] - margins[3],
            id='landscape_frame'
        )
        landscape_template = PageTemplate(id='landscape', frames=[landscape_frame])
        
        # 2. 纵向页面模板
        portrait_width, portrait_height = A4  # A4默认纵向
        portrait_frame = Frame(
            margins[0],
            margins[3],
            portrait_width - margins[0] - margins[1],
            portrait_height - margins[2] - margins[3],
            id='portrait_frame'
        )
        portrait_template = PageTemplate(id='portrait', frames=[portrait_frame], pagesize=A4)
        
        # 添加页面模板
        doc.addPageTemplates([landscape_template, portrait_template])
        
        elements = []
        styles = getSampleStyleSheet()
        
        # 创建支持中文的标题样式
        title_style = ParagraphStyle(
            "ChineseTitle",
            parent=styles["Title"],
            fontName="ChineseFont" if has_chinese_font else "Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor("#2c3e50"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )
        
        # 添加标题
        elements.append(Paragraph("网段分配报告", title_style))
        elements.append(Spacer(1, 20))
        
        # 添加图表（纵向页面）
        elements.append(NextPageTemplate('portrait'))
        elements.append(Paragraph("网段分布图表", title_style))
        elements.append(Spacer(1, 20))
        
        # 添加图表图像
        from reportlab.platypus import Image as RLImage
        chart_image = RLImage(chart_file, width=18 * cm, height=10 * cm)
        elements.append(chart_image)
        elements.append(Spacer(1, 20))
        
        # 测试数据
        test_data = {
            'parent_subnet': '192.168.0.0/16',
            'total_hosts': 65534,
            'used_hosts': 768,
            'remaining_hosts': 64766,
            'split_subnets': [
                {'subnet': '192.168.1.0/24', 'gateway': '192.168.1.1', 'vlan': '100', 'description': '测试网段1'},
                {'subnet': '192.168.2.0/24', 'gateway': '192.168.2.1', 'vlan': '101', 'description': '测试网段2'},
                {'subnet': '192.168.3.0/24', 'gateway': '192.168.3.1', 'vlan': '102', 'description': '测试网段3'}
            ],
            'remaining_subnets': [
                {'subnet': '192.168.4.0/22', 'hosts': 1022, 'description': '剩余网段1'},
                {'subnet': '192.168.8.0/21', 'hosts': 2046, 'description': '剩余网段2'},
                {'subnet': '192.168.16.0/20', 'hosts': 4094, 'description': '剩余网段3'}
            ]
        }
        
        # 创建数据表格
        data_table = [
            ["父网段", test_data['parent_subnet']],
            ["总主机数", f"{test_data['total_hosts']:,}"],
            ["已分配主机数", f"{test_data['used_hosts']:,}"],
            ["剩余主机数", f"{test_data['remaining_hosts']:,}"],
        ]
        
        # 创建表格样式
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'ChineseFont' if has_chinese_font else 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ])
        
        # 添加表格
        table = Table(data_table, colWidths=[6 * cm, 12 * cm])
        table.setStyle(table_style)
        elements.append(table)
        
        # 生成PDF
        print("生成PDF文件...")
        doc.build(elements)
        
        if os.path.exists(pdf_file):
            file_size = os.path.getsize(pdf_file)
            print(f"✓ 成功生成PDF文件: {pdf_file} ({file_size:,} 字节)")
            return True
        else:
            print(f"✗ 生成PDF文件失败: {pdf_file} 不存在")
            return False
            
    except Exception as e:
        print(f"✗ PDF导出测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时文件
        if os.path.exists(chart_file):
            os.remove(chart_file)
            print(f"✓ 清理临时文件: {chart_file}")

# 主测试函数
def main():
    """主测试函数"""
    print("=== 开始简单PDF导出测试 ===")
    
    # 运行测试
    pdf_result = test_pdf_export()
    
    print("\n=== 测试结果汇总 ===")
    print(f"PDF导出测试: {'通过' if pdf_result else '失败'}")
    
    if pdf_result:
        print("\n🎉 PDF导出测试通过！")
        return 0
    else:
        print("\n❌ PDF导出测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
