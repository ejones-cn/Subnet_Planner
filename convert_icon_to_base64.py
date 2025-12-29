#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将PNG图标转换为base64编码，生成可嵌入到Python代码中的图标数据
"""

import base64
import os


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


def main():
    """
    主函数，生成图标代码
    """
    print("PNG图标转Base64编码工具")
    print("=" * 40)

    png_path = "icon.png"

    if not os.path.exists(png_path):
        print(f"错误：文件 {png_path} 不存在！")
        return

    base64_data = png_to_base64(png_path)

    code = f"""# 应用图标 - Base64编码
APP_ICON_BASE64 = '{base64_data}'
"""

    output_path = "icon_base64.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"成功生成图标代码文件：{output_path}")
    print("\n接下来需要在主程序中添加以下代码来使用图标：")
    print("\n# 导入必要的模块")
    print("import base64")
    print("from PIL import Image, ImageTk")
    print("import io")
    print("from icon_base64 import APP_ICON_BASE64")
    print("")
    print("# 在创建窗口后添加以下代码")
    print("def load_icon():")
    print("    # 解码base64数据")
    print("    icon_data = base64.b64decode(APP_ICON_BASE64)")
    print("    # 创建字节流")
    print("    icon_stream = io.BytesIO(icon_data)")
    print("    # 打开为PIL Image")
    print("    icon = Image.open(icon_stream)")
    print("    # 转换为tkinter可用的PhotoImage")
    print("    return ImageTk.PhotoImage(icon)")
    print("")
    print("# 在窗口创建后调用")
    print("icon_photo = load_icon()")
    print("root.iconphoto(True, icon_photo)")


if __name__ == "__main__":
    main()
