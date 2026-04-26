# -*- coding: utf-8 -*-
"""
字体配置模块
集中管理所有语言的字体候选列表
"""

from typing import Any

from version import get_version
from i18n import get_language

__version__ = get_version()


class FontConfig:
    """字体配置类，集中管理所有语言的字体候选列表"""

    LANGUAGE_FONT_MAP: dict[str, list[tuple[str, str]]] = {
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

    UI_FONT_SETTINGS: dict[str, tuple[str, int]] = {
        "zh": ("微软雅黑", 11),
        "zh_tw": ("Microsoft JhengHei", 11),
        "ja": ("Meiryo", 10),
        "ko": ("Malgun Gothic", 10),
        "default": ("Segoe UI", 10)
    }
    
    # Canvas 专用字体配置
    # Tk Canvas create_text 使用 Tk 内置文本渲染引擎，不会像 ttk 控件那样
    # 在字体回退时进行度量同步，导致回退字符与主字体字符粗细大小不一致。
    #
    # 设计原则：
    # - 中文系统：使用"微软雅黑"，全面覆盖简体中文字符，避免回退
    # - 日语/韩语系统：也使用"微软雅黑"，因为软件界面语言是中文，
    #   拓扑图主要显示中文内容（中文字符回退少，即使回退也与界面一致）
    # - 如果需要显示日文/韩文，会回退到系统字体，与界面回退行为一致
    #
    # 注意：在纯日语/韩语软件环境下，可能需要不同的字体配置
    CANVAS_FONT_SETTINGS: dict[str, tuple[str, int]] = {
        "zh": ("微软雅黑", 11),
        "zh_tw": ("Microsoft JhengHei", 11),
        "ja": ("微软雅黑", 11),
        "ko": ("微软雅黑", 11),
        "default": ("Segoe UI", 11)
    }
    
    PIN_BUTTON_FONT_SIZE_SETTINGS: dict[str, int] = {
        "zh": 10,
        "zh_tw": 10,
        "ja": 10,  # 统一为10，避免语言切换时图标大小变化
        "ko": 10,
        "default": 10
    }
    
    # 钉住按钮专用字体设置（使用支持emoji的字体）
    PIN_BUTTON_FONT_FAMILY_SETTINGS: dict[str, str] = {
        "zh": "Segoe UI Symbol",
        "zh_tw": "Segoe UI Symbol",
        "ja": "Segoe UI Symbol",  # 使用Symbol字体确保日语下emoji正常显示
        "ko": "Segoe UI Symbol",
        "default": "Segoe UI Symbol"
    }
    
    FUNCTION_BUTTON_FONT_SIZE_SETTINGS: dict[str, int] = {
        "zh": 10,
        "zh_tw": 11,
        "ja": 10,
        "ko": 10,
        "default": 9
    }
    
    INFO_BAR_FONT_SIZE_SETTINGS: dict[str, int] = {
        "zh": 10,
        "zh_tw": 10,
        "ja": 10,
        "ko": 10,
        "default": 9
    }
    
    # 移动按钮字体设置映射表（仅设置字体，不设置大小）
    MOVE_BUTTON_FONT_SETTINGS: dict[str, str] = {
        "zh": "Segoe UI",
        "zh_tw": "Segoe UI",
        "ja": "Segoe UI",
        "ko": "Segoe UI",
        "default": "Segoe UI"
    }
    
    # 启动画面字体设置
    SPLASH_FONT_SETTINGS: dict[str, dict[str, Any]] = {
        "zh": {
            "font": "微软雅黑",
            "sizes": {
                "title": 32,
                "version": 14,
                "status": 12,
                "loading": 12
            }
        },
        "zh_tw": {
            "font": "Microsoft JhengHei",
            "sizes": {
                "title": 32,
                "version": 14,
                "status": 12,
                "loading": 12
            }
        },
        "ja": {
            "font": "Meiryo",
            "sizes": {
                "title": 30,
                "version": 12,
                "status": 10,
                "loading": 10
            }
        },
        "ko": {
            "font": "Malgun Gothic",
            "sizes": {
                "title": 26,
                "version": 12,
                "status": 10,
                "loading": 10
            }
        },
        "default": {
            "font": "Segoe UI",
            "sizes": {
                "title": 24,
                "version": 11,
                "status": 9,
                "loading": 9
            }
        }
    }

    FONT_TEST_TEXTS: dict[str, str] = {
        "ko": "한글테스트",
        "ja": "テスト日本語",
        "zh": "测试简体中文",
        "zh_tw": "測試繁體中文",
        "en": "Test English"
    }

    @classmethod
    def get_font_candidates(cls, language: str) -> list[tuple[str, str]]:
        """根据语言获取字体候选列表（完整信息）"""
        return cls.LANGUAGE_FONT_MAP.get(language, cls.LANGUAGE_FONT_MAP.get("en", []))

    @classmethod
    def get_font_filenames(cls, language: str) -> list[str]:
        """根据语言获取字体文件名列表"""
        candidates = cls.LANGUAGE_FONT_MAP.get(language, cls.LANGUAGE_FONT_MAP.get("en", []))
        return [font[0] for font in candidates]

    @classmethod
    def get_font_names(cls, language: str) -> list[str]:
        """根据语言获取字体名称列表"""
        candidates = cls.LANGUAGE_FONT_MAP.get(language, cls.LANGUAGE_FONT_MAP.get("en", []))
        return [font[1] for font in candidates]

    @classmethod
    def get_ui_font_settings(cls, language: str) -> tuple[str, int]:
        """获取UI字体设置"""
        return cls.UI_FONT_SETTINGS.get(language, cls.UI_FONT_SETTINGS["default"])

    @classmethod
    def get_canvas_font_settings(cls, language: str) -> tuple[str, int]:
        """获取Canvas字体设置
        
        Canvas create_text 使用 Tk 内置文本渲染引擎，不会像 ttk 控件那样
        在字体回退时进行度量同步。因此需要使用具有全面 CJK 覆盖的字体，
        避免因字体回退导致的字符粗细大小不一致问题。
        
        Args:
            language: 当前语言代码
            
        Returns:
            tuple: (字体名称, 字体大小)
        """
        return cls.CANVAS_FONT_SETTINGS.get(language, cls.CANVAS_FONT_SETTINGS["default"])

    @classmethod
    def get_font_test_text(cls, language: str) -> str:
        """获取字体测试文本"""
        return cls.FONT_TEST_TEXTS.get(language, "测试")

    @classmethod
    def get_all_supported_languages(cls) -> list[str]:
        """获取所有支持的语言列表"""
        return list(cls.LANGUAGE_FONT_MAP.keys())

    @classmethod
    def is_language_supported(cls, language: str) -> bool:
        """检查语言是否支持"""
        return language in cls.LANGUAGE_FONT_MAP
    
    @classmethod
    def lookup_pin_button_font_size(cls, language: str) -> int:
        """获取钉住按钮的字体大小设置"""
        return cls.PIN_BUTTON_FONT_SIZE_SETTINGS.get(language, cls.PIN_BUTTON_FONT_SIZE_SETTINGS["default"])
    
    @classmethod
    def lookup_pin_button_font_family(cls, language: str) -> str:
        """获取钉住按钮的字体家族设置（使用支持emoji的字体）"""
        return cls.PIN_BUTTON_FONT_FAMILY_SETTINGS.get(language, cls.PIN_BUTTON_FONT_FAMILY_SETTINGS["default"])
    
    @classmethod
    def lookup_function_button_font_size(cls, language: str) -> int:
        """获取功能按钮的字体大小设置（添加、删除、撤销、移动、导入等）"""
        return cls.FUNCTION_BUTTON_FONT_SIZE_SETTINGS.get(language, cls.FUNCTION_BUTTON_FONT_SIZE_SETTINGS["default"])
    
    @classmethod
    def lookup_info_bar_font_size(cls, language: str) -> int:
        """获取信息栏的字体大小设置"""
        return cls.INFO_BAR_FONT_SIZE_SETTINGS.get(language, cls.INFO_BAR_FONT_SIZE_SETTINGS["default"])
    
    @classmethod
    def lookup_move_button_font(cls, language: str) -> str:
        """获取移动按钮的字体设置（仅字体，不包含大小）"""
        return cls.MOVE_BUTTON_FONT_SETTINGS.get(language, cls.MOVE_BUTTON_FONT_SETTINGS["default"])
    
    @classmethod
    def get_splash_font_family(cls, language: str) -> str:
        """获取启动画面的字体家族设置
        
        Args:
            language: 当前语言
            
        Returns:
            str: 字体家族名称
        """
        lang_settings = cls.SPLASH_FONT_SETTINGS.get(language, cls.SPLASH_FONT_SETTINGS["default"])
        return lang_settings.get("font", "Segoe UI")
    
    @classmethod
    def get_splash_font_size(cls, language: str, font_type: str) -> int:
        """获取启动画面的字体大小设置
        
        Args:
            language: 当前语言
            font_type: 字体类型，支持 "title", "version", "status", "loading"
            
        Returns:
            int: 字体大小
        """
        lang_settings = cls.SPLASH_FONT_SETTINGS.get(language, cls.SPLASH_FONT_SETTINGS["default"])
        sizes = lang_settings.get("sizes", {})
        return sizes.get(font_type, 12)
    
    @classmethod
    def get_pin_button_font_size(cls) -> int:
        """获取钉住按钮的字体大小设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.PIN_BUTTON_FONT_SIZE_SETTINGS.get(
            current_language, 
            cls.PIN_BUTTON_FONT_SIZE_SETTINGS["default"]
        )
    
    @classmethod
    def get_pin_button_font_family(cls) -> str:
        """获取钉住按钮的字体家族设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.PIN_BUTTON_FONT_FAMILY_SETTINGS.get(
            current_language, 
            cls.PIN_BUTTON_FONT_FAMILY_SETTINGS["default"]
        )
    
    @classmethod
    def get_function_button_font_size(cls) -> int:
        """获取功能按钮的字体大小设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.FUNCTION_BUTTON_FONT_SIZE_SETTINGS.get(
            current_language, 
            cls.FUNCTION_BUTTON_FONT_SIZE_SETTINGS["default"]
        )
    
    @classmethod
    def get_info_bar_font_size(cls) -> int:
        """获取信息栏的字体大小设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.INFO_BAR_FONT_SIZE_SETTINGS.get(
            current_language, 
            cls.INFO_BAR_FONT_SIZE_SETTINGS["default"]
        )
    
    @classmethod
    def get_move_button_font(cls) -> str:
        """获取移动按钮的字体设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.MOVE_BUTTON_FONT_SETTINGS.get(
            current_language, 
            cls.MOVE_BUTTON_FONT_SETTINGS["default"]
        )
    
    @classmethod
    def get_splash_font_family_current(cls) -> str:
        """获取启动画面的字体家族设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.get_splash_font_family(current_language)
    
    @classmethod
    def get_splash_font_size_current(cls, font_type: str) -> int:
        """获取启动画面的字体大小设置（自动使用当前语言）"""
        current_language = get_language()
        return cls.get_splash_font_size(current_language, font_type)


def get_pin_button_font_size() -> int:
    """获取钉住按钮的字体大小设置（自动使用当前语言）"""
    return FontConfig.lookup_pin_button_font_size(get_language())


def get_pin_button_font_family() -> str:
    """获取钉住按钮的字体家族设置（自动使用当前语言）"""
    return FontConfig.lookup_pin_button_font_family(get_language())


def get_function_button_font_size() -> int:
    """获取功能按钮的字体大小设置（自动使用当前语言）"""
    return FontConfig.lookup_function_button_font_size(get_language())


def get_info_bar_font_size() -> int:
    """获取信息栏的字体大小设置（自动使用当前语言）"""
    return FontConfig.lookup_info_bar_font_size(get_language())


def get_move_button_font() -> str:
    """获取移动按钮的字体设置（自动使用当前语言）"""
    return FontConfig.lookup_move_button_font(get_language())


def get_splash_font_family() -> str:
    """获取启动画面的字体家族设置（自动使用当前语言）"""
    return FontConfig.get_splash_font_family_current()


def get_splash_font_size(font_type: str) -> int:
    """获取启动画面的字体大小设置（自动使用当前语言）"""
    return FontConfig.get_splash_font_size_current(font_type)
