#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import range_to_cidr  # noqa: E402



def test_range_to_cidr():
    """测试range_to_cidr函数"""
    print("测试range_to_cidr函数...")
    
    # 测试用例1: 有效的IPv4范围
    print("\n测试1: 有效的IPv4范围")
    result = range_to_cidr("192.168.0.1", "192.168.0.100")
    print(f"结果: {result}")
    
    # 测试用例2: 有效的IPv6范围
    print("\n测试2: 有效的IPv6范围")
    result = range_to_cidr("2001:db8::1", "2001:db8::100")
    print(f"结果: {result}")
    
    # 测试用例3: 起始IP大于结束IP
    print("\n测试3: 起始IP大于结束IP")
    result = range_to_cidr("192.168.0.100", "192.168.0.1")
    print(f"结果: {result}")
    
    # 测试用例4: 不同类型的IPv6地址（全局地址和链路本地地址）
    print("\n测试4: 不同类型的IPv6地址（全局地址和链路本地地址）")
    result = range_to_cidr("2001:db8::1", "fe80::1")
    print(f"结果: {result}")
    
    # 测试用例5: 无效的IPv4地址
    print("\n测试5: 无效的IPv4地址")
    result = range_to_cidr("192.168.0.300", "192.168.0.100")
    print(f"结果: {result}")
    
    # 测试用例6: 无效的IPv6地址
    print("\n测试6: 无效的IPv6地址")
    result = range_to_cidr("2001:db8::g", "2001:db8::100")
    print(f"结果: {result}")
    
    # 测试用例7: 不同IP版本
    print("\n测试7: 不同IP版本")
    result = range_to_cidr("192.168.0.1", "2001:db8::1")
    print(f"结果: {result}")


if __name__ == "__main__":
    test_range_to_cidr()
