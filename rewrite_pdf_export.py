#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重写windows_app.py中的PDF导出部分，修复所有缩进问题
"""

import os

def rewrite_pdf_export():
    """重写PDF导出部分，修复所有缩进问题"""
    # 读取原始文件
    with open('windows_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到PDF导出部分的开始和结束位置
    pdf_start = content.find('elif file_ext == \".pdf\":')
    if pdf_start == -1:
        print("未找到PDF导出部分")
        return
    
    pdf_end = content.find('elif file_ext == \".xlsx\":', pdf_start)
    if pdf_end == -1:
        print("未找到Excel导出部分")
        return
    
    # 创建新的PDF导出代码
    new_pdf_export = '''            elif file_ext == ".pdf":
                # PDF格式导出
                try:
                    print("\n=== PDF导出调试信息 ===")
                    print(f"文件路径: {file_path}")
                    print(f"文件扩展名: {file_ext}")
                    print("进入PDF导出分支")
                    from reportlab.lib.pagesizes import A4, landscape
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.platypus import (
                        Table,
                        TableStyle,
                        Paragraph,
                        Spacer,
                    )
                    from reportlab.lib import colors
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.lib.units import cm
                    from reportlab.lib.enums import TA_LEFT, TA_CENTER
                    import time
                    import subprocess
                    import sys
                    import traceback

                    # 注册中文字体
                    print("调用register_chinese_fonts()")
                    self.has_chinese_font = self.register_chinese_fonts()
                    print(f"中文字体注册结果: {self.has_chinese_font}")

                    # 创建PDF文档，使用BaseDocTemplate以支持多页面模板
                    print("创建PDF文档对象")
                    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, NextPageTemplate

                    # 设置页面边距
                    margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)  # 左、右、上、下

                    # 创建BaseDocTemplate，默认使用横向A4
                    doc = BaseDocTemplate(
                        file_path,
                        pagesize=landscape(A4),  # 默认横向
                        leftMargin=margins[0],
                        rightMargin=margins[1],
                        topMargin=margins[2],
                        bottomMargin=margins[3],
                        showBoundary=False,
                    )
                    print("PDF文档对象创建成功")

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

                    # 定义页面宽度变量，初始使用横向页面尺寸
                    page_width = landscape_width

                    elements = []
                    styles = getSampleStyleSheet()
                    print("创建样式表成功")

                    # 创建支持中文的标题样式
                    title_style = ParagraphStyle(
                        "ChineseTitle",
                        parent=styles["Title"],
                        fontName="ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                        fontSize=20,
                        textColor=colors.HexColor("#2c3e50"),  # 深蓝灰色
                        alignment=TA_CENTER,  # 居中对齐
                        spaceAfter=20,
                    )

                    # 创建支持中文的一级标题样式
                    heading2_style = ParagraphStyle(
                        "ChineseHeading2",
                        parent=styles["Heading2"],
                        fontName="ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                        fontSize=16,
                        textColor=colors.HexColor("#34495e"),  # 深灰色
                        alignment=TA_LEFT,
                        spaceBefore=20,
                        spaceAfter=12,
                    )

                    # 创建支持中文的正文样式
                    normal_style = ParagraphStyle(
                        "ChineseNormal",
                        parent=styles["Normal"],
                        fontName="ChineseFont" if self.has_chinese_font else "Helvetica",
                        fontSize=11,
                        textColor=colors.HexColor("#34495e"),  # 深灰色
                        spaceAfter=5,
                    )

                    # 创建支持中文的表格文本样式
                    table_text_style = ParagraphStyle(
                        "ChineseTableText",
                        parent=styles["Normal"],
                        fontName="ChineseFont" if self.has_chinese_font else "Helvetica",
                        fontSize=10,
                        alignment=TA_CENTER,  # 居中对齐
                    )

                    # 添加标题
                    elements.append(Paragraph(data_source["pdf_title"], title_style))
                    elements.append(Spacer(1, 10))

                    # 添加导出时间信息
                    export_time = time.strftime("%Y年%m月%d日 %H:%M:%S")
                    elements.append(Paragraph(f"导出时间: {export_time}", normal_style))
                    elements.append(Spacer(1, 15))

                    # 添加主数据信息
                    elements.append(Paragraph(data_source["main_name"], heading2_style))

                    # 如果是键值对格式（如切分网段信息）
                    if len(main_headers) == 2 and main_headers[0] == "项目" and main_headers[1] == "值":
                        main_table_data = [["项目", "值"]]
                        for values in main_data:
                            main_table_data.append(
                                [
                                    Paragraph(str(values[0]) if values[0] is not None else "", table_text_style),
                                    Paragraph(str(values[1]) if values[1] is not None else "", table_text_style),
                                ]
                            )
                    else:
                        main_table_data = [[Paragraph(h, table_text_style) for h in main_headers]]
                        for values in main_data:
                            main_table_data.append(
                                [Paragraph(str(v) if v is not None else "", table_text_style) for v in values]
                            )

                    if len(main_table_data) > 1:
                        # 计算表格宽度（页宽减去左右边距）
                        table_width = page_width - margins[0] - margins[1]

                        # 确定表格列数
                        table_cols = len(main_table_data[0])

                        # 使用指定的列宽或默认列宽
                        col_widths = data_source.get("main_table_cols")

                        # 处理字符串格式的列宽配置，如"1:1:1:1:1:1:1:1:1"
                        if isinstance(col_widths, str):
                            try:
                                # 尝试将字符串按冒号分割并转换为数字列表
                                col_ratios = [float(w) for w in col_widths.split(":")]
                                # 如果所有比例值都很小（< 10），将其解释为比例而不是直接宽度
                                if all(ratio < 10 for ratio in col_ratios):
                                    # 计算总比例
                                    total_ratio = sum(col_ratios)
                                    if total_ratio > 0:
                                        # 根据比例分配实际宽度
                                        col_widths = [table_width * (ratio / total_ratio) for ratio in col_ratios]
                                    else:
                                        # 如果总比例为0，使用默认列宽
                                        col_widths = None
                                else:
                                    # 否则直接使用转换后的宽度
                                    col_widths = col_ratios
                            except (ValueError, TypeError):
                                # 如果转换失败，使用默认列宽
                                col_widths = None

                        if not col_widths or len(col_widths) != table_cols:
                            if len(main_headers) == 2:  # 键值对格式
                                col_widths = [table_width * 0.3, table_width * 0.7]
                            else:
                                # 默认平均分配列宽
                                col_widths = [table_width / table_cols] * table_cols
                        else:
                            # 确保所有列宽值都是有效的数字且大于0
                            processed_col_widths = []
                            for width in col_widths:
                                try:
                                    # 尝试将宽度转换为数字
                                    numeric_width = float(width) if width is not None else table_width / table_cols
                                    if numeric_width <= 0:
                                        numeric_width = table_width / table_cols
                                    processed_col_widths.append(numeric_width)
                                except (ValueError, TypeError):
                                    processed_col_widths.append(table_width / table_cols)
                            col_widths = processed_col_widths

                        # 创建主表格
                        main_table = Table(main_table_data, colWidths=col_widths)

                        # 设置主表格样式
                        main_table.setStyle(
                            TableStyle(
                                [
                                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),  # 蓝色表头
                                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # 所有列居中对齐
                                    (
                                        "FONTNAME",
                                        (0, 0),
                                        (-1, 0),
                                        "ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                                    ),
                                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),  # 浅灰色边框
                                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3498db")),  # 蓝色外框
                                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),  # 浅灰色背景
                                ]
                            )
                        )

                        elements.append(main_table)
                    else:
                        elements.append(Paragraph(f"无{data_source['main_name']}", normal_style))

                    elements.append(Spacer(1, 20))

                    # 添加剩余网段信息
                    elements.append(Paragraph(data_source["remaining_name"], heading2_style))
                    remaining_table_data = [[Paragraph(h, table_text_style) for h in remaining_headers]]
                    for item in remaining_tree.get_children():
                        values = remaining_tree.item(item, "values")
                        if values:
                            remaining_table_data.append(
                                [Paragraph(str(v) if v is not None else "", table_text_style) for v in values]
                            )

                    if len(remaining_table_data) > 1:
                        # 计算剩余表格宽度
                        remaining_table_width = page_width - margins[0] - margins[1]
                        remaining_table_cols = len(remaining_table_data[0])

                        # 使用指定的列宽或默认列宽
                        remaining_col_widths = data_source.get("remaining_table_cols")

                        # 处理字符串格式的列宽配置
                        if isinstance(remaining_col_widths, str):
                            try:
                                col_ratios = [float(w) for w in remaining_col_widths.split(":")]
                                if all(ratio < 10 for ratio in col_ratios):
                                    total_ratio = sum(col_ratios)
                                    if total_ratio > 0:
                                        remaining_col_widths = [remaining_table_width * (ratio / total_ratio) for ratio in col_ratios]
                                    else:
                                        remaining_col_widths = None
                                else:
                                    remaining_col_widths = col_ratios
                            except (ValueError, TypeError):
                                remaining_col_widths = None

                        if not remaining_col_widths or len(remaining_col_widths) != remaining_table_cols:
                            remaining_col_widths = [remaining_table_width / remaining_table_cols] * remaining_table_cols

                        # 创建剩余网段表格
                        remaining_table = Table(remaining_table_data, colWidths=remaining_col_widths)

                        # 设置剩余网段表格样式
                        remaining_table.setStyle(
                            TableStyle(
                                [
                                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                    (
                                        "FONTNAME",
                                        (0, 0),
                                        (-1, 0),
                                        "ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
                                    ),
                                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bdc3c7")),
                                    ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#3498db")),
                                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
                                ]
                            )
                        )

                        elements.append(remaining_table)
                    else:
                        elements.append(Paragraph(f"无{data_source['remaining_name']}", normal_style))

                    # 检查是否需要添加网段分布图
                    has_chart_data = hasattr(self, 'chart_data') and self.chart_data is not None
                    has_chart_data = has_chart_data and isinstance(self.chart_data, dict)
                    has_chart_data = has_chart_data and 'networks' in self.chart_data
                    has_chart_data = has_chart_data and len(self.chart_data['networks']) > 0
                    print(f"是否有网段分布图数据: {has_chart_data}")

                    if has_chart_data:
                        try:
                            print("检测到有效网段分布图数据，准备添加到PDF")
                            from reportlab.platypus import Image
                            import io
                            import base64

                            # 检查是否有graph_data
                            if hasattr(self, 'graph_data') and self.graph_data is not None:
                                print("使用graph_data生成图像")
                                graph_data = self.graph_data

                                # 提取图像数据
                                if isinstance(graph_data, str) and graph_data.startswith('data:image/png;base64,'):
                                    # 提取base64图像数据
                                    image_data = graph_data.split(',', 1)[1]
                                    img_byte_arr = io.BytesIO(base64.b64decode(image_data))
                                    print("成功解码base64图像数据")
                                elif isinstance(graph_data, bytes):
                                    # 直接使用字节流
                                    img_byte_arr = io.BytesIO(graph_data)
                                    print("直接使用字节流图像数据")
                                else:
                                    print(f"不支持的graph_data类型: {type(graph_data)}")
                                    raise ValueError(f"不支持的graph_data类型: {type(graph_data)}")

                                # 计算图像在PDF中的合适尺寸
                                from PIL import Image as PILImage
                                with PILImage.open(img_byte_arr) as img:
                                    # 获取原始图像尺寸
                                    original_width, original_height = img.size
                                    print(f"原始图像尺寸: {original_width}x{original_height}")

                                    # 重置文件指针到开始位置
                                    img_byte_arr.seek(0)

                                    # 计算图像在PDF中的最佳尺寸，保持宽高比
                                    image_ratio = original_width / original_height

                                    # 计算PDF可用空间，确保图像不超过页面框架
                                    available_width = page_width - margins[0] - margins[1] - 40
                                    available_height = 20 * cm
                                    print(f"PDF可用空间: {available_width:.1f}x{available_height:.1f}点")

                                    # 计算PDF中图像的最佳尺寸，保持宽高比，确保图表能完整显示
                                    final_pdf_height = available_height
                                    final_pdf_width = final_pdf_height * image_ratio

                                    if final_pdf_width > available_width:
                                        final_pdf_width = available_width
                                        final_pdf_height = final_pdf_width / image_ratio

                                    # 确保最终尺寸合理
                                    final_pdf_width = max(100, final_pdf_width)
                                    final_pdf_height = max(100, final_pdf_height)

                                    # 计算实际DPI，用于调试
                                    high_res_width, high_res_height = original_width, original_height
                                    actual_dpi = high_res_width / (final_pdf_width / 72.0)
                                    print(f"图像在PDF中的尺寸: {final_pdf_width:.1f}x{final_pdf_height:.1f}点，实际DPI: {actual_dpi:.1f}")

                                # 图表本身已经包含了"网段分布图"标题，所以不需要在PDF页面上重复显示
                                chart_elements = []

                                # 添加换行符和图表标题
                                chart_elements.append(Paragraph("网段分布图", heading2_style))
                                chart_elements.append(Spacer(1, 10))

                                # 确保文件指针在开始位置
                                img_byte_arr.seek(0)

                                # 添加图像到图表元素
                                chart_elements.append(Image(img_byte_arr, width=final_pdf_width, height=final_pdf_height))

                                # 添加分页符，确保图表单独占一页
                                from reportlab.platypus import PageBreak
                                chart_elements.append(PageBreak())

                                # 添加图表元素到主文档
                                elements.extend(chart_elements)
                                print("网段分布图成功添加到PDF")
                            else:
                                print("graph_data不存在或为空，跳过添加网段分布图")
                        except Exception as e:
                            print(f"添加网段分布图到PDF失败: {type(e).__name__}: {e}")
                            traceback.print_exc()
                            # 清除临时文件（如果有）
                            # 在PDF生成后由系统自动清理
                    else:
                        print("没有检测到有效网段分布图数据，跳过添加")

                    # 生成PDF
                    print("开始生成PDF文档...")
                    try:
                        # 确保中文支持
                        # 注册中文字体，确保与register_chinese_fonts方法一致
                        try:
                            # 使用已注册的ChineseFont，确保字体名称一致
                            print(f"使用已注册的中文字体，has_chinese_font: {self.has_chinese_font}")
                            if self.has_chinese_font:
                                # 确认ChineseFont已经注册
                                if 'ChineseFont' in pdfmetrics.getRegisteredFontNames():
                                    print("ChineseFont已成功注册，使用该字体")
                                    # 确保所有样式使用正确的字体名称
                                    title_style.fontName = 'ChineseFont'
                                    heading2_style.fontName = 'ChineseFont'
                                    normal_style.fontName = 'ChineseFont'
                                    table_text_style.fontName = 'ChineseFont'
                                    print("已更新所有样式使用ChineseFont字体")
                                else:
                                    print("ChineseFont未注册，重新注册")
                                    # 重新注册中文字体
                                    self.has_chinese_font = self.register_chinese_fonts()
                                    if self.has_chinese_font:
                                        print("重新注册中文字体成功")
                            else:
                                print("未注册中文字体，尝试重新注册")
                                self.has_chinese_font = self.register_chinese_fonts()
                        except Exception as e:
                            print(f"处理中文字体失败: {e}")
                            traceback.print_exc()

                        # 移除未定义的add_footer回调
                        doc.build(elements)
                        print("PDF文档生成成功")
                    except Exception as e:
                        print(f"PDF文档生成失败: {type(e).__name__}: {e}")
                        traceback.print_exc()
                    print("=== PDF导出调试信息结束 ===")
                except ImportError as e:
                    print(f"PDF导出失败: {type(e).__name__}: {e}")
                    import sys
                    import traceback
                    traceback.print_exc()
                    # 捕获reportlab导入错误，提供友好的错误信息
                    error_msg = f"PDF导出失败: 缺少reportlab模块\n\n"\
                                f"当前Python解释器: {sys.executable}\n\n"\
                                f"解决方案:\n"\
                                f"1. 打开命令行终端\n"\
                                f"2. 执行以下命令安装reportlab:\n"\
                                f"   {sys.executable} -m pip install reportlab\n"\
                                f"3. 安装完成后重新运行程序\n\n"\
                                f"或者使用其他格式导出数据，如CSV、Excel等。"
                    self.show_error("PDF导出失败", error_msg)
                    return
                except Exception as e:
                    print(f"PDF导出失败: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    # 其他PDF导出错误
                    self.show_error("PDF导出失败", f"PDF导出失败: {str(e)}")
                    return
'''
    
    # 替换原始内容
    new_content = content[:pdf_start] + new_pdf_export + content[pdf_end:]
    
    # 保存修复后的文件
    with open('windows_app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("PDF导出部分重写完成，所有缩进问题已修复")

if __name__ == "__main__":
    rewrite_pdf_export()
