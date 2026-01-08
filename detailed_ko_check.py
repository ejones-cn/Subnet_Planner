#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
韩语翻译详细检查脚本
"""

import json
import re

def main():
    # 加载JSON文件
    with open('translations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print('=== 韩语翻译全面检查 ===')
    total_translations = len([k for k, v in data.items() if isinstance(v, dict) and 'ko' in v])
    print(f'总翻译项数: {total_translations}')
    
    # 特别检查confirm键
    print('\n--- 特别检查confirm键 ---')
    if 'confirm' in data and isinstance(data['confirm'], dict) and 'ko' in data['confirm']:
        confirm_ko = data['confirm']['ko']
        print(f"confirm键当前翻译: {confirm_ko}")
        print(f"状态: {'✓ 正确' if confirm_ko == '확인' else '✗ 需要修复'}")
    
    # 检查所有韩语翻译的正确性
    print('\n--- 详细检查所有韩语翻译 ---')
    
    # 定义检查规则
    rules = {
        # 规则名: (检查函数, 错误信息)
        '韩语字符检查': (lambda s: re.search(r'[\uAC00-\uD7AF]+', s) is not None, '缺少韩语字符'),
        '多余空格检查': (lambda s: '   ' not in s, '包含多余空格'),
        '无效表达检查': (lambda s: '사용 가능 수 수' not in s and '사용 가능 수한' not in s, '包含无效表达'),
        '术语一致性检查': (lambda s: '예약 가능한' not in s, '应使用"사용 가능한"而非"예약 가능한"'),
        '技术术语检查': (lambda s: '와일드카드 가면' not in s, '应使用"와일드카드 마스크"'),
    }
    
    # 执行检查
    issues_found = 0
    for key, value in data.items():
        if isinstance(value, dict) and 'ko' in value:
            ko_value = value['ko']
            for rule_name, (check_func, error_msg) in rules.items():
                if not check_func(ko_value):
                    print(f"✗ {key}: {ko_value} - {rule_name}: {error_msg}")
                    issues_found += 1
    
    print(f'\n--- 检查结果 ---')
    if issues_found == 0:
        print("🎉 未发现任何问题！所有韩语翻译都符合规范。")
    else:
        print(f"❌ 发现 {issues_found} 个问题，需要进一步修复。")
    
    # 检查术语统计
    print('\n--- 术语使用统计 ---')
    term_count = {}
    for key, value in data.items():
        if isinstance(value, dict) and 'ko' in value:
            ko_value = value['ko']
            terms = re.findall(r'[\uAC00-\uD7AF]+', ko_value)
            for term in terms:
                term_count[term] = term_count.get(term, 0) + 1
    
    # 打印使用频率最高的10个术语
    print("使用频率最高的10个韩语术语：")
    sorted_terms = sorted(term_count.items(), key=lambda x: x[1], reverse=True)[:10]
    for term, count in sorted_terms:
        print(f"  {term}: {count} 次")
    
    # 检查关键术语一致性
    print('\n--- 关键术语一致性检查 ---')
    key_terms = {
        '확인': '确认/Confirm',
        '사용 가능한': '可用/Available',
        '서브넷': '子网/Subnet',
        '주소': '地址/Address',
        '네트워크': '网络/Network',
        '마스크': '掩码/Mask',
        '계획': '规划/Plan',
        '내보내기': '导出/Export',
        '가져오기': '导入/Import',
        '실행': '执行/Execute',
    }
    
    for term, desc in key_terms.items():
        count = term_count.get(term, 0)
        print(f"  {term} ({desc}): {count} 次")

if __name__ == "__main__":
    main()
