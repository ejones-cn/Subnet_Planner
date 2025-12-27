#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 修复前的正则表达式（有问题）
old_ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

# 修复后的正则表达式
new_ipv4_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'

# 测试用例
test_cases = [
    "192.168.1.1",      # 有效IP
    "192.168.1、",      # 无效IP（中文顿号）
    "192.168.1、3",     # 无效IP（中文顿号）
    "192.168.1.256",    # 无效IP（八位组超过255）
    "192.168.1",        # 无效IP（缺少八位组）
    "192.168.1.1.1",    # 无效IP（多了一个八位组）
    "abc.def.ghi.jkl",   # 无效IP（包含字母）
]

print("=== 测试IPv4地址验证修复效果 ===\n")
print(f"{'测试用例':<20} {'修复前结果':<15} {'修复后结果':<15} {'预期结果':<15}")
print("-" * 65)

for test_case in test_cases:
    # 修复前的匹配结果
    old_match = bool(re.match(old_ipv4_pattern, test_case))
    
    # 修复后的匹配结果
    new_match = bool(re.match(new_ipv4_pattern, test_case))
    
    # 预期结果
    expected = True if test_case == "192.168.1.1" else False
    
    # 输出结果
    print(f"{test_case:<20} {old_match!s:<15} {new_match!s:<15} {expected!s:<15}")

print("\n=== 修复说明 ===")
print("问题：修复前的正则表达式中点号(.)没有被转义，导致它匹配任何字符，包括中文顿号(、)")
print("解决方案：将点号转义为\\.，确保它只匹配实际的点号字符")
print("效果：现在'192.168.1、3'这样的输入会被正确识别为无效IP，显示红色")