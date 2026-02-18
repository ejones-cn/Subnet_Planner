#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试子网规划和子网切分功能的IP版本独立性
"""

import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from windows_app import SubnetPlannerApp
import tkinter as tk

# 创建测试窗口
root = tk.Tk()
root.withdraw()  # 隐藏主窗口

# 创建应用实例
app = SubnetPlannerApp(root)

print("测试子网规划和子网切分功能的IP版本独立性")
print("=" * 70)

# 测试用例
test_cases = [
    ("子网规划IPv4 + 子网切分IPv4", "IPv4", "IPv4", "10.21.48.0/20", "10.0.0.0/8", "10.21.50.0/23"),
    ("子网规划IPv4 + 子网切分IPv6", "IPv4", "IPv6", "10.21.48.0/20", "2001:0db8::/32", "2001:0db8::/64"),
    ("子网规划IPv6 + 子网切分IPv4", "IPv6", "IPv4", "2001:0db8::/32", "10.0.0.0/8", "10.21.50.0/23"),
    ("子网规划IPv6 + 子网切分IPv6", "IPv6", "IPv6", "2001:0db8::/32", "2001:0db8::/32", "2001:0db8::/64"),
]

for test_name, planning_ip_version, split_ip_version, planning_address, split_parent, split_segment in test_cases:
    print(f"\n{test_name}")
    print("-" * 70)
    
    # 设置子网规划的IP版本
    app.ip_version_var.set(planning_ip_version)
    print(f"子网规划IP版本: {app.ip_version_var.get()}")
    
    # 验证子网规划的IP地址
    planning_result = app._validate_planning_input(planning_address)
    print(f"子网规划验证 {planning_address}: {'✅ 有效' if planning_result['valid'] else '❌ 无效'}")
    
    # 设置子网切分的IP版本
    app.split_ip_version_var.set(split_ip_version)
    print(f"子网切分IP版本: {app.split_ip_version_var.get()}")
    
    # 验证子网切分的IP地址
    split_result = app._validate_split_input(split_parent, split_segment)
    print(f"子网切分验证 {split_parent} 和 {split_segment}: {'✅ 有效' if split_result['valid'] else '❌ 无效'}")
    
    # 验证validate_cidr方法的独立性
    # 测试子网规划的validate_cidr
    planning_cidr_result = app.validate_cidr(planning_address, ip_version=planning_ip_version)
    print(f"validate_cidr({planning_address}, ip_version={planning_ip_version}): {'✅ 有效' if planning_cidr_result else '❌ 无效'}")
    
    # 测试子网切分的validate_cidr
    split_parent_result = app.validate_cidr(split_parent, ip_version=split_ip_version)
    split_segment_result = app.validate_cidr(split_segment, ip_version=split_ip_version)
    print(f"validate_cidr({split_parent}, ip_version={split_ip_version}): {'✅ 有效' if split_parent_result else '❌ 无效'}")
    print(f"validate_cidr({split_segment}, ip_version={split_ip_version}): {'✅ 有效' if split_segment_result else '❌ 无效'}")
    
    # 测试交叉验证，确保IP版本不会互相影响
    cross_result = app.validate_cidr(split_parent, ip_version=planning_ip_version)
    expected_result = (split_ip_version == planning_ip_version)
    if cross_result == expected_result:
        print(f"交叉验证结果正确: {'✅ 有效' if cross_result else '❌ 无效'} (预期: {'✅ 有效' if expected_result else '❌ 无效'})")
    else:
        print(f"交叉验证结果错误: {'✅ 有效' if cross_result else '❌ 无效'} (预期: {'✅ 有效' if expected_result else '❌ 无效'})")

print("\n" + "=" * 70)
print("测试完成！")

# 关闭测试窗口
root.destroy()
