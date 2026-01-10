# -*- coding: utf-8 -*-
"""
字体配置模块
集中管理所有语言的字体候选列表
项目版本：v2.5.4
"""

from typing import List, Tuple


class FontConfig:
    """字体配置类，集中管理所有语言的字体候选列表"""

    # 语言字体映射（合并后的统一数据结构）
    # 注意：Windows 11 中某些字体可能是 .ttc 格式而非 .ttf
    # 因此为这些字体同时提供 .ttf 和 .ttc 两种格式
    LANGUAGE_FONT_MAP = {
        "ko": [
            ("malgun.ttf", "Malgun Gothic"),
            ("malgun.ttc", "Malgun Gothic (TTC)"),
            ("malgunbd.ttf", "Malgun Gothic Bold"),
            ("malgunbd.ttc", "Malgun Gothic Bold (TTC)"),
            ("malgunsl.ttf", "Malgun Gothic Semilight"),
            ("malgunsl.ttc", "Malgun Gothic Semilight (TTC)"),
            ("batang.ttc", "Batang"),
            ("batangbd.ttc", "Batang Bold"),
            ("batangche.ttc", "Batang Che"),
            ("gulim.ttc", "Gulim"),
            ("gulimbd.ttc", "Gulim Bold"),
            ("gulimche.ttc", "Gulim Che"),
            ("dotum.ttc", "Dotum"),
            ("dotumbd.ttc", "Dotum Bold"),
            ("dotumche.ttc", "Dotum Che"),
            ("gungsuh.ttf", "Gungsuh"),
            ("gungsuhbd.ttf", "Gungsuh Bold"),
        ],
        "ja": [
            ("meiryo.ttc", "Meiryo"),
            ("meiryob.ttc", "Meiryo Bold"),
            ("meiryom.ttc", "Meiryo Medium"),
            ("msgothic.ttc", "MS Gothic"),
            ("msmincho.ttc", "MS Mincho"),
            ("msuigothic.ttc", "MS UI Gothic"),
            ("msuimincho.ttc", "MS UI Mincho"),
        ],
        "zh": [
            ("msyh.ttf", "Microsoft YaHei"),
            ("msyh.ttc", "Microsoft YaHei (TTC)"),
            ("msyhbd.ttf", "Microsoft YaHei Bold"),
            ("msyhbd.ttc", "Microsoft YaHei Bold (TTC)"),
            ("msyhl.ttf", "Microsoft YaHei Light"),
            ("msyhl.ttc", "Microsoft YaHei Light (TTC)"),
            ("simhei.ttf", "SimHei"),
            ("simsun.ttc", "SimSun"),
            ("simfang.ttf", "SimFang"),
            ("simkai.ttf", "SimKai"),
            ("simli.ttf", "SimLi"),
        ],
        "zh_tw": [
            ("msjh.ttc", "Microsoft JhengHei"),
            ("msjhbd.ttc", "Microsoft JhengHei Bold"),
            ("msjhl.ttc", "Microsoft JhengHei Light"),
            ("mingliu.ttc", "MingLiU"),
            ("pmingliu.ttc", "PMingLiU"),
            ("dfkai-sb.ttf", "DFKai-SB"),
            ("msyh.ttf", "Microsoft YaHei"),
            ("msyh.ttc", "Microsoft YaHei (TTC)"),
            ("msyhbd.ttf", "Microsoft YaHei Bold"),
            ("msyhbd.ttc", "Microsoft YaHei Bold (TTC)"),
            ("msyhl.ttf", "Microsoft YaHei Light"),
            ("msyhl.ttc", "Microsoft YaHei Light (TTC)"),
            ("simhei.ttf", "SimHei"),
            ("simsun.ttc", "SimSun"),
            ("simfang.ttf", "SimFang"),
            ("simkai.ttf", "SimKai"),
            ("simli.ttf", "SimLi"),
        ],
        "en": [
            ("segoeui.ttf", "Segoe UI"),
            ("segoeui.ttc", "Segoe UI (TTC)"),
            ("segoeuil.ttf", "Segoe UI Light"),
            ("segoeuisl.ttf", "Segoe UI Semilight"),
            ("segoeuisb.ttf", "Segoe UI Semibold"),
            ("segoeuib.ttf", "Segoe UI Bold"),
            ("arial.ttf", "Arial"),
            ("arialbd.ttf", "Arial Bold"),
            ("calibri.ttf", "Calibri"),
            ("verdana.ttf", "Verdana"),
            ("tahoma.ttf", "Tahoma"),
            ("times.ttf", "Times New Roman"),
            ("georgia.ttf", "Georgia"),
            ("cambria.ttc", "Cambria"),
            ("consola.ttf", "Consolas"),
            ("cour.ttf", "Courier New"),
        ],
    }

    # UI字体设置映射表（微软官方推荐）
    UI_FONT_SETTINGS = {
        "zh": ("微软雅黑", 10),
        "zh_tw": ("Microsoft JhengHei", 11),
        "ja": ("MS Gothic", 10),
        "ko": ("Malgun Gothic", 10),
        "default": ("Segoe UI", 10)
    }

    # PDF字体测试文本
    FONT_TEST_TEXTS = {
        "ko": "한글테스트",
        "ja": "テスト日本語",
        "zh": "测试简体中文",
        "zh_tw": "測試繁體中文",
        "en": "Test English"
    }

    @classmethod
    def get_font_candidates(cls, language: str) -> List[Tuple[str, str]]:
        """根据语言获取字体候选列表（完整信息）

        Args:
            language: 语言代码

        Returns:
            list: 字体候选列表 [(字体文件, 字体名称), ...]
        """
        return cls.LANGUAGE_FONT_MAP.get(language, cls.LANGUAGE_FONT_MAP.get("en", []))

    @classmethod
    def get_font_filenames(cls, language: str) -> List[str]:
        """根据语言获取字体文件名列表

        Args:
            language: 语言代码

        Returns:
            list: 字体文件名列表
        """
        candidates = cls.LANGUAGE_FONT_MAP.get(language, cls.LANGUAGE_FONT_MAP.get("en", []))
        return [font[0] for font in candidates]

    @classmethod
    def get_font_names(cls, language: str) -> List[str]:
        """根据语言获取字体名称列表

        Args:
            language: 语言代码

        Returns:
            list: 字体名称列表
        """
        candidates = cls.LANGUAGE_FONT_MAP.get(language, cls.LANGUAGE_FONT_MAP.get("en", []))
        return [font[1] for font in candidates]

    @classmethod
    def get_ui_font_settings(cls, language: str) -> Tuple[str, int]:
        """获取UI字体设置

        Args:
            language: 语言代码

        Returns:
            tuple: (字体名称, 字体大小)
        """
        return cls.UI_FONT_SETTINGS.get(language, cls.UI_FONT_SETTINGS["default"])

    @classmethod
    def get_font_test_text(cls, language: str) -> str:
        """获取字体测试文本

        Args:
            language: 语言代码

        Returns:
            str: 测试文本
        """
        return cls.FONT_TEST_TEXTS.get(language, "测试")

    @classmethod
    def get_all_supported_languages(cls) -> List[str]:
        """获取所有支持的语言列表

        Returns:
            list: 语言代码列表
        """
        return list(cls.LANGUAGE_FONT_MAP.keys())

    @classmethod
    def is_language_supported(cls, language: str) -> bool:
        """检查语言是否支持

        Args:
            language: 语言代码

        Returns:
            bool: 是否支持
        """
        return language in cls.LANGUAGE_FONT_MAP
