import json
from exporters.base import DataExporter
from i18n import _ as translate


class JSONExporter(DataExporter):
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        export_data = {}

        parent_cidr = self._get_parent_cidr(data_source)
        if parent_cidr:
            export_data[translate("parent_network")] = parent_cidr

        if data_source["main_name"] == translate("split_segment_info"):
            export_data[translate("split_segment_info")] = dict(main_data)
            export_data[translate("remaining_subnets")] = remaining_data
        else:
            export_data[f"{data_source['main_name']}"] = [dict(zip(main_headers, item)) for item in main_data]
            export_data[translate("remaining_subnets")] = remaining_data

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

    def _get_parent_cidr(self, data_source):
        chart_data = data_source.get("chart_data")
        if chart_data and "parent" in chart_data:
            return chart_data["parent"].get("name", "")
        return ""

    def get_file_extension(self) -> str:
        return ".json"
