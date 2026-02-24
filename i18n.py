#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
国际化模块
提供翻译功能和语言切换支持
支持从外部JSON文件加载翻译数据
"""

import json
import os
import sys
from typing import cast
from version import get_version

__version__ = get_version()

# 提前导入ctypes，以便类型检查器能识别其类型
try:
    import ctypes
except ImportError:
    # 在非Windows系统上，ctypes可能不可用
    ctypes = None


# 处理PyInstaller打包后的文件路径
def get_resource_path(relative_path: str) -> str:
    """获取资源文件的绝对路径"""
    meipass: str | None = getattr(sys, '_MEIPASS', None)
    if meipass is not None:
        return os.path.join(meipass, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


class Translator:
    """翻译类，提供简洁高效的翻译功能"""
    
    def __init__(self):
        self._current_language: str = self._detect_system_language()
        self._translations_file: str = get_resource_path('translations.json')
        # 默认翻译字典 - 只保留最基本的翻译键作为最后的回退
        # 完整的翻译内容已经移到了 translations.json 文件中
        self._default_translations: dict[str, dict[str, str]] = {
            "error": {"zh": "错误", "en": "Error", "zh_tw": "錯誤", "ja": "エラー", "ko": "오류"},
            "ok": {"zh": "确定", "en": "OK", "zh_tw": "確定", "ja": "OK", "ko": "확인"},
            "cancel": {"zh": "取消", "en": "Cancel", "zh_tw": "取消", "ja": "キャンセル", "ko": "취소"},
            "about": {"zh": "关于", "en": "About", "zh_tw": "關於", "ja": "アプリについて", "ko": "정보"},
            "close": {"zh": "关闭", "en": "Close", "zh_tw": "關閉", "ja": "閉じる", "ko": "닫기"}
        }
        self._translations: dict[str, dict[str, str]] = self._load_translations()
    
    def _detect_system_language(self) -> str:
        """检测系统语言
        
        Returns:
            检测到的语言代码，如果无法检测则返回默认语言 "zh"
        """
        try:
            # 尝试使用 locale 模块检测系统语言
            import locale
            lang_code, _ = locale.getdefaultlocale()
            if lang_code:
                # 处理语言代码映射
                lang_code = lang_code.lower()
                if 'zh' in lang_code:
                    if 'tw' in lang_code or 'hk' in lang_code or 'mo' in lang_code:
                        return 'zh_tw'
                    return 'zh'
                elif 'en' in lang_code:
                    return 'en'
                elif 'ja' in lang_code:
                    return 'ja'
                elif 'ko' in lang_code:
                    return 'ko'
            
            # 尝试使用 ctypes 检测 Windows 系统语言
            try:
                if ctypes is not None:
                    lcid = cast(int, ctypes.windll.kernel32.GetUserDefaultUILanguage())
                    # LCID 映射
                    lcid_map = {
                        0x804: 'zh',      # 中文简体
                        0x404: 'zh_tw',   # 中文繁体
                        0x409: 'en',      # 英文
                        0x411: 'ja',      # 日语
                        0x412: 'ko'       # 韩语
                    }
                    if lcid in lcid_map:
                        return lcid_map[lcid]
            except (ImportError, AttributeError):
                # 非 Windows 系统或无法使用 ctypes
                pass
        except Exception:
            # 任何异常都返回默认语言
            pass
        
        return 'zh'
    
    def _load_translations(self) -> dict[str, dict[str, str]]:
        """从JSON文件加载翻译数据"""
        try:
            with open(self._translations_file, 'r', encoding='utf-8') as f:
                loaded = cast(dict[str, dict[str, str]], json.load(f))
                # 合并默认翻译和加载的翻译
                for key, value in self._default_translations.items():
                    if key not in loaded:
                        loaded[key] = value
                return loaded
        except (FileNotFoundError, json.JSONDecodeError):
            # 如果加载失败，使用默认翻译
            return self._default_translations
    
    def set_language(self, lang: str) -> None:
        """设置当前语言
        
        Args:
            lang: 语言代码，支持 "zh" (简体中文), "zh_tw" (繁体中文), "en" (英文), "ja" (日语) 和 "ko" (韩语)
        """
        if lang in ["zh", "zh_tw", "en", "ja", "ko"]:
            self._current_language = lang
    
    def get_language(self) -> str:
        """获取当前语言
        
        Returns:
            当前语言代码
        """
        return self._current_language
    
    def translate(self, key: str, **kwargs: str) -> str:
        """翻译文本
        
        Args:
            key: 翻译键名
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        translations = self._translations.get(key, {})
        text = translations.get(self._current_language, key)
        if kwargs and text:
            text = text.format(**kwargs)
        return text or key
    
    def get_supported_languages(self) -> list[tuple[str, str]]:
        """获取支持的语言列表
        
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
    
    @property
    def translations(self) -> dict[str, dict[str, str]]:
        """获取翻译字典（公共访问接口）"""
        return self._translations


# 创建单例实例
translator = Translator()


def set_language(lang: str) -> None:
    """设置当前语言"""
    translator.set_language(lang)


def get_language() -> str:
    """获取当前语言"""
    return translator.get_language()


def translate(key: str, **kwargs: str) -> str:
    """翻译文本"""
    return translator.translate(key, **kwargs)


# 导出 _ 作为 translate 的别名，用于标准 gettext 风格导入
_ = translate


def get_supported_languages() -> list[tuple[str, str]]:
    """获取支持的语言列表"""
    return translator.get_supported_languages()


# 导出TRANSLATIONS常量，保持向后兼容
TRANSLATIONS = translator.translations
