#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将图标文件转换为base64编码，用于嵌入到代码中
"""
import base64

def convert_file_to_base64(file_path):
    """将文件转换为base64编码
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: base64编码的字符串
    """
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def main():
    """主函数"""
    # 转换图标文件
    ico_base64 = convert_file_to_base64('icon.ico')
    png_base64 = convert_file_to_base64('icon.png')
    
    # 生成Python代码
    code = f"""
# 嵌入的图标数据 - base64编码
ICON_ICO_BASE64 = '''{ico_base64}'''

ICON_PNG_BASE64 = '''{png_base64}'''
"""
    
    # 保存到文件
    with open('embedded_icons.py', 'w', encoding='utf-8') as f:
        f.write(code)
    
    print("图标已转换为base64编码并保存到embedded_icons.py文件中")
    print("请将此文件中的代码复制到windows_app.py中，然后修改图标设置逻辑")

if __name__ == "__main__":
    main()
