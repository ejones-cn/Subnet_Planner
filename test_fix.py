#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试子网规划功能的IP版本匹配修复效果
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

print("测试子网规划功能的IP版本匹配修复效果")
print("=" * 60)

# 测试1: 验证初始化时只显示IPv4样例
print("\n测试1: 验证初始化时只显示IPv4样例")
print("-" * 40)
print(f"初始IP版本: {app.ip_version_var.get()}")
print(f"初始下拉列表内容: {app.planning_parent_networks}")
if all(":" not in cidr for cidr in app.planning_parent_networks):
    print("✅ 初始下拉列表只包含IPv4样例")
else:
    print("❌ 初始下拉列表包含IPv6样例")

# 测试2: 验证IPv4模式下无法输入IPv6地址
print("\n测试2: 验证IPv4模式下无法输入IPv6地址")
print("-" * 40)
ipv6_address = "2001:0db8::/32"
result = app._validate_planning_input(ipv6_address)
print(f"验证IPv6地址 '{ipv6_address}' 在IPv4模式下:")
if not result['valid']:
    print(f"✅ 正确拒绝了IPv6地址，错误信息: {result['error']}")
else:
    print("❌ 错误地接受了IPv6地址")

# 测试3: 验证IPv4模式下可以输入IPv4地址
print("\n测试3: 验证IPv4模式下可以输入IPv4地址")
print("-" * 40)
ipv4_address = "10.21.48.0/20"
result = app._validate_planning_input(ipv4_address)
print(f"验证IPv4地址 '{ipv4_address}' 在IPv4模式下:")
if result['valid']:
    print("✅ 正确接受了IPv4地址")
else:
    print(f"❌ 错误地拒绝了IPv4地址，错误信息: {result['error']}")

# 测试4: 验证IPv6模式下可以输入IPv6地址
print("\n测试4: 验证IPv6模式下可以输入IPv6地址")
print("-" * 40)
app.ip_version_var.set("IPv6")
ipv6_address = "2001:0db8::/32"
result = app._validate_planning_input(ipv6_address)
print(f"验证IPv6地址 '{ipv6_address}' 在IPv6模式下:")
if result['valid']:
    print("✅ 正确接受了IPv6地址")
else:
    print(f"❌ 错误地拒绝了IPv6地址，错误信息: {result['error']}")

# 测试5: 验证IPv6模式下无法输入IPv4地址
print("\n测试5: 验证IPv6模式下无法输入IPv4地址")
print("-" * 40)
ipv4_address = "10.21.48.0/20"
result = app._validate_planning_input(ipv4_address)
print(f"验证IPv4地址 '{ipv4_address}' 在IPv6模式下:")
if not result['valid']:
    print(f"✅ 正确拒绝了IPv4地址，错误信息: {result['error']}")
else:
    print("❌ 错误地接受了IPv4地址")

# 测试6: 验证validate_cidr方法的IP版本匹配检查
print("\n测试6: 验证validate_cidr方法的IP版本匹配检查")
print("-" * 40)
app.ip_version_var.set("IPv4")
result = app.validate_cidr("2001:0db8::/32")
print(f"validate_cidr('2001:0db8::/32') 在IPv4模式下: {result}")
if not result:
    print("✅ validate_cidr方法正确识别IP版本不匹配")
else:
    print("❌ validate_cidr方法未能识别IP版本不匹配")

# 测试7: 验证on_ip_version_change方法
print("\n测试7: 验证on_ip_version_change方法")
print("-" * 40)
# 切换到IPv6
app.ip_version_var.set("IPv6")
app.on_ip_version_change()
print(f"切换到IPv6后，IP版本: {app.ip_version_var.get()}")
print(f"切换到IPv6后，下拉列表内容: {app.planning_parent_networks}")
if all(":" in cidr for cidr in app.planning_parent_networks):
    print("✅ 切换到IPv6后，下拉列表只包含IPv6样例")
else:
    print("❌ 切换到IPv6后，下拉列表包含IPv4样例")

# 切换回IPv4
app.ip_version_var.set("IPv4")
app.on_ip_version_change()
print(f"切换回IPv4后，IP版本: {app.ip_version_var.get()}")
print(f"切换回IPv4后，下拉列表内容: {app.planning_parent_networks}")
if all(":" not in cidr for cidr in app.planning_parent_networks):
    print("✅ 切换回IPv4后，下拉列表只包含IPv4样例")
else:
    print("❌ 切换回IPv4后，下拉列表包含IPv6样例")

print("\n" + "=" * 60)
print("测试完成！")

# 关闭测试窗口
root.destroy()
