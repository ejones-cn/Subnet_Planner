#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试无效子网的错误处理
"""

from ip_subnet_calculator import check_subnet_overlap, merge_subnets

# 测试无效子网的情况
print("=== 测试无效子网的错误处理 ===")

# 测试用例1：单个无效子网
print("\n1. 测试单个无效子网:")
subnets1 = ['192.168.0.0/24', 'invalid_subnet']
result1 = check_subnet_overlap(subnets1)
print(f"   子网列表: {subnets1}")
print(f"   检测结果: {result1}")
print(f"   是否包含invalid_subnets字段: {'invalid_subnets' in result1}")

# 测试用例2：多个无效子网
print("\n2. 测试多个无效子网:")
subnets2 = ['invalid_subnet1', 'invalid_subnet2', '192.168.0.0/24']
result2 = check_subnet_overlap(subnets2)
print(f"   子网列表: {subnets2}")
print(f"   检测结果: {result2}")
print(f"   是否包含invalid_subnets字段: {'invalid_subnets' in result2}")
if 'invalid_subnets' in result2:
    invalid_subnets = result2['invalid_subnets']
    # 添加类型检查，确保是可迭代类型
    if isinstance(invalid_subnets, (list, tuple, str)):
        print(f"   无效子网数量: {len(invalid_subnets)}")
    else:
        print(f"   无效子网信息: {invalid_subnets}")

# 测试用例3：无效子网格式（缺少前缀）
print("\n3. 测试无效子网格式（缺少前缀）:")
subnets3 = ['192.168.0.0', '192.168.1.0/24']
result3 = check_subnet_overlap(subnets3)
print(f"   子网列表: {subnets3}")
print(f"   检测结果: {result3}")

# 测试用例4：无效子网格式（无效前缀）
print("\n4. 测试无效子网格式（无效前缀）:")
subnets4 = ['192.168.0.0/33', '192.168.1.0/24']
result4 = check_subnet_overlap(subnets4)
print(f"   子网列表: {subnets4}")
print(f"   检测结果: {result4}")

# 测试merge_subnets函数的错误处理
print("\n=== 测试merge_subnets函数的错误处理 ===")
subnets5 = ['invalid_subnet', '192.168.0.0/24']
result5 = merge_subnets(subnets5)
print(f"   子网列表: {subnets5}")
print(f"   检测结果: {result5}")
print(f"   是否包含invalid_subnets字段: {'invalid_subnets' in result5}")
