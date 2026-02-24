# 测试翻译文件加载的脚本
import json
import os

# 检查translations.json文件是否存在
translations_file = 'translations.json'
if os.path.exists(translations_file):
    print(f'文件存在: {translations_file}')
    
    # 尝试加载文件
    try:
        with open(translations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f'加载成功，包含 {len(data)} 个翻译键')
        
        # 检查几个关键翻译
        key = 'app_name'
        if key in data:
            print(f'\n检查 {key} 翻译:')
            for lang, value in data[key].items():
                print(f'  {lang}: {value}')
        
        # 检查是否有无效的JSON结构
        key = 'invalid_parent_network_format'
        if key in data:
            print(f'\n检查 {key} 翻译:')
            for lang, value in data[key].items():
                print(f'  {lang}: {value}')
                
    except json.JSONDecodeError as e:
        print(f'JSON解析错误: {e}')
        print(f'错误位置: 第 {e.lineno} 行，第 {e.colno} 列')
    except Exception as e:
        print(f'其他错误: {e}')
else:
    print(f'文件不存在: {translations_file}')
