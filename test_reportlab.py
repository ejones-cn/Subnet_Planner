#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试reportlab库是否能正常导入和使用
"""

import sys

try:
    # 测试reportlab导入
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    print("✓ reportlab库导入成功")
    
    # 创建一个简单的PDF文件
    file_path = "test_reportlab_output.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=landscape(A4))
    
    # 创建一些内容
    elements = []
    styles = getSampleStyleSheet()
    
    # 添加标题
    title = Paragraph("ReportLab测试", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # 添加表格
    data = [
        ['项目', '值'],
        ['父网段', '10.0.0.0/8'],
        ['切分网段', '10.21.60.0/23'],
        ['网络地址', '10.21.60.0'],
        ['子网掩码', '255.255.254.0'],
        ['可用地址数', '510'],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
    ]))
    
    elements.append(table)
    
    # 生成PDF
    doc.build(elements)
    
    print(f"✓ 成功创建测试PDF文件: {file_path}")
    print("✓ PDF导出功能测试通过")
    
    sys.exit(0)
    
except ImportError as e:
    print(f"✗ 导入错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ 其他错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)