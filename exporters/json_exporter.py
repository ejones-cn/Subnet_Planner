import json
from exporters.base import DataExporter
from i18n import _ as translate


class JSONExporter(DataExporter):
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
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

    def get_file_extension(self) -> str:
        return ".json"
