from PIL import Image
import os

png_path = "icon-1.png"
ico_path = "icon-1.ico"

img = Image.open(png_path)

ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

img.save(ico_path, format='ICO', sizes=ico_sizes)

print(f"成功生成ICO文件：{ico_path}")
print(f"包含尺寸：{', '.join([f'{size[0]}x{size[1]}' for size in ico_sizes])}")
