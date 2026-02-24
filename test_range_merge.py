#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import ipaddress

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import range_to_cidr  # noqa: E402


def test_range_to_cidr_merge():
    """测试range_to_cidr函数的合并行为"""
    print("测试range_to_cidr函数的合并行为...")
    
    # 测试用例1: 从192.168.0.1到192.168.30.254
    print("\n测试1: 从192.168.0.1到192.168.30.254")
    result = range_to_cidr("192.168.0.1", "192.168.30.254")
    print(f"CIDR列表: {result['cidr_list']}")
    print(f"CIDR数量: {result['cidr_count']}")
    
    # 测试用例2: 从192.168.0.0到192.168.31.255（完整的/21子网）
    print("\n测试2: 从192.168.0.0到192.168.31.255")
    result = range_to_cidr("192.168.0.0", "192.168.31.255")
    print(f"CIDR列表: {result['cidr_list']}")
    print(f"CIDR数量: {result['cidr_count']}")
    
    # 测试用例3: 使用ipaddress模块直接测试summarize_address_range
    print("\n测试3: 使用ipaddress.summarize_address_range直接测试")
    start = ipaddress.IPv4Address("192.168.0.1")
    end = ipaddress.IPv4Address("192.168.30.254")
    cidr_list = list(ipaddress.summarize_address_range(start, end))
    print(f"CIDR列表: {[str(cidr) for cidr in cidr_list]}")
    print(f"CIDR数量: {len(cidr_list)}")
    
    # 测试用例4: 从192.168.0.0到192.168.0.255（完整的/24子网）
    print("\n测试4: 从192.168.0.0到192.168.0.255")
    result = range_to_cidr("192.168.0.0", "192.168.0.255")
    print(f"CIDR列表: {result['cidr_list']}")
    print(f"CIDR数量: {result['cidr_count']}")
    
    # 测试用例5: 从192.168.0.1到192.168.0.255
    print("\n测试5: 从192.168.0.1到192.168.0.255")
    result = range_to_cidr("192.168.0.1", "192.168.0.255")
    print(f"CIDR列表: {result['cidr_list']}")
    print(f"CIDR数量: {result['cidr_count']}")


if __name__ == "__main__":
    test_range_to_cidr_merge()
