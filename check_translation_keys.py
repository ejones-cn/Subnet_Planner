import json
import re

# 读取translations.json文件
with open('translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

# 读取windows_app.py文件
with open('windows_app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# 提取所有翻译键
# 匹配_"key"格式，包括带参数的情况
pattern = r'_\("([^"]+)"\)'
app_keys = set(re.findall(pattern, app_content))

# 获取translations.json中的所有键（排除__version__）
translation_keys = set([k for k in translations.keys() if k != '__version__'])

# 检查是否有app_keys中的键不在translation_keys中
missing_keys = app_keys - translation_keys

# 检查是否有translation_keys中的键不在app_keys中（可能是未使用的键）
unused_keys = translation_keys - app_keys

# 输出结果
print(f"从windows_app.py中提取的翻译键数量: {len(app_keys)}")
print(f"translations.json中的翻译键数量: {len(translation_keys)}")
print()

if missing_keys:
    print("❌ 以下键在windows_app.py中使用但在translations.json中不存在:")
    for key in sorted(missing_keys):
        print(f"  - {key}")
else:
    print("✅ windows_app.py中使用的所有翻译键都存在于translations.json中")

print()

if unused_keys:
    print(f"ℹ️ translations.json中有 {len(unused_keys)} 个键未在windows_app.py中使用")
    print("前20个未使用的键:")
    for key in sorted(unused_keys)[:20]:
        print(f"  - {key}")
    if len(unused_keys) > 20:
        print(f"  ... 还有 {len(unused_keys) - 20} 个未使用的键")
else:
    print("✅ translations.json中的所有键都在windows_app.py中使用")

print()

# 检查每个翻译键的韩语翻译是否存在
print("📋 检查韩语翻译完整性:")
ko_missing = []
for key in app_keys:
    if key in translations:
        if 'ko' not in translations[key]:
            ko_missing.append(key)

if ko_missing:
    print(f"❌ 以下键缺少韩语翻译: {len(ko_missing)}")
    for key in sorted(ko_missing):
        print(f"  - {key}")
else:
    print("✅ 所有翻译键都有韩语翻译")

# 检查硬编码的韩语文本
print()
print("🔍 检查硬编码的韩语文本:")
# 匹配可能的硬编码韩语文本（韩文Unicode范围）
ko_text_pattern = r'[\uAC00-\uD7AF]+'
hardcoded_ko = set(re.findall(ko_text_pattern, app_content))

# 排除翻译函数中的韩语文本（已处理）
# 提取翻译函数中的韩语文本
ko_in_translations = set()
for key, trans in translations.items():
    if 'ko' in trans:
        ko_in_translations.update(re.findall(ko_text_pattern, trans['ko']))

# 硬编码的韩语文本 = 所有韩语文本 - 翻译函数中的韩语文本
true_hardcoded = hardcoded_ko - ko_in_translations

if true_hardcoded:
    print(f"⚠️ 发现 {len(true_hardcoded)} 个可能的硬编码韩语文本:")
    for text in sorted(true_hardcoded):
        print(f"  - {text}")
else:
    print("✅ 未发现硬编码的韩语文本")
