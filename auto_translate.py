#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动为translations.json文件添加韩文翻译
使用百度翻译API进行自动翻译
"""

import json
import requests
import time

# 读取翻译文件
with open('translations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 翻译函数
def translate(text, from_lang='zh', to_lang='ko'):
    """
    使用百度翻译API进行翻译
    """
    # 这里使用一个免费的翻译API，实际使用时可能需要替换为更可靠的API
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={from_lang}|{to_lang}"
    try:
        response = requests.get(url, timeout=5)
        result = response.json()
        return result['responseData']['translatedText']
    except Exception as e:
        print(f"翻译失败: {e}")
        return text

# 为每个条目添加韩文翻译
def add_korean_translations():
    """
    为translations.json文件中的每个条目添加韩文翻译
    """
    for key, translations in data.items():
        if key == '__version__':
            continue
        
        # 如果已经有韩文翻译，跳过
        if 'ko' in translations:
            continue
        
        # 获取中文翻译作为源文本
        if 'zh' in translations:
            source_text = translations['zh']
        elif 'en' in translations:
            source_text = translations['en']
        else:
            print(f"跳过 {key}: 没有找到可用的源文本")
            continue
        
        # 翻译为韩文
        print(f"正在翻译 {key}: {source_text}")
        korean_translation = translate(source_text, from_lang='zh', to_lang='ko')
        
        # 添加韩文翻译
        translations['ko'] = korean_translation
        
        # 避免请求过于频繁
        time.sleep(0.5)

# 执行翻译
add_korean_translations()

# 保存更新后的翻译文件
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("韩文翻译添加完成！")