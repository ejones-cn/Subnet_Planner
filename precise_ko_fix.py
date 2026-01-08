import json
import re

# 读取translations.json文件
with open('translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# 定义需要修复的术语映射
term_fixes = {
    # 基本术语
    '슬라이스': '분할',
    '수요': '요구 사항',
    '쿼리': '조회',
    '디버그': '디버깅',
    
    # 复合术语
    '슬라이스 분할': '분할',
    '슬라이스 세그먼트': '분할 네트워크 세그먼트',
    '남은 세그먼트': '남은 네트워크 세그먼트',
    '상위 세그먼트': '상위 네트워크',
    '서브넷 요구': '서브넷 요구 사항',
    '수요 풀': '요구 사항 풀',
    '수요 수': '요구 사항 수',
    '사용 가능 수': '사용 가능한 수',
    '내보내기 계획': '계획 내보내기',
    '기능성 디버그': '기능성 디버깅',
    '세그먼트 분포': '네트워크 세그먼트 분포',
    '주소 세그먼트': '주소 네트워크 세그먼트',
}

# 修复每个键的韩语翻译
fixed_count = 0
for key, value in translations.items():
    if key == '__version__':
        continue
    
    if 'ko' in value:
        original_ko = value['ko']
        fixed_ko = original_ko
        
        # 应用术语修复
        for old_term, new_term in term_fixes.items():
            if old_term in fixed_ko:
                # 确保不会过度替换，例如避免将"사용 가능한"替换为"사용 가능한한"
                if not (new_term in fixed_ko and len(old_term) < len(new_term)):
                    fixed_ko = fixed_ko.replace(old_term, new_term)
        
        # 特殊处理：修复"사용 가능 수 수"这样的重复错误
        fixed_ko = re.sub(r'사용 가능한 수 수', '사용 가능한 수', fixed_ko)
        fixed_ko = re.sub(r'사용 가능 수 수', '사용 가능한 수', fixed_ko)
        
        # 特殊处理：修复"사용 가능 수한"这样的错误组合
        fixed_ko = re.sub(r'사용 가능 수한', '사용 가능한', fixed_ko)
        
        # 特殊处理：修复连续空格
        fixed_ko = re.sub(r'\s{2,}', ' ', fixed_ko)
        
        # 如果有变化，更新翻译
        if fixed_ko != original_ko:
            translations[key]['ko'] = fixed_ko
            fixed_count += 1
            print(f"修复 {key}: {original_ko} -> {fixed_ko}")

# 保存修复后的翻译
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(translations, f, ensure_ascii=False, indent=2)

print(f"\n总共修复了 {fixed_count} 个韩语翻译问题")
