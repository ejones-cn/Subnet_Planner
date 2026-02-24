#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
详细测试IPv6子网合并功能
"""

import sys
import os
import ipaddress

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import merge_subnets  # noqa: E402



def test_merge_ipv6():
    """详细测试IPv6子网合并"""
    print("=== 详细测试IPv6子网合并功能 ===")
    
    # 测试1：合并三个连续的/64子网
    print("\n测试1：合并三个连续的/64子网")
    subnets = [
        "2001:0db8:1::/64",
        "2001:0db8:2::/64",
        "2001:0db8:3::/64"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
    
    # 测试2：合并两个可以合并的/66子网
    print("\n测试2：合并两个可以合并的/66子网")
    subnets = [
        "2001:0db8:1:0::/66",
        "2001:0db8:1:1000::/66"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
    
    # 测试3：合并四个连续的/65子网
    print("\n测试3：合并四个连续的/65子网")
    subnets = [
        "2001:0db8:1:0::/65",
        "2001:0db8:1:8000::/65",
        "2001:0db8:2:0::/65",
        "2001:0db8:2:8000::/65"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
    
    # 测试4：合并两个相邻的/120子网
    print("\n测试4：合并两个相邻的/120子网")
    subnets = [
        "2001:0db8::1000/120",
        "2001:0db8::2000/120"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")


if __name__ == "__main__":
    test_merge_ipv6()
