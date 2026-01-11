#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
国际化模块
提供翻译功能和语言切换支持
支持从外部JSON文件加载翻译数据
项目版本：v2.5.5
"""

import json
import os
import sys
from typing import cast


# 处理PyInstaller打包后的文件路径
def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径"""
    meipass: str | None = getattr(sys, '_MEIPASS', None)  # type: ignore[attr-defined]
    if meipass is not None:
        return os.path.join(meipass, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


_translations_file = get_resource_path('translations.json')


def _load_translations() -> dict[str, dict[str, str]] | None:
    """从JSON文件加载翻译数据"""
    try:
        with open(_translations_file, 'r', encoding='utf-8') as f:
            return cast(dict[str, dict[str, str]], json.load(f))
    except FileNotFoundError:
        print(f"翻译文件未找到: {_translations_file}")
        return None
    except json.JSONDecodeError as e:
        print(f"翻译文件解析错误: {e}")
        return None


_loaded_translations = _load_translations()

_DEFAULT_TRANSLATIONS: dict[str, dict[str, str]] = {
    "error": {"zh": "错误", "zh_tw": "錯誤", "en": "Error", "ja": "エラー", "ko": "오류"},
    "ok": {"zh": "确定", "zh_tw": "確定", "en": "OK", "ja": "OK", "ko": "확인"},
    "cancel": {"zh": "取消", "zh_tw": "取消", "en": "Cancel", "ja": "キャンセル", "ko": "취소"},
    "export": {"zh": "导出", "zh_tw": "匯出", "en": "Export", "ja": "エクスポート", "ko": "내보내기"},
    "subnet_planner": {"zh": "子网规划师", "zh_tw": "子網規劃師", "en": "Subnet Planner", "ja": "サブネット設計師", "ko": "서브넷 플래너"},
    "about": {"zh": "关于", "zh_tw": "關於", "en": "About", "ja": "アプリについて", "ko": "정보"},
    "close": {"zh": "关闭", "zh_tw": "關閉", "en": "Close", "ja": "閉じる", "ko": "닫기"}
}

_translations_dict: dict[str, dict[str, str]]

if _loaded_translations is None:
    _translations_dict = _DEFAULT_TRANSLATIONS
else:
    _translations_dict = _loaded_translations
    for key, value in _DEFAULT_TRANSLATIONS.items():
        if key not in _translations_dict:
            _translations_dict[key] = value

TRANSLATIONS: dict[str, dict[str, str]] = _translations_dict

_current_language: str = "zh"


def set_language(lang: str) -> None:
    """
    设置当前语言
    
    Args:
        lang: 语言代码，支持 "zh" (简体中文), "zh_tw" (繁体中文), "en" (英文), "ja" (日语) 和 "ko" (韩语)
    """
    global _current_language
    if lang in ["zh", "zh_tw", "en", "ja", "ko"]:
        _current_language = lang


def get_language() -> str:
    """
    获取当前语言
    
    Returns:
        当前语言代码 ("zh", "en" 或 "ja")
    """
    return _current_language


def translate(key: str, **kwargs: str) -> str:
    """
    翻译文本
    
    Args:
        key: 翻译键名
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    translation: dict[str, str] | None = TRANSLATIONS.get(key, {}) if TRANSLATIONS else {}
    if translation:
        text = translation.get(_current_language, key)
    else:
        text = key
    
    if kwargs and text:
        text = text.format(**kwargs)
    
    return text or key


# 导出 _ 作为 translate 的别名，用于标准 gettext 风格导入
_ = translate


def get_supported_languages() -> list[tuple[str, str]]:
    """
    获取支持的语言列表
    
    Returns:
        支持的语言列表，格式为 [(语言代码, 语言名称)]
    """
    return [
        ("zh", "简体中文"),
        ("zh_tw", "繁體中文"),
        ("en", "English"),
        ("ja", "日本語"),
        ("ko", "한국어")
    ]
