import csv
from exporters.base import DataExporter
from exporters.data_preparer import DataPreparer


class CSVExporter(DataExporter):
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        remaining_data_list = DataPreparer.convert_remaining_data(remaining_data, remaining_headers)
        mock_tree = DataPreparer.create_mock_tree(remaining_headers, remaining_data_list)

        with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

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

    def get_file_extension(self) -> str:
        return ".csv"
