import json

# 打开并加载JSON文件
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 定义需要统一的术语映射
term_fixes = {
    # Import相关
    "取込": "インポート",
    # Export相关
    "結果出力": "エクスポート結果",
    "計画出力": "計画エクスポート",
    # 其他术语
    "サブネット設計師": "サブネット計画ツール",
    "サブマスク": "サブネットマスク",
    "ネットアドレス": "ネットワークアドレス"
}

# 修复计数器
fix_count = 0

# 遍历所有翻译项
for key, value in data.items():
    if isinstance(value, dict) and 'ja' in value:
        original_translation = value["ja"]
        updated_translation = original_translation
        
        # 1. 统一术语翻译
        for old_term, new_term in term_fixes.items():
            if old_term in updated_translation:
                updated_translation = updated_translation.replace(old_term, new_term)
                print(f"修复术语: {key} - 将 '{old_term}' 替换为 '{new_term}'")
                fix_count += 1
        
        # 2. 修复语法问题
        # 移除句尾的英文标点符号
        if updated_translation and updated_translation[-1] in ['.', ',', ';', ':']:
            updated_translation = updated_translation[:-1]
            print(f"修复语法: {key} - 移除句尾英文标点")
            fix_count += 1
        
        # 移除多余的空格
        while '  ' in updated_translation:
            updated_translation = updated_translation.replace('  ', ' ')
            print(f"修复语法: {key} - 移除多余空格")
            fix_count += 1
        
        # 更新翻译
        if updated_translation != original_translation:
            value["ja"] = updated_translation

# 保存修复后的JSON文件
with open('translations_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n修复完成！共修复了 {fix_count} 个问题")
print("修复后的文件已保存为 translations_fixed.json")
