#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试IP释放功能
"""

import sqlite3
import os

# 数据库文件路径
db_file = os.path.join(os.path.dirname(__file__), 'ipam_data.db')

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 查询10.0.0.1的状态
cursor.execute('SELECT id, status FROM ip_addresses WHERE ip_address = ?', ('10.0.0.1',))
rows = cursor.fetchall()

print('IP 10.0.0.1 的状态:')
for row in rows:
    print(f'ID: {row[0]}, 状态: {row[1]}')

# 关闭连接
conn.close()
