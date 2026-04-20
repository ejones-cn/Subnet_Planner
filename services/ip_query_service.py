import ipaddress

from i18n import _
from ip_subnet_calculator import (
    get_ip_info,
    merge_subnets,
    range_to_cidr,
    check_subnet_overlap,
    format_large_number,
    handle_ip_subnet_error,
)


class IPQueryService:
    def __init__(self, app=None):
        self.app = app

    def execute_ipv4_info(self, ip_address, subnet_mask_or_cidr):
        try:
            if '/' in ip_address:
                ip_info = get_ip_info(ip_address)
            else:
                if subnet_mask_or_cidr.isdigit():
                    cidr = int(subnet_mask_or_cidr)
                    ip_info = get_ip_info(f"{ip_address}/{cidr}")
                else:
                    ip_info = get_ip_info(f"{ip_address}/{subnet_mask_or_cidr}")
            return {'success': True, 'data': ip_info}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'success': False, 'error': error_result.get('error', str(e))}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_ipv6_info(self, ip_address, cidr_prefix):
        try:
            if '/' in ip_address:
                ip_info = get_ip_info(ip_address)
            else:
                ip_info = get_ip_info(f"{ip_address}/{cidr_prefix}")
            return {'success': True, 'data': ip_info}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'success': False, 'error': error_result.get('error', str(e))}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_merge_subnets(self, subnets_text):
        try:
            subnets = [s.strip() for s in subnets_text.strip().split(',') if s.strip()]
            if not subnets:
                return {'success': False, 'error': _("please_enter_subnets_to_merge")}
            result = merge_subnets(subnets)
            return {'success': True, 'data': result}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'success': False, 'error': error_result.get('error', str(e))}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_range_to_cidr(self, start_ip, end_ip):
        try:
            if not start_ip or not end_ip:
                return {'success': False, 'error': _("please_enter_ip_range")}
            result = range_to_cidr(start_ip, end_ip)
            return {'success': True, 'data': result}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'success': False, 'error': error_result.get('error', str(e))}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def execute_check_overlap(self, subnets_text):
        try:
            subnets = [s.strip() for s in subnets_text.strip().split(',') if s.strip()]
            if not subnets:
                return {'success': False, 'error': _("please_enter_subnets_to_check")}
            result = check_subnet_overlap(subnets)
            return {'success': True, 'data': result}
        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            return {'success': False, 'error': error_result.get('error', str(e))}
        except Exception as e:
            return {'success': False, 'error': str(e)}
