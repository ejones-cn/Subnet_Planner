#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试新的错误模式：At most one '::' permitted in
"""

# 导入模块
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(__file__))

from ip_subnet_calculator import handle_ip_subnet_error
from i18n import set_language, _


def test_new_error_pattern():
    """
    测试新的错误模式
    """
    # 测试不同语言
    languages = ['zh', 'en', 'ja', 'zh_tw']
    
    # 测试新的错误信息
    new_error = "At most one '::' permitted in '2001:0db8:85a3:0000:0000:8a2e:0370'"
    
    print(f"\n=== 测试新的错误模式 ===")
    print(f"原始错误信息: {new_error}")
    print("=" * 50)
    
    for lang in languages:
        print(f"\n语言: {lang}")
        set_language(lang)
        
        # 创建一个模拟的ValueError对象
        error = ValueError(new_error)
        
        # 调用错误处理函数
        result = handle_ip_subnet_error(error)
        
        # 打印结果
        print(f"翻译结果: {result['error']}")


if __name__ == "__main__":
    test_new_error_pattern()
