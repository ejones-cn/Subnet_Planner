import ipaddress

from i18n import _


class ValidationService:
    def __init__(self, app=None):
        self.app = app

    def validate_cidr(self, cidr_str, ip_version=None):
        if not cidr_str:
            return {'valid': True, 'error': None}

        try:
            network = ipaddress.ip_network(cidr_str, strict=False)
            if ip_version:
                expected_version = 6 if ip_version == "IPv6" else 4
                if network.version != expected_version:
                    return {
                        'valid': False,
                        'error': _("ip_version_mismatch")
                    }
            return {'valid': True, 'error': None}
        except ValueError as e:
            return {'valid': False, 'error': str(e)}

    def validate_ip_address(self, ip_str, ip_version=None):
        if not ip_str:
            return {'valid': True, 'error': None}

        try:
            addr = ipaddress.ip_address(ip_str)
            if ip_version:
                expected_version = 6 if ip_version == "IPv6" else 4
                if addr.version != expected_version:
                    return {
                        'valid': False,
                        'error': _("ip_version_mismatch")
                    }
            return {'valid': True, 'error': None}
        except ValueError as e:
            return {'valid': False, 'error': str(e)}

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

        for name, hosts in requirements:
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
