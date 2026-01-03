#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试语言切换功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from windows_app import SubnetPlannerApp
from i18n import set_language, _, get_language, get_supported_languages

class MockRoot:
    """模拟Tkinter根窗口类"""
    def __init__(self):
        self.title = lambda x: print(f"设置窗口标题: {x}")
        self.destroy = lambda: print("销毁窗口")
        self.after = lambda *args: None
        self.bind = lambda *args: None
        self.unbind = lambda *args: None

class MockEvent:
    """模拟事件类"""
    def __init__(self):
        self.widget = None

class MockCombobox:
    """模拟Combobox类"""
    def __init__(self):
        self.destroy = lambda: None


def test_language_switch():
    """测试语言切换功能"""
    print("=== 测试语言切换功能 ===")
    
    # 测试1: 直接测试语言设置和获取
    print("\n1. 测试语言设置和获取:")
    languages = ["zh", "en", "ja"]
    for lang_code in languages:
        set_language(lang_code)
        current_lang = get_language()
        print(f"   设置语言为 {lang_code}, 获取到的语言: {current_lang}, 翻译'app_name': {_("app_name")}")
    
    # 测试2: 测试支持的语言列表
    print("\n2. 测试支持的语言列表:")
    supported_langs = get_supported_languages()
    for lang_code, lang_name in supported_langs:
        print(f"   {lang_code}: {lang_name}")
    
    # 测试3: 模拟语言切换事件处理
    print("\n3. 模拟语言切换事件处理:")
    
    # 创建SubnetPlannerApp实例，但只初始化必要的部分
    app = SubnetPlannerApp()
    
    # 模拟根窗口
    app.root = MockRoot()
    
    # 模拟语言选择变量和下拉框
    app.language_var = type('obj', (object,), {'get': lambda: "日本語"})()
    app.language_combobox = MockCombobox()
    
    # 模拟应用名称和版本
    app.app_name = _("app_name")
    app.app_version = "1.0"
    
    # 模拟事件
    event = MockEvent()
    
    # 模拟窗口销毁方法
    app.destroy_all_widgets = lambda: print("销毁所有控件")
    
    # 测试语言切换
    print("   模拟选择日语...")
    app.on_language_change(event)
    print(f"   切换后语言: {get_language()}, 翻译'app_name': {_("app_name")}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_language_switch()
