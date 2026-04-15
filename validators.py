class IPAMValidator:
    ALLOW_EMPTY_FIELDS = ('expiry_date', 'vlan', 'hostname', 'mac_address')
    
    @staticmethod
    def validate_allocation_params(hostname, description):
        if not description:
            return False, "描述不能为空"
        return True, None
    
    @staticmethod
    def validate_inline_edit(column_name, value):
        if not value:
            if column_name not in IPAMValidator.ALLOW_EMPTY_FIELDS:
                return False, "输入不能为空"
        return True, None