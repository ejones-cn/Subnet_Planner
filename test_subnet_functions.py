#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试子网切分和规划功能
"""

# 导入必要的模块
from ip_subnet_calculator import split_subnet, suggest_subnet_planning


def test_split_subnet():
    """测试子网切分功能"""
    print("\n=== 测试子网切分功能 ===")
    
    # 测试用例1: 基本切分
    print("\n测试用例1: 基本切分")
    parent = "192.168.1.0/24"
    split = "192.168.1.0/25"
    result = split_subnet(parent, split)
    print(f"父网段: {parent}")
    print(f"切分网段: {split}")
    print(f"结果: {result}")
    
    # 测试用例2: 切分后的子网
    print("\n测试用例2: 切分后的子网")
    parent = "192.168.1.0/25"
    split = "192.168.1.0/26"
    result = split_subnet(parent, split)
    print(f"父网段: {parent}")
    print(f"切分网段: {split}")
    print(f"结果: {result}")
    
    # 测试用例3: 边界情况
    print("\n测试用例3: 边界情况")
    parent = "10.0.0.0/8"
    split = "10.0.0.0/16"
    result = split_subnet(parent, split)
    print(f"父网段: {parent}")
    print(f"切分网段: {split}")
    print(f"剩余网段数量: {len(result.get('remaining_subnets_info', []))}")


def test_subnet_planning():
    """测试子网规划功能"""
    print("\n=== 测试子网规划功能 ===")
    
    # 测试用例1: 基本规划
    print("\n测试用例1: 基本规划")
    parent_cidr = "192.168.1.0/24"
    requirements = [
        {'name': '子网A', 'hosts': 100},
        {'name': '子网B', 'hosts': 50},
        {'name': '子网C', 'hosts': 25}
    ]
    result = suggest_subnet_planning(parent_cidr, requirements)
    print(f"父网段: {parent_cidr}")
    print(f"需求: {requirements}")
    print(f"已分配子网数量: {len(result.get('allocated_subnets', []))}")
    print(f"剩余网段数量: {len(result.get('remaining_subnets_info', []))}")
    
    # 测试用例2: 复杂规划
    print("\n测试用例2: 复杂规划")
    parent_cidr = "10.0.0.0/16"
    requirements = [
        {'name': '子网1', 'hosts': 500},
        {'name': '子网2', 'hosts': 200},
        {'name': '子网3', 'hosts': 100},
        {'name': '子网4', 'hosts': 50},
        {'name': '子网5', 'hosts': 25},
        {'name': '子网6', 'hosts': 12},
        {'name': '子网7', 'hosts': 6},
        {'name': '子网8', 'hosts': 2}
    ]
    result = suggest_subnet_planning(parent_cidr, requirements)
    print(f"父网段: {parent_cidr}")
    print(f"需求: {[req['name'] + ':' + str(req['hosts']) for req in requirements]}")
    print(f"已分配子网数量: {len(result.get('allocated_subnets', []))}")
    print(f"剩余网段数量: {len(result.get('remaining_subnets_info', []))}")
    
    # 测试用例3: 资源不足情况
    print("\n测试用例3: 资源不足情况")
    parent_cidr = "192.168.1.0/25"  # 只有126个可用地址
    requirements = [
        {'name': '子网A', 'hosts': 100},
        {'name': '子网B', 'hosts': 100}  # 总共需要200个地址，超过可用地址
    ]
    result = suggest_subnet_planning(parent_cidr, requirements)
    print(f"父网段: {parent_cidr}")
    print(f"需求: {requirements}")
    print(f"结果: {result}")


if __name__ == "__main__":
    test_split_subnet()
    test_subnet_planning()
    print("\n=== 所有测试完成 ===")
