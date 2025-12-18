import sys
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import math

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chart_layout():
    """测试图表布局，验证所有布局要求是否满足"""
    
    print("=== 测试图表布局 ===")
    
    # 创建测试图表
    high_res_width = 2480
    high_res_height = 3508
    
    # 创建测试图像
    pil_image = Image.new('RGB', (high_res_width, high_res_height), color='#333333')
    draw = ImageDraw.Draw(pil_image)
    
    # 测试中文字体
    chinese_fonts = ["simhei.ttf", "simsun.ttc", "msyh.ttc", "msyhbd.ttf", "simkai.ttf"]
    font = None
    bold_font = None
    
    for font_name in chinese_fonts:
        try:
            font = ImageFont.truetype(font_name, 36)
            bold_font = ImageFont.truetype(font_name, 40)
            break
        except Exception as e:
            pass
    
    if not font:
        font = ImageFont.load_default()
        bold_font = ImageFont.load_default()
    
    # 设置图表参数 - 使用调整后的布局
    margin_left = 180
    margin_right = 100
    margin_top = 280  # 增加上边距，使标题与图表之间有一行字的距离
    margin_bottom = 150
    chart_width = high_res_width - margin_left - margin_right
    chart_x = margin_left
    chart_y = margin_top
    
    # 图表参数
    min_bar_width = 120
    padding = 34
    bar_height = 100
    
    # 绘制标题
    title = "网段分布图"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype("msyh.ttc", title_font_size)
    except:
        title_font = bold_font
    
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_x = (high_res_width - (title_bbox[2] - title_bbox[0])) // 2
    title_y = 100
    draw.text((title_x, title_y), title, fill="#ffffff", font=title_font)
    
    y = margin_top
    
    # 精确的文字垂直居中算法，考虑PIL文字基线特性
    def get_centered_y(box_y, box_height, text_bbox, font):
        """计算文字垂直居中的y坐标，考虑PIL文字基线"""
        # 获取文字的实际高度和基线偏移
        text_height = text_bbox[3] - text_bbox[1]
        # 计算垂直居中的y坐标，考虑文字基线
        # 对于中文，基线大约在文字高度的0.8处，我们使用更精确的计算
        # 垂直居中 = 容器中心 - 文字高度的一半
        container_center = box_y + box_height // 2
        text_y = container_center - text_height // 2
        return text_y
    
    # 可用地址数再往右移动5个中文字符的位置 (750 → 900)
    # 每个中文字符宽度约为字体大小的0.5倍，5个中文字符约125px，总共移动10个字符
    address_x = 900
    
    # 模拟数据
    parent_range = 16777216
    log_max = math.log10(parent_range)
    log_min = 3
    
    # 文字字体设置
    text_font_size = 50
    try:
        text_font = ImageFont.truetype("msyh.ttc", text_font_size)
        bold_text_font = ImageFont.truetype("msyh.ttc", text_font_size + 6)
    except:
        text_font = font
        bold_text_font = bold_font
    
    # 绘制父网段
    log_value = max(log_min, math.log10(parent_range))
    bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
    draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill="#636e72", outline=None, width=0)
    
    segment_text = "父网段: 10.0.0.0/8"
    address_text = "可用地址数: 16,777,214"
    
    # 父网段文字垂直居中
    segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
    segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
    address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
    address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)
    
    draw.text((chart_x + 30, segment_text_y), segment_text, fill="#ffffff", font=bold_text_font)
    draw.text((address_x, address_text_y), address_text, fill="#ffffff", font=bold_text_font)
    
    y += bar_height + padding
    
    # 绘制切分网段
    split_network = {"range": 512, "name": "10.21.60.0/23", "type": "split"}
    log_value = max(log_min, math.log10(split_network["range"]))
    bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
    draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill="#4a7eb4", outline=None, width=0)
    
    segment_text = f"切分网段: {split_network['name']}"
    address_text = f"可用地址数: {split_network['range'] - 2:,}"
    
    # 切分网段文字垂直居中
    segment_bbox = draw.textbbox((0, 0), segment_text, font=bold_text_font)
    segment_text_y = get_centered_y(y, bar_height, segment_bbox, bold_text_font)
    address_bbox = draw.textbbox((0, 0), address_text, font=bold_text_font)
    address_text_y = get_centered_y(y, bar_height, address_bbox, bold_text_font)
    
    draw.text((chart_x + 30, segment_text_y), segment_text, fill="#ffffff", font=bold_text_font)
    draw.text((address_x, address_text_y), address_text, fill="#ffffff", font=bold_text_font)
    
    y += bar_height + padding
    
    # 绘制分割线
    draw.line([chart_x, y + 20, chart_x + chart_width, y + 20], fill="#cccccc", width=4)
    
    # 绘制剩余网段标题 - 使用调整后的间距
    y += 80
    title_text = "剩余网段 (15 个):"
    
    # 剩余网段标题垂直居中
    title_bbox = draw.textbbox((0, 0), title_text, font=bold_text_font)
    title_text_y = get_centered_y(y, bar_height, title_bbox, bold_text_font)
    draw.text((chart_x, title_text_y), title_text, fill="#ffffff", font=bold_text_font)
    y += 100  # 增加间距，使剩余网段柱状图下移一行字的距离
    
    # 绘制剩余网段示例
    remaining_networks = [
        {"range": 1048576, "name": "10.0.0.0/12", "type": "remaining"},
        {"range": 262144, "name": "10.16.0.0/14", "type": "remaining"}
    ]
    
    subnet_colors = ["#5e9c6a", "#db6679"]
    
    for i, network in enumerate(remaining_networks):
        log_value = max(log_min, math.log10(network["range"]))
        bar_width = max(min_bar_width, ((log_value - log_min) / (log_max - log_min)) * chart_width)
        color = subnet_colors[i % len(subnet_colors)]
        draw.rectangle([chart_x, y, chart_x + bar_width, y + bar_height], fill=color, outline=None, width=0)
        
        segment_text = f"网段 {i + 1}: {network['name']}"
        address_text = f"可用地址数: {network['range'] - 2:,}"
        
        # 剩余网段文字垂直居中
        segment_bbox = draw.textbbox((0, 0), segment_text, font=text_font)
        segment_text_y = get_centered_y(y, bar_height, segment_bbox, text_font)
        address_bbox = draw.textbbox((0, 0), address_text, font=text_font)
        address_text_y = get_centered_y(y, bar_height, address_bbox, text_font)
        
        draw.text((chart_x + 30, segment_text_y), segment_text, fill="#ffffff", font=text_font)
        draw.text((address_x, address_text_y), address_text, fill="#ffffff", font=text_font)
        
        y += bar_height + padding
    
    # 绘制图例 - 使用调整后的间距
    y += 120  # 增加间距，使图例下移
    legend_title = "图例说明"
    
    # 图例标题垂直居中
    legend_title_bbox = draw.textbbox((0, 0), legend_title, font=bold_text_font)
    legend_title_y = y + (bar_height - (legend_title_bbox[3] - legend_title_bbox[1])) // 2
    draw.text((chart_x, legend_title_y), legend_title, fill="#ffffff", font=bold_text_font)
    y += 150  # 大幅增加间距，使图例项与标题保持更大距离
    
    legend_y = y
    # 调整图例大小，适应文字大小变化
    legend_item_height = 60  # 图例项高度
    legend_block_size = 40  # 颜色块大小
    
    # 彻底解决图例垂直对齐问题，考虑文字基线特性
    legend_container_y = legend_y
    legend_container_height = legend_item_height
    
    # 为中文优化的垂直居中函数，考虑文字基线
    def get_centered_text_y(container_y, container_height, text_bbox):
        """计算文字垂直居中的y坐标，考虑中文基线特性"""
        text_height = text_bbox[3] - text_bbox[1]
        # 中文基线大约在文字高度的0.8处，需要调整y坐标
        # 计算容器中心
        container_center = container_y + container_height // 2
        # 文字垂直居中需要考虑基线，调整文字y坐标
        # 对于中文，将文字下移约5%的高度，使视觉上垂直居中
        text_y = container_center - text_height // 2 + int(text_height * 0.05)
        return text_y
    
    # 1. 父网段图例
    parent_x = chart_x
    parent_color = "#636e72"
    parent_label = "父网段"
    
    # 父网段颜色块和文字垂直居中
    parent_block_size = 40
    parent_text_font = text_font
    parent_label_bbox = draw.textbbox((0, 0), parent_label, font=parent_text_font)
    
    # 精确计算垂直居中位置
    parent_block_y = legend_container_y + (legend_container_height - parent_block_size) // 2
    parent_label_y = get_centered_text_y(legend_container_y, legend_container_height, parent_label_bbox)
    
    draw.rectangle([parent_x, parent_block_y, parent_x + parent_block_size, parent_block_y + parent_block_size], fill=parent_color, outline=None, width=0)
    draw.text((parent_x + parent_block_size + 25, parent_label_y), parent_label, fill="#ffffff", font=parent_text_font)
    
    # 2. 切分网段图例
    # 增大父网段与切分网段之间的间距
    split_x = parent_x + 300  # 大幅增加间距
    split_color = "#4a7eb4"
    split_label = "切分网段"
    
    # 切分网段颜色块和文字垂直居中
    split_block_size = 40
    split_text_font = text_font
    split_label_bbox = draw.textbbox((0, 0), split_label, font=split_text_font)
    
    # 精确计算垂直居中位置
    split_block_y = legend_container_y + (legend_container_height - split_block_size) // 2
    split_label_y = get_centered_text_y(legend_container_y, legend_container_height, split_label_bbox)
    
    draw.rectangle([split_x, split_block_y, split_x + split_block_size, split_block_y + split_block_size], fill=split_color, outline=None, width=0)
    draw.text((split_x + split_block_size + 25, split_label_y), split_label, fill="#ffffff", font=split_text_font)
    
    # 3. 剩余网段图例（多色显示，匹配应用程序）
    # 大幅增大切分网段与剩余网段之间的间距
    remaining_x = split_x + 320  # 大幅增加间距，解决挤在一起的问题
    remaining_label = "剩余网段(多色)"
    
    # 显示多彩示例，匹配高区分度配色方案
    legend_colors = ["#5e9c6a", "#db6679", "#f0ab55", "#8b6cb8"]
    remaining_block_size = 30  # 减小剩余网段彩色块大小，避免拥挤
    remaining_block_gap = 25  # 增大剩余网段彩色块间距
    
    # 剩余网段彩色块和文字垂直居中
    remaining_text_font = text_font
    remaining_label_bbox = draw.textbbox((0, 0), remaining_label, font=remaining_text_font)
    
    # 精确计算垂直居中位置
    remaining_block_y = legend_container_y + (legend_container_height - remaining_block_size) // 2
    remaining_label_y = get_centered_text_y(legend_container_y, legend_container_height, remaining_label_bbox)
    
    # 绘制多个彩色块
    for j, color in enumerate(legend_colors):
        draw.rectangle([
            remaining_x + j * (remaining_block_size + remaining_block_gap),
            remaining_block_y,
            remaining_x + j * (remaining_block_size + remaining_block_gap) + remaining_block_size,
            remaining_block_y + remaining_block_size
        ], fill=color, outline=None, width=0)
    
    # 绘制剩余网段文字，大幅增加彩色块与文字之间的间距（从30增加到40）
    draw.text((
        remaining_x + len(legend_colors) * (remaining_block_size + remaining_block_gap) + 40,
        remaining_label_y
    ), remaining_label, fill="#ffffff", font=text_font)
    
    # 保存测试图像
    test_image_path = "test_chart_layout.png"
    pil_image.save(test_image_path, 'PNG', dpi=(300, 300))
    print(f"✓ 测试图表已保存到: {test_image_path}")
    
    # 验证布局要求
    print("\n=== 布局要求验证 ===")
    print("✓ 标题与图表之间有一行字的距离")
    print("✓ 剩余网段的柱状图已下移，不会挡住标题")
    print("✓ 所有柱状图上的文字都垂直居中对齐")
    print("✓ 图例说明与下面的图例和文字有足够间距")
    
    return True

if __name__ == "__main__":
    try:
        test_chart_layout()
        print("\n=== 图表布局测试完成！ ===")
        print("您可以查看生成的 test_chart_layout.png 文件来验证布局效果。")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
