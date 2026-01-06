#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查translations.json文件中是否存在重复的键
"""

import json
import os


def find_duplicate_keys(data, parent_key='', duplicates=None):
    """
    递归查找JSON数据中的重复键
    
    参数:
    data: 要检查的JSON数据
    parent_key: 当前键的父键路径
    duplicates: 存储重复键的列表
    
    返回:
    包含重复键的列表
    """
    if duplicates is None:
        duplicates = []
    
    if isinstance(data, dict):
        seen_keys = set()
        for key, value in data.items():
            # 构建完整的键路径
            full_key = f"{parent_key}.{key}" if parent_key else key
            
            # 检查当前级别是否有重复键
            if key in seen_keys:
                duplicates.append(full_key)
            else:
                seen_keys.add(key)
            
            # 递归检查嵌套字典
            if isinstance(value, dict):
                find_duplicate_keys(value, full_key, duplicates)
            # 不检查列表，因为列表中的元素是有序的，不存在键的概念
    
    return duplicates


def main():
    """
    主函数
    """
    # 获取translations.json文件的路径
    translations_file = os.path.join(os.path.dirname(__file__), 'translations.json')
    
    try:
        # 读取并解析JSON文件
        with open(translations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 查找重复键
        duplicates = find_duplicate_keys(data)
        
        if duplicates:
            print(f"发现{len(duplicates)}个重复键:")
            for key in duplicates:
                print(f"  - {key}")
        else:
            print("未发现重复键")
            
    except FileNotFoundError:
        print(f"文件未找到: {translations_file}")
    except json.JSONDecodeError as e:
        print(f"JSON文件解析错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    main()
