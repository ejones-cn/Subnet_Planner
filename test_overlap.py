#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试子网重叠检测的不同情况
"""

import ipaddress
from ip_subnet_calculator import check_subnet_overlap

# 直接使用ipaddress模块验证子网关系
print("=== 使用ipaddress模块验证子网关系 ===")

# 测试部分重叠的情况 - 使用有效的网络地址，严格模式为False
subnet1 = ipaddress.ip_network('192.168.0.0/24')
subnet2 = ipaddress.ip_network('192.168.0.128/25', strict=False)
subnet3 = ipaddress.ip_network('192.168.0.64/25', strict=False)
subnet4 = ipaddress.ip_network('192.168.1.0/24')

# 测试完全重叠
print("\n1. 完全重叠测试:")
print(f"   子网1: {subnet1}")
print(f"   子网2: {subnet1}")
print(f"   是否重叠: {subnet1.overlaps(subnet1)}")
print(f"   子网1包含于子网1: {subnet1.prefixlen <= subnet1.prefixlen and subnet1.network_address == subnet1.network_address}")

# 测试包含关系
print("\n2. 包含关系测试:")
print(f"   子网1: {subnet1} (/24)")
print(f"   子网2: {subnet2} (/25)")
print(f"   是否重叠: {subnet1.overlaps(subnet2)}")
print(f"   子网2包含于子网1: {subnet2.prefixlen >= subnet1.prefixlen and subnet1.network_address == subnet2.network_address}")
print(f"   子网1包含于子网2: {subnet1.prefixlen >= subnet2.prefixlen and subnet2.network_address == subnet1.network_address}")

# 测试相邻子网
print("\n3. 相邻子网测试:")
subnet5 = ipaddress.ip_network('192.168.0.0/25', strict=False)
subnet6 = ipaddress.ip_network('192.168.0.128/25', strict=False)
print(f"   子网5: {subnet5} (/25)")
print(f"   子网6: {subnet6} (/25)")
print(f"   是否重叠: {subnet5.overlaps(subnet6)}")
print(f"   子网5包含于子网6: {subnet5.prefixlen >= subnet6.prefixlen and subnet6.network_address == subnet5.network_address}")
print(f"   子网6包含于子网5: {subnet6.prefixlen >= subnet5.prefixlen and subnet5.network_address == subnet6.network_address}")

# 测试check_subnet_overlap函数
print("\n=== 测试check_subnet_overlap函数 ===")

# 测试包含关系
print("\n1. 包含关系测试:")
subnets_contained = ['192.168.0.0/24', '192.168.0.128/25']
result_contained = check_subnet_overlap(subnets_contained)
print(f"   子网列表: {subnets_contained}")
print(f"   检测结果: {result_contained}")

# 测试无重叠
print("\n2. 无重叠测试:")
subnets_no_overlap = ['192.168.0.0/24', '192.168.1.0/24']
result_no_overlap = check_subnet_overlap(subnets_no_overlap)
print(f"   子网列表: {subnets_no_overlap}")
print(f"   检测结果: {result_no_overlap}")

# 查看_check_overlaps_in_networks函数的实现
print("\n=== 查看重叠检测函数实现 ===")
print("   函数中定义了两种重叠类型:")
print("   1. 'partial overlap' - 部分重叠")
print("   2. 'contained in' - 包含关系")
