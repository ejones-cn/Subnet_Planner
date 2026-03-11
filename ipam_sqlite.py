#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP地址管理（IPAM）模块 - SQLite版本
负责IP地址的分配、跟踪、状态管理和历史记录
"""

import sqlite3
import json
import os
import sys
import platform
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import ipaddress

class IPAMSQLite:
    """IP地址管理类 - SQLite版本"""
    
    def __init__(self, db_file: str = "ipam_data.db"):
        """初始化IPAM
        
        Args:
            db_file: 数据库文件路径
        """
        self.db_file = db_file
        self.backup_dir = os.path.join(os.path.dirname(db_file), "ipam_backups")
        # 创建备份目录
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # 创建networks表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS networks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_address TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
        ''')
        
        # 创建ip_addresses表
        cursor.execute('''
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
        cursor.execute('''
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
        cursor.execute('''
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
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_network_id ON ip_addresses(network_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_status ON ip_addresses(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_ip_address ON ip_addresses(ip_address)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_expiry_date ON ip_addresses(expiry_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocation_history_network_id ON allocation_history(network_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocation_history_action ON allocation_history(action)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_allocation_history_performed_at ON allocation_history(performed_at)')
        
        conn.commit()
        conn.close()
    
    def migrate_from_json(self, json_file: str = "ipam_data.json"):
        """从JSON文件迁移数据
        
        Args:
            json_file: JSON数据文件路径
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
            conn.execute('BEGIN TRANSACTION')
            
            # 迁移networks
            networks_map = {}  # 用于映射网络地址到ID
            for network_str, network_data in data.get('networks', {}).items():
                created_at = network_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                cursor.execute('''
                INSERT OR IGNORE INTO networks (network_address, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ''', (network_str, network_data.get('description', ''), created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 获取所有网络的ID
            cursor.execute('SELECT id, network_address FROM networks')
            for row in cursor.fetchall():
                networks_map[row[1]] = row[0]
            
            # 迁移ip_addresses
            for network_str, network_data in data.get('networks', {}).items():
                network_id = networks_map.get(network_str)
                if not network_id:
                    continue
                
                for ip_str, ip_data in network_data.get('ip_addresses', {}).items():
                    created_at = ip_data.get('allocated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    cursor.execute('''
                    INSERT OR IGNORE INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                    allocated_at, allocated_by, expiry_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_str, ip_data.get('status', 'available'), 
                          ip_data.get('hostname', ''), ip_data.get('description', ''),
                          ip_data.get('allocated_at'), ip_data.get('allocated_by'),
                          ip_data.get('expiry_date'), created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 迁移allocation_history
            for history_item in data.get('allocation_history', []):
                network_id = networks_map.get(history_item.get('network'))
                if not network_id:
                    continue
                
                cursor.execute('''
                INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                performed_by, performed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (network_id, history_item.get('ip_address'), history_item.get('action'),
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
    
    def get_most_specific_network(self, ip_address: str):
        """获取IP地址最具体的归属网络
        
        Args:
            ip_address: IP地址
            
        Returns:
            Dict: 网络信息，或None
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, network_address, description, created_at, updated_at FROM networks')
        networks = cursor.fetchall()
        
        conn.close()
        
        import ipaddress
        target_ip = ipaddress.ip_address(ip_address)
        most_specific_network = None
        max_prefix_len = 0
        
        for network in networks:
            try:
                network_obj = ipaddress.ip_network(network[1])
                if target_ip in network_obj:
                    if network_obj.prefixlen > max_prefix_len:
                        max_prefix_len = network_obj.prefixlen
                        most_specific_network = {
                            'id': network[0],
                            'network_address': network[1],
                            'description': network[2],
                            'created_at': network[3],
                            'updated_at': network[4]
                        }
            except:
                pass
        
        return most_specific_network
    
    def add_network(self, network: str, description: str = ""):
        """添加网络
        
        Args:
            network: 网络地址（CIDR格式）
            description: 网络描述
        
        Returns:
            tuple: (bool, str) - (是否添加成功, 错误信息)
        """
        try:
            # 验证网络格式
            if not network:
                return False, "网络地址不能为空"
            
            try:
                ip_network = ipaddress.ip_network(network, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return False, f"网络格式错误: {str(e)}"
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查网络是否已存在
            cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
            if cursor.fetchone():
                conn.close()
                return False, "网络已存在"
            
            # 添加网络
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
            INSERT INTO networks (network_address, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ''', (network_str, description, created_at, created_at))
            
            network_id = cursor.lastrowid
            
            # 检查是否有IP地址应该归属到这个新网络
            cursor.execute('SELECT id, network_id, ip_address FROM ip_addresses')
            ips = cursor.fetchall()
            
            for ip in ips:
                try:
                    ip_obj = ipaddress.ip_address(ip[2])
                    if ip_obj in ip_network:
                        # 检查是否是更具体的网络
                        cursor.execute('SELECT network_address FROM networks WHERE id = ?', (ip[1],))
                        current_network_row = cursor.fetchone()
                        if current_network_row:
                            current_network_obj = ipaddress.ip_network(current_network_row[0])
                            if ip_network.prefixlen > current_network_obj.prefixlen:
                                # 更新归属关系
                                cursor.execute('UPDATE ip_addresses SET network_id = ? WHERE id = ?', (network_id, ip[0]))
                except:
                    pass
            
            conn.commit()
            conn.close()
            return True, "网络添加成功"
        except Exception as e:
            return False, f"添加网络失败: {str(e)}"
    
    def allocate_ip(self, network: str, ip_address: str, hostname: str, description: str = "", expiry_date: str = None):
        """分配IP地址
        
        Args:
            network: 网络地址（CIDR格式）
            ip_address: 要分配的IP地址
            hostname: 主机名
            description: 描述
            expiry_date: 过期日期（ISO格式）
        
        Returns:
            tuple: (bool, str) - (是否分配成功, 错误信息)
        """
        try:
            # 验证参数
            if not network:
                return False, "网络地址不能为空"
            if not ip_address:
                return False, "IP地址不能为空"
            if not hostname and not description:
                return False, "主机名和描述不能同时为空"
            
            # 验证IP地址格式
            try:
                ip_obj = ipaddress.ip_address(ip_address)
            except ValueError as e:
                return False, f"IP地址格式错误: {str(e)}"
            
            # 找到最具体的网络
            most_specific_network = self.get_most_specific_network(ip_address)
            if not most_specific_network:
                # 如果没有找到合适的网络，使用指定的网络
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network,))
                network_row = cursor.fetchone()
                if not network_row:
                    conn.close()
                    return False, "网络不存在"
                network_id = network_row[0]
                conn.close()
            else:
                network_id = most_specific_network['id']
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            try:
                # 开始事务
                conn.execute('BEGIN EXCLUSIVE')
                
                # 检查IP地址是否已存在
                cursor.execute('SELECT id, status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                ip_row = cursor.fetchone()
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                success_result = None
                if ip_row:
                    # IP地址已存在
                    ip_id, status = ip_row
                    if status == 'available':
                        # IP地址已被释放，可以重新分配
                        cursor.execute('''
                        UPDATE ip_addresses SET status = ?, hostname = ?, description = ?, 
                        allocated_at = ?, allocated_by = ?, expiry_date = ?, updated_at = ?
                        WHERE id = ?
                        ''', ('allocated', hostname, description, now, 'admin', expiry_date, now, ip_id))
                    else:
                        # IP地址已被分配或保留
                        success_result = (False, "IP地址已被分配或保留")
                else:
                    # 新的IP地址，插入记录
                    cursor.execute('''
                    INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                    allocated_at, allocated_by, expiry_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, 'allocated', hostname, description,
                          now, 'admin', expiry_date, now, now))
                
                if success_result is None:
                    # 记录分配历史
                    cursor.execute('''
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
    
    def get_network_ips(self, network: str):
        """获取网络及其所有子网络的IP地址
        
        Args:
            network: 网络地址（CIDR格式）
        
        Returns:
            List[Dict]: IP地址列表
        """
        try:
            ip_network = ipaddress.ip_network(network, strict=False)
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取所有IP地址
            cursor.execute('SELECT id, network_id, ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at FROM ip_addresses')
            ips = cursor.fetchall()
            
            conn.close()
            
            # 过滤出属于目标网络的IP地址
            relevant_ips = []
            for ip in ips:
                try:
                    ip_obj = ipaddress.ip_address(ip[2])
                    if ip_obj in ip_network:
                        relevant_ips.append({
                            'id': ip[0],
                            'network_id': ip[1],
                            'ip_address': ip[2],
                            'status': ip[3],
                            'hostname': ip[4],
                            'description': ip[5],
                            'allocated_at': ip[6],
                            'allocated_by': ip[7],
                            'expiry_date': ip[8],
                            'created_at': ip[9],
                            'updated_at': ip[10]
                        })
                except:
                    pass
            
            return relevant_ips
        except Exception:
            return []
    
    def get_all_networks(self):
        """获取所有网络
        
        Returns:
            List[Dict]: 网络列表
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, network_address, description, created_at, updated_at FROM networks')
        networks = cursor.fetchall()
        
        # 一次性获取所有IP地址，避免多次数据库查询
        cursor.execute('SELECT ip_address FROM ip_addresses')
        all_ips = cursor.fetchall()
        
        conn.close()
        
        # 预处理IP地址，避免重复创建ipaddress对象
        ip_objects = []
        for ip in all_ips:
            try:
                ip_obj = ipaddress.ip_address(ip[0])
                ip_objects.append(ip_obj)
            except:
                pass
        
        network_list = []
        for network in networks:
            # 计算网络及其子网络的IP数量
            ip_count = self.get_network_ip_count(network[1], ip_objects)
            
            network_list.append({
                'id': network[0],
                'network': network[1],
                'description': network[2],
                'created_at': network[3],
                'updated_at': network[4],
                'ip_count': ip_count
            })
        
        return network_list
    
    def get_network_ip_count(self, network_address: str, ip_objects=None):
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
            count = 0
            
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
                cursor.execute('SELECT ip_address FROM ip_addresses')
                ips = cursor.fetchall()
                
                conn.close()
                
                for ip in ips:
                    try:
                        ip_obj = ipaddress.ip_address(ip[0])
                        if ip_obj in ip_network:
                            count += 1
                    except:
                        pass
            
            return count
        except Exception:
            return 0
    
    def release_ip(self, ip_address: str):
        """释放IP地址
        
        Args:
            ip_address: 要释放的IP地址
        
        Returns:
            tuple: (bool, str) - (是否释放成功, 错误信息)
        """
        try:
            # 验证参数
            if not ip_address:
                return False, "IP地址不能为空"
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查找IP地址
            cursor.execute('SELECT id, network_id, status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            if not ip_row:
                conn.close()
                return False, "IP地址不存在"
            
            ip_id = ip_row[0]
            network_id = ip_row[1]
            status = ip_row[2]
            
            if status == 'available':
                conn.close()
                return False, "IP地址未被分配或已被释放"
            
            # 释放IP地址
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('UPDATE ip_addresses SET status = ?, updated_at = ? WHERE id = ?', ('available', now, ip_id))
            
            # 记录释放历史
            cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'release', 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址释放成功"
        except Exception as e:
            return False, f"释放IP地址失败: {str(e)}"
    
    def get_ip_info(self, ip_address: str):
        """获取IP地址信息
        
        Args:
            ip_address: IP地址
        
        Returns:
            Dict or None: IP地址信息，包含hostname, description等字段，失败返回None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查询IP地址信息
            cursor.execute('SELECT hostname, description, network_id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            
            if ip_row:
                return {
                    'hostname': ip_row[0],
                    'description': ip_row[1],
                    'network_id': ip_row[2]
                }
            return None
        except Exception as e:
            print(f"获取IP地址信息失败: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()
    
    def update_ip_info(self, ip_address: str, hostname: str, description: str):
        """更新IP地址信息
        
        Args:
            ip_address: IP地址
            hostname: 新的主机名
            description: 新的描述
        
        Returns:
            tuple: (bool, str) - (是否更新成功, 错误信息)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查IP地址是否存在
            cursor.execute('SELECT id, network_id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            if not ip_row:
                conn.close()
                return False, "IP地址不存在"
            
            ip_id, network_id = ip_row
            
            # 更新IP地址信息
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
            UPDATE ip_addresses 
            SET hostname = ?, description = ?, updated_at = ?
            WHERE id = ?
            ''', (hostname, description, now, ip_id))
            
            # 记录更新历史
            cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
            performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'update', hostname, description, 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址信息更新成功"
        except Exception as e:
            return False, f"更新IP地址信息失败: {str(e)}"

    def update_ip_expiry(self, ip_address: str, expiry_date: str):
        """更新IP地址过期日期
        
        Args:
            ip_address: IP地址
            expiry_date: 过期日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS，传入None则清除过期日期）
            
        Returns:
            tuple: (bool, str) - (是否更新成功, 错误信息)
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
                cursor.execute('SELECT id, network_id, hostname, description FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                ip_row = cursor.fetchone()
                if not ip_row:
                    return False, "IP地址不存在"
                
                ip_id, network_id, hostname, description = ip_row
                
                # 更新IP地址过期日期
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                UPDATE ip_addresses 
                SET expiry_date = ?, updated_at = ?
                WHERE id = ?
                ''', (expiry_date, now, ip_id))
                
                # 记录更新历史
                cursor.execute('''
                INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                performed_by, performed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (network_id, ip_address, 'update', hostname, description, 'admin', now))
                
                conn.commit()
                return True, "IP地址过期日期更新成功"
        except Exception as e:
            return False, f"更新IP地址过期日期失败: {str(e)}"
    
    def _validate_expiry_date(self, expiry_date: str) -> Optional[str]:
        """验证并标准化过期日期格式
        
        Args:
            expiry_date: 过期日期字符串
            
        Returns:
            Optional[str]: 标准化后的日期字符串（YYYY-MM-DD HH:MM:SS），验证失败返回None
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

    def cleanup_available_ips(self):
        """清理所有可用状态的IP地址
        
        Returns:
            tuple: (bool, str) - (是否清理成功, 错误信息)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查找所有可用状态的IP地址
            cursor.execute('SELECT id, network_id, ip_address FROM ip_addresses WHERE status = ?', ('available',))
            available_ips = cursor.fetchall()
            
            if not available_ips:
                conn.close()
                return True, "没有可用状态的IP地址需要清理"
            
            # 记录清理历史
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for ip in available_ips:
                ip_id, network_id, ip_address = ip
                # 记录清理历史
                cursor.execute('''
                INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
                VALUES (?, ?, ?, ?, ?)
                ''', (network_id, ip_address, 'cleanup', 'admin', now))
            
            # 删除可用状态的IP地址
            cursor.execute('DELETE FROM ip_addresses WHERE status = ?', ('available',))
            
            conn.commit()
            conn.close()
            return True, f"成功清理 {len(available_ips)} 个可用状态的IP地址"
        except Exception as e:
            return False, f"清理可用IP地址失败: {str(e)}"
    
    def get_ip_status(self, network: str, ip_address: str):
        """获取IP地址状态
        
        Args:
            network: 网络地址（CIDR格式）
            ip_address: IP地址
        
        Returns:
            str: IP地址状态（allocated, reserved, available）
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('SELECT status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return result[0]
            else:
                return 'available'
        except Exception:
            return 'available'
    
    def reserve_ip(self, network: str, ip_address: str, description: str = ""):
        """保留IP地址
        
        Args:
            network: 网络地址（CIDR格式）
            ip_address: 要保留的IP地址
            description: 描述
        
        Returns:
            tuple: (bool, str) - (是否保留成功, 错误信息)
        """
        try:
            # 验证参数
            if not network:
                return False, "网络地址不能为空"
            if not ip_address:
                return False, "IP地址不能为空"
            
            # 验证IP地址格式
            try:
                ip_obj = ipaddress.ip_address(ip_address)
            except ValueError as e:
                return False, f"IP地址格式错误: {str(e)}"
            
            # 找到最具体的网络
            most_specific_network = self.get_most_specific_network(ip_address)
            if not most_specific_network:
                # 如果没有找到合适的网络，使用指定的网络
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network,))
                network_row = cursor.fetchone()
                if not network_row:
                    conn.close()
                    return False, "网络不存在"
                network_id = network_row[0]
                conn.close()
            else:
                network_id = most_specific_network['id']
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查IP地址是否已存在
            cursor.execute('SELECT id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if ip_row:
                # 更新IP地址状态
                cursor.execute('UPDATE ip_addresses SET status = ?, description = ?, updated_at = ? WHERE id = ?', 
                             ('reserved', description, now, ip_row[0]))
            else:
                # 创建新的IP地址记录
                cursor.execute('''
                INSERT INTO ip_addresses (network_id, ip_address, status, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (network_id, ip_address, 'reserved', description, now, now))
            
            # 记录保留历史
            cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, description, performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'reserve', description, 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址保留成功"
        except Exception as e:
            return False, f"保留IP地址失败: {str(e)}"

    def update_network_description(self, network: str, description: str):
        """更新网络描述
        
        Args:
            network: 网络地址（CIDR格式）
            description: 新的描述信息
        
        Returns:
            tuple: (bool, str) - (是否更新成功, 错误信息)
        """
        try:
            if not network:
                return False, "网络地址不能为空"
            
            try:
                ip_network = ipaddress.ip_network(network, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return False, f"网络格式错误: {str(e)}"
            
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # 检查网络是否存在
                cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
                network_row = cursor.fetchone()
                if not network_row:
                    return False, "网络不存在"
                
                # 更新网络描述
                cursor.execute('UPDATE networks SET description = ?, updated_at = datetime("now") WHERE id = ?', 
                             (description, network_row[0]))
                
                conn.commit()
            return True, "网络描述更新成功"
        except Exception as e:
            return False, f"更新网络描述失败: {str(e)}"

    def remove_network(self, network: str):
        """移除网络
        
        Args:
            network: 网络地址（CIDR格式）
        
        Returns:
            tuple: (bool, str) - (是否移除成功, 错误信息)
        """
        try:
            if not network:
                return False, "网络地址不能为空"
            
            try:
                ip_network = ipaddress.ip_network(network, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return False, f"网络格式错误: {str(e)}"
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 检查网络是否存在
            cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
            network_row = cursor.fetchone()
            if not network_row:
                conn.close()
                return False, "网络不存在"
            
            network_id = network_row[0]
            
            # 检查网络是否有IP地址
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE network_id = ?', (network_id,))
            ip_count = cursor.fetchone()[0]
            if ip_count > 0:
                conn.close()
                return False, f"网络中存在 {ip_count} 个IP地址，请先释放或保留这些IP地址"
            
            # 移除网络
            cursor.execute('DELETE FROM networks WHERE id = ?', (network_id,))
            
            conn.commit()
            conn.close()
            return True, "网络移除成功"
        except Exception as e:
            return False, f"移除网络失败: {str(e)}"
    
    def get_overall_stats(self):
        """获取整体统计信息
        
        Returns:
            Dict: 整体统计信息
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取网络总数
            cursor.execute('SELECT COUNT(*) FROM networks')
            total_networks = cursor.fetchone()[0]
            
            # 获取IP总数
            cursor.execute('SELECT COUNT(*) FROM ip_addresses')
            total_ips = cursor.fetchone()[0]
            
            # 获取已分配IP数
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE status = ?', ('allocated',))
            allocated_ips = cursor.fetchone()[0]
            
            # 获取已保留IP数
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE status = ?', ('reserved',))
            reserved_ips = cursor.fetchone()[0]
            
            # 获取过期IP数
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE expiry_date < ?', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            expired_ips = cursor.fetchone()[0]
            
            # 获取IPv4和IPv6网络数
            cursor.execute('SELECT network_address FROM networks')
            networks = cursor.fetchall()
            ipv4_networks = 0
            ipv6_networks = 0
            
            for network in networks:
                try:
                    ip_network = ipaddress.ip_network(network[0])
                    if ip_network.version == 4:
                        ipv4_networks += 1
                    elif ip_network.version == 6:
                        ipv6_networks += 1
                except:
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
    
    def backup_data(self, backup_name=None, backup_type='auto', frequency='hourly', compress=False, encrypt=False, password=None):
        """备份IPAM数据
        
        Args:
            backup_name: 可选的备份名称，如果不提供则使用时间戳
            backup_type: 备份类型，可选值：'auto'（自动备份）、'manual'（手动备份）、'before_import'（导入前备份）、'before_operation'（操作前备份）
            frequency: 备份频率，可选值：'hourly'（每小时）、'daily'（每天）、'weekly'（每周）
            compress: 是否压缩备份文件
            encrypt: 是否加密备份文件
            password: 加密密码
            
        Returns:
            str: 备份文件路径
        """
        try:
            # 检查是否需要自动备份
            if backup_type == 'auto':
                last_backup_file = os.path.join(self.backup_dir, f'last_{frequency}_backup.txt')
                if os.path.exists(last_backup_file):
                    try:
                        with open(last_backup_file, 'r', encoding='utf-8') as f:
                            last_backup_time = f.read().strip()
                        if last_backup_time:
                            last_backup = datetime.fromisoformat(last_backup_time)
                            # 根据频率确定备份间隔
                            if frequency == 'hourly':
                                if (datetime.now() - last_backup).total_seconds() < 3600:  # 1小时
                                    return None  # 不需要备份
                            elif frequency == 'daily':
                                if (datetime.now() - last_backup).total_seconds() < 86400:  # 24小时
                                    return None  # 不需要备份
                            elif frequency == 'weekly':
                                if (datetime.now() - last_backup).total_seconds() < 604800:  # 7天
                                    return None  # 不需要备份
                    except:
                        pass
                
                # 更新最后备份时间
                with open(last_backup_file, 'w', encoding='utf-8') as f:
                    f.write(datetime.now().isoformat())
            
            # 生成备份文件名
            if backup_name:
                backup_filename = f"ipam_bak_{backup_name}"
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                # 将备份类型转换为单字母
                type_code = {
                    'auto': 'a',
                    'manual': 'm',
                    'before_import': 'i',
                    'before_operation': 'o'
                }.get(backup_type, backup_type[0])
                backup_filename = f"ipam_bak_{timestamp}_{type_code}"
            
            # 添加文件扩展名
            if compress:
                backup_filename += '.zip'
            else:
                backup_filename += '.json'
            
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # 准备备份数据
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取网络数据
            cursor.execute('SELECT network_address, description, created_at, updated_at FROM networks')
            networks_rows = cursor.fetchall()
            
            networks = {}
            for row in networks_rows:
                network_address, description, created_at, updated_at = row
                networks[network_address] = {
                    'description': description,
                    'ip_addresses': {},
                    'created_at': created_at
                }
                
                # 获取该网络的IP地址
                cursor.execute('SELECT ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at FROM ip_addresses WHERE network_id = (SELECT id FROM networks WHERE network_address = ?)', (network_address,))
                ips_rows = cursor.fetchall()
                
                for ip_row in ips_rows:
                    ip_address, status, hostname, ip_description, allocated_at, allocated_by, expiry_date, ip_created_at, ip_updated_at = ip_row
                    networks[network_address]['ip_addresses'][ip_address] = {
                        'status': status,
                        'hostname': hostname,
                        'description': ip_description,
                        'allocated_at': allocated_at,
                        'allocated_by': allocated_by,
                        'expiry_date': expiry_date
                    }
            
            # 获取分配历史
            cursor.execute('SELECT network_id, ip_address, action, hostname, description, performed_by, performed_at FROM allocation_history')
            history_rows = cursor.fetchall()
            
            allocation_history = []
            for row in history_rows:
                network_id, ip_address, action, hostname, description, performed_by, performed_at = row
                
                # 获取网络地址
                cursor.execute('SELECT network_address FROM networks WHERE id = ?', (network_id,))
                network_row = cursor.fetchone()
                network = network_row[0] if network_row else ''
                
                allocation_history.append({
                    'network': network,
                    'ip_address': ip_address,
                    'action': action,
                    'hostname': hostname,
                    'description': description,
                    'performed_by': performed_by,
                    'timestamp': performed_at
                })
            
            conn.close()
            
            data = {
                'networks': networks,
                'allocation_history': allocation_history,
                'backup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'backup_name': backup_name,
                'backup_type': backup_type,
                'backup_frequency': frequency,
                'backup_version': '1.2',
                'network_count': len(networks),
                'ip_count': sum(len(net['ip_addresses']) for net in networks.values()),
                'data_version': '1.0',
                'system_info': {
                    'python_version': sys.version,
                    'platform': platform.platform(),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'backup_options': {
                    'compress': compress,
                    'encrypt': encrypt,
                    'version': '1.2'
                }
            }
            
            if compress:
                # 压缩备份
                import zipfile
                import io
                
                # 创建内存中的JSON数据
                json_data = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
                
                # 创建ZIP文件
                with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.writestr('ipam_data.json', json_data)
            else:
                # 直接保存为JSON文件
                with open(backup_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 清理旧备份
            self._cleanup_old_backups(keep=10, backup_type=backup_type, frequency=frequency)
            
            return backup_path
        except Exception:
            return None
    
    def _cleanup_old_backups(self, keep=10, backup_type=None, frequency=None):
        """清理旧备份文件，保留指定数量的最新备份
        
        Args:
            keep: 要保留的备份文件数量
            backup_type: 备份类型，可选，用于智能清理
            frequency: 备份频率，可选，用于智能清理
        """
        try:
            # 获取所有备份文件
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if (filename.startswith('ipam_backup_') or filename.startswith('ipam_bak_')) and filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    backup_files.append((os.path.getmtime(file_path), file_path, filename))
            
            # 按修改时间排序，最新的在前
            backup_files.sort(reverse=True)
            
            # 根据备份类型和频率进行智能清理
            if backup_type and frequency:
                # 只清理相同类型和频率的备份
                filtered_backups = []
                for mtime, path, filename in backup_files:
                    if f'_{backup_type}_' in filename and f'_{frequency}' in filename:
                        filtered_backups.append((mtime, path))
                if filtered_backups:
                    # 删除多余的备份
                    for _, file_path in filtered_backups[keep:]:
                        try:
                            os.remove(file_path)
                        except:
                            pass
            else:
                # 清理所有备份
                for _, file_path, _ in backup_files[keep:]:
                    try:
                        os.remove(file_path)
                    except:
                        pass
        except:
            pass
    
    def get_backup_info(self, backup_file):
        """获取备份文件的信息
        
        Args:
            backup_file: 备份文件路径
            
        Returns:
            dict: 备份信息
        """
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'backup_time': data.get('backup_time'),
                    'backup_name': data.get('backup_name'),
                    'network_count': data.get('network_count', 0),
                    'ip_count': data.get('ip_count', 0)
                }
        except:
            return None
    
    def list_backups(self):
        """列出所有备份文件
        
        Returns:
            list: 备份文件信息列表
        """
        try:
            backups = []
            for filename in os.listdir(self.backup_dir):
                if (filename.startswith('ipam_backup_') or filename.startswith('ipam_bak_')) and filename.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, filename)
                    info = self.get_backup_info(file_path)
                    if info:
                        backups.append({
                            'file_path': file_path,
                            'filename': filename,
                            'info': info
                        })
            
            # 按备份时间排序，最新的在前
            backups.sort(key=lambda x: x['info'].get('backup_time', ''), reverse=True)
            return backups
        except:
            return []
    
    def restore_data(self, backup_file: str, password=None):
        """从备份文件恢复IPAM数据
        
        Args:
            backup_file: 备份文件路径
            password: 解密密码
            
        Returns:
            bool: 是否恢复成功
        """
        try:
            if not os.path.exists(backup_file):
                return False
            
            # 检查是否为压缩文件
            if backup_file.endswith('.zip'):
                import zipfile
                import io
                
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # 读取压缩文件中的IPAM数据
                    with zipf.open('ipam_data.json') as f:
                        data = json.load(f)
            else:
                # 直接读取JSON文件
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # 恢复数据
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 开始事务
            conn.execute('BEGIN TRANSACTION')
            
            # 清空现有数据
            cursor.execute('DELETE FROM allocation_history')
            cursor.execute('DELETE FROM ip_addresses')
            cursor.execute('DELETE FROM networks')
            
            # 恢复网络数据
            networks = data.get('networks', {})
            for network_address, network_data in networks.items():
                description = network_data.get('description', '')
                created_at = network_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                cursor.execute('''
                INSERT INTO networks (network_address, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ''', (network_address, description, created_at, created_at))
                
                network_id = cursor.lastrowid
                
                # 恢复IP地址数据
                ip_addresses = network_data.get('ip_addresses', {})
                for ip_address, ip_data in ip_addresses.items():
                    status = ip_data.get('status', 'available')
                    hostname = ip_data.get('hostname', '')
                    ip_description = ip_data.get('description', '')
                    allocated_at = ip_data.get('allocated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    allocated_by = ip_data.get('allocated_by', 'admin')
                    expiry_date = ip_data.get('expiry_date')
                    
                    cursor.execute('''
                    INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                    allocated_at, allocated_by, expiry_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, status, hostname, ip_description, 
                          allocated_at, allocated_by, expiry_date, allocated_at, allocated_at))
            
            # 恢复分配历史
            allocation_history = data.get('allocation_history', [])
            for record in allocation_history:
                network = record.get('network')
                ip_address = record.get('ip_address')
                action = record.get('action')
                hostname = record.get('hostname', '')
                description = record.get('description', '')
                performed_by = record.get('performed_by', 'admin')
                performed_at = record.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                # 获取网络ID
                cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network,))
                network_row = cursor.fetchone()
                if network_row:
                    network_id = network_row[0]
                    cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                    performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_address, action, hostname, description, performed_by, performed_at))
            
            # 提交事务
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def batch_allocate_ips(self, network: str, ip_list: list):
        """批量分配IP地址
        
        Args:
            network: 网络地址（CIDR格式）
            ip_list: IP地址列表，每个元素是字典格式：{'ip_address': str, 'hostname': str, 'description': str}
        
        Returns:
            tuple: (int, list) - (成功分配的数量, 失败的IP列表)
        """
        try:
            # 验证网络格式
            try:
                ip_network = ipaddress.ip_network(network, strict=False)
                network_str = str(ip_network)
            except ValueError as e:
                return 0, [{'ip': ip_info.get('ip_address', ''), 'error': f"网络格式错误: {str(e)}"} for ip_info in ip_list]
            
            # 检查网络是否存在
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
            network_row = cursor.fetchone()
            if not network_row:
                conn.close()
                return 0, [{'ip': ip_info.get('ip_address', ''), 'error': "网络不存在"} for ip_info in ip_list]
            network_id = network_row[0]
            conn.close()
            
            success_count = 0
            failed_ips = []
            allocation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            for ip_info in ip_list:
                ip_address = ip_info.get('ip_address', '')
                hostname = ip_info.get('hostname', '')
                description = ip_info.get('description', '')
                
                try:
                    # 验证IP地址格式
                    try:
                        ip = ipaddress.ip_address(ip_address)
                        ip_str = str(ip)
                    except ValueError as e:
                        failed_ips.append({'ip': ip_address, 'error': f"IP地址格式错误: {str(e)}"})
                        continue
                    
                    # 检查IP是否在网络内
                    if ip not in ip_network:
                        failed_ips.append({'ip': ip_str, 'error': f"IP地址不在网络 {network_str} 内"})
                        continue
                    
                    # 检查IP是否已分配
                    conn = sqlite3.connect(self.db_file)
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM ip_addresses WHERE ip_address = ?', (ip_str,))
                    if cursor.fetchone():
                        conn.close()
                        failed_ips.append({'ip': ip_str, 'error': "IP地址已被分配或保留"})
                        continue
                    
                    # 分配IP地址
                    cursor.execute('''
                    INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                    allocated_at, allocated_by, expiry_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_str, 'allocated', hostname, description,
                          allocation_time, 'admin', None, allocation_time, allocation_time))
                    
                    # 记录分配历史
                    cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                    performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_str, 'allocate', hostname, description, 'admin', allocation_time))
                    
                    conn.commit()
                    conn.close()
                    success_count += 1
                    
                except Exception as e:
                    failed_ips.append({'ip': ip_address, 'error': f"分配失败: {str(e)}"})
                    if conn:
                        conn.close()
            
            return success_count, failed_ips
        except Exception as e:
            return 0, [{'ip': ip_info.get('ip_address', ''), 'error': f"批量分配失败: {str(e)}"} for ip_info in ip_list]
    
    def get_allocation_history(self, limit: int = 100):
        """获取分配历史
        
        Args:
            limit: 历史记录数量限制
        
        Returns:
            List[Dict]: 历史记录列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取分配历史，按时间倒序排列，限制数量
            cursor.execute('''
            SELECT a.network_id, a.ip_address, a.action, a.hostname, a.description, a.performed_by, a.performed_at, n.network_address
            FROM allocation_history a
            JOIN networks n ON a.network_id = n.id
            ORDER BY a.performed_at DESC
            LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                network_id, ip_address, action, hostname, description, performed_by, performed_at, network_address = row
                history.append({
                    'network': network_address,
                    'ip_address': ip_address,
                    'action': action,
                    'hostname': hostname,
                    'description': description,
                    'performed_by': performed_by,
                    'timestamp': performed_at
                })
            
            conn.close()
            return history
        except Exception:
            return []
    
    def export_data(self, export_file: str, format: str = 'json', networks: list = None):
        """导出IPAM数据
        
        Args:
            export_file: 导出文件路径
            format: 导出格式，支持 'json', 'csv'
            networks: 要导出的网络列表，如果为None则导出所有网络
        
        Returns:
            bool: 是否导出成功
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 确定要导出的网络
            if networks:
                # 只导出指定的网络
                export_networks = {}
                for network_str in networks:
                    # 获取网络信息
                    cursor.execute('SELECT network_address, description, created_at, updated_at FROM networks WHERE network_address = ?', (network_str,))
                    network_row = cursor.fetchone()
                    if network_row:
                        network_address, description, created_at, updated_at = network_row
                        export_networks[network_address] = {
                            'description': description,
                            'ip_addresses': {},
                            'created_at': created_at
                        }
                        
                        # 获取该网络的IP地址
                        cursor.execute('''
                        SELECT ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at 
                        FROM ip_addresses 
                        WHERE network_id = (SELECT id FROM networks WHERE network_address = ?)
                        ''', (network_address,))
                        ips_rows = cursor.fetchall()
                        
                        for ip_row in ips_rows:
                            ip_address, status, hostname, ip_description, allocated_at, allocated_by, expiry_date, ip_created_at, ip_updated_at = ip_row
                            export_networks[network_address]['ip_addresses'][ip_address] = {
                                'status': status,
                                'hostname': hostname,
                                'description': ip_description,
                                'allocated_at': allocated_at,
                                'allocated_by': allocated_by,
                                'expiry_date': expiry_date
                            }
            else:
                # 导出所有网络
                export_networks = {}
                cursor.execute('SELECT network_address, description, created_at, updated_at FROM networks')
                networks_rows = cursor.fetchall()
                
                for network_row in networks_rows:
                    network_address, description, created_at, updated_at = network_row
                    export_networks[network_address] = {
                        'description': description,
                        'ip_addresses': {},
                        'created_at': created_at
                    }
                    
                    # 获取该网络的IP地址
                    cursor.execute('''
                    SELECT ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at 
                    FROM ip_addresses 
                    WHERE network_id = (SELECT id FROM networks WHERE network_address = ?)
                    ''', (network_address,))
                    ips_rows = cursor.fetchall()
                    
                    for ip_row in ips_rows:
                        ip_address, status, hostname, ip_description, allocated_at, allocated_by, expiry_date, ip_created_at, ip_updated_at = ip_row
                        export_networks[network_address]['ip_addresses'][ip_address] = {
                            'status': status,
                            'hostname': hostname,
                            'description': ip_description,
                            'allocated_at': allocated_at,
                            'allocated_by': allocated_by,
                            'expiry_date': expiry_date
                        }
            
            # 获取分配历史
            cursor.execute('''
            SELECT a.network_id, a.ip_address, a.action, a.hostname, a.description, a.performed_by, a.performed_at, n.network_address
            FROM allocation_history a
            JOIN networks n ON a.network_id = n.id
            ''')
            history_rows = cursor.fetchall()
            
            allocation_history = []
            for row in history_rows:
                network_id, ip_address, action, hostname, description, performed_by, performed_at, network_address = row
                allocation_history.append({
                    'network': network_address,
                    'ip_address': ip_address,
                    'action': action,
                    'hostname': hostname,
                    'description': description,
                    'performed_by': performed_by,
                    'timestamp': performed_at
                })
            
            conn.close()
            
            if format == 'json':
                # 导出为JSON格式
                data = {
                    'networks': export_networks,
                    'allocation_history': allocation_history,
                    'export_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif format == 'csv':
                # 导出为CSV格式
                import csv
                with open(export_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # 写入表头
                    writer.writerow(['Network', 'IP Address', 'Status', 'Hostname', 'Description', 'Allocated At', 'Allocated By'])
                    
                    # 写入数据
                    for network_str, network_data in export_networks.items():
                        for ip_str, ip_data in network_data.get('ip_addresses', {}).items():
                            writer.writerow([
                                network_str,
                                ip_str,
                                ip_data.get('status', ''),
                                ip_data.get('hostname', ''),
                                ip_data.get('description', ''),
                                ip_data.get('allocated_at', ''),
                                ip_data.get('allocated_by', '')
                            ])
            else:
                return False
            
            return True
        except Exception:
            return False
    
    def import_data(self, import_file: str, format: str = 'json'):
        """导入IPAM数据
        
        Args:
            import_file: 导入文件路径
            format: 导入格式，支持 'json', 'csv'
        
        Returns:
            bool: 是否导入成功
        """
        try:
            if not os.path.exists(import_file):
                return False
            
            if format == 'json':
                # 从JSON文件导入
                with open(import_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                # 开始事务
                conn.execute('BEGIN TRANSACTION')
                
                # 清空现有数据
                cursor.execute('DELETE FROM allocation_history')
                cursor.execute('DELETE FROM ip_addresses')
                cursor.execute('DELETE FROM networks')
                
                # 导入网络数据
                networks = data.get('networks', {})
                for network_address, network_data in networks.items():
                    description = network_data.get('description', '')
                    created_at = network_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    cursor.execute('''
                    INSERT INTO networks (network_address, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ''', (network_address, description, created_at, created_at))
                    
                    network_id = cursor.lastrowid
                    
                    # 导入IP地址数据
                    ip_addresses = network_data.get('ip_addresses', {})
                    for ip_address, ip_data in ip_addresses.items():
                        status = ip_data.get('status', 'available')
                        hostname = ip_data.get('hostname', '')
                        ip_description = ip_data.get('description', '')
                        allocated_at = ip_data.get('allocated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        allocated_by = ip_data.get('allocated_by', 'admin')
                        expiry_date = ip_data.get('expiry_date')
                        
                        cursor.execute('''
                        INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                        allocated_at, allocated_by, expiry_date, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (network_id, ip_address, status, hostname, ip_description, 
                              allocated_at, allocated_by, expiry_date, allocated_at, allocated_at))
                
                # 导入分配历史
                allocation_history = data.get('allocation_history', [])
                for record in allocation_history:
                    network = record.get('network')
                    ip_address = record.get('ip_address')
                    action = record.get('action')
                    hostname = record.get('hostname', '')
                    description = record.get('description', '')
                    performed_by = record.get('performed_by', 'admin')
                    performed_at = record.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # 获取网络ID
                    cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network,))
                    network_row = cursor.fetchone()
                    if network_row:
                        network_id = network_row[0]
                        cursor.execute('''
                        INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                        performed_by, performed_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (network_id, ip_address, action, hostname, description, performed_by, performed_at))
                
                # 提交事务
                conn.commit()
                conn.close()
            elif format == 'csv':
                # 从CSV文件导入
                import csv
                with open(import_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    conn = sqlite3.connect(self.db_file)
                    cursor = conn.cursor()
                    
                    # 开始事务
                    conn.execute('BEGIN TRANSACTION')
                    
                    # 清空现有数据
                    cursor.execute('DELETE FROM allocation_history')
                    cursor.execute('DELETE FROM ip_addresses')
                    cursor.execute('DELETE FROM networks')
                    
                    # 导入数据
                    networks_set = set()
                    for row in reader:
                        network_str = row.get('Network', '')
                        ip_str = row.get('IP Address', '')
                        status = row.get('Status', '')
                        hostname = row.get('Hostname', '')
                        description = row.get('Description', '')
                        allocated_at = row.get('Allocated At', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        allocated_by = row.get('Allocated By', 'admin')
                        
                        # 确保网络存在
                        if network_str not in networks_set:
                            cursor.execute('''
                            INSERT INTO networks (network_address, description, created_at, updated_at)
                            VALUES (?, ?, ?, ?)
                            ''', (network_str, '', allocated_at, allocated_at))
                            networks_set.add(network_str)
                        
                        # 获取网络ID
                        cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
                        network_row = cursor.fetchone()
                        if network_row:
                            network_id = network_row[0]
                            cursor.execute('''
                            INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                            allocated_at, allocated_by, expiry_date, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (network_id, ip_str, status, hostname, description, 
                                  allocated_at, allocated_by, None, allocated_at, allocated_at))
                    
                    # 提交事务
                    conn.commit()
                    conn.close()
            else:
                return False
            
            return True
        except Exception:
            return False
    
    def check_ip_conflict(self, ip_address: str):
        """检查IP地址是否与其他网络存在冲突
        
        Args:
            ip_address: IP地址
        
        Returns:
            bool: 是否存在冲突
        """
        try:
            # 验证IP地址格式
            ip = ipaddress.ip_address(ip_address)
            ip_str = str(ip)
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取所有网络
            cursor.execute('SELECT network_address FROM networks')
            networks = cursor.fetchall()
            
            conflict_count = 0
            for network in networks:
                network_str = network[0]
                try:
                    network_obj = ipaddress.ip_network(network_str, strict=False)
                    if ip in network_obj:
                        conflict_count += 1
                        if conflict_count > 1:
                            break
                except:
                    pass
            
            conn.close()
            return conflict_count > 1
        except Exception:
            return False
    
    def get_expired_ips(self):
        """获取过期的IP地址
        
        Returns:
            List[Dict]: 过期IP地址列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取过期的IP地址
            cursor.execute('''
            SELECT i.ip_address, i.hostname, i.description, n.network_address
            FROM ip_addresses i
            JOIN networks n ON i.network_id = n.id
            WHERE i.expiry_date < ? AND i.status = 'allocated'
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            
            expired_ips = []
            for row in cursor.fetchall():
                ip_address, hostname, description, network = row
                expired_ips.append({
                    'ip_address': ip_address,
                    'hostname': hostname,
                    'description': description,
                    'network': network
                })
            
            conn.close()
            return expired_ips
        except Exception:
            return []
    
    def get_network_stats(self, network):
        """获取网络统计信息
        
        Args:
            network: 网络地址（CIDR格式）
        
        Returns:
            Dict: 网络统计信息
        """
        try:
            # 验证网络格式
            ip_network = ipaddress.ip_network(network, strict=False)
            network_str = str(ip_network)
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取网络ID
            cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
            network_row = cursor.fetchone()
            if not network_row:
                conn.close()
                return {
                    'total_ips': 0,
                    'allocated_ips': 0,
                    'reserved_ips': 0,
                    'available_ips': 0
                }
            network_id = network_row[0]
            
            # 获取IP地址统计
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE network_id = ?', (network_id,))
            total_ips = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE network_id = ? AND status = ?', (network_id, 'allocated'))
            allocated_ips = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE network_id = ? AND status = ?', (network_id, 'reserved'))
            reserved_ips = cursor.fetchone()[0]
            
            # 计算可用IP数
            available_ips = total_ips - allocated_ips - reserved_ips
            
            conn.close()
            return {
                'total_ips': total_ips,
                'allocated_ips': allocated_ips,
                'reserved_ips': reserved_ips,
                'available_ips': available_ips
            }
        except Exception:
            return {
                'total_ips': 0,
                'allocated_ips': 0,
                'reserved_ips': 0,
                'available_ips': 0
            }
    
    def get_ips_by_time_range(self, start_time, end_time):
        """按时间范围获取IP地址
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            List[Dict]: IP地址列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取指定时间范围内分配的IP地址
            cursor.execute('''
            SELECT i.ip_address, i.hostname, i.description, n.network_address, i.allocated_at
            FROM ip_addresses i
            JOIN networks n ON i.network_id = n.id
            WHERE i.allocated_at >= ? AND i.allocated_at <= ? AND i.status = 'allocated'
            ORDER BY i.allocated_at
            ''', (start_time, end_time))
            
            ips = []
            for row in cursor.fetchall():
                ip_address, hostname, description, network, allocated_at = row
                ips.append({
                    'ip_address': ip_address,
                    'hostname': hostname,
                    'description': description,
                    'network': network,
                    'allocated_at': allocated_at
                })
            
            conn.close()
            return ips
        except Exception:
            return []
    
    def get_ips_by_expiry_range(self, start_time, end_time):
        """按过期时间范围获取IP地址
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            List[Dict]: IP地址列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取指定过期时间范围内的IP地址
            cursor.execute('''
            SELECT i.ip_address, i.hostname, i.description, n.network_address, i.expiry_date
            FROM ip_addresses i
            JOIN networks n ON i.network_id = n.id
            WHERE i.expiry_date >= ? AND i.expiry_date <= ? AND i.status = 'allocated'
            ORDER BY i.expiry_date
            ''', (start_time, end_time))
            
            ips = []
            for row in cursor.fetchall():
                ip_address, hostname, description, network, expiry_date = row
                ips.append({
                    'ip_address': ip_address,
                    'hostname': hostname,
                    'description': description,
                    'network': network,
                    'expiry_date': expiry_date
                })
            
            conn.close()
            return ips
        except Exception:
            return []

# 创建全局IPAM实例
ipam_instance = None

def init_ipam(db_file: str = "ipam_data.db"):
    """初始化IPAM实例
    
    Args:
        db_file: 数据库文件路径
    
    Returns:
        IPAMSQLite: IPAM实例
    """
    global ipam_instance
    ipam_instance = IPAMSQLite(db_file)
    return ipam_instance

def get_ipam():
    """获取IPAM实例
    
    Returns:
        IPAMSQLite: IPAM实例
    """
    global ipam_instance
    if ipam_instance is None:
        ipam_instance = IPAMSQLite()
    return ipam_instance

# 测试迁移功能
if __name__ == "__main__":
    ipam = IPAMSQLite()
    success, message = ipam.migrate_from_json()
    print(f"迁移结果: {success}, {message}")
    
    # 测试获取网络列表
    networks = ipam.get_all_networks()
    print(f"网络数量: {len(networks)}")
    for network in networks:
        print(f"网络: {network['network']}, 描述: {network['description']}, IP数量: {network['ip_count']}")
