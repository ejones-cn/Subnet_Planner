#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试翻译文件的脚本
"""

from i18n import _, set_language, get_supported_languages

def test_translations():
    """测试翻译功能"""
    # 测试英语翻译
    set_language("en")
    print("=== 测试英语翻译 ===")
    
    # 测试IP验证相关的翻译
    test_keys = [
        "invalid_ipv4_address_format",
        "invalid_ipv4_decimal_digits",
        "invalid_ipv4_unexpected_slash",
        "invalid_ipv6_address_format",
        "invalid_ipv6_hex_digits",
        "invalid_ipv6_too_many_colons",
        "invalid_ipv6_hex_only",
        "invalid_ipv4_octet_too_long",
        "invalid_ipv6_characters_limit",
        "invalid_ipv6_format",
        "invalid_ipv6_group_too_long",
        "invalid_ipv6_address_too_long",
        "invalid_ipv6_trailing_colon",
        "invalid_ipv6_exactly_8_parts"
    ]
    
    for key in test_keys:
        translated = _(key)
        print(f"{key}: {translated}")
        # 检查翻译是否包含例子
        if "(e.g.," not in translated:
            print(f"  警告: {key} 缺少例子")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_translations()
