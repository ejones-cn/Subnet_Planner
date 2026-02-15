#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单测试IPv6子网合并功能 - 使用真正可以合并的子网
"""

import sys
import os
import ipaddress

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import merge_subnets  # noqa: E402



def test_merge_ipv6_simple():
    """测试真正可以合并的IPv6子网"""
    print("=== 测试真正可以合并的IPv6子网 ===")
    
    # 测试1：合并两个连续的/127子网
    print("\n测试1：合并两个连续的/127子网")
    subnets = [
        "2001:0db8::/127",
        "2001:0db8::2/127"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}, 地址数量={net.num_addresses}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
    
    # 测试2：合并四个连续的/126子网
    print("\n测试2：合并四个连续的/126子网")
    subnets = [
        "2001:0db8::/126",
        "2001:0db8::4/126",
        "2001:0db8::8/126",
        "2001:0db8::c/126"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}, 地址数量={net.num_addresses}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")


if __name__ == "__main__":
    test_merge_ipv6_simple()
