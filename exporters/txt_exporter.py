from exporters.base import DataExporter
from exporters.data_preparer import DataPreparer


class TXTExporter(DataExporter):
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"{data_source['main_name']}\n")
            f.write("=" * 80 + "\n")

            if DataPreparer.is_k2v_headers(main_headers):
                self._write_k2v_data(f, main_data)
            else:
                self._write_table_data(f, main_data, main_headers)

            f.write(f"\n\n{data_source['remaining_name']}\n")
            f.write("=" * 80 + "\n")

            if remaining_headers and remaining_data:
                self._write_remaining_data(f, remaining_data, remaining_headers)
            else:
                self._write_remaining_from_tree(f, data_source)

    def _write_k2v_data(self, f, main_data):
        max_key_colon_width = 0
        for values in main_data:
            if len(values) > 0:
                key_colon_width = len(f"{str(values[0])}:")
                if key_colon_width > max_key_colon_width:
                    max_key_colon_width = key_colon_width

        tab_width = 8
        max_tabs = (max_key_colon_width + tab_width - 1) // tab_width

        reduced_tab_fields = ["通配符掩码", "可用地址数"]

        for values in main_data:
            key = str(values[0])
            value = str(values[1])
            key_colon = f"{key}:"
            current_tabs = (len(key_colon) + tab_width - 1) // tab_width
            extra_tabs = max_tabs - current_tabs + 1

            if key in reduced_tab_fields:
                extra_tabs = max(1, extra_tabs - 1)

            f.write(f"{key_colon}{'\t' * extra_tabs}{value}\n")

    def _write_table_data(self, f, data, headers):
        max_widths = []
        for i, header in enumerate(headers):
            max_widths.append(len(str(header)) + 2)

        for values in data:
            for i, value in enumerate(values):
                if i < len(max_widths):
                    current_width = len(str(value)) + 2
                    if current_width > max_widths[i]:
                        max_widths[i] = current_width

        max_widths = [max(w, 12) for w in max_widths]

        for i, header in enumerate(headers):
            f.write(f"{header:<{max_widths[i]}}")
        f.write("\n")

        total_width = sum(max_widths)
        f.write("-" * total_width + "\n")

        for values in data:
            for i, value in enumerate(values):
                if i < len(max_widths):
                    f.write(f"{str(value):<{max_widths[i]}}")
            f.write("\n")

    def _write_remaining_data(self, f, remaining_data, remaining_headers):
        all_remaining_rows = []
        for item in remaining_data:
            if isinstance(item, dict):
                values = [item.get(header, '') for header in remaining_headers]
            else:
                values = item
            all_remaining_rows.append(values)

        self._write_table_data(f, all_remaining_rows, remaining_headers)

    def _write_remaining_from_tree(self, f, data_source):
        remaining_tree = data_source["remaining_tree"]
        remaining_headers = [remaining_tree.heading(col, "text") or ""
                             for col in remaining_tree["columns"]]

        all_remaining_rows = []
        for item in remaining_tree.get_children():
            values = remaining_tree.item(item, "values")
            all_remaining_rows.append(values)

        self._write_table_data(f, all_remaining_rows, remaining_headers)

    def get_file_extension(self) -> str:
        return ".txt"
