import csv
from exporters.base import DataExporter
from exporters.data_preparer import DataPreparer
from i18n import _ as translate


class CSVExporter(DataExporter):
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        remaining_data_list = DataPreparer.convert_remaining_data(remaining_data, remaining_headers)
        mock_tree = DataPreparer.create_mock_tree(remaining_headers, remaining_data_list)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            parent_cidr = self._get_parent_cidr(data_source)
            if parent_cidr:
                writer.writerow([translate("parent_network"), parent_cidr])
                writer.writerow([])

            writer.writerow(main_headers)
            for values in main_data:
                writer.writerow(values)

            writer.writerow([])

            if remaining_headers:
                writer.writerow(remaining_headers)
            else:
                remaining_headers = [mock_tree.heading(col, "text") or "" for col in mock_tree["columns"]]
                writer.writerow(remaining_headers)

            for item in mock_tree.get_children():
                values = mock_tree.item(item, "values")
                writer.writerow(values)

    def _get_parent_cidr(self, data_source):
        chart_data = data_source.get("chart_data")
        if chart_data and "parent" in chart_data:
            return chart_data["parent"].get("name", "")
        return ""

    def get_file_extension(self) -> str:
        return ".csv"
