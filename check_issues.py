#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查代码中的常见问题
"""

import ast
import re

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析代码
try:
    tree = ast.parse(content)
except SyntaxError as e:
    print(f"语法错误: {e}")
    exit(1)

lines = content.split('\n')
print("=== 代码问题检查结果 ===")

issues = []

# 1. 检查未使用的函数参数
def check_unused_params():
    """检查未使用的函数参数"""
    class ParamVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            # 收集函数内使用的变量
            used_vars = set()
            
            class NameCollector(ast.NodeVisitor):
                def visit_Name(self, node):
                    if isinstance(node.ctx, ast.Load):
                        used_vars.add(node.id)
            
            collector = NameCollector()
            collector.visit(node)
            
            # 检查参数是否被使用
            for arg in node.args.args:
                if arg.arg not in used_vars and arg.arg != 'self':  # 忽略self参数
                    issues.append(f"第 {node.lineno} 行: 函数 {node.name} 有未使用的参数 {arg.arg}")
    
    ParamVisitor().visit(tree)

# 2. 检查重复的代码行
def check_repeated_lines():
    """检查重复的代码行"""
    line_counts = {}
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped and len(stripped) > 20:  # 只检查有意义的长行
            line_counts[stripped] = line_counts.get(stripped, []) + [i]
    
    repeated_lines = [lines for lines in line_counts.values() if len(lines) > 1]
    
    for line_nums in repeated_lines[:10]:  # 只显示前10个
        line_content = lines[line_nums[0]-1].strip()
        issues.append(f"重复的代码行: 行 {', '.join(map(str, line_nums))}: {line_content[:60]}...")

# 3. 检查长行
def check_long_lines():
    """检查长行"""
    for i, line in enumerate(lines, 1):
        if len(line) > 120:  # 超过120个字符的长行
            issues.append(f"第 {i} 行: 长行 ({len(line)} 字符)")

# 4. 检查注释掉的代码
def check_commented_code():
    """检查注释掉的代码"""
    commented_code_patterns = [
        r'^\s*#\s*def\s',    # 注释掉的函数定义
        r'^\s*#\s*class\s',   # 注释掉的类定义
        r'^\s*#\s*self\.',    # 注释掉的实例变量赋值
        r'^\s*#\s*[a-zA-Z0-9_]+\s*=',  # 注释掉的变量赋值
        r'^\s*#\s*[a-zA-Z0-9_]+\s*\(',  # 注释掉的函数调用
    ]
    
    for i, line in enumerate(lines, 1):
        for pattern in commented_code_patterns:
            if re.match(pattern, line):
                issues.append(f"第 {i} 行: 注释掉的代码")
                break

# 5. 检查多个连续空行
def check_empty_lines():
    """检查多个连续空行"""
    current_empty = 0
    start_line = 0
    
    for i, line in enumerate(lines, 1):
        if not line.strip():
            if current_empty == 0:
                start_line = i
            current_empty += 1
        else:
            if current_empty >= 3:  # 超过3个连续空行
                issues.append(f"第 {start_line}-{start_line+current_empty-1} 行: {current_empty} 个连续空行")
            current_empty = 0
    
    if current_empty >= 3:
        issues.append(f"第 {start_line}-{start_line+current_empty-1} 行: {current_empty} 个连续空行")

# 运行所有检查
check_unused_params()
check_repeated_lines()
check_long_lines()
check_commented_code()
check_empty_lines()

# 显示结果
for i, issue in enumerate(issues[:13], 1):  # 只显示前13个问题
    print(f"{i}. {issue}")

if len(issues) > 13:
    print(f"... 还有 {len(issues) - 13} 个问题未显示")

print(f"\n=== 总问题数: {len(issues)} ===")
