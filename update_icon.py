#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新应用图标，将ICO文件转换为Base64编码并写入icon_base64.py
"""

import base64
import os



def update_icon(icon_path="icon.ico", output_file="icon_base64.py"):
    """更新应用图标
    
    Args:
        icon_path: 新的ICO文件路径
        output_file: 输出的Python文件路径
    """
    try:
        # 检查ICO文件是否存在
        if not os.path.exists(icon_path):
            print(f"❌ 错误：未找到ICO文件 '{icon_path}'")
            return False
        
        # 读取ICO文件并转换为Base64编码
        with open(icon_path, "rb") as f:
            icon_data = f.read()
        
        base64_data = base64.b64encode(icon_data).decode("utf-8")
        
        # 生成Python文件内容
        file_content = f"# 应用图标 - Base64编码\nAPP_ICON_BASE64 = '{base64_data}'\n"
        
        # 写入输出文件
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(file_content)
        
        print(f"✅ 成功：已更新图标到 '{output_file}'")
        print(f"📦 图标大小：{len(icon_data):,} 字节")
        print(f"🔢 Base64编码大小：{len(base64_data):,} 字符")
        return True
        
    except Exception as e:
        print(f"❌ 更新图标失败：{e}")
        return False


if __name__ == "__main__":
    update_icon()
