#!/usr/bin/env python3
# 修复文件末尾的空行问题

# 读取整个文件内容
with open('update_version.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 移除末尾的空行
while lines and lines[-1].strip() == '':
    _ = lines.pop()  # 使用下划线变量接收未使用的返回值

# 确保最后一行以换行符结束
if lines and not lines[-1].endswith('\n'):
    lines[-1] += '\n'

# 重新写入文件
with open('update_version.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ 已修复update_version.py末尾的空行问题")
