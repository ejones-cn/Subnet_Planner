from PIL import Image
import os

# 输入PNG文件路径
png_path = "icon-1.png"
# 输出ICO文件路径
ico_path = "icon-1.ico"

# 打开PNG图像
img = Image.open(png_path)

# 定义ICO文件中包含的不同尺寸（高质量ICO通常包含多种尺寸）
ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

# 保存为ICO文件，包含所有指定尺寸
img.save(ico_path, format='ICO', sizes=ico_sizes)

print(f"成功生成ICO文件：{ico_path}")
print(f"包含尺寸：{', '.join([f'{size[0]}x{size[1]}' for size in ico_sizes])}")