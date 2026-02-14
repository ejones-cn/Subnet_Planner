#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IPv6功能测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import (
    split_subnet,
    get_subnet_info,
    suggest_subnet_planning,
    merge_subnets,
    check_subnet_overlap,
    range_to_cidr,
    get_ip_info
)

def test_split_subnet_ipv6():
    """测试IPv6子网切分功能"""
    print("=== 测试IPv6子网切分功能 ===")
    
    # 测试1：从大子网切分小子网
    result = split_subnet("2001:0db8::/32", "2001:0db8:1::/64")
    print(f"测试1 - 从2001:0db8::/32切分2001:0db8:1::/64")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，剩余子网数量: {len(result['remaining_subnets'])}")
        print(f"  剩余子网示例: {result['remaining_subnets'][:3]}...")
    
    # 测试2：切分相同子网
    result = split_subnet("2001:0db8::/64", "2001:0db8::/64")
    print(f"\n测试2 - 切分相同子网2001:0db8::/64")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，剩余子网数量: {len(result['remaining_subnets'])}")
    
    # 测试3：切分非子网
    result = split_subnet("2001:0db8::/64", "2001:0dc8::/64")
    print(f"\n测试3 - 切分非子网2001:0dc8::/64")
    if "error" in result:
        print(f"  预期错误: {result['error']}")
    else:
        print(f"  意外成功")

def test_get_subnet_info_ipv6():
    """测试IPv6子网信息获取功能"""
    print("\n=== 测试IPv6子网信息获取功能 ===")
    
    # 测试1：标准IPv6子网
    result = get_subnet_info("2001:0db8::/64")
    print(f"测试1 - 获取2001:0db8::/64的信息")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  网络地址: {result['network']}")
        print(f"  子网掩码: {result['netmask']}")
        print(f"  可用地址数: {result['usable_addresses']}")
        print(f"  IP版本: {result['version']}")
    
    # 测试2：/128子网
    result = get_subnet_info("2001:0db8::1/128")
    print(f"\n测试2 - 获取2001:0db8::1/128的信息")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  网络地址: {result['network']}")
        print(f"  可用地址数: {result['usable_addresses']}")
        print(f"  IP版本: {result['version']}")

def test_suggest_subnet_planning_ipv6():
    """测试IPv6子网规划功能"""
    print("\n=== 测试IPv6子网规划功能 ===")
    
    parent_cidr = "2001:0db8::/48"
    required_subnets = [
        {"name": "部门A", "hosts": 1000},
        {"name": "部门B", "hosts": 500},
        {"name": "部门C", "hosts": 200}
    ]
    
    result = suggest_subnet_planning(parent_cidr, required_subnets)
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，分配了 {len(result['allocated_subnets'])} 个子网")
        for subnet in result['allocated_subnets']:
            print(f"    {subnet['name']}: {subnet['cidr']} (可用: {subnet['available_hosts']})")
        print(f"  IP版本: {result['ip_version']}")

def test_merge_subnets_ipv6():
    """测试IPv6子网合并功能"""
    print("\n=== 测试IPv6子网合并功能 ===")
    
    # 测试1：合并连续子网
    subnets = [
        "2001:0db8:1::/64",
        "2001:0db8:2::/64",
        "2001:0db8:3::/64"
    ]
    result = merge_subnets(subnets)
    print(f"测试1 - 合并连续子网")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
        print(f"  合并结果: {result['merged_subnets']}")
        print(f"  IP版本: {result['ip_version']}")
    
    # 测试2：合并可聚合子网
    subnets = [
        "2001:0db8:1:0::/66",
        "2001:0db8:1:1000::/66"
    ]
    result = merge_subnets(subnets)
    print(f"\n测试2 - 合并可聚合子网")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，合并前: {result['original_count']}个，合并后: {result['merged_count']}个")
        print(f"  合并结果: {result['merged_subnets']}")

def test_check_subnet_overlap_ipv6():
    """测试IPv6子网重叠检查功能"""
    print("\n=== 测试IPv6子网重叠检查功能 ===")
    
    # 测试1：有重叠子网
    subnets = [
        "2001:0db8::/64",
        "2001:0db8::1000/120"
    ]
    result = check_subnet_overlap(subnets)
    print(f"测试1 - 检查有重叠的子网")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，重叠数量: {result['overlap_count']}")
        print(f"  重叠类型: {[o['type'] for o in result['overlaps']]}")
        print(f"  IP版本: {result['ip_version']}")
    
    # 测试2：无重叠子网
    subnets = [
        "2001:0db8:1::/64",
        "2001:0db8:2::/64"
    ]
    result = check_subnet_overlap(subnets)
    print(f"\n测试2 - 检查无重叠的子网")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，重叠数量: {result['overlap_count']}")

def test_range_to_cidr_ipv6():
    """测试IPv6地址范围转CIDR功能"""
    print("\n=== 测试IPv6地址范围转CIDR功能 ===")
    
    # 测试1：完整子网范围
    result = range_to_cidr("2001:0db8::1", "2001:0db8::ffff")
    print(f"测试1 - 将2001:0db8::1-2001:0db8::ffff转为CIDR")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  成功，转换为 {result['cidr_count']} 个CIDR")
        print(f"  结果: {result['cidr_list']}")
        print(f"  IP版本: {result['ip_version']}")

def test_get_ip_info_ipv6():
    """测试IPv6地址信息获取功能"""
    print("\n=== 测试IPv6地址信息获取功能 ===")
    
    # 测试1：IPv6地址
    result = get_ip_info("2001:0db8::1")
    print(f"测试1 - 获取2001:0db8::1的信息")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  IP版本: {result['version']}")
        print(f"  压缩格式: {result['compressed']}")
        print(f"  扩展格式: {result['exploded']}")
        print(f"  地址类型: {result['address_type']}")
    
    # 测试2：IPv6网络
    result = get_ip_info("2001:0db8::/64")
    print(f"\n测试2 - 获取2001:0db8::/64的网络信息")
    if "error" in result:
        print(f"  错误: {result['error']}")
    else:
        print(f"  IP版本: {result['version']}")
        print(f"  网络地址: {result['network_address']}")
        print(f"  可用主机数: {result['usable_hosts']}")

def run_all_tests():
    """运行所有IPv6测试"""
    print("开始IPv6功能测试...\n")
    
    test_get_subnet_info_ipv6()
    test_split_subnet_ipv6()
    test_suggest_subnet_planning_ipv6()
    test_merge_subnets_ipv6()
    test_check_subnet_overlap_ipv6()
    test_range_to_cidr_ipv6()
    test_get_ip_info_ipv6()
    
    print("\n=== 所有测试完成 ===")

if __name__ == "__main__":
    run_all_tests()
