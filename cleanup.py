#!/usr/bin/env python3

# 清理show_result方法中的冗余代码

with open('windows_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到show_result方法的起始行
start_line = None
for i, line in enumerate(lines):
    if 'def show_result(' in line:
        start_line = i
        break

if start_line is not None:
    # 移除冗余代码行（从注释开始到第一个truncate_text_by_pixel函数结束）
    # 查找冗余代码的起始和结束位置
    redundant_start = None
    redundant_end = None
    
    for i in range(start_line, len(lines)):
        if '# 基于像素宽度的文本截断算法' in lines[i]:
            redundant_start = i
        elif 'return text[:best_length] + "..."' in lines[i] and redundant_start is not None:
            redundant_end = i
            break
    
    if redundant_start is not None and redundant_end is not None:
        # 移除冗余代码
        del lines[redundant_start:redundant_end + 1]
        
        # 将修改后的内容写回文件
        with open('windows_app.py', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"已移除冗余代码，从行 {redundant_start + 1} 到行 {redundant_end + 1}")
    else:
        print("未找到冗余代码")
else:
    print("未找到show_result方法")
