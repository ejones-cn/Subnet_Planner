class IPAMValidator:
    ALLOW_EMPTY_FIELDS = ('expiry_date', 'vlan', 'hostname', 'mac_address', 'description')
    
    @staticmethod
    def validate_allocation_params(hostname, description):
        if not hostname and not description:
            return False, "主机名和描述不能同时为空"
        return True, None

    
    @staticmethod
    def validate_inline_edit(column_name, value):
        if not value:
            if column_name not in IPAMValidator.ALLOW_EMPTY_FIELDS:
                return False, "输入不能为空"
        return True, None
