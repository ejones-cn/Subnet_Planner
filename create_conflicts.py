#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建IP冲突数据脚本
用于向数据库中插入冲突的IP地址，以便验证冲突检查功能
"""

import sqlite3
import os
from datetime import datetime

# 数据库文件路径
db_file = os.path.join(os.path.dirname(__file__), 'ipam_data.db')


def init_database():
    """初始化数据库表结构"""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 创建networks表
    _ = cursor.execute('''
        CREATE TABLE IF NOT EXISTS networks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_address TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # 检查ip_addresses表是否存在
    _ = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ip_addresses'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        # 检查表结构，看ip_address是否有唯一约束
        _ = cursor.execute("PRAGMA table_info(ip_addresses)")
        columns = cursor.fetchall()
        ip_address_column = next((col for col in columns if col[1] == 'ip_address'), None)
        
        if ip_address_column and ip_address_column[3] == 1:  # 1表示有唯一约束
            # 如果有唯一约束，需要重新创建表
            print("检测到ip_address字段有唯一约束，正在修改表结构...")
            # 创建临时表
            _ = cursor.execute('''
                CREATE TABLE IF NOT EXISTS ip_addresses_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    network_id INTEGER NOT NULL,
                    ip_address TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'available',
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
            
            # 复制数据
            _ = cursor.execute('''
                INSERT INTO ip_addresses_temp (id, network_id, ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at)
                SELECT id, network_id, ip_address, status, hostname, description, allocated_at, allocated_by, expiry_date, created_at, updated_at
                FROM ip_addresses
            ''')
            
            # 删除原表
            _ = cursor.execute('DROP TABLE ip_addresses')
            
            # 重命名临时表
            _ = cursor.execute('ALTER TABLE ip_addresses_temp RENAME TO ip_addresses')
    else:
        # 创建ip_addresses表
        _ = cursor.execute('''
            CREATE TABLE IF NOT EXISTS ip_addresses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                network_id INTEGER NOT NULL,
                ip_address TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'available',
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
    
    # 创建索引以提高查询性能
    _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_ip ON ip_addresses (ip_address)')
    _ = cursor.execute('CREATE INDEX IF NOT EXISTS idx_ip_addresses_network ON ip_addresses (network_id)')
    
    conn.commit()
    conn.close()


def create_conflicts():
    """创建冲突的IP地址数据"""
    try:
        # 初始化数据库
        init_database()
        
        # 连接数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 确保网络存在
        network1 = '192.168.1.0/24'
        network2 = '10.0.0.0/24'
        
        # 插入网络1
        _ = cursor.execute('''
            INSERT OR IGNORE INTO networks (network_address, description, created_at)
            VALUES (?, ?, ?)
        ''', (network1, '测试网络1', datetime.now().isoformat()))
        
        # 插入网络2
        _ = cursor.execute('''
            INSERT OR IGNORE INTO networks (network_address, description, created_at)
            VALUES (?, ?, ?)
        ''', (network2, '测试网络2', datetime.now().isoformat()))
        
        # 获取网络ID
        _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network1,))
        network1_id = cursor.fetchone()[0]
        
        _ = cursor.execute('SELECT id FROM networks WHERE network_address = ?', (network2,))
        network2_id = cursor.fetchone()[0]
        
        # 创建冲突的IP地址
        conflict_ips = {
            network1_id: ['192.168.1.100', '192.168.1.101', '192.168.1.102'],
            network2_id: ['10.0.0.1', '10.0.0.2', '10.0.0.3']
        }
        
        # 为每个IP地址创建多个分配记录
        for net_id, ips in conflict_ips.items():
            for ip in ips:
                now = datetime.now().isoformat()
                # 第一条记录
                _ = cursor.execute('''
                    INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, allocated_at, allocated_by, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (net_id, ip, 'allocated', f'Host-{ip}', '第一次分配', now, 'admin', now, now))
                
                # 第二条记录（冲突）
                _ = cursor.execute('''
                    INSERT INTO ip_addresses (network_id, ip_address, status, hostname, description, allocated_at, allocated_by, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (net_id, ip, 'allocated', f'Conflict-{ip}', '第二次分配（冲突）', now, 'admin', now, now))
        
        # 提交事务
        conn.commit()
        conn.close()
        
        print("成功创建冲突数据！")
        print(f"在网络 {network1} 中为以下IP地址创建了冲突：")
        for ip in conflict_ips[network1_id]:
            print(f"- {ip}")
        print(f"在网络 {network2} 中为以下IP地址创建了冲突：")
        for ip in conflict_ips[network2_id]:
            print(f"- {ip}")
        print("现在可以使用检查冲突功能来验证这些冲突。")
        
    except Exception as e:
        print(f"创建冲突数据失败: {e}")



if __name__ == "__main__":
    create_conflicts()
