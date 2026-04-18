import traceback
from reportlab.platypus import TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


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

HEADER_STYLE = [
    ("FONTSIZE", (0, 0), (-1, 0), 11),
    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ("TOPPADDING", (0, 0), (-1, 0), 4),
]


class TableStyleHelper:
    @staticmethod
    def get_table_style(table_colors, has_asian_font):
        header_font = "ChineseFont" if has_asian_font else "Helvetica-Bold"
        style = [
            ("BACKGROUND", (0, 0), (-1, 0), table_colors["header_bg"]),
            ("TEXTCOLOR", (0, 0), (-1, 0), table_colors["header_text"]),
            ("FONTNAME", (0, 0), (-1, 0), header_font),
            ("GRID", (0, 0), (-1, -1), 1, "#bdc3c7"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]
        return TableStyle(style + HEADER_STYLE + [("WORDWRAP", (0, 0), (-1, -1), False)])

    @staticmethod
    def calculate_text_width(text, ascii_width=8, non_ascii_width=12, padding=15):
        text_width = 0
        for char in text:
            if ord(char) > 127:
                text_width += non_ascii_width
            else:
                text_width += ascii_width
        text_width += padding
        return text_width

    @staticmethod
    def get_cell_text(cell):
        if hasattr(cell, 'getPlainText'):
            return cell.getPlainText()
        elif hasattr(cell, 'text'):
            return cell.text
        else:
            return str(cell)

    @staticmethod
    def calculate_auto_col_widths(table_data, table_width):
        table_cols = len(table_data[0]) if table_data else 0
        if table_cols == 0:
            return []

        max_col_widths = [0] * table_cols
        min_col_width = 60

        for row in table_data:
            for col_idx, cell in enumerate(row[:table_cols]):
                text = TableStyleHelper.get_cell_text(cell)
                text_width = TableStyleHelper.calculate_text_width(text, ascii_width=8, non_ascii_width=12, padding=15)
                if text_width > max_col_widths[col_idx]:
                    max_col_widths[col_idx] = text_width

        for i, width in enumerate(max_col_widths):
            if width < min_col_width:
                max_col_widths[i] = min_col_width

        total_width = sum(max_col_widths)
        final_widths = []

        data_col_widths = [0] * table_cols
        for row_idx, row in enumerate(table_data):
            if row_idx == 0:
                continue
            for col_idx, cell in enumerate(row[:table_cols]):
                text = TableStyleHelper.get_cell_text(cell)
                text_width = TableStyleHelper.calculate_text_width(text, ascii_width=8, non_ascii_width=12, padding=15)
                if text_width > data_col_widths[col_idx]:
                    data_col_widths[col_idx] = text_width

        if total_width > 0:
            combined_widths = [max(max_col_widths[i], data_col_widths[i]) for i in range(table_cols)]

            remaining_width = table_width
            for i in range(table_cols):
                final_widths.append(min_col_width)
                remaining_width -= min_col_width

            if remaining_width > 0:
                extra_widths = [max(0, combined_widths[i] - min_col_width) for i in range(table_cols)]
                total_extra = sum(extra_widths)

                if total_extra > 0:
                    for i in range(table_cols):
                        if extra_widths[i] > 0:
                            extra = (extra_widths[i] / total_extra) * remaining_width
                            final_widths[i] += extra
                        if data_col_widths[i] < min_col_width * 1.5:
                            final_widths[i] = min(final_widths[i], min_col_width * 1.5)
        else:
            final_widths = [table_width / table_cols] * table_cols

        return final_widths

    @staticmethod
    def get_col_widths(table_data, table_width, col_widths, num_cols):
        try:
            auto_col_widths = TableStyleHelper.calculate_auto_col_widths(table_data, table_width)
            col_widths = auto_col_widths
        except (ValueError, TypeError, AttributeError):
            traceback.print_exc()
            col_widths = [table_width / num_cols] * num_cols

        valid = []
        for width in col_widths:
            if width is None or not isinstance(width, (int, float)) or width <= 0:
                valid.append(100)
            else:
                valid.append(width)

        return valid

    @staticmethod
    def adjust_table_font_size(table_data, col_widths, table_text_style, min_font_size=8, style_prefix="CustomStyle"):
        adjusted_data = []
        for row_idx, row in enumerate(table_data):
            adjusted_row = []
            for col_idx, cell in enumerate(row[:len(col_widths)]):
                text = TableStyleHelper.get_cell_text(cell)
                text_width = TableStyleHelper.calculate_text_width(text, ascii_width=5, non_ascii_width=10, padding=8)

                font_size = 11 if row_idx == 0 else 10
                if text_width > col_widths[col_idx] * 0.9:
                    scale_factor = (col_widths[col_idx] * 0.95) / text_width
                    font_size = max(font_size * scale_factor, min_font_size)

                custom_style = ParagraphStyle(
                    f"{style_prefix}_{row_idx}_{col_idx}",
                    parent=table_text_style,
                    fontSize=font_size,
                    wordWrap="None"
                )
                adjusted_cell = Paragraph(text, custom_style)
                adjusted_row.append(adjusted_cell)
            adjusted_data.append(adjusted_row)
        return adjusted_data
