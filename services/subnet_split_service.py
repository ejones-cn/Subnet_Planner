import ipaddress

from i18n import _
from ip_subnet_calculator import (
    split_subnet,
    format_large_number,
    handle_ip_subnet_error,
)
from services.table_column_manager import TableColumnManager


class SubnetSplitService:
    def __init__(self, app):
        self.app = app

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
            parent_net = ipaddress.ip_network(parent, strict=False)
            parent_address = ipaddress.ip_address(parent.split('/')[0])
            if parent_address != parent_net.network_address:
                correct_parent = f"{parent_net.network_address}/{parent_net.prefixlen}"
                self.app.parent_entry.delete(0, 'end')
                self.app.parent_entry.insert(0, correct_parent)
        except ValueError:
            return {
                'valid': False,
                'error': _("invalid_parent_network_cidr"),
                'error_code': 'invalid_parent'
            }

        try:
            split_net = ipaddress.ip_network(split, strict=False)
            split_address = ipaddress.ip_address(split.split('/')[0])
            if split_address != split_net.network_address:
                correct_split = f"{split_net.network_address}/{split_net.prefixlen}"
                self.app.split_entry.delete(0, 'end')
                self.app.split_entry.insert(0, correct_split)
        except ValueError:
            return {
                'valid': False,
                'error': _("invalid_split_segment_cidr"),
                'error_code': 'invalid_split'
            }

        return {'valid': True, 'error': None, 'error_code': None}

    def execute_split(self, from_history=False):
        app = self.app
        parent = app.parent_entry.get().strip()
        split = app.split_entry.get().strip()

        validation_result = self.validate_split_input(parent, split)
        if not validation_result['valid']:
            app.clear_result()
            app.clear_tree_items(app.split_tree)
            app.show_error(_("input_error"), validation_result['error'])
            return

        parent = app.parent_entry.get().strip()
        split = app.split_entry.get().strip()

        try:
            parent_network = ipaddress.ip_network(parent, strict=False)
            split_network = ipaddress.ip_network(split, strict=False)

            result = split_subnet(parent, split)

            app.clear_tree_items(app.split_tree)
            app.clear_tree_items(app.remaining_tree)

            if "error" in result:
                app.show_error(_("error"), result["error"])
                return

            row_index = 0
            app.split_tree.insert("", 'end', values=(_("parent_network"), result["parent_info"]["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1

            app.split_tree.insert("", 'end', values=(_("split_segment"), result["split_info"]["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            app.split_tree.insert("", 'end', values=("-" * 10, "-" * 20), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1

            split_info = result["split_info"]
            app.split_tree.insert("", 'end', values=(_("network_address"), split_info["network"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1

            is_ipv6 = TableColumnManager.is_ipv6_network(parent)
            if not is_ipv6:
                app.split_tree.insert("", 'end', values=(_("subnet_mask"), split_info["netmask"]), tags=("odd" if row_index % 2 == 0 else "even",))
                row_index += 1
                app.split_tree.insert("", 'end', values=(_("wildcard_mask"), split_info["wildcard"]), tags=("odd" if row_index % 2 == 0 else "even",))
                row_index += 1
                app.split_tree.insert("", 'end', values=(_("broadcast_address"), split_info["broadcast"]), tags=("odd" if row_index % 2 == 0 else "even",))
                row_index += 1

            app.split_tree.insert("", 'end', values=(_("start_address"), split_info["host_range_start"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            app.split_tree.insert("", 'end', values=(_("end_address"), split_info["host_range_end"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1

            app.split_tree.insert("", 'end', values=(_("usable_addresses"), format_large_number(split_info["usable_addresses"], use_scientific=True)), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            app.split_tree.insert("", 'end', values=(_("total_addresses"), format_large_number(split_info["num_addresses"], use_scientific=True)), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            app.split_tree.insert("", 'end', values=(_("prefix_length"), split_info["prefixlen"]), tags=("odd" if row_index % 2 == 0 else "even",))
            row_index += 1
            app.split_tree.insert("", 'end', values=(_("cidr"), split_info["cidr"]), tags=("odd" if row_index % 2 == 0 else "even",))

            TableColumnManager.configure_split_remaining_tree(app.remaining_tree, is_ipv6)

            if result["remaining_subnets_info"]:
                for i, network in enumerate(result["remaining_subnets_info"], 1):
                    tags = ("even",) if i % 2 == 0 else ("odd",)
                    hidden_vals = TableColumnManager.get_hidden_values_for_ipv6(network, is_ipv6)

                    app.remaining_tree.insert(
                        "",
                        'end',
                        values=(
                            i,
                            network["cidr"],
                            network["network"],
                            network["host_range_end"],
                            hidden_vals["netmask"],
                            hidden_vals["wildcard"],
                            hidden_vals["broadcast"],
                            format_large_number(network["usable_addresses"], use_scientific=True),
                        ),
                        tags=tags,
                    )
            else:
                app.remaining_tree.insert("", 'end', values=(1, _("none"), _("none"), _("none"), _("none"), _("none"), _("none"), _("none")))

            if hasattr(app, 'remaining_scroll_v'):
                yview = app.remaining_tree.yview()
                need_scrollbar = not (float(yview[0]) <= 0.0 and float(yview[1]) >= 1.0)
                current_state = app.remaining_scroll_v.winfo_ismapped()
                if need_scrollbar != current_state:
                    if need_scrollbar:
                        app.remaining_scroll_v.grid(row=0, column=1, sticky='ns')
                        app.remaining_scroll_v.set(yview[0], yview[1])
                    else:
                        app.remaining_scroll_v.grid_remove()

            app.prepare_chart_data(result, split_info, result["remaining_subnets_info"])
            app.draw_distribution_chart()

            if not from_history:
                app._update_history_entry(parent, app.split_parent_networks, app.parent_entry)
                app._update_history_entry(split, app.split_networks, app.split_entry)

                app.history_repo.add_split_record(parent, split)
                app.update_history_listbox()

        except ValueError as e:
            error_result = handle_ip_subnet_error(e)
            message = error_result.get('error', str(e))
            app.clear_result()
            app.split_tree.insert("", 'end', values=(_("error"), message), tags=("error",))
        except Exception as e:
            app.clear_result()
            app.split_tree.insert("", 'end', values=(_("error"), f"{_('unknown_error_occurred')}: {str(e)}"), tags=("error",))
