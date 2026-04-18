from exporters.base import DataExporter
from exporters.font_manager import FontManager
from exporters.json_exporter import JSONExporter
from exporters.csv_exporter import CSVExporter
from exporters.txt_exporter import TXTExporter
from exporters.excel_exporter import ExcelExporter
from exporters.pdf_exporter import PDFExporter


class ExporterFactory:
    _exporters: dict[str, DataExporter] = {}

    @classmethod
    def initialize(cls, font_manager: FontManager | None = None) -> None:
        if font_manager is None:
            font_manager = FontManager()

        cls._exporters = {
            ".json": JSONExporter(),
            ".csv": CSVExporter(),
            ".txt": TXTExporter(),
            ".xlsx": ExcelExporter(),
            ".pdf": PDFExporter(font_manager),
        }

    @classmethod
    def get_exporter(cls, file_extension: str) -> DataExporter | None:
        if not cls._exporters:
            cls.initialize()
        return cls._exporters.get(file_extension)

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        if not cls._exporters:
            cls.initialize()
        return list(cls._exporters.keys())
