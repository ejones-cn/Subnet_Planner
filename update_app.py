#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
更新应用程序，将IP转换功能替换为IPv6信息查询功能
"""

import re


def main():
    # 读取文件内容
    with open('windows_app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到create_ip_conversion_section方法的位置
    create_start = None
    create_end = None
    for i, line in enumerate(lines):
        if 'def create_ip_conversion_section(self):' in line:
            create_start = i
        elif create_start is not None and 'def create_ip_info_section(self):' in line:
            create_end = i
            break
    
    # 找到execute_ipv4_to_ipv6方法的位置
    execute_start = None
    execute_end = None
    for i, line in enumerate(lines):
        if 'def execute_ipv4_to_ipv6(self):' in line:
            execute_start = i
        elif execute_start is not None and 'def execute_ip_info(self):' in line:
            execute_end = i
            break
    
    # 替换create_ip_conversion_section方法
    new_create_method = [
        '    def create_ip_conversion_section(self):\n',
        '        """创建IPv6地址信息查询功能界面"""\n',
        '        # 创建输入区域\n',
        '        input_frame = ttk.LabelFrame(self.conversion_frame, text="IPv6地址信息查询", padding="10")\n',
        '        input_frame.pack(fill=tk.X, pady=(0, 10))\n',
        '        \n',
        '        ttk.Label(input_frame, text="IPv6地址:").pack(side=tk.LEFT, padx=(0, 5))\n',
        '        self.ipv6_info_entry = ttk.Entry(input_frame, width=40)\n',
        '        self.ipv6_info_entry.pack(side=tk.LEFT, padx=(0, 10))\n',
        '        self.ipv6_info_entry.insert(0, "2001:0db8:85a3:0000:0000:8a2e:0370:7334")\n',
        '        \n',
        '        # CIDR下拉列表（IPv6支持1-128）\n',
        '        ttk.Label(input_frame, text="CIDR:").pack(side=tk.LEFT, padx=(0, 5))\n',
        '        self.ipv6_cidr_var = tk.StringVar()\n',
        '        self.ipv6_cidr_combobox = ttk.Combobox(input_frame, textvariable=self.ipv6_cidr_var, width=3, state="readonly")\n',
        '        self.ipv6_cidr_combobox[\'values\'] = list(range(1, 129))\n',
        '        self.ipv6_cidr_combobox.current(63)  # 默认选择64\n',
        '        self.ipv6_cidr_combobox.pack(side=tk.LEFT, padx=(0, 10))\n',
        '        \n',
        '        self.ipv6_info_btn = ttk.Button(input_frame, text="查询信息", command=self.execute_ipv6_info)\n',
        '        self.ipv6_info_btn.pack(side=tk.LEFT)\n',
        '        \n',
        '        # 创建结果区域\n',
        '        result_frame = ttk.LabelFrame(self.conversion_frame, text="查询结果", padding="10")\n',
        '        result_frame.pack(fill=tk.BOTH, expand=True)\n',
        '        \n',
        '        self.ipv6_info_tree = ttk.Treeview(result_frame, columns=("item", "value"), show="headings")\n',
        '        self.ipv6_info_tree.heading("item", text="项目")\n',
        '        self.ipv6_info_tree.heading("value", text="值")\n',
        '        \n',
        '        self.ipv6_info_tree.column("item", width=200)\n',
        '        self.ipv6_info_tree.column("value", width=350)\n',
        '        \n',
        '        self.ipv6_info_tree.pack(fill=tk.BOTH, expand=True)\n',
        '        self.configure_treeview_styles(self.ipv6_info_tree, include_special_tags=True)\n',
        '        \n'
    ]
    
    # 替换execute_ipv4_to_ipv6和execute_ipv6_to_ipv4方法
    new_execute_method = [
        '    def execute_ipv6_info(self):\n',
        '        """执行IPv6地址信息查询"""\n',
        '        try:\n',
        '            # 清空结果树\n',
        '            for item in self.ipv6_info_tree.get_children():\n',
        '                self.ipv6_info_tree.delete(item)\n',
        '            \n',
        '            ipv6 = self.ipv6_info_entry.get().strip()\n',
        '            if not ipv6:\n',
        '                self.show_info("提示", "请输入IPv6地址")\n',
        '                return\n',
        '            \n',
        '            # 获取CIDR\n',
        '            cidr = self.ipv6_cidr_var.get()\n',
        '            \n',
        '            # 构造网络地址\n',
        '            network_str = f"{ipv6}/{cidr}"\n',
        '            \n',
        '            # 获取IPv6信息\n',
        '            ipv6_info = get_ip_info(network_str)\n',
        '            \n',
        '            # 显示结果\n',
        '            for key, value in ipv6_info.items():\n',
        '                # 将英文键转换为中文\n',
        '                key_map = {\n',
        '                    "ip_address": "IP地址",\n',
        '                    "version": "IP版本",\n',
        '                    "is_global": "是否全局可路由",\n',
        '                    "is_private": "是否私有地址",\n',
        '                    "is_link_local": "是否链路本地",\n',
        '                    "is_loopback": "是否回环地址",\n',
        '                    "is_multicast": "是否组播地址",\n',
        '                    "is_unspecified": "是否未指定地址",\n',
        '                    "is_reserved": "是否保留地址",\n',
        '                    "network_address": "网络地址",\n',
        '                    "broadcast_address": "广播地址",\n',
        '                    "subnet_mask": "子网掩码",\n',
        '                    "cidr": "CIDR前缀",\n',
        '                    "prefix_length": "前缀长度",\n',
        '                    "total_hosts": "总主机数",\n',
        '                    "usable_hosts": "可用主机数",\n',
        '                    "first_host": "第一个可用主机",\n',
        '                    "last_host": "最后一个可用主机",\n',
        '                    "binary": "二进制表示",\n',
        '                    "hexadecimal": "十六进制表示",\n',
        '                    "compressed": "压缩格式",\n',
        '                    "exploded": "展开格式",\n',
        '                    "reverse_dns": "反向DNS格式",\n',
        '                    "integer": "整数值",\n',
        '                    "ip_int": "整数值",\n',
        '                    "class": "地址类别"\n',
        '                }\n',
        '                \n',
        '                display_key = key_map.get(key, key)\n',
        '                self.ipv6_info_tree.insert("", tk.END, values=(display_key, value))\n',
        '            \n',
        '        except ValueError as e:\n',
        '            self.show_info("错误", f"查询失败: {str(e)}")\n',
        '        except Exception as e:\n',
        '            self.show_info("错误", f"操作失败: {str(e)}")\n',
        '        \n'
    ]
    
    # 构建新的文件内容
    new_lines = []
    
    # 添加create_start之前的行
    new_lines.extend(lines[:create_start])
    
    # 添加新的create_ip_conversion_section方法
    new_lines.extend(new_create_method)
    
    # 添加create_end到execute_start之间的行
    new_lines.extend(lines[create_end:execute_start])
    
    # 添加新的execute_ipv6_info方法
    new_lines.extend(new_execute_method)
    
    # 添加execute_end之后的行
    new_lines.extend(lines[execute_end:])
    
    # 保存新的文件内容
    with open('windows_app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("文件更新完成！")


if __name__ == "__main__":
    main()
