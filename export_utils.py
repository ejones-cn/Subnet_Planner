#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出工具模块

提供多种格式的数据导出功能，包括:
1. PDF格式导出（支持中文）
2. JSON格式导出
3. TXT格式导出
4. CSV格式导出
5. Excel格式导出

所有导出功能均正确处理中文编码问题。

重构说明：本模块已重构为委托模式，核心逻辑已拆分到 exporters 包中：
- exporters.base: DataExporter 抽象基类
- exporters.font_manager: FontManager 字体管理器
- exporters.data_preparer: DataPreparer 数据准备逻辑
- exporters.table_style: TableStyleHelper 表格样式管理
- exporters.json_exporter: JSONExporter JSON导出器
- exporters.csv_exporter: CSVExporter CSV导出器
- exporters.txt_exporter: TXTExporter TXT导出器
- exporters.excel_exporter: ExcelExporter Excel导出器
- exporters.pdf_exporter: PDFExporter PDF导出器
- exporters.factory: ExporterFactory 导出器工厂
"""

import os
import traceback
from version import get_version
from i18n import _ as translate

__version__ = get_version()

from exporters.font_manager import FontManager
from exporters.data_preparer import DataPreparer
from exporters.factory import ExporterFactory


class ExportUtils:
    """数据导出工具类（重构后：委托模式）"""

    def __init__(self) -> None:
        self._font_manager = FontManager()
        self.has_asian_font: bool = self._font_manager.has_asian_font
        ExporterFactory.initialize(self._font_manager)

    @classmethod
    def clear_font_cache(cls) -> None:
        FontManager.clear_font_cache()

    def format_large_number(self, num, use_scientific=True):
        from ip_subnet_calculator import format_large_number
        return format_large_number(num, use_scientific)

    def _prepare_export_data(self, data_source):
        return DataPreparer.prepare_export_data(data_source)

    def export_data(self, data_source, _title, _success_msg, failure_msg):
        try:
            main_data, main_headers, remaining_data, remaining_headers = DataPreparer.prepare_export_data(data_source)

            is_valid = True
            error_msg = ""

            split_segment_info = translate("split_segment_info")
            allocated_subnets = translate("allocated_subnets")

            if data_source["main_name"] == split_segment_info:
                if not main_data:
                    is_valid = False
                    error_msg = translate("no_split_data_found")
            elif data_source["main_name"] == allocated_subnets:
                if not main_data:
                    is_valid = False
                    error_msg = translate("no_planning_data_found")

            if not is_valid:
                return False, error_msg, None

            return True, "data_prepared", (main_data, main_headers, remaining_data, remaining_headers)

        except (ValueError, TypeError, KeyError) as e:
            traceback.print_exc()
            return False, f"{failure_msg}: {str(e)}", None

    def export_to_file(self, file_path, data_source, main_data, main_headers, remaining_data, remaining_headers):
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            exporter = ExporterFactory.get_exporter(file_ext)

            if not exporter:
                return False, f"不支持的文件格式: {file_ext}"

            exporter.export(file_path, data_source, main_data, main_headers, remaining_data, remaining_headers)

            return True, f"成功导出到: {file_path}"
        except PermissionError as e:
            return False, f"导出失败: 没有写入权限，请检查文件是否被占用或目录权限是否正确: {e}"
        except FileNotFoundError as e:
            return False, f"导出失败: 文件路径不存在: {e}"
        except (IOError, OSError) as e:
            return False, f"导出失败: IO错误: {e}"
        except ValueError as e:
            return False, f"导出失败: 数据格式错误: {e}"
        except TypeError as e:
            return False, f"导出失败: 类型错误: {e}"
        except Exception as e:
            print(f"导出过程中发生意外错误: {e}")
            traceback.print_exc()
            return False, f"导出失败: 意外错误: {type(e).__name__}: {e}"
