#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复windows_app.py文件的缩进问题
"""

import os
import re

def fix_indentation():
    """修复windows_app.py文件中PDF导出部分的缩进问题"""
    # 读取文件内容
    with open('windows_app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 找到PDF导出部分的开始行
    start_line = None
    for i, line in enumerate(lines):
        if 'elif file_ext == ".pdf":' in line:
            start_line = i
            break
    
    if start_line is None:
        print("未找到PDF导出部分")
        return
    
    # 找到PDF导出部分的结束行（下一个elif或else）
    end_line = None
    for i in range(start_line + 1, len(lines)):
        stripped_line = lines[i].strip()
        if stripped_line.startswith('elif') or stripped_line.startswith('else'):
            end_line = i
            break
    
    if end_line is None:
        print("未找到PDF导出部分的结束行")
        return
    
    # 输出调试信息
    print(f"PDF导出部分范围: 第{start_line+1}行到第{end_line}行")
    
    # 检查是否已经有try块
    has_try = any('try:' in line for line in lines[start_line:end_line])
    
    if not has_try:
        # 添加try块
        lines.insert(start_line + 2, '                try:\n')
        end_line += 1
        
        # 增加所有行的缩进
        for i in range(start_line + 3, end_line):
            lines[i] = '                    ' + lines[i]
        
        # 添加except块
        except_lines = [
            '                except ImportError as e:\n',
            '                    import sys\n',
            '                    error_msg = f"PDF导出失败: 缺少reportlab模块\\n\\n"\\\n',
            '                               f"当前Python解释器: {sys.executable}\\n\\n"\\\n',
            '                               f"解决方案:\\n"\\\n',
            '                               f"1. 打开命令行终端\\n"\\\n',
            '                               f"2. 执行以下命令安装reportlab:\\n"\\\n',
            '                               f"   {sys.executable} -m pip install reportlab\\n"\\\n',
            '                               f"3. 安装完成后重新运行程序\\n\\n"\\\n',
            '                               f"或者使用其他格式导出数据，如CSV、Excel等。"\n',
            '                    self.show_error("PDF导出失败", error_msg)\n',
            '                    return\n',
            '                except Exception as e:\n',
            '                    self.show_error("PDF导出失败", f"PDF导出失败: {str(e)}")\n',
            '                    return\n'
        ]
        
        lines.insert(end_line, *except_lines)
    else:
        print("已存在try块，跳过添加")
    
    # 保存修复后的文件
    with open('windows_app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("缩进修复完成")

if __name__ == "__main__":
    fix_indentation()
