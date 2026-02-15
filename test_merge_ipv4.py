#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试IPv4子网合并功能
"""

import sys
import os
import ipaddress

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import merge_subnets  # noqa: E402



def test_merge_ipv4():
    """测试IPv4子网合并功能"""
    print("=== 测试IPv4子网合并功能 ===")
    
    # 测试1：合并两个连续的/30子网
    print("\n测试1：合并两个连续的/30子网")
    subnets = [
        "192.168.1.0/30",
        "192.168.1.4/30"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}, 地址数量={net.num_addresses}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
    
    # 测试2：合并四个连续的/29子网
    print("\n测试2：合并四个连续的/29子网")
    subnets = [
        "192.168.1.0/29",
        "192.168.1.8/29",
        "192.168.1.16/29",
        "192.168.1.24/29"
    ]
    
    # 计算每个子网的网络地址和广播地址
    for subnet in subnets:
        net = ipaddress.ip_network(subnet, strict=False)
        print(f"{subnet}: 网络地址={net.network_address}, 广播地址={net.broadcast_address}, 地址数量={net.num_addresses}")
    
    result = merge_subnets(subnets)
    print(f"合并结果: {result['merged_subnets']}")
    print(f"合并前: {result['original_count']}个，合并后: {result['merged_count']}个")


if __name__ == "__main__":
    test_merge_ipv4()
