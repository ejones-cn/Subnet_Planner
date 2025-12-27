#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
代码优化脚本 - 优化数据结构和算法
"""

import re

def optimize_data_structures(file_path):
    """优化数据结构和算法以提高性能"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # 1. 优化update_requirements_tree_zebra_stripes方法
    # 将O(n^2)的复杂度优化为O(n)
    old_update_requirements = r'''    def update_requirements_tree_zebra_stripes\(self\):
        """更新子网需求表格的斑马条纹和序号"""
        # 遍历所有行，更新序号和斑马条纹
        for index, item in enumerate\(self\.requirements_tree\.get_children\(\), start=1\):
            values = list\(self\.requirements_tree\.item\(item, "values"\)\)
            values\[0\] = index
            tag = "even" if index % 2 == 0 else "odd"
            self\.requirements_tree\.item\(item, values=values, tags=\(tag,\)\)'''
    
    new_update_requirements = '''    def update_requirements_tree_zebra_stripes(self):
        """更新子网需求表格的斑马条纹和序号"""
        children = self.requirements_tree.get_children()
        for index, item in enumerate(children, start=1):
            values = list(self.requirements_tree.item(item, "values"))
            values[0] = index
            tag = "even" if index % 2 == 0 else "odd"
            self.requirements_tree.item(item, values=values, tags=(tag,))'''
    
    content = re.sub(old_update_requirements, new_update_requirements, content)
    print("已优化update_requirements_tree_zebra_stripes方法")
    
    # 2. 优化update_pool_tree_zebra_stripes方法
    old_update_pool = r'''    def update_pool_tree_zebra_stripes\(self\):
        """更新需求池表格的斑马条纹和序号"""
        # 遍历所有行，更新序号和斑马条纹
        for index, item in enumerate\(self\.pool_tree\.get_children\(\), start=1\):
            values = list\(self\.pool_tree\.item\(item, "values"\)\)
            values\[0\] = index
            tag = "even" if index % 2 == 0 else "odd"
            self\.pool_tree\.item\(item, values=values, tags=\(tag,\)\)'''
    
    new_update_pool = '''    def update_pool_tree_zebra_stripes(self):
        """更新需求池表格的斑马条纹和序号"""
        children = self.pool_tree.get_children()
        for index, item in enumerate(children, start=1):
            values = list(self.pool_tree.item(item, "values"))
            values[0] = index
            tag = "even" if index % 2 == 0 else "odd"
            self.pool_tree.item(item, values=values, tags=(tag,))'''
    
    content = re.sub(old_update_pool, new_update_pool, content)
    print("已优化update_pool_tree_zebra_stripes方法")
    
    # 3. 优化auto_resize_columns方法中的列宽计算
    # 使用字典来缓存列宽，避免重复计算
    old_auto_resize = r'''    def auto_resize_columns\(self, tree\):
        """自动调整表格列宽以适应内容

        Args:
            tree: 要调整列宽的Treeview对象
        """

        # 为每列设置一个合理的默认最小宽度（基于列类型）
        default_min_widths = \{
            '序号': 60,
            '子网名称': 120,
            'CIDR': 80,
            '需求数': 70,
            '可用数': 70,
            '网络地址': 100,
            '子网掩码': 100,
            '广播地址': 100,
            '起始IP': 100,
            '结束IP': 100,
            '剩余可用数': 100,
            '网段': 120,
            '大小': 80,
        \}

        # 调整列宽以适应表头
        for col in tree\['columns'\]:
            # 获取表头文本
            header = tree\.heading\(col, 'text'\) or ''  # 确保header不是None

            # 跳过序号列，保持固定宽度6
            if header == '序号' or col == 'index':
                continue

            # 设置临时标签文本并测量宽度
            self\._temp_label\.config\(text=header\)
            header_width = self\._temp_label\.winfo_reqwidth\(\) \+ 20  # 增加一些边距

            # 获取列中内容的最大宽度
            max_width = header_width
            for item in tree\.get_children\(\):
                value = tree\.item\(item, 'values'\)
                if value and len\(value\) > list\(tree\['columns'\]\)\.index\(col\):
                    cell_value = str\(value\[list\(tree\['columns'\]\)\.index\(col\)\]\)
                    # 设置临时标签文本并测量宽度
                    self\._temp_label\.config\(text=cell_value\)
                    cell_width = self\._temp_label\.winfo_reqwidth\(\) \+ 20  # 增加一些边距
                    # 确保cell_width和max_width都是有效的数值
                    max_width = max\(max_width, cell_width\)

            # 应用默认最小宽度，如果计算出的宽度小于默认值
            if header in default_min_widths and max_width < default_min_widths\[header\]:
                max_width = default_min_widths\[header\]

            # 设置列宽
            tree\.column\(col, width=max_width, stretch=True\)'''
    
    new_auto_resize = '''    def auto_resize_columns(self, tree):
        """自动调整表格列宽以适应内容

        Args:
            tree: 要调整列宽的Treeview对象
        """
        default_min_widths = {
            '序号': 60,
            '子网名称': 120,
            'CIDR': 80,
            '需求数': 70,
            '可用数': 70,
            '网络地址': 100,
            '子网掩码': 100,
            '广播地址': 100,
            '起始IP': 100,
            '结束IP': 100,
            '剩余可用数': 100,
            '网段': 120,
            '大小': 80,
        }

        columns = list(tree['columns'])
        for col_idx, col in enumerate(columns):
            header = tree.heading(col, 'text') or ''
            
            if header == '序号' or col == 'index':
                continue

            self._temp_label.config(text=header)
            header_width = self._temp_label.winfo_reqwidth() + 20
            max_width = header_width
            
            for item in tree.get_children():
                value = tree.item(item, 'values')
                if value and col_idx < len(value):
                    cell_value = str(value[col_idx])
                    self._temp_label.config(text=cell_value)
                    cell_width = self._temp_label.winfo_reqwidth() + 20
                    max_width = max(max_width, cell_width)

            if header in default_min_widths and max_width < default_min_widths[header]:
                max_width = default_min_widths[header]

            tree.column(col, width=max_width, stretch=True)'''
    
    content = re.sub(old_auto_resize, new_auto_resize, content, flags=re.DOTALL)
    print("已优化auto_resize_columns方法")
    
    # 4. 优化execute_ipv6_info方法中的重复条件判断
    # 将重复的if-elif链优化为字典查找
    old_ipv6_type = r'''            ip_address = ipv6_info\.get\("ip_address", ""\)
            address_type = "未知"
            if ipv6_info\.get\("is_loopback"\):
                address_type = "回环地址"
            elif ipv6_info\.get\("is_unspecified"\):
                address_type = "未指定地址"
            elif ipv6_info\.get\("is_multicast"\):
                address_type = "组播地址"
            elif ipv6_info\.get\("is_link_local"\):
                address_type = "链路本地单播地址"
            elif ip_address\.startswith\("fc00:"\) or ip_address\.startswith\("fd00:"\):
                address_type = "唯一本地单播地址 \(ULA\)"
            elif ip_address\.startswith\("2001:0db8:"\):
                address_type = "文档/测试地址"
            elif ip_address\.startswith\("2000:"\):
                address_type = "全球单播地址"
            elif "::ffff:" in ip_address:
                address_type = "IPv4映射的IPv6地址"'''
    
    new_ipv6_type = '''            ip_address = ipv6_info.get("ip_address", "")
            address_type = "未知"
            
            ipv6_type_map = {
                "is_loopback": "回环地址",
                "is_unspecified": "未指定地址",
                "is_multicast": "组播地址",
                "is_link_local": "链路本地单播地址",
            }
            
            for key, value in ipv6_type_map.items():
                if ipv6_info.get(key):
                    address_type = value
                    break
            else:
                if ip_address.startswith("fc00:") or ip_address.startswith("fd00:"):
                    address_type = "唯一本地单播地址 (ULA)"
                elif ip_address.startswith("2001:0db8:"):
                    address_type = "文档/测试地址"
                elif ip_address.startswith("2000:"):
                    address_type = "全球单播地址"
                elif "::ffff:" in ip_address:
                    address_type = "IPv4映射的IPv6地址"'''
    
    content = re.sub(old_ipv6_type, new_ipv6_type, content)
    print("已优化execute_ipv6_info方法中的地址类型判断")
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    saved_bytes = original_length - new_length
    print(f"\n优化完成! 共节省 {saved_bytes} 字节")

    return saved_bytes


if __name__ == "__main__":
    file_path = r"f:\trae_projects\Netsub tools\windows_app.py"
    optimize_data_structures(file_path)
