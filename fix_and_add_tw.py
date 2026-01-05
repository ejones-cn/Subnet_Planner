#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复JSON语法错误并添加繁体中文支持
"""

import json
import os

def fix_json_syntax(file_path):
    """修复JSON文件中的语法错误"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复缺失的逗号
    # 这个方法可能不够完美，但可以处理大部分情况
    # 查找模式: "key": { ... }
    # 替换为: "key": { ... },
    import re
    
    # 匹配翻译条目，例如: "key": {"zh": "...", "en": "...", "ja": "..."}
    pattern = r'"(\w+)"\s*:\s*\{[^}]*\}'
    
    def add_comma(match):
        return match.group(0) + ','
    
    # 应用替换
    content = re.sub(pattern, add_comma, content)
    
    # 移除最后一个条目的逗号
    content = content.rstrip()
    if content.endswith(','):
        content = content[:-1]
    
    # 确保文件以正确的JSON格式结束
    if not content.endswith('}'):
        content = content + '}'
    
    # 保存修复后的内容
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已修复 {file_path} 的语法错误")

def add_traditional_chinese(file_path):
    """为修复后的JSON文件添加繁体中文支持"""
    try:
        # 读取修复后的翻译文件
        with open(file_path, 'r', encoding='utf-8') as f:
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
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)
        
        print(f"成功为 {file_path} 添加了繁体中文支持")
        return True
        
    except json.JSONDecodeError as e:
        print(f"错误: 解析修复后的JSON文件失败 - {e}")
        return False
    except Exception as e:
        print(f"错误: 处理文件时发生错误 - {e}")
        return False

def main():
    translations_file = 'translations.json'
    
    # 检查文件是否存在
    if not os.path.exists(translations_file):
        print(f"错误: 文件 {translations_file} 不存在")
        return False
    
    # 先修复语法错误
    fix_json_syntax(translations_file)
    
    # 然后添加繁体中文翻译
    add_traditional_chinese(translations_file)
    
    print("所有操作已完成")

if __name__ == "__main__":
    main()