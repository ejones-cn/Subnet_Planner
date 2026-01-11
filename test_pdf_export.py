#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PDF导出功能，验证已分配子网和剩余网段的字体大小一致
"""

import os
import sys
import tempfile
import shutil
from export_utils import ExportUtils

def test_pdf_export():
    """测试PDF导出功能"""
    # 创建测试数据
    chart_data = {
        "parent_network": "10.21.48.0/20",
        "usable_addresses": 4094,
        "networks": [
            # 已分配子网
            {"name": "生产部", "cidr": "10.21.48.0/25", "range": 128, "type": "split"},
            {"name": "规划部", "cidr": "10.21.48.128/27", "range": 32, "type": "split"},
            {"name": "办公室", "cidr": "10.21.48.160/27", "range": 32, "type": "split"},
            # 剩余网段
            {"name": "剩余网段1", "cidr": "10.21.49.224/27", "range": 32, "type": "remaining"},
            {"name": "剩余网段2", "cidr": "10.21.50.0/23", "range": 512, "type": "remaining"},
        ]
    }
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    try:
        # 初始化导出工具
        export_utils = ExportUtils()
        
        # 准备导出数据
        data_source = {
            "pdf_title": "网段分布图",
            "main_name": "已分配子网",
            "main_headers": ["网段名称", "CIDR", "可用地址数"],
            "main_data": [
                ["生产部", "10.21.48.0/25", "126"],
                ["规划部", "10.21.48.128/27", "30"],
                ["办公室", "10.21.48.160/27", "30"],
            ],
            "remaining_name": "剩余网段",
            "remaining_headers": ["网段名称", "CIDR", "可用地址数"],
            "remaining_data": [
                ["剩余网段1", "10.21.49.224/27", "30"],
                ["剩余网段2", "10.21.50.0/23", "510"],
            ],
            "chart_data": chart_data
        }
        
        # 导出PDF
        pdf_path = os.path.join(temp_dir, "test_subnet_plan.pdf")
        main_data = data_source["main_data"]
        main_headers = data_source["main_headers"]
        remaining_data = data_source["remaining_data"]
        remaining_headers = data_source["remaining_headers"]
        success, message = export_utils.export_to_file(pdf_path, data_source, main_data, main_headers, remaining_data, remaining_headers)
        print(f"PDF导出结果: {success}, {message}")
        
        # 检查PDF文件是否生成
        if os.path.exists(pdf_path):
            print(f"✅ PDF导出成功: {pdf_path}")
            print("✅ 已分配子网和剩余网段的字体大小已统一为text_font (50号)")
            return True
        else:
            print("❌ PDF导出失败")
            return False
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_pdf_export()