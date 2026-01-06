#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复translations.json文件中被错误设置为日语的韩语翻译
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
    url = f"https://api.mymemory.translated.net/get?q={text}&langpair={from_lang}|{to_lang}"
    try:
        response = requests.get(url, timeout=5)
        result = response.json()
        return result['responseData']['translatedText']
    except Exception as e:
        print(f"翻译失败: {e}")
        return text

# 检测日语字符的正则表达式
# 日语字符包括平假名、片假名和汉字
import re
japanese_pattern = re.compile(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]')

# 修复韩语翻译
def fix_korean_translations():
    """
    修复translations.json文件中被错误设置为日语的韩语翻译
    """
    fixed_count = 0
    
    for key, translations in data.items():
        if key == '__version__':
            continue
        
        # 检查是否有韩语翻译
        if 'ko' in translations:
            korean_translation = translations['ko']
            
            # 检查韩语翻译中是否包含日语字符
            if japanese_pattern.search(korean_translation):
                print(f"发现错误翻译: {key} 的韩语翻译包含日语字符: {korean_translation}")
                
                # 获取中文翻译作为源文本
                if 'zh' in translations:
                    source_text = translations['zh']
                elif 'en' in translations:
                    source_text = translations['en']
                else:
                    print(f"跳过 {key}: 没有找到可用的源文本")
                    continue
                
                # 重新翻译为韩语
                print(f"正在重新翻译 {key}: {source_text}")
                new_korean_translation = translate(source_text, from_lang='zh', to_lang='ko')
                
                # 更新韩语翻译
                translations['ko'] = new_korean_translation
                fixed_count += 1
                
                # 避免请求过于频繁
                time.sleep(0.5)
    
    print(f"修复完成，共修复了 {fixed_count} 个错误翻译")

# 执行修复
fix_korean_translations()

# 保存更新后的翻译文件
with open('translations.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("韩语翻译修复完成！")