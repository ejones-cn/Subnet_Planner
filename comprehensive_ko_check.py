import json
import re

# 读取translations.json文件
with open('translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# 检查韩语翻译的问题
issues = []

# 定义常见术语的正确翻译
term_standard = {
    '사용 가능': '사용 가능한',
    '사용 가능 수': '사용 가능한 수',
    '수요': '요구 사항',
    '서브넷 요구': '서브넷 요구 사항',
    '상위 세그먼트': '상위 네트워크',
    '세그먼트': '네트워크 세그먼트',
    '슬라이스': '분할',
    '쿼리': '조회',
    '디버그': '디버깅',
    '메시지': '메시지',
    '오류': '오류',
    '성공': '성공',
    '실패': '실패',
    '확인': '확인',
    '취소': '취소',
    '추가': '추가',
    '삭제': '삭제',
    '저장': '저장',
    '내보내기': '내보내기',
    '가져오기': '가져오기',
    '실행': '실행',
    '재실행': '재실행',
    '계획': '계획',
    '분할': '분할',
    '병합': '병합'
}

# 检查每个键的韩语翻译
for key, value in translations.items():
    if key == '__version__':
        continue
    
    if 'ko' in value:
        ko_trans = value['ko']
        
        # 1. 检查是否包含非韩语字符（允许空格、数字和常见标点）
        if not re.match(r'^[\uAC00-\uD7AF\s\d.,?!"\']*$', ko_trans):
            non_ko_chars = re.findall(r'[^\uAC00-\uD7AF\s\d.,?!"\']', ko_trans)
            issues.append({
                'key': key,
                'type': 'non_korean_chars',
                'current': ko_trans,
                'issue': f'包含非韩语字符: {set(non_ko_chars)}'
            })
        
        # 2. 检查术语一致性
        for term, correct in term_standard.items():
            if term in ko_trans and term != correct:
                # 避免误判，如"사용 가능한"包含"사용 가능"但已经是正确形式
                if not (correct in ko_trans and len(term) < len(correct)):
                    issues.append({
                        'key': key,
                        'type': 'term_consistency',
                        'current': ko_trans,
                        'issue': f'术语不一致: "{term}" 应该为 "{correct}"'
                    })
        
        # 3. 检查语法问题
        # 检查"사용 가능 수 수"这样的重复错误
        if re.search(r'사용 가능 수 수', ko_trans):
            issues.append({
                'key': key,
                'type': 'grammar',
                'current': ko_trans,
                'issue': '重复的"수"字: "사용 가능 수 수" 应该为 "사용 가능 수"'
            })
        
        # 检查"사용 가능 수한"这样的错误组合
        if re.search(r'사용 가능 수한', ko_trans):
            issues.append({
                'key': key,
                'type': 'grammar',
                'current': ko_trans,
                'issue': '错误的组合: "사용 가능 수한" 应该为 "사용 가능한"'
            })
        
        # 4. 检查空格问题
        if re.search(r'\s{2,}', ko_trans):
            issues.append({
                'key': key,
                'type': 'spacing',
                'current': ko_trans,
                'issue': '包含连续空格'
            })
        
        # 5. 检查特定语法结构
        # 例如："내보내기 계획" 应该为 "계획 내보내기"（动宾结构）
        if re.match(r'내보내기\s+\w+', ko_trans):
            parts = ko_trans.split()
            if len(parts) == 2:
                issues.append({
                    'key': key,
                    'type': 'word_order',
                    'current': ko_trans,
                    'issue': f'语序可能有问题，建议调整为: "{parts[1]} {parts[0]}"'
                })
        
        # 6. 检查"서브넷 요구" 应该为 "서브넷 요구 사항"
        if re.search(r'서브넷 요구(?! 사항)', ko_trans):
            issues.append({
                'key': key,
                'type': 'incomplete_term',
                'current': ko_trans,
                'issue': '"서브넷 요구" 应该为 "서브넷 요구 사항"'
            })

# 输出问题报告
print(f"总共发现 {len(issues)} 个问题")
print("\n问题详情：")
for i, issue in enumerate(issues, 1):
    print(f"{i}. 键: {issue['key']}")
    print(f"   类型: {issue['type']}")
    print(f"   当前翻译: {issue['current']}")
    print(f"   问题: {issue['issue']}")
    print()

# 创建修复建议
fix_suggestions = {}
for issue in issues:
    if issue['key'] not in fix_suggestions:
        fix_suggestions[issue['key']] = issue['current']
    
    # 根据问题类型生成修复建议
    current = fix_suggestions[issue['key']]
    
    if issue['type'] == 'non_korean_chars':
        # 对于非韩语字符，需要人工判断是否保留
        pass
    elif issue['type'] == 'term_consistency':
        # 修复术语一致性
        for term, correct in term_standard.items():
            if term in current and term != correct:
                if not (correct in current and len(term) < len(correct)):
                    current = current.replace(term, correct)
    elif issue['type'] == 'grammar':
        # 修复语法问题
        if '사용 가능 수 수' in current:
            current = current.replace('사용 가능 수 수', '사용 가능 수')
        if '사용 가능 수한' in current:
            current = current.replace('사용 가능 수한', '사용 가능한')
    elif issue['type'] == 'spacing':
        # 修复空格问题
        current = re.sub(r'\s{2,}', ' ', current)
    elif issue['type'] == 'word_order' and '내보내기 계획' in current:
        # 修复语序问题
        current = current.replace('내보내기 계획', '계획 내보내기')
    elif issue['type'] == 'incomplete_term' and '서브넷 요구' in current and '서브넷 요구 사항' not in current:
        # 修复不完整术语
        current = current.replace('서브넷 요구', '서브넷 요구 사항')
    
    fix_suggestions[issue['key']] = current

# 输出修复建议
print("\n修复建议：")
for key, fixed in fix_suggestions.items():
    current = translations[key]['ko']
    if fixed != current:
        print(f"{key}: {current} -> {fixed}")

# 保存修复后的翻译到新文件
fixed_translations = translations.copy()
for key, fixed in fix_suggestions.items():
    if fixed != translations[key]['ko']:
        fixed_translations[key]['ko'] = fixed

with open('translations_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(fixed_translations, f, ensure_ascii=False, indent=2)

print("\n修复后的翻译已保存到 translations_fixed.json 文件")
