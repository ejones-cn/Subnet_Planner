#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 translations.json 文件中是否有重复的翻译键
"""

import json
import collections


def check_duplicate_keys():
    """检查翻译文件中的重复键"""
    try:
        with open('translations.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keys = list(data.keys())
        duplicate_keys = [key for key, count in collections.Counter(keys).items() if count > 1]
        
        if duplicate_keys:
            print(f"发现 {len(duplicate_keys)} 个重复的翻译键：")
            for key in duplicate_keys:
                count = keys.count(key)
                print(f"  - {key}: 出现 {count} 次")
        else:
            print("✓ 未发现重复的翻译键")
            
    except json.JSONDecodeError as e:
        print(f"解析JSON文件失败：{e}")
    except FileNotFoundError:
        print("translations.json 文件未找到")
    except Exception as e:
        print(f"检查过程中发生错误：{e}")


if __name__ == "__main__":
    check_duplicate_keys()
