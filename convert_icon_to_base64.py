#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将PNG图标转换为base64编码，生成可嵌入到Python代码中的图标数据
"""

import base64
from PIL import Image
import io

def png_to_base64(png_path):
    """
    将PNG图片转换为base64编码字符串
    
    Args:
        png_path: PNG图片路径
        
    Returns:
        base64编码的字符串
    """
    with open(png_path, 'rb') as f:
        png_data = f.read()
    return base64.b64encode(png_data).decode('utf-8')

def generate_icon_code(png_path, variable_name="APP_ICON_BASE6