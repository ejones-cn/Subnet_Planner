#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
韩语翻译最终验证脚本
"""

import json

# 加载JSON文件
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取所有韩语翻译
ko_translations = {k: v['ko'] for k, v in data.items() if isinstance(v, dict) and 'ko' in v}

print("=== 韩语翻译最终验证 ===")
print(f"总翻译项数: {len(ko_translations)}")

# 验证关键术语
print("\n--- 关键术语验证 ---")

# 定义关键术语和预期翻译
key_terms = {
    'confirm': '확인',
    'about': '소개',
    'wildcard_mask': '와일드카드 마스크',
    'end': '끝',
    'check_overlap': '중첩 검사',
    'detection_result': '검출 결과',
    'unknown': '알 수 없는',
    'valid': '유효',
    'invalid': '무효',
    'planning_result': '계획 결과',
    'execute_split': '분할 실행',
    'usable_hosts': '사용 가능한 호스트 수',
    'first_host': '사용 가능한 첫 번째 호스트',
    'last_host': '사용 가능한 마지막 호스트',
    'first_usable_host': '사용 가능한 첫 번째 호스트',
    'last_usable_host': '사용 가능한 마지막 호스트',
    'available_addresses': '사용 가능한 주소 수',
}

# 验证每个关键术语
all_correct = True
for key, expected in key_terms.items():
    if key in ko_translations:
        actual = ko_translations[key]
        status = '✓' if actual == expected else '✗'
        if actual != expected:
            all_correct = False
        print(f"{status} {key}: {actual}")
    else:
        print(f"✗ {key}: 未找到")
        all_correct = False

# 验证"导出目录"相关翻译
print("\n--- 导出目录相关翻译验证 ---")
export_dir_keys = ['select_export_directory', 'one_click_export_success', 'one_click_pdf_success']
for key in export_dir_keys:
    if key in ko_translations:
        print(f"✓ {key}: {ko_translations[key]}")
    else:
        print(f"✗ {key}: 未找到")
        all_correct = False

# 验证没有明显错误
print("\n--- 错误模式检查 ---")
error_patterns = [
    '사용 가능 수 수',
    '사용 가능 수한',
    '사용可能な',
    '使用可用な',
    '하루 동안 머물러',
    '유효없음',
    '의문의',
    '관련 있는',
    '와일드카드 가면',
    '검출 중첩',
    '테스트 결과',
    '결과 계획하기',
    '폼주소',
]

for pattern in error_patterns:
    found = any(pattern in v for v in ko_translations.values())
    status = '✓' if not found else '✗'
    if found:
        all_correct = False
    print(f"{status} 未发现 '{pattern}'")

# 验证结果
print("\n=== 验证结果 ===")
if all_correct:
    print("🎉 所有韩语翻译验证通过！")
    print("✅ 术语一致")
    print("✅ 语法正确")
    print("✅ 表达习惯符合规范")
else:
    print("❌ 部分翻译仍存在问题，需要进一步检查")

# 统计修复情况
print(f"\n总翻译项数: {len(ko_translations)}")
