#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试IP子网错误处理的翻译功能
"""

# 导入模块
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from ip_subnet_calculator import handle_ip_subnet_error
from i18n import set_language, _


def test_error_translation():
    """
    测试各种错误情况的翻译
    """
    # 测试不同语言
    languages = ['zh', 'en', 'ja', 'zh_tw']
    
    # 模拟各种错误情况
    test_errors = [
        # (错误信息, 预期翻译键)
        ("'256.0.0.0' is not a valid netmask", 'invalid_subnet_mask'),
        ("'192.168.1.1/33' does not appear to be an IPv4 or IPv6 network", 'invalid_network_address_format'),
        ("'192.168.1.1/24' has host bits set", 'cidr_has_host_bits_set'),
        ("expected 4 octets, got 3", 'invalid_ip_format_4_octets'),
        ("octet 256 is invalid", 'invalid_octet_in_ip'),
        ("Only decimal digits permitted", 'invalid_ipv4_decimal_digits'),
        ("Unexpected '/'", 'invalid_ipv4_unexpected_slash'),
        ("'2001:0db8:85a3:0000:0000:8a2e:0370:7334:1234' does not appear to be an IPv6 address", 'invalid_ipv6_address_format'),
        ("at most 4 hex digits per group", 'invalid_ipv6_hex_digits'),
        ("too many colons", 'invalid_ipv6_too_many_colons'),
        ("Only hex digits permitted", 'invalid_ipv6_hex_only'),
        ("At most 3 characters permitted", 'invalid_ipv4_octet_too_long'),
        ("At most 4 characters permitted", 'invalid_ipv6_group_too_long'),
        ("At most 8 colons permitted", 'invalid_ipv6_too_many_colons'),
        ("At most 45 characters expected", 'invalid_ipv6_address_too_long'),
        ("At most 10 characters permitted", 'invalid_ipv6_characters_limit'),
        ("Trailing ':' only permitted as part of '::'", 'invalid_ipv6_trailing_colon'),
        ("Exactly 8 parts expected", 'invalid_ipv6_exactly_8_parts'),
        ("7 parts expected", 'invalid_ipv6_parts_count'),
        ("Expected at most 7 other parts with ':' in '2001:0db8:85a3:0000:0000:8a2e:0370::7334'", 'invalid_ipv6_parts_count'),
        ("Expected at most 7 other parts with \"in '2001:0db8:85a3:0000:0000:8a2e:0370::7334'", 'invalid_ipv6_parts_count'),
        ("Expected at most 7 other parts with \":\" in '2001:0db8:85a3:0000:0000:8a2e:0370::7334'", 'invalid_ipv6_parts_count'),
    ]
    
    for lang in languages:
        print(f"\n=== 测试语言: {lang} ===")
        set_language(lang)
        
        for error_msg, expected_key in test_errors:
            # 创建一个模拟的ValueError对象
            error = ValueError(error_msg)
            
            # 调用错误处理函数
            result = handle_ip_subnet_error(error)
            
            # 打印结果
            print(f"错误信息: {error_msg}")
            print(f"翻译结果: {result['error']}")
            print("-" * 50)


if __name__ == "__main__":
    test_error_translation()
