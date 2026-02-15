#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试IPv6 /127子网可用地址计算
"""

from ip_subnet_calculator import get_subnet_info


def test_ipv6_127_subnet():
    """测试IPv6 /127子网可用地址计算"""
    print("=== 测试IPv6 /127子网可用地址计算 ===")
    
    # 测试/127子网
    cidr = "2001:db8::/127"
    result = get_subnet_info(cidr)
    
    print(f"CIDR: {cidr}")
    print(f"网络地址: {result['network']}")
    print(f"广播地址: {result['broadcast']}")
    print(f"可用地址数: {result['usable_addresses']}")
    print(f"地址范围: {result['host_range_start']} - {result['host_range_end']}")
    
    # 验证结果
    if result['usable_addresses'] == 2:
        print("✅ 测试通过: /127子网可用地址数为2")
    else:
        print(f"❌ 测试失败: 预期可用地址数为2，实际为{result['usable_addresses']}")
    
    if result['host_range_start'] == "2001:db8::" and result['host_range_end'] == "2001:db8::1":
        print("✅ 测试通过: 地址范围正确")
    else:
        print(f"❌ 测试失败: 预期地址范围为'2001:db8:: - 2001:db8::1'，实际为'{result['host_range_start']} - {result['host_range_end']}'")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_ipv6_127_subnet()
