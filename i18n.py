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
    "cancel": {"zh": "取消", "en": "Cancel"},
    "ok": {"zh": "确定", "en": "OK"},
    
    # 菜单和标签
    "history": {"zh": "历史记录", "en": "History"},
    "parent_network": {"zh": "父网段", "en": "Parent Network"},
    "split_segments": {"zh": "切分段", "en": "Split Segments"},
    "execute_split": {"zh": "执行切分", "en": "Execute Split"},
    "split_result": {"zh": "切分结果", "en": "Split Result"},
    "export_result": {"zh": "导出结果", "en": "Export Result"},
    "parent_network_settings": {"zh": "父网段设置", "en": "Parent Network Settings"},
    "requirements_pool": {"zh": "需求池", "en": "Requirements Pool"},
    "subnet_requirements": {"zh": "子网需求", "en": "Subnet Requirements"},
    "move_records": {"zh": "↔", "en": "↔"},
    "import_requirements": {"zh": "导入", "en": "Import"},
    "planning_result": {"zh": "规划结果", "en": "Planning Result"},
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
    "about": {"zh": "关于", "en": "About"},
    "author": {"zh": "作者", "en": "Author"},
    
    # 错误信息
    "record_already_exists": {"zh": "中已存在名称为 '{name}' 的记录", "en": "already contains a record named '{name}'"},
    "input_cannot_be_empty": {"zh": "输入不能为空", "en": "Input cannot be empty"},
    "subnet_already_exists": {"zh": "已经存在名称为 '{name}' 的子网，请使用其他名称", "en": "A subnet named '{name}' already exists, please use another name"},
    "host_count_must_be_greater_than_0": {"zh": "主机数量必须大于0", "en": "Host count must be greater than 0"},
    "host_count_must_be_integer": {"zh": "主机数量必须是整数", "en": "Host count must be an integer"},
    "please_enter_parent_network": {"zh": "请输入父网段", "en": "Please enter parent network"},
    "invalid_parent_network_format": {"zh": "父网段格式不正确，请输入有效的CIDR格式（例如：192.168.1.0/24）", "en": "Invalid parent network format, please enter a valid CIDR format (e.g., 192.168.1.0/24)"},
    "please_add_at_least_one_requirement": {"zh": "请添加至少一个子网需求", "en": "Please add at least one subnet requirement"},
    "subnet_planning_failed": {"zh": "子网规划失败", "en": "Subnet planning failed"},
    "unknown_error_occurred": {"zh": "发生未知错误", "en": "An unknown error occurred"},
    "invalid_parent_network_cidr": {"zh": "父网段格式无效，请输入有效的CIDR格式（如: 10.0.0.0/8）", "en": "Invalid parent network CIDR format, please enter a valid CIDR (e.g., 10.0.0.0/8)"},
    "invalid_split_segment_cidr": {"zh": "切分网段格式无效，请输入有效的CIDR格式（如: 10.21.50.0/23）", "en": "Invalid split segment CIDR format, please enter a valid CIDR (e.g., 10.21.50.0/23)"},
    "please_enter_subnet_name": {"zh": "请输入子网名称", "en": "Please enter subnet name"},
    "please_enter_valid_host_count": {"zh": "请输入有效的主机数量", "en": "Please enter a valid host count"},
    "msg_template_generation_failed": {"zh": "模板生成失败", "en": "Template generation failed"},
    "msg_file_parse_failed": {"zh": "文件解析失败", "en": "File parsing failed"},
    
    # 应用名称
    "app_name": {"zh": "子网规划师", "en": "Subnet Planner"},
    "version": {"zh": "版本", "en": "Version"},
    
    # 其他
    "msg_already_exists": {"zh": "中已存在名称为 '{name}' 的记录", "en": "already contains a record named '{name}'"},
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
