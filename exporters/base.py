from abc import ABC, abstractmethod


class DataExporter(ABC):
    @abstractmethod
    def export(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        pass
