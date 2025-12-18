#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查代码中的冗余部分
"""

import re

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print("=== 代码冗余检查 ===")

# 1. 检查重复的代码块
print("\n1. 检查重复的代码块:")

# 定义代码块的大小（行数）
block_size = 5

# 存储代码块及其出现的位置
code_blocks = {}

# 遍历所有行，创建代码块
for i in range(len(lines) - block_size + 1):
    # 创建当前代码块
    block = tuple(lines[i:i+block_size])
    # 计算代码块的哈希值
    block_hash = hash(block)
    # 存储代码块的位置
    if block_hash not in code_blocks:
        code_blocks[block_hash] = []
    code_blocks[block_hash].append(i+1)  # 记录起始行号

# 找出重复的代码块
repeated_blocks = {hash_val: positions for hash_val, positions in code_blocks.items() if len(positions) > 1}

if repeated_blocks:
    print(f"找到 {len(repeated_blocks)} 个重复的代码块:")
    
    # 显示前5个重复的代码块
    count = 0
    for block_hash, positions in repeated_blocks.items():
        if count >= 5:
            break
        count += 1
        
        # 获取代码块内容
        block = tuple(lines[positions[0]-1:positions[0]-1+block_size])
        
        print(f"\n代码块 {count} 重复出现在行: {', '.join(map(str, positions))}")
        print("代码内容:")
        for line in block:
            print(f"  {line}")
else:
    print("未找到重复的代码块")

# 2. 检查过长的函数
print("\n2. 检查过长的函数:")

# 定义函数长度阈值
function_length_threshold = 50

# 查找函数定义及其长度
function_defs = []

for i, line in enumerate(lines, 1):
    if re.match(r'^\s*def\s+', line):
        function_name = line.strip().split()[1].split('(')[0]
        # 计算函数长度
        end_line = len(lines)
        for j in range(i, len(lines)):
            if re.match(r'^\s*(def\s+|class\s+)', lines[j]):
                end_line = j
                break
        function_length = end_line - i
        function_defs.append((function_name, i, function_length))

# 找出过长的函数
long_functions = [func for func in function_defs if func[2] > function_length_threshold]

if long_functions:
    print(f"找到 {len(long_functions)} 个过长的函数（超过 {function_length_threshold} 行）:")
    for func_name, start_line, length in long_functions[:5]:
        print(f"  - {func_name}（第 {start_line} 行，共 {length} 行）")
else:
    print("未找到过长的函数")

# 3. 检查重复的条件判断
print("\n3. 检查重复的条件判断:")

# 存储条件判断及其出现的位置
condition_counts = {}

for i, line in enumerate(lines, 1):
    # 查找条件判断行
    if re.match(r'^\s*(if\s+|elif\s+|while\s+)', line):
        # 提取条件部分
        condition = line.strip().split(':', 1)[0]
        condition_counts[condition] = condition_counts.get(condition, 0) + 1

# 找出重复的条件判断
repeated_conditions = {cond: count for cond, count in condition_counts.items() if count > 1}

if repeated_conditions:
    print(f"找到 {len(repeated_conditions)} 个重复的条件判断:")
    # 按重复次数排序，显示前5个
    sorted_conditions = sorted(repeated_conditions.items(), key=lambda x: x[1], reverse=True)
    for cond, count in sorted_conditions[:5]:
        print(f"  - '{cond}' 出现 {count} 次")
else:
    print("未找到重复的条件判断")

print("\n=== 检查完成 ===")
