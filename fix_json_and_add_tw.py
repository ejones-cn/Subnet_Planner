#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复JSON语法错误并添加繁体中文支持
"""

import json
import os
import re

def fix_json_syntax(file_path):
    """修复JSON文件中的语法错误，包括：
    1. 删除多余的逗号
    2. 修复引号内的逗号问题
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: 删除多余的逗号（在}之后的逗号）
    # 例如: "key": { ... },, 改为 "key": { ... },
    pattern1 = r'\},\s*,\s*('\w+')'  # 匹配 "},," 然后是下一个键
    
    def replace_extra_commas(match):
        return '}, ' + match.group(1)
    
    content = re.sub(pattern1, replace_extra_commas, content)
    
    # 修复2: 删除行尾多余的逗号
    # 例如: "key": { ... },, 改为 "key": { ... },
    pattern2 = r'\},\s*,'  # 匹配 "},," 模式
    content = re.sub(pattern2, '},', content)
    
    # 修复3: 处理引号内的逗号问题
    # 例如: "content, with comma" 保持不变
    # 这部分比较复杂，我们使用JSON解析器来最终验证
    
    # 保存临时修复后的内容
    temp_path = file_path + '.temp'
    with open(temp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    try:
        # 尝试解析修复后的内容
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果解析成功，保存修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        # 删除临时文件
        os.remove(temp_path)
        
        print(f"已修复 {file_path} 的语法错误")
        return True
        
    except json.JSONDecodeError as e:
        print(f"错误: 修复后的JSON文件仍有语法错误 - {e}")
        # 查看错误位置附近的内容
        with open(temp_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        error_line = e.lineno
        start_line = max(0, error_line - 5)
        end_line = min(len(lines), error_line + 5)
        print(f"错误位置附近的内容 (行 {start_line+1} 到 {end_line}):")
        for i in range(start_line, end_line):
            print(f"{i+1}: {lines[i].rstrip()}")
        # 删除临时文件
        os.remove(temp_path)
        return False
    except Exception as e:
        print(f"错误: 处理文件时发生错误 - {e}")
        # 删除临时文件
        os.remove(temp_path)
        return False

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
    
    # 备份原始文件
    backup_path = translations_file + '.backup'
    import shutil
    shutil.copy2(translations_file, backup_path)
    print(f"已备份原始文件到 {backup_path}")
    
    # 修复语法错误
    if fix_json_syntax(translations_file):
        # 添加繁体中文翻译
        add_traditional_chinese(translations_file)
    
    print("所有操作已完成")

if __name__ == "__main__":
    main()