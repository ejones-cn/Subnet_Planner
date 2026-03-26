import json

try:
    with open('translations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print('JSON文件格式正确')
except json.JSONDecodeError as e:
    print('错误位置:', e.pos)
    print('错误行号:', open('translations.json', 'r', encoding='utf-8').read()[: e.pos].count('\n') + 1)
    print('错误附近的内容:', repr(open('translations.json', 'r', encoding='utf-8').read()[max(0, e.pos - 50): e.pos + 50]))
