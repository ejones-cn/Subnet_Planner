import json
import re

# Load the translations file
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define allowed characters for Japanese translations
# Includes Hiragana, Katakana, Kanji, common punctuation, and placeholders
japanese_pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF\d\s{}(),.:;?!"\'\-_]+$')

# Define common terms and their correct translations
common_terms = {
    'Error': 'エラー',
    'Add': '追加',
    'Delete': '削除',
    'Save': '保存',
    'Import': 'インポート',
    'Export': 'エクスポート',
    'Cancel': 'キャンセル',
    'OK': '確定',
    'Confirm': '確認',
    'Network': 'ネットワーク',
    'Subnet': 'サブネット',
    'IP': 'IP',
    'CIDR': 'CIDR',
    'Host': 'ホスト',
    'Address': 'アドレス',
}

# Track issues
issues = {
    'non_japanese': [],
    'term_inconsistency': [],
    'placeholder_issues': [],
    'duplicate_words': [],
    'other_issues': []
}

# Process each translation entry
for key, translations in data.items():
    if 'ja' in translations:
        ja_text = translations['ja']
        en_text = translations.get('en', '')
        
        # Check for non-Japanese characters (excluding allowed punctuation and placeholders)
        if not japanese_pattern.match(ja_text):
            issues['non_japanese'].append((key, ja_text))
        
        # Check for placeholder issues
        if '{' in ja_text or '}' in ja_text:
            # Check if placeholders are properly formatted
            if ja_text.count('{') != ja_text.count('}'):
                issues['placeholder_issues'].append((key, ja_text, 'Mismatched curly braces'))
            # Check for spaces inside placeholders
            if re.search(r'\{\s+[^}]*\s+\}', ja_text):
                issues['placeholder_issues'].append((key, ja_text, 'Spaces inside placeholders'))
        
        # Check for duplicate words
        duplicate_matches = re.findall(r'(\b\w+)\s+\1\b', ja_text)
        if duplicate_matches:
            issues['duplicate_words'].append((key, ja_text, ', '.join(duplicate_matches)))
        
        # Check term consistency for common terms
        for en_term, ja_term in common_terms.items():
            if en_term.lower() in en_text.lower():
                # This is a heuristic - we're checking if the English term is in the English text
                # and if the corresponding Japanese term is in the Japanese text
                if ja_term not in ja_text:
                    # Don't flag if it's a different form or part of another word
                    # This is just a warning, not an error
                    issues['term_inconsistency'].append((key, en_text, ja_text, en_term, ja_term))

# Print the results
print("=== Japanese Translation Quality Report ===")
print()

if issues['non_japanese']:
    print("1. Non-Japanese Translations:")
    for key, text in issues['non_japanese']:
        print(f"   - {key}: {text}")
    print()
else:
    print("1. Non-Japanese Translations: None")
    print()

if issues['placeholder_issues']:
    print("2. Placeholder Issues:")
    for key, text, issue in issues['placeholder_issues']:
        print(f"   - {key}: {text} ({issue})")
    print()
else:
    print("2. Placeholder Issues: None")
    print()

if issues['duplicate_words']:
    print("3. Duplicate Words:")
    for key, text, duplicates in issues['duplicate_words']:
        print(f"   - {key}: {text} (Duplicates: {duplicates})")
    print()
else:
    print("3. Duplicate Words: None")
    print()

if issues['term_inconsistency']:
    print("4. Term Consistency Warnings (Check if these are intentional):")
    # Limit to first 20 warnings to avoid too much output
    for key, en_text, ja_text, en_term, ja_term in issues['term_inconsistency'][:20]:
        print(f"   - {key}: EN='{en_text}' JA='{ja_text}' (Expected '{ja_term}' for '{en_term}')")
    if len(issues['term_inconsistency']) > 20:
        print(f"   ... and {len(issues['term_inconsistency']) - 20} more warnings")
    print()
else:
    print("4. Term Consistency Warnings: None")
    print()

# Summary
print("=== Summary ===")
print(f"Total entries checked: {len([k for k, v in data.items() if 'ja' in v])}")
print(f"Total issues found: {sum(len(v) for v in issues.values())}")
print()

if sum(len(v) for v in issues.values()) == 0:
    print("🎉 All Japanese translations look good!")
else:
    print("⚠️  Some issues were found. Please review the report above.")
