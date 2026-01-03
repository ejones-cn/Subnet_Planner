#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试国际化功能，不依赖于GUI库
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n import set_language, _, get_language, get_supported_languages

def test_i18n_simple():
    """简单测试国际化功能"""
    print("=== 简单测试国际化功能 ===")
    
    # 测试1: 测试语言设置和获取
    print("\n1. 测试语言设置和获取:")
    languages = ["zh", "en", "ja"]
    for lang_code in languages:
        set_language(lang_code)
        current_lang = get_language()
        print(f"   设置语言为 {lang_code}, 获取到的语言: {current_lang}")
        # 测试一些常用的翻译
        test_keys = ["app_name", "error", "ok", "cancel", "confirm", "export", "execute"]
        for key in test_keys:
            print(f"     {key}: {_(key)}")
    
    # 测试2: 测试支持的语言列表
    print("\n2. 测试支持的语言列表:")
    supported_langs = get_supported_languages()
    for lang_code, lang_name in supported_langs:
        print(f"   {lang_code}: {lang_name}")
    
    # 测试3: 测试带参数的翻译
    print("\n3. 测试带参数的翻译:")
    test_cases = [
        ("zh", "result_successfully_exported", {"file_path": "/test/path/result.txt"}),
        ("en", "result_successfully_exported", {"file_path": "/test/path/result.txt"}),
        ("ja", "result_successfully_exported", {"file_path": "/test/path/result.txt"}),
    ]
    for lang_code, key, kwargs in test_cases:
        set_language(lang_code)
        translated = _(key, **kwargs)
        print(f"   {lang_code} - {key}: {translated}")
    
    # 测试4: 模拟语言切换逻辑
    print("\n4. 模拟语言切换逻辑:")
    language_mapping = {
        "中文": "zh",
        "English": "en",
        "日本語": "ja"
    }
    
    for display_name, lang_code in language_mapping.items():
        # 模拟从下拉框选择语言
        selected_language = display_name
        # 模拟语言切换逻辑
        lang_code = language_mapping[selected_language]
        # 设置语言
        set_language(lang_code)
        print(f"   选择了 '{selected_language}', 设置语言为 {lang_code}, 翻译'app_name': {_("app_name")}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_i18n_simple()
