#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出工具模块

提供多种格式的数据导出功能，包括:
1. PDF格式导出（支持中文）
2. JSON格式导出
3. TXT格式导出
4. CSV格式导出
5. Excel格式导出

所有导出功能均正确处理中文编码问题。
项目版本：v2.5.2
"""

import os
import sys
import json
import csv
import time
import traceback
import math
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from i18n import _ as translate, get_language  # _ 是翻译函数，这里重命名为 translate 以避免冲突
from reportlab.lib.pagesizes import A4, landscape  # type: ignore
from reportlab.lib.units import cm  # type: ignore
from reportlab.lib import colors  # type: ignore
from reportlab.platypus import (  # type: ignore
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image as RLImage,
    PageBreak,
    NextPageTemplate,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.pdfbase import pdfmetrics  # type: ignore
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # type: ignore
from openpyxl import Workbook  # type: ignore
from openpyxl.styles import Font, Alignment  # type: ignore

MAIN_TABLE_COLORS = {
    "header_bg": "#3498db",
    "header_text": "white",
    "box": "#3498db",
    "row_even": "#f0f4f8",
}

REMAINING_TABLE_COLORS = {
    "header_bg": "#27ae60",
    "header_text": "white",
    "box": "#27ae60",
    "row_even": "#f0f4f8",
}

TABLE_COMMON_STYLE = [
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("GRID", (0, 0), (-1, -1), 1, "#bdc3c7"),
    ("BACKGROUND", (0, 1), (-1, -1), "#f8f9fa"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), ["white", "#f0f4f8"]),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("TOPPADDING", (0, 0), (-1, -1), 2),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
]

HEADER_STYLE = [
    ("FONTSIZE", (0, 0), (-1, 0), 11),
    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ("TOPPADDING", (0, 0), (-1, 0), 4),
]

K2V_HEADERS = ["项目", "值"]


class ExportUtils:
    """数据导出工具类"""

    def __init__(self):
        """初始化导出工具"""
        self.has_chinese_font = False
        self._register_chinese_fonts()

    def _register_chinese_fonts(self):
        """注册中文字体供PDF导出使用"""
        font_path = None

        if sys.platform == "win32":
            font_dir = "C:\\Windows\\Fonts"
            if os.path.exists(font_dir):
                font_candidates = [
                    ("simhei.ttf", "SimHei"),
                    ("simsun.ttc", "SimSun"),
                    ("msyh.ttf", "Microsoft YaHei"),
                    ("msyhbd.ttf", "Microsoft YaHei Bold"),
                    ("msyhui.ttf", "Microsoft YaHei UI"),
                    ("stsong.ttf", "STSong"),
                    ("stheiti.ttf", "STHeiti"),
                    ("stkaiti.ttf", "STKaiti"),
                ]

                for font_file, _unused in font_candidates:
                    potential_path = os.path.join(font_dir, font_file)
                    if os.path.exists(potential_path):
                        font_path = potential_path
                        if font_file.lower() == "simhei.ttf":
                            break

        if font_path:
            try:
                pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                self.has_chinese_font = True
            except (OSError, ValueError, ImportError) as e:
                print(f"注册字体失败: {e}")
                self.has_chinese_font = False
        else:
            print("未找到可用的中文字体")
            self.has_chinese_font = False

    def _calculate_auto_col_widths(self, table_data, table_width):
        """根据内容计算自适应列宽

        Args:
            table_data: 表格数据，包含Paragraph对象的列表
            table_width: 表格可用宽度

        Returns:
            list: 每列的自适应宽度
        """
        table_cols = len(table_data[0]) if table_data else 0
        max_col_widths = [0] * table_cols
        min_col_width = 60  # 调整最小列宽

        # 计算每列的最大内容宽度
        for row in table_data:
            for col_idx, cell in enumerate(row):
                if hasattr(cell, 'getPlainText'):
                    text = cell.getPlainText()
                elif hasattr(cell, 'text'):
                    text = cell.text
                else:
                    text = str(cell)

                # 更精确的字符宽度计算，确保足够容纳内容
                text_width = 0
                for char in text:
                    if ord(char) > 127:
                        # 中文、日文等非ASCII字符使用12宽度
                        text_width += 12
                    else:
                        # ASCII字符使用8宽度，确保足够容纳英文字母和数字
                        text_width += 8
                text_width += 15  # 调整额外边距，确保有足够空间

                if text_width > max_col_widths[col_idx]:
                    max_col_widths[col_idx] = text_width

        # 确保最小列宽
        for i, width in enumerate(max_col_widths):
            if width < min_col_width:
                max_col_widths[i] = min_col_width

        # 计算总宽度和比例
        total_width = sum(max_col_widths)
        final_widths = []

        # 收集所有数据行的内容宽度，不仅仅是表头
        data_col_widths = [0] * table_cols
        for row_idx, row in enumerate(table_data):
            if row_idx == 0:  # 跳过表头，只考虑数据行
                continue
            for col_idx, cell in enumerate(row):
                if hasattr(cell, 'getPlainText'):
                    text = cell.getPlainText()
                elif hasattr(cell, 'text'):
                    text = cell.text
                else:
                    text = str(cell)
                
                # 计算数据行内容宽度
                text_width = 0
                for char in text:
                    if ord(char) > 127:
                        text_width += 12
                    else:
                        text_width += 8
                text_width += 15
                
                if text_width > data_col_widths[col_idx]:
                    data_col_widths[col_idx] = text_width

        if total_width > 0:
            # 结合表头和数据行的宽度，计算最终列宽
            combined_widths = [max(max_col_widths[i], data_col_widths[i]) for i in range(table_cols)]
            
            # 先分配最小宽度
            remaining_width = table_width
            for i in range(table_cols):
                final_widths.append(min_col_width)
                remaining_width -= min_col_width
            
            # 计算每列可分配的额外宽度，基于实际内容（表头+数据行的最大值）
            if remaining_width > 0:
                # 计算各列超出最小宽度的部分
                extra_widths = [max(0, combined_widths[i] - min_col_width) for i in range(table_cols)]
                total_extra = sum(extra_widths)
                
                if total_extra > 0:
                    # 按比例分配额外宽度
                    for i in range(table_cols):
                        if extra_widths[i] > 0:
                            extra = (extra_widths[i] / total_extra) * remaining_width
                            final_widths[i] += extra
                        # 对于数据行内容很少的列，限制最大宽度
                        if data_col_widths[i] < min_col_width * 1.5:
                            final_widths[i] = min(final_widths[i], min_col_width * 1.5)
        else:
            # 平均分配宽度
            final_widths = [table_width / table_cols] * table_cols

        return final_widths

    def _is_k2v_headers(self, headers):
        return len(headers) == 2 and headers[0] == translate("item") and headers[1] == translate("value")

    def _get_col_widths(self, table_data, table_width, col_widths, num_cols):
        """获取表格列宽，确保自适应页面宽度"""
        try:
            # 始终使用自适应宽度计算
            auto_col_widths = self._calculate_auto_col_widths(table_data, table_width)
            col_widths = auto_col_widths
        except (ValueError, TypeError, AttributeError):
            traceback.print_exc()
            # 回退到平均分配宽度
            col_widths = [table_width / num_cols] * num_cols

        # 确保列宽有效
        valid = []
        for width in col_widths:
            if width is None or not isinstance(width, (int, float)) or width <= 0:
                valid.append(100)
            else:
                valid.append(width)

        return valid

    def _get_table_style(self, table_colors, has_chinese_font):
        header_font = "ChineseFont" if has_chinese_font else "Helvetica-Bold"
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), table_colors["header_bg"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), table_colors["header_text"]),
            ("FONTNAME", (0, 0), (-1, 0), header_font),
            # 使用GRID代替BOX，避免重复线条
            ("GRID", (0, 0), (-1, -1), 1, "#bdc3c7"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]
        # 只添加必要的样式，避免与TABLE_COMMON_STYLE冲突
        return TableStyle(style + HEADER_STYLE + [("WORDWRAP", (0, 0), (-1, -1), False)])

    def _prepare_export_data(self, data_source):
        """准备导出数据

        Args:
            data_source: 字典，包含导出数据的源信息

        Returns:
            tuple: (main_data, main_headers, remaining_data, remaining_headers)
        """
        main_data = []
        main_tree = data_source["main_tree"]
        main_filter = data_source.get("main_filter", None)
        main_headers = data_source.get("main_headers")

        if main_headers is None:
            main_headers = [main_tree.heading(col, "text") or "" for col in main_tree["columns"]]

        added_items = set()
        for item in main_tree.get_children():
            values = main_tree.item(item, "values")
            if main_filter:
                if main_filter(values):
                    if len(values) >= 2 and values[0] != "":
                        item_key = values[0]
                        if item_key not in added_items:
                            added_items.add(item_key)
                            main_data.append(values)
                    else:
                        main_data.append(values)
            elif values:
                if len(values) >= 2 and values[0] != "":
                    item_key = values[0]
                    if item_key not in added_items:
                        added_items.add(item_key)
                        main_data.append(values)
                else:
                    main_data.append(values)

        unique_main_data = []
        seen_rows = set()
        for row in main_data:
            row_tuple = tuple(row)
            if row_tuple not in seen_rows:
                seen_rows.add(row_tuple)
                unique_main_data.append(row)
        main_data = unique_main_data

        remaining_tree = data_source["remaining_tree"]
        remaining_headers = [remaining_tree.heading(col, "text") or "" for col in remaining_tree["columns"]]
        remaining_data = []
        for item in remaining_tree.get_children():
            values = remaining_tree.item(item, "values")
            if values:
                remaining_data.append(dict(zip(remaining_headers, values)))

        return main_data, main_headers, remaining_data, remaining_headers

    def _export_to_json(self, file_path, data_source, main_data, main_headers, remaining_data):
        """导出数据为JSON格式（UTF-8编码，不转义中文）"""
        if data_source["main_name"] == translate("split_segment_info"):
            export_data = {
                translate("split_segment_info"): dict(main_data), 
                translate("remaining_subnets"): remaining_data
            }
        else:
            export_data = {
                f"{data_source['main_name']}": [dict(zip(main_headers, item)) for item in main_data],
                
                translate("remaining_subnets"): remaining_data,
            }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def _export_to_txt(self, file_path, data_source, main_data, main_headers, remaining_data=None, remaining_headers=None):
        """导出数据为TXT格式（UTF-8编码）"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{data_source['main_name']}\n")
            f.write("=" * 80 + "\n")

            if self._is_k2v_headers(main_headers):
                # 计算项目名+冒号的最大宽度
                max_key_colon_width = 0
                for values in main_data:
                    if len(values) > 0:
                        key_colon_width = len(f"{str(values[0])}:")
                        if key_colon_width > max_key_colon_width:
                            max_key_colon_width = key_colon_width
                
                # 计算需要的Tab数量，确保所有值对齐在同一列（每个Tab对应8个字符宽度）
                tab_width = 8
                # 计算最大宽度需要的Tab数
                max_tabs = (max_key_colon_width + tab_width - 1) // tab_width
                
                # 特殊字段处理：需要少一个Tab的字段列表
                reduced_tab_fields = ["通配符掩码", "可用地址数"]
                
                for values in main_data:
                    key = str(values[0])
                    value = str(values[1])
                    key_colon = f"{key}:"
                    # 计算当前项目名+冒号需要的Tab数
                    current_tabs = (len(key_colon) + tab_width - 1) // tab_width
                    # 需要的额外Tab数 = 最大Tab数 - 当前Tab数 + 1（+1确保有足够的间距）
                    extra_tabs = max_tabs - current_tabs + 1
                    
                    # 特殊处理：通配符掩码和可用地址数少一个Tab
                    if key in reduced_tab_fields:
                        extra_tabs = max(1, extra_tabs - 1)  # 确保至少有一个Tab
                    
                    f.write(f"{key_colon}{'\t' * extra_tabs}{value}\n")
            else:
                # 计算每个列的最大宽度，使用自适应宽度
                max_widths = []
                # 先处理表头
                for i, header in enumerate(main_headers):
                    max_widths.append(len(str(header)) + 2)  # 表头宽度+2边距
                
                # 再处理数据行
                for values in main_data:
                    for i, value in enumerate(values):
                        if i < len(max_widths):
                            current_width = len(str(value)) + 2  # 数据宽度+2边距
                            if current_width > max_widths[i]:
                                max_widths[i] = current_width
                
                # 确保最小宽度为12
                max_widths = [max(w, 12) for w in max_widths]
                
                # 写入表头
                for i, header in enumerate(main_headers):
                    f.write(f"{header:<{max_widths[i]}}")
                f.write("\n")
                
                # 写入分隔线
                total_width = sum(max_widths)
                f.write("-" * total_width + "\n")
                
                # 写入数据行
                for values in main_data:
                    for i, value in enumerate(values):
                        if i < len(max_widths):
                            f.write(f"{str(value):<{max_widths[i]}}")
                    f.write("\n")

            f.write(f"\n\n{data_source['remaining_name']}\n")
            f.write("=" * 80 + "\n")

            if remaining_headers and remaining_data:
                # 使用传入的剩余数据表头和数据
                # 收集所有剩余数据行
                all_remaining_rows = []
                for item in remaining_data:
                    if isinstance(item, dict):
                        # 如果是字典，按照剩余表头的顺序提取值
                        values = [item.get(header, '') for header in remaining_headers]
                    else:
                        # 如果已经是列表，直接使用
                        values = item
                    all_remaining_rows.append(values)
                
                # 计算每个列的最大宽度，使用自适应宽度
                max_widths = []
                # 先处理表头
                for i, header in enumerate(remaining_headers):
                    max_widths.append(len(str(header)) + 2)  # 表头宽度+2边距
                
                # 再处理数据行
                for values in all_remaining_rows:
                    for i, value in enumerate(values):
                        if i < len(max_widths):
                            current_width = len(str(value)) + 2  # 数据宽度+2边距
                            if current_width > max_widths[i]:
                                max_widths[i] = current_width
                
                # 确保最小宽度为12
                max_widths = [max(w, 12) for w in max_widths]
                
                # 写入表头
                for i, header in enumerate(remaining_headers):
                    f.write(f"{header:<{max_widths[i]}}")
                f.write("\n")
                
                # 写入分隔线
                total_width = sum(max_widths)
                f.write("-" * total_width + "\n")
                
                # 写入数据行
                for values in all_remaining_rows:
                    for i, value in enumerate(values):
                        if i < len(max_widths):
                            f.write(f"{str(value):<{max_widths[i]}}")
                    f.write("\n")
            else:
                # 动态获取剩余数据的表头（备用方案）
                remaining_headers = [data_source["remaining_tree"].heading(col, "text") or ""
                                   for col in data_source["remaining_tree"]["columns"]]
                
                # 收集所有剩余数据行
                all_remaining_rows = []
                for item in data_source["remaining_tree"].get_children():
                    values = data_source["remaining_tree"].item(item, "values")
                    all_remaining_rows.append(values)
                
                # 计算每个列的最大宽度，使用自适应宽度
                max_widths = []
                # 先处理表头
                for i, header in enumerate(remaining_headers):
                    max_widths.append(len(str(header)) + 2)  # 表头宽度+2边距
                
                # 再处理数据行
                for values in all_remaining_rows:
                    for i, value in enumerate(values):
                        if i < len(max_widths):
                            current_width = len(str(value)) + 2  # 数据宽度+2边距
                            if current_width > max_widths[i]:
                                max_widths[i] = current_width
                
                # 确保最小宽度为12
                max_widths = [max(w, 12) for w in max_widths]
                
                # 写入表头
                for i, header in enumerate(remaining_headers):
                    f.write(f"{header:<{max_widths[i]}}")
                f.write("\n")
                
                # 写入分隔线
                total_width = sum(max_widths)
                f.write("-" * total_width + "\n")
                
                # 写入数据行
                for values in all_remaining_rows:
                    for i, value in enumerate(values):
                        if i < len(max_widths):
                            f.write(f"{str(value):<{max_widths[i]}}")
                    f.write("\n")

    def _export_to_csv(self, file_path, main_data, main_headers, remaining_tree, remaining_headers=None):
        """导出数据为CSV格式（UTF-8-BOM编码，Excel友好）
        
        Args:
            file_path: 文件路径
            main_data: 主数据
            main_headers: 主数据表头
            remaining_tree: 剩余数据的Treeview对象或MockTree对象
            remaining_headers: 剩余数据表头，如果为None则从tree中获取
        """
        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            writer.writerow(main_headers)
            for values in main_data:
                writer.writerow(values)

            writer.writerow([])

            # 使用传递进来的headers，或者从tree中获取
            if remaining_headers:
                writer.writerow(remaining_headers)
            else:
                remaining_headers = [remaining_tree.heading(col, "text") or "" for col in remaining_tree["columns"]]
                writer.writerow(remaining_headers)
            
            # 写入剩余数据
            for item in remaining_tree.get_children():
                values = remaining_tree.item(item, "values")
                writer.writerow(values)

    def _export_to_excel(self, file_path, data_source, main_data, main_headers, remaining_tree, remaining_headers):
        """导出数据为Excel格式（原生支持中文）"""
        wb = Workbook()

        main_sheet = wb.active
        # 根据数据类型设置不同的sheet名称
        if data_source["main_name"] == translate("split_segment_info"):
            # 子网切分结果
            main_sheet.title = translate("split_segment_info")
        else:
            # 子网规划结果
            main_sheet.title = translate("subnet_requirements")

        for col_idx, header in enumerate(main_headers, 1):
            cell = main_sheet.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        for row_idx, values in enumerate(main_data, 2):
            for col_idx, value in enumerate(values, 1):
                main_sheet.cell(row=row_idx, column=col_idx, value=value)

        remaining_sheet = wb.create_sheet(title=translate("remaining_subnets"))

        for col_idx, header in enumerate(remaining_headers, 1):
            cell = remaining_sheet.cell(row=1, column=col_idx, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        for row_idx, item in enumerate(remaining_tree.get_children(), 2):
            values = remaining_tree.item(item, "values")
            for col_idx, value in enumerate(values, 1):
                remaining_sheet.cell(row=row_idx, column=col_idx, value=value)

        wb.save(file_path)

    def _export_to_pdf(self, file_path, data_source, main_data, main_headers, _remaining_data, remaining_headers):
        """导出数据为PDF格式（支持中文）"""
        margins = (2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm)

        doc = BaseDocTemplate(
            file_path,
            pagesize=landscape(A4),
            leftMargin=margins[0],
            rightMargin=margins[1],
            topMargin=margins[2],
            bottomMargin=margins[3],
            showBoundary=False,
        )

        landscape_width, landscape_height = landscape(A4)
        portrait_width, portrait_height = A4
        
        # 根据当前语言获取日期格式
        def get_date_format():
            lang = get_language()
            if lang in ["zh", "zh_tw", "ja"]:
                return "%Y年%m月%d日 %H:%M:%S"
            else:  # 英文
                return "%Y-%m-%d %H:%M:%S"
        
        # 生成导出时间，用于页眉显示
        export_time = time.strftime(get_date_format())
        
        # 创建页眉回调函数
        def on_page(canvas, event):
            """页面回调函数，用于绘制页眉"""
            canvas.saveState()
            # 获取当前页面尺寸
            current_width, current_height = canvas._pagesize
            # 设置字体
            font_name = "ChineseFont" if self.has_chinese_font else "Helvetica"
            canvas.setFont(font_name, 10)
            canvas.setFillColor(colors.HexColor("#666666"))
            # 在页眉右侧绘制导出时间
            canvas.drawRightString(
                current_width - margins[1],  # x坐标：页面宽度 - 右边距
                current_height - 40,  # y坐标：页面顶部 - 20像素，留有适当边距
                f"{translate('export_time')}: {export_time}"
            )
            canvas.restoreState()
        
        landscape_frame = Frame(
            margins[0],
            margins[3],
            landscape_width - margins[0] - margins[1],
            landscape_height - margins[2] - margins[3],
            id='landscape_frame',
        )
        landscape_template = PageTemplate(id='landscape', frames=[landscape_frame], onPage=on_page)

        portrait_frame = Frame(
            margins[0],
            margins[3],
            portrait_width - margins[0] - margins[1],
            portrait_height - margins[2] - margins[3],
            id='portrait_frame',
        )
        portrait_template = PageTemplate(id='portrait', frames=[portrait_frame], pagesize=A4, onPage=on_page)

        doc.addPageTemplates([landscape_template, portrait_template])

        page_width = landscape_width
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ChineseTitle",
            parent=styles["Title"],
            fontName="ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor("#2c3e50"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        heading2_style = ParagraphStyle(
            "ChineseHeading2",
            parent=styles["Heading2"],
            fontName="ChineseFont" if self.has_chinese_font else "Helvetica-Bold",
            fontSize=16,
            textColor=colors.HexColor("#34495e"),
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=12,
        )

        normal_style = ParagraphStyle(
            "ChineseNormal",
            parent=styles["Normal"],
            fontName="ChineseFont" if self.has_chinese_font else "Helvetica",
            fontSize=11,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=5,
        )

        table_text_style = ParagraphStyle(
            "ChineseTableText",
            parent=styles["Normal"],
            fontName="ChineseFont" if self.has_chinese_font else "Helvetica",
            fontSize=10,
            alignment=TA_CENTER,
            wordWrap="None",  # 禁用自动换行
            leading=12,  # 设置行间距为12，确保垂直居中
            spaceBefore=0,
            spaceAfter=0,
        )

        elements.append(Paragraph(data_source["pdf_title"], title_style))
        elements.append(Spacer(1, 15))

        # 在切分段信息/已分配子网信息前添加父网段信息
        if data_source["main_name"] in [translate("split_segment_info"), translate("allocated_subnet_info")]:
            # 显示父网段信息
            elements.append(Paragraph(translate("parent_network_info"), heading2_style))
            
            # 从chart_data获取父网段信息
            chart_data = data_source.get("chart_data")
            if chart_data and "parent" in chart_data:
                parent_info = chart_data["parent"]
                
                # 获取完整的父网段信息
                from ip_subnet_calculator import get_subnet_info
                
                parent_cidr = parent_info.get("name", "")
                full_parent_info = get_subnet_info(parent_cidr)
                
                # 转置表格：将信息水平排列
                parent_table_data = []
                
                # 第一行：标题行
                parent_table_data.append([
                    Paragraph(translate("parent_cidr"), table_text_style),
                    Paragraph(translate("network_address"), table_text_style),
                    Paragraph(translate("subnet_mask"), table_text_style),
                    Paragraph(translate("broadcast_address"), table_text_style),
                    Paragraph(translate("prefix_length"), table_text_style),
                    Paragraph(translate("available_addresses"), table_text_style),
                    Paragraph(translate("host_address_range"), table_text_style)
                ])
                
                # 第二行：数据行
                parent_table_data.append([
                    Paragraph(full_parent_info.get("cidr", parent_cidr), table_text_style),
                    Paragraph(full_parent_info.get("network", ""), table_text_style),
                    Paragraph(full_parent_info.get("netmask", ""), table_text_style),
                    Paragraph(full_parent_info.get("broadcast", ""), table_text_style),
                    Paragraph(str(full_parent_info.get("prefixlen", "")), table_text_style),
                    Paragraph(f"{full_parent_info.get('usable_addresses', 0):,}", table_text_style),
                    Paragraph(f"{full_parent_info.get('host_range_start', '')} - {full_parent_info.get('host_range_end', '')}", table_text_style)
                ])
                
                # 创建父网段信息表格
                table_width = page_width - margins[0] - margins[1]
                
                # 使用自适应列宽
                num_cols = len(parent_table_data[0])
                # 获取自适应列宽
                col_widths = self._get_col_widths(parent_table_data, table_width, None, num_cols)
                
                # 确保所有列宽都是有效的数字
                valid_col_widths = []
                for width in col_widths:
                    if width is None or not isinstance(width, (int, float)) or width <= 0:
                        valid_col_widths.append(table_width / num_cols)
                    else:
                        valid_col_widths.append(width)
                
                # 确保表格数据有效
                valid_table_data = []
                for row in parent_table_data:
                    valid_row = []
                    for cell in row:
                        if cell is None:
                            valid_row.append(Paragraph("", table_text_style))
                        else:
                            valid_row.append(cell)
                    valid_table_data.append(valid_row)
                
                # 创建表格时直接传递列宽
                parent_table = Table(valid_table_data, colWidths=valid_col_widths, repeatRows=1)
                # 应用样式
                parent_table.setStyle(self._get_table_style(MAIN_TABLE_COLORS, self.has_chinese_font))
                elements.append(parent_table)
                elements.append(Spacer(1, 20))
        
        # 显示切分段信息或已分配子网信息
        main_heading = Paragraph(data_source["main_name"], heading2_style)
        # 准备KeepTogether的内容列表
        keep_together_main = [main_heading]

        # 特殊处理：子网切分PDF的切分段信息表格
        if data_source["main_name"] == translate("split_segment_info"):
            # 转置表格并移除指定列
            # 定义要移除的列名
            columns_to_remove = [translate("parent_network"), translate("split_line"), translate("prefix_length"), translate("cidr"), translate("separator"), translate("network_address")]
            
            # 键值对格式处理
            filtered_data = {}
            for values in main_data:
                key = str(values[0]) if values[0] is not None else ""
                value = str(values[1]) if values[1] is not None else ""
                # 只保留非空键和不需要移除的键，同时移除虚线列
                if key and key not in columns_to_remove and not all(c == '-' for c in key):
                    filtered_data[key] = value
            
            # 转置：将键作为表头，值作为一行
            if filtered_data:
                # 创建表头行
                headers = list(filtered_data.keys())
                main_table_data = [[Paragraph(h, table_text_style) for h in headers]]
                # 创建数据行
                values = [filtered_data[h] for h in headers]
                main_table_data.append([Paragraph(str(v), table_text_style) for v in values])
            else:
                main_table_data = []
        elif self._is_k2v_headers(main_headers):
            main_table_data = [[Paragraph("项目", table_text_style), Paragraph("值", table_text_style)]]
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
            table_width = page_width - margins[0] - margins[1]
            table_cols = len(main_table_data[0])

            col_widths = data_source.get("main_table_cols")
            if isinstance(col_widths, str):
                try:
                    col_ratios = [float(w) for w in col_widths.split(":")]
                    if all(ratio < 10 for ratio in col_ratios):
                        total_ratio = sum(col_ratios)
                        col_widths = [table_width * (ratio / total_ratio) for ratio in col_ratios] if total_ratio > 0 else None
                    else:
                        col_widths = col_ratios
                except (ValueError, TypeError):
                    col_widths = None

            valid_col_widths = self._get_col_widths(main_table_data, table_width, col_widths, table_cols)

            # 动态调整表格单元格的字体大小
            adjusted_table_data = []
            for row_idx, row in enumerate(main_table_data):
                adjusted_row = []
                for col_idx, cell in enumerate(row):
                    # 获取当前单元格的文本内容
                    if hasattr(cell, 'getPlainText'):
                        text = cell.getPlainText()
                    elif hasattr(cell, 'text'):
                        text = cell.text
                    else:
                        text = str(cell)

                    # 计算文本宽度
                    text_width = 0
                    for char in text:
                        if ord(char) > 127:
                            text_width += 10
                        else:
                            text_width += 5
                    text_width += 8

                    # 初始字号
                    font_size = 10
                    if row_idx == 0:  # 表头使用稍大的字号
                        font_size = 11
                    min_font_size = 8

                    # 根据列宽调整字号，确保内容不换行
                    column_width = valid_col_widths[col_idx]
                    # 使用更严格的判断条件，确保内容能够完全容纳
                    if text_width > column_width * 0.9:  # 当文本宽度超过列宽的90%时，就缩小字号
                        # 计算合适的字号，确保内容能够完全显示
                        scale_factor = (column_width * 0.95) / text_width
                        # 应用缩放因子，确保字号足够小以容纳内容
                        font_size = font_size * scale_factor
                        # 确保不小于最小字号
                        font_size = max(font_size, min_font_size)

                    # 创建自定义的ParagraphStyle，包含动态计算的字体大小和禁用自动换行
                    custom_style = ParagraphStyle(
                        f"CustomStyle_{row_idx}_{col_idx}",
                        parent=table_text_style,
                        fontSize=font_size,
                        wordWrap="None"  # 明确禁用自动换行
                    )

                    # 使用自定义样式创建新的Paragraph对象
                    if hasattr(cell, 'getPlainText'):
                        adjusted_cell = Paragraph(text, custom_style)
                    else:
                        adjusted_cell = Paragraph(str(cell), custom_style)
                    
                    adjusted_row.append(adjusted_cell)
                adjusted_table_data.append(adjusted_row)

            main_table = Table(adjusted_table_data, colWidths=valid_col_widths, repeatRows=1)
            main_table.setStyle(self._get_table_style(MAIN_TABLE_COLORS, self.has_chinese_font))
            keep_together_main.append(main_table)
        else:
            keep_together_main.append(Paragraph(f"{translate('no')}{data_source['main_name']}", normal_style))
        
        # 将标题和表格包装在KeepTogether中
        elements.append(KeepTogether(keep_together_main))
        elements.append(Spacer(1, 20))

        # 显示剩余网段信息
        remaining_heading = Paragraph(data_source["remaining_name"], heading2_style)
        # 准备KeepTogether的内容列表
        keep_together_remaining = [remaining_heading]
        remaining_table_data = [[Paragraph(h, table_text_style) for h in remaining_headers]]
        for item in data_source["remaining_tree"].get_children():
            values = data_source["remaining_tree"].item(item, "values")
            if values:
                remaining_table_data.append(
                    [Paragraph(str(v) if v is not None else "", table_text_style) for v in values]
                )

        if len(remaining_table_data) > 1:
            table_width = page_width - margins[0] - margins[1]
            table_cols = len(remaining_table_data[0])

            col_widths = data_source.get("remaining_table_cols")
            if isinstance(col_widths, str):
                try:
                    col_ratios = [float(w) for w in col_widths.split(":")]
                    if all(ratio < 10 for ratio in col_ratios):
                        total_ratio = sum(col_ratios)
                        col_widths = [table_width * (ratio / total_ratio) for ratio in col_ratios] if total_ratio > 0 else None
                    else:
                        col_widths = col_ratios
                except (ValueError, TypeError):
                    col_widths = None

            valid_col_widths = self._get_col_widths(remaining_table_data, table_width, col_widths, table_cols)

            # 动态调整剩余网段表格单元格的字体大小
            adjusted_remaining_data = []
            for row_idx, row in enumerate(remaining_table_data):
                adjusted_row = []
                for col_idx, cell in enumerate(row):
                    # 获取当前单元格的文本内容
                    if hasattr(cell, 'getPlainText'):
                        text = cell.getPlainText()
                    elif hasattr(cell, 'text'):
                        text = cell.text
                    else:
                        text = str(cell)

                    # 计算文本宽度
                    text_width = 0
                    for char in text:
                        if ord(char) > 127:
                            text_width += 10
                        else:
                            text_width += 5
                    text_width += 8

                    # 初始字号
                    font_size = 10
                    if row_idx == 0:  # 表头使用稍大的字号
                        font_size = 11
                    min_font_size = 8

                    # 根据列宽调整字号，确保内容不换行
                    column_width = valid_col_widths[col_idx]
                    # 使用更严格的判断条件，确保内容能够完全容纳
                    if text_width > column_width * 0.9:  # 当文本宽度超过列宽的90%时，就缩小字号
                        # 计算合适的字号，确保内容能够完全显示
                        scale_factor = (column_width * 0.95) / text_width
                        # 应用缩放因子，确保字号足够小以容纳内容
                        font_size = font_size * scale_factor
                        # 确保不小于最小字号
                        font_size = max(font_size, min_font_size)

                    # 创建自定义的ParagraphStyle，包含动态计算的字体大小和禁用自动换行
                    custom_style = ParagraphStyle(
                        f"CustomRemainingStyle_{row_idx}_{col_idx}",
                        parent=table_text_style,
                        fontSize=font_size,
                        wordWrap="None"  # 明确禁用自动换行
                    )

                    # 使用自定义样式创建新的Paragraph对象
                    if hasattr(cell, 'getPlainText'):
                        adjusted_cell = Paragraph(text, custom_style)
                    else:
                        adjusted_cell = Paragraph(str(cell), custom_style)
                    
                    adjusted_row.append(adjusted_cell)
                adjusted_remaining_data.append(adjusted_row)

            remaining_table = Table(adjusted_remaining_data, colWidths=valid_col_widths, repeatRows=1)
            remaining_table.setStyle(self._get_table_style(REMAINING_TABLE_COLORS, self.has_chinese_font))
            keep_together_remaining.append(remaining_table)
        else:
            keep_together_remaining.append(Paragraph(f"{translate('no')}{data_source['remaining_name']}", normal_style))
        
        # 将标题和表格包装在KeepTogether中
        elements.append(KeepTogether(keep_together_remaining))

        # 添加网段分布图（对子网切分和子网规划功能，放在剩余网段表之后）
        chart_data = data_source.get("chart_data")
        # 检查chart_data是否存在，而不依赖于硬编码的中文文本
        if chart_data:
            try:
                print("开始添加网段分布图到PDF...")
                self._add_chart_to_pdf(elements, chart_data, margins, portrait_width, portrait_height)
            except (IOError, ValueError, TypeError, AttributeError) as e:
                print(f"添加网段分布图失败: {e}")
                traceback.print_exc()

        doc.build(elements)

    def _load_system_font(self, font_size=36, bold_offset=4, verbose=False):
        """加载系统中文字体

        Args:
            font_size: 字体大小
            bold_offset: 粗体字体大小偏移量
            verbose: 是否打印详细信息

        Returns:
            tuple: (font, bold_font, font_loaded)
        """
        font = None
        bold_font = None
        font_loaded = False
        try:
            system_font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
            font_candidates = [
                ('msyh.ttc', font_size, '微软雅黑'),
                ('simhei.ttf', font_size, '黑体'),
                ('simsun.ttc', font_size - 2, '宋体'),
                ('simkai.ttf', font_size - 2, '楷体'),
            ]

            for font_file, size, font_name in font_candidates:
                font_path = os.path.join(system_font_dir, font_file)
                if os.path.exists(font_path):
                    try:
                        font = ImageFont.truetype(font_path, size)
                        bold_font = ImageFont.truetype(font_path, size + bold_offset)
                        font_loaded = True
                        if verbose:
                            print(f"成功加载{font_name}字体: {font_path}")
                        break
                    except (FileNotFoundError, IOError, OSError, ValueError, TypeError) as e:
                        if verbose:
                            print(f"尝试加载{font_name}失败: {e}")
                        continue

            if not font_loaded:
                font = ImageFont.load_default()
                bold_font = ImageFont.load_default()
                if verbose:
                    print("使用默认字体")
        except (IOError, OSError, ValueError, TypeError) as e:
            if verbose:
                print(f"加载中文字体失败: {e}")
            font = ImageFont.load_default()
            bold_font = ImageFont.load_default()
        return font, bold_font, font_loaded

    def _calculate_chart_dimensions(self, networks):
        """计算图表所需的尺寸

        Args:
            networks: 网段列表

        Returns:
            tuple: (segment_height, required_height)
        """
        split_networks = [net for net in networks if net.get("type") == "split"]
        remaining_networks = [net for net in networks if net.get("type") != "split"]
        total_networks = len(split_networks) + len(remaining_networks)

        segment_height = 100 + 34
        # 动态计算基础高度和所需总高度
        base_height = 280 + 100 + 100 + 150 + 300
        required_height = base_height + total_networks * segment_height
        return segment_height, required_height

    def _draw_title(self, draw, high_res_width, title=None):
        """绘制图表标题

        Args:
            draw: ImageDraw对象
            high_res_width: 图像宽度
            title: 标题文字，默认使用国际化的"distribution_chart"

        Returns:
            tuple: (title_font, title_x, title_y)
        """
        title_font_size = 76
        # 正确获取字体对象
        _, bold_font, _ = self._load_system_font(title_font_size, verbose=False)
        title_font = bold_font

        # 使用国际化标题，如果没有提供则使用默认翻译
        if not title:
            title = translate("distribution_chart")

        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = (high_res_width - (title_bbox[2] - title_bbox[0])) // 2
        title_y = 100
        return title_font, title_x, title_y

    def _add_chart_to_pdf(self, elements, chart_data, margins, portrait_width, portrait_height):
        """添加网段分布图到PDF元素列表

        Args:
            elements: PDF元素列表
            chart_data: 网段分布图数据
            margins: 页面边距
            portrait_width: 纵向页面宽度
            portrait_height: 纵向页面高度
            main_name: 主数据名称，用于区分子网切分和子网规划
        """
        # 导入翻译函数，避免与局部变量冲突
        from i18n import _ as translate  # _ 是翻译函数，这里重命名为 translate 以避免冲突
        
        if not chart_data or 'networks' not in chart_data or len(chart_data['networks']) == 0:
            print("没有有效的网段分布图数据，跳过")
            return

        print(f"检测到有效网段分布图数据，包含 {len(chart_data['networks'])} 个网段")

        # 切换到纵向页面模板
        elements.append(NextPageTemplate('portrait'))
        elements.append(PageBreak())

        # 准备图表数据
        parent_info = chart_data.get("parent", {})
        parent_cidr = parent_info.get("name", translate("parent_network"))
        parent_range = parent_info.get("range", 1)
        networks = chart_data.get("networks", [])

        # 直接从chart_data中获取chart_type，如果没有则根据数据结构自动判断
        chart_type = chart_data.get("type", "split")
        
        # 计算切分段和剩余网段
        split_networks = [net for net in networks if net.get("type") == "split"]
        remaining_networks = [net for net in networks if net.get("type") != "split"]
        
        # 精确计算图表所需的总高度
        # 基本元素高度
        title_height = 280  # 标题部分高度
        parent_network_height = 150  # 父网段部分高度
        legend_height = 150  # 图例部分高度（减小，因为图例实际不需要那么高）
        
        # 网段列表高度
        segment_height = 134  # 每个网段行的高度（100高度 + 34间距）
        
        # 需求网段/切分段标题高度
        demand_title_height = 180 if chart_type == "plan" else 0  # 需求网段标题高度
        
        # 分隔线高度
        separator_height = 100  # 分隔线和间距高度
        
        # 剩余网段标题高度
        remaining_title_height = 180  # 剩余网段标题高度
        
        # 精确计算所需总高度
        required_height = (title_height
                          + parent_network_height
                          + separator_height
                          + demand_title_height
                          + len(split_networks) * segment_height
                          + separator_height
                          + remaining_title_height
                          + len(remaining_networks) * segment_height
                          + legend_height
                          + 50)  # 减小额外的安全间距到50

        # 创建高分辨率图像
        high_res_width = 2480
        high_res_height = max(3508, required_height)

        pil_image = Image.new('RGB', (high_res_width, high_res_height), color='#333333')
        draw = ImageDraw.Draw(pil_image)

        # 加载中文字体
        font, bold_font, _ = self._load_system_font(font_size=36, verbose=True)

        # 设置图表参数
        margin_left = 180
        margin_right = 150
        margin_top = 280
        chart_width = high_res_width - margin_left - margin_right
        chart_x = margin_left
        chart_right = chart_x + chart_width  # 计算图表右边缘位置
        ADDRESS_OFFSET = 50  # 地址文本距离图表右边缘的偏移量（左缩进）

        # 定义绘制带描边文字的辅助函数
        def draw_text_with_stroke(draw_obj, position, text, font, fill, stroke_color="#666666", stroke_width=4):
            """绘制带描边的文字

            Args:
                draw_obj: ImageDraw对象
                position: (x, y) 坐标
                text: 要绘制的文字
                font: 字体对象
                fill: 文字颜色
                stroke_color: 描边颜色
                stroke_width: 描边宽度
            """
            # 使用PIL的描边参数绘制文字
            try:
                draw_obj.text(
                    position,
                    text,
                    font=font,
                    fill=fill,
                    stroke_width=stroke_width,
                    stroke_fill=stroke_color
                )
            except (TypeError, AttributeError):
                # 如果PIL版本不支持描边参数，使用方向性格式
                x, y = position
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dx, dy in directions:
                    draw_obj.text((x + dx, y + dy), text, font=font, fill=stroke_color)
                draw_obj.text((x, y), text, font=font, fill=fill)

        # 使用对数比例尺
        log_max = math.log10(parent_range)
        log_min = 3

        min_bar_width = 120
        padding = 34
        bar_height = 100
        
        # 为所有网段分配颜色
        subnet_colors = [
            "#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8",
            "#5b8fd9", "#3c70d8", "#e68838", "#a04132",
            "#6a9da8", "#87c569", "#6d8de8", "#c16fa0",
            "#a99bc6", "#a44d69", "#b9d0f8", "#5d4ea5",
            "#f5ad8c", "#5b8fd9", "#db6679", "#a6c589",
        ]

        # 绘制标题
        title_font, title_x, title_y = self._draw_title(draw, high_res_width)
        draw_text_with_stroke(draw, (title_x, title_y), translate("distribution_chart"), title_font, "#ffffff")

        y = margin_top

        # 绘制父网段
        log_value = max(log_min, math.log10(parent_range))
        bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
        parent_color = "#636e72"
        draw.rectangle([chart_x, y, chart_x
            + bar_width, y
            + bar_height], fill=parent_color, outline=None, width=0)

        usable_addresses = parent_range - 2 if parent_range > 2 else parent_range
        segment_text = f"{translate('parent_network')}: {parent_cidr}"
        address_text = f"{translate('usable_addresses')}: {usable_addresses:,}"

        text_font_size = 50
        text_font = None
        bold_text_font = None
        try:
            system_font_dir = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')
            text_font_path = os.path.join(system_font_dir, 'msyh.ttc')
            if os.path.exists(text_font_path):
                text_font = ImageFont.truetype(text_font_path, text_font_size)
                bold_text_font = ImageFont.truetype(text_font_path, text_font_size + 6)
            else:
                text_font = font
                bold_text_font = bold_font
        except (IOError, OSError, ValueError, TypeError):
            text_font = font
            bold_text_font = bold_font

        def get_centered_y(box_y, box_height, _, _font):
            text_y = box_y + box_height // 2 - 38
            return text_y

        segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
        segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
        address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
        address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)
        
        # 计算地址文本的右对齐位置：图表右边缘 - 左偏移 - 文本宽度
        address_width = address_bbox[2] - address_bbox[0]
        address_x = chart_right - ADDRESS_OFFSET - address_width

        draw_text_with_stroke(draw, (chart_x
            + 30, segment_text_y), segment_text, bold_text_font, "#ffffff")
        draw_text_with_stroke(draw, (address_x, address_text_y), address_text, bold_text_font, "#ffffff")

        y += bar_height + padding

        # 在父网段和需求/切分网段之间添加分割线（仅子网规划显示）
        if chart_type == "plan":
            draw.line([chart_x, y + 20, chart_x + chart_width, y + 20], fill="#cccccc", width=4)
            y += 60  # 增大间距，让需求网段与上部分割线的距离和剩余网段保持一致
        else:
            y += 0  # 子网切分保持较小间距
        
        # 绘制需求网段标题
        if chart_type == "plan":
            demand_count = len(split_networks)
            title_text = f"{translate('allocated_subnets')} ({demand_count} {translate('pieces')}):"
            title_bbox = draw.textbbox((0, 0), title_text, font=bold_text_font)
            title_text_y = get_centered_y(y, bar_height, title_bbox, bold_text_font)
            draw_text_with_stroke(draw, (chart_x, title_text_y), title_text, bold_text_font, "#ffffff")
            y += 100
        
        # 绘制切分/需求网段
        for i, network in enumerate(split_networks):
            network_range = network.get("range", 1)
            log_value = max(log_min, math.log10(network_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
            
            if chart_type == "split":
                # 子网切分
                split_color = "#4a7eb4"
                name = network.get("name", "")
                segment_text = f"{translate('split_segment')}: {name}"
            else:
                # 子网规划 - 使用多彩样式
                color_index = i % len(subnet_colors)
                split_color = subnet_colors[color_index]
                name = network.get("name", "")
                cidr = network.get("cidr", "")
                segment_text = f"{translate('segment')} {i + 1}: {name}    {cidr}"
            
            draw.rectangle([chart_x, y, chart_x
                + bar_width, y
                + bar_height], fill=split_color, outline=None, width=0)

            usable_addresses = network_range - 2 if network_range > 2 else network_range
            address_text = f"{translate("usable_addresses")}: {usable_addresses:,}"

            segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
            segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
            address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
            address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)
            
            # 计算地址文本的右对齐位置：图表右边缘 - 左偏移 - 文本宽度
            address_width = address_bbox[2] - address_bbox[0]
            address_x = chart_right - ADDRESS_OFFSET - address_width

            draw_text_with_stroke(draw, (chart_x
                + 30, segment_text_y), segment_text, bold_text_font, "#ffffff")
            draw_text_with_stroke(draw, (address_x, address_text_y), address_text, bold_text_font, "#ffffff")

            y += bar_height + padding

        # 在需求/切分网段和剩余网段之间添加分割线
        draw.line([chart_x, y + 20, chart_x + chart_width, y + 20], fill="#cccccc", width=4)

        # 绘制剩余网段标题
        y += 80
        remaining_count = len(remaining_networks)
        title_text = f"{translate('remaining_subnets')} ({remaining_count} {translate('pieces')}):"

        title_bbox = draw.textbbox((0, 0), title_text, font=bold_text_font)
        title_text_y = get_centered_y(y, bar_height, title_bbox, bold_text_font)
        draw_text_with_stroke(draw, (chart_x, title_text_y), title_text, bold_text_font, "#ffffff")
        y += 100

        # 绘制剩余网段
        for i, network in enumerate(remaining_networks):
            network_range = network.get("range", 1)
            log_value = max(log_min, math.log10(network_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
            color_index = i % len(subnet_colors)
            color = subnet_colors[color_index]
            draw.rectangle([chart_x, y, chart_x
                + bar_width, y
                + bar_height], fill=color, outline=None, width=0)

            name = network.get("name", "")
            usable_addresses = network_range - 2 if network_range > 2 else network_range
            
            if chart_type == "split":
                segment_text = f"{translate('segment')} {i + 1}: {name}"
            else:
                segment_text = f"{translate('segment')} {i + 1}: {name}"
                
            address_text = f"{translate("usable_addresses")}: {usable_addresses:,}"

            segment_bbox = draw.textbbox((0, 0), segment_text, font=text_font)
            segment_text_y = get_centered_y(y, bar_height, segment_bbox, text_font)
            address_bbox = draw.textbbox((0, 0), address_text, font=text_font)
            address_text_y = get_centered_y(y, bar_height, address_bbox, text_font)
            
            # 计算地址文本的右对齐位置：图表右边缘 - 左偏移 - 文本宽度
            address_width = address_bbox[2] - address_bbox[0]
            address_x = chart_right - ADDRESS_OFFSET - address_width

            draw_text_with_stroke(draw, (chart_x
                + 30, segment_text_y), segment_text, text_font, "#ffffff")
            draw_text_with_stroke(draw, (address_x, address_text_y), address_text, text_font, "#ffffff")

            y += bar_height + padding

        # 绘制图例
        y += 80
        legend_title = f"{translate('legend')}:"
        legend_title_bbox = draw.textbbox((0, 0), legend_title, font=bold_text_font)
        legend_title_y = y + (bar_height - (legend_title_bbox[3] - legend_title_bbox[1])) // 2
        draw_text_with_stroke(draw, (chart_x, legend_title_y), legend_title, bold_text_font, "#ffffff")
        y += 100

        legend_y = y
        legend_item_height = 60
        legend_container_y = legend_y
        legend_container_height = legend_item_height

        def get_centered_text_y(container_y, container_height, text_bbox):
            text_height = text_bbox[3] - text_bbox[1]
            container_center = container_y + container_height // 2
            text_y = container_center - text_height // 2 - int(text_height * 0.30)
            return text_y

        # 父网段图例
        parent_x = chart_x
        parent_color = "#636e72"
        parent_label = translate("parent_network")
        parent_block_size = 40
        parent_text_font = text_font
        parent_label_bbox = draw.textbbox((0, 0), parent_label, font=parent_text_font)

        parent_block_y = legend_container_y + (legend_container_height - parent_block_size) // 2
        parent_label_y = get_centered_text_y(legend_container_y, legend_container_height, parent_label_bbox)

        draw.rectangle([parent_x, parent_block_y, parent_x + parent_block_size, parent_block_y + parent_block_size],
                      fill=parent_color, outline=None, width=0)
        draw_text_with_stroke(draw, (parent_x
            + parent_block_size
            + 25, parent_label_y), parent_label, parent_text_font, "#ffffff")

        # 切分/需求网段图例 - 动态计算位置，增加间距
        # 先计算父网段图例的总宽度
        parent_label_width = parent_label_bbox[2] - parent_label_bbox[0]
        split_x = parent_x + parent_block_size + 25 + parent_label_width + 80  # 增加间距到80
        split_text_font = text_font
        
        if chart_type == "split":
            # 子网切分 - 单一颜色
            split_color = "#4a7eb4"
            split_label = translate("split_segment")
            split_block_size = 40
            
            split_block_y = legend_container_y + (legend_container_height - split_block_size) // 2
            split_label_bbox = draw.textbbox((0, 0), split_label, font=split_text_font)
            split_label_y = get_centered_text_y(legend_container_y, legend_container_height, split_label_bbox)
            
            draw.rectangle([split_x, split_block_y, split_x + split_block_size, split_block_y + split_block_size],
                          fill=split_color, outline=None, width=0)
            draw_text_with_stroke(draw, (split_x + split_block_size + 15, split_label_y), split_label, split_text_font, "#ffffff")
        else:
            # 子网规划 - 多彩样式
            split_label = f"{translate('allocated_subnets')}"
            legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
            split_block_size = 30
            split_block_gap = 15  # 减小颜色块之间的间距
            
            split_block_y = legend_container_y + (legend_container_height - split_block_size) // 2
            split_label_bbox = draw.textbbox((0, 0), split_label, font=split_text_font)
            split_label_y = get_centered_text_y(legend_container_y, legend_container_height, split_label_bbox)
            
            # 绘制多彩图例块
            for j, color in enumerate(legend_colors):
                draw.rectangle(
                    [split_x + j * (split_block_size + split_block_gap), split_block_y,
                     split_x + j * (split_block_size + split_block_gap) + split_block_size,
                     split_block_y + split_block_size],
                    fill=color, outline=None, width=0
                )
            
            draw_text_with_stroke(draw,
                (split_x + len(legend_colors) * (split_block_size + split_block_gap) + 15, split_label_y),
                split_label, text_font, "#ffffff"
            )

        # 剩余网段图例 - 动态计算位置，增加间距
        # 计算切分/需求网段图例的总宽度
        if chart_type == "split":
            split_label_text = translate("split_segment")
            split_label_width = draw.textbbox((0, 0), split_label_text, font=split_text_font)[2] - draw.textbbox((0, 0), split_label_text, font=split_text_font)[0]
            remaining_x = split_x + split_block_size + 15 + split_label_width + 80  # 增加间距到80
        else:
            split_label_text = f"{translate('allocated_subnets')}"
            split_label_width = draw.textbbox((0, 0), split_label_text, font=split_text_font)[2] - draw.textbbox((0, 0), split_label_text, font=split_text_font)[0]
            remaining_x = split_x + len(legend_colors) * (split_block_size + split_block_gap) + 15 + split_label_width + 80  # 增加间距到80
        remaining_label = f"{translate('remaining_subnets')}"
        legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
        remaining_block_size = 30
        remaining_block_gap = 15  # 减小颜色块之间的间距
        remaining_text_font = text_font
        remaining_label_bbox = draw.textbbox((0, 0), remaining_label, font=remaining_text_font)

        remaining_block_y = legend_container_y + (legend_container_height - remaining_block_size) // 2
        remaining_label_y = get_centered_text_y(legend_container_y, legend_container_height, remaining_label_bbox)

        for j, color in enumerate(legend_colors):
            draw.rectangle(
                [remaining_x + j * (remaining_block_size + remaining_block_gap), remaining_block_y,
                 remaining_x + j * (remaining_block_size + remaining_block_gap) + remaining_block_size,
                 remaining_block_y + remaining_block_size],
                fill=color, outline=None, width=0
            )

        draw_text_with_stroke(draw,
            (remaining_x + len(legend_colors) * (remaining_block_size + remaining_block_gap) + 15, remaining_label_y),
            remaining_label, text_font, "#ffffff"
        )

        print("成功创建网段分布图")

        # 保存图像为高DPI PNG
        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format='PNG', dpi=(300, 300))
        img_byte_arr.seek(0)
        print(f"成功保存高DPI PNG图像，尺寸: {pil_image.size}, DPI: 300")

        # 计算图像在PDF中的尺寸
        actual_image_height = high_res_height
        image_ratio = high_res_width / actual_image_height

        available_width = portrait_width - margins[0] - margins[1] - 20
        
        # 不固定高度，而是根据图像比例和可用宽度计算合适的高度
        # 先根据可用宽度计算理论高度
        final_pdf_width = available_width
        final_pdf_height = final_pdf_width / image_ratio
        
        # 确保高度不会超过页面的可用高度
        max_available_height = portrait_height - margins[2] - margins[3] - 20
        if final_pdf_height > max_available_height:
            final_pdf_height = max_available_height
            final_pdf_width = final_pdf_height * image_ratio

        # 添加图像到PDF
        elements.append(RLImage(img_byte_arr, width=final_pdf_width, height=final_pdf_height))

        # 切换回横向页面模板
        elements.append(NextPageTemplate('landscape'))
        elements.append(PageBreak())

        print("网段分布图成功添加到PDF")

    def export_data(self, data_source, _title, _success_msg, failure_msg):
        """通用数据导出函数

        Args:
            data_source: 字典，包含导出数据的源信息
            title: 文件对话框标题
            success_msg: 成功消息格式字符串
            failure_msg: 失败消息格式字符串

        Returns:
            tuple: (success: bool, message: str, file_path: str or None)
        """
        try:
            main_data, main_headers, remaining_data, remaining_headers = self._prepare_export_data(data_source)

            is_valid = True
            error_msg = ""

            if data_source["main_name"] == "切分段信息":
                if not main_data:
                    is_valid = False
                    error_msg = "未找到切分数据，请先执行子网切分！"
            elif data_source["main_name"] == "已分配子网信息":
                if not main_data:
                    is_valid = False
                    error_msg = "未找到规划数据，请先执行子网规划！"

            if not is_valid:
                return False, error_msg, None

            return True, "data_prepared", (main_data, main_headers, remaining_data, remaining_headers)

        except (ValueError, TypeError, KeyError) as e:
            traceback.print_exc()
            return False, f"{failure_msg}: {str(e)}", None

    def export_to_file(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        """将数据导出到指定文件

        Args:
            file_path: 文件路径
            data_source: 数据源字典
            main_data: 主数据
            main_headers: 主数据表头
            remaining_data: 剩余数据
            remaining_headers: 剩余数据表头

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # 根据文件扩展名选择相应的导出方法
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".json":
                self._export_to_json(file_path, data_source, main_data, main_headers, remaining_data)
            elif file_ext == ".txt":
                self._export_to_txt(file_path, data_source, main_data, main_headers, remaining_data, remaining_headers)
            elif file_ext == ".csv":
                # 对于CSV导出，需要创建一个模拟的tree对象
                class MockTree:
                    """模拟Treeview对象，用于CSV导出"""
                    def __init__(self, headers, data):
                        self.headers = headers
                        self.data = data
                        self.columns = list(range(len(headers)))
                    
                    def heading(self, col, event):
                        """获取列标题
                        
                        Args:
                            col: 列索引或列名
                            option: 选项名，通常是"text"
                        
                        Returns:
                            列标题字符串
                        """
                        if isinstance(col, str) and col.isdigit():
                            col = int(col)
                        return self.headers[col] if isinstance(col, int) and 0 <= col < len(self.headers) else ""
                    
                    def get_children(self):
                        """获取所有子项的ID列表"""
                        return range(len(self.data))
                    
                    def item(self, item, option=None):
                        """获取项目的属性
                        
                        Args:
                            item: 项目ID
                            option: 选项名，如果为None则返回所有选项的字典
                        
                        Returns:
                            如果option为None则返回字典，否则返回对应选项的值
                        """
                        values = self.data[item] if item < len(self.data) else []
                        if option is None:
                            return {"values": values}
                        elif option == "values":
                            return values
                        else:
                            return None
                    
                    def __getitem__(self, key):
                        """支持字典访问方式"""
                        if key == "columns":
                            return self.columns
                        raise KeyError(key)
                
                # 将字典列表转换为列表列表，以便 MockTree 正确处理
                remaining_data_list = []
                for item in remaining_data:
                    if isinstance(item, dict):
                        # 按照剩余表头的顺序提取值
                        row = [item.get(header, '') for header in remaining_headers]
                        remaining_data_list.append(row)
                    else:
                        # 如果已经是列表，直接添加
                        remaining_data_list.append(item)
                
                mock_tree = MockTree(remaining_headers, remaining_data_list)
                self._export_to_csv(file_path, main_data, main_headers, mock_tree, remaining_headers)
            elif file_ext == ".xlsx":
                # 对于Excel导出，需要创建一个模拟的tree对象
                class MockTree:
                    """模拟Treeview对象，用于Excel导出"""
                    def __init__(self, headers, data):
                        self.headers = headers
                        self.data = data
                        self.columns = list(range(len(headers)))
                    
                    def heading(self, col, _):
                        return self.headers[col]
                    
                    def get_children(self):
                        return range(len(self.data))
                    
                    def item(self, item, option=None):
                        values = self.data[item] if item < len(self.data) else []
                        if option is None:
                            return {"values": values}
                        elif option == "values":
                            return values
                        else:
                            return None
                    
                    def __getitem__(self, key):
                        """支持字典访问方式"""
                        if key == "columns":
                            return self.columns
                        raise KeyError(key)
                
                # 将字典列表转换为列表列表，以便 MockTree 正确处理
                remaining_data_list = []
                for item in remaining_data:
                    if isinstance(item, dict):
                        # 按照剩余表头的顺序提取值
                        row = [item.get(header, '') for header in remaining_headers]
                        remaining_data_list.append(row)
                    else:
                        # 如果已经是列表，直接添加
                        remaining_data_list.append(item)
                
                mock_tree = MockTree(remaining_headers, remaining_data_list)
                self._export_to_excel(file_path, data_source, main_data, main_headers, mock_tree, remaining_headers)
            elif file_ext == ".pdf":
                self._export_to_pdf(file_path, data_source, main_data, main_headers, remaining_data, remaining_headers)
            else:
                return False, f"不支持的文件格式: {file_ext}"

            return True, f"成功导出到: {file_path}"
        except PermissionError as e:
            return False, f"导出失败: 没有写入权限，请检查文件是否被占用或目录权限是否正确: {e}"
        except FileNotFoundError as e:
            return False, f"导出失败: 文件路径不存在: {e}"
        except (IOError, OSError) as e:
            return False, f"导出失败: IO错误: {e}"
        except ValueError as e:
            return False, f"导出失败: 数据格式错误: {e}"
        except TypeError as e:
            return False, f"导出失败: 类型错误: {e}"
        except Exception as e:
            print(f"导出过程中发生意外错误: {e}")
            traceback.print_exc()
            return False, f"导出失败: 意外错误: {type(e).__name__}: {e}"
