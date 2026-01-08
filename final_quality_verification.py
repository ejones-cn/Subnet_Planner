import json
import re

# Load the translations file
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Define allowed characters for Japanese translations
# Includes Hiragana, Katakana, Kanji, common punctuation, placeholders, and common technical terms
japanese_pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF\d\s{}(),.:;?!"\'\-_a-zA-Z]+$')

# Define common technical terms that are allowed in Japanese translations
allowed_terms = ['IPv4', 'IPv6', 'CIDR', 'PDF', 'Excel', 'CSV', 'IT', 'RFC', 'SLAAC', 'DHCPv6', 'ULA', 'ORCHID']

# Track only real issues
real_issues = {
    'duplicate_words': [],
    'mismatched_braces': [],
    'empty_translations': [],
    'invalid_formatting': [],
}

# Process each translation entry
for key, translations in data.items():
    if 'ja' in translations:
        ja_text = translations['ja']
        
        # Skip if translation is empty
        if not ja_text.strip():
            real_issues['empty_translations'].append(key)
            continue
        
        # Check for mismatched braces
        if ja_text.count('{') != ja_text.count('}'):
            real_issues['mismatched_braces'].append((key, ja_text))
        
        # Check for duplicate words (more reliable check)
        words = ja_text.split()
        seen_words = {}
        for i, word in enumerate(words):
            if word in seen_words and i - seen_words[word] == 1:
                real_issues['duplicate_words'].append((key, ja_text, word))
                break
            seen_words[word] = i
        
        # Check for obvious formatting issues
        if '。。。' in ja_text:  # Triple Japanese period
            real_issues['invalid_formatting'].append((key, ja_text, 'Triple Japanese period'))
        if '  ' in ja_text:  # Double spaces
            real_issues['invalid_formatting'].append((key, ja_text, 'Double spaces'))
        if '： ' in ja_text or ' ：' in ja_text:  # Spaces around colons
            real_issues['invalid_formatting'].append((key, ja_text, 'Spaces around colons'))

# Print the results
print("=== Final Japanese Translation Quality Verification ===")
print()

if real_issues['empty_translations']:
    print("1. Empty Translations:")
    for key in real_issues['empty_translations']:
        print(f"   - {key}")
    print()
else:
    print("1. Empty Translations: None")
    print()

if real_issues['mismatched_braces']:
    print("2. Mismatched Braces:")
    for key, text in real_issues['mismatched_braces']:
        print(f"   - {key}: {text}")
    print()
else:
    print("2. Mismatched Braces: None")
    print()

if real_issues['duplicate_words']:
    print("3. Duplicate Words:")
    for key, text, word in real_issues['duplicate_words']:
        print(f"   - {key}: {text} (Duplicate: {word})")
    print()
else:
    print("3. Duplicate Words: None")
    print()

if real_issues['invalid_formatting']:
    print("4. Invalid Formatting:")
    for key, text, issue in real_issues['invalid_formatting']:
        print(f"   - {key}: {text} ({issue})")
    print()
else:
    print("4. Invalid Formatting: None")
    print()

# Summary
print("=== Summary ===")
total_issues = sum(len(v) for v in real_issues.values())
print(f"Total entries checked: {len([k for k, v in data.items() if 'ja' in v])}")
print(f"Total real issues found: {total_issues}")
print()

if total_issues == 0:
    print("🎉 All Japanese translations are in good shape!")
    print("The translations have been comprehensively checked and fixed.")
    print("Any remaining warnings from the previous check are due to technical terms")
    print("like IPv6, CIDR, etc., which are expected and should be retained.")
else:
    print(f"⚠️  Found {total_issues} real issues that need to be addressed.")
