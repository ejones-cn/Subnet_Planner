from i18n import _ as translate


class DataPreparer:
    @staticmethod
    def prepare_export_data(data_source):
        main_data = []
        main_tree = data_source["main_tree"]
        main_filter = data_source.get("main_filter", None)
        main_headers = data_source.get("main_headers")

        is_ipv6 = False

        ip_version = data_source.get("ip_version")
        if ip_version:
            is_ipv6 = ip_version == "IPv6"
        else:
            for col in main_tree["columns"]:
                col_width = main_tree.column(col, "width")
                if col == "end_address" and col_width > 0:
                    is_ipv6 = True
                    break

            if not is_ipv6 and "remaining_tree" in data_source:
                remaining_tree = data_source["remaining_tree"]
                for col in remaining_tree["columns"]:
                    col_width = remaining_tree.column(col, "width")
                    if col == "end_address" and col_width > 0:
                        is_ipv6 = True
                        break

        main_columns = main_tree["columns"]

        def ipv6_main_field_filter(h):
            return h not in [translate("subnet_mask"), translate("wildcard_mask"), translate("broadcast_address")]

        def ipv4_main_field_filter(h):
            return h != translate("network_end_address")

        if is_ipv6:
            main_field_filter = ipv6_main_field_filter
        else:
            main_field_filter = ipv4_main_field_filter

        if main_headers is None:
            all_main_headers = [main_tree.heading(col, "text") or "" for col in main_columns]
            main_headers = [h for h in all_main_headers if main_field_filter(h)]
        else:
            main_headers = [h for h in main_headers if main_field_filter(h)]

        filtered_main_columns = []
        for i, col in enumerate(main_columns):
            header = main_tree.heading(col, "text") or ""
            if main_field_filter(header):
                filtered_main_columns.append(i)

        added_items = set()
        for item in main_tree.get_children():
            values = main_tree.item(item, "values")
            if main_filter:
                if main_filter(values):
                    if len(values) >= 2 and values[0] != "":
                        item_key = values[0]
                        if item_key not in added_items:
                            added_items.add(item_key)
                            filtered_values = [values[i] for i in filtered_main_columns]
                            main_data.append(filtered_values)
                    else:
                        filtered_values = [values[i] for i in filtered_main_columns]
                        main_data.append(filtered_values)
            elif values:
                if len(values) >= 2 and values[0] != "":
                    item_key = values[0]
                    if item_key not in added_items:
                        added_items.add(item_key)
                        filtered_values = [values[i] for i in filtered_main_columns]
                        main_data.append(filtered_values)
                else:
                    filtered_values = [values[i] for i in filtered_main_columns]
                    main_data.append(filtered_values)

        unique_main_data = []
        seen_rows = set()
        for row in main_data:
            row_tuple = tuple(row)
            if row_tuple not in seen_rows:
                seen_rows.add(row_tuple)
                unique_main_data.append(row)
        main_data = unique_main_data

        remaining_tree = data_source["remaining_tree"]
        remaining_columns = remaining_tree["columns"]
        remaining_headers = []

        filtered_columns = []
        for col in remaining_columns:
            col_width = remaining_tree.column(col, "width")
            if col_width > 0:
                header = remaining_tree.heading(col, "text") or ""
                if main_field_filter(header):
                    filtered_columns.append(col)
                    remaining_headers.append(header)

        remaining_data = []
        for item in remaining_tree.get_children():
            values = remaining_tree.item(item, "values")
            if values:
                filtered_values = []
                for i, col in enumerate(remaining_columns):
                    if col in filtered_columns:
                        filtered_values.append(values[i])
                filtered_dict = dict(zip(remaining_headers, filtered_values))
                remaining_data.append(filtered_dict)

        return main_data, main_headers, remaining_data, remaining_headers

    @staticmethod
    def is_k2v_headers(headers):
        return len(headers) == 2

    @staticmethod
    def convert_remaining_data(remaining_data, remaining_headers):
        remaining_data_list = []
        for item in remaining_data:
            if isinstance(item, dict):
                row = [item.get(header, '') for header in remaining_headers]
                remaining_data_list.append(row)
            else:
                remaining_data_list.append(item)
        return remaining_data_list

    @staticmethod
    def create_mock_tree(headers, data):
        class MockTree:
            def __init__(self, headers, data):
                self.headers = headers
                self.data = data
                self.columns = list(range(len(headers)))

            def heading(self, col, _event):
                if isinstance(col, str) and col.isdigit():
                    col = int(col)
                return self.headers[col] if isinstance(col, int) and 0 <= col < len(self.headers) else ""

            def get_children(self):
                return range(len(self.data))

            def item(self, item, option=None):
                values = self.data[item] if item < len(self.data) else []
                if option is None:
                    return {"values": values}
                elif option == "values":
                    return values
                else:
                    return None

            def __getitem__(self, key):
                if key == "columns":
                    return self.columns
                raise KeyError(key)

        return MockTree(headers, data)
