import ipaddress

from i18n import _
from ip_subnet_calculator import (
    suggest_subnet_planning,
    format_large_number,
    handle_ip_subnet_error,
)
from services.table_column_manager import TableColumnManager


class SubnetPlanningService:
    def __init__(self, app):
        self.app = app

    def validate_planning_input(self, parent):
        if not parent:
            return {
                'valid': False,
                'error': _("please_enter_parent_network"),
                'error_code': 'empty_parent'
            }

        try:
            parent_net = ipaddress.ip_network(parent, strict=False)
            parent_address = ipaddress.ip_address(parent.split('/')[0])
            if parent_address != parent_net.network_address:
                correct_parent = f"{parent_net.network_address}/{parent_net.prefixlen}"
                self.app.planning_parent_entry.delete(0, 'end')
                self.app.planning_parent_entry.insert(0, correct_parent)
        except ValueError:
            return {
                'valid': False,
                'error': _("invalid_parent_network_cidr"),
                'error_code': 'invalid_parent'
            }

        return {'valid': True, 'error': None, 'error_code': None}

    def execute_planning(self, from_history=False):
        app = self.app
        parent = app.planning_parent_entry.get().strip()

        validation_result = self.validate_planning_input(parent)
        if not validation_result['valid']:
            app.show_error(_("error"), validation_result['error'])
            return

        parent = app.planning_parent_entry.get().strip()

        subnet_requirements = []
        for item in app.requirements_tree.get_children():
            values = app.requirements_tree.item(item, "values")
            subnet_requirements.append((values[1], int(values[2])))

        if not subnet_requirements:
            app.show_error(_("error"), _("please_add_at_least_one_requirement"))
            return

        try:
            parent_network = ipaddress.ip_network(parent, strict=False)

            formatted_requirements = [{'name': name, 'hosts': hosts} for name, hosts in subnet_requirements]
            plan_result = suggest_subnet_planning(parent, formatted_requirements)

            if 'error' in plan_result:
                app.show_error(_("error"), f"{_('subnet_planning_failed')}: {plan_result['error']}")
                return

            selected_plan = plan_result['plans'][0]

            app.clear_tree_items(app.allocated_tree)
            app.clear_tree_items(app.planning_remaining_tree)

            is_ipv6 = TableColumnManager.is_ipv6_network(parent)

            TableColumnManager.configure_planning_allocated_tree(app.allocated_tree, is_ipv6)

            for i, subnet in enumerate(selected_plan['allocated_subnets'], 1):
                tags = ("even",) if i % 2 == 0 else ("odd",)
                app.allocated_tree.insert(
                    "",
                    'end',
                    values=(
                        i,
                        subnet["name"],
                        subnet["cidr"],
                        format_large_number(subnet["required_hosts"]),
                        format_large_number(subnet["available_hosts"]),
                        subnet["info"]["network"],
                        subnet["info"]["broadcast"],
                        subnet["info"]["netmask"],
                        subnet["info"]["wildcard"],
                        subnet["info"]["broadcast"] if not is_ipv6 else "-",
                    ),
                    tags=tags,
                )

            app.auto_resize_columns(app.allocated_tree)

            TableColumnManager.configure_planning_remaining_tree(app.planning_remaining_tree, is_ipv6)

            for i, subnet in enumerate(selected_plan['remaining_subnets_info'], 1):
                tags = ("even",) if i % 2 == 0 else ("odd",)
                hidden_vals = TableColumnManager.get_hidden_values_for_ipv6(subnet, is_ipv6)

                app.planning_remaining_tree.insert(
                    "",
                    'end',
                    values=(
                        i,
                        selected_plan['remaining_subnets'][i - 1],
                        subnet["network"],
                        subnet["host_range_end"],
                        hidden_vals["netmask"],
                        hidden_vals["wildcard"],
                        hidden_vals["broadcast"],
                        format_large_number(subnet["usable_addresses"]),
                    ),
                    tags=tags,
                )

            app.auto_resize_columns(app.planning_remaining_tree)

            if not from_history:
                current_parent = app.planning_parent_entry.get().strip()
                app._update_history_entry(current_parent, app.planning_parent_networks, app.planning_parent_entry)
                app.save_current_state(_("execute_planning"))

            compatible_plan_result = {
                "parent_cidr": plan_result["parent_cidr"],
                "allocated_subnets": selected_plan["allocated_subnets"],
                "remaining_subnets": selected_plan["remaining_subnets"],
                "remaining_subnets_info": selected_plan["remaining_subnets_info"],
                "ip_version": plan_result["ip_version"]
            }
            app.generate_planning_chart_data(compatible_plan_result)

        except ValueError as e:
            error_dict = handle_ip_subnet_error(e)
            app.show_error(_("error"), f"{_('subnet_planning_failed')}: {error_dict.get('error', str(e))}")
        except Exception as e:
            app.show_error(_("error"), f"{_('subnet_planning_failed')}: {_('unknown_error_occurred')} - {str(e)}")
