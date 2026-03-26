#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试IP释放功能的详细信息
"""

import sqlite3
import os

# 数据库文件路径
db_file = os.path.join(os.path.dirname(__file__), 'ipam_data.db')

# 连接数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 查询10.0.0.1的详细信息
cursor.execute('SELECT * FROM ip_addresses WHERE ip_address = ?', ('10.0.0.1',))
rows = cursor.fetchall()

print('IP 10.0.0.1 的详细信息:')
print('ID | network_id | ip_address | status | hostname | description | allocated_at | allocated_by | expiry_date | created_at | updated_at')
print('-' * 120)
for row in rows:
    # 处理None值
    row_data = [str(col) if col is not None else '' for col in row]
    print(f'{row_data[0]:3} | {row_data[1]:10} | {row_data[2]:10} | {row_data[3]:9} | {row_data[4]:12} | {row_data[5]:15} | {row_data[6]:19} | {row_data[7]:12} | {row_data[8]:11} | {row_data[9]:19} | {row_data[10]:19}')

# 关闭连接
conn.close()
