#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ipaddress
from ip_subnet_calculator import handle_ip_subnet_error

# 测试无效的IPv4地址（全面测试各种边界情况）
invalid_ipv4_addresses = [
    # 八位组过长
    "192.168.1.1111",  # 单个八位组过长
    "192.168.1111.1",  # 第三个八位组过长
    "1111.168.1.1",    # 第一个八位组过长
    
    # 缺少八位组
    "192.168.1",       # 缺少第四个八位组
    "192.168",          # 缺少后两个八位组
    "192",              # 缺少后三个八位组
    
    # 八位组值超过255
    "192.168.1.256",   # 第四个八位组超过255
    "192.168.256.1",   # 第三个八位组超过255
    "192.256.1.1",     # 第二个八位组超过255
    "256.168.1.1",     # 第一个八位组超过255
    
    # 包含无效字符
    "abc.def.ghi.jkl",  # 包含字母
    "192.168.1.abc",   # 最后一个八位组包含字母
    "192.168.abc.1",   # 第三个八位组包含字母
    "192.abc.1.1",     # 第二个八位组包含字母
    "abc.168.1.1",     # 第一个八位组包含字母
    
    # 包含特殊字符
    "192.168.1.1/33",  # 包含斜杠
    "192.168.1.1.",    # 末尾有点号
    ".192.168.1.1",    # 开头有点号
    "192..168.1.1",    # 连续点号
    
    # 其他无效格式
    "",                 # 空字符串
    "123456789",       # 纯数字
    "invalid_ip",       # 纯文本
]

# 测试无效的IPv6地址
invalid_ipv6_addresses = [
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334:7777",  # 超过8个部分
    "2001:0db8:85a3:0000:0000:8a2e:0370",           # 少于8个部分
    "2001:0db8:85a3:0000:0000:8a2e:0370::7334::123",# 多个双冒号
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334:1234",# 9个部分
    "2001:0db8:85a3:0000:0000:8a2e:0370:z334",      # 包含无效字符
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334:",     # 末尾有冒号
    ":2001:0db8:85a3:0000:0000:8a2e:0370:7334",     # 开头有冒号
    "2001::0db8::85a3::0000::0000::8a2e::0370::7334",# 过多双冒号
]

print("=== 全面测试IP错误处理 ===\n")

print("1. 测试无效IPv4地址错误处理:")
print("-" * 50)
for ip in invalid_ipv4_addresses:
    print(f"\n测试IP: {ip}")
    try:
        ipaddress.IPv4Address(ip)
        print("✓ 有效IP")
    except ValueError as e:
        error_msg = str(e)
        print(f"✗ 无效IP")
        print(f"  原始错误: {error_msg}")
        # 调用错误处理函数
        error_info = handle_ip_subnet_error(e, "IP地址验证")
        print(f"  处理后错误: {error_info['error']}")
        # 检查是否错误地返回了IPv6错误
        if "IPv6" in error_info['error']:
            print(f"  ❌ 错误：IPv4地址返回了IPv6错误信息！")
        else:
            print(f"  ✅ 正确：返回了IPv4相关错误信息")

print("\n\n2. 测试无效IPv6地址错误处理:")
print("-" * 50)
for ip in invalid_ipv6_addresses:
    print(f"\n测试IP: {ip}")
    try:
        ipaddress.IPv6Address(ip)
        print("✓ 有效IP")
    except ValueError as e:
        error_msg = str(e)
        print(f"✗ 无效IP")
        print(f"  原始错误: {error_msg}")
        # 调用错误处理函数
        error_info = handle_ip_subnet_error(e, "IP地址验证")
        print(f"  处理后错误: {error_info['error']}")
        # 检查是否正确返回了IPv6错误
        if "IPv6" in error_info['error']:
            print(f"  ✅ 正确：返回了IPv6相关错误信息")
        else:
            print(f"  ❌ 错误：IPv6地址没有返回IPv6错误信息！")

print("\n\n=== 测试完成 ===")