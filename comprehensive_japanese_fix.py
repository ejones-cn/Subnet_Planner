import json
import re

# Load the translations file
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define fixes
fixes = {
    # Common duplicate word fixes
    '親ネットワークワーク': '親ネットワーク',
    'ネットワークワーク': 'ネットワーク',
    
    # Punctuation fixes
    '。。。': '...',
    
    # Placeholder quote fixes
    '’{': '{',
    '}’': '}',
    
    # Fix spacing in examples
    '192。168。1。0': '192.168.1.0',
    '10。0。0。0': '10.0.0.0',
    '10。21。50。0': '10.21.50.0',
}

# Additional fixes for specific keys
key_specific_fixes = {
    'click_execute_split_to_start': {
        'ja': '「分割を実行」ボタンをクリックして操作を開始してください...'
    }
}

# Count of fixes applied
fix_count = 0

# Process each translation entry
for key, translations in data.items():
    if 'ja' in translations:
        ja_text = translations['ja']
        original_text = ja_text
        
        # Apply general fixes
        for old, new in fixes.items():
            if old in ja_text:
                ja_text = ja_text.replace(old, new)
                fix_count += ja_text.count(new) - original_text.count(old)
        
        # Apply key-specific fixes
        if key in key_specific_fixes:
            ja_text = key_specific_fixes[key]['ja']
            fix_count += 1
        
        # Update the translation if changes were made
        if ja_text != original_text:
            translations['ja'] = ja_text
            print(f"Fixed: {key} - {original_text} -> {ja_text}")

# Save the fixed translations
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nTotal fixes applied: {fix_count}")
print("Japanese translations have been comprehensively fixed!")
