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
import zipfile
import csv
from datetime import datetime
from typing import Any

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
                data: dict[str, Any] = json.load(f)
        except Exception as e:
            return False, f"读取JSON文件失败: {str(e)}"
        
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        try:
            # 开始事务
            _ = conn.execute('BEGIN TRANSACTION')
            
            # 迁移networks
            networks_map: dict[str, int] = {}  # 用于映射网络地址到ID
            for network_str, network_data in data.get('networks', {}).items():
                created_at: str = network_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                _ = cursor.execute('''
                INSERT OR IGNORE INTO networks (network_address, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ''', (network_str, network_data.get('description', ''), created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 获取所有网络的ID
            _ = cursor.execute('SELECT id, network_address FROM networks')
            for row in cursor.fetchall():
                networks_map[row[1]] = row[0]
            
            # 迁移ip_addresses
            for network_str, network_data in data.get('networks', {}).items():
                network_id: int | None = networks_map.get(network_str)
                if not network_id:
                    continue
                
                for ip_str, ip_data in network_data.get('ip_addresses', {}).items():
                    created_at: str = ip_data.get('allocated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    _ = cursor.execute('''
                    INSERT OR IGNORE INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                    allocated_at, allocated_by, expiry_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, ip_str, ip_data.get('status', 'available'), 
                          ip_data.get('hostname', ''), ip_data.get('description', ''),
                          ip_data.get('allocated_at'), ip_data.get('allocated_by'),
                          ip_data.get('expiry_date'), created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # 迁移allocation_history
            for history_item in data.get('allocation_history', []):
                network_id: int | None = networks_map.get(history_item.get('network'))
                if not network_id:
                    continue
                
                _ = cursor.execute('''
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
    
    def get_most_specific_network(self, ip_address: str) -> dict[str, Any] | None:
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
        most_specific_network: dict[str, Any] | None = None
        max_prefix_len = 0
        
        for network in network_rows:
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
            
            for ip in ips:
                try:
                    ip_obj = ipaddress.ip_address(ip[2])
                    if ip_obj in ip_network:
                        # 检查是否是更具体的网络
                        _ = cursor.execute('SELECT network_address FROM networks WHERE id = ?', (ip[1],))
                        current_network_row = cursor.fetchone()
                        if current_network_row:
                            current_network_obj = ipaddress.ip_network(current_network_row[0])
                            if ip_network.prefixlen > current_network_obj.prefixlen:
                                # 更新归属关系
                                _ = cursor.execute('UPDATE ip_addresses SET network_id = ? WHERE id = ?', (network_id, ip[0]))
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
                _ = conn.execute('BEGIN EXCLUSIVE')
                
                # 检查IP地址是否已存在
                _ = cursor.execute('SELECT id, status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                ip_row = cursor.fetchone()
                
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                success_result = None
                if ip_row:
                    # IP地址已存在
                    ip_id, status = ip_row
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
    
    def get_network_ips(self, network_str: str) -> list[dict[str, Any]]:
        """获取网络及其所有子网络的IP地址
        
        Args:
            network_str: 网络地址（CIDR格式）
        
        Returns:
            list[dict]: IP地址列表
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
                except Exception:
                    pass
            
            return relevant_ips
        except Exception:
            return []
    
    def get_all_networks(self) -> list[dict[str, Any]]:
        """获取所有网络
        
        Returns:
            list[dict]: 网络列表
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
        ip_objects = []
        for ip in all_ips:
            try:
                ip_obj = ipaddress.ip_address(ip[0])
                ip_objects.append(ip_obj)
            except Exception:
                pass
        
        network_list = []
        for network in network_rows:
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
                _ = cursor.execute('SELECT ip_address FROM ip_addresses')
                ips = cursor.fetchall()
                
                conn.close()
                
                for ip in ips:
                    try:
                        ip_obj = ipaddress.ip_address(ip[0])
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
            
            # 查找IP地址
            _ = cursor.execute('SELECT id, network_id, status FROM ip_addresses WHERE ip_address = ?', (ip_address,))
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
            _ = cursor.execute('UPDATE ip_addresses SET status = ?, updated_at = ? WHERE id = ?', ('available', now, ip_id))
            
            # 记录释放历史
            _ = cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'release', 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址释放成功"
        except Exception as e:
            return False, f"释放IP地址失败: {str(e)}"
    
    def delete_ip_by_id(self, ip_id: int) -> tuple[bool, str]:
        """根据ID删除IP地址记录
        
        Args:
            ip_id: IP地址记录ID
            
        Returns:
            tuple[bool, str]: (是否删除成功, 错误信息)
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取IP地址信息用于历史记录
            cursor.execute('SELECT ip_address, network_id FROM ip_addresses WHERE id = ?', (ip_id,))
            ip_row = cursor.fetchone()
            if not ip_row:
                conn.close()
                return False, "IP地址记录不存在"
            
            ip_address = ip_row[0]
            network_id = ip_row[1]
            
            # 删除IP地址记录
            cursor.execute('DELETE FROM ip_addresses WHERE id = ?', (ip_id,))
            
            # 记录删除历史
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
            INSERT INTO allocation_history (network_id, ip_address, action, performed_by, performed_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (network_id, ip_address, 'delete_conflict', 'admin', now))
            
            conn.commit()
            conn.close()
            return True, "IP地址记录删除成功"
        except Exception as e:
            return False, f"删除IP地址记录失败: {str(e)}"
    
    def get_ip_info(self, ip_address: str) -> dict[str, Any] | None:
        """获取IP地址信息
        
        Args:
            ip_address: IP地址
        
        Returns:
            dict or None: IP地址信息，包含hostname, description等字段，失败返回None
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查询IP地址信息
            _ = cursor.execute('SELECT hostname, description, network_id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
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
            if not ip_row:
                conn.close()
                return False, "IP地址不存在"
            
            ip_id, network_id = ip_row
            
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

    def update_ip_expiry(self, ip_address: str, expiry_date: str | None):
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
                _ = cursor.execute('SELECT id, network_id, hostname, description FROM ip_addresses WHERE ip_address = ?', (ip_address,))
                ip_row = cursor.fetchone()
                if not ip_row:
                    return False, "IP地址不存在"
                
                ip_id, network_id, hostname, description = ip_row
                
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
            tuple: (bool, str, int) - (是否更新成功, 错误信息, 更新的IP数量)
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
                    if not ip_row:
                        continue
                    
                    ip_id, network_id, hostname, description = ip_row
                    
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
            for ip in available_ips:
                _, network_id, ip_address = ip
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
            
            if result:
                return result[0]
            return 'available'
        except Exception:
            return 'available'
    
    def get_expired_ips(self) -> list[dict[str, Any]]:
        """获取所有过期的IP地址
        
        Returns:
            list[dict]: 过期IP地址列表
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
            
            expired_ips = []
            for row in cursor.fetchall():
                expired_ips.append({
                    'id': row[0],
                    'network_id': row[1],
                    'ip_address': row[2],
                    'status': row[3],
                    'hostname': row[4],
                    'description': row[5],
                    'allocated_at': row[6],
                    'expiry_date': row[7]
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
    
    def get_expiring_ips(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        """获取即将过期的IP地址
        
        Args:
            days_ahead: 提前多少天提醒
        
        Returns:
            list[dict]: 即将过期的IP地址列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 计算日期范围
            now = datetime.now()
            future_date = now + datetime.timedelta(days=days_ahead)
            
            # 获取即将过期的IP地址
            _ = cursor.execute('''
            SELECT id, network_id, ip_address, status, hostname, description, allocated_at, expiry_date 
            FROM ip_addresses 
            WHERE expiry_date BETWEEN ? AND ? AND status IN ('allocated', 'reserved')
            ''', (now.strftime("%Y-%m-%d %H:%M:%S"), future_date.strftime("%Y-%m-%d %H:%M:%S")))
            
            expiring_ips = []
            for row in cursor.fetchall():
                expiring_ips.append({
                    'id': row[0],
                    'network_id': row[1],
                    'ip_address': row[2],
                    'status': row[3],
                    'hostname': row[4],
                    'description': row[5],
                    'allocated_at': row[6],
                    'expiry_date': row[7]
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
            _ = cursor.execute('SELECT id FROM ip_addresses WHERE ip_address = ?', (ip_address,))
            ip_row = cursor.fetchone()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if ip_row:
                # 更新IP地址状态
                _ = cursor.execute('UPDATE ip_addresses SET status = ?, description = ?, updated_at = ? WHERE id = ?', 
                             ('reserved', description, now, ip_row[0]))
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
                cursor.execute('SELECT id FROM networks WHERE network_address = ?', (old_network_str,))
                network_row = cursor.fetchone()
                if not network_row:
                    return False, "旧网络不存在"
                
                # 检查新网络是否已存在
                cursor.execute('SELECT id FROM networks WHERE network_address = ? AND id != ?', (new_network_str, network_row[0]))
                existing_row = cursor.fetchone()
                if existing_row:
                    return False, "新网络地址已存在"
                
                # 更新网络地址
                cursor.execute('UPDATE networks SET network_address = ?, updated_at = datetime("now") WHERE id = ?', 
                             (new_network_str, network_row[0]))
                
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
            if not network_row:
                conn.close()
                return False, "网络不存在"
            
            network_id = network_row[0]
            
            # 检查网络是否有IP地址
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE network_id = ?', (network_id,))
            ip_count = cursor.fetchone()[0]
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
            dict: 整体统计信息
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取网络总数
            _ = cursor.execute('SELECT COUNT(*) FROM networks')
            total_networks = cursor.fetchone()[0]
            
            # 获取IP总数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses')
            total_ips = cursor.fetchone()[0]
            
            # 获取已分配IP数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE status = ?', ('allocated',))
            allocated_ips = cursor.fetchone()[0]
            
            # 获取已保留IP数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE status = ?', ('reserved',))
            reserved_ips = cursor.fetchone()[0]
            
            # 获取过期IP数，包括allocated和reserved状态
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE expiry_date < ? AND status IN ("allocated", "reserved")', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))
            expired_ips = cursor.fetchone()[0]
            
            # 获取IPv4和IPv6网络数
            _ = cursor.execute('SELECT network_address FROM networks')
            network_rows = cursor.fetchall()
            ipv4_networks = 0
            ipv6_networks = 0
            
            for network in network_rows:
                try:
                    ip_network = ipaddress.ip_network(network[0])
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
    
    def check_ip_conflict(self, ip_address: str) -> bool:
        """检查IP地址是否存在冲突
        
        Args:
            ip_address: IP地址
            
        Returns:
            bool: True表示存在冲突，False表示无冲突
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 查询IP地址的分配情况，统计非available状态的记录数
            _ = cursor.execute('SELECT COUNT(*) FROM ip_addresses WHERE ip_address = ? AND status != ?', (ip_address, 'available'))
            count = cursor.fetchone()[0]
            
            conn.close()
            
            # 如果IP地址被分配多次（ count > 1 ），则存在冲突
            return count > 1
        except Exception:
            return False

    def backup_data(self, backup_name: str | None = None, backup_type: str = 'auto', frequency: str = 'hourly', compress: bool = False, encrypt: bool = False):
        """备份IPAM数据
        
        Args:
            backup_name: 可选的备份名称，如果不提供则使用时间戳
            backup_type: 备份类型，可选值：'auto'（自动备份）、'manual'（手动备份）、'before_import'（导入前备份）、'before_operation'（操作前备份）
            frequency: 备份频率，可选值：'hourly'（每小时）、'daily'（每天）、'weekly'（每周）、'monthly'（每月）
            compress: 是否压缩备份文件
            encrypt: 是否加密备份文件
            
        Returns:
            str: 备份文件路径
        """
        try:
            # 检查是否需要自动备份
            if backup_type == 'auto':
                # 使用统一的备份配置文件
                backup_config_file = os.path.join(self.backup_dir, 'backup_config.json')
                last_backup_time = None
                last_backup_frequency = None
                
                # 加载配置文件
                if os.path.exists(backup_config_file):
                    try:
                        with open(backup_config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            last_backup_time = config.get('last_backup_time')
                            last_backup_frequency = config.get('last_backup_frequency')
                    except Exception:
                        pass
                
                # 检查备份间隔
                if last_backup_time:
                    try:
                        last_backup = datetime.fromisoformat(last_backup_time)
                        # 根据当前频率确定备份间隔
                        if frequency == 'hourly':
                            if (datetime.now() - last_backup).total_seconds() < 3600:  # 1小时
                                return None  # 不需要备份
                        elif frequency == 'daily':
                            if (datetime.now() - last_backup).total_seconds() < 86400:  # 24小时
                                return None  # 不需要备份
                        elif frequency == 'weekly':
                            if (datetime.now() - last_backup).total_seconds() < 604800:  # 7天
                                return None  # 不需要备份
                        elif frequency == 'monthly':
                            if (datetime.now() - last_backup).total_seconds() < 2592000:  # 30天
                                return None  # 不需要备份
                    except Exception:
                        pass
                
                # 更新最后备份时间和频率
                config = {
                    'last_backup_time': datetime.now().isoformat(),
                    'last_backup_frequency': frequency
                }
                
                # 保存配置文件
                with open(backup_config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            
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
            _ = cursor.execute('SELECT network_address, description, created_at, updated_at FROM networks')
            networks_rows = cursor.fetchall()
            
            export_networks = {}
            for row in networks_rows:
                network_address, description, created_at, _ = row
                export_networks[network_address] = {
                    'description': description,
                    'ip_addresses': {},
                    'created_at': created_at
                }
                
                # 获取该网络的IP地址
                _ = cursor.execute('SELECT ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at FROM ip_addresses WHERE network_id = (SELECT id FROM networks WHERE network_address = ?)', (network_address,))
                ips_rows = cursor.fetchall()
                
                for ip_row in ips_rows:
                    ip_address, status, hostname, ip_description, allocated_at, allocated_by, expiry_date, _, _ = ip_row
                    export_networks[network_address]['ip_addresses'][ip_address] = {
                        'status': status,
                        'hostname': hostname,
                        'description': ip_description,
                        'allocated_at': allocated_at,
                        'allocated_by': allocated_by,
                        'expiry_date': expiry_date
                    }
            
            # 获取分配历史
            _ = cursor.execute('SELECT network_id, ip_address, action, hostname, description, performed_by, performed_at FROM allocation_history')
            history_rows = cursor.fetchall()
            
            allocation_history = []
            for row in history_rows:
                network_id, ip_address, action, hostname, description, performed_by, performed_at = row
                
                # 获取网络地址
                _ = cursor.execute('SELECT network_address FROM networks WHERE id = ?', (network_id,))
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
                'networks': export_networks,
                'allocation_history': allocation_history,
                'backup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'backup_name': backup_name,
                'backup_type': backup_type,
                'backup_frequency': frequency,
                'backup_version': '1.2',
                'network_count': len(export_networks),
                'ip_count': sum(len(net['ip_addresses']) for net in export_networks.values()),
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
            self._cleanup_old_backups(keep=10)
            
            return backup_path
        except Exception:
            return None
    
    def _cleanup_old_backups(self, keep: int = 10):
        """清理旧备份文件，保留指定数量的最新备份
        
        Args:
            keep: 要保留的备份文件数量
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
            
            # 删除多余的备份文件
            for i in range(keep, len(backup_files)):
                try:
                    os.remove(backup_files[i][1])
                except Exception:
                    pass
        except Exception:
            pass
    
    def import_data(self, import_file: str, format: str = 'json') -> bool:
        """导入IPAM数据
        
        Args:
            import_file: 导入文件路径
            format: 导入格式，可选值：'json'、'csv'
        
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
                _ = conn.execute('BEGIN TRANSACTION')
                
                # 清空现有数据
                _ = cursor.execute('DELETE FROM allocation_history')
                _ = cursor.execute('DELETE FROM ip_addresses')
                _ = cursor.execute('DELETE FROM networks')
                
                # 导入网络数据
                networks_map = {}
                for network_str, network_data in data.get('networks', {}).items():
                    created_at = network_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    _ = cursor.execute('''
                    INSERT INTO networks (network_address, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ''', (network_str, network_data.get('description', ''), created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    networks_map[network_str] = cursor.lastrowid
                
                # 导入IP地址数据
                for network_str, network_data in data.get('networks', {}).items():
                    network_id = networks_map.get(network_str)
                    if not network_id:
                        continue
                    
                    for ip_str, ip_data in network_data.get('ip_addresses', {}).items():
                        created_at = ip_data.get('allocated_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        _ = cursor.execute('''
                        INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                        allocated_at, allocated_by, expiry_date, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (network_id, ip_str, ip_data.get('status', 'available'), 
                              ip_data.get('hostname', ''), ip_data.get('description', ''),
                              ip_data.get('allocated_at'), ip_data.get('allocated_by'),
                              ip_data.get('expiry_date'), created_at, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                # 导入分配历史数据
                for history_item in data.get('allocation_history', []):
                    network_str = history_item.get('network', '')
                    network_id = networks_map.get(network_str)
                    if not network_id:
                        continue
                    
                    _ = cursor.execute('''
                    INSERT INTO allocation_history (network_id, ip_address, action, hostname, description, 
                    performed_by, performed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (network_id, history_item.get('ip_address'), history_item.get('action'),
                          history_item.get('hostname'), history_item.get('description'),
                          history_item.get('performed_by'), history_item.get('timestamp')))
                
                # 提交事务
                conn.commit()
                conn.close()
            elif format == 'csv':
                # 从CSV文件导入
                with open(import_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    conn = sqlite3.connect(self.db_file)
                    cursor = conn.cursor()
                    
                    # 开始事务
                    _ = conn.execute('BEGIN TRANSACTION')
                    
                    # 清空现有数据
                    _ = cursor.execute('DELETE FROM allocation_history')
                    _ = cursor.execute('DELETE FROM ip_addresses')
                    _ = cursor.execute('DELETE FROM networks')
                    
                    # 导入数据
                    networks_set = set()
                    for row in reader:
                        network_str = row.get('Network', '')
                        ip_str = row.get('IP Address', '')
                        status = row.get('Status', '')
                        hostname = row.get('Hostname', '')
                        description = row.get('Description', '')
                        allocated_at = row.get('Allocated At', '')
                        allocated_by = row.get('Allocated By', '')
                        
                        if network_str and network_str not in networks_set:
                            networks_set.add(network_str)
                            _ = cursor.execute('''
                            INSERT INTO networks (network_address, description, created_at, updated_at)
                            VALUES (?, ?, ?, ?)
                            ''', (network_str, '', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                        
                        if ip_str:
                            # 获取网络ID
                            _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network_str,))
                            network_row = cursor.fetchone()
                            if network_row:
                                network_id = network_row[0]
                                _ = cursor.execute('''
                                INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, 
                                allocated_at, allocated_by, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (network_id, ip_str, status, hostname, description, 
                                      allocated_at, allocated_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    
                    # 提交事务
                    conn.commit()
                    conn.close()
            else:
                return False
            
            return True
        except Exception:
            return False
    
    def export_data(self, export_file: str, format: str = 'json', networks: list = None) -> bool:
        """导出IPAM数据
        
        Args:
            export_file: 导出文件路径
            format: 导出格式，可选值：'json'、'csv'
            networks: 要导出的网络列表，如果为None则导出所有网络
        
        Returns:
            bool: 是否导出成功
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            if format == 'json':
                # 导出为JSON格式
                # 获取网络数据
                if networks:
                    # 只获取指定的网络
                    placeholders = ','.join(['?'] * len(networks))
                    _ = cursor.execute(f'SELECT network_address, description, created_at, updated_at FROM networks WHERE network_address IN ({placeholders})', networks)
                else:
                    # 获取所有网络
                    _ = cursor.execute('SELECT network_address, description, created_at, updated_at FROM networks')
                
                networks_rows = cursor.fetchall()
                
                export_networks = {}
                for row in networks_rows:
                    network_address, description, created_at, _ = row
                    export_networks[network_address] = {
                        'description': description,
                        'ip_addresses': {},
                        'created_at': created_at
                    }
                    
                    # 获取该网络的IP地址
                    _ = cursor.execute('SELECT ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at FROM ip_addresses WHERE network_id = (SELECT id FROM networks WHERE network_address = ?)', (network_address,))
                    ips_rows = cursor.fetchall()
                    
                    for ip_row in ips_rows:
                        ip_address, status, hostname, ip_description, allocated_at, allocated_by, expiry_date, _, _ = ip_row
                        export_networks[network_address]['ip_addresses'][ip_address] = {
                            'status': status,
                            'hostname': hostname,
                            'description': ip_description,
                            'allocated_at': allocated_at,
                            'allocated_by': allocated_by,
                            'expiry_date': expiry_date
                        }
                
                # 获取分配历史
                if networks:
                    # 只获取指定网络的历史
                    network_ids = []
                    for network in networks:
                        _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network,))
                        network_row = cursor.fetchone()
                        if network_row:
                            network_ids.append(network_row[0])
                    
                    if network_ids:
                        placeholders = ','.join(['?'] * len(network_ids))
                        _ = cursor.execute(f'SELECT network_id, ip_address, action, hostname, description, performed_by, performed_at FROM allocation_history WHERE network_id IN ({placeholders})', network_ids)
                    else:
                        history_rows = []
                else:
                    # 获取所有历史
                    _ = cursor.execute('SELECT network_id, ip_address, action, hostname, description, performed_by, performed_at FROM allocation_history')
                
                if not networks or network_ids:
                    history_rows = cursor.fetchall()
                
                allocation_history = []
                for row in history_rows:
                    network_id, ip_address, action, hostname, description, performed_by, performed_at = row
                    
                    # 获取网络地址
                    _ = cursor.execute('SELECT network_address FROM networks WHERE id = ?', (network_id,))
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
                
                data = {
                    'networks': export_networks,
                    'allocation_history': allocation_history,
                    'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'export_version': '1.2',
                    'network_count': len(export_networks),
                    'ip_count': sum(len(net['ip_addresses']) for net in export_networks.values())
                }
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif format == 'csv':
                # 导出为CSV格式
                with open(export_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # 写入表头
                    writer.writerow(['Network', 'IP Address', 'Status', 'Hostname', 'Description', 'Allocated At', 'Allocated By', 'Expiry Date'])
                    
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
                                ip_data.get('allocated_by', ''),
                                ip_data.get('expiry_date', '')
                            ])
            else:
                return False
            
            conn.close()
            return True
        except Exception:
            return False
    
    def get_allocation_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """获取分配历史记录
        
        Args:
            limit: 返回记录数量限制
        
        Returns:
            list[dict]: 分配历史记录列表
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 获取分配历史记录
            _ = cursor.execute('''
            SELECT a.network_id, a.ip_address, a.action, a.hostname, a.description, a.performed_by, a.performed_at, n.network_address
            FROM allocation_history a
            JOIN networks n ON a.network_id = n.id
            ORDER BY a.performed_at DESC
            LIMIT ?
            ''', (limit,))
            
            history = []
            for row in cursor.fetchall():
                _, ip_address, action, hostname, description, performed_by, performed_at, network_address = row
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
    

    
    def get_network_by_id(self, network_id: int) -> Dict[str, Any] | None:
        """通过ID获取网络信息
        
        Args:
            network_id: 网络ID
        
        Returns:
            dict: 网络信息，或None
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            _ = cursor.execute('SELECT id, network_address, description, created_at, updated_at FROM networks WHERE id = ?', (network_id,))
            network_row = cursor.fetchone()
            
            conn.close()
            
            if network_row:
                return {
                    'id': network_row[0],
                    'network_address': network_row[1],
                    'description': network_row[2],
                    'created_at': network_row[3],
                    'updated_at': network_row[4]
                }
            return None
        except Exception:
            return None
    
    def get_ip_by_id(self, ip_id: int) -> Dict[str, Any] | None:
        """通过ID获取IP地址信息
        
        Args:
            ip_id: IP地址ID
        
        Returns:
            dict: IP地址信息，或None
        """
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            _ = cursor.execute('''
            SELECT i.id, i.network_id, i.ip_address, i.status, i.hostname, i.description, i.allocated_at, i.allocated_by, i.expiry_date, i.created_at, i.updated_at, n.network_address
            FROM ip_addresses i
            JOIN networks n ON i.network_id = n.id
            WHERE i.id = ?
            ''', (ip_id,))
            ip_row = cursor.fetchone()
            
            conn.close()
            
            if ip_row:
                return {
                    'id': ip_row[0],
                    'network_id': ip_row[1],
                    'network': ip_row[11],
                    'ip_address': ip_row[2],
                    'status': ip_row[3],
                    'hostname': ip_row[4],
                    'description': ip_row[5],
                    'allocated_at': ip_row[6],
                    'allocated_by': ip_row[7],
                    'expiry_date': ip_row[8],
                    'created_at': ip_row[9],
                    'updated_at': ip_row[10]
                }
            return None
        except Exception:
            return None
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份文件
        
        Returns:
            list[dict]: 备份文件列表，每个元素包含备份文件的信息
        """
        try:
            backups = []
            
            # 检查备份目录是否存在
            if not os.path.exists(self.backup_dir):
                return backups
            
            # 遍历备份目录中的所有文件
            for filename in os.listdir(self.backup_dir):
                if (filename.startswith('ipam_backup_') or filename.startswith('ipam_bak_')) and (filename.endswith('.json') or filename.endswith('.zip')):
                    file_path = os.path.join(self.backup_dir, filename)
                    
                    # 获取文件修改时间
                    file_mtime = os.path.getmtime(file_path)
                    backup_time = datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 尝试从备份文件中读取网络数和IP数
                    network_count = 0
                    ip_count = 0
                    
                    try:
                        if filename.endswith('.zip'):
                            # 处理压缩备份文件
                            with zipfile.ZipFile(file_path, 'r') as zipf:
                                if 'ipam_data.json' in zipf.namelist():
                                    with zipf.open('ipam_data.json') as f:
                                        data = json.load(f)
                                        network_count = data.get('network_count', 0)
                                        ip_count = data.get('ip_count', 0)
                        else:
                            # 处理普通JSON备份文件
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                network_count = data.get('network_count', 0)
                                ip_count = data.get('ip_count', 0)
                    except Exception:
                        # 如果无法读取文件内容，使用默认值
                        pass
                    
                    # 添加备份信息到列表，使用与windows_app.py期望的格式一致
                    backups.append({
                        'filename': filename,
                        'file_path': file_path,
                        'info': {
                            'backup_time': backup_time,
                            'network_count': network_count,
                            'ip_count': ip_count
                        }
                    })
            
            # 按备份时间降序排序
            backups.sort(key=lambda x: x['info']['backup_time'], reverse=True)
            
            return backups
        except Exception:
            return []


if __name__ == "__main__":
    # 测试IPAMSQLite类
    ipam = IPAMSQLite()
    
    # 测试添加网络
    # result = ipam.add_network('192.168.1.0/24', '测试网络')
    # print(f"添加网络结果: {result}")
    
    # 测试分配IP
    # result = ipam.allocate_ip('192.168.1.0/24', '192.168.1.100', 'test-host', '测试主机')
    # print(f"分配IP结果: {result}")
    
    # 测试获取网络IP
    # ips = ipam.get_network_ips('192.168.1.0/24')
    # print(f"网络IP地址: {ips}")
    
    # 测试获取所有网络
    # networks = ipam.get_all_networks()
    # print(f"所有网络: {networks}")
    
    # 测试释放IP
    # result = ipam.release_ip('192.168.1.100')
    # print(f"释放IP结果: {result}")
    
    # 测试备份数据
    # backup_path = ipam.backup_data()
    # print(f"备份路径: {backup_path}")
    
    # 测试导入数据
    # result = ipam.import_data('ipam_data.json')
    # print(f"导入数据结果: {result}")
    
    # 测试导出数据
    # result = ipam.export_data('ipam_export.json', 'json')
    # print(f"导出数据结果: {result}")
    
    # 测试获取整体统计信息
    # stats = ipam.get_overall_stats()
    # print(f"整体统计信息: {stats}")
    
    print("IPAMSQLite类测试完成")
