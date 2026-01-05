#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
国际化模块
提供翻译功能和语言切换支持
支持从外部JSON文件加载翻译数据
项目版本：v2.5.3
"""

import json
import os
import sys


# 处理PyInstaller打包后的文件路径
def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境下的路径
    return os.path.join(os.path.dirname(__file__), relative_path)


_translations_file = get_resource_path('translations.json')



def _load_translations():
    """从JSON文件加载翻译数据"""
    try:
        with open(_translations_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"翻译文件未找到: {_translations_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"翻译文件解析错误: {e}")
        return None


TRANSLATIONS = _load_translations()



_DEFAULT_TRANSLATIONS = {
    "error": {"zh": "错误", "zh_tw": "錯誤", "en": "Error", "ja": "エラー"},
    "ok": {"zh": "确定", "zh_tw": "確定", "en": "OK", "ja": "OK"},
    "cancel": {"zh": "取消", "zh_tw": "取消", "en": "Cancel", "ja": "キャンセル"},
    "export": {"zh": "导出", "zh_tw": "匯出", "en": "Export", "ja": "エクスポート"},
    "subnet_planner": {"zh": "子网规划师", "zh_tw": "子網規劃師", "en": "Subnet Planner", "ja": "サブネット設計師"},
    "about": {"zh": "关于", "zh_tw": "關於", "en": "About", "ja": "アプリについて"},
    "close": {"zh": "关闭", "zh_tw": "關閉", "en": "Close", "ja": "閉じる"}
}

if TRANSLATIONS is None:
    TRANSLATIONS = _DEFAULT_TRANSLATIONS

_current_language = "zh"


def set_language(lang):
    """
    设置当前语言
    
    Args:
        lang: 语言代码，支持 "zh" (中文), "zh_tw" (繁体中文), "en" (英文) 和 "ja" (日语)
    """
    global _current_language
    if lang in ["zh", "zh_tw", "en", "ja"]:
        _current_language = lang


def get_language():
    """
    获取当前语言
    
    Returns:
        当前语言代码 ("zh", "en" 或 "ja")
    """
    return _current_language


def _(key, **kwargs):
    """
    翻译函数
    
    Args:
        key: 翻译键名
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    translation = TRANSLATIONS.get(key, {})
    text = translation.get(_current_language, key)
    
    if kwargs:
        text = text.format(**kwargs)
    
    return text


def get_supported_languages():
    """
    获取支持的语言列表
    
    Returns:
        支持的语言列表，格式为 [(语言代码, 语言名称)]
    """
    return [
        ("zh", "简体中文"),
        ("zh_tw", "繁體中文"),
        ("en", "English"),
        ("ja", "日本語")
    ]
