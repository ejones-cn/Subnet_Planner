import json

with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print('JSON格式正确！')
