#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ipaddress
from ip_subnet_calculator import handle_ip_subnet_error

# 测试无效的IPv4地址
invalid_ips = [
    "192.168.1.1111",  # 无效的八位组
    "192.168.1",       # 缺少八位组
    "192.168.1.256",   # 八位组值超过255
    "192.168.1.0/33",  # 无效的CIDR前缀
    "abc.def.ghi.jkl"   # 非数字字符
]

for ip in invalid_ips:
    print(f"\n测试IP: {ip}")
    try:
        ipaddress.IPv4Address(ip)
        print("✓ 有效IP")
    except ValueError as e:
        error_msg = str(e)
        print(f"✗ 无效IP")
        print(f"  原始错误: {error_msg}")
        # 调用错误处理函数
        error_info = handle_ip_subnet_error(e, "IP地址验证")
        print(f"  处理后错误: {error_info['error']}")