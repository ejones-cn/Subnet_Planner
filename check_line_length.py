#!/usr/bin/env python3
import sys
import os

def check_line_length(filename=None, max_length=100) -> list:
    """检查文件中行长度超过指定值的行
    
    参数:
        filename: 要检查的文件名，默认为 None
        max_length: 最大行长度，默认为 100
    
    返回:
        list: 违规行的列表，每个元素包含行号、长度和内容
    """
    # 设置默认文件名
    if filename is None:
        # 从当前目录自动检测Python文件
        python_files = [f for f in os.listdir('.') if f.endswith('.py')]
        if python_files:
            # 优先选择 ipam_sqlite.py，如果不存在则选择第一个Python文件
            if 'ipam_sqlite.py' in python_files:
                filename = 'ipam_sqlite.py'
            else:
                filename = python_files[0]
            print(f'自动检测到Python文件: {filename}')
        else:
            # 如果没有找到Python文件，使用默认值
            filename = 'ipam_sqlite.py'
            print(f'未检测到Python文件，使用默认值: {filename}')
    
    violations = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if len(line) > max_length:
                    violation = {
                        'line': i,
                        'length': len(line),
                        'content': line.strip()
                    }
                    violations.append(violation)
                    print(f'Line {i}: {len(line)} characters')
                    print(f'Content: {line.strip()}')
                    print()
    except FileNotFoundError:
        print(f'错误：文件 {filename} 不存在')
    except PermissionError:
        print(f'错误：没有权限读取文件 {filename}')
    return violations

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else 'ipam_sqlite.py'
    violations = check_line_length(filename)
    if not violations:
        print(f'文件 {filename} 中没有超过 100 字符的行')
    else:
        print(f'文件 {filename} 中共有 {len(violations)} 行超过 100 字符')
