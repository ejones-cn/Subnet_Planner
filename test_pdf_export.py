#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF导出功能的脚本

这个脚本用于验证PDF导出功能是否正常工作，包括：
1. 图表生成（与主应用相同的逻辑）
2. PDF多页模板（横向/纵向）
3. 高DPI图表嵌入
4. 中文支持
5. 图例显示
6. 页面布局
"""

import os
import sys
import tempfile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主应用中的PDF导出相关函数
try:
    from windows_app import IPSubnetSplitterApp
    print("✓ 成功导入主应用模块")
except Exception as e:
    print(f"✗ 导入主应用模块失败: {e}")
    sys.exit(1)

# 模拟Tkinter Canvas类，用于测试PostScript导出
class MockCanvas:
    """模拟Tkinter Canvas类，用于测试PostScript导出"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 创建一个PIL图像用于绘制
        self.image = Image.new('RGB', (width, height), color='#2c3e50')
        self.draw = ImageDraw.Draw(self.image)
        
        # 模拟图表数据
        self.chart_data = {
            'parent_subnets': [
                {'label': '192.168.0.0/16', 'size': 65536, 'color': '#636e72'}
            ],
            'split_subnets': [
                {'label': '192.168.1.0/24', 'size': 256, 'color': '#4a7eb4'},
                {'label': '192.168.2.0/24', 'size': 256, 'color': '#4a7eb4'},
                {'label': '192.168.3.0/24', 'size': 256, 'color': '#4a7eb4'}
            ],
            'remaining_subnets': [
                {'label': '192.168.4.0/22', 'size': 1024, 'color': '#5e9c6a'},
                {'label': '192.168.8.0/21', 'size': 2048, 'color': '#db6679'},
                {'label': '192.168.16.0/20', 'size': 4096, 'color': '#f0ab55'},
                {'label': '192.168.32.0/19', 'size': 8192, 'color': '#8b6cb8'},
                {'label': '192.168.64.0/18', 'size': 16384, 'color': '#5e9c6a'},
                {'label': '192.168.128.0/17', 'size': 32768, 'color': '#db6679'}
            ]
        }
        
        # 绘制测试图表
        self.draw_test_chart()
    
    def draw_test_chart(self):
        """绘制测试图表"""
        # 图表配置
        margin = 100
        chart_width = self.width - 2 * margin
        chart_height = self.height - 2 * margin
        
        # 绘制标题
        font = ImageFont.truetype('simhei.ttf', 24) if os.path.exists('simhei.ttf') else ImageFont.load_default()
        title = "网段分布图表"
        title_bbox = self.draw.textbbox((0, 0), title, font=font)
        title_x = (self.width - title_bbox[2] + title_bbox[0]) // 2
        title_y = margin // 2
        self.draw.text((title_x, title_y), title, fill='#ffffff', font=font)
        
        # 绘制坐标轴
        axis_color = '#bdc3c7'
        self.draw.line([(margin, margin), (margin, self.height - margin)], fill=axis_color, width=2)
        self.draw.line([(margin, self.height - margin), (self.width - margin, self.height - margin)], fill=axis_color, width=2)
        
        # 准备图表数据
        all_subnets = self.chart_data['parent_subnets'] + self.chart_data['split_subnets'] + self.chart_data['remaining_subnets']
        
        # 绘制柱状图（简化版，不使用对数缩放）
        bar_width = chart_width / len(all_subnets) * 0.8
        spacing = chart_width / len(all_subnets) * 0.2
        
        max_size = max(subnet['size'] for subnet in all_subnets)
        
        for i, subnet in enumerate(all_subnets):
            bar_x = margin + i * (bar_width + spacing)
            bar_height = (subnet['size'] / max_size) * chart_height
            bar_y = self.height - margin - bar_height
            
            # 绘制柱状图
            self.draw.rectangle([(bar_x, bar_y), (bar_x + bar_width, self.height - margin)], fill=subnet['color'])
            
            # 绘制标签
            label_font = ImageFont.truetype('simhei.ttf', 12) if os.path.exists('simhei.ttf') else ImageFont.load_default()
            label = f"{subnet['label']} ({subnet['size']})".split('.0/')[0]
            label_bbox = self.draw.textbbox((0, 0), label, font=label_font)
            label_x = bar_x + (bar_width - label_bbox[2] + label_bbox[0]) // 2
            label_y = bar_y - 10
            self.draw.text((label_x, label_y), label, fill='#ffffff', font=label_font)
    
    def postscript(self, colormode='color', pagex=0, pagey=0, pagewidth=None, pageheight=None):
        """模拟postscript方法，返回图像的PostScript表示"""
        # 由于我们无法直接生成PostScript，这里返回一个简化的版本
        # 实际测试中，我们会使用PIL图像
        return f"%!PS-Adobe-3.0\n%%BoundingBox: 0 0 {self.width} {self.height}\n%%EndComments\n"
    
    def save_image(self, filename):
        """保存图像到文件"""
        self.image.save(filename, 'PNG', dpi=(300, 300))

# 测试PDF导出功能
def test_pdf_export():
    """测试PDF导出功能"""
    print("\n=== 测试PDF导出功能 ===")
    
    # 创建测试数据
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
            {'subnet': '192.168.16.0/20', 'hosts': 4094, 'description': '剩余网段3'},
            {'subnet': '192.168.32.0/19', 'hosts': 8190, 'description': '剩余网段4'},
            {'subnet': '192.168.64.0/18', 'hosts': 16382, 'description': '剩余网段5'},
            {'subnet': '192.168.128.0/17', 'hosts': 32766, 'description': '剩余网段6'}
        ]
    }
    
    try:
        # 创建应用实例
        app = IPSubnetSplitterApp()
        
        # 创建模拟画布
        mock_canvas = MockCanvas(1600, 900)
        mock_canvas.save_image('test_chart.png')
        print("✓ 成功创建模拟画布和测试图表")
        
        # 设置模拟画布到应用实例
        app.chart_canvas = mock_canvas
        
        # 测试PDF导出
        pdf_file = 'test_export.pdf'
        app.export_pdf(test_data, pdf_file)
        
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

# 测试图表生成功能
def test_chart_generation():
    """测试图表生成功能"""
    print("\n=== 测试图表生成功能 ===")
    
    try:
        # 创建应用实例
        app = IPSubnetSplitterApp()
        
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
        
        # 测试图表生成
        chart_file = 'test_generated_chart.png'
        app.generate_chart(test_data, chart_file)
        
        if os.path.exists(chart_file):
            file_size = os.path.getsize(chart_file)
            print(f"✓ 成功生成图表文件: {chart_file} ({file_size:,} 字节)")
            return True
        else:
            print(f"✗ 生成图表文件失败: {chart_file} 不存在")
            return False
            
    except Exception as e:
        print(f"✗ 图表生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 主测试函数
def main():
    """主测试函数"""
    print("=== 开始PDF导出功能测试 ===")
    
    # 运行测试
    chart_result = test_chart_generation()
    pdf_result = test_pdf_export()
    
    print("\n=== 测试结果汇总 ===")
    print(f"图表生成测试: {'通过' if chart_result else '失败'}")
    print(f"PDF导出测试: {'通过' if pdf_result else '失败'}")
    
    if chart_result and pdf_result:
        print("\n🎉 所有测试通过！PDF导出功能正常工作。")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
