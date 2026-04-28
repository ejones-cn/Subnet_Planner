import time
import traceback
import math
from io import BytesIO
from PIL import Image, ImageDraw

from typing import override

from exporters.base import DataExporter
from exporters.font_manager import FontManager
from exporters.table_style import TableStyleHelper, MAIN_TABLE_COLORS, REMAINING_TABLE_COLORS
from exporters.data_preparer import DataPreparer
from i18n import _ as translate, get_language

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Table,
    Paragraph,
    Spacer,
    Image as RLImage,
    PageBreak,
    NextPageTemplate,
    KeepTogether,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class PDFExporter(DataExporter):
    def __init__(self, font_manager: FontManager):
        self.font_manager = font_manager

    @override
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        self.font_manager.register_pdf_fonts()
        has_asian_font = self.font_manager.has_asian_font

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

        def get_date_format():
            lang = get_language()
            if lang == "ko":
                return "%Y년%m월%d일 %H:%M:%S"
            elif lang in ["zh", "zh_tw"]:
                return "%Y年%m月%d日 %H:%M:%S"
            elif lang == "ja":
                return "%Y年%m月%d日 %H:%M:%S"
            else:
                return "%Y-%m-%d %H:%M:%S"

        export_time = time.strftime(get_date_format())

        def on_page(canvas, _event):
            canvas.saveState()
            current_width, current_height = canvas._pagesize
            font_name = "ChineseFont" if has_asian_font else "Helvetica"
            canvas.setFont(font_name, 10)
            canvas.setFillColor(colors.HexColor("#666666"))
            canvas.drawRightString(
                current_width - margins[1],
                current_height - 40,
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
            fontName="ChineseFont" if has_asian_font else "Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor("#2c3e50"),
            alignment=TA_CENTER,
            spaceAfter=20,
        )

        heading2_style = ParagraphStyle(
            "ChineseHeading2",
            parent=styles["Heading2"],
            fontName="ChineseFont" if has_asian_font else "Helvetica-Bold",
            fontSize=16,
            textColor=colors.HexColor("#34495e"),
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=12,
        )

        normal_style = ParagraphStyle(
            "ChineseNormal",
            parent=styles["Normal"],
            fontName="ChineseFont" if has_asian_font else "Helvetica",
            fontSize=11,
            textColor=colors.HexColor("#34495e"),
            spaceAfter=5,
        )

        table_text_style = ParagraphStyle(
            "ChineseTableText",
            parent=styles["Normal"],
            fontName="ChineseFont" if has_asian_font else "Helvetica",
            fontSize=10,
            alignment=TA_CENTER,
            wordWrap="None",
            leading=12,
            spaceBefore=0,
            spaceAfter=0,
        )

        elements.append(Paragraph(data_source["pdf_title"], title_style))
        elements.append(Spacer(1, 15))

        if data_source["main_name"] in [translate("split_segment_info"), translate("allocated_subnets")]:
            self._add_parent_network_section(elements, data_source, heading2_style, table_text_style, has_asian_font, page_width, margins)

        self._add_main_data_section(elements, data_source, main_data, main_headers, heading2_style, normal_style, table_text_style, has_asian_font, page_width, margins)

        self._add_remaining_data_section(elements, data_source, remaining_data, remaining_headers, heading2_style, normal_style, table_text_style, has_asian_font, page_width, margins)

        chart_data = data_source.get("chart_data")
        if chart_data:
            try:
                print("开始添加网段分布图到PDF...")
                self._add_chart_to_pdf(elements, chart_data, margins, portrait_width, portrait_height)
            except (IOError, ValueError, TypeError, AttributeError) as e:
                print(f"添加网段分布图失败: {e}")
                traceback.print_exc()

        doc.build(elements)

    def _add_parent_network_section(self, elements, data_source, heading2_style, table_text_style, has_asian_font, page_width, margins):
        elements.append(Paragraph(str(translate("parent_network_info")), heading2_style))

        chart_data = data_source.get("chart_data")
        if chart_data and "parent" in chart_data:
            parent_info = chart_data["parent"]

            from ip_subnet_calculator import get_subnet_info

            parent_cidr = parent_info.get("name", "")
            full_parent_info = get_subnet_info(parent_cidr)

            parent_table_data = []

            parent_ip_version = full_parent_info.get('version', 4)
            is_ipv6 = parent_ip_version == 6

            if is_ipv6:
                parent_table_data.append([
                    Paragraph(str(translate("parent_cidr")), table_text_style),
                    Paragraph(str(translate("network_address")), table_text_style),
                    Paragraph(str(translate("prefix_length")), table_text_style),
                    Paragraph(str(translate("available_addresses")), table_text_style),
                    Paragraph(str(translate("host_address_range")), table_text_style)
                ])

                parent_table_data.append([
                    Paragraph(str(full_parent_info.get("cidr", parent_cidr)), table_text_style),
                    Paragraph(str(full_parent_info.get("network", "")), table_text_style),
                    Paragraph(str(full_parent_info.get("prefixlen", "")), table_text_style),
                    Paragraph(self._format_large_number(full_parent_info.get('usable_addresses', 0)), table_text_style),
                    Paragraph(f"{full_parent_info.get('host_range_start', '')} - {full_parent_info.get('host_range_end', '')}", table_text_style)
                ])
            else:
                parent_table_data.append([
                    Paragraph(str(translate("parent_cidr")), table_text_style),
                    Paragraph(str(translate("network_address")), table_text_style),
                    Paragraph(str(translate("subnet_mask")), table_text_style),
                    Paragraph(str(translate("wildcard_mask")), table_text_style),
                    Paragraph(str(translate("broadcast_address")), table_text_style),
                    Paragraph(str(translate("prefix_length")), table_text_style),
                    Paragraph(str(translate("available_addresses")), table_text_style),
                    Paragraph(str(translate("host_address_range")), table_text_style)
                ])

                parent_table_data.append([
                    Paragraph(str(full_parent_info.get("cidr", parent_cidr)), table_text_style),
                    Paragraph(str(full_parent_info.get("network", "")), table_text_style),
                    Paragraph(str(full_parent_info.get("netmask", "")), table_text_style),
                    Paragraph(str(full_parent_info.get("wildcard", "")), table_text_style),
                    Paragraph(str(full_parent_info.get("broadcast", "")), table_text_style),
                    Paragraph(str(full_parent_info.get("prefixlen", "")), table_text_style),
                    Paragraph(self._format_large_number(full_parent_info.get('usable_addresses', 0)), table_text_style),
                    Paragraph(f"{full_parent_info.get('host_range_start', '')} - {full_parent_info.get('host_range_end', '')}", table_text_style)
                ])

            table_width = page_width - margins[0] - margins[1]
            num_cols = len(parent_table_data[0])
            col_widths = TableStyleHelper.get_col_widths(parent_table_data, table_width, None, num_cols)

            valid_col_widths = []
            for width in col_widths:
                if width is None or not isinstance(width, (int, float)) or width <= 0:
                    valid_col_widths.append(table_width / num_cols)
                else:
                    valid_col_widths.append(width)

            valid_table_data = []
            for row in parent_table_data:
                valid_row = []
                for cell in row:
                    if cell is None:
                        valid_row.append(Paragraph("", table_text_style))
                    else:
                        valid_row.append(cell)
                valid_table_data.append(valid_row)

            parent_table = Table(valid_table_data, colWidths=valid_col_widths, repeatRows=1)
            parent_table.setStyle(TableStyleHelper.get_table_style(MAIN_TABLE_COLORS, has_asian_font))
            elements.append(parent_table)
            elements.append(Spacer(1, 20))

    def _add_main_data_section(self, elements, data_source, main_data, main_headers, heading2_style, normal_style, table_text_style, has_asian_font, page_width, margins):
        main_heading = Paragraph(data_source["main_name"], heading2_style)
        keep_together_main: list = [main_heading]

        is_ipv6 = False
        for values in main_data:
            for v in values:
                if isinstance(v, str) and ':' in v and len(v) > 10:
                    is_ipv6 = True
                    break
            if is_ipv6:
                break

        if data_source["main_name"] == translate("split_segment_info"):
            main_table_data = self._build_split_segment_table(main_data, table_text_style, is_ipv6)
        elif DataPreparer.is_k2v_headers(main_headers):
            main_table_data = [[Paragraph("项目", table_text_style), Paragraph("值", table_text_style)]]
            for values in main_data:
                main_table_data.append(
                    [
                        Paragraph(str(values[0]) if values[0] is not None else "", table_text_style),
                        Paragraph(str(values[1]) if values[1] is not None else "", table_text_style),
                    ]
                )
        else:
            main_table_data = self._build_allocated_subnets_table(main_data, main_headers, table_text_style, is_ipv6, data_source)

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

            valid_col_widths = TableStyleHelper.get_col_widths(main_table_data, table_width, col_widths, table_cols)
            adjusted_table_data = TableStyleHelper.adjust_table_font_size(main_table_data, valid_col_widths, table_text_style, style_prefix="CustomStyle")

            main_table = Table(adjusted_table_data, colWidths=valid_col_widths, repeatRows=1)
            main_table.setStyle(TableStyleHelper.get_table_style(MAIN_TABLE_COLORS, has_asian_font))
            keep_together_main.append(main_table)
        else:
            main_name_text = str(translate('no')) if translate('no') else "无"
            keep_together_main.append(Paragraph(f"{main_name_text}{str(data_source['main_name'])}", normal_style))

        elements.append(KeepTogether(keep_together_main))
        elements.append(Spacer(1, 20))

    def _build_split_segment_table(self, main_data, table_text_style, is_ipv6):
        columns_to_remove = [translate("parent_network"), translate("split_line"), translate("prefix_length"), translate("cidr"), translate("separator"), translate("network_address")]

        if not is_ipv6:
            columns_to_remove.append(translate("broadcast_address"))

        filtered_data = {}
        for values in main_data:
            key = str(values[0]) if values[0] is not None else ""
            value = str(values[1]) if values[1] is not None else ""
            if key and key not in columns_to_remove and not all(c == '-' for c in key):
                filtered_data[key] = value

        if filtered_data:
            headers = list(filtered_data.keys())
            main_table_data = [[Paragraph(h, table_text_style) for h in headers]]
            values = [filtered_data[h] for h in headers]
            main_table_data.append([Paragraph(str(v), table_text_style) for v in values])
        else:
            main_table_data = []

        return main_table_data

    def _build_allocated_subnets_table(self, main_data, main_headers, table_text_style, is_ipv6, data_source):
        if is_ipv6 and data_source["main_name"] == translate("allocated_subnets"):
            main_headers = [h for h in main_headers if h not in [translate("subnet_mask"), translate("wildcard_mask"), translate("broadcast_address")]]
            main_table_data = [[Paragraph(h, table_text_style) for h in main_headers]]

            for values in main_data:
                filtered_values = []
                for i, header in enumerate(main_headers):
                    if i < len(values):
                        if header not in [translate("subnet_mask"), translate("wildcard_mask"), translate("broadcast_address")]:
                            filtered_values.append(values[i])
                main_table_data.append(
                    [Paragraph(str(v) if v is not None else "", table_text_style) for v in filtered_values]
                )
        else:
            filtered_headers = [h for h in main_headers if h != translate("network_end_address")]
            main_table_data = [[Paragraph(h, table_text_style) for h in filtered_headers]]

            for values in main_data:
                filtered_values = []
                for i, header in enumerate(main_headers):
                    if i < len(values):
                        if header != translate("network_end_address"):
                            filtered_values.append(values[i])
                main_table_data.append(
                    [Paragraph(str(v) if v is not None else "", table_text_style) for v in filtered_values]
                )

        return main_table_data

    def _add_remaining_data_section(self, elements, data_source, remaining_data, remaining_headers, heading2_style, normal_style, table_text_style, has_asian_font, page_width, margins):
        remaining_heading = Paragraph(str(data_source["remaining_name"]), heading2_style)
        keep_together_remaining: list = [remaining_heading]

        remaining_table_data = [[Paragraph(str(h), table_text_style) for h in remaining_headers]]

        for item in remaining_data:
            if isinstance(item, dict):
                values = [item.get(header, '') for header in remaining_headers]
            else:
                values = item
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

            valid_col_widths = TableStyleHelper.get_col_widths(remaining_table_data, table_width, col_widths, table_cols)
            adjusted_remaining_data = TableStyleHelper.adjust_table_font_size(remaining_table_data, valid_col_widths, table_text_style, style_prefix="CustomRemainingStyle")

            remaining_table = Table(adjusted_remaining_data, colWidths=valid_col_widths, repeatRows=1)
            remaining_table.setStyle(TableStyleHelper.get_table_style(REMAINING_TABLE_COLORS, has_asian_font))
            keep_together_remaining.append(remaining_table)
        else:
            no_text = str(translate('no')) if translate('no') else "无"
            remaining_name_text = str(data_source['remaining_name'])
            keep_together_remaining.append(Paragraph(f"{no_text}{remaining_name_text}", normal_style))

        elements.append(KeepTogether(keep_together_remaining))

    def _add_chart_to_pdf(self, elements, chart_data, margins, portrait_width, portrait_height):
        from i18n import _ as translate

        if not chart_data or 'networks' not in chart_data or len(chart_data['networks']) == 0:
            print("没有有效的网段分布图数据，跳过")
            return

        print(f"检测到有效网段分布图数据，包含 {len(chart_data['networks'])} 个网段")

        elements.append(NextPageTemplate('portrait'))
        elements.append(PageBreak())

        parent_info = chart_data.get("parent", {})
        parent_cidr = parent_info.get("name", translate("parent_network"))
        parent_range = parent_info.get("range", 1)
        networks = chart_data.get("networks", [])

        chart_type = chart_data.get("type", "split")

        split_networks = [net for net in networks if net.get("type") == "split"]
        remaining_networks = [net for net in networks if net.get("type") != "split"]

        title_height = 280
        parent_network_height = 150
        legend_height = 150
        segment_height = 134
        demand_title_height = 180 if chart_type == "plan" else 0
        separator_height = 100
        remaining_title_height = 180

        required_height = (title_height
                          + parent_network_height
                          + separator_height
                          + demand_title_height
                          + len(split_networks) * segment_height
                          + separator_height
                          + remaining_title_height
                          + len(remaining_networks) * segment_height
                          + legend_height
                          + 50)

        high_res_width = 2480
        high_res_height = max(3508, required_height)

        pil_image = Image.new('RGB', (high_res_width, high_res_height), color='#333333')
        draw = ImageDraw.Draw(pil_image)

        title_font_size = 76
        _, title_font, _ = self.font_manager.load_system_font(title_font_size, verbose=False)
        self.font_manager.load_system_font(font_size=36, verbose=False)
        text_font_size = 50
        text_font, bold_text_font, _ = self.font_manager.load_system_font(font_size=text_font_size, bold_offset=6, verbose=False)

        margin_left = 180
        margin_right = 150
        margin_top = 280
        chart_width = high_res_width - margin_left - margin_right
        chart_x = margin_left
        chart_right = chart_x + chart_width
        ADDRESS_OFFSET = 50

        def draw_text_with_stroke(draw_obj, position, text, font, fill, stroke_color="#666666", stroke_width=4):
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
                x, y = position
                directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for dx, dy in directions:
                    draw_obj.text((x + dx, y + dy), text, font=font, fill=stroke_color)
                draw_obj.text((x, y), text, font=font, fill=fill)

        log_max = math.log10(parent_range)
        log_min = 3

        min_bar_width = 120
        padding = 34
        bar_height = 100

        subnet_colors = [
            "#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8",
            "#5b8fd9", "#3c70d8", "#e68838", "#a04132",
            "#6a9da8", "#87c569", "#6d8de8", "#c16fa0",
            "#a99bc6", "#a44d69", "#b9d0f8", "#5d4ea5",
            "#f5ad8c", "#5b8fd9", "#db6679", "#a6c589",
        ]

        title = translate("distribution_chart")
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = (high_res_width - (title_bbox[2] - title_bbox[0])) // 2
        title_y = 100
        draw_text_with_stroke(draw, (title_x, title_y), translate("distribution_chart"), title_font, "#ffffff")

        y = margin_top

        log_value = max(log_min, math.log10(parent_range))
        bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
        parent_color = "#636e72"
        draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=parent_color, outline=None, width=0)

        usable_addresses = parent_range - 2 if parent_range > 2 else parent_range
        segment_text = f"{translate('parent_network')}: {parent_cidr}"
        address_text = f"{translate('usable_addresses')}: {self._format_large_number(usable_addresses)}"

        def get_centered_y(box_y, box_height, _, _font):
            return box_y + box_height // 2 - 38

        segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
        segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
        address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
        address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)

        address_width = address_bbox[2] - address_bbox[0]
        address_x = chart_right - ADDRESS_OFFSET - address_width

        draw_text_with_stroke(draw, (chart_x + 30, segment_text_y), segment_text, bold_text_font, "#ffffff")
        draw_text_with_stroke(draw, (address_x, address_text_y), address_text, bold_text_font, "#ffffff")

        y += bar_height + padding

        if chart_type == "plan":
            draw.line([chart_x, y + 20, chart_x + chart_width, y + 20], fill="#cccccc", width=4)
            y += 60
        else:
            y += 0

        if chart_type == "plan":
            demand_count = len(split_networks)
            title_text = f"{translate('allocated_subnets')} ({demand_count} {translate('pieces')}):"
            title_bbox = draw.textbbox((0, 0), title_text, font=bold_text_font)
            title_text_y = get_centered_y(y, bar_height, title_bbox, bold_text_font)
            draw_text_with_stroke(draw, (chart_x, title_text_y), title_text, bold_text_font, "#ffffff")
            y += 100

        for i, network in enumerate(split_networks):
            network_range = network.get("range", 1)
            log_value = max(log_min, math.log10(network_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)

            if chart_type == "split":
                split_color = "#4a7eb4"
                name = network.get("name", "")
                segment_text = f"{translate('split_segment')}: {name}"

                usable_addresses = network_range - 2 if network_range > 2 else network_range
                address_text = f"{translate('usable_addresses')}: {self._format_large_number(usable_addresses)}"

                segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
                segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
                address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
                address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)

                address_width = address_bbox[2] - address_bbox[0]
                address_x = chart_right - ADDRESS_OFFSET - address_width

                draw_text_with_stroke(draw, (chart_x + 30, segment_text_y), segment_text, bold_text_font, "#ffffff")
                draw_text_with_stroke(draw, (address_x, address_text_y), address_text, bold_text_font, "#ffffff")
            else:
                color_index = i % len(subnet_colors)
                split_color = subnet_colors[color_index]
                name = network.get("name", "")
                cidr = network.get("cidr", "")
                segment_text = f"{translate('segment')} {i + 1}: {name}    {cidr}"

                draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=split_color, outline=None, width=0)

                usable_addresses = network_range - 2 if network_range > 2 else network_range
                address_text = f"{translate('usable_addresses')}: {self._format_large_number(usable_addresses)}"

                segment_bbox = draw.textbbox((0, 0), segment_text, font=text_font)
                segment_text_y = get_centered_y(y, bar_height, segment_bbox, text_font)
                address_bbox = draw.textbbox((0, 0), address_text, font=text_font)
                address_text_y = get_centered_y(y, bar_height, address_bbox, text_font)

                address_width = address_bbox[2] - address_bbox[0]
                address_x = chart_right - ADDRESS_OFFSET - address_width

                draw_text_with_stroke(draw, (chart_x + 30, segment_text_y), segment_text, text_font, "#ffffff")
                draw_text_with_stroke(draw, (address_x, address_text_y), address_text, text_font, "#ffffff")

            y += bar_height + padding

        draw.line([chart_x, y + 20, chart_x + chart_width, y + 20], fill="#cccccc", width=4)

        y += 80
        remaining_count = len(remaining_networks)
        title_text = f"{translate('remaining_subnets')} ({remaining_count} {translate('pieces')}):"

        title_bbox = draw.textbbox((0, 0), title_text, font=bold_text_font)
        title_text_y = get_centered_y(y, bar_height, title_bbox, bold_text_font)
        draw_text_with_stroke(draw, (chart_x, title_text_y), title_text, bold_text_font, "#ffffff")
        y += 100

        for i, network in enumerate(remaining_networks):
            network_range = network.get("range", 1)
            log_value = max(log_min, math.log10(network_range))
            bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
            color_index = i % len(subnet_colors)
            color = subnet_colors[color_index]
            draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=color, outline=None, width=0)

            name = network.get("name", "")
            usable_addresses = network_range - 2 if network_range > 2 else network_range

            segment_text = f"{translate('segment')} {i + 1}: {name}"
            address_text = f"{translate('usable_addresses')}: {self._format_large_number(usable_addresses)}"

            segment_bbox = draw.textbbox((0, 0), segment_text, font=text_font)
            segment_text_y = get_centered_y(y, bar_height, segment_bbox, text_font)
            address_bbox = draw.textbbox((0, 0), address_text, font=text_font)
            address_text_y = get_centered_y(y, bar_height, address_bbox, text_font)

            address_width = address_bbox[2] - address_bbox[0]
            address_x = chart_right - ADDRESS_OFFSET - address_width

            draw_text_with_stroke(draw, (chart_x + 30, segment_text_y), segment_text, text_font, "#ffffff")
            draw_text_with_stroke(draw, (address_x, address_text_y), address_text, text_font, "#ffffff")

            y += bar_height + padding

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
            return container_center - text_height // 2 - int(text_height * 0.30)

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
        draw_text_with_stroke(draw, (parent_x + parent_block_size + 25, parent_label_y), parent_label, parent_text_font, "#ffffff")

        parent_label_width = parent_label_bbox[2] - parent_label_bbox[0]
        split_x = parent_x + parent_block_size + 25 + parent_label_width + 80
        split_text_font = text_font
        legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
        split_block_gap = 15

        if chart_type == "split":
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
            split_label = f"{translate('allocated_subnets')}"
            split_block_size = 30

            split_block_y = legend_container_y + (legend_container_height - split_block_size) // 2
            split_label_bbox = draw.textbbox((0, 0), split_label, font=split_text_font)
            split_label_y = get_centered_text_y(legend_container_y, legend_container_height, split_label_bbox)

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

        if chart_type == "split":
            split_label_text = translate("split_segment")
            split_label_width = draw.textbbox((0, 0), split_label_text, font=split_text_font)[2] - draw.textbbox((0, 0), split_label_text, font=split_text_font)[0]
            remaining_x = split_x + split_block_size + 15 + split_label_width + 80
        else:
            split_label_text = f"{translate('allocated_subnets')}"
            split_label_width = draw.textbbox((0, 0), split_label_text, font=split_text_font)[2] - draw.textbbox((0, 0), split_label_text, font=split_text_font)[0]
            remaining_x = split_x + len(legend_colors) * (split_block_size + split_block_gap) + 15 + split_label_width + 80
        remaining_label = f"{translate('remaining_subnets')}"
        remaining_block_size = 30
        remaining_block_gap = 15
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

        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format='PNG', dpi=(300, 300))
        img_byte_arr.seek(0)
        print(f"成功保存高DPI PNG图像，尺寸: {pil_image.size}, DPI: 300")

        actual_image_height = high_res_height
        image_ratio = high_res_width / actual_image_height

        available_width = portrait_width - margins[0] - margins[1] - 20

        final_pdf_width = available_width
        final_pdf_height = final_pdf_width / image_ratio

        max_available_height = portrait_height - margins[2] - margins[3] - 20
        if final_pdf_height > max_available_height:
            final_pdf_height = max_available_height
            final_pdf_width = final_pdf_height * image_ratio

        elements.append(RLImage(img_byte_arr, width=final_pdf_width, height=final_pdf_height))

        elements.append(NextPageTemplate('landscape'))
        elements.append(PageBreak())

        print("网段分布图成功添加到PDF")

    def _format_large_number(self, num, use_scientific=True):
        from ip_subnet_calculator import format_large_number
        return format_large_number(num, use_scientific)

    @override
    def get_file_extension(self) -> str:
        return ".pdf"
