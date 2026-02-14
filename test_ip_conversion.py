#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试IP地址转换功能
"""

from ip_subnet_calculator import ip_to_int, int_to_ip

# 测试IPv4地址转换
print("=== 测试IPv4地址转换 ===")
ipv4_addr = "192.168.1.1"
ipv4_int = ip_to_int(ipv4_addr)
print(f"IPv4地址 {ipv4_addr} 转换为整数: {ipv4_int}")
converted_back = int_to_ip(ipv4_int)
print(f"整数 {ipv4_int} 转换回IPv4地址: {converted_back}")
print(f"转换是否正确: {ipv4_addr == converted_back}")

# 测试IPv6地址转换
print("\n=== 测试IPv6地址转换 ===")
ipv6_addr = "2001:0db8::1"
try:
    ipv6_int = ip_to_int(ipv6_addr)
    print(f"IPv6地址 {ipv6_addr} 转换为整数: {ipv6_int}")
    converted_back = int_to_ip(ipv6_int)
    print(f"整数 {ipv6_int} 转换回IPv6地址: {converted_back}")
    print(f"转换是否正确: {ipv6_addr == converted_back or ipv6_addr.lower() == converted_back.lower()}")
except Exception as e:
    print(f"转换错误: {e}")
