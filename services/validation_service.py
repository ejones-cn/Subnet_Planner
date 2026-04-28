import ipaddress
from typing import Any

from i18n import _
from ip_subnet_calculator import handle_ip_subnet_error


class ValidationService:
    def __init__(self, app: Any = None):
        self.app: Any = app

    def validate_cidr(self, cidr_str, ip_version=None, require_prefix=None):
        """统一的CIDR验证核心方法

        Args:
            cidr_str: 要验证的CIDR字符串
            ip_version: 可选的IP版本字符串，如"IPv4"或"IPv6"
            require_prefix: 前缀要求模式:
                - None: 带不带前缀都可以（默认）
                - True: 必须带前缀（如 10.0.0.0/8）
                - False: 必须不带前缀（纯IP地址，如 10.0.0.1）

        Returns:
            验证结果字典: {'valid': bool, 'error': str, 'version': int}
        """
        text = cidr_str.strip()
        
        if not text:
            return {'valid': True, 'error': None, 'version': None}
        
        has_prefix = '/' in text
        
        # 检查前缀要求
        if require_prefix is True and not has_prefix:
            return {'valid': False, 'error': _("prefix_required"), 'version': None}
        elif require_prefix is False and has_prefix:
            return {'valid': False, 'error': _("prefix_not_allowed"), 'version': None}
        
        try:
            if has_prefix:
                # CIDR格式验证
                network = ipaddress.ip_network(text, strict=False)
                version = network.version
                
                if ip_version:
                    expected_version = 6 if ip_version == "IPv6" else 4
                    if network.version != expected_version:
                        return {
                            'valid': False,
                            'error': _("ip_version_mismatch"),
                            'version': version
                        }
                return {'valid': True, 'error': None, 'version': version}
            else:
                # 纯IP地址验证
                addr = ipaddress.ip_address(text)
                version = addr.version
                
                if ip_version:
                    expected_version = 6 if ip_version == "IPv6" else 4
                    if addr.version != expected_version:
                        return {
                            'valid': False,
                            'error': _("ip_version_mismatch"),
                            'version': version
                        }
                return {'valid': True, 'error': None, 'version': version}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'valid': False, 'error': error_result.get('error', str(e)), 'version': None}

    def validate_ip_address(self, ip_str, ip_version=None):
        if not ip_str:
            return {'valid': True, 'error': None, 'version': None}

        try:
            addr = ipaddress.ip_address(ip_str)
            version = addr.version
            if ip_version:
                expected_version = 6 if ip_version == "IPv6" else 4
                if addr.version != expected_version:
                    return {
                        'valid': False,
                        'error': _("ip_version_mismatch"),
                        'version': version
                    }
            return {'valid': True, 'error': None, 'version': version}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'valid': False, 'error': error_result.get('error', str(e)), 'version': None}

    def validate_split_input(self, parent, split):
        if not parent:
            return {
                'valid': False,
                'error': _("please_enter_parent_network"),
                'error_code': 'empty_parent'
            }

        if not split:
            return {
                'valid': False,
                'error': _("please_enter_split_segment"),
                'error_code': 'empty_split'
            }

        try:
            ipaddress.ip_network(parent, strict=False)
        except ValueError:
            return {
                'valid': False,
                'error': _("invalid_parent_network_cidr"),
                'error_code': 'invalid_parent'
            }

        try:
            ipaddress.ip_network(split, strict=False)
        except ValueError:
            return {
                'valid': False,
                'error': _("invalid_split_segment_cidr"),
                'error_code': 'invalid_split'
            }

        return {'valid': True, 'error': None, 'error_code': None}

    def validate_planning_input(self, parent):
        if not parent:
            return {
                'valid': False,
                'error': _("please_enter_parent_network"),
                'error_code': 'empty_parent'
            }

        try:
            ipaddress.ip_network(parent, strict=False)
        except ValueError:
            return {
                'valid': False,
                'error': _("invalid_parent_network_cidr"),
                'error_code': 'invalid_parent'
            }

        return {'valid': True, 'error': None, 'error_code': None}

    def validate_requirements(self, requirements):
        if not requirements:
            return {
                'valid': False,
                'error': _("please_add_at_least_one_requirement"),
                'error_code': 'empty_requirements'
            }

        for _name, hosts in requirements:
            try:
                hosts_int = int(hosts)
                if hosts_int <= 0:
                    return {
                        'valid': False,
                        'error': _("host_count_must_be_positive"),
                        'error_code': 'invalid_hosts'
                    }
            except (ValueError, TypeError):
                return {
                    'valid': False,
                    'error': _("invalid_host_count"),
                    'error_code': 'invalid_hosts'
                }

        return {'valid': True, 'error': None, 'error_code': None}

    def is_valid_ipv4(self, ip_address: str) -> bool:
        """验证是否为有效的IPv4地址
        
        Args:
            ip_address: 要验证的IP地址字符串
            
        Returns:
            bool: 是否为有效的IPv4地址
        """
        result = self.validate_ip_address(ip_address, ip_version="IPv4")
        return bool(result['valid'])

    def is_valid_ipv6(self, ip_address: str) -> bool:
        """验证是否为有效的IPv6地址
        
        Args:
            ip_address: 要验证的IP地址字符串
            
        Returns:
            bool: 是否为有效的IPv6地址
        """
        result = self.validate_ip_address(ip_address, ip_version="IPv6")
        return bool(result['valid'])

    def is_ip_in_network(self, ip_address: str, network: str) -> bool:
        """检查IP地址是否在指定的网络范围内
        
        Args:
            ip_address: 要检查的IP地址
            network: 网络地址（CIDR格式）
            
        Returns:
            bool: IP地址是否在网络范围内
        """
        try:
            ip = ipaddress.ip_address(ip_address.strip())
            net = ipaddress.ip_network(network.strip(), strict=False)
            return ip in net
        except ValueError:
            return False

    def get_ip_version(self, ip_or_network: str) -> int | None:
        """获取IP地址或网络的版本
        
        Args:
            ip_or_network: IP地址或网络字符串
            
        Returns:
            int | None: IP版本（4或6），如果无效则返回None
        """
        try:
            if '/' in ip_or_network:
                net = ipaddress.ip_network(ip_or_network.strip(), strict=False)
                return net.version
            else:
                addr = ipaddress.ip_address(ip_or_network.strip())
                return addr.version
        except ValueError:
            return None

    def detect_ip_version(self, ip_or_network: str) -> str | None:
        """检测IP地址或网络的版本，返回格式化字符串
        
        Args:
            ip_or_network: IP地址或网络字符串
            
        Returns:
            str | None: IP版本字符串（"IPv4"或"IPv6"），如果无效则返回None
        """
        version = self.get_ip_version(ip_or_network)
        return f"IPv{version}" if version else None
