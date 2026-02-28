#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试IPAMSQLite类的功能
"""

from ipam_sqlite import IPAMSQLite

# 初始化IPAMSQLite实例
ipam = IPAMSQLite()

print("=== 测试IPAMSQLite功能 ===")

# 测试1: 获取所有网络
print("\n1. 测试获取所有网络:")
networks = ipam.get_all_networks()
print(f"网络数量: {len(networks)}")
for network in networks:
    print(f"  - {network['network']}: {network['description']} (IP数量: {network['ip_count']})")

# 测试2: 获取网络IP地址
print("\n2. 测试获取网络IP地址:")
for network in networks:
    ips = ipam.get_network_ips(network['network'])
    print(f"  网络 {network['network']} 有 {len(ips)} 个IP地址")
    if len(ips) > 0:
        for i, ip in enumerate(ips[:3]):  # 只显示前3个
            print(f"    {i+1}. {ip['ip_address']} - {ip['status']} - {ip['hostname']}")
        if len(ips) > 3:
            print(f"    ... 还有 {len(ips) - 3} 个IP地址")

# 测试3: 获取整体统计信息
print("\n3. 测试获取整体统计信息:")
stats = ipam.get_overall_stats()
print(f"  总网络数: {stats['total_networks']}")
print(f"  总IP数: {stats['total_ips']}")
print(f"  已分配IP数: {stats['allocated_ips']}")
print(f"  已保留IP数: {stats['reserved_ips']}")
print(f"  过期IP数: {stats['expired_ips']}")
print(f"  IPv4网络数: {stats['ipv4_networks']}")
print(f"  IPv6网络数: {stats['ipv6_networks']}")

# 测试4: 测试最具体网络检测
print("\n4. 测试最具体网络检测:")
test_ips = ["10.0.2.5", "10.0.3.7", "192.168.1.10"]
for ip in test_ips:
    network = ipam.get_most_specific_network(ip)
    if network:
        print(f"  IP {ip} 最具体的网络是: {network['network_address']}")
    else:
        print(f"  IP {ip} 没有找到归属网络")

print("\n=== 测试完成 ===")
