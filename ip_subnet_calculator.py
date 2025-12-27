#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IP子网切分计算器

提供IP子网切分的核心功能，包括:
1. IP地址和整数之间的转换
2. 获取子网的详细信息
3. 检查子网关系
4. 执行子网切分
5. 子网合并功能
6. IP地址范围计算
7. 子网重叠检查
8. IP地址分类与属性判断
9. IPv4/IPv6转换
"""

# 导入标准库模块
import re
import math
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
    return int(ipaddress.IPv4Address(ip_str))


def int_to_ip(ip_int):
    return str(ipaddress.IPv4Address(ip_int))


def ipv4_to_ipv6(ipv4_str):
    """
    将IPv4地址转换为IPv6地址（IPv4映射格式）
    
    参数:
    ipv4_str: IPv4地址字符串
    
    返回:
    IPv6地址字符串（::ffff:ipv4格式）
    """
    try:
        # 验证IPv4地址格式
        ipaddress.IPv4Address(ipv4_str)
        # 返回IPv4映射的IPv6地址
        return f"::ffff:{ipv4_str}"
    except ValueError as e:
        return handle_ip_subnet_error(e, "IPv4转IPv6")


def ipv6_to_ipv4(ipv6_str):
    """
    将IPv6地址转换为IPv4地址（仅支持IPv4映射格式）
    
    参数:
    ipv6_str: IPv6地址字符串
    
    返回:
    IPv4地址字符串，如果不是IPv4映射格式则返回错误
    """
    try:
        ipv6_addr = ipaddress.IPv6Address(ipv6_str)
        # 检查是否为IPv4映射地址
        if ipv6_addr.ipv4_mapped:
            return str(ipv6_addr.ipv4_mapped)
        else:
            return {"error": f"{ipv6_str} 不是IPv4映射的IPv6地址，该功能仅支持IPv4映射格式（如::ffff:192.168.1.1）"}
    except ValueError as e:
        return handle_ip_subnet_error(e, "IPv6转IPv4")


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


def merge_subnets(subnets):
    """
    将多个连续子网合并为更大的子网
    
    参数:
    subnets: 子网列表，每个子网为CIDR格式字符串
    
    返回:
    包含合并结果的字典
    """
    try:
        # 验证输入是否为空
        if not subnets or len(subnets) == 0:
            return {"error": "子网列表不能为空"}
        
        # 验证输入并转换为IPv4Network对象
        ipv4_subnets = []
        for subnet in subnets:
            try:
                ipv4_subnets.append(ipaddress.IPv4Network(subnet, strict=False))
            except ValueError as e:
                return handle_ip_subnet_error(e, "子网合并")
        
        # 按网络地址排序
        ipv4_subnets.sort()
        
        merged = [ipv4_subnets[0]]
        
        for subnet in ipv4_subnets[1:]:
            last_merged = merged[-1]
            
            # 检查是否可以合并
            # 条件1：连续（broadcast + 1 == next network）
            # 条件2：可以合并成更小的前缀
            is_contiguous = last_merged.broadcast_address + 1 == subnet.network_address
            is_overlapping = last_merged.overlaps(subnet)
            
            if (is_contiguous or is_overlapping):
                # 查找可以同时包含两个子网的最小超网
                min_prefix = min(last_merged.prefixlen, subnet.prefixlen)
                candidate_supernet = None
                
                for prefix_len in range(min_prefix - 1, -1, -1):
                    supernet = ipaddress.IPv4Network(
                        f"{last_merged.network_address}/{prefix_len}",
                        strict=False
                    )
                    # 检查超网是否包含两个子网
                    if (supernet.network_address <= last_merged.network_address
                        and supernet.broadcast_address >= last_merged.broadcast_address
                        and supernet.network_address <= subnet.network_address
                        and supernet.broadcast_address >= subnet.broadcast_address):
                        # 检查超网是否恰好等于两个子网的合并（即不包含其他地址）
                        expected_size = (
                            int(last_merged.broadcast_address) - int(last_merged.network_address) + 1
                            + int(subnet.broadcast_address) - int(subnet.network_address) + 1
                        )
                        if supernet.num_addresses == expected_size:
                            candidate_supernet = supernet
                            break
                
                if candidate_supernet:
                    merged.pop()
                    merged.append(candidate_supernet)
                    
                    # 尝试继续合并
                    while len(merged) > 1:
                        prev = merged[-2]
                        curr = merged[-1]
                        
                        prev_contiguous = prev.broadcast_address + 1 == curr.network_address
                        prev_overlap = prev.overlaps(curr)
                        
                        if prev_contiguous or prev_overlap:
                            min_prefix = min(prev.prefixlen, curr.prefixlen)
                            candidate = None
                            
                            for prefix_len in range(min_prefix - 1, -1, -1):
                                supernet = ipaddress.IPv4Network(
                                    f"{prev.network_address}/{prefix_len}",
                                    strict=False
                                )
                                if (supernet.network_address <= prev.network_address
                                    and supernet.broadcast_address >= prev.broadcast_address
                                    and supernet.network_address <= curr.network_address
                                    and supernet.broadcast_address >= curr.broadcast_address):
                                    expected_size = (
                                        int(prev.broadcast_address) - int(prev.network_address) + 1
                                        + int(curr.broadcast_address) - int(curr.network_address) + 1
                                    )
                                    if supernet.num_addresses == expected_size:
                                        candidate = supernet
                                        break
                            
                            if candidate:
                                merged.pop()
                                merged.pop()
                                merged.append(candidate)
                            else:
                                break
                        else:
                            break
                else:
                    merged.append(subnet)
            else:
                merged.append(subnet)
        
        # 转换回字符串格式
        merged_str = [str(subnet) for subnet in merged]
        
        return {
            "original_subnets": subnets,
            "merged_subnets": merged_str,
            "merged_subnets_info": [get_subnet_info(str(subnet)) for subnet in merged],
            "merged_count": len(merged),
            "original_count": len(subnets),
        }
        
    except ValueError as e:
        return handle_ip_subnet_error(e, "子网合并")


def get_ip_info(ip_str):
    """
    获取IP地址或网络的详细信息，同时支持IPv4和IPv6
    
    参数:
    ip_str: IP地址或网络字符串，可以是纯IP地址或带CIDR前缀的地址
    
    返回:
    包含IP或网络信息的字典
    """
    try:
        # 检查是否为带CIDR前缀的地址
        has_cidr = '/' in ip_str
        
        # 尝试解析为IPv4网络或地址
        try:
            if has_cidr:
                # 解析为IPv4网络
                network = ipaddress.IPv4Network(ip_str, strict=False)
                ip = network.network_address
                ip_version = "IPv4"
                
                # 获取网络信息
                network_address = str(network.network_address)
                broadcast_address = str(network.broadcast_address)
                subnet_mask = str(network.netmask)
                cidr = network.prefixlen
                total_hosts = network.num_addresses
                usable_hosts = total_hosts - 2 if total_hosts > 2 else total_hosts
                first_host = str(network.network_address + 1) if total_hosts > 2 else str(network.network_address)
                last_host = str(network.broadcast_address - 1) if total_hosts > 2 else str(network.broadcast_address)
            else:
                # 解析为IPv4地址
                ip = ipaddress.IPv4Address(ip_str)
                ip_version = "IPv4"
                
                # 网络信息设为None
                network_address = None
                broadcast_address = None
                subnet_mask = None
                cidr = None
                total_hosts = None
                usable_hosts = None
                first_host = None
                last_host = None
            
            # 判断IP地址类型
            ip_class = None
            first_octet = int(str(ip).split('.')[0])
            if 1 <= first_octet <= 126:
                ip_class = 'A'
            elif 128 <= first_octet <= 191:
                ip_class = 'B'
            elif 192 <= first_octet <= 223:
                ip_class = 'C'
            elif 224 <= first_octet <= 239:
                ip_class = 'D'  # 组播地址
            elif 240 <= first_octet <= 255:
                ip_class = 'E'  # 保留地址
            
            # 获取各个字节
            octets = [int(o) for o in str(ip).split('.')]
            
            # 生成二进制表示
            binary = '.'.join(f'{o:08b}' for o in octets)
            
            # 生成十六进制表示
            hexadecimal = '.'.join(f'{o:02x}' for o in octets)
            
            # 获取默认子网掩码
            default_netmask = None
            if ip_class == 'A':
                default_netmask = '255.0.0.0'
            elif ip_class == 'B':
                default_netmask = '255.255.0.0'
            elif ip_class == 'C':
                default_netmask = '255.255.255.0'
            
            return {
                "ip_address": str(ip),
                "version": ip_version,
                "class": ip_class,
                "binary": binary,
                "hexadecimal": hexadecimal,
                "integer": int(ip),
                "is_global": ip.is_global,
                "is_private": ip.is_private,
                "is_link_local": ip.is_link_local,
                "is_loopback": ip.is_loopback,
                "is_multicast": ip.is_multicast,
                "is_unspecified": ip.is_unspecified,
                "is_reserved": ip.is_reserved,
                "network_address": network_address,
                "broadcast_address": broadcast_address,
                "subnet_mask": subnet_mask,
                "cidr": cidr,
                "prefix_length": cidr,
                "total_hosts": total_hosts,
                "usable_hosts": usable_hosts,
                "first_host": first_host,
                "last_host": last_host,
                "default_netmask": default_netmask,
            }
        except ValueError:
            # 尝试解析为IPv6网络或地址
            if has_cidr:
                # 解析为IPv6网络
                network = ipaddress.IPv6Network(ip_str, strict=False)
                ip = network.network_address
                ip_version = "IPv6"
                
                # 获取网络信息
                network_address = str(network.network_address)
                broadcast_address = str(network.broadcast_address)
                subnet_mask = str(network.netmask)
                cidr = network.prefixlen
                total_hosts = network.num_addresses
                usable_hosts = total_hosts - 2 if total_hosts > 2 else total_hosts
                first_host = str(network.network_address + 1) if total_hosts > 2 else str(network.network_address)
                last_host = str(network.broadcast_address - 1) if total_hosts > 2 else str(network.broadcast_address)
            else:
                # 解析为IPv6地址
                ip = ipaddress.IPv6Address(ip_str)
                ip_version = "IPv6"
                
                # 网络信息设为None
                network_address = None
                broadcast_address = None
                subnet_mask = None
                cidr = None
                total_hosts = None
                usable_hosts = None
                first_host = None
                last_host = None
            
            # 生成二进制表示
            binary = ip.exploded.replace(':', '').zfill(32)
            # 每4位分组，便于阅读
            binary_grouped = ' '.join([binary[i:i + 4] for i in range(0, 32, 4)])
            
            return {
                "ip_address": str(ip),
                "version": ip_version,
                "binary": binary_grouped,
                "hexadecimal": ip.exploded,
                "integer": int(ip),
                "is_global": ip.is_global,
                "is_private": ip.is_private,
                "is_link_local": ip.is_link_local,
                "is_loopback": ip.is_loopback,
                "is_multicast": ip.is_multicast,
                "is_unspecified": ip.is_unspecified,
                "is_reserved": ip.is_reserved,
                "network_address": network_address,
                "broadcast_address": broadcast_address,
                "subnet_mask": subnet_mask,
                "cidr": cidr,
                "prefix_length": cidr,
                "total_hosts": total_hosts,
                "usable_hosts": usable_hosts,
                "first_host": first_host,
                "last_host": last_host,
                "compressed": ip.compressed,
                "exploded": ip.exploded,
                "reverse_dns": '.'.join(reversed(ip.exploded.replace(':', ''))),
            }
        
    except ValueError as e:
        return handle_ip_subnet_error(e, "IP信息获取")


def range_to_cidr(start_ip, end_ip):
    """
    将IP地址范围转换为CIDR表示法
    
    参数:
    start_ip: 起始IP地址字符串
    end_ip: 结束IP地址字符串
    
    返回:
    包含CIDR列表的字典
    """
    try:
        # 验证IP地址格式
        start = ipaddress.IPv4Address(start_ip)
        end = ipaddress.IPv4Address(end_ip)
        
        # 确保起始IP小于等于结束IP
        if start > end:
            return {"error": "起始IP地址必须小于或等于结束IP地址"}
        
        # 智能扩展范围，尝试找到包含当前范围的最小子网
        # 将起始IP向左扩展到网络地址，结束IP向右扩展到广播地址
        # 计算当前范围所在的可能子网
        current_range = int(end) - int(start) + 1
        
        # 尝试找到包含整个范围的子网
        expanded_start = start
        expanded_end = end
        
        # 通用处理：尝试找到包含当前范围的最小子网
        # 通过查找起始IP和结束IP的共同超网来确定
        expanded_start = start
        expanded_end = end
        
        # 尝试从/24到/0，找到包含整个范围的最小子网
        for prefix in range(24, -1, -1):
            try:
                network = ipaddress.IPv4Network(f"{start}/{prefix}", strict=False)
                if network.network_address <= start and network.broadcast_address >= end:
                    expanded_start = network.network_address
                    expanded_end = network.broadcast_address
                    break
            except ValueError:
                continue
        
        # 使用ipaddress模块的summary_addresses函数获取CIDR列表
        cidr_list = list(ipaddress.summarize_address_range(expanded_start, expanded_end))
        
        return {
            "start_ip": start_ip,
            "end_ip": end_ip,
            "expanded_start": str(expanded_start),
            "expanded_end": str(expanded_end),
            "cidr_list": [str(cidr) for cidr in cidr_list],
            "cidr_count": len(cidr_list),
            "total_addresses": int(end) - int(start) + 1,
        }
        
    except ValueError as e:
        return handle_ip_subnet_error(e, "IP地址范围计算")


def check_subnet_overlap(subnets):
    """
    检查多个子网之间是否存在重叠
    
    参数:
    subnets: 子网列表，每个子网为CIDR格式字符串
    
    返回:
    包含重叠信息的字典
    """
    try:
        # 验证输入并转换为IPv4Network对象
        ipv4_subnets = []
        for subnet in subnets:
            try:
                ipv4_subnets.append(ipaddress.IPv4Network(subnet, strict=False))
            except ValueError as e:
                return handle_ip_subnet_error(e, "子网重叠检查")
        
        if len(ipv4_subnets) < 2:
            return {"error": "至少需要两个子网来检查重叠"}
        
        overlaps = []
        
        # 比较每对子网之间的关系
        for i in range(len(ipv4_subnets)):
            for j in range(i + 1, len(ipv4_subnets)):
                subnet1 = ipv4_subnets[i]
                subnet2 = ipv4_subnets[j]
                
                if subnet1.overlaps(subnet2):
                    overlaps.append({
                        "subnet1": str(subnet1),
                        "subnet2": str(subnet2),
                        "type": "包含" if subnet1.subnet_of(subnet2) or subnet2.subnet_of(subnet1) else "部分重叠"
                    })
        
        return {
            "subnets": subnets,
            "overlaps": overlaps,
            "has_overlap": len(overlaps) > 0,
            "overlap_count": len(overlaps),
        }
        
    except ValueError as e:
        return handle_ip_subnet_error(e, "子网重叠检查")


# 测试示例
if __name__ == "__main__":
    # 测试IP地址信息获取
    print("=== 测试IP地址信息获取功能 ===")
    ip_info = get_ip_info("192.168.1.1")
    if "error" in ip_info:
        print(f"错误: {ip_info['error']}")
    else:
        print(f"IP地址: {ip_info['ip_address']}")
        print(f"IP分类: {ip_info['class']}")
        print(f"是否私有IP: {ip_info['is_private']}")
        print(f"是否回环地址: {ip_info['is_loopback']}")
        print(f"是否链路本地地址: {ip_info['is_link_local']}")
        print(f"是否组播地址: {ip_info['is_multicast']}")
        print(f"是否保留地址: {ip_info['is_reserved']}")
        print(f"整数表示: {ip_info['integer']}")

    # 测试IP地址范围转CIDR
    print("\n=== 测试IP地址范围转CIDR功能 ===")
    range_result = range_to_cidr("192.168.1.0", "192.168.1.255")
    if "error" in range_result:
        print(f"错误: {range_result['error']}")
    else:
        print(f"起始IP: {range_result['start_ip']}")
        print(f"结束IP: {range_result['end_ip']}")
        print(f"转换后的CIDR列表: {range_result['cidr_list']}")
        print(f"CIDR数量: {range_result['cidr_count']}")
        print(f"总地址数: {range_result['total_addresses']}")

    # 测试子网合并功能
    print("\n=== 测试子网合并功能 ===")
    merge_result = merge_subnets(["192.168.1.0/24", "192.168.2.0/24", "192.168.3.0/24"])
    if "error" in merge_result:
        print(f"错误: {merge_result['error']}")
    else:
        print(f"原始子网列表: {merge_result['original_subnets']}")
        print(f"合并后的子网列表: {merge_result['merged_subnets']}")
        print(f"合并前数量: {merge_result['original_count']}")
        print(f"合并后数量: {merge_result['merged_count']}")

    # 测试子网重叠检查
    print("\n=== 测试子网重叠检查功能 ===")
    overlap_result = check_subnet_overlap(["192.168.1.0/24", "192.168.1.128/25", "192.168.2.0/24"])
    if "error" in overlap_result:
        print(f"错误: {overlap_result['error']}")
    else:
        print(f"检查的子网列表: {overlap_result['subnets']}")
        print(f"是否存在重叠: {overlap_result['has_overlap']}")
        print(f"重叠数量: {overlap_result['overlap_count']}")
        if overlap_result['overlaps']:
            print("重叠详情:")
            for idx, overlap in enumerate(overlap_result['overlaps'], 1):
                print(f"  {idx}. {overlap['subnet1']} 与 {overlap['subnet2']} ({overlap['type']})")
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
    
    # 测试IP信息获取功能
    print("\n=== 测试IP信息获取功能 ===")
    test_ips = ["192.168.1.1", "8.8.8.8", "127.0.0.1", "224.0.0.1"]
    for ip in test_ips:
        ip_info = get_ip_info(ip)
        if "error" in ip_info:
            print(f"{ip}: 错误 - {ip_info['error']}")
        else:
            print(f"{ip}:")
            print(f"  类别: {ip_info['class']}")
            print(f"  私有IP: {ip_info['is_private']}")
            print(f"  回环地址: {ip_info['is_loopback']}")
            print(f"  组播地址: {ip_info['is_multicast']}")
            print(f"  保留地址: {ip_info['is_reserved']}")
    
    # 测试IPv4转IPv6功能
    print("\n=== 测试IPv4转IPv6功能 ===")
    test_ipv4s = ["192.168.1.1", "8.8.8.8", "127.0.0.1"]
    for ipv4 in test_ipv4s:
        ipv6 = ipv4_to_ipv6(ipv4)
        if "error" in ipv6:
            print(f"{ipv4} 转 IPv6 失败: {ipv6['error']}")
        else:
            print(f"{ipv4} -> {ipv6}")
    
    # 测试IPv6转IPv4功能
    print("\n=== 测试IPv6转IPv4功能 ===")
    test_ipv6s = ["::ffff:192.168.1.1", "::ffff:8.8.8.8", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"]
    for ipv6 in test_ipv6s:
        ipv4 = ipv6_to_ipv4(ipv6)
        if isinstance(ipv4, dict) and "error" in ipv4:
            print(f"{ipv6} 转 IPv4 失败: {ipv4['error']}")
        else:
            print(f"{ipv6} -> {ipv4}")
