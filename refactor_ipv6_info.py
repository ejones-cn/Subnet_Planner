#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用于重构execute_ipv6_info函数的脚本
"""

import os

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换基本信息部分
basic_info_old = '''            # 分组显示结果
            # 1. 基本信息
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("ip_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("IP版本", ipv6_info.get("version", "")))
            # 分析IPv6地址类型
            ip_address = ipv6_info.get("ip_address", "")
            address_type = "未知"
            if ipv6_info.get("is_loopback"):
                address_type = "回环地址"
            elif ipv6_info.get("is_unspecified"):
                address_type = "未指定地址"
            elif ipv6_info.get("is_multicast"):
                address_type = "组播地址"
            elif ipv6_info.get("is_link_local"):
                address_type = "链路本地单播地址"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                address_type = "唯一本地单播地址 (ULA)"
            elif ip_address.startswith("2001:0db8:"):
                address_type = "文档/测试地址"
            elif ip_address.startswith("2000:"):
                address_type = "全球单播地址"
            # 添加IPv4映射地址检测
            elif "::ffff:" in ip_address:
                address_type = "IPv4映射的IPv6地址"
            self.ipv6_info_tree.insert("", tk.END, values=("地址类型", address_type))
            self.ipv6_info_tree.insert("", tk.END, values=("CIDR前缀", ipv6_info.get("cidr", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("前缀长度", ipv6_info.get("prefix_length", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("网络地址", ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("广播地址", ipv6_info.get("broadcast_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("第一个可用主机", ipv6_info.get("first_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("最后一个可用主机", ipv6_info.get("last_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("总主机数", ipv6_info.get("total_hosts", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("可用主机数", ipv6_info.get("usable_hosts", "")))'''

basic_info_new = '''            # 分组显示结果
            # 1. 基本信息
            ip_address = ipv6_info.get("ip_address", "")
            
            self._insert_treeview_item(self.ipv6_info_tree, "IP地址", ipv6_info.get("ip_address", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "IP版本", ipv6_info.get("version", ""))
            
            # 分析IPv6地址类型
            address_type = self._analyze_ipv6_address_type(ipv6_info)
            self._insert_treeview_item(self.ipv6_info_tree, "地址类型", address_type)
            
            self._insert_treeview_item(self.ipv6_info_tree, "CIDR前缀", ipv6_info.get("cidr", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "前缀长度", ipv6_info.get("prefix_length", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "网络地址", ipv6_info.get("network_address", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "广播地址", ipv6_info.get("broadcast_address", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "子网掩码", ipv6_info.get("subnet_mask", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "第一个可用主机", ipv6_info.get("first_host", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "最后一个可用主机", ipv6_info.get("last_host", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "总主机数", ipv6_info.get("total_hosts", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "可用主机数", ipv6_info.get("usable_hosts", ""))'''

content = content.replace(basic_info_old, basic_info_new)

# 替换地址格式部分
address_format_old = '''            # 2. 地址格式
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址格式", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("压缩格式", ipv6_info.get("compressed", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("展开格式", ipv6_info.get("exploded", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("反向DNS格式", ipv6_info.get("reverse_dns", "")))

            # 添加IPv4映射地址转换（如果适用）
            if "::ffff:" in ip_address:
                ipv4_part = ip_address.split("::ffff:")[-1]
                self.ipv6_info_tree.insert("", tk.END, values=("映射的IPv4地址", ipv4_part))'''

address_format_new = '''            # 2. 地址格式
            self._insert_treeview_section(self.ipv6_info_tree, "地址格式")
            self._insert_treeview_item(self.ipv6_info_tree, "压缩格式", ipv6_info.get("compressed", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "展开格式", ipv6_info.get("exploded", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "反向DNS格式", ipv6_info.get("reverse_dns", ""))

            # 添加IPv4映射地址转换（如果适用）
            if "::ffff:" in ip_address:
                ipv4_part = ip_address.split("::ffff:")[-1]
                self._insert_treeview_item(self.ipv6_info_tree, "映射的IPv4地址", ipv4_part)'''

content = content.replace(address_format_old, address_format_new)

# 替换地址属性部分
address_properties_old = '''            # 3. 地址属性
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址属性", ""))
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否全局可路由", "是" if ipv6_info.get("is_global") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否私有地址", "是" if ipv6_info.get("is_private") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否链路本地", "是" if ipv6_info.get("is_link_local") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否回环地址", "是" if ipv6_info.get("is_loopback") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否组播地址", "是" if ipv6_info.get("is_multicast") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否未指定地址", "是" if ipv6_info.get("is_unspecified") else "否")
            )
            self.ipv6_info_tree.insert(
                "", tk.END, values=("是否保留地址", "是" if ipv6_info.get("is_reserved") else "否")
            )
            self.ipv6_info_tree.insert("", tk.END, values=("是否IPv4映射", "是" if "::ffff:" in ip_address else "否"))'''

address_properties_new = '''            # 3. 地址属性
            self._insert_treeview_section(self.ipv6_info_tree, "地址属性")
            self._insert_treeview_item(self.ipv6_info_tree, "是否全局可路由", "是" if ipv6_info.get("is_global") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否私有地址", "是" if ipv6_info.get("is_private") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否链路本地", "是" if ipv6_info.get("is_link_local") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否回环地址", "是" if ipv6_info.get("is_loopback") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否组播地址", "是" if ipv6_info.get("is_multicast") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否未指定地址", "是" if ipv6_info.get("is_unspecified") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否保留地址", "是" if ipv6_info.get("is_reserved") else "否")
            self._insert_treeview_item(self.ipv6_info_tree, "是否IPv4映射", "是" if "::ffff:" in ip_address else "否")'''

content = content.replace(address_properties_old, address_properties_new)

# 替换地址结构分析部分
address_structure_old = '''            # 4. 地址结构分析
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址结构分析", ""))

            # 分析前缀类型
            prefix_analysis = ""
            if ipv6_info.get("is_multicast"):
                prefix_analysis = "多播地址前缀"
                # 进一步分析多播地址类型
                if ip_address.startswith("ff01:"):
                    prefix_analysis += " (接口本地多播)"
                elif ip_address.startswith("ff02:"):
                    prefix_analysis += " (链路本地多播)"
                elif ip_address.startswith("ff05:"):
                    prefix_analysis += " (站点本地多播)"
                elif ip_address.startswith("ff0e:"):
                    prefix_analysis += " (全球多播)"
                else:
                    prefix_analysis += " (其他多播类型)"
            elif ip_address.startswith("fe80:"):
                prefix_analysis = "链路本地前缀 (fe80::/10)"
            elif ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                prefix_analysis = "唯一本地地址前缀 (fc00::/7)"
            elif ip_address.startswith("2000:") or ip_address.startswith("2001:") or ip_address.startswith("2002:"):
                prefix_analysis = "全球单播地址前缀 (2000::/3)"
            elif ip_address.startswith("::ffff:"):
                prefix_analysis = "IPv4映射地址前缀 (::ffff:0:0/96)"
            elif ip_address.startswith("64:ff9b::"):
                prefix_analysis = "IPv4/IPv6转换地址前缀 (64:ff9b::/96)"
            elif ip_address.startswith("2001:db8::"):
                prefix_analysis = "文档地址前缀 (2001:db8::/32)"
            elif ip_address == "::1":
                prefix_analysis = "回环地址 (::1/128)"
            elif ip_address == "::":
                prefix_analysis = "未指定地址 (::/128)"
            elif ip_address.startswith("100::"):
                prefix_analysis = "黑洞地址前缀 (100::/64)"
            elif ip_address.startswith("2001:10::"):
                prefix_analysis = "ORCHID地址前缀 (2001:10::/28)"
            elif ip_address.startswith("fec0:"):
                prefix_analysis = "站点本地地址前缀 (已弃用)"
            else:
                # 对于未匹配到的地址，提供通用的前缀分析
                if ipv6_info.get("is_global"):
                    prefix_analysis = "全球单播地址前缀"
                elif ipv6_info.get("is_private"):
                    prefix_analysis = "私有地址前缀"
                elif ipv6_info.get("is_link_local"):
                    prefix_analysis = "链路本地地址前缀"
                else:
                    prefix_analysis = "未知地址前缀"
            # 获取用户指定的CIDR前缀长度
            user_cidr = ipv6_info.get("prefix_length", ipv6_info.get("cidr", 128))

            # 生成完整的前缀分析，包括基础前缀和用户指定的CIDR
            full_prefix_analysis = f"{prefix_analysis}，网络前缀：/{user_cidr}"
            self.ipv6_info_tree.insert("", tk.END, values=("前缀分析", full_prefix_analysis))

            # 分析地址结构
            segments = ip_address.split(":")
            if len(segments) > 1:
                self.ipv6_info_tree.insert("", tk.END, values=("地址段数量", f"{len(segments)}"))'''

address_structure_new = '''            # 4. 地址结构分析
            self._insert_treeview_section(self.ipv6_info_tree, "地址结构分析")
            
            # 分析前缀类型
            prefix_analysis = self._analyze_ipv6_prefix(ipv6_info)
            
            # 获取用户指定的CIDR前缀长度
            user_cidr = ipv6_info.get("prefix_length", ipv6_info.get("cidr", 128))
            
            # 生成完整的前缀分析，包括基础前缀和用户指定的CIDR
            full_prefix_analysis = f"{prefix_analysis}，网络前缀：/{user_cidr}"
            self._insert_treeview_item(self.ipv6_info_tree, "前缀分析", full_prefix_analysis)
            
            # 分析地址结构
            segments = ip_address.split(":")
            if len(segments) > 1:
                self._insert_treeview_item(self.ipv6_info_tree, "地址段数量", f"{len(segments)}")'''

content = content.replace(address_structure_old, address_structure_new)

# 替换二进制表示部分
binary_representation_old = '''            # 5. 二进制表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("二进制表示", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("binary", "")))

            # 计算并显示子网掩码的二进制表示
            if ipv6_info.get("subnet_mask"):
                subnet_mask = ipv6_info["subnet_mask"]
                subnet_bin = subnet_mask.replace(':', '').zfill(32)
                subnet_bin_grouped = ' '.join([subnet_bin[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", subnet_bin_grouped))

            # 计算并显示网络地址的二进制表示
            if ipv6_info.get("network_address"):
                network_addr = ipv6_info["network_address"]
                network_bin = network_addr.replace(':', '').zfill(32)
                network_bin_grouped = ' '.join([network_bin[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("网络地址", network_bin_grouped))

            # 计算并显示广播地址的二进制表示
            if ipv6_info.get("broadcast_address"):
                broadcast_addr = ipv6_info["broadcast_address"]
                broadcast_bin = broadcast_addr.replace(':', '').zfill(32)
                broadcast_bin_grouped = ' '.join([broadcast_bin[i:i + 4] for i in range(0, 32, 4)])
                self.ipv6_info_tree.insert("", tk.END, values=("广播地址", broadcast_bin_grouped))'''

binary_representation_new = '''            # 5. 二进制表示
            self._insert_treeview_section(self.ipv6_info_tree, "二进制表示")
            self._insert_ipv6_binary_representation(self.ipv6_info_tree, ipv6_info)'''

content = content.replace(binary_representation_old, binary_representation_new)

# 替换十六进制表示部分
hex_representation_old = '''            # 6. 十六进制表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("十六进制表示", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("hexadecimal", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("网络地址", ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("广播地址", ipv6_info.get("broadcast_address", "")))'''

hex_representation_new = '''            # 6. 十六进制表示
            self._insert_treeview_section(self.ipv6_info_tree, "十六进制表示")
            self._insert_treeview_item(self.ipv6_info_tree, "IP地址", ipv6_info.get("hexadecimal", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "子网掩码", ipv6_info.get("subnet_mask", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "网络地址", ipv6_info.get("network_address", ""))
            self._insert_treeview_item(self.ipv6_info_tree, "广播地址", ipv6_info.get("broadcast_address", ""))'''

content = content.replace(hex_representation_old, hex_representation_new)

# 替换十进制数值表示部分
decimal_representation_old = '''            # 7. 十进制数值表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("十进制数值表示", ""))
            if "integer" in ipv6_info:
                self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info["integer"]))'''

decimal_representation_new = '''            # 7. 十进制数值表示
            self._insert_treeview_section(self.ipv6_info_tree, "十进制数值表示")
            if "integer" in ipv6_info:
                self._insert_treeview_item(self.ipv6_info_tree, "IP地址", ipv6_info["integer"])'''

content = content.replace(decimal_representation_old, decimal_representation_new)

# 将修改后的内容写回文件
with open('windows_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("execute_ipv6_info函数重构完成")
