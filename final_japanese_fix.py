import json
import re

# Load the translations file
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define fixes with more context awareness
fixes = {
    # Common duplicate word fixes
    '親ネットワークワーク': '親ネットワーク',
    'ネットワークワーク': 'ネットワーク',
    
    # Punctuation fixes
    '。。。': '...',
    
    # Fix misused single quotes around placeholders
    '’{': '{',
    '}’': '}',
    
    # Fix Japanese full-width periods in IP examples
    '192。168。1。0': '192.168.1.0',
    '10。0。0。0': '10.0.0.0',
    '10。21。50。0': '10.21.50.0',
    
    # Fix extra spaces around colons in some cases
    '： ': '：',
    ' ：': '：',
    
    # Fix double spaces
    '  ': ' ',
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
        
        # Fix any remaining double spaces (multiple passes)
        while '  ' in ja_text:
            ja_text = ja_text.replace('  ', ' ')
        
        # Fix escaped braces that were introduced by previous fixes
        ja_text = ja_text.replace('\{', '{').replace('\}', '}')
        
        # Update the translation if changes were made
        if ja_text != original_text:
            translations['ja'] = ja_text
            print(f"Fixed: {key} - {original_text} -> {ja_text}")
            fix_count += 1

# Save the fixed translations
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nTotal fixes applied: {fix_count}")
print("Japanese translations have been comprehensively fixed!")
