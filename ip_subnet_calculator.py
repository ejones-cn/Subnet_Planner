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

# 导入标准库模块
import re
import ipaddress

# 导入本地模块
from version import get_version

# 模块版本号
__version__ = get_version()


def handle_ip_subnet_error(error, error_type="子网操作", language="zh"):
    """
    通用IP子网错误处理函数

    参数:
    error: 捕获的ValueError异常
    error_type: 错误类型前缀（如"子网计算"、"子网规划"）
    language: 错误信息语言，"zh"表示中文，"en"表示英文

    返回:
    包含错误信息的字典
    """
    error_msg = str(error)
    error_info = None

    # 定义错误模式匹配列表，包含错误类型、匹配模式和错误信息模板
    error_patterns = [
        # (匹配函数, 英文模板, 中文模板)
        (lambda msg: "not a valid netmask" in msg,
         lambda m: f"'{m.split()[0]}' is not a valid subnet mask",
         lambda m: f"'{m.split()[0]}' 不是有效的子网掩码"),
        
        (lambda msg: "does not appear to be an IPv4 or IPv6 network" in msg,
         lambda m: f"Invalid network address format: {m.split()[-1]}",
         lambda m: f"无效的网络地址格式: {m.split()[-1]}"),
        
        (lambda msg: "has host bits set" in msg,
         lambda m: f"CIDR address has host bits set: {m.split()[0]}",
         lambda m: f"CIDR地址包含主机位: {m.split()[0]}"),
        
        (lambda msg: re.search(r"octet.*?(\d+)", msg, re.IGNORECASE),
         lambda m: f"Invalid octet '{re.search(r'octet.*?(\d+)', m, re.IGNORECASE).group(1)}' in IP, must be ≤ 255",
         lambda m: f"IP地址中八位组 '{re.search(r'octet.*?(\d+)', m, re.IGNORECASE).group(1)}' 无效，必须≤255"),
        
        (lambda msg: re.search(r"expected.*?4 octets", msg, re.IGNORECASE | re.DOTALL),
         lambda m: "Invalid IP format, expected 4 octets" if not re.search(r"'([^']+)'", m) else f"Invalid IP format, expected 4 octets, got '{re.search(r"'([^']+)'", m).group(1)}'",
         lambda m: "IP地址格式错误，需要4个八位组" if not re.search(r"'([^']+)'", m) else f"IP地址格式错误，需要4个八位组，实际为 '{re.search(r"'([^']+)'", m).group(1)}'"),
    ]

    # 检查错误模式
    for match_func, en_template, zh_template in error_patterns:
        if match_func(error_msg):
            if language == "en":
                error_info = en_template(error_msg)
            else:
                error_info = zh_template(error_msg)
            break

    # 检查octet长度错误（特殊处理）
    if not error_info and re.search(r"at most 3 characters permitted", error_msg, re.IGNORECASE):
        octet_match = re.search(r"in?'?([^']+)'?", error_msg, re.IGNORECASE)
        if octet_match:
            invalid_octet = octet_match.group(1)
            if language == "en":
                error_info = f"Invalid octet '{invalid_octet}' in IP, max 3 chars (0-255) allowed"
            else:
                error_info = f"IP地址中八位组 '{invalid_octet}' 无效，最多允许3个字符（0-255）"

    # 使用默认错误信息
    if not error_info:
        if language == "en":
            error_info = f"{error_type} error: {error_msg}"
        else:
            error_info = f"{error_type}错误: {error_msg}"

    return {"error": error_info}


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
        usable_addresses = network.num_addresses - 2 if network.num_addresses > 2 else network.num_addresses

        return {
            "network": str(network.network_address),
            "netmask": str(network.netmask),
            "wildcard": wildcard_mask,
            "broadcast": str(network.broadcast_address),
            "cidr": str(network.with_prefixlen),
            "prefixlen": network.prefixlen,
            "num_addresses": network.num_addresses,
            "usable_addresses": usable_addresses,
            "host_range_start": host_range_start,
            "host_range_end": host_range_end
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


def _allocate_subnet(available_subnets, required):
    """
    辅助函数：从可用子网列表中为需求子网分配空间
    
    参数:
    available_subnets: 可用子网列表
    required: 需求子网信息
    
    返回:
    分配结果元组 (success, allocated_subnet, remaining_subnets, error)
    """
    new_prefix = required["prefix_len"]

    for i, available in enumerate(available_subnets):
        if available.prefixlen <= new_prefix:
            try:
                # 只获取第一个子网，不需要生成所有子网
                subnets_gen = available.subnets(new_prefix=new_prefix)
                new_subnet = next(subnets_gen, None)
                if not new_subnet:
                    return False, None, None, f"无法为 {required['name']} 创建前缀长度为 {new_prefix} 的子网"
                
                # 计算剩余子网
                remaining = list(available.address_exclude(new_subnet))
                updated_available = available_subnets.copy()
                updated_available.pop(i)
                updated_available.extend(remaining)
                updated_available.sort()
                
                return True, new_subnet, updated_available, None
            except ValueError as e:
                return False, None, None, f"创建子网失败: {str(e)}"
    
    return False, None, None, f"无法为 {required['name']} 分配足够大的子网空间"


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

        # 预处理子网需求：计算前缀长度并排序
        sorted_subnets = []
        for subnet in required_subnets:
            # 计算需要的地址数量和前缀长度
            required_addresses = subnet["hosts"] + 2
            prefix_len = 32 - (required_addresses - 1).bit_length()
            prefix_len = max(prefix_len, parent_net.prefixlen)
            prefix_len = min(prefix_len, 32)
            
            sorted_subnets.append({
                "name": subnet["name"],
                "hosts": subnet["hosts"],
                "prefix_len": prefix_len
            })
        
        # 按所需主机数量从大到小排序，优先分配大的子网
        sorted_subnets.sort(key=lambda x: x["hosts"], reverse=True)

        # 开始分配子网
        available_subnets = [parent_net]
        allocated_subnets = []

        for required in sorted_subnets:
            # 调用辅助函数分配子网
            success, new_subnet, updated_available, error = _allocate_subnet(available_subnets, required)
            
            if not success:
                return {"error": error}
            
            # 分配成功，更新状态
            available_subnets = updated_available
            subnet_info = get_subnet_info(str(new_subnet))
            allocated_subnets.append({
                "name": required["name"],
                "cidr": str(new_subnet),
                "required_hosts": required["hosts"],
                "available_hosts": subnet_info["usable_addresses"],
                "info": subnet_info,
            })

        # 生成剩余子网信息
        remaining_subnets = [str(subnet) for subnet in available_subnets]
        remaining_subnets_info = [get_subnet_info(str(subnet)) for subnet in available_subnets]
        
        return {
            "parent_cidr": parent_cidr,
            "required_subnets": required_subnets,
            "allocated_subnets": allocated_subnets,
            "remaining_subnets": remaining_subnets,
            "remaining_subnets_info": remaining_subnets_info,
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
        for idx, sub in enumerate(result["remaining_subnets_info"], 1):
            print(f"\n网段 {idx}:")
            for key, value in sub.items():
                print(f"  {key}: {value}")

    # 测试子网规划智能建议
    print("\n=== 测试子网规划智能建议功能 ===")
    test_required_subnets = [
        {"name": "办公区", "hosts": 200},
        {"name": "服务器区", "hosts": 50},
        {"name": "研发部", "hosts": 100},
        {"name": "测试环境", "hosts": 30},
    ]

    plan = suggest_subnet_planning("192.168.0.0/16", test_required_subnets)
    if "error" in plan:
        print(f"错误: {plan['error']}")
    else:
        print(f"父网段: {plan['parent_cidr']}")
        print("\n已分配子网:")
        for sub in plan["allocated_subnets"]:
            print(f"\n{sub['name']}:")
            print(f"  CIDR: {sub['cidr']}")
            print(f"  需求主机数: {sub['required_hosts']}")
            print(f"  可用主机数: {sub['available_hosts']}")
            print(f"  网络地址: {sub['info']['network']}")
            print(f"  子网掩码: {sub['info']['netmask']}")
            print(f"  广播地址: {sub['info']['broadcast']}")

        print(f"\n剩余网段 ({len(plan['remaining_subnets'])} 个):")
        for idx, sub in enumerate(plan["remaining_subnets_info"], 1):
            print(f"\n网段 {idx}: {sub['cidr']}")
