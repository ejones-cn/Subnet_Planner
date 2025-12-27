#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 修复信息栏动画问题

import re

# 读取文件内容
with open('f:/trae_projects/Netsub tools/windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找show_result方法中动画部分的准确内容
show_result_start = content.find('def show_result')
show_result_end = content.find('def prepare_chart_data', show_result_start)
show_result_content = content[show_result_start:show_result_end]

# 找到动画代码的开始位置
animation_start = show_result_content.find('# 显示信息栏 - 使用高度动画实现滑入效果')
animation_end = show_result_content.find('self.root.after(50, show_with_width)') + len('self.root.after(50, show_with_width)') + 1
animation_code = show_result_content[animation_start:animation_end]

# 修复动画代码，移除手动设置的self.info_bar_animating = True
fixed_animation_code = animation_code.replace('        if self.info_bar_animating:\n            return\n\n        self.info_bar_animating = True\n\n', '        if self.info_bar_animating:\n            return\n\n')

# 更新show_result方法
fixed_show_result = show_result_content[:animation_start] + fixed_animation_code + show_result_content[animation_end:]

# 更新整个文件内容
fixed_content = content[:show_result_start] + fixed_show_result + content[show_result_end:]

# 写入修复后的内容
with open('f:/trae_projects/Netsub tools/windows_app.py', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("已修复信息栏动画问题")
