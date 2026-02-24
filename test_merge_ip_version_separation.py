#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试子网合并功能的IP版本分离
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import merge_subnets, get_subnet_info

print("测试子网合并功能的IP版本分离")
print("=" * 60)

# 测试用例：混合IPv4和IPv6子网
subnets = [
    "192.168.0.0/24",
    "192.168.1.0/24",
    "192.168.2.0/24",
    "10.21.16.0/24",
    "10.21.17.0/24",
    "10.21.18.0/24",
    "10.21.19.128/26",
    "10.21.19.192/26",
    "2001:0db8::/127",
    "2001:0db8::2/127",
    "2001:0db8::4/127",
    "2001:0db8::6/127",
    "2001:0db8:1::/64",
    "2001:0db8:2::/64",
    "2001:0db8:3::/64",
]

print("输入子网列表：")
for subnet in subnets:
    print(f"  {subnet}")

# 执行合并
print("\n执行子网合并...")
result = merge_subnets(subnets)

if isinstance(result, dict) and "error" in result:
    print(f"❌ 合并失败: {result['error']}")
    sys.exit(1)

merged_subnets = result.get("merged_subnets", [])
print(f"\n合并结果：")
for subnet in merged_subnets:
    print(f"  {subnet}")

# 测试IP版本分离
print("\n\n测试IP版本分离：")
print("=" * 60)

ipv4_results = []
ipv6_results = []

for subnet in merged_subnets:
    info = get_subnet_info(subnet)
    print(f"子网: {subnet}, 版本: {info['version']} ({type(info['version']).__name__})")
    if info["version"] == 4:  # 使用整数比较
        ipv4_results.append((subnet, info))
    elif info["version"] == 6:  # 使用整数比较
        ipv6_results.append((subnet, info))
    else:
        print(f"❌ 未知IP版本: {info['version']}")

print(f"\n分离结果：")
print(f"IPv4结果数量: {len(ipv4_results)}")
print(f"IPv6结果数量: {len(ipv6_results)}")

print("\nIPv4结果：")
for subnet, info in ipv4_results:
    print(f"  {subnet}")

print("\nIPv6结果：")
for subnet, info in ipv6_results:
    print(f"  {subnet}")

# 验证分离是否正确
all_ipv4 = all(info["version"] == 4 for subnet, info in ipv4_results)
all_ipv6 = all(info["version"] == 6 for subnet, info in ipv6_results)

if all_ipv4 and all_ipv6:
    print("\n✅ IP版本分离正确")
else:
    print("\n❌ IP版本分离错误")
    if not all_ipv4:
        print("   IPv4结果中包含非IPv4子网")
    if not all_ipv6:
        print("   IPv6结果中包含非IPv6子网")

print("\n测试完成！")
