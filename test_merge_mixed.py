#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试混合IPv4和IPv6子网合并功能
"""

import sys
import os
import ipaddress

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import merge_subnets  # noqa: E402



def test_merge_mixed():
    """测试混合IPv4和IPv6子网合并"""
    print("=== 测试混合IPv4和IPv6子网合并 ===")
    
    # 测试：混合IPv4和IPv6子网
    print("\n测试：混合IPv4和IPv6子网")
    subnets = [
        "192.168.0.0/24",
        "192.168.1.0/24",
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
    print(f"IP版本: {result['ip_version']}")
    print(f"IPv4合并后数量: {result['ipv4_merged_count']}")
    print(f"IPv6合并后数量: {result['ipv6_merged_count']}")
    
    # 测试：多个IPv4和多个IPv6子网
    print("\n测试：多个IPv4和多个IPv6子网")
    subnets = [
        "10.0.0.0/24",
        "10.0.1.0/24",
        "10.0.2.0/24",
        "10.0.3.0/24",
        "2001:0db8:1::/64",
        "2001:0db8:2::/64",
        "2001:0db8:3::/64",
        "2001:0db8:4::/64"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}, 地址数量={net.num_addresses}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
    print(f"IP版本: {result['ip_version']}")
    print(f"IPv4合并后数量: {result['ipv4_merged_count']}")
    print(f"IPv6合并后数量: {result['ipv6_merged_count']}")


if __name__ == "__main__":
    test_merge_mixed()
