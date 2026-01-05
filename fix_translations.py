import json
import re

# 读取并修复JSON文件
def fix_translations_file():
    # 先读取文件内容
    with open('translations.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复多余的逗号 (},, 或 ,,").
    # 移除连续的逗号
    content = re.sub(r'},,\s*"', r'}, "', content)
    content = re.sub(r'},,\s*}', r'}}', content)
    
    # 修复所有连续的逗号
    content = re.sub(r',+', r',', content)
    
    # 修复键值对末尾的多余逗号
    content = re.sub(r',\s*}', r'}', content)  
    content = re.sub(r',\s*\]', r']', content)
    
    # 尝试解析JSON
    try:
        translations = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        # 更详细的修复尝试
        # 移除所有连续的逗号
        content = re.sub(r',,+', r',', content)
        # 修复可能的逗号在}前的情况
        content = re.sub(r',\s*}', r'}', content)
        # 再次尝试解析
        translations = json.loads(content)
    
    # 确保所有翻译键都有完整的四种语言支持
    supported_languages = ['zh', 'zh_tw', 'en', 'ja']
    for key, values in translations.items():
        for lang in supported_languages:
            if lang not in values:
                # 如果缺少繁体中文，复制简体中文
                if lang == 'zh_tw' and 'zh' in values:
                    translations[key]['zh_tw'] = values['zh']
                # 如果缺少其他语言，使用英文作为默认
                elif lang == 'en' and 'en' not in values:
                    translations[key]['en'] = key.replace('_', ' ').title()
                # 如果缺少日语，尝试使用英文作为默认
                elif lang == 'ja' and 'ja' not in values:
                    translations[key]['ja'] = values.get('en', key)
                # 如果缺少简体中文，使用英文作为默认
                elif lang == 'zh' and 'zh' not in values:
                    translations[key]['zh'] = values.get('en', key)
    
    # 保存修复后的JSON文件
    with open('translations.json', 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=4)
    
    print("翻译文件修复完成！")
    
    # 验证修复后的文件
    try:
        with open('translations.json', 'r', encoding='utf-8') as f:
            json.load(f)
        print("验证通过：JSON格式正确！")
    except json.JSONDecodeError as e:
        print(f"验证失败：JSON格式仍有错误: {e}")

if __name__ == "__main__":
    fix_translations_file()