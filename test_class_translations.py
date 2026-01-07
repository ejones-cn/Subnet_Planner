#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试class相关翻译的脚本
"""

from i18n import _, set_language

def test_class_translations():
    """测试class相关翻译"""
    # 测试韩语翻译
    set_language("ko")
    print("=== 测试韩语Class翻译 ===")
    
    # 测试class相关的翻译
    test_keys = [
        "class_a",
        "class_b",
        "class_c",
        "class_d",
        "class_e"
    ]
    
    for key in test_keys:
        translated = _(key)
        print(f"{key}: {translated}")
        # 检查翻译是否正确
        if "클래스" not in translated:
            print(f"  警告: {key} 翻译不正确")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_class_translations()
