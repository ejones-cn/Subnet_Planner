#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复文件开头的BOM字符"""

import os

def fix_bom(file_path):
    """修复文件开头的BOM字符"""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        if content.startswith(b'\xef\xbb\xbf'):
            print(f"修复 {file_path} 中的BOM字符...")
            content = content[3:]
            with open(file_path, 'wb') as f:
                f.write(content)
            print(f"✅ {file_path} 修复完成")
            return True
        else:
            print(f"{file_path} 没有BOM字符")
            return False
    except Exception as e:
        print(f"❌ 修复 {file_path} 失败: {e}")
        return False

if __name__ == "__main__":
    # 修复指定文件
    fix_bom('windows_app.py')
