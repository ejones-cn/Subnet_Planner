    def execute_ipv6_info(self):
        """执行IPv6地址信息查询"""
        try:
            # 清空结果树
            for item in self.ipv6_info_tree.get_children():
                self.ipv6_info_tree.delete(item)
            
            ipv6 = self.ipv6_info_entry.get().strip()
            if not ipv6:
                self.show_info("提示", "请输入IPv6地址")
                return
            
            # 获取CIDR
            cidr = self.ipv6_cidr_var.get()
            
            # 构造网络地址
            network_str = f"{ipv6}/{cidr}"
            
            # 获取IPv6信息
            ipv6_info = get_ip_info(network_str)
            
            # 分组显示结果
            # 1. 基本信息
            self.ipv6_info_tree.insert("", tk.END, values=("IP地址", ipv6_info.get("ip_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("IP版本", ipv6_info.get("version", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("CIDR前缀", ipv6_info.get("cidr", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("前缀长度", ipv6_info.get("prefix_length", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("网络地址", ipv6_info.get("network_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("广播地址", ipv6_info.get("broadcast_address", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("子网掩码", ipv6_info.get("subnet_mask", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("第一个可用主机", ipv6_info.get("first_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("最后一个可用主机", ipv6_info.get("last_host", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("总主机数", ipv6_info.get("total_hosts", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("可用主机数", ipv6_info.get("usable_hosts", "")))
            
            # 2. 地址格式
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址格式", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("压缩格式", ipv6_info.get("compressed", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("展开格式", ipv6_info.get("exploded", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("反向DNS格式", ipv6_info.get("reverse_dns", "")))
            
            # 3. 地址属性
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("地址属性", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("地址类别", ipv6_info.get("class", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("是否全局可路由", "是" if ipv6_info.get("is_global") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否私有地址", "是" if ipv6_info.get("is_private") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否链路本地", "是" if ipv6_info.get("is_link_local") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否回环地址", "是" if ipv6_info.get("is_loopback") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否组播地址", "是" if ipv6_info.get("is_multicast") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否未指定地址", "是" if ipv6_info.get("is_unspecified") else "否"))
            self.ipv6_info_tree.insert("", tk.END, values=("是否保留地址", "是" if ipv6_info.get("is_reserved") else "否"))
            
            # 4. 数值表示
            self.ipv6_info_tree.insert("", tk.END, values=())
            self.ipv6_info_tree.insert("", tk.END, values=("数值表示", ""))
            self.ipv6_info_tree.insert("", tk.END, values=("二进制表示", ipv6_info.get("binary", "")))
            self.ipv6_info_tree.insert("", tk.END, values=("十六进制表示", ipv6_info.get("hexadecimal", "")))
            
            # 显示整数值（如果有）
            if "integer" in ipv6_info:
                self.ipv6_info_tree.insert("", tk.END, values=("整数值", ipv6_info["integer"]))
            elif "ip_int" in ipv6_info:
                self.ipv6_info_tree.insert("", tk.END, values=("整数值", ipv6_info["ip_int"]))
            
        except ValueError as e:
            self.show_info("错误", f"查询失败: {str(e)}")
        except Exception as e:
            self.show_info("错误", f"操作失败: {str(e)}")
