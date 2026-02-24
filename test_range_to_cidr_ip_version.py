#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试IP范围转CIDR功能的IP版本分离
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ip_subnet_calculator import range_to_cidr, get_subnet_info

print("测试IP范围转CIDR功能的IP版本分离")
print("=" * 60)

# 测试用例1：IPv4范围
print("\n测试用例1：IPv4范围")
print("-" * 40)
start_ip = "192.168.0.1"
end_ip = "192.168.30.254"
print(f"IP范围: {start_ip} - {end_ip}")

result = range_to_cidr(start_ip, end_ip)
if isinstance(result, dict) and "error" in result:
    print(f"❌ 转换失败: {result['error']}")
else:
    cidr_list = result.get("cidr_list", [])
    print(f"转换结果: {cidr_list}")
    
    # 测试IP版本分离
    ipv4_cidrs = []
    ipv6_cidrs = []
    
    for cidr in cidr_list:
        info = get_subnet_info(cidr)
        print(f"  子网: {cidr}, 版本: {info['version']} ({type(info['version']).__name__})")
        if info["version"] == 4:  # 使用整数比较
            ipv4_cidrs.append(cidr)
        elif info["version"] == 6:  # 使用整数比较
            ipv6_cidrs.append(cidr)
    
    print(f"\n分离结果：")
    print(f"  IPv4结果数量: {len(ipv4_cidrs)}")
    print(f"  IPv6结果数量: {len(ipv6_cidrs)}")
    
    if len(ipv4_cidrs) == len(cidr_list) and len(ipv6_cidrs) == 0:
        print("✅ IPv4范围转换结果正确分离到IPv4结果")
    else:
        print("❌ IPv4范围转换结果分离错误")

# 测试用例2：IPv6范围
print("\n\n测试用例2：IPv6范围")
print("-" * 40)
start_ip = "2001:0db8::1"
end_ip = "2001:0db8::100"
print(f"IP范围: {start_ip} - {end_ip}")

result = range_to_cidr(start_ip, end_ip)
if isinstance(result, dict) and "error" in result:
    print(f"❌ 转换失败: {result['error']}")
else:
    cidr_list = result.get("cidr_list", [])
    print(f"转换结果: {cidr_list}")
    
    # 测试IP版本分离
    ipv4_cidrs = []
    ipv6_cidrs = []
    
    for cidr in cidr_list:
        info = get_subnet_info(cidr)
        print(f"  子网: {cidr}, 版本: {info['version']} ({type(info['version']).__name__})")
        if info["version"] == 4:  # 使用整数比较
            ipv4_cidrs.append(cidr)
        elif info["version"] == 6:  # 使用整数比较
            ipv6_cidrs.append(cidr)
    
    print(f"\n分离结果：")
    print(f"  IPv4结果数量: {len(ipv4_cidrs)}")
    print(f"  IPv6结果数量: {len(ipv6_cidrs)}")
    
    if len(ipv6_cidrs) == len(cidr_list) and len(ipv4_cidrs) == 0:
        print("✅ IPv6范围转换结果正确分离到IPv6结果")
    else:
        print("❌ IPv6范围转换结果分离错误")

print("\n\n测试完成！")
