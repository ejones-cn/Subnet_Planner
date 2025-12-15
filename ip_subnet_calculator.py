#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IP子网切分计算器

提供IP子网切分的核心功能，包括:
1. IP地址和整数之间的转换
2. 获取子网的详细信息
3. 检查子网关系
4. 执行子网切分
"""

# 导入版本管理模块
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from version import get_version

__version__ = get_version()

import ipaddress

def handle_ip_subnet_error(error, error_type="子网操作"):
    """
    通用IP子网错误处理函数
    
    参数:
    error: 捕获的ValueError异常
    error_type: 错误类型前缀（如"子网计算"、"子网规划"）
    
    返回:
    包含错误信息的字典
    """
    error_msg = str(error)
    if "not a valid netmask" in error_msg:
        return {"error": f"'{error_msg.split()[0]}' 不是有效的子网掩码"}
    elif re.search(r"octet.*?not permitted", error_msg, re.IGNORECASE):
        match = re.search(r"octet.*?(\d+)", error_msg, re.IGNORECASE)
        if match:
            octet = match.group(1)
            if int(octet) > 255:
                return {"error": f"IP地址中包含无效的八位组 '{octet}'（必须小于等于255）"}
        return {"error": f"{error_type}错误: {error_msg}"}
    elif "does not appear to be an IPv4 or IPv6 network" in error_msg:
        return {"error": f"无效的网络地址格式: {error_msg.split()[-1]}"}
    elif "has host bits set" in error_msg:
        return {"error": f"CIDR地址包含主机位: {error_msg.split()[0]}"}
    elif re.search(r"expected.*?4 octets", error_msg, re.IGNORECASE | re.DOTALL):
        ip_match = re.search(r"'([^']+)'", error_msg)
        if ip_match:
            invalid_ip = ip_match.group(1)
            return {"error": f"IP地址格式错误，需要4个八位组，实际为 '{invalid_ip}'"}
        else:
            return {"error": "IP地址格式错误，需要4个八位组"}
    elif re.search(r"at most 3 characters permitted", error_msg, re.IGNORECASE):
        octet_match = re.search(r"in?'?([^']+)'?", error_msg, re.IGNORECASE)
        if octet_match:
            invalid_octet = octet_match.group(1)
            return {"error": f"IP地址中八位组 '{invalid_octet}' 无效，最多允许3个字符（0-255）"}
    elif re.search(r"octet.*?exceeds", error_msg, re.IGNORECASE):
        match = re.search(r"octet.*?(\d+)", error_msg, re.IGNORECASE)
        if match:
            octet_value = match.group(1)
            return {"error": f"IP地址中八位组 '{octet_value}' 无效，必须小于等于255"}
    elif "Octet" in error_msg and "exceeds" in error_msg:
        match = re.search(r"Octet (\d+) exceeds", error_msg)
        if match:
            octet_value = match.group(1)
            return {"error": f"IP地址中八位组 '{octet_value}' 无效，必须小于等于255"}
    else:
        return {"error": f"{error_type}错误: {error_msg}"}


def ip_to_int(ip_str):
    """
    将IP地址字符串转换为整数
    """
    parts = ip_str.split(".")
    return int(parts[0]) << 24 | int(parts[1]) << 16 | int(parts[2]) << 8 | int(parts[3])


def int_to_ip(ip_int):
    """
    将整数转换为IP地址字符串
    """
    return f"{ip_int >> 24}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 8) & 0xFF}.{ip_int & 0xFF}"


def get_subnet_info(network_str):
    """
    获取子网的详细信息
    """
    try:
        network = ipaddress.IPv4Network(network_str, strict=False)

        # 计算通配符掩码：子网掩码的反码
        wildcard = ~int(network.netmask) & 0xFFFFFFFF
        wildcard_mask = int_to_ip(wildcard)
        
        # 计算可用主机范围
        host_range_start = str(network.network_address + 1) if network.num_addresses > 2 else str(network.network_address)
        host_range_end = str(network.broadcast_address - 1) if network.num_addresses > 2 else str(network.broadcast_address)
        
        # 获取可用主机数量
        number_of_hosts = network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses

        return {
            "network": str(network.network_address),
            "netmask": str(network.netmask),
            "wildcard": wildcard_mask,
            "broadcast": str(network.broadcast_address),
            "cidr": str(network.with_prefixlen),
            "prefixlen": network.prefixlen,
            "num_addresses": network.num_addresses,
            "usable_addresses": number_of_hosts,
            # 以下是为了兼容导出函数添加的键
            "network_address": str(network.network_address),
            "subnet_mask": str(network.netmask),
            "prefix_length": network.prefixlen,
            "broadcast_address": str(network.broadcast_address),
            "host_range_start": host_range_start,
            "host_range_end": host_range_end,
            "number_of_hosts": number_of_hosts
        }
    except ValueError as e:
        return handle_ip_subnet_error(e, "子网计算")


def split_subnet(parent_cidr, split_cidr):
    """
    将split_cidr从parent_cidr中切分出来，返回剩余的子网列表
    """
    try:
        parent_net = ipaddress.IPv4Network(parent_cidr, strict=False)
        split_net = ipaddress.IPv4Network(split_cidr, strict=False)

        # 检查split_net是否是parent_net的子网
        if not split_net.subnet_of(parent_net):
            return {"error": f"{split_cidr} 不是 {parent_cidr} 的子网"}

        # 如果父网段和切分网段相同，直接返回空列表
        if parent_net == split_net:
            return {
            "parent": parent_cidr,
            "split": split_cidr,
            "remaining_subnets": [],
            "parent_info": get_subnet_info(parent_cidr),
            "split_info": get_subnet_info(split_cidr),
            "remaining_subnets_info": [],
        }

        # 使用Python ipaddress模块的address_exclude方法获取剩余网段
        # 这个方法会自动生成最简洁的剩余网段列表
        remaining = list(parent_net.address_exclude(split_net))

        # 对剩余网段按CIDR进行排序
        remaining.sort()

        return {
            "parent": parent_cidr,
            "split": split_cidr,
            "remaining_subnets": [str(subnet) for subnet in remaining],
            "parent_info": get_subnet_info(parent_cidr),
            "split_info": get_subnet_info(split_cidr),
            "remaining_subnets_info": [get_subnet_info(str(subnet)) for subnet in remaining],
        }

    except ValueError as e:
        return handle_ip_subnet_error(e, "子网规划")


def suggest_subnet_planning(parent_cidr, required_subnets):
    """
    子网规划智能建议功能

    参数:
    parent_cidr: 父网段，格式为CIDR (例如: "10.0.0.0/8")
    required_subnets: 需要的子网列表，每个子网包含name和hosts两个字段

    返回:
    包含建议子网规划的字典
    """
    try:
        parent_net = ipaddress.IPv4Network(parent_cidr, strict=False)

        # 按所需主机数量从大到小排序，优先分配大的子网
        sorted_subnets = sorted(required_subnets, key=lambda x: x["hosts"], reverse=True)

        # 计算每个子网需要的CIDR前缀长度
        for subnet in sorted_subnets:
            # 计算需要的地址数量（包括网络地址和广播地址）
            required_addresses = subnet["hosts"] + 2
            # 计算合适的前缀长度
            prefix_len = 32 - (required_addresses - 1).bit_length()
            # 确保前缀长度在有效范围内（0-32）且不小于父网段的前缀长度
            prefix_len = max(prefix_len, parent_net.prefixlen)
            prefix_len = min(prefix_len, 32)  # 确保前缀长度不超过32
            prefix_len = max(prefix_len, 0)   # 确保前缀长度不小于0
            subnet["prefix_len"] = prefix_len

        # 开始分配子网
        available_subnets = [parent_net]
        allocated_subnets = []

        for required in sorted_subnets:
            allocated = False

            # 尝试在可用子网中找到合适的网段
            for i, available in enumerate(available_subnets):
                # 检查可用子网是否有足够的空间
                if available.prefixlen <= required["prefix_len"]:
                    # 创建所需的子网
                    # 确保新前缀长度在有效范围内
                    new_prefix = required["prefix_len"]
                    new_prefix = max(new_prefix, 0)
                    new_prefix = min(new_prefix, 32)
                    
                    # 验证是否可以使用该前缀长度创建子网
                    try:
                        subnets_list = list(available.subnets(new_prefix=new_prefix))
                        if not subnets_list:
                            return {"error": f"无法为 {required['name']} 创建前缀长度为 {new_prefix} 的子网"}
                        
                        new_subnet = subnets_list[0]
                        
                        # 确保生成的子网有有效的前缀长度
                        if not (0 <= new_subnet.prefixlen <= 32):
                            return {"error": f"生成了无效的子网前缀长度: {new_subnet.prefixlen}"}
                    except ValueError as e:
                        return {"error": f"创建子网失败: {str(e)}"}

                    # 分配该子网
                    allocated_subnets.append(
                        {
                            "name": required["name"],
                            "cidr": str(new_subnet),
                            "required_hosts": required["hosts"],
                            "available_hosts": (
                                new_subnet.num_addresses - 2
                                if new_subnet.num_addresses > 2
                                else new_subnet.num_addresses
                            ),
                            "info": get_subnet_info(str(new_subnet)),
                        }
                    )

                    # 更新可用子网列表
                    remaining = list(available.address_exclude(new_subnet))
                    available_subnets.pop(i)
                    available_subnets.extend(remaining)
                    available_subnets.sort()  # 保持排序

                    allocated = True
                    break

            if not allocated:
                return {"error": f"无法为 {required['name']} 分配足够大的子网空间"}

        return {
            "parent_cidr": parent_cidr,
            "required_subnets": required_subnets,
            "allocated_subnets": allocated_subnets,
            "remaining_subnets": [str(subnet) for subnet in available_subnets],
            "remaining_subnets_info": [
                get_subnet_info(str(subnet)) for subnet in available_subnets
            ],
        }

    except ValueError as e:
        return handle_ip_subnet_error(e, "子网规划")


# 测试示例
if __name__ == "__main__":
    # 测试子网切分
    print("=== 测试子网切分功能 ===")
    result = split_subnet("10.0.0.0/8", "10.21.60.0/23")
    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print(f"父网段: {result['parent']}")
        print(f"切分网段: {result['split']}")
        print("\n切分网段信息:")
        for key, value in result["split_info"].items():
            print(f"  {key}: {value}")
        print(f"\n剩余网段 ({len(result['remaining_subnets'])} 个):")
        for i, subnet in enumerate(result["remaining_subnets_info"], 1):
            print(f"\n网段 {i}:")
            for key, value in subnet.items():
                print(f"  {key}: {value}")

    # 测试子网规划智能建议
    print("\n=== 测试子网规划智能建议功能 ===")
    required_subnets = [
        {"name": "办公区", "hosts": 200},
        {"name": "服务器区", "hosts": 50},
        {"name": "研发部", "hosts": 100},
        {"name": "测试环境", "hosts": 30},
    ]

    plan = suggest_subnet_planning("192.168.0.0/16", required_subnets)
    if "error" in plan:
        print(f"错误: {plan['error']}")
    else:
        print(f"父网段: {plan['parent_cidr']}")
        print(f"\n已分配子网:")
        for subnet in plan["allocated_subnets"]:
            print(f"\n{subnet['name']}:")
            print(f"  CIDR: {subnet['cidr']}")
            print(f"  需求主机数: {subnet['required_hosts']}")
            print(f"  可用主机数: {subnet['available_hosts']}")
            print(f"  网络地址: {subnet['info']['network']}")
            print(f"  子网掩码: {subnet['info']['netmask']}")
            print(f"  广播地址: {subnet['info']['broadcast']}")

        print(f"\n剩余网段 ({len(plan['remaining_subnets'])} 个):")
        for i, subnet in enumerate(plan["remaining_subnets_info"], 1):
            print(f"\n网段 {i}: {subnet['cidr']}")



