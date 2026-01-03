#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
国际化模块
提供翻译功能和语言切换支持
"""

# 翻译字典
# 结构：{"英文键名": {"zh": "中文翻译", "en": "英文翻译"}}
TRANSLATIONS = {
    # 通用
    "error": {"zh": "错误", "en": "Error"},
    "input_error": {"zh": "输入错误", "en": "Input Error"},
    "ok": {"zh": "确定", "en": "OK"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "confirm": {"zh": "确认", "en": "Confirm"},
    "export": {"zh": "导出", "en": "Export"},
    "execute": {"zh": "执行", "en": "Execute"},
    "add": {"zh": "添加", "en": "Add"},
    "delete": {"zh": "删除", "en": "Delete"},
    "undo": {"zh": "撤销", "en": "Undo"},
    "import": {"zh": "导入", "en": "Import"},
    "save": {"zh": "保存", "en": "Save"},
    "add_subnet_requirement": {"zh": "添加子网需求", "en": "Add Subnet Requirement"},
    "split_segment_info": {"zh": "切分段信息", "en": "Split Segment Info"},
    "remaining_segment_info": {"zh": "剩余网段信息", "en": "Remaining Segment Info"},
    "subnet_planner": {"zh": "子网规划师", "en": "Subnet Planner"},
    "save_subnet_split_result": {"zh": "保存子网切分结果", "en": "Save Subnet Split Result"},
    "save_subnet_planning_result": {"zh": "保存子网规划结果", "en": "Save Subnet Planning Result"},
    "result_successfully_exported": {"zh": "结果已成功导出到: {file_path}", "en": "Result successfully exported to: {file_path}"},
    "export_failed": {"zh": "导出失败: {error}", "en": "Export failed: {error}"},
    "apply_theme": {"zh": "应用主题", "en": "Apply Theme"},
    "close": {"zh": "关闭", "en": "Close"},
    
    # 菜单和标签
    "history": {"zh": "历史记录", "en": "History"},
    "parent_network": {"zh": "父网段", "en": "Parent Network"},
    "split_segments": {"zh": "切分段", "en": "Split Segments"},
    "execute_split": {"zh": "执行切分", "en": "Execute Split"},
    "reexecute_split": {"zh": "重新切分", "en": "Re-execute Split"},
    "split_result": {"zh": "切分结果", "en": "Split Result"},
    "export_result": {"zh": "导出结果", "en": "Export Result"},
    "parent_network_settings": {"zh": "父网段设置", "en": "Parent Network Settings"},
    "requirements_pool": {"zh": "需求池", "en": "Requirements Pool"},
    "subnet_requirements": {"zh": "子网需求", "en": "Subnet Requirements"},
    "move_records": {"zh": "↔", "en": "↔"},
    "import_requirements": {"zh": "导入", "en": "Import"},
    "planning_result": {"zh": "规划结果", "en": "Planning Result"},
    "subnet_planning": {"zh": "子网规划", "en": "Subnet Planning"},
    "subnet_split": {"zh": "子网切分", "en": "Subnet Split"},
    "advanced_tools": {"zh": "高级工具", "en": "Advanced Tools"},
    "input_parameters": {"zh": "输入参数", "en": "Input Parameters"},
    "hint": {"zh": "提示", "en": "Hint"},
    "click_execute_split_to_start": {"zh": "点击'执行切分'按钮开始操作...", "en": "Click 'Execute Split' to start operation..."},
    "subnet_name": {"zh": "子网名称", "en": "Subnet Name"},
    "host_count": {"zh": "主机数量", "en": "Host Count"},
    "save_to_pool": {"zh": "暂存到池", "en": "Save to Pool"},
    "import_from_file": {"zh": "从文件导入", "en": "Import from File"},
    "select_file_to_import": {"zh": "选择要导入的文件", "en": "Select File to Import"},
    "file_parse_failed": {"zh": "文件解析失败", "en": "File Parsing Failed"},
    "import_requirements_pool": {"zh": "导入需求池", "en": "Import Requirements Pool"},
    "import_subnet_requirements": {"zh": "导入子网需求", "en": "Import Subnet Requirements"},
    "save_template": {"zh": "保存模板", "en": "Save Template"},
    "template_generation_failed": {"zh": "模板生成失败", "en": "Template Generation Failed"},
    "export_planning": {"zh": "导出规划", "en": "Export Planning"},
    "execute_planning": {"zh": "规划子网", "en": "Plan Subnet"},
    "required_count": {"zh": "需求数", "en": "Required"},
    "available_count": {"zh": "可用数", "en": "Available"},
    "ipv6_address_info": {"zh": "IPv6地址信息查询", "en": "IPv6 Address Information"},
    "ipv6_address": {"zh": "IPv6地址", "en": "IPv6 Address"},
    "cidr": {"zh": "CIDR", "en": "CIDR"},
    "query_info": {"zh": "查询信息", "en": "Query Info"},
    "query_result": {"zh": "查询结果", "en": "Query Result"},
    "merge_subnets": {"zh": "子网合并列表", "en": "Merge Subnets"},
    "merge_subnet": {"zh": "合并子网", "en": "Merge Subnet"},
    "ip_address_range": {"zh": "IP地址范围", "en": "IP Address Range"},
    "start": {"zh": "起始", "en": "Start"},
    "end": {"zh": "结束", "en": "End"},
    "convert_to_cidr": {"zh": "转换为CIDR", "en": "Convert to CIDR"},
    "cidr_result": {"zh": "CIDR结果", "en": "CIDR Result"},
    "ipv4_address_info": {"zh": "IPv4地址信息查询", "en": "IPv4 Address Information"},
    "ipv4_address": {"zh": "IPv4地址", "en": "IPv4 Address"},
    "subnet_mask": {"zh": "子网掩码", "en": "Subnet Mask"},
    "check_overlap": {"zh": "检测重叠", "en": "Check Overlap"},
    "detection_result": {"zh": "检测结果", "en": "Detection Result"},
    "function_debug_panel": {"zh": "功能调试面板", "en": "Function Debug Panel"},
    "theme_switch": {"zh": "主题切换", "en": "Theme Switch"},
    "select_theme": {"zh": "选择主题", "en": "Select Theme"},
    "window_lock": {"zh": "窗口锁定", "en": "Window Lock"},
    "lock_window_width": {"zh": "锁定窗口横向尺寸（禁止调整宽度）", "en": "Lock window horizontal size (disable width adjustment)"},
    "about": {"zh": "关于", "en": "About"},
    "author": {"zh": "作者", "en": "Author"},
    "index": {"zh": "序号", "en": "Index"},
    "network_address": {"zh": "网络地址", "en": "Network Address"},
    "wildcard_mask": {"zh": "通配符掩码", "en": "Wildcard Mask"},
    "broadcast_address": {"zh": "广播地址", "en": "Broadcast Address"},
    "usable_address_count": {"zh": "可用地址数", "en": "Usable Address Count"},
    "item": {"zh": "项目", "en": "Item"},
    "value": {"zh": "值", "en": "Value"},
    "allocated_subnets": {"zh": "已分配子网", "en": "Allocated Subnets"},
    "remaining_subnets": {"zh": "剩余网段", "en": "Remaining Subnets"},
    "distribution_chart": {"zh": "网段分布图", "en": "Distribution Chart"},
    
    # 错误信息
    "record_already_exists": {"zh": "中已存在名称为 '{name}' 的记录", "en": "already contains a record named '{name}'"},
    "input_cannot_be_empty": {"zh": "输入不能为空", "en": "Input cannot be empty"},
    "subnet_already_exists": {"zh": "已经存在名称为 '{name}' 的子网，请使用其他名称", "en": "A subnet named '{name}' already exists, please use another name"},
    "host_count_must_be_greater_than_0": {"zh": "主机数量必须大于0", "en": "Host count must be greater than 0"},
    "please_enter_parent_network": {"zh": "请输入父网段", "en": "Please enter parent network"},
    "invalid_parent_network_format": {"zh": "父网段格式不正确，请输入有效的CIDR格式（例如：192.168.1.0/24）", "en": "Invalid parent network format, please enter a valid CIDR format (e.g., 192.168.1.0/24)"},
    "please_add_at_least_one_requirement": {"zh": "请添加至少一个子网需求", "en": "Please add at least one subnet requirement"},
    "subnet_planning_failed": {"zh": "子网规划失败", "en": "Subnet planning failed"},
    "unknown_error_occurred": {"zh": "发生未知错误", "en": "An unknown error occurred"},
    "invalid_parent_network_cidr": {"zh": "父网段格式无效，请输入有效的CIDR格式（如: 10.0.0.0/8）", "en": "Invalid parent network CIDR format, please enter a valid CIDR (e.g., 10.0.0.0/8)"},
    "invalid_split_segment_cidr": {"zh": "切分网段格式无效，请输入有效的CIDR格式（如: 10.21.50.0/23）", "en": "Invalid split segment CIDR format, please enter a valid CIDR (e.g., 10.21.50.0/23)"},
    "parent_and_split_cidr_cannot_be_empty": {"zh": "父网段和切分网段都不能为空！", "en": "Parent network and split segment cannot be empty!"},
    "please_enter_subnet_name": {"zh": "请输入子网名称", "en": "Please enter subnet name"},
    "please_enter_valid_host_count": {"zh": "请输入有效的主机数量", "en": "Please enter a valid host count"},
    "msg_template_generation_failed": {"zh": "模板生成失败", "en": "Template generation failed"},
    "msg_file_parse_failed": {"zh": "文件解析失败", "en": "File parsing failed"},
    "failed": {"zh": "失败", "en": "failed"},
    "operation_failed": {"zh": "操作失败", "en": "Operation failed"},
    "query_failed": {"zh": "查询失败", "en": "Query failed"},
    "conversion_failed": {"zh": "转换失败", "en": "Conversion failed"},
    "execute_subnet_overlap_detection_failed": {"zh": "执行子网重叠检测失败", "en": "Failed to execute subnet overlap detection"},
    "please_select_records_to_move": {"zh": "请先选择要移动的{record_type}记录", "en": "Please select {record_type} records to move first"},
    "please_select_records_to_swap": {"zh": "请同时选择两个表格中的记录进行交换", "en": "Please select records from both tables to swap"},
    "split_segment": {"zh": "切分网段", "en": "Split Segment"},
    "start_address": {"zh": "起始地址", "en": "Start Address"},
    "end_address": {"zh": "结束地址", "en": "End Address"},
    "total_addresses": {"zh": "总地址数", "en": "Total Addresses"},
    "usable_addresses": {"zh": "可用地址数", "en": "Usable Addresses"},
    "prefix_length": {"zh": "前缀长度", "en": "Prefix Length"},
    
    # 应用名称
    "app_name": {"zh": "子网规划师", "en": "Subnet Planner"},
    "version": {"zh": "版本", "en": "Version"},
    
    # IPv6地址类型
    "unknown": {"zh": "未知", "en": "Unknown"},
    "loopback_address": {"zh": "回环地址", "en": "Loopback Address"},
    "unspecified_address": {"zh": "未指定地址", "en": "Unspecified Address"},
    "multicast_address": {"zh": "组播地址", "en": "Multicast Address"},
    "link_local_unicast_address": {"zh": "链路本地单播地址", "en": "Link-Local Unicast Address"},
    "unique_local_unicast_address": {"zh": "唯一本地单播地址 (ULA)", "en": "Unique Local Unicast Address (ULA)"},
    "documentation_test_address": {"zh": "文档/测试地址", "en": "Documentation/Test Address"},
    "global_unicast_address": {"zh": "全球单播地址", "en": "Global Unicast Address"},
    "ipv4_mapped_ipv6_address": {"zh": "IPv4映射的IPv6地址", "en": "IPv4-Mapped IPv6 Address"},
    
    # IPv6信息显示
    "total_hosts": {"zh": "总主机数", "en": "Total Hosts"},
    "usable_hosts": {"zh": "可用主机数", "en": "Usable Hosts"},
    "address_format": {"zh": "地址格式", "en": "Address Format"},
    "compressed_format": {"zh": "压缩格式", "en": "Compressed Format"},
    "expanded_format": {"zh": "展开格式", "en": "Expanded Format"},
    "reverse_dns_format": {"zh": "反向DNS格式", "en": "Reverse DNS Format"},
    "mapped_ipv4_address": {"zh": "映射的IPv4地址", "en": "Mapped IPv4 Address"},
    "address_properties": {"zh": "地址属性", "en": "Address Properties"},
    "is_global_routable": {"zh": "是否全局可路由", "en": "Is Globally Routable"},
    "is_private_address": {"zh": "是否私有地址", "en": "Is Private Address"},
    "address_structure_analysis": {"zh": "地址结构分析", "en": "Address Structure Analysis"},
    "prefix_analysis": {"zh": "前缀分析", "en": "Prefix Analysis"},
    "address_segment_count": {"zh": "地址段数量", "en": "Address Segment Count"},
    "binary_representation": {"zh": "二进制表示", "en": "Binary Representation"},
    "hexadecimal_representation": {"zh": "十六进制表示", "en": "Hexadecimal Representation"},
    "decimal_value_representation": {"zh": "十进制值表示", "en": "Decimal Value Representation"},
    "address_segment_details": {"zh": "地址段详情", "en": "Address Segment Details"},
    "network_scale_and_usage": {"zh": "网络规模与用途", "en": "Network Scale and Usage"},
    "subnet_size": {"zh": "子网规模", "en": "Subnet Size"},
    "main_usage": {"zh": "主要用途", "en": "Main Usage"},
    "configuration_advice": {"zh": "配置建议", "en": "Configuration Advice"},
    "network_configuration": {"zh": "网络配置", "en": "Network Configuration"},
    "rfc_standards_reference": {"zh": "RFC标准参考", "en": "RFC Standards Reference"},
    "extended_information": {"zh": "扩展信息", "en": "Extended Information"},
    "address_usage": {"zh": "地址用途", "en": "Address Usage"},
    "rfc_specification": {"zh": "RFC规范", "en": "RFC Specification"},
    
    # 标签页
    "ipv4_query": {"zh": "IPv4查询", "en": "IPv4 Query"},
    "ipv6_query": {"zh": "IPv6查询", "en": "IPv6 Query"},
    "subnet_merge": {"zh": "子网合并", "en": "Subnet Merge"},
    "overlap_detection": {"zh": "重叠检测", "en": "Overlap Detection"},
    
    # 表格列名
    "project": {"zh": "项目", "en": "Item"},
    "status": {"zh": "状态", "en": "Status"},
    "description": {"zh": "描述", "en": "Description"},
    "hosts": {"zh": "主机数量", "en": "Hosts"},
    "netmask": {"zh": "子网掩码", "en": "Subnet Mask"},
    "network": {"zh": "网络地址", "en": "Network Address"},
    "first_host": {"zh": "第一个可用主机", "en": "First Usable Host"},
    "last_host": {"zh": "最后一个可用主机", "en": "Last Usable Host"},
    "address_type": {"zh": "地址类型", "en": "Address Type"},
    "compressed": {"zh": "压缩格式", "en": "Compressed Format"},
    "exploded": {"zh": "展开格式", "en": "Expanded Format"},
    "reverse_dns": {"zh": "反向DNS格式", "en": "Reverse DNS Format"},
    "mapped_ipv4": {"zh": "映射的IPv4地址", "en": "Mapped IPv4 Address"},
    "address_attributes": {"zh": "地址属性", "en": "Address Attributes"},
    "address_structure": {"zh": "地址结构分析", "en": "Address Structure Analysis"},
    "num_addresses": {"zh": "总地址数", "en": "Total Addresses"},
    "host_range_start": {"zh": "起始地址", "en": "Start Address"},
    "host_range_end": {"zh": "结束地址", "en": "End Address"},
    "split_info": {"zh": "切分网段", "en": "Split Segment"},
    "save_requirement": {"zh": "保存需求", "en": "Save Requirement"},
    "choose_import_method": {"zh": "请选择导入方式：", "en": "Please choose import method:"},
    "download_excel_template": {"zh": "下载Excel模板", "en": "Download Excel Template"},
    "download_csv_template": {"zh": "下载CSV模板", "en": "Download CSV Template"},
    "address_class": {"zh": "网络类别", "en": "Network Class"},
    "default_netmask": {"zh": "默认子网掩码", "en": "Default Subnet Mask"},
    "integer_representation": {"zh": "整数表示", "en": "Integer Representation"},
    "parent_info": {"zh": "父网段", "en": "Parent Network"},
    "yes": {"zh": "是", "en": "Yes"},
    "no": {"zh": "否", "en": "No"},
    "please_select_a_history_record": {"zh": "请选择一条历史记录", "en": "Please select a history record"},
    "please_select_record_to_delete": {"zh": "请先选择要删除的记录", "en": "Please select the record to delete"},
    "no_undoable_delete_operation": {"zh": "没有可撤销的删除操作", "en": "No undoable delete operation"},
    "please_select_record_to_move_or_swap": {"zh": "请选择要移动或交换的记录", "en": "Please select the record to move or swap"},
    "import_data": {"zh": "导入数据", "en": "Import Data"},
    "data_import_summary": {"zh": "共 {total_count} 条数据，{valid_count} 条有效，{error_count} 条无效", "en": "Total {total_count} records, {valid_count} valid, {error_count} invalid"},
    "valid": {"zh": "有效", "en": "Valid"},
    "invalid": {"zh": "无效", "en": "Invalid"},
    "none": {"zh": "无", "en": "None"},
    
    # 其他
    "msg_already_exists": {"zh": "中已存在名称为 '{name}' 的记录", "en": "already contains a record named '{name}'"},
    "no_valid_data_found": {"zh": "文件中没有找到有效数据", "en": "No valid data found in the file"},
    "no_data_to_import": {"zh": "没有可导入的数据", "en": "No data to import"},
    "confirm_delete": {"zh": "确认删除", "en": "Confirm Delete"},
    "delete_confirmation_message": {"zh": "确定要删除选中的记录吗？此操作可以通过撤销按钮恢复。", "en": "Are you sure you want to delete the selected records? This operation can be undone using the undo button."},
    
    # 功能调试面板
    "test_info_display_effect": {"zh": "点击下方按钮测试不同类型的信息栏显示效果：", "en": "Click the buttons below to test different information bar display effects:"},
    "test_success_message": {"zh": "测试正确信息", "en": "Test Success Message"},
    "test_error_message": {"zh": "测试错误信息", "en": "Test Error Message"},
    "test_long_text_message": {"zh": "测试长文本信息", "en": "Test Long Text Message"},
    "test_mixed_language": {"zh": "测试中英文混排", "en": "Test Mixed Language"},
    "hide_info_bar": {"zh": "隐藏信息栏", "en": "Hide Info Bar"},
    "clear_subnet_split": {"zh": "清空子网切分", "en": "Clear Subnet Split"},
    "function_debug": {"zh": "功能调试", "en": "Function Debug"},
    "test_success_content": {"zh": "测试正确信息：操作成功！", "en": "Test success message: Operation successful!"},
    "test_error_content": {"zh": "测试错误信息：操作失败！", "en": "Test error message: Operation failed!"},
    "test_long_text_content": {"zh": "测试长文本信息：这是一条非常长的测试信息，用于测试信息栏的文本截断功能。", "en": "Test long text message: This is a very long test message used to test the text truncation feature of the information bar."},
    "test_mixed_text_content": {"zh": "中英文混排测试：", "en": "Mixed language test: "},
    
    # 子网重叠检测
    "enter_subnet_list": {"zh": "请输入子网列表", "en": "Please enter subnet list"},
    "no_overlap": {"zh": "无", "en": "No"},
    "no_subnet_overlap_detected": {"zh": "未检测到子网重叠", "en": "No subnet overlap detected"},
    "overlap": {"zh": "重叠", "en": "Overlap"},
    "with": {"zh": "与", "en": "with"},
    
    # IP信息显示 - 通用
    "ip_address": {"zh": "IP地址", "en": "IP Address"},
    "network_class": {"zh": "网络类别", "en": "Network Class"},
    "address_range": {"zh": "地址范围", "en": "Address Range"},
    "first_usable_address": {"zh": "第一个可用地址", "en": "First Usable Address"},
    "last_usable_address": {"zh": "最后一个可用地址", "en": "Last Usable Address"},
    "cidr_prefix": {"zh": "CIDR前缀", "en": "CIDR Prefix"},
    "ip_properties": {"zh": "IP属性", "en": "IP Properties"},
    "extended_info": {"zh": "扩展信息", "en": "Extended Info"},
    
    # IPv6特定
    "first_usable_host": {"zh": "第一个可用主机", "en": "First Usable Host"},
    "last_usable_host": {"zh": "最后一个可用主机", "en": "Last Usable Host"},
    
    # IPv6前缀分析
    "multicast_prefix": {"zh": "多播地址前缀", "en": "Multicast Address Prefix"},
    "interface_local_multicast": {"zh": "(接口本地多播)", "en": "(Interface-Local Multicast)"},
    "link_local_multicast": {"zh": "(链路本地多播)", "en": "(Link-Local Multicast)"},
    "site_local_multicast": {"zh": "(站点本地多播)", "en": "(Site-Local Multicast)"},
    "global_multicast": {"zh": "(全球多播)", "en": "(Global Multicast)"},
    "other_multicast_type": {"zh": "(其他多播类型)", "en": "(Other Multicast Type)"},
    "link_local_prefix": {"zh": "链路本地前缀 (fe80::/10)", "en": "Link-Local Prefix (fe80::/10)"},
    "unique_local_prefix": {"zh": "唯一本地地址前缀 (fc00::/7)", "en": "Unique Local Address Prefix (fc00::/7)"},
    "global_unicast_prefix": {"zh": "全球单播地址前缀 (2000::/3)", "en": "Global Unicast Prefix (2000::/3)"},
    "ipv4_mapped_prefix": {"zh": "IPv4映射地址前缀 (::ffff:0:0/96)", "en": "IPv4-Mapped Address Prefix (::ffff:0:0/96)"},
    "ipv4_ipv6_translation_prefix": {"zh": "IPv4/IPv6转换地址前缀 (64:ff9b::/96)", "en": "IPv4/IPv6 Translation Prefix (64:ff9b::/96)"},
    "documentation_prefix": {"zh": "文档地址前缀 (2001:db8::/32)", "en": "Documentation Prefix (2001:db8::/32)"},
    "blackhole_prefix": {"zh": "黑洞地址前缀 (100::/64)", "en": "Blackhole Prefix (100::/64)"},
    "orchid_prefix": {"zh": "ORCHID地址前缀 (2001:10::/28)", "en": "ORCHID Prefix (2001:10::/28)"},
    "deprecated_site_local_prefix": {"zh": "站点本地地址前缀 (已弃用)", "en": "Deprecated Site-Local Prefix"},
    "global_unicast_prefix_generic": {"zh": "全球单播地址前缀", "en": "Global Unicast Prefix"},
    "private_prefix": {"zh": "私有地址前缀", "en": "Private Prefix"},
    "link_local_prefix_generic": {"zh": "链路本地地址前缀", "en": "Link-Local Prefix"},
    "unknown_prefix": {"zh": "未知地址前缀", "en": "Unknown Address Prefix"},
    
    # IPv6子网规模
    "single_host_address": {"zh": "单主机地址（/128前缀）", "en": "Single Host Address (/128 Prefix)"},
    "small_network": {"zh": "小型网络（/64前缀）", "en": "Small Network (/64 Prefix)"},
    "medium_network": {"zh": "中型网络（/48前缀）", "en": "Medium Network (/48 Prefix)"},
    "regional_network": {"zh": "区域级网络（/{0}前缀）", "en": "Regional Network (/ {0} Prefix)"},
    "large_network": {"zh": "大型网络（/{0}前缀）", "en": "Large Network (/ {0} Prefix)"},
    "extra_large_network": {"zh": "超大型网络（/32或更短前缀）", "en": "Extra Large Network (/32 or Shorter Prefix)"},
    "special_network": {"zh": "特殊网络（/{0}前缀）", "en": "Special Network (/ {0} Prefix)"},
    
    # IPv6地址用途
    "purpose_loopback_ipv6": {"zh": "用于本地主机测试和诊断", "en": "Used for local host testing and diagnostics"},
    "purpose_link_local": {"zh": "用于同一链路内的设备通信，无需路由器", "en": "Used for communication between devices on the same link, no router needed"},
    "purpose_multicast_ipv6": {"zh": "用于一对多通信，支持组播应用", "en": "Used for one-to-many communication, supports multicast applications"},
    "purpose_ipv4_mapped": {"zh": "用于在IPv6网络中表示IPv4地址", "en": "Used to represent IPv4 addresses in IPv6 networks"},
    "purpose_ipv4_ipv6_translation": {"zh": "用于IPv4/IPv6网络之间的地址转换", "en": "Used for address translation between IPv4 and IPv6 networks"},
    "purpose_ula": {"zh": "用于内部网络通信，不可路由到公网", "en": "Used for internal network communication, not routable to the public internet"},
    "purpose_documentation": {"zh": "用于文档示例和教学，不用于实际网络部署", "en": "Used for documentation examples and teaching, not for actual network deployment"},
    "purpose_blackhole": {"zh": "用于黑洞路由，丢弃不需要的流量", "en": "Used for blackhole routing, discarding unwanted traffic"},
    "purpose_orchid": {"zh": "用于ORCHID（Overlay Routable Cryptographic Hash Identifiers）系统", "en": "Used for ORCHID (Overlay Routable Cryptographic Hash Identifiers) system"},
    "purpose_unspecified": {"zh": "表示未指定地址，通常用于初始启动阶段", "en": "Represents unspecified address, typically used during initial startup phase"},
    "purpose_deprecated_site_local": {"zh": "已弃用的站点本地地址，不建议在新网络中使用", "en": "Deprecated site-local address, not recommended for use in new networks"},
    "purpose_specific": {"zh": "根据地址类型和前缀规划的特定用途", "en": "Specific purpose based on address type and prefix planning"},
    
    # IPv6配置建议
    "advice_global_routable": {"zh": "建议配置防火墙规则，限制不必要的入站访问", "en": "It is recommended to configure firewall rules to restrict unnecessary inbound access"},
    "advice_private_network": {"zh": "建议使用SLAAC或DHCPv6自动分配地址", "en": "It is recommended to use SLAAC or DHCPv6 for automatic address assignment"},
    "advice_prefix_length": {"zh": "\n建议为终端设备分配/64前缀，符合IPv6最佳实践", "en": "\nIt is recommended to assign /64 prefixes to end devices, which complies with IPv6 best practices"},
    
    # IPv6 RFC参考
    "related_rfc": {"zh": "相关RFC", "en": "Related RFCs"},
    "network_prefix": {"zh": "网络前缀", "en": "Network Prefix"},
    
    # IPv6地址段
    "segment_index": {"zh": "第{0}段", "en": "Segment {0}"},
    "segment_value": {"zh": "{0} (十六进制) = {1} (十进制) = {2} (二进制)", "en": "{0} (Hex) = {1} (Decimal) = {2} (Binary)"},
    "segment_value_zero": {"zh": "0000 (十六进制) = 0 (十进制) = 0000000000000000 (二进制)", "en": "0000 (Hex) = 0 (Decimal) = 0000000000000000 (Binary)"},
    
    # 子网重叠检测
    "enter_subnet_merge_list": {"zh": "请输入子网合并列表", "en": "Please enter subnet merge list"},
    "enter_ipv6_address": {"zh": "请输入IPv6地址", "en": "Please enter IPv6 address"},
    "enter_ip_address": {"zh": "请输入IP地址", "en": "Please enter IP address"},
    
    # IP信息显示 - 扩展
    "ip_purpose": {"zh": "IP地址用途", "en": "IP Address Purpose"},
    
    # IP用途描述
    "purpose_loopback": {"zh": "本地回环地址，用于测试本地网络", "en": "Local loopback address, used for testing local network"},
    "purpose_private": {"zh": "私有地址，用于内部网络", "en": "Private address, used for internal network"},
    "purpose_multicast": {"zh": "组播地址，用于一对多通信", "en": "Multicast address, used for one-to-many communication"},
    "purpose_reserved": {"zh": "保留地址，用于特殊用途", "en": "Reserved address, used for special purposes"},
    "purpose_global": {"zh": "全球可路由地址，用于公网通信", "en": "Globally routable address, used for public network communication"},
    "purpose_unknown": {"zh": "未知用途", "en": "Unknown purpose"},
    
    # 子网规模描述
    "size_small": {"zh": "小型网络，适合家庭或小型办公室", "en": "Small network, suitable for home or small office"},
    "size_medium": {"zh": "中型网络，适合企业或校园网络", "en": "Medium network, suitable for enterprise or campus network"},
    "size_large": {"zh": "大型网络，适合大型机构或运营商", "en": "Large network, suitable for large organizations or ISPs"},
    
    # 配置建议
    "advice_large_subnet": {"zh": "建议划分为多个子网，便于管理和减少广播域", "en": "It is recommended to divide into multiple subnets for easier management and reduced broadcast domains"},
    "advice_public_network": {"zh": "建议配置静态路由和防火墙规则", "en": "It is recommended to configure static routes and firewall rules"},
    
    # 操作结果
    "attribute": {"zh": "属性", "en": "Attribute"},
    "success": {"zh": "成功", "en": "Success"},
    "successfully_imported": {"zh": "成功导入", "en": "Successfully imported"},
    "records_to": {"zh": "条记录到", "en": "records to"},
    "template_saved_to": {"zh": "模板已保存到: {file_path}", "en": "Template saved to: {file_path}"},
    "copied_to_clipboard": {"zh": "已复制到剪贴板", "en": "Copied to clipboard"},
    "successfully_restored": {"zh": "成功恢复了", "en": "Successfully restored"},
    "records": {"zh": "条记录", "en": "records"},
    "invalid_network_address_format": {"zh": "无效的网络地址格式", "en": "Invalid network address format"},
    "cidr_address_has_host_bits_set": {"zh": "CIDR地址包含主机位", "en": "CIDR address has host bits set"},
    "invalid_ip_format_expected_4_octets": {"zh": "IP地址格式错误, 需要4个八位组（例如：192.168.1.1）", "en": "Invalid IP format, expected 4 octets"},
    "got": {"zh": "实际为", "en": "got"},
    "invalid_octet_in_ip": {"zh": "IP地址中八位组", "en": "Invalid octet in IP"},
    "must_be_less_than_or_equal_to_255": {"zh": "无效, 必须≤255（例如：192.168.1.1）", "en": "must be ≤ 255"},
    "invalid_ipv4_address_format": {"zh": "无效的IPv4地址格式: IP地址中只允许使用十进制数字和点（例如：192.168.1.1）", "en": "Invalid IPv4 address format"},
    "invalid_ip_address_format": {"zh": "无效的IP地址格式", "en": "Invalid IP address format"},
    "unexpected_slash_in_ip_address": {"zh": "IP地址中包含不允许的字符'/'（例如：192.168.1.1）", "en": "unexpected '/' in IP address"},
    "invalid_ipv6_address_format": {"zh": "无效的IPv6地址格式（例如：2001:0db8:85a3:0000:0000:8a2e:0370:7334）", "en": "Invalid IPv6 address format"},
    "invalid_ipv6_address": {"zh": "无效的IPv6地址", "en": "Invalid IPv6 address"},
    "at_most_4_hex_digits_per_group": {"zh": "每组最多允许4个十六进制字符（例如：2001:0db8::1）", "en": "at most 4 hex digits per group"},
    "too_many_colons": {"zh": "冒号数量过多（例如：2001:0db8::1）", "en": "too many colons"},
    "octet_too_long_max_3_characters_allowed": {"zh": "八位组过长, 最多允许3个字符（例如：192.168.1.1）", "en": "octet too long, max 3 characters allowed"},
    "group_too_long_max_4_hex_characters_allowed": {"zh": "组过长, 每组最多允许4个十六进制字符（例如：2001:0db8::1）", "en": "group too long, max 4 hex characters allowed"},
    "max_3_chars_0_255_allowed": {"zh": "无效, 最多允许3个字符(0-255)", "en": "max 3 chars (0-255) allowed"},
    "is_not_a_subnet_of": {"zh": "不是", "en": "is not a subnet of"},
    "is_not_ipv4_mapped_ipv6_address": {"zh": "不是IPv4映射的IPv6地址，该功能仅支持IPv4映射格式(如::ffff:192.168.1.1)", "en": "is not an IPv4-mapped IPv6 address, this feature only supports IPv4-mapped format (e.g., ::ffff:192.168.1.1)"},
    "cannot_create_subnet_for": {"zh": "无法为", "en": "Cannot create subnet for"},
    "with_prefix_length": {"zh": "创建前缀长度为", "en": "with prefix length"},
    "failed_to_create_subnet": {"zh": "创建子网失败", "en": "Failed to create subnet"},
    "cannot_allocate_sufficiently_large_subnet_for": {"zh": "无法为", "en": "Cannot allocate sufficiently large subnet for"},
    "subnet_list_cannot_be_empty": {"zh": "子网列表不能为空", "en": "Subnet list cannot be empty"},
    "start_ip_must_be_less_than_or_equal_to_end_ip": {"zh": "起始IP地址必须小于或等于结束IP地址", "en": "Start IP address must be less than or equal to end IP address"},
    "at_least_two_subnets_needed_to_check_overlap": {"zh": "至少需要两个子网来检查重叠", "en": "At least two subnets needed to check overlap"},
    
    # 网络类别
    "pieces": {"zh": "个", "en": "pieces"},
    "class_a": {"zh": "A类", "en": "Class A"},
    "class_b": {"zh": "B类", "en": "Class B"},
    "class_c": {"zh": "C类", "en": "Class C"},
    "class_d": {"zh": "D类", "en": "Class D"},
    "class_e": {"zh": "E类", "en": "Class E"},
    
    # 图表相关
    "segment": {"zh": "网段", "en": "Segment"},
    "legend": {"zh": "图例", "en": "Legend"},
    "multicolor": {"zh": "多色", "en": "Multi-color"},
    "no_segment_data": {"zh": "暂无网段数据", "en": "No segment data"},
    "chart_drawing_failed": {"zh": "图表绘制失败", "en": "Chart drawing failed"}
}

# 当前语言设置
_current_language = "zh"  # 默认中文


def set_language(lang):
    """
    设置当前语言
    
    Args:
        lang: 语言代码，支持 "zh" (中文) 和 "en" (英文)
    """
    global _current_language
    if lang in ["zh", "en"]:
        _current_language = lang


def get_language():
    """
    获取当前语言
    
    Returns:
        当前语言代码 ("zh" 或 "en")
    """
    return _current_language


def _(key, **kwargs):
    """
    翻译函数
    
    Args:
        key: 翻译键名
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    # 获取翻译，如果不存在则返回键名
    translation = TRANSLATIONS.get(key, {})
    text = translation.get(_current_language, key)
    
    # 格式化文本
    if kwargs:
        text = text.format(**kwargs)
    
    return text


def get_supported_languages():
    """
    获取支持的语言列表
    
    Returns:
        支持的语言列表，格式为 [(语言代码, 语言名称)]
    """
    return [
        ("zh", "中文"),
        ("en", "English")
    ]
