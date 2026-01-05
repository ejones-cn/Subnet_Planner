#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
为翻译文件添加繁体中文支持
通过复制简体中文翻译并添加为繁体中文翻译
"""

import json
import os

def add_traditional_chinese():
    """为翻译文件添加繁体中文支持"""
    # 翻译文件路径
    translations_file = 'translations.json'
    
    # 检查文件是否存在
    if not os.path.exists(translations_file):
        print(f"错误: 文件 {translations_file} 不存在")
        return False
    
    try:
        # 读取翻译文件
        with open(translations_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        # 为每个翻译键添加繁体中文翻译
        for key, value in translations.items():
            # 如果已经有繁体中文翻译，跳过
            if 'zh_tw' in value:
                continue
            
            # 如果有简体中文翻译，复制为繁体中文翻译
            if 'zh' in value:
                value['zh_tw'] = value['zh']
        
        # 保存更新后的翻译文件
        with open(translations_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
        
        print(f"成功为 {translations_file} 添加了繁体中文支持")
        return True
        
    except json.JSONDecodeError as e:
        print(f"错误: 解析 JSON 文件失败 - {e}")
        return False
    except Exception as e:
        print(f"错误: 处理文件时发生错误 - {e}")
        return False

if __name__ == "__main__":
    add_traditional_chinese()