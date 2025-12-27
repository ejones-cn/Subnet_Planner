#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ipaddress
from ip_subnet_calculator import handle_ip_subnet_error

# 测试截图中显示的IPv6错误
print("=== 测试IPv6特定错误处理 ===\n")

# 测试截图中的IPv6错误
ipv6_error = "At most 4 characters permitted in '733411' in '2001:db8:85a3:0000:0000:8a2e:0370:733411'"
print(f"原始错误信息: {ipv6_error}")

# 模拟捕获的ValueError异常
class MockValueError(ValueError):
    def __str__(self):
        return ipv6_error

# 调用错误处理函数
error_info = handle_ip_subnet_error(MockValueError(), "IP地址验证")
print(f"处理后错误: {error_info['error']}")

# 检查是否返回了正确的中文错误信息
if "IPv6" in error_info['error'] and "过长" in error_info['error']:
    print("✅ 正确：返回了中文IPv6错误信息")
else:
    print("❌ 错误：没有返回正确的中文IPv6错误信息")

# 测试其他IPv6错误情况
print("\n\n其他IPv6错误测试:")
print("-" * 50)

additional_errors = [
    "At most 8 colons permitted in '2001:0db8:85a3:0000:0000:8a2e:0370::7334::123'",
    "At most 45 characters expected in '2001::0db8::85a3::0000::0000::8a2e::0370::7334'",
    "Only hex digits permitted in 'z334' in '2001:0db8:85a3:0000:0000:8a2e:0370:z334'",
]

for err_msg in additional_errors:
    print(f"\n原始错误: {err_msg}")
    
    class MockError(ValueError):
        def __str__(self):
            return err_msg
    
    error_info = handle_ip_subnet_error(MockError(), "IP地址验证")
    print(f"处理后: {error_info['error']}")
    if "IPv6" in error_info['error']:
        print(f"  ✅ 正确：返回了IPv6相关错误信息")
    else:
        print(f"  ❌ 错误：没有返回IPv6相关错误信息")