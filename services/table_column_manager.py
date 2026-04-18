import ipaddress


class TableColumnManager:
    IPV4_SPLIT_REMAINING = {
        "wildcard": {"width": 100, "stretch": True},
        "netmask": {"width": 100, "stretch": True},
        "broadcast": {"width": 120, "stretch": True},
        "end_address": {"width": 0, "stretch": False},
        "cidr": {"width": 120, "stretch": True},
        "network": {"width": 120, "stretch": True},
        "usable": {"width": 60, "stretch": True},
    }

    IPV6_SPLIT_REMAINING = {
        "wildcard": {"width": 0, "stretch": False},
        "netmask": {"width": 0, "stretch": False},
        "broadcast": {"width": 0, "stretch": False},
        "end_address": {"width": 200, "stretch": True},
        "cidr": {"width": 180, "stretch": True},
        "network": {"width": 180, "stretch": True},
        "usable": {"width": 60, "stretch": True},
    }

    IPV4_PLANNING_ALLOCATED = {
        "wildcard": {"width": 100, "stretch": True},
        "netmask": {"width": 100, "stretch": True},
        "broadcast": {"width": 120, "stretch": True},
        "end_address": {"width": 0, "stretch": False},
    }

    IPV6_PLANNING_ALLOCATED = {
        "wildcard": {"width": 0, "stretch": False},
        "netmask": {"width": 0, "stretch": False},
        "broadcast": {"width": 0, "stretch": False},
        "end_address": {"width": 120, "stretch": True},
    }

    IPV4_PLANNING_REMAINING = {
        "wildcard": {"width": 100, "stretch": True},
        "netmask": {"width": 100, "stretch": True},
        "broadcast": {"width": 120, "stretch": True},
        "end_address": {"width": 0, "stretch": False},
        "cidr": {"width": 120, "stretch": True},
        "network": {"width": 120, "stretch": True},
        "usable": {"width": 60, "stretch": True},
    }

    IPV6_PLANNING_REMAINING = {
        "wildcard": {"width": 0, "stretch": False},
        "netmask": {"width": 0, "stretch": False},
        "broadcast": {"width": 0, "stretch": False},
        "end_address": {"width": 200, "stretch": True},
        "cidr": {"width": 180, "stretch": True},
        "network": {"width": 180, "stretch": True},
        "usable": {"width": 60, "stretch": True},
    }

    @staticmethod
    def is_ipv6_network(network_str):
        try:
            return ipaddress.ip_network(network_str, strict=False).version == 6
        except (ValueError, TypeError):
            return False

    @classmethod
    def configure_split_remaining_tree(cls, tree, is_ipv6):
        config = cls.IPV6_SPLIT_REMAINING if is_ipv6 else cls.IPV4_SPLIT_REMAINING
        for column, settings in config.items():
            tree.column(column, **settings)

    @classmethod
    def configure_planning_allocated_tree(cls, tree, is_ipv6):
        config = cls.IPV6_PLANNING_ALLOCATED if is_ipv6 else cls.IPV4_PLANNING_ALLOCATED
        for column, settings in config.items():
            tree.column(column, **settings)

    @classmethod
    def configure_planning_remaining_tree(cls, tree, is_ipv6):
        config = cls.IPV6_PLANNING_REMAINING if is_ipv6 else cls.IPV4_PLANNING_REMAINING
        for column, settings in config.items():
            tree.column(column, **settings)

    @classmethod
    def get_hidden_values_for_ipv6(cls, subnet_info, is_ipv6):
        if is_ipv6:
            return {
                "netmask": "",
                "wildcard": subnet_info.get("wildcard", ""),
                "broadcast": "",
            }
        return {
            "netmask": subnet_info.get("netmask", ""),
            "wildcard": subnet_info.get("wildcard", ""),
            "broadcast": subnet_info.get("broadcast", ""),
        }
