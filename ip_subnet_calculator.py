#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
子网规划师 - IP子网计算核心

提供IP子网计算的核心功能，包括:
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
import ipaddress
import math
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Pattern, TypedDict, Union

# 导入本地模块
from version import get_version
from i18n import _


class SubnetInfo(TypedDict):
    """子网详细信息类型"""
    network: str
    netmask: str
    wildcard: str
    broadcast: str
    cidr: str
    prefixlen: int
    num_addresses: int
    usable_addresses: int
    host_range_start: str
    host_range_end: str
    version: int


class SplitResult(TypedDict):
    """子网切分结果类型"""
    parent: str
    split: str
    remaining_subnets: List[str]
    parent_info: SubnetInfo
    split_info: SubnetInfo
    remaining_subnets_info: List[SubnetInfo]


class ErrorResult(TypedDict):
    """错误结果类型"""
    error: str


# 错误处理器抽象基类
class ErrorProcessor(ABC):
    """错误处理器抽象基类，定义错误处理的统一接口"""
    
    def can_handle(self, error_msg: str) -> bool:
        """判断是否能处理该错误消息
        
        参数:
            error_msg: 错误消息字符串
            
        返回:
            bool: 如果能处理返回True，否则返回False
            
        抛出:
            TypeError: 如果error_msg不是字符串类型
        """
        if not isinstance(error_msg, str):
            raise TypeError("error_msg must be a string")
        return self._can_handle_impl(error_msg)
    
    @abstractmethod
    def _can_handle_impl(self, error_msg: str) -> bool:
        """具体实现判断是否能处理该错误消息
        
        参数:
            error_msg: 错误消息字符串
            
        返回:
            bool: 如果能处理返回True，否则返回False
        """
        pass
    
    def extract_params(self, error_msg: str) -> Dict[str, str]:
        """从错误消息中提取参数
        
        参数:
            error_msg: 错误消息字符串
            
        返回:
            Dict[str, str]: 提取的参数字典
            
        抛出:
            TypeError: 如果error_msg不是字符串类型
            ValueError: 如果error_msg为空
        """
        if not isinstance(error_msg, str):
            raise TypeError("error_msg must be a string")
        if not error_msg:
            raise ValueError("error_msg cannot be empty")
        return self._extract_params_impl(error_msg)
    
    @abstractmethod
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        """具体实现从错误消息中提取参数
        
        参数:
            error_msg: 错误消息字符串
            
        返回:
            Dict[str, str]: 提取的参数字典
        """
        pass
    
    @abstractmethod
    def get_translation_key(self) -> str:
        """获取翻译键
        
        返回:
            str: 翻译键
        """
        pass


# 全局初始化状态
_ERROR_PROCESSORS_INITIALIZED = False


def _ensure_processors_initialized():
    """确保错误处理器已初始化（惰性初始化）
    
    如果处理器未初始化，则执行初始化，避免模块加载时的副作用
    """
    global _ERROR_PROCESSORS_INITIALIZED
    if not _ERROR_PROCESSORS_INITIALIZED:
        _register_all_processors()
        _ERROR_PROCESSORS_INITIALIZED = True


# 错误处理器注册表
class ErrorProcessorRegistry:
    """错误处理器注册表，管理所有错误处理器"""
    
    def __init__(self):
        self._processors: List[ErrorProcessor] = []
    
    def register(self, processor: ErrorProcessor) -> None:
        """注册错误处理器
        
        参数:
            processor: 错误处理器实例
        """
        self._processors.append(processor)
    
    def find_processor(self, error_msg: str) -> Optional[ErrorProcessor]:
        """查找能够处理该错误消息的处理器
        
        参数:
            error_msg: 错误消息字符串
            
        返回:
            Optional[ErrorProcessor]: 如果找到处理器返回处理器实例，否则返回None
        """
        _ensure_processors_initialized()
        for processor in self._processors:
            if processor.can_handle(error_msg):
                return processor
        return None


# 创建全局注册表实例
_error_processor_registry = ErrorProcessorRegistry()


# 具体错误处理器类


class InvalidSubnetMaskProcessor(ErrorProcessor):
    """无效子网掩码错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "not a valid netmask" in error_msg
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        netmask_match = re.search(r"'([^']+)'", error_msg)
        netmask = netmask_match.group(1) if netmask_match else error_msg.split()[0].strip("'")
        return {"netmask": netmask}
    
    def get_translation_key(self) -> str:
        return 'invalid_subnet_mask'


class InvalidNetworkAddressProcessor(ErrorProcessor):
    """无效网络地址错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "does not appear to be an IPv4 or IPv6 network" in error_msg
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        network_match = re.search(r"'([^']+)'", error_msg)
        network = network_match.group(1) if network_match else "invalid_network"
        return {"network": network}
    
    def get_translation_key(self) -> str:
        return 'invalid_network_address_format'


class InvalidIPAddressProcessor(ErrorProcessor):
    """无效IP地址错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "Invalid IP address:" in error_msg
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        ip_match = re.search(r"Invalid IP address:\s*([^\s]+)", error_msg)
        ip_address = ip_match.group(1) if ip_match else "invalid_ip"
        return {"ip_address": ip_address}
    
    def get_translation_key(self) -> str:
        return 'invalid_ip_address_with_value'


class CIDRHostBitsSetProcessor(ErrorProcessor):
    """CIDR主机位设置错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "has host bits set" in error_msg
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        cidr_match = re.search(r"'([^']+)'", error_msg)
        cidr = cidr_match.group(1) if cidr_match else error_msg.split()[0]
        return {"cidr": cidr}
    
    def get_translation_key(self) -> str:
        return 'cidr_has_host_bits_set'


class InvalidOctetProcessor(ErrorProcessor):
    """无效八位组错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return bool(re.search(r"octet.*?(\d+)", error_msg, re.IGNORECASE))
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        octet_match = re.search(r"octet.*?(\d+)", error_msg, re.IGNORECASE)
        octet = octet_match.group(1) if octet_match else "invalid"
        return {"octet": octet}
    
    def get_translation_key(self) -> str:
        return 'invalid_octet_in_ip'


class InvalidIPv6GroupTooLongProcessor(ErrorProcessor):
    """IPv6组过长错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "At most 4 characters permitted" in error_msg and "IPv6" in error_msg
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        group_match = re.search(r"'([^']+)'", error_msg)
        group = group_match.group(1) if group_match else "invalid_group"
        return {"group": group}
    
    def get_translation_key(self) -> str:
        return 'invalid_ipv6_group_too_long'


class IPv6DoubleColonProcessor(ErrorProcessor):
    """IPv6双冒号错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "At most one '::' permitted" in error_msg
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        address_match = re.search(r"in ['\"]([^'\"]+)['\"]", error_msg)
        address = address_match.group(1) if address_match else error_msg
        return {"address": address}
    
    def get_translation_key(self) -> str:
        return 'invalid_ipv6_double_colon'


class IPv6PartsCountProcessor(ErrorProcessor):
    """IPv6部分数量错误处理器"""
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        return "Expected at most" in error_msg and "IPv6" in error_msg.lower()
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        max_parts_match = re.search(r'Expected at most (\d+)', error_msg)
        max_parts = max_parts_match.group(1) if max_parts_match else '7'
        
        address_match = re.search(r"in ['\"]([^'\"]+)['\"]", error_msg)
        address = address_match.group(1) if address_match else error_msg
        
        return {"max_parts": max_parts, "address": address}
    
    def get_translation_key(self) -> str:
        return 'invalid_ipv6_parts_count'


class SimpleErrorProcessor(ErrorProcessor):
    """简单错误处理器，用于处理不需要额外参数的错误"""
    
    def __init__(self, pattern: Union[str, Pattern[str]], translation_key: str):
        self._pattern = pattern
        self._translation_key = translation_key
    
    def _can_handle_impl(self, error_msg: str) -> bool:
        if isinstance(self._pattern, str):
            return self._pattern in error_msg
        else:
            return bool(self._pattern.search(error_msg))
    
    def _extract_params_impl(self, error_msg: str) -> Dict[str, str]:
        return {}
    
    def get_translation_key(self) -> str:
        return self._translation_key


# 注册所有错误处理器

def _register_all_processors() -> None:
    """注册所有错误处理器到全局注册表"""
    
    # 1. 注册需要参数提取的复杂处理器
    _error_processor_registry.register(InvalidSubnetMaskProcessor())
    _error_processor_registry.register(InvalidNetworkAddressProcessor())
    _error_processor_registry.register(InvalidIPAddressProcessor())
    _error_processor_registry.register(CIDRHostBitsSetProcessor())
    _error_processor_registry.register(InvalidOctetProcessor())
    _error_processor_registry.register(InvalidIPv6GroupTooLongProcessor())
    _error_processor_registry.register(IPv6DoubleColonProcessor())
    _error_processor_registry.register(IPv6PartsCountProcessor())
    
    # 2. 注册不需要参数的简单处理器
    # 定义简单错误模式列表，格式：(匹配模式, 翻译键)
    simple_patterns = [
        # IPv4相关错误
        ("Only decimal digits permitted", 'invalid_ipv4_decimal_digits'),
        ("Unexpected '/'", 'invalid_ipv4_unexpected_slash'),
        ("At most 3 characters permitted", 'invalid_ipv4_octet_too_long'),
        (re.compile(r"expected.*?4 octets", re.IGNORECASE | re.DOTALL), 'invalid_ip_format_4_octets'),
        
        # IPv6相关错误
        ("does not appear to be an IPv6 address", 'invalid_ipv6_address_format'),
        ("at most 4 hex digits per group", 'invalid_ipv6_hex_digits'),
        ("too many colons", 'invalid_ipv6_too_many_colons'),
        ("At most 8 colons permitted", 'invalid_ipv6_too_many_colons'),
        ("Only hex digits permitted", 'invalid_ipv6_hex_only'),
        ("At most 45 characters expected", 'invalid_ipv6_address_too_long'),
        ("Trailing ':' only permitted as part of '::'", 'invalid_ipv6_trailing_colon'),
        ("Exactly 8 parts expected", 'invalid_ipv6_exactly_8_parts'),
        ("parts expected", 'invalid_ipv6_parts_count'),
        (re.compile(r"At most.*?characters permitted", re.IGNORECASE), 'invalid_ipv6_characters_limit'),
        
        # 通用错误
        ("are not of the same version", 'ip_versions_not_compatible'),
        
        # IPv6通用匹配
        (re.compile(r"IPv6|(colon.*?hex)|(hex.*?colon)", re.IGNORECASE), 'invalid_ipv6_format'),
    ]
    
    # 注册简单错误处理器
    for pattern, translation_key in simple_patterns:
        _error_processor_registry.register(SimpleErrorProcessor(pattern, translation_key))


def format_large_number(num, use_scientific=True):
    """格式化大数值，可选择使用科学计数法或千位分隔符
    
    参数:
        num: 要格式化的数值
        use_scientific: 是否使用科学计数法，默认为True
        
    返回:
        str: 格式化后的字符串
    """
    try:
        # 转换为整数
        num = int(num)
        
        # 根据参数决定格式化方式
        if use_scientific and num >= 1000000:  # 10^6
            # 计算科学计数法的实际值，保留2位小数但不四舍五入
            # 使用math模块进行精确计算，避免浮点精度问题
            
            # 计算指数（10的幂次），使用更可靠的方式
            if num == 0:
                exp_int = 0
            else:
                # 使用字符串转换来避免浮点精度问题
                exp_int = len(str(abs(num))) - 1
            
            # 计算系数（保留2位小数的截断值）
            coeff = num / (10 ** exp_int)
            coeff_trunc = math.floor(coeff * 100) / 100
            
            # 计算精确值用于比较
            exact_value = int(coeff_trunc * (10 ** exp_int))
            
            # 使用整数运算计算truncated_num，避免浮点精度误差
            truncated_num = int(coeff_trunc * 100) * (10 ** (exp_int - 2))
            
            # 比较原始数值和精确值，决定符号
            if num == exact_value:
                symbol = "="
            else:
                symbol = "≈"  # 使用Unicode近似符号，保持用户喜欢的格式
            
            # 使用截断后的系数和原始指数重新组合科学计数法字符串
            return f"{symbol}{coeff_trunc:.2f}e+{exp_int:d}"
        else:
            return f"{num:,}"
    except (ValueError, TypeError):
        # 如果转换失败，返回原始值的字符串形式
        return str(num)


# 模块版本号
__version__ = get_version()


def _collect_invalid_subnets(subnets):
    """
    收集无效子网并分类有效子网

    参数:
    subnets: 子网列表，每个子网为CIDR格式字符串

    返回:
    tuple: (ipv4_nets, ipv6_nets, invalid_subnets)
    ipv4_nets: 有效的IPv4子网列表
    ipv6_nets: 有效的IPv6子网列表
    invalid_subnets: 无效子网列表，每个元素包含subnet和error信息
    """
    ipv4_nets = []
    ipv6_nets = []
    invalid_subnets = []
    
    for subnet in subnets:
        try:
            network = ipaddress.ip_network(subnet, strict=False)
            
            # 按IP版本分组
            if isinstance(network, ipaddress.IPv6Network):
                ipv6_nets.append(network)
            else:
                ipv4_nets.append(network)
                
        except ValueError as e:
            # 收集无效子网，使用handle_ip_subnet_error获取详细错误信息
            try:
                error_info = handle_ip_subnet_error(e)
            except (ValueError, TypeError) as ex:
                error_info = {"error": f"处理子网错误时发生异常: {str(ex)}"}
            invalid_subnets.append({
                "subnet": subnet,
                "error": error_info["error"]
            })
    
    return ipv4_nets, ipv6_nets, invalid_subnets


def handle_ip_subnet_error(error) -> ErrorResult:
    """
    通用IP子网错误处理函数

    参数:
        error: 捕获的ValueError异常

    返回:
        包含错误信息的字典
    """
    error_msg = str(error)
    error_type = _("ip_subnet")
    
    # 查找能够处理该错误的处理器
    processor = _error_processor_registry.find_processor(error_msg)
    
    if processor:
        try:
            # 提取参数并格式化错误信息
            params = processor.extract_params(error_msg)
            translation_key = processor.get_translation_key()
            translation = _(translation_key)
            
            if translation and params:
                error_info = translation.format(**params)
            elif translation:
                error_info = translation
            else:
                error_info = f"Error ({translation_key})"
        except Exception as e:
            # 处理器提取参数失败，使用默认错误信息
            error_text = _('error') or "Error"
            error_info = f"{error_type} {error_text}: {error_msg}"
    else:
        # 使用默认错误信息
        error_text = _('error') or "Error"
        error_info = f"{error_type} {error_text}: {error_msg}"
    
    return {"error": error_info}


def ip_to_int(ip_str):
    """
    将IP地址字符串转换为整数，支持IPv4和IPv6

    参数:
    ip_str: IP地址字符串

    返回:
    对应的整数表示
    """
    try:
        # 先检测IP版本
        addr = ipaddress.ip_address(ip_str)
        if addr.version == 4:
            return int(ipaddress.IPv4Address(ip_str))
        else:
            return int(ipaddress.IPv6Address(ip_str))
    except ValueError as e:
        return handle_ip_subnet_error(e)


def int_to_ip(ip_int):
    """
    将整数转换为IP地址字符串，支持IPv4和IPv6

    参数:
    ip_int: IP地址的整数表示

    返回:
    对应的IP地址字符串
    """
    # 先尝试IPv4转换，失败时再尝试IPv6转换，不依赖整数范围判断
    try:
        # 尝试转换为IPv4地址
        return str(ipaddress.IPv4Address(ip_int))
    except ValueError:
        # IPv4转换失败，尝试IPv6转换
        try:
            return str(ipaddress.IPv6Address(ip_int))
        except ValueError as e:
            # 处理IPv6转换失败的情况，与ip_to_int保持一致
            return handle_ip_subnet_error(e)


def ipv4_to_ipv6(ipv4_str):
    """
    将IPv4地址转换为IPv6地址(IPv4映射格式)

    参数:
    ipv4_str: IPv4地址字符串

    返回:
    IPv6地址字符串(::ffff:ipv4格式)
    """
    try:
        # 验证IPv4地址格式
        ipaddress.IPv4Address(ipv4_str)
        # 返回IPv4映射的IPv6地址
        return f"::ffff:{ipv4_str}"
    except ValueError as e:
        return handle_ip_subnet_error(e)


def ipv6_to_ipv4(ipv6_str):
    """
    将IPv6地址转换为IPv4地址(仅支持IPv4映射格式)

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
        return {"error": f"{ipv6_str} {_('is_not_ipv4_mapped_ipv6_address')}"}
    except ValueError as e:
        return handle_ip_subnet_error(e)


def get_subnet_info(network_str) -> Union[SubnetInfo, ErrorResult]:
    """
    获取子网的详细信息，支持IPv4和IPv6
    """
    try:
        # 使用ipaddress.ip_network自动检测IP版本，支持IPv4和IPv6
        network = ipaddress.ip_network(network_str, strict=False)
        is_ipv6 = isinstance(network, ipaddress.IPv6Network)

        # 计算通配符掩码：子网掩码的反码
        if is_ipv6:
            # IPv6处理：直接使用network.hostmask获取主机掩码
            wildcard_mask = str(network.hostmask)
        else:
            # IPv4处理
            wildcard = ~int(network.netmask) & 0xFFFFFFFF
            wildcard_mask = int_to_ip(wildcard)

        # 计算可用主机范围和数量
        if is_ipv6:
            # IPv6没有广播地址，所有地址都是可用的，除了网络地址
            if network.num_addresses == 1:
                # /128子网，只有一个地址，可用地址数为1
                usable_addresses = 1
                host_range_start = str(network.network_address)
                host_range_end = str(network.network_address)
            elif network.num_addresses == 2:
                # /127子网，有2个地址，都可用
                usable_addresses = 2
                host_range_start = str(network.network_address)
                host_range_end = str(network.network_address + 1)
            else:
                # 所有其他IPv6子网，可用地址数 = 总地址数 - 1（仅减去网络地址）
                usable_addresses = network.num_addresses - 1
                host_range_start = str(network.network_address + 1)
                host_range_end = str(network.network_address + network.num_addresses - 1)
        else:
            # IPv4处理
            if network.num_addresses == 1:
                # /32子网，只有一个地址，可用地址数为1
                usable_addresses = 1
                host_range_start = str(network.network_address)
                host_range_end = str(network.network_address)
            elif network.num_addresses == 2:
                # /31子网，只有网络地址和广播地址，没有可用主机地址
                usable_addresses = 0
                host_range_start = str(network.network_address)
                host_range_end = str(network.broadcast_address)
            else:
                # 其他情况，可用地址数 = 总地址数 - 2（网络地址和广播地址）
                usable_addresses = network.num_addresses - 2
                host_range_start = str(network.network_address + 1)
                host_range_end = str(network.broadcast_address - 1)

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
            "host_range_end": host_range_end,
            "version": 6 if is_ipv6 else 4
        }
    except (ValueError, TypeError) as e:
        return handle_ip_subnet_error(e)


def split_subnet(parent_cidr, split_cidr) -> Union[SplitResult, ErrorResult]:
    """
    将split_cidr从parent_cidr中切分出来，返回剩余的子网列表
    
    参数:
    parent_cidr: 父网段，支持IPv4和IPv6格式
    split_cidr: 要切分的子网，支持IPv4和IPv6格式
    
    返回:
    包含切分结果的字典，支持IPv4和IPv6
    """
    try:
        # 使用ipaddress.ip_network自动检测IP版本，支持IPv4和IPv6
        parent_net = ipaddress.ip_network(parent_cidr, strict=False)
        split_net = ipaddress.ip_network(split_cidr, strict=False)

        # 检查split_net是否是parent_net的子网
        if not split_net.subnet_of(parent_net):
            # 直接使用翻译键的完整句子和变量占位符
            error_msg = _('is_not_a_subnet_of').format(split_cidr=split_cidr, parent_cidr=parent_cidr)
            return {"error": error_msg}

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

    except (ValueError, TypeError) as e:
        return handle_ip_subnet_error(e)


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
                    # 使用完整翻译键和变量占位符
                    translation = _('cannot_create_subnet_for')
                    error_msg = translation.format(name=required['name'], prefix=new_prefix) if translation else f"Cannot create subnet for {required['name']} with prefix {new_prefix}"
                    return False, None, None, error_msg

                # 计算剩余子网
                remaining = list(available.address_exclude(new_subnet))
                updated_available = available_subnets.copy()
                updated_available.pop(i)
                updated_available.extend(remaining)
                updated_available.sort()

                return True, new_subnet, updated_available, None
            except ValueError as e:
                translation = _('failed_to_create_subnet')
                return False, None, None, (translation + ": " + str(e)) if translation else f"Failed to create subnet: {e}"

    # 使用完整翻译键和变量占位符
    translation = _('cannot_allocate_sufficiently_large_subnet_for')
    error_msg = translation.format(name=required['name']) if translation else f"Cannot allocate sufficiently large subnet for {required['name']}"
    return False, None, None, error_msg


def suggest_subnet_planning(parent_cidr, required_subnets):
    """
    子网规划智能建议功能，支持IPv4和IPv6

    参数:
    parent_cidr: 父网段，格式为CIDR (例如: "10.0.0.0/8" 或 "2001:0db8::/32")
    required_subnets: 需要的子网列表，每个子网包含name和hosts两个字段

    返回:
    包含建议子网规划的字典，可能包含多个方案
    """
    try:
        # 使用ipaddress.ip_network自动检测IP版本，支持IPv4和IPv6
        parent_net = ipaddress.ip_network(parent_cidr, strict=False)
        is_ipv6 = isinstance(parent_net, ipaddress.IPv6Network)
        address_bits = 128 if is_ipv6 else 32

        # 预处理子网需求：计算前缀长度
        processed_subnets = []
        for subnet in required_subnets:
            # 计算需要的地址数量和前缀长度
            if is_ipv6:
                # IPv6没有广播地址，只需要考虑网络地址
                required_addresses = subnet["hosts"] + 1
            else:
                # IPv4需要考虑网络地址和广播地址
                required_addresses = subnet["hosts"] + 2
            
            prefix_len = address_bits - (required_addresses - 1).bit_length()
            prefix_len = max(prefix_len, parent_net.prefixlen)
            prefix_len = min(prefix_len, address_bits)

            processed_subnets.append({
                "name": subnet["name"],
                "hosts": subnet["hosts"],
                "prefix_len": prefix_len
            })

        # 生成多种分配方案
        plans = []
        
        # 方案1：按主机数量从大到小排序（传统方法）
        plan1 = _generate_plan(parent_net, processed_subnets, sort_key=lambda x: x["hosts"], reverse=True, name="按主机数量排序")
        if "error" not in plan1:
            plans.append(plan1)
        
        # 方案2：按前缀长度从小到大排序（更均匀分配）
        plan2 = _generate_plan(parent_net, processed_subnets, sort_key=lambda x: x["prefix_len"], reverse=False, name="按前缀长度排序")
        if "error" not in plan2:
            plans.append(plan2)
        
        # 方案3：混合排序（大主机优先，同级别按名称排序）
        plan3 = _generate_plan(parent_net, processed_subnets, sort_key=lambda x: (x["hosts"], x["name"]), reverse=True, name="混合排序")
        if "error" not in plan3:
            plans.append(plan3)

        # 为每个方案评分
        for plan in plans:
            plan["score"] = _score_plan(plan, parent_net)
            plan["score_explanation"] = _explain_score(plan, parent_net)

        # 按评分排序
        plans.sort(key=lambda x: x["score"], reverse=True)

        # 如果没有生成任何方案，返回错误
        if not plans:
            return {"error": _("failed_to_generate_any_plan")}

        return {
            "parent_cidr": parent_cidr,
            "required_subnets": required_subnets,
            "plans": plans,
            "ip_version": "IPv6" if is_ipv6 else "IPv4"
        }

    except ValueError as e:
        return handle_ip_subnet_error(e)


def _generate_plan(parent_net, required_subnets, sort_key, reverse, name):
    """
    生成单个子网规划方案

    参数:
    parent_net: 父网络对象
    required_subnets: 处理后的子网需求
    sort_key: 排序键函数
    reverse: 是否倒序排序
    name: 方案名称

    返回:
    包含规划方案的字典
    """
    # 复制并排序子网需求
    sorted_subnets = sorted(required_subnets.copy(), key=sort_key, reverse=reverse)
    
    # 开始分配子网
    available_subnets = [parent_net]
    allocated_subnets = []

    for required in sorted_subnets:
        # 调用辅助函数分配子网
        success, new_subnet, updated_available, error = _allocate_subnet(available_subnets, required)

        if not success:
            return {"error": error}

        # 分配成功，更新状态
        if updated_available is not None:
            available_subnets = updated_available
        subnet_info = get_subnet_info(str(new_subnet)) if new_subnet else None
        if subnet_info and new_subnet:
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
        "name": name,
        "allocated_subnets": allocated_subnets,
        "remaining_subnets": remaining_subnets,
        "remaining_subnets_info": remaining_subnets_info
    }


def _score_plan(plan, parent_net):
    """
    为子网规划方案评分

    参数:
    plan: 规划方案
    parent_net: 父网络对象

    返回:
    评分（0-100）
    """
    score = 0
    
    # 1. 地址利用率评分（40分）
    total_required_hosts = sum(subnet["required_hosts"] for subnet in plan["allocated_subnets"])
    total_available_hosts = sum(subnet["available_hosts"] for subnet in plan["allocated_subnets"])
    if total_available_hosts > 0:
        utilization = total_required_hosts / total_available_hosts
        utilization_score = min(utilization * 40, 40)
        score += utilization_score
    
    # 2. 剩余子网数量评分（20分）- 剩余子网越少越好
    remaining_count = len(plan["remaining_subnets"])
    if remaining_count == 0:
        score += 20
    elif remaining_count <= 2:
        score += 15
    elif remaining_count <= 5:
        score += 10
    else:
        score += 5
    
    # 3. 子网连续性评分（20分）- 分配的子网越连续越好
    # 这里简化处理，假设按顺序分配的子网更连续
    score += 20
    
    # 4. 管理便利性评分（20分）
    # 基于子网大小的一致性
    prefix_lengths = [subnet["info"]["prefixlen"] for subnet in plan["allocated_subnets"]]
    unique_prefixes = len(set(prefix_lengths))
    if unique_prefixes == 1:
        score += 20
    elif unique_prefixes <= 3:
        score += 15
    elif unique_prefixes <= 5:
        score += 10
    else:
        score += 5
    
    return int(score)


def _explain_score(plan, parent_net):
    """
    解释方案评分

    参数:
    plan: 规划方案
    parent_net: 父网络对象

    返回:
    评分解释
    """
    explanations = []
    
    # 1. 地址利用率
    total_required_hosts = sum(subnet["required_hosts"] for subnet in plan["allocated_subnets"])
    total_available_hosts = sum(subnet["available_hosts"] for subnet in plan["allocated_subnets"])
    if total_available_hosts > 0:
        utilization = total_required_hosts / total_available_hosts
        utilization_percent = int(utilization * 100)
        explanations.append(f"地址利用率: {utilization_percent}% (满分40分)")
    
    # 2. 剩余子网数量
    remaining_count = len(plan["remaining_subnets"])
    explanations.append(f"剩余子网数量: {remaining_count} (满分20分)")
    
    # 3. 子网连续性
    explanations.append("子网连续性: 良好 (满分20分)")
    
    # 4. 管理便利性
    prefix_lengths = [subnet["info"]["prefixlen"] for subnet in plan["allocated_subnets"]]
    unique_prefixes = len(set(prefix_lengths))
    explanations.append(f"管理便利性: {unique_prefixes} 种不同前缀长度 (满分20分)")
    
    return explanations


def merge_subnets(subnets):
    """
    将多个连续子网合并为更大的子网，支持IPv4和IPv6

    参数:
    subnets: 子网列表，每个子网为CIDR格式字符串

    返回:
    包含合并结果的字典
    """
    try:
        # 验证输入是否为空
        if not subnets or len(subnets) == 0:
            return {"error": _('subnet_list_cannot_be_empty')}

        # 验证输入并按IP版本分组
        ipv4_nets, ipv6_nets, invalid_subnets = _collect_invalid_subnets(subnets)
        
        # 允许分别合并不同IP版本的子网（即使有无效子网也继续处理有效子网）
        
        # 合并函数：对单个IP版本的子网列表进行合并，支持不同前缀长度的子网合并
        def merge_single_version(networks):
            if not networks:
                return []
            
            # 按网络地址排序
            networks.sort()
            
            merged = []
            
            # 简单的合并策略：先尝试合并相同前缀长度的连续子网
            # 这是一个更可靠的合并策略，可以避免过度合并
            temp_merged = []
            
            for network in networks:
                if not temp_merged:
                    temp_merged.append(network)
                else:
                    last = temp_merged[-1]
                    
                    # 只尝试合并相同前缀长度的连续子网
                    if last.prefixlen == network.prefixlen:
                        # 计算合并后的前缀长度
                        new_prefix = last.prefixlen - 1
                        
                        # 尝试创建超网
                        try:
                            # 使用网络地址和新前缀创建超网
                            supernet = ipaddress.ip_network(f"{last.network_address}/{new_prefix}", strict=False)
                            
                            # 检查两个子网是否都完全包含在超网中
                            # 并且超网的地址空间正好是两个子网的总和
                            if (last.subnet_of(supernet) 
                                    and network.subnet_of(supernet) 
                                    and supernet.num_addresses == last.num_addresses + network.num_addresses):
                                # 检查两个子网是否连续
                                last_merged_last = int(last.network_address) + last.num_addresses - 1
                                subnet_first = int(network.network_address)
                                
                                if last_merged_last + 1 == subnet_first:
                                    # 可以合并，替换最后一个网络为超网
                                    temp_merged.pop()
                                    temp_merged.append(supernet)
                                else:
                                    # 不连续，直接添加
                                    temp_merged.append(network)
                            else:
                                # 不能合并，直接添加
                                temp_merged.append(network)
                        except ValueError:
                            # 创建超网失败，直接添加
                            temp_merged.append(network)
                    else:
                        # 前缀长度不同，直接添加
                        temp_merged.append(network)
            
            # 对临时合并结果进行第二轮合并，处理可能的连续超网
            merged = []
            
            for network in temp_merged:
                if not merged:
                    merged.append(network)
                else:
                    last = merged[-1]
                    
                    # 尝试合并连续的超网
                    try:
                        # 计算合并后的前缀长度
                        new_prefix = last.prefixlen - 1
                        
                        # 尝试创建超网
                        supernet = ipaddress.ip_network(f"{last.network_address}/{new_prefix}", strict=False)
                        
                        # 检查两个网络是否都在超网范围内，且超网正好包含它们
                        if (last.subnet_of(supernet) and network.subnet_of(supernet) and supernet.num_addresses == last.num_addresses + network.num_addresses):
                            # 检查两个网络是否连续
                            last_merged_last = int(last.network_address) + last.num_addresses - 1
                            subnet_first = int(network.network_address)
                            
                            if last_merged_last + 1 == subnet_first:
                                # 可以合并，替换最后一个网络为超网
                                merged.pop()
                                merged.append(supernet)
                            else:
                                # 不连续，直接添加
                                merged.append(network)
                        else:
                            # 不能合并，直接添加
                            merged.append(network)
                    except ValueError:
                        # 创建超网失败，直接添加
                        merged.append(network)
            
            return merged
        
        # 分别合并IPv4和IPv6子网
        merged_ipv4 = merge_single_version(ipv4_nets)
        merged_ipv6 = merge_single_version(ipv6_nets)
        
        # 合并结果
        all_merged = merged_ipv4 + merged_ipv6
        
        # 转换回字符串格式
        merged_str = [str(subnet) for subnet in all_merged]
        
        # 生成结果信息
        merged_info = [get_subnet_info(str(subnet)) for subnet in all_merged]
        
        result = {
            "original_subnets": subnets,
            "merged_subnets": merged_str,
            "merged_subnets_info": merged_info,
            "merged_count": len(all_merged),
            "original_count": len(subnets),
            "ip_version": "mixed" if ipv4_nets and ipv6_nets else ("IPv4" if ipv4_nets else "IPv6"),
            "ipv4_merged_count": len(merged_ipv4),
            "ipv6_merged_count": len(merged_ipv6)
        }
        
        # 如果有无效子网，添加到结果中
        if invalid_subnets:
            result["error"] = _('invalid_subnet_format').format(subnets=', '.join([item["subnet"] for item in invalid_subnets]))
            result["invalid_subnets"] = invalid_subnets
        
        return result

    except ValueError as e:
        return handle_ip_subnet_error(e)


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
                
                # 计算可用主机数量
                if total_hosts == 1:
                    # /32子网，只有一个地址，可用地址数为1
                    usable_hosts = 1
                    first_host = str(network.network_address)
                    last_host = str(network.network_address)
                elif total_hosts == 2:
                    # /31子网，只有网络地址和广播地址，没有可用主机地址
                    usable_hosts = 0
                    first_host = str(network.network_address)
                    last_host = str(network.broadcast_address)
                else:
                    # 其他情况，可用地址数 = 总地址数 - 2（网络地址和广播地址）
                    usable_hosts = total_hosts - 2
                    first_host = str(network.network_address + 1)
                    last_host = str(network.broadcast_address - 1)
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
            first_octet = int(str(ip).split('.', maxsplit=1)[0])
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

            # 计算地址段详细信息
            segments = str(ip).split(".")
            segment_details = []
            for i, segment in enumerate(segments):
                if segment:
                    dec_value = int(segment)
                    bin_value = f"{dec_value:08b}"
                    hex_value = f"{dec_value:02x}"
                    segment_details.append({
                        "index": i + 1,
                        "segment": segment,
                        "decimal": dec_value,
                        "binary": bin_value,
                        "hexadecimal": hex_value
                    })

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
                "segment_details": segment_details
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
                
                # 计算可用主机数量（IPv6规则）
                if total_hosts == 1:
                    # /128子网，只有一个地址，可用地址数为1
                    usable_hosts = 1
                    first_host = str(network.network_address)
                    last_host = str(network.network_address)
                else:
                    # 所有其他IPv6子网，可用地址数 = 总地址数 - 1（只减去网络地址，IPv6没有广播地址）
                    usable_hosts = total_hosts - 1
                    first_host = str(network.network_address + 1)
                    last_host = str(network.network_address + total_hosts - 1)
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

            # 计算RFC参考信息
            ip_address_str = str(ip)
            rfc_ref = ""
            if ip.is_multicast:
                rfc_ref = "RFC 4291, RFC 3306"
            elif ip_address_str.startswith("fe80:"):
                rfc_ref = "RFC 4291"
            elif ip_address_str.startswith("fc00:") or ip_address_str.startswith("fd00:"):
                rfc_ref = "RFC 4193"
            elif ip_address_str.startswith("2000:") or ip_address_str.startswith("2001:") or ip_address_str.startswith("2002:"):
                rfc_ref = "RFC 4291, RFC 7454"
            elif "::ffff:" in ip_address_str:
                rfc_ref = "RFC 4291"
            elif ip_address_str.startswith("64:ff9b::"):
                rfc_ref = "RFC 6052"
            elif ip_address_str.startswith("2001:0db8::"):
                rfc_ref = "RFC 3849"
            elif ip_address_str.startswith("100::"):
                rfc_ref = "RFC 6666"
            elif ip_address_str.startswith("2001:10::"):
                rfc_ref = "RFC 4843, RFC 7343"
            elif ip.is_loopback or ip.is_unspecified:
                rfc_ref = "RFC 4291"
            elif ip_address_str.startswith("fec0:"):
                rfc_ref = "RFC 3879"

            # 计算地址类型
            address_type = "unknown"
            if ip.is_loopback:
                address_type = "loopback_address"
            elif ip.is_unspecified:
                address_type = "unspecified_address"
            elif ip.is_multicast:
                address_type = "multicast_address"
            elif ip.is_link_local:
                address_type = "link_local_unicast_address"
            elif ip_address_str.startswith("fc00:") or ip_address_str.startswith("fd00:"):
                address_type = "unique_local_unicast_address"
            elif ip_address_str.startswith("2001:0db8:"):
                address_type = "documentation_test_address"
            elif ip_address_str.startswith("2000:"):
                address_type = "global_unicast_address"
            elif "::ffff:" in ip_address_str:
                address_type = "ipv4_mapped_ipv6_address"

            # 计算前缀分析
            prefix_analysis = ""
            if ip.is_multicast:
                prefix_analysis = "multicast_prefix"
                if ip_address_str.startswith("ff01:"):
                    prefix_analysis += " interface_local_multicast"
                elif ip_address_str.startswith("ff02:"):
                    prefix_analysis += " link_local_multicast"
                elif ip_address_str.startswith("ff05:"):
                    prefix_analysis += " site_local_multicast"
                elif ip_address_str.startswith("ff0e:"):
                    prefix_analysis += " global_multicast"
                else:
                    prefix_analysis += " other_multicast_type"
            elif ip_address_str.startswith("fe80:"):
                prefix_analysis = "link_local_prefix"
            elif ip_address_str.startswith("fc00:") or ip_address_str.startswith("fd00:"):
                prefix_analysis = "unique_local_prefix"
            elif ip_address_str.startswith("2000:") or ip_address_str.startswith("2001:") or ip_address_str.startswith("2002:"):
                prefix_analysis = "global_unicast_prefix"
            elif ip_address_str.startswith("::ffff:"):
                prefix_analysis = "ipv4_mapped_prefix"
            elif ip_address_str.startswith("64:ff9b::"):
                prefix_analysis = "ipv4_ipv6_translation_prefix"
            elif ip_address_str.startswith("2001:db8::"):
                prefix_analysis = "documentation_prefix"
            elif ip_address_str == "::1":
                prefix_analysis = "loopback_address"
            elif ip_address_str == "::":
                prefix_analysis = "unspecified_address"
            elif ip_address_str.startswith("100::"):
                prefix_analysis = "blackhole_prefix"
            elif ip_address_str.startswith("2001:10::"):
                prefix_analysis = "orchid_prefix"
            elif ip_address_str.startswith("fec0:"):
                prefix_analysis = "deprecated_site_local_prefix"
            else:
                if ip.is_global:
                    prefix_analysis = "global_unicast_prefix_generic"
                elif ip.is_private:
                    prefix_analysis = "private_prefix"
                elif ip.is_link_local:
                    prefix_analysis = "link_local_prefix_generic"
                else:
                    prefix_analysis = "unknown_prefix"

            # 计算地址段详细信息
            segments = ip.exploded.split(":")
            segment_details = []
            for i, segment in enumerate(segments):
                if segment:
                    dec_value = int(segment, 16)
                    bin_value = f"{dec_value:016b}"
                    segment_details.append({
                        "index": i + 1,
                        "segment": segment,
                        "decimal": dec_value,
                        "binary": bin_value
                    })
                else:
                    segment_details.append({
                        "index": i + 1,
                        "segment": "",
                        "decimal": 0,
                        "binary": "0000000000000000"
                    })

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
                "rfc_reference": rfc_ref,
                "address_type": address_type,
                "prefix_analysis": prefix_analysis,
                "segment_details": segment_details
            }

    except ValueError as e:
        return handle_ip_subnet_error(e)


def range_to_cidr(start_ip, end_ip):
    """
    将IP地址范围转换为CIDR表示法，支持IPv4和IPv6

    参数:
    start_ip: 起始IP地址字符串
    end_ip: 结束IP地址字符串

    返回:
    包含CIDR列表的字典
    """
    try:
        # 自动检测IP版本，支持IPv4和IPv6
        # 先确定起始IP的版本
        is_ipv4 = False
        is_ipv6 = False
        
        try:
            # 尝试IPv4
            start = ipaddress.IPv4Address(start_ip)
            is_ipv4 = True
        except ValueError:
            # 尝试IPv6
            try:
                start = ipaddress.IPv6Address(start_ip)
                is_ipv6 = True
            except ValueError:
                # 起始IP格式无效
                return handle_ip_subnet_error(ValueError(f"Invalid IP address: {start_ip}"))
        
        # 确保结束IP与起始IP版本一致
        if is_ipv4:
            try:
                end = ipaddress.IPv4Address(end_ip)
            except ValueError:
                # 结束IP与起始IP版本不一致
                return {"error": _('different_ip_versions_cannot_be_converted')}
        else:
            try:
                end = ipaddress.IPv6Address(end_ip)
            except ValueError:
                # 结束IP与起始IP版本不一致
                return {"error": _('different_ip_versions_cannot_be_converted')}

        # 确保起始IP小于等于结束IP
        if start > end:
            return {"error": _('start_ip_must_be_less_than_or_equal_to_end_ip')}
        
        # 检查是否为IPv6且地址类型差异太大，无法合并
        if is_ipv6:
            # 检查是否为不同类型的IPv6地址（如全局地址和链路本地地址）
            start_is_link_local = start.is_link_local
            end_is_link_local = end.is_link_local
            start_is_global = start.is_global
            end_is_global = end.is_global
            
            # 检查地址类型是否匹配
            if (start_is_link_local != end_is_link_local 
                    or start_is_global != end_is_global):
                return {"error": _('ipv6_address_type_mismatch')}

        if not is_ipv6:
            max_prefix = 32
            NetworkClass = ipaddress.IPv4Network
        else:
            max_prefix = 128
            NetworkClass = ipaddress.IPv6Network
        
        best_network = None
        for prefix_len in range(max_prefix, 0, -1):
            try:
                network = NetworkClass(f"{start}/{prefix_len}", strict=False)
                if network.network_address <= start and network.broadcast_address >= end:
                    best_network = network
                    break
            except ValueError:
                continue
        
        if not best_network:
            return {"error": _('cannot_convert_cross_class_network')}

        expanded_start = best_network.network_address
        expanded_end = best_network.broadcast_address

        try:
            cidr_list = list(ipaddress.summarize_address_range(expanded_start, expanded_end))
        except ValueError as e:
            return {"error": f"无法合并IP范围: {str(e)}"}

        if not cidr_list:
            return {"error": "无法合并IP范围，起始地址和结束地址可能不属于同一网络类型"}

        return {
            "start_ip": start_ip,
            "end_ip": end_ip,
            "cidr_list": [str(cidr) for cidr in cidr_list],
            "cidr_count": len(cidr_list),
            "total_addresses": int(end) - int(start) + 1,
            "ip_version": "IPv6" if is_ipv6 else "IPv4"
        }

    except ValueError as e:
        return handle_ip_subnet_error(e)


def _check_overlaps_in_networks(networks):
    """
    检查同一IP版本的子网列表之间是否存在重叠

    参数:
    networks: 子网对象列表，必须为同一IP版本

    返回:
    包含重叠信息的列表
    """
    overlaps = []
    for i in range(len(networks)):
        for j in range(i + 1, len(networks)):
            subnet1, subnet2 = networks[i], networks[j]
            if subnet1.overlaps(subnet2):
                # 对于CIDR子网，任何重叠必然是包含关系
                if subnet1.subnet_of(subnet2):
                    overlap_type = f"{subnet1} {_('contained_in')} {subnet2}"
                    overlaps.append({
                        "subnet1": str(subnet1),
                        "subnet2": str(subnet2),
                        "type": overlap_type
                    })
                elif subnet2.subnet_of(subnet1):
                    overlap_type = f"{subnet2} {_('contained_in')} {subnet1}"
                    overlaps.append({
                        "subnet1": str(subnet2),
                        "subnet2": str(subnet1),
                        "type": overlap_type
                    })
    return overlaps


def check_subnet_overlap(subnets):
    """
    检查多个子网之间是否存在重叠，支持IPv4和IPv6

    参数:
    subnets: 子网列表，每个子网为CIDR格式字符串

    返回:
    包含重叠信息的字典
    """
    try:
        # 验证输入并按IP版本分类
        ipv4_networks, ipv6_networks, invalid_subnets = _collect_invalid_subnets(subnets)
        
        # 如果有无效子网，返回详细的错误信息
        if invalid_subnets:
            return {
                "error": _('invalid_subnet_format').format(subnets=', '.join([item["subnet"] for item in invalid_subnets])),
                "invalid_subnets": invalid_subnets
            }

        # 检查是否至少有两个有效子网
        if len(ipv4_networks) + len(ipv6_networks) < 2:
            return {'error': _('at_least_two_subnets_needed_to_check_overlap')}

        overlaps = []

        # 检查IPv4子网之间的重叠
        overlaps.extend(_check_overlaps_in_networks(ipv4_networks))

        # 检查IPv6子网之间的重叠
        overlaps.extend(_check_overlaps_in_networks(ipv6_networks))

        # 确定返回的IP版本信息
        ip_version = None
        if ipv4_networks and not ipv6_networks:
            ip_version = "IPv4"
        elif ipv6_networks and not ipv4_networks:
            ip_version = "IPv6"
        elif ipv4_networks and ipv6_networks:
            ip_version = "mixed"

        return {
            "subnets": subnets,
            "overlaps": overlaps,
            "has_overlap": len(overlaps) > 0,
            "overlap_count": len(overlaps),
            "ip_version": ip_version
        }

    except ValueError as e:
        return handle_ip_subnet_error(e)


# 测试示例
if __name__ == "__main__":
    pass
