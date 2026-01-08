import json
import re

# 读取translations.json文件
with open('translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# 定义验证规则
validation_rules = {
    'term_consistency': {
        'required_terms': ['사용 가능한', '요구 사항', '상위 네트워크', '조회', '디버깅'],
        'forbidden_terms': ['사용 가능 수 수', '사용 가능 수한', '수요 수', '슬라이스 세그먼트']
    },
    'grammar': {
        'no_duplicate_words': True,
        'no_invalid_combinations': True
    },
    'spacing': {
        'no_double_spaces': True
    }
}

# 验证结果
validation_results = {
    'pass': [],
    'fail': []
}

# 验证每个键的韩语翻译
for key, value in translations.items():
    if key == '__version__':
        continue
    
    if 'ko' in value:
        ko_trans = value['ko']
        key_results = {
            'key': key,
            'translation': ko_trans,
            'issues': []
        }
        
        # 检查术语一致性 - 禁止的术语
        for forbidden_term in validation_rules['term_consistency']['forbidden_terms']:
            if forbidden_term in ko_trans:
                key_results['issues'].append(f'包含禁止术语: {forbidden_term}')
        
        # 检查语法 - 重复单词
        if validation_rules['grammar']['no_duplicate_words']:
            # 检查连续重复的单词，但排除IPv6地址示例中的0000:
            words = ko_trans.split()
            for i in range(1, len(words)):
                if words[i] == words[i-1]:
                    # 排除IPv6地址示例中的0000:情况
                    if not (words[i] == '0000:' and 'IPv6' in ko_trans):
                        key_results['issues'].append(f'包含连续重复单词: {words[i]}')
        
        # 检查语法 - 无效组合
        if validation_rules['grammar']['no_invalid_combinations']:
            if '사용 가능 수한' in ko_trans:
                key_results['issues'].append('包含无效组合: 사용 가능 수한')
        
        # 检查空格 - 双空格
        if validation_rules['spacing']['no_double_spaces']:
            if '  ' in ko_trans:
                key_results['issues'].append('包含连续空格')
        
        # 特殊检查：确认键的翻译
        if key == 'confirm' and ko_trans != '확인':
            key_results['issues'].append('confirm键翻译不正确，应该为: 확인')
        
        # 添加到验证结果
        if key_results['issues']:
            validation_results['fail'].append(key_results)
        else:
            validation_results['pass'].append(key_results)

# 输出验证结果
print(f"验证完成: {len(validation_results['pass'])} 个翻译通过, {len(validation_results['fail'])} 个翻译失败")

if validation_results['fail']:
    print("\n失败详情:")
    for result in validation_results['fail']:
        print(f"键: {result['key']}")
        print(f"翻译: {result['translation']}")
        print(f"问题: {', '.join(result['issues'])}")
        print()
else:
    print("\n所有翻译都通过了验证！")

# 检查特定的键是否翻译正确
print("\n特定键检查:")
key_checks = ['confirm', 'ok', 'cancel', 'save', 'export', 'import']
for key in key_checks:
    if key in translations and 'ko' in translations[key]:
        print(f"{key}: {translations[key]['ko']}")
    else:
        print(f"{key}: 未找到")

# 检查术语一致性
print("\n术语一致性检查:")
term_usage = {}
for key, value in translations.items():
    if key == '__version__' or 'ko' not in value:
        continue
    
    ko_trans = value['ko']
    for term in validation_rules['term_consistency']['required_terms']:
        if term in ko_trans:
            if term not in term_usage:
                term_usage[term] = []
            term_usage[term].append(key)

for term, keys in term_usage.items():
    print(f"术语 '{term}' 使用了 {len(keys)} 次，在以下键中: {', '.join(keys[:5])}{'...' if len(keys) > 5 else ''}")
