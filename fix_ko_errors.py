#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复韩语翻译中的错误
"""

import json

# 加载JSON文件
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 修复的错误模式
fix_patterns = {
    # 错误字符串: 正确字符串
    '사용 가능 수 수': '사용 가능 수',
    '사용 가능 수한': '사용 가능한',
    '사용可能な 주소 수': '사용 가능한 주소 수',
    '使用可用な 第一个 ホスト': '사용 가능한 첫 번째 호스트',
    '使用可用な 最后一个 ホスト': '사용 가능한 마지막 호스트',
    # 修复click_execute_split_to_start中的错误
    '\'분할 실행\' 버튼을 클릭하여 시작하세요...': '\'분할 수행\' 버튼을 클릭하여 시작하세요...',
}

# 应用修复
fixed_count = 0
for key, value in data.items():
    if isinstance(value, dict) and 'ko' in value:
        ko_value = value['ko']
        for error_pattern, correct_value in fix_patterns.items():
            if error_pattern in ko_value:
                new_value = ko_value.replace(error_pattern, correct_value)
                if new_value != ko_value:
                    data[key]['ko'] = new_value
                    print(f'修复了 {key}: {ko_value} → {new_value}')
                    fixed_count += 1

# 保存修复后的文件
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f'\n共修复了 {fixed_count} 个错误')
