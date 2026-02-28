#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPAM功能测试脚本
"""

from ipam import IPAM
from datetime import datetime, timedelta


def test_ipam_basic_operations():
    """测试IPAM基本操作"""
    print("开始测试IPAM基本操作...")
    
    # 创建IPAM实例
    ipam = IPAM("test_ipam_data.json")
    
    # 测试添加网络
    print("\n1. 测试添加网络:")
    # 测试IPv4网络
    success, message = ipam.add_network("192.168.1.0/24", "测试网络1")
    print(f"添加192.168.1.0/24: {success}, {message}")
    
    # 测试IPv6网络
    success, message = ipam.add_network("2001:db8::/32", "测试网络2")
    print(f"添加2001:db8::/32: {success}, {message}")
    
    # 测试添加重复网络
    success, message = ipam.add_network("192.168.1.0/24", "测试网络1")
    print(f"添加重复网络: {success}, {message}")
    
    # 测试分配IP
    print("\n2. 测试分配IP:")
    # 分配IPv4地址
    success, message = ipam.allocate_ip("192.168.1.0/24", "192.168.1.10", "host1", "测试主机1")
    print(f"分配192.168.1.10: {success}, {message}")
    
    # 分配IPv6地址
    success, message = ipam.allocate_ip("2001:db8::/32", "2001:db8::1", "host2", "测试主机2")
    print(f"分配2001:db8::1: {success}, {message}")
    
    # 测试分配已存在的IP
    success, message = ipam.allocate_ip("192.168.1.0/24", "192.168.1.10", "host1", "测试主机1")
    print(f"分配已存在的IP: {success}, {message}")
    
    # 测试获取网络IP
    print("\n3. 测试获取网络IP:")
    # 测试小网络
    ips = ipam.get_network_ips("192.168.1.0/24")
    print(f"192.168.1.0/24的IP数量: {len(ips)}")
    for ip in ips:
        print(f"  - {ip['ip_address']}: {ip['status']}, {ip['hostname']}")
    
    # 测试大网络（应该不会卡死）
    success, message = ipam.add_network("10.0.0.0/8", "大型网络")
    print(f"添加10.0.0.0/8: {success}, {message}")
    
    # 分配一个IP到大型网络
    success, message = ipam.allocate_ip("10.0.0.0/8", "10.0.0.1", "big-host", "大型网络主机")
    print(f"分配10.0.0.1: {success}, {message}")
    
    # 获取大型网络的IP（应该只返回已分配的IP）
    big_network_ips = ipam.get_network_ips("10.0.0.0/8")
    print(f"10.0.0.0/8的IP数量: {len(big_network_ips)}")
    for ip in big_network_ips:
        print(f"  - {ip['ip_address']}: {ip['status']}, {ip['hostname']}")
    
    # 测试释放IP
    print("\n4. 测试释放IP:")
    success, message = ipam.release_ip("192.168.1.0/24", "192.168.1.10")
    print(f"释放192.168.1.10: {success}, {message}")
    
    # 测试获取释放后的IP列表
    ips_after_release = ipam.get_network_ips("192.168.1.0/24")
    print(f"释放后192.168.1.0/24的IP数量: {len(ips_after_release)}")
    
    # 测试移除网络
    print("\n5. 测试移除网络:")
    # 先释放所有IP
    for ip in ipam.get_network_ips("2001:db8::/32"):
        ipam.release_ip("2001:db8::/32", ip['ip_address'])
    
    # 移除网络
    success, message = ipam.remove_network("2001:db8::/32")
    print(f"移除2001:db8::/32: {success}, {message}")
    
    # 测试备份和恢复
    print("\n6. 测试备份和恢复:")
    backup_path = ipam.backup_data(backup_name="test_backup", compress=True)
    print(f"备份到: {backup_path}")
    
    # 测试搜索功能（暂时跳过，需要实现search_ips方法）
    print("\n7. 测试搜索功能:")
    # 重新分配一个IP用于后续测试
    ipam.allocate_ip("192.168.1.0/24", "192.168.1.10", "test-host", "测试搜索主机")
    print("搜索功能测试暂时跳过，需要实现search_ips方法")
    
    # 测试统计功能
    print("\n8. 测试统计功能:")
    stats = ipam.get_network_stats("192.168.1.0/24")
    print(f"192.168.1.0/24 统计: {stats}")
    
    print("\nIPAM基本操作测试完成!")


def test_cidr_validation():
    """测试CIDR格式验证"""
    print("\n\n开始测试CIDR格式验证...")
    
    ipam = IPAM("test_cidr_data.json")
    
    # 测试有效的CIDR格式
    valid_cidrs = [
        "192.168.1.0/24",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "2001:db8::/32",
        "fd00::/8"
    ]
    
    print("有效CIDR测试:")
    for cidr in valid_cidrs:
        success, message = ipam.add_network(cidr, f"测试网络 {cidr}")
        print(f"  {cidr}: {success}, {message}")
    
    # 测试无效的CIDR格式
    invalid_cidrs = [
        "192.168.1.0",  # 缺少前缀
        "192.168.1.0/33",  # 无效的前缀长度
        "300.0.0.0/24",  # 无效的IP地址
        "2001:db8::/129"  # 无效的IPv6前缀长度
    ]
    
    print("\n无效CIDR测试:")
    for cidr in invalid_cidrs:
        success, message = ipam.add_network(cidr, f"测试网络 {cidr}")
        print(f"  {cidr}: {success}, {message}")
    
    print("\nCIDR格式验证测试完成!")


if __name__ == "__main__":
    test_ipam_basic_operations()
    test_cidr_validation()
    print("\n所有测试完成!")
