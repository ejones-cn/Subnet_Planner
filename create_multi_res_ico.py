#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成多种分辨率的ICO文件
"""

from PIL import Image
import os


def create_multi_resolution_ico(png_path, ico_path):
    """从PNG文件创建包含多种分辨率的ICO文件
    
    Args:
        png_path: 输入PNG文件路径
        ico_path: 输出ICO文件路径
    """
    try:
        # 支持的图标尺寸列表
        icon_sizes = [
            (16, 16),    # 小图标
            (24, 24),    # 任务栏图标
            (32, 32),    # 大图标
            (48, 48),    # 高DPI任务栏
            (64, 64),    # 高分屏支持
            (128, 128),  # 现代应用支持
            (256, 256)   # 超大图标支持
        ]
        
        print(f"🔍 读取PNG文件: {png_path}")
        with Image.open(png_path) as img:
            # 创建临时图标文件列表
            temp_icons = []
            
            print("📏 生成多种分辨率图标...")
            for size in icon_sizes:
                try:
                    # 调整图像大小，使用LANCZOS算法保持高质量
                    resized_img = img.resize(size, Image.Resampling.LANCZOS)
                    
                    # 创建临时文件路径
                    temp_path = f"temp_{size[0]}x{size[1]}.png"
                    
                    # 保存临时PNG文件
                    resized_img.save(temp_path, format='PNG')
                    temp_icons.append((temp_path, size))
                    print(f"✅ 生成 {size[0]}x{size[1]} 图标成功")
                except Exception as e:
                    print(f"❌ 生成 {size[0]}x{size[1]} 图标失败: {e}")
            
            # 使用PIL保存为ICO文件，包含所有分辨率
            print(f"💾 保存ICO文件: {ico_path}")
            
            # 打开所有临时图标
            icon_list = []
            for temp_path, size in temp_icons:
                icon_img = Image.open(temp_path)
                icon_list.append(icon_img)
            
            # 保存为ICO文件
            icon_list[0].save(ico_path, format='ICO', sizes=icon_sizes, append_images=icon_list[1:])
            
            # 关闭所有临时图标
            for img in icon_list:
                img.close()
            
            # 删除临时文件
            print("🗑️ 清理临时文件...")
            for temp_path, size in temp_icons:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    print(f"✅ 删除临时文件: {temp_path}")
            
            print(f"🎉 多种分辨率ICO文件生成成功: {ico_path}")
            return True
            
    except Exception as e:
        print(f"❌ 生成ICO文件失败: {e}")
        return False


if __name__ == "__main__":
    # 输入PNG文件路径
    input_png = "new_icon.png"
    
    # 输出ICO文件路径
    output_ico = "icon.ico"
    
    print("=" * 50)
    print("生成多种分辨率ICO文件")
    print("=" * 50)
    
    # 检查输入文件是否存在
    if not os.path.exists(input_png):
        print(f"❌ 输入文件不存在: {input_png}")
    else:
        # 生成ICO文件
        create_multi_resolution_ico(input_png, output_ico)
    
    print("=" * 50)
    print("操作完成")
    print("=" * 50)
