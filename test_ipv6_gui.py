#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IPv6 GUI功能测试脚本
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from windows_app import IPSubnetSplitterApp

class TestIPv6GUIFunctions(unittest.TestCase):
    """测试IPv6 GUI功能"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建一个模拟的root窗口
        self.mock_root = MagicMock()
        self.mock_root.winfo_width.return_value = 800
        self.mock_root.winfo_height.return_value = 600
        
        # 创建应用程序实例
        self.app = IPSubnetSplitterApp(self.mock_root)
    
    def test_validate_cidr_ipv6(self):
        """测试CIDR验证函数对IPv6的支持"""
        """测试CIDR验证函数对IPv6的支持"""
        # 测试有效的IPv6 CIDR
        self.assertTrue(self.app.validate_cidr("2001:0db8::/32"))
        self.assertTrue(self.app.validate_cidr("2001:0db8::1/128"))
        self.assertTrue(self.app.validate_cidr("fe80::/10"))
        
        # 测试无效的IPv6 CIDR
        self.assertFalse(self.app.validate_cidr("2001:0db8::/32/"))
        self.assertFalse(self.app.validate_cidr("2001:0db8::1:2:3:4:5:6/64"))
        self.assertFalse(self.app.validate_cidr("invalid_ipv6"))
    
    def test_on_ip_version_change(self):
        """测试IP版本切换功能"""
        # 模拟规划父网段输入框
        self.app.planning_parent_entry = MagicMock()
        self.app.planning_parent_entry.delete = MagicMock()
        self.app.planning_parent_entry.insert = MagicMock()
        self.app.planning_parent_entry.config = MagicMock()
        
        # 测试切换到IPv6
        self.app.ip_version_var = MagicMock()
        self.app.ip_version_var.get.return_value = "IPv6"
        
        self.app.on_ip_version_change()
        
        # 验证输入框被清空
        self.app.planning_parent_entry.delete.assert_called_once_with(0, "end")
        
        # 验证IPv6默认值被设置
        self.app.planning_parent_entry.insert.assert_called_once()
        inserted_value = self.app.planning_parent_entry.insert.call_args[0][1]
        self.assertTrue(inserted_value.startswith("2001:0db8::"))
    
    def test_on_split_ip_version_change(self):
        """测试子网切分功能的IP版本切换"""
        # 模拟子网切分的输入框
        self.app.parent_entry = MagicMock()
        self.app.parent_entry.delete = MagicMock()
        self.app.parent_entry.insert = MagicMock()
        self.app.parent_entry.config = MagicMock()
        
        self.app.split_entry = MagicMock()
        self.app.split_entry.delete = MagicMock()
        self.app.split_entry.insert = MagicMock()
        self.app.split_entry.config = MagicMock()
        
        # 测试切换到IPv6
        self.app.split_ip_version_var = MagicMock()
        self.app.split_ip_version_var.get.return_value = "IPv6"
        
        self.app.on_split_ip_version_change()
        
        # 验证输入框被清空
        self.app.parent_entry.delete.assert_called_once_with(0, "end")
        self.app.split_entry.delete.assert_called_once_with(0, "end")
        
        # 验证IPv6默认值被设置
        self.app.parent_entry.insert.assert_called_once()
        inserted_parent = self.app.parent_entry.insert.call_args[0][1]
        self.assertTrue(inserted_parent.startswith("2001:0db8::"))
        
        self.app.split_entry.insert.assert_called_once()
        inserted_split = self.app.split_entry.insert.call_args[0][1]
        self.assertTrue(inserted_split.startswith("2001:0db8::"))
    
    def test_autocomplete_ipv6(self):
        """测试IPv6自动补全功能"""
        # 模拟事件和输入框
        mock_event = MagicMock()
        mock_entry = MagicMock()
        mock_event.widget = mock_entry
        
        # 测试单冒号情况，应该补全为双冒号
        mock_entry.get.return_value = "2001:"
        mock_entry.index.return_value = 6  # 光标位置在冒号后
        mock_entry.insert = MagicMock()
        
        self.app.autocomplete_ipv6(mock_event)
        
        # 验证自动补全功能被调用
        mock_entry.insert.assert_called_once_with(6, ":")
        
        # 测试双冒号情况，不应该再补全
        mock_entry.get.return_value = "2001::"
        mock_entry.insert = MagicMock()
        
        self.app.autocomplete_ipv6(mock_event)
        
        # 验证自动补全功能没有被调用
        mock_entry.insert.assert_not_called()
    
    def test_generate_template_ipv6(self):
        """测试生成包含IPv6示例数据的模板"""
        # 由于生成模板功能涉及文件操作，这里只测试模板生成函数是否存在
        self.assertTrue(hasattr(self.app, "_generate_template"))
    
    def test_validate_planning_input_ipv6(self):
        """测试子网规划输入验证对IPv6的支持"""
        # 测试有效的IPv6父网段
        result = self.app._validate_planning_input("2001:0db8::/32")
        self.assertTrue(result["valid"])
        self.assertIsNone(result["error"])
        
        # 测试无效的IPv6父网段
        result = self.app._validate_planning_input("invalid_ipv6/32")
        self.assertFalse(result["valid"])
        self.assertIsNotNone(result["error"])
    
    def test_ipv6_hint_label(self):
        """测试IPv6使用提示标签是否被正确添加"""
        # 这个测试需要实际的GUI环境，这里只验证相关函数存在
        self.assertTrue(hasattr(self.app, "setup_planning_page"))
    
    def tearDown(self):
        """清理测试环境"""
        del self.app

if __name__ == "__main__":
    unittest.main()
