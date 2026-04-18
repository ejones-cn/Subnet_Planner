from abc import ABC, abstractmethod


class DataExporter(ABC):
    @abstractmethod
    def export(self, file_path: str, data_source: dict, main_data: list, main_headers: list, remaining_data: list, remaining_headers: list) -> None:
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass
