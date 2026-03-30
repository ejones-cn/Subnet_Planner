#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地址管理（IPAM）模块 - SQLite版本
负责IP地址的分配、跟踪、状态管理和历史记录
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta




import ipaddress


class IPAMSQLite:
    """IP地址管理类 - SQLite版本"""
    
    def __init__(self, db_file: str = "ipam_data.db"):
        """初始化IPAM
        
        Args:
            db_file: 数据库文件路径
        """
        self.db_file: str = db_file
        self.backup_dir: str = os.path.join(os.path.dirname(db_file), "ipam_backups")
        # 创建备份目录
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        self.init_db()
    
    def init_db(self) -> None:
        """初始化数据库"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 创建networks表
        _ = cursor.execute('''
        CREATE TABLE IF NOT EXISTS networks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_address TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
        ''')
        
        # 创建ip_addresses表
        _ = cursor.execute('''
        CREATE TABLE IF NOT EXISTS ip_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_id INTEGER NOT NULL,
            ip_address TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            hostname TEXT,
            description TEXT,
            allocated_at TEXT,
            allocated_by TEXT,
            expiry_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (network_id) REFERENCES networks(id)
        )
        ''')
        
        # 创建allocation_history表
        _ = cursor.execute('''
        CREATE TABLE IF NOT EXISTS allocation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_id INTEGER NOT NULL,
            ip_address TEXT NOT NULL,
            action TEXT NOT NULL,
            hostname TEXT,
            description TEXT,
            performed_by TEXT,
            performed_at TEXT NOT NULL,
            FOREIGN KEY (network_id) REFERENCES networks(id)
        )
        ''')
        
        # 创建backups表
        _ = cursor.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_name TEXT NOT NULL,
            backup_path TEXT NOT NULL,
            backup_type TEXT NOT NULL,
            backup_time TEXT NOT NULL,
            network_count INTEGER NOT NULL,
            ip_count INTEGER NOT NULL
        )
        ''')
        
        # 创建索引
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_network_id ON ip_addresses(network_id)')
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_status ON ip_addresses(status)')
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_ip_address ON ip_addresses(ip_address)')
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_expiry_date ON ip_addresses(expiry_date)')
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocation_history_network_id ON allocation_history(network_id)')
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocation_history_action ON allocation_history(action)')
        _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocation_history_performed_at ON allocation_history(performed_at)')
        
        conn.commit()
        conn.close()
    
    def migrate_from_json(self, json_file: str = "ipam_data.json") -> tuple[bool, str]:
        """从JSON文件迁移数据
        
        Args:
            json_file: JSON数据文件路径
        
        Returns:
            tuple[bool, str]: (是否迁移成功, 错误信息)
        """
        if not os.path.exists(json_file):
            return False, "JSON文件不存在"
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            return False, f"读取JSON文件失败: {str(e)}"
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            # 开始事务
            _ = conn.execute('BEGIN TRANSACTION')
            
            # 迁移networks
            networks_map: dict[str, int] = {}  # 用于映射网络地址到ID
            data_dict = data if isinstance(data, dict) else {}
            networks_data = data_dict.get('networks', {})
            if isinstance(networks_data, dict):
                for net_str, net_data in networks_data.items():
                    if isinstance(net_str, str) and isinstance(net_data, dict):
                        network_created_at = net_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        if isinstance(network_created_at, str):
                            _ = cursor.execute('''
                            INSERT OR IGNORE INTO networks (network_address, description, created_at, updated_at)
                            VALUES (?, ?, ?, ?)
                            ''', (net_str, net_data.get('description', ''), network_created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 获取所有网络的ID
            _ = cursor.execute('SELECT id, network_address FROM networks')
            rows = cursor.fetchall()
            for row in rows:
                if isinstance(row, tuple) and len(row) >= 2:
                    networks_map[str(row[1])] = int(row[0])
            
            # 迁移ip_addresses
            if isinstance(networks_data, dict):
                for net_str, net_data in networks_data.items():
                    if isinstance(net_str, str) and isinstance(net_data, dict):
                        network_id = networks_map.get(net_str)
                        if not network_id:
                            continue
                        
                        ip_addresses_data = net_data.get('ip_addresses', {})
                        if isinstance(ip_addresses_data, dict):
                            for ip_str, ip_data in ip_addresses_data.items():
                                if isinstance(ip_str, str) and isinstance(ip_data, dict):
                                    ip_created_at = ip_data.get('allocated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                                    if isinstance(ip_created_at, str):
                                        _ = cursor.execute('''
                                        INSERT OR IGNORE INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                                        allocated_at, allocated_by, expiry_date, created_at, updated_at)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        ''', (network_id, ip_str, ip_data.get('status', 'available'), 
                                              ip_data.get('hostname', ''), ip_data.get('description', ''),
                                              ip_data.get('allocated_at'), ip_data.get('allocated_by'),
                                              ip_data.get('expiry_date'), ip_created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 迁移allocation_history
            allocation_history_data = data_dict.get('allocation_history', [])
            if isinstance(allocation_history_data, list):
                for history_item in allocation_history_data:
                    if isinstance(history_item, dict):
                        network = history_item.get('network')
                        if isinstance(network, str):
                            history_network_id = networks_map.get(network)
                            if history_network_id:
                                _ = cursor.execute('''
                                INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                                performed_by, performed_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                ''', (history_network_id, history_item.get('ip_address'), history_item.get('action'),
                                      history_item.get('hostname'), history_item.get('description'),
                                      history_item.get('performed_by'), history_item.get('timestamp')))
            
            # 提交事务
            conn.commit()
            conn.close()
            return True, "数据迁移成功"
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"数据迁移失败: {str(e)}"
    
    def get_most_specific_network(self, ip_address: str) -> dict[str, str | int] | None:
        """获取IP地址最具体的归属网络
        
        Args:
            ip_address: IP地址
            
        Returns:
            dict: 网络信息，或None
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        _ = cursor.execute('SELECT id, network_address, description, created_at, updated_at FROM networks')
        network_rows = cursor.fetchall()
        
        conn.close()
        
        target_ip = ipaddress.ip_address(ip_address)
        most_specific_network: dict[str, str | int] | None = None
        max_prefix_len = 0
        
        for network_row in network_rows:
            try:
                if isinstance(network_row, tuple) and len(network_row) >= 5:
                    network_id: int = int(network_row[0])
                    network_address: str = str(network_row[1])
                    description: str = str(network_row[2]) if network_row[2] else ''
                    created_at: str = str(network_row[3]) if network_row[3] else ''
                    updated_at: str = str(network_row[4]) if network_row[4] else ''
                    network_obj = ipaddress.ip_network(network_address)
                    if target_ip in network_obj:
                        if network_obj.prefixlen > max_prefix_len:
                            max_prefix_len = network_obj.prefixlen
                            most_specific_network = {
                                'id': network_id,
                                'network_address': network_address,
                                'description': description,
                                'created_at': created_at,
                                'updated_at': updated_at
                            }
            except Exception:
                pass
        
        return most_specific_network
    
    def add_network(self, network_str: str, description: str = "") -> tuple[bool, str]:
        """添加网络
        
        Args:
            network_str: 网络地址（CIDR格式）
            description: 网络描述
        
        Returns:
            tuple[bool, str]: (是否添加成功, 错误信息)
        """
        try:
            # 验证网络格式
            if not network_str:
                return False, "网络地址不能为空"
            
            try:
                ip_network = ipaddress.ip_network(network_str, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return False, f"网络格式错误: {str(e)}"
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查网络是否已存在
            _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
            if cursor.fetchone():
                conn.close()
                return False, "网络已存在"
            
            # 添加网络
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _ = cursor.execute('''
            INSERT INTO networks (network_address, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ''', (network_str, description, created_at, created_at))
            
            network_id = cursor.lastrowid
            
            # 检查是否有IP地址应该归属到这个新网络
            _ = cursor.execute('SELECT id, network_id, ip_address FROM ip_addresses')
            ips = cursor.fetchall()
            
            for ip_item in ips:
                try:
                    if isinstance(ip_item, tuple) and len(ip_item) >= 3:
                        ip_id: int = int(ip_item[0])
                        current_network_id: int = int(ip_item[1])
                        ip_address: str = str(ip_item[2])
                        ip_obj = ipaddress.ip_address(ip_address)
                        if ip_obj in ip_network:
                            # 检查是否是更具体的网络
                            _ = cursor.execute('SELECT network_address FROM networks WHERE id = ?', (current_network_id,))
                            current_network_row = cursor.fetchone()
                            if current_network_row and isinstance(current_network_row, tuple) and len(current_network_row) >= 1:
                                current_network_address: str = str(current_network_row[0])
                                current_network_obj = ipaddress.ip_network(current_network_address)
                                if ip_network.prefixlen > current_network_obj.prefixlen:
                                    # 更新归属关系
                                    _ = cursor.execute('UPDATE ip_addresses SET network_id = ? WHERE id = ?', (network_id, ip_id))
                except Exception:
                    pass
            
            conn.commit()
            conn.close()
            return True, "网络添加成功"
        except Exception as e:
            return False, f"添加网络失败: {str(e)}"
    
    def allocate_ip(self, network_str: str, ip_address: str, hostname: str, description: str = "", expiry_date: str | None = None) -> tuple[bool, str]:
        """分配IP地址
        
        Args:
            network_str: 网络地址（CIDR格式）
            ip_address: 要分配的IP地址
            hostname: 主机名
            description: 描述
            expiry_date: 过期日期（ISO格式）
        
        Returns:
            tuple[bool, str]: (是否分配成功, 错误信息)
        """
        try:
            # 验证参数
            if not network_str:
                return False, "网络地址不能为空"
            if not ip_address:
                return False, "IP地址不能为空"
            if not hostname and not description:
                return False, "主机名和描述不能同时为空"
            
            # 验证IP地址格式
            try:
                _ = ipaddress.ip_address(ip_address)
            except ValueError as e:
                return False, f"IP地址格式错误: {str(e)}"
            
            # 找到最具体的网络
            most_specific_network = self.get_most_specific_network(ip_address)
            if not most_specific_network:
                # 如果没有找到合适的网络，使用指定的网络
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
                network_row = cursor.fetchone()
                if not network_row or not isinstance(network_row, tuple) or len(network_row) < 1:
                    conn.close()
                    return False, "网络不存在"
                network_id = int(network_row[0])
                conn.close()
            else:
                network_id = int(most_specific_network['id'])
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            try:
                # 开始事务
                _ = conn.execute('BEGIN EXCLUSIVE')
                
                # 检查IP地址是否已存在
                _ = cursor.execute('SELECT id, status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                ip_row = cursor.fetchone()
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                success_result: tuple[bool, str] | None = None
                if ip_row and isinstance(ip_row, tuple) and len(ip_row) >= 2:
                    # IP地址已存在
                    ip_id: int = int(ip_row[0])
                    status: str = str(ip_row[1])
                    if status in ['available', 'reserved']:
                        # IP地址可用或已保留，可以分配
                        _ = cursor.execute('''
                        UPDATE ip_addresses SET status = ?, hostname = ?, description = ?, 
                        allocated_at = ?, allocated_by = ?, expiry_date = ?, updated_at = ?
                        WHERE id = ?
                        ''', ('allocated', hostname, description, now, 'admin', expiry_date, now, ip_id))
                    else:
                        # IP地址已被分配
                        success_result = (False, "IP地址已被分配")
                else:
                    # 新的IP地址，插入记录
                    _ = cursor.execute('''
                    INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                    allocated_at, allocated_by, expiry_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, 'allocated', hostname, description,
                          now, 'admin', expiry_date, now, now))
                
                if success_result is None:
                    # 记录分配历史
                    _ = cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                    performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, 'allocate', hostname, description, 'admin', now))
                    conn.commit()
                    success_result = (True, "IP地址分配成功")
                else:
                    conn.rollback()
                
                return success_result
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        except Exception as e:
            return False, f"分配IP地址失败: {str(e)}"
    
    def get_network_ips(self, network_str: str) -> list[dict[str, str | int | None]]:
        """获取网络及其所有子网络的IP地址
        
        Args:
            network_str: 网络地址（CIDR格式）
        
        Returns:
            list[dict[str, str | int | None]]: IP地址列表
        """
        try:
            ip_network = ipaddress.ip_network(network_str, strict=False)
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取所有IP地址
            _ = cursor.execute('SELECT id, network_id, ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at FROM ip_addresses')
            ips = cursor.fetchall()
            
            conn.close()
            
            # 过滤出属于目标网络的IP地址
            relevant_ips: list[dict[str, str | int | None]] = []
            for ip_item in ips:
                try:
                    if isinstance(ip_item, tuple) and len(ip_item) >= 11:
                        ip_id: int = int(ip_item[0])
                        network_id: int = int(ip_item[1])
                        ip_address: str = str(ip_item[2])
                        status: str = str(ip_item[3])
                        hostname: str | None = str(ip_item[4]) if ip_item[4] else None
                        description: str | None = str(ip_item[5]) if ip_item[5] else None
                        allocated_at: str | None = str(ip_item[6]) if ip_item[6] else None
                        allocated_by: str | None = str(ip_item[7]) if ip_item[7] else None
                        expiry_date: str | None = str(ip_item[8]) if ip_item[8] else None
                        created_at: str | None = str(ip_item[9]) if ip_item[9] else None
                        updated_at: str | None = str(ip_item[10]) if ip_item[10] else None
                        ip_obj = ipaddress.ip_address(ip_address)
                        if ip_obj in ip_network:
                            relevant_ips.append({
                                'id': ip_id,
                                'network_id': network_id,
                                'ip_address': ip_address,
                                'status': status,
                                'hostname': hostname,
                                'description': description,
                                'allocated_at': allocated_at,
                                'allocated_by': allocated_by,
                                'expiry_date': expiry_date,
                                'created_at': created_at,
                                'updated_at': updated_at
                            })
                except Exception:
                    pass
            
            return relevant_ips
        except Exception:
            return []
    
    def get_all_networks(self) -> list[dict[str, str | int]]:
        """获取所有网络
        
        Returns:
            list[dict[str, str | int]]: 网络列表
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        _ = cursor.execute('SELECT id, network_address, description, created_at, updated_at FROM networks')
        network_rows = cursor.fetchall()
        
        # 一次性获取所有IP地址，避免多次数据库查询
        _ = cursor.execute('SELECT ip_address FROM ip_addresses')
        all_ips = cursor.fetchall()
        
        conn.close()
        
        # 预处理IP地址，避免重复创建ipaddress对象
        ip_objects: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
        for ip_item in all_ips:
            try:
                if isinstance(ip_item, tuple) and len(ip_item) >= 1:
                    ip_address: str = str(ip_item[0])
                    ip_obj = ipaddress.ip_address(ip_address)
                    ip_objects.append(ip_obj)
            except Exception:
                pass
        
        network_list: list[dict[str, str | int]] = []
        for network_item in network_rows:
            # 计算网络及其子网络的IP数量
            if isinstance(network_item, tuple) and len(network_item) >= 5:
                network_id: int = int(network_item[0])
                network_address: str = str(network_item[1])
                description: str = str(network_item[2]) if network_item[2] else ''
                created_at: str = str(network_item[3]) if network_item[3] else ''
                updated_at: str = str(network_item[4]) if network_item[4] else ''
                ip_count: int = self.get_network_ip_count(network_address, ip_objects)
                
                network_list.append({
                    'id': network_id,
                    'network': network_address,
                    'description': description,
                    'created_at': created_at,
                    'updated_at': updated_at,
                    'ip_count': ip_count
                })
        
        return network_list
    
    def get_network_ip_count(self, network_address: str, ip_objects: list[ipaddress.IPv4Address | ipaddress.IPv6Address] | None = None) -> int:
        """计算网络及其所有子网络的IP数量
        
        Args:
            network_address: 网络地址（CIDR格式）
            ip_objects: 预处理的IP地址对象列表，避免重复计算
        
        Returns:
            int: IP地址数量
        """
        try:
            ip_network = ipaddress.ip_network(network_address, strict=False)
            
            # 计算属于目标网络的IP地址数量
            count: int = 0
            
            if ip_objects:
                # 使用预处理的IP对象列表
                for ip_obj in ip_objects:
                    if ip_obj in ip_network:
                        count += 1
            else:
                # 回退到原始方法
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                # 获取所有IP地址
                _ = cursor.execute('SELECT ip_address FROM ip_addresses')
                ips = cursor.fetchall()
                
                conn.close()
                
                for ip_item in ips:
                    try:
                        if isinstance(ip_item, tuple) and len(ip_item) >= 1:
                            ip_address_str: str = str(ip_item[0])
                            ip_obj = ipaddress.ip_address(ip_address_str)
                            if ip_obj in ip_network:
                                count += 1
                    except Exception:
                        pass
            
            return count
        except Exception:
            return 0
    
    def release_ip(self, ip_address: str) -> tuple[bool, str]:
        """释放IP地址
        
        Args:
            ip_address: 要释放的IP地址
        
        Returns:
            tuple[bool, str]: (是否释放成功, 错误信息)
        """
        try:
            # 验证参数
            if not ip_address:
                return False, "IP地址不能为空"
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查找所有该IP地址的记录
            _ = cursor.execute('SELECT id, network_id, status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_rows = cursor.fetchall()
            
            if not ip_rows:
                conn.close()
                return False, "IP地址不存在"
            
            # 检查是否有可释放的IP地址
            allocatable_rows: list[tuple[int, int, str]] = [row for row in ip_rows if isinstance(row, tuple) and len(row) >= 3 and str(row[2]) != 'available']
            if not allocatable_rows:
                conn.close()
                return False, "IP地址未被分配或已被释放"
            
            # 释放所有未释放的IP地址记录
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            released_count: int = 0
            
            for ip_row_item in allocatable_rows:
                if isinstance(ip_row_item, tuple) and len(ip_row_item) >= 3:
                    ip_id: int = int(ip_row_item[0])
                    network_id: int = int(ip_row_item[1])
                    
                    # 释放IP地址
                    _ = cursor.execute('UPDATE ip_addresses SET status = ?, updated_at = ? WHERE id = ?', ('available', now, ip_id))
                    
                    # 记录释放历史
                    _ = cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, 'release', 'admin', now))
                    
                    released_count += 1
            
            conn.commit()
            conn.close()
            return True, f"成功释放 {released_count} 个IP地址记录"
        except Exception as e:
            return False, f"释放IP地址失败: {str(e)}"
    
    def delete_ip_by_id(self, ip_id: int) -> tuple[bool, str]:
        """根据ID删除IP地址记录
        
        Args:
            ip_id: IP地址记录ID
            
        Returns:
            Tuple[bool, str]: (是否删除成功, 错误信息)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取IP地址信息用于历史记录
            _ = cursor.execute('SELECT ip_address, network_id FROM ip_addresses WHERE id = ?', (ip_id,))
            ip_row = cursor.fetchone()
            if not ip_row or not isinstance(ip_row, tuple) or len(ip_row) < 2:
                conn.close()
                return False, "IP地址记录不存在"
            
            ip_address: str = str(ip_row[0])
            network_id: int = int(ip_row[1])
            
            # 删除IP地址记录
            _ = cursor.execute('DELETE FROM ip_addresses WHERE id = ?', (ip_id,))
            
            # 记录删除历史
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _ = cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'delete_conflict', 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址记录删除成功"
        except Exception as e:
            return False, f"删除IP地址记录失败: {str(e)}"
    
    def get_ip_info(self, ip_address: str) -> dict[str, str | int] | None:
        """获取IP地址信息
        
        Args:
            ip_address: IP地址
        
        Returns:
            dict[str, str | int] or None: IP地址信息，包含hostname, description等字段，失败返回None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查询IP地址信息
            _ = cursor.execute('SELECT hostname, description, network_id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            
            if ip_row and isinstance(ip_row, tuple) and len(ip_row) >= 3:
                hostname: str = str(ip_row[0]) if ip_row[0] else ''
                description: str = str(ip_row[1]) if ip_row[1] else ''
                network_id: int = int(ip_row[2])
                return {
                    'hostname': hostname,
                    'description': description,
                    'network_id': network_id
                }
            return None
        except Exception as e:
            print(f"获取IP地址信息失败: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    def update_ip_info(self, ip_address: str, hostname: str, description: str) -> tuple[bool, str]:
        """更新IP地址信息
        
        Args:
            ip_address: IP地址
            hostname: 新的主机名
            description: 新的描述
        
        Returns:
            tuple[bool, str]: (是否更新成功, 错误信息)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查IP地址是否存在
            _ = cursor.execute('SELECT id, network_id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            if not ip_row or not isinstance(ip_row, tuple) or len(ip_row) < 2:
                conn.close()
                return False, "IP地址不存在"
            
            ip_id: int = int(ip_row[0])
            network_id: int = int(ip_row[1])
            
            # 更新IP地址信息
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _ = cursor.execute('''
            UPDATE ip_addresses 
            SET hostname = ?, description = ?, updated_at = ?
            WHERE id = ?
            ''', (hostname, description, now, ip_id))
            
            # 记录更新历史
            _ = cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
            performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'update', hostname, description, 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址信息更新成功"
        except Exception as e:
            return False, f"更新IP地址信息失败: {str(e)}"

    def update_ip_expiry(self, ip_address: str, expiry_date: str | None) -> tuple[bool, str]:
        """更新IP地址过期日期
        
        Args:
            ip_address: IP地址
            expiry_date: 过期日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS，传入None则清除过期日期）
            
        Returns:
            tuple[bool, str]: (是否更新成功, 错误信息)
        """
        # 验证日期格式
        if expiry_date is not None:
            validated_date = self._validate_expiry_date(expiry_date)
            if validated_date is None:
                return False, "过期日期格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 格式"
            expiry_date = validated_date
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 检查IP地址是否存在
                _ = cursor.execute('SELECT id, network_id, hostname, description FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                ip_row = cursor.fetchone()
                if not ip_row or not isinstance(ip_row, tuple) or len(ip_row) < 4:
                    return False, "IP地址不存在"
                
                ip_id: int = int(ip_row[0])
                network_id: int = int(ip_row[1])
                hostname: str = str(ip_row[2]) if ip_row[2] else ''
                description: str = str(ip_row[3]) if ip_row[3] else ''
                
                # 更新IP地址过期日期
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                _ = cursor.execute('''
                UPDATE ip_addresses 
                SET expiry_date = ?, updated_at = ?
                WHERE id = ?
                ''', (expiry_date, now, ip_id))
                
                # 记录更新历史
                _ = cursor.execute('''
                INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                performed_by, performed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (network_id, ip_address, 'update', hostname, description, 'admin', now))
                
                conn.commit()
                return True, "IP地址过期日期更新成功"
        except Exception as e:
            return False, f"更新IP地址过期日期失败: {str(e)}"
    
    def batch_update_ip_expiry(self, ip_addresses: list[str], expiry_date: str | None) -> tuple[bool, str, int]:
        """批量更新IP地址过期日期
        
        Args:
            ip_addresses: IP地址列表
            expiry_date: 过期日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS，传入None则清除过期日期）
            
        Returns:
            Tuple: (bool, str, int) - (是否更新成功, 错误信息, 更新的IP数量)
        """
        # 验证日期格式
        if expiry_date is not None:
            validated_date = self._validate_expiry_date(expiry_date)
            if validated_date is None:
                return False, "过期日期格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 格式", 0
            expiry_date = validated_date
        
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                updated_count = 0
                
                for ip_address in ip_addresses:
                    # 检查IP地址是否存在
                    _ = cursor.execute('SELECT id, network_id, hostname, description FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                    ip_row = cursor.fetchone()
                    if not ip_row or not isinstance(ip_row, tuple) or len(ip_row) < 4:
                        continue
                    
                    ip_id: int = int(ip_row[0])
                    network_id: int = int(ip_row[1])
                    hostname: str = str(ip_row[2]) if ip_row[2] else ''
                    description: str = str(ip_row[3]) if ip_row[3] else ''
                    
                    # 更新IP地址过期日期
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    _ = cursor.execute('''
                    UPDATE ip_addresses 
                    SET expiry_date = ?, updated_at = ?
                    WHERE id = ?
                    ''', (expiry_date, now, ip_id))
                    
                    # 记录更新历史
                    _ = cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                    performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, 'batch_update', hostname, description, 'admin', now))
                    
                    updated_count += 1
                
                conn.commit()
                
                if updated_count > 0:
                    return True, f"成功更新 {updated_count} 个IP地址的过期日期", updated_count
                else:
                    return True, "没有IP地址被更新", 0
        except Exception as e:
            return False, f"批量更新IP地址过期日期失败: {str(e)}", 0
    
    def _validate_expiry_date(self, expiry_date: str | None) -> str | None:
        """验证并标准化过期日期格式
        
        Args:
            expiry_date: 过期日期字符串
            
        Returns:
            str | None: 标准化后的日期字符串（YYYY-MM-DD HH:MM:SS），验证失败返回None
        """
        if not expiry_date:
            return None
        
        expiry_date = expiry_date.strip()
        
        # 支持的日期格式列表
        date_formats = [
            "%Y-%m-%d %H:%M:%S",    # 2023-12-31 23:59:59
            "%Y-%m-%dT%H:%M:%S",    # 2023-12-31T23:59:59
            "%Y-%m-%d",             # 2023-12-31
            "%Y/%m/%d %H:%M:%S",    # 2023/12/31 23:59:59
            "%Y/%m/%d",             # 2023/12/31
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(expiry_date, fmt)
                # 如果只有日期部分（格式为%Y-%m-%d或%Y/%m/%d），添加时间部分为23:59:59
                if fmt in ["%Y-%m-%d", "%Y/%m/%d"]:
                    return dt.strftime("%Y-%m-%d") + " 23:59:59"
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
        
        return None

    def cleanup_available_ips(self) -> tuple[bool, str]:
        """清理所有可用状态的IP地址
        
        Returns:
            tuple[bool, str]: (是否清理成功, 错误信息)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查找所有可用状态的IP地址
            _ = cursor.execute('SELECT id, network_id, ip_address FROM ip_addresses WHERE status = ?', ('available',))
            available_ips = cursor.fetchall()
            
            if not available_ips:
                conn.close()
                return True, "没有可用状态的IP地址需要清理"
            
            # 记录清理历史
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for ip_item in available_ips:
                if isinstance(ip_item, tuple) and len(ip_item) >= 3:
                    network_id: int = int(ip_item[1])
                    ip_address: str = str(ip_item[2])
                    # 记录清理历史
                    _ = cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, 'cleanup', 'admin', now))
            
            # 删除可用状态的IP地址
            _ = cursor.execute('DELETE FROM ip_addresses WHERE status = ?', ('available',))
            
            conn.commit()
            conn.close()
            return True, f"成功清理 {len(available_ips)} 个可用状态的IP地址"
        except Exception as e:
            return False, f"清理可用IP地址失败: {str(e)}"
    
    def get_ip_status(self, ip_address: str) -> str:
        """获取IP地址状态
        
        Args:
            ip_address: IP地址
        
        Returns:
            str: IP地址状态（allocated, reserved, available）
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            _ = cursor.execute('SELECT status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result and isinstance(result, tuple) and len(result) >= 1:
                status: str = str(result[0])
                return status
            return 'available'
        except Exception:
            return 'available'
    
    def get_expired_ips(self) -> list[dict[str, str | int | None]]:
        """获取所有过期的IP地址
        
        Returns:
            list[dict[str, str | int | None]]: 过期IP地址列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取所有过期的IP地址，包括allocated和reserved状态
            _ = cursor.execute('''
            SELECT id, network_id, ip_address, status, hostname, description, allocated_at, expiry_date 
            FROM ip_addresses 
            WHERE expiry_date < ? AND status IN ('allocated', 'reserved')
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            
            expired_ips: list[dict[str, str | int | None]] = []
            for row in cursor.fetchall():
                if isinstance(row, tuple) and len(row) >= 8:
                    ip_id: int = int(row[0])
                    network_id: int = int(row[1])
                    ip_address: str = str(row[2])
                    status: str = str(row[3])
                    hostname: str | None = str(row[4]) if row[4] else None
                    description: str | None = str(row[5]) if row[5] else None
                    allocated_at: str | None = str(row[6]) if row[6] else None
                    expiry_date: str | None = str(row[7]) if row[7] else None
                    expired_ips.append({
                        'id': ip_id,
                        'network_id': network_id,
                        'ip_address': ip_address,
                        'status': status,
                        'hostname': hostname,
                        'description': description,
                        'allocated_at': allocated_at,
                        'expiry_date': expiry_date
                    })
            
            conn.close()
            return expired_ips
        except Exception:
            return []
    
    def auto_release_expired_ips(self) -> tuple[bool, str, int]:
        """自动释放过期的IP地址
        
        Returns:
            tuple[bool, str, int]: (是否成功, 错误信息, 释放的IP数量)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取过期的IP地址
            expired_ips = self.get_expired_ips()
            released_count = 0
            
            for ip in expired_ips:
                # 释放IP地址
                _ = cursor.execute('UPDATE ip_addresses SET status = ?, updated_at = ? WHERE id = ?', 
                             ('available', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip['id']))
                
                # 记录释放历史
                _ = cursor.execute('''
                INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                performed_by, performed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (ip['network_id'], ip['ip_address'], 'auto_release', ip['hostname'], 
                      ip['description'], 'system', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                released_count += 1
            
            conn.commit()
            conn.close()
            
            if released_count > 0:
                return True, f"成功释放 {released_count} 个过期IP地址", released_count
            else:
                return True, "没有过期IP地址需要释放", 0
        except Exception as e:
            return False, f"自动释放过期IP地址失败: {str(e)}", 0
    
    def get_expiring_ips(self, days_ahead: int = 7) -> list[dict[str, str | int | None]]:
        """获取即将过期的IP地址
        
        Args:
            days_ahead: 提前多少天提醒
        
        Returns:
            list[dict[str, str | int | None]]: 即将过期的IP地址列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 计算日期范围
            now = datetime.now()
            future_date = now + timedelta(days=days_ahead)
            
            # 获取即将过期的IP地址
            _ = cursor.execute('''
            SELECT id, network_id, ip_address, status, hostname, description, allocated_at, expiry_date 
            FROM ip_addresses 
            WHERE expiry_date BETWEEN ? AND ? AND status IN ('allocated', 'reserved')
            ''', (now.strftime("%Y-%m-%d %H:%M:%S"), future_date.strftime("%Y-%m-%d %H:%M:%S")))
            
            expiring_ips: list[dict[str, str | int | None]] = []
            for row in cursor.fetchall():
                if isinstance(row, tuple) and len(row) >= 8:
                    ip_id: int = int(row[0])
                    network_id: int = int(row[1])
                    ip_address: str = str(row[2])
                    status: str = str(row[3])
                    hostname: str | None = str(row[4]) if row[4] else None
                    description: str | None = str(row[5]) if row[5] else None
                    allocated_at: str | None = str(row[6]) if row[6] else None
                    expiry_date: str | None = str(row[7]) if row[7] else None
                    expiring_ips.append({
                        'id': ip_id,
                        'network_id': network_id,
                        'ip_address': ip_address,
                        'status': status,
                        'hostname': hostname,
                        'description': description,
                        'allocated_at': allocated_at,
                        'expiry_date': expiry_date
                    })
            
            conn.close()
            return expiring_ips
        except Exception:
            return []
    
    def reserve_ip(self, network_str: str, ip_address: str, description: str = "") -> tuple[bool, str]:
        """保留IP地址
        
        Args:
            network_str: 网络地址（CIDR格式）
            ip_address: 要保留的IP地址
            description: 描述
        
        Returns:
            tuple[bool, str]: (是否保留成功, 错误信息)
        """
        try:
            # 验证参数
            if not network_str:
                return False, "网络地址不能为空"
            if not ip_address:
                return False, "IP地址不能为空"
            
            # 验证IP地址格式
            try:
                _ = ipaddress.ip_address(ip_address)
            except ValueError as e:
                return False, f"IP地址格式错误: {str(e)}"
            
            # 找到最具体的网络
            most_specific_network = self.get_most_specific_network(ip_address)
            if not most_specific_network:
                # 如果没有找到合适的网络，使用指定的网络
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
                network_row = cursor.fetchone()
                if not network_row or not isinstance(network_row, tuple) or len(network_row) < 1:
                    conn.close()
                    return False, "网络不存在"
                network_id = int(network_row[0])
                conn.close()
            else:
                network_id = int(most_specific_network['id'])
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查IP地址是否已存在
            _ = cursor.execute('SELECT id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if ip_row and isinstance(ip_row, tuple) and len(ip_row) >= 1:
                # 更新IP地址状态
                ip_id: int = int(ip_row[0])
                _ = cursor.execute('UPDATE ip_addresses SET status = ?, description = ?, updated_at = ? WHERE id = ?', 
                             ('reserved', description, now, ip_id))
            else:
                # 创建新的IP地址记录
                _ = cursor.execute('''
                INSERT INTO ip_addresses (network_id, ip_address, status, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (network_id, ip_address, 'reserved', description, now, now))
            
            # 记录保留历史
            _ = cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, description, performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'reserve', description, 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址保留成功"
        except Exception as e:
            return False, f"保留IP地址失败: {str(e)}"

    def update_network_description(self, network_str: str, description: str) -> tuple[bool, str]:
        """更新网络描述
        
        Args:
            network_str: 网络地址（CIDR格式）
            description: 新的描述信息
        
        Returns:
            tuple[bool, str]: (是否更新成功, 错误信息)
        """
        try:
            if not network_str:
                return False, "网络地址不能为空"
            
            try:
                ip_network = ipaddress.ip_network(network_str, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return False, f"网络格式错误: {str(e)}"
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 检查网络是否存在
                _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
                network_row = cursor.fetchone()
                if not network_row or not isinstance(network_row, tuple) or len(network_row) < 1:
                    return False, "网络不存在"
                
                # 更新网络描述
                _ = cursor.execute('UPDATE networks SET description = ?, updated_at = datetime("now") WHERE id = ?', 
                             (description, int(network_row[0])))
                
                conn.commit()
            return True, "网络描述更新成功"
        except Exception as e:
            return False, f"更新网络描述失败: {str(e)}"
    
    def update_network(self, old_network: str, new_network: str) -> tuple[bool, str]:
        """更新网络地址
        
        Args:
            old_network: 旧的网络地址（CIDR格式）
            new_network: 新的网络地址（CIDR格式）
        
        Returns:
            tuple[bool, str]: (是否更新成功, 错误信息)
        """
        try:
            if not old_network or not new_network:
                return False, "网络地址不能为空"
            
            # 验证旧网络格式
            try:
                old_ip_network = ipaddress.ip_network(old_network, strict=False)
                old_network_str = str(old_ip_network)
            except ValueError as e:
                return False, f"旧网络格式错误: {str(e)}"
            
            # 验证新网络格式
            try:
                new_ip_network = ipaddress.ip_network(new_network, strict=False)
                new_network_str = str(new_ip_network)
            except ValueError as e:
                return False, f"新网络格式错误: {str(e)}"
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 检查旧网络是否存在
                _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (old_network_str,))
                network_row = cursor.fetchone()
                if not network_row or not isinstance(network_row, tuple) or len(network_row) < 1:
                    return False, "旧网络不存在"
                
                # 检查新网络是否已存在
                _ = cursor.execute('SELECT id FROM networks WHERE network_address = ? AND id != ?', (new_network_str, int(network_row[0])))
                existing_row = cursor.fetchone()
                if existing_row:
                    return False, "新网络地址已存在"
                
                # 更新网络地址
                _ = cursor.execute('UPDATE networks SET network_address = ?, updated_at = datetime("now") WHERE id = ?', 
                             (new_network_str, int(network_row[0])))
                
                conn.commit()
            return True, "网络地址更新成功"
        except Exception as e:
            return False, f"更新网络地址失败: {str(e)}"

    def remove_network(self, network_str: str) -> tuple[bool, str]:
        """移除网络
        
        Args:
            network_str: 网络地址（CIDR格式）
        
        Returns:
            tuple[bool, str]: (是否移除成功, 错误信息)
        """
        try:
            if not network_str:
                return False, "网络地址不能为空"
            
            try:
                ip_network = ipaddress.ip_network(network_str, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return False, f"网络格式错误: {str(e)}"
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查网络是否存在
            _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
            network_row = cursor.fetchone()
            if not network_row or not isinstance(network_row, tuple) or len(network_row) < 1:
                conn.close()
                return False, "网络不存在"
            
            network_id = int(network_row[0])
            
            # 检查网络是否有IP地址
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE network_id = ?', (network_id,))
            ip_count_result = cursor.fetchone()
            ip_count = int(ip_count_result[0]) if ip_count_result and isinstance(ip_count_result, tuple) and len(ip_count_result) >= 1 else 0
            if ip_count > 0:
                conn.close()
                return False, f"网络中存在 {ip_count} 个IP地址，请先释放或保留这些IP地址"
            
            # 移除网络
            _ = cursor.execute('DELETE FROM networks WHERE id = ?', (network_id,))
            
            conn.commit()
            conn.close()
            return True, "网络移除成功"
        except Exception as e:
            return False, f"移除网络失败: {str(e)}"
    
    def get_overall_stats(self) -> dict[str, int]:
        """获取整体统计信息
        
        Returns:
            dict[str, int]: 整体统计信息
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取网络总数
            _ = cursor.execute('SELECT COUNT(*) FROM networks')
            total_networks_result = cursor.fetchone()
            total_networks = int(total_networks_result[0]) if total_networks_result and isinstance(total_networks_result, tuple) and len(total_networks_result) >= 1 else 0
            
            # 获取IP总数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses')
            total_ips_result = cursor.fetchone()
            total_ips = int(total_ips_result[0]) if total_ips_result and isinstance(total_ips_result, tuple) and len(total_ips_result) >= 1 else 0
            
            # 获取已分配IP数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE status = ?', ('allocated',))
            allocated_ips_result = cursor.fetchone()
            allocated_ips = int(allocated_ips_result[0]) if allocated_ips_result and isinstance(allocated_ips_result, tuple) and len(allocated_ips_result) >= 1 else 0
            
            # 获取已保留IP数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE status = ?', ('reserved',))
            reserved_ips_result = cursor.fetchone()
            reserved_ips = int(reserved_ips_result[0]) if reserved_ips_result and isinstance(reserved_ips_result, tuple) and len(reserved_ips_result) >= 1 else 0
            
            # 获取过期IP数，包括allocated和reserved状态
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE expiry_date < ? AND status IN ("allocated", "reserved")', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            expired_ips_result = cursor.fetchone()
            expired_ips = int(expired_ips_result[0]) if expired_ips_result and isinstance(expired_ips_result, tuple) and len(expired_ips_result) >= 1 else 0
            
            # 获取IPv4和IPv6网络数
            _ = cursor.execute('SELECT network_address FROM networks')
            network_rows = cursor.fetchall()
            ipv4_networks = 0
            ipv6_networks = 0
            
            for network in network_rows:
                try:
                    if isinstance(network, tuple) and len(network) >= 1:
                        ip_network = ipaddress.ip_network(str(network[0]))
                        if ip_network.version == 4:
                            ipv4_networks += 1
                        elif ip_network.version == 6:
                            ipv6_networks += 1
                except Exception:
                    pass
            
            conn.close()
            
            stats = {
                'total_networks': total_networks,
                'total_ips': total_ips,
                'allocated_ips': allocated_ips,
                'reserved_ips': reserved_ips,
                'expired_ips': expired_ips,
                'ipv4_networks': ipv4_networks,
                'ipv6_networks': ipv6_networks
            }
            
            return stats
        except Exception:
            return {
                'total_networks': 0,
                'total_ips': 0,
                'allocated_ips': 0,
                'reserved_ips': 0,
                'expired_ips': 0,
                'ipv4_networks': 0,
                'ipv6_networks': 0
            }
