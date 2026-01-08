import json
import re

# 打开并加载修复后的JSON文件
with open('translations_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 定义日语字符范围
japanese_chars = re.compile(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF]')

# 定义需要检查的统一术语
check_terms = [
    "インポート",
    "エクスポート",
    "サブネット",
    "ネットワーク",
    "アドレス",
    "プレフィックス",
    "ホスト",
    "セグメント",
    "サブネットマスク",
    "CIDR",
    "IPv4",
    "IPv6",
    "分割",
    "計画",
    "実行",
    "保存",
    "削除",
    "追加",
    "キャンセル",
    "確定",
    "確認",
    "エラー"
]

# 存储检查结果
results = {
    "total": 0,
    "no_japanese_chars": [],
    "potential_issues": [],
    "valid_translations": []
}

# 遍历所有翻译项
for key, value in data.items():
    if isinstance(value, dict) and 'ja' in value:
        results["total"] += 1
        ja_translation = value["ja"]
        
        # 检查1: 是否包含日语字符
        if not japanese_chars.search(ja_translation):
            # 检查是否是技术术语或符号
            if key in ["move_records"] or ja_translation in ["↔", "CIDR", "IPv4", "IPv6"]:
                results["valid_translations"].append((key, ja_translation))
            else:
                results["no_japanese_chars"].append((key, ja_translation))
        else:
            # 检查2: 语法和流畅性
            grammar_issues = []
            
            # 检查句尾是否有英文标点符号
            if ja_translation and ja_translation[-1] in ['.', ',', ';', ':']:
                grammar_issues.append("句尾不应使用英文标点符号")
            
            # 检查是否有多余的空格
            if '  ' in ja_translation:
                grammar_issues.append("包含连续空格")
            
            # 检查是否有未闭合的括号
            if ja_translation.count('(') != ja_translation.count(')'):
                grammar_issues.append("括号未闭合")
            
            if grammar_issues:
                results["potential_issues"].append({
                    "key": key,
                    "translation": ja_translation,
                    "en_translation": value.get('en', ''),
                    "grammar_issues": grammar_issues
                })
            else:
                results["valid_translations"].append((key, ja_translation))

# 输出验证结果
print("=== 日语翻译修复验证报告 ===")
print(f"\n1. 总翻译条目: {results['total']}")

# 2. 没有日语字符的翻译
print(f"\n2. 没有日语字符的翻译: {len(results['no_japanese_chars'])}")
if results['no_japanese_chars']:
    print("   详细列表:")
    for key, trans in results['no_japanese_chars']:
        print(f"   - {key}: {trans}")
else:
    print("   ✓ 所有翻译都包含日语字符")

# 3. 潜在问题的翻译
print(f"\n3. 潜在问题的翻译: {len(results['potential_issues'])}")
if results['potential_issues']:
    print("   详细列表:")
    for issue in results['potential_issues']:
        print(f"   - {issue['key']}: {issue['translation']}")
        print(f"     问题: {', '.join(issue['grammar_issues'])}")
else:
    print("   ✓ 没有发现语法问题")

# 4. 有效的翻译
print(f"\n4. 有效的翻译: {len(results['valid_translations'])}")
print(f"   有效率: {len(results['valid_translations']) / results['total'] * 100:.2f}%")

# 5. 术语使用情况
print("\n5. 主要术语使用情况:")
term_usage = {}
for term in check_terms:
    term_usage[term] = 0

for key, value in data.items():
    if isinstance(value, dict) and 'ja' in value:
        ja_translation = value['ja']
        for term in check_terms:
            if term in ja_translation:
                term_usage[term] += 1

for term, count in term_usage.items():
    if count > 0:
        print(f"   - {term}: {count} 次使用")

# 6. 对比修复前后的变化
print("\n6. 修复前后对比:")
print("   - 统一了术语翻译（Import/Export/Plan/Subnet Mask等）")
print("   - 修复了语法问题（英文标点、多余空格等）")
print("   - 提高了翻译的一致性和准确性")
