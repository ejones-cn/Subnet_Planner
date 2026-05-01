#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块
提供统一的配置管理功能，支持多种配置类型、版本控制和向后兼容
"""

import json
import os
from typing import cast


class ConfigManager:
    """配置管理器类"""
    
    # 当前配置版本
    CURRENT_VERSION: str = "1.0"

    DEFAULT_CONFIG: dict[str, object] = {
        "version": CURRENT_VERSION,
        "language": "zh",
        "window": {
            "width": 1050,
            "height": 950,
            "maximized": False,
            "x": None,
            "y": None
        },
        "auto_backup": {
            "enabled": True,
            "frequency": "weekly"
        },
        "ui": {
            "theme": "vista",
            "font_size": 11,
            "tab_order": []
        },
        "recent_files": [],
        "last_used_network": None
    }
    
    SUPPORTED_LANGUAGES: list[str] = ["zh", "zh_tw", "en", "ja", "ko"]

    SUPPORTED_BACKUP_FREQUENCIES: list[str] = ["disabled", "hourly", "daily", "weekly", "monthly"]

    SUPPORTED_THEMES: list[str] = ["default", "dark", "light"]
    
    def __init__(self, config_file: str | None = None):
        """初始化配置管理器
        
        Args:
            config_file: 配置文件路径，默认为 SubnetPlanner_config.json
        """
        if config_file is None:
            from window_utils import get_app_directory
            self._config_file: str = os.path.join(get_app_directory(), 'SubnetPlanner_config.json')
        else:
            self._config_file = config_file
        
        self._config: dict[str, object] = self._load_config()
    
    def _translate(self, translation_key: str, **kwargs: str) -> str:
        """延迟导入翻译函数，避免循环导入
        
        Args:
            translation_key: 翻译键名
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本，如果导入失败则返回键名
        """
        try:
            from i18n import translate
            return translate(translation_key, **kwargs)
        except (ImportError, Exception):
            return translation_key
    
    def _load_config(self) -> dict[str, object]:
        """加载配置文件
        
        Returns:
            配置字典，如果加载失败则返回默认配置
        """
        if not os.path.exists(self._config_file):
            return self._create_default_config()
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                config = cast(dict[str, object], json.load(f))
            
            return self._migrate_config(config)
        
        except json.JSONDecodeError as e:
            print(self._translate("config_parse_error", error=str(e)))
            return self._create_default_config()
        except Exception as e:
            print(self._translate("config_load_failed", error=str(e)))
            return self._create_default_config()
    
    def _create_default_config(self) -> dict[str, object]:
        """创建默认配置"""
        return cast(dict[str, object], json.loads(json.dumps(self.DEFAULT_CONFIG)))
    
    def _migrate_config(self, config: dict[str, object]) -> dict[str, object]:
        """迁移配置到最新版本
        
        Args:
            config: 旧版本配置
            
        Returns:
            迁移后的新版本配置
        """
        result = self._create_default_config()
        current_version = config.get("version", "0.0")
        
        if current_version == "0.0" or current_version == "1.0":
            if 'language' in config:
                lang = config['language']
                if lang in self.SUPPORTED_LANGUAGES:
                    result['language'] = lang
            
            if 'window' in config:
                window = config['window']
                if isinstance(window, dict):
                    result_window = result.get('window')
                    if isinstance(result_window, dict):
                        if 'width' in window:
                            w = window['width']
                            if isinstance(w, int):
                                result_window['width'] = w
                        if 'height' in window:
                            h = window['height']
                            if isinstance(h, int):
                                result_window['height'] = h
                        if 'maximized' in window:
                            m = window['maximized']
                            if isinstance(m, bool):
                                result_window['maximized'] = m
            
            if 'auto_backup' in config:
                auto_backup = config['auto_backup']
                if isinstance(auto_backup, dict):
                    result_backup = result.get('auto_backup')
                    if isinstance(result_backup, dict):
                        if 'enabled' in auto_backup:
                            en = auto_backup['enabled']
                            if isinstance(en, bool):
                                result_backup['enabled'] = en
                        if 'frequency' in auto_backup:
                            freq = auto_backup['frequency']
                            if freq in self.SUPPORTED_BACKUP_FREQUENCIES:
                                result_backup['frequency'] = freq
            
            if 'ui' in config:
                ui = config['ui']
                if isinstance(ui, dict):
                    result_ui = result.get('ui')
                    if isinstance(result_ui, dict):
                        if 'theme' in ui:
                            theme = ui['theme']
                            if isinstance(theme, str):
                                result_ui['theme'] = theme
                        if 'font_size' in ui:
                            fs = ui['font_size']
                            if isinstance(fs, int):
                                result_ui['font_size'] = fs
                        if 'tab_order' in ui:
                            to = ui['tab_order']
                            if isinstance(to, list):
                                result_ui['tab_order'] = to
            
            if 'recent_files' in config:
                rf = config['recent_files']
                if isinstance(rf, list):
                    result['recent_files'] = [f for f in rf if isinstance(f, str)]
            
            if 'last_used_network' in config:
                result['last_used_network'] = config['last_used_network']
        
        result['version'] = self.CURRENT_VERSION
        
        return result
    
    def _validate_config(self, config: dict[str, object]) -> bool:
        """验证配置的完整性和有效性
        
        Args:
            config: 待验证的配置
            
        Returns:
            配置是否有效
        """
        try:
            # 检查版本号
            if 'version' not in config or not isinstance(config['version'], str):
                return False
            
            # 检查语言
            if 'language' not in config or config['language'] not in self.SUPPORTED_LANGUAGES:
                return False
            
            # 检查窗口配置
            if 'window' not in config or not isinstance(config['window'], dict):
                return False
            window = config['window']
            if 'width' not in window or not isinstance(window['width'], int):
                return False
            if 'height' not in window or not isinstance(window['height'], int):
                return False
            if 'maximized' not in window or not isinstance(window['maximized'], bool):
                return False
            
            # 检查自动备份配置
            if 'auto_backup' not in config or not isinstance(config['auto_backup'], dict):
                return False
            auto_backup = config['auto_backup']
            if 'enabled' not in auto_backup or not isinstance(auto_backup['enabled'], bool):
                return False
            if 'frequency' not in auto_backup or auto_backup['frequency'] not in self.SUPPORTED_BACKUP_FREQUENCIES:
                return False
            
            # 检查UI配置
            if 'ui' not in config or not isinstance(config['ui'], dict):
                return False
            ui = config['ui']
            if 'theme' not in ui or not isinstance(ui['theme'], str):
                return False
            if 'font_size' not in ui or not isinstance(ui['font_size'], int):
                return False
            if 'tab_order' in ui and not isinstance(ui['tab_order'], list):
                return False
            
            # 检查最近文件列表
            if 'recent_files' not in config or not isinstance(config['recent_files'], list):
                return False
            
            return True
        except Exception as e:
            print(self._translate("config_validation_failed", error=str(e)))
            return False
    
    def _save_config(self) -> bool:
        """保存配置到文件
        
        Returns:
            是否保存成功
        """
        try:
            # 验证配置
            if not self._validate_config(self._config):
                print(self._translate("config_validation_failed_save"))
                return False
            
            # 确保目录存在
            config_dir = os.path.dirname(self._config_file)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(self._translate("config_save_failed", error=str(e)))
            return False
    
    def get(self, key: str, default: object = None) -> object:
        """获取配置项
        
        Args:
            key: 配置键名，支持点分隔符（如 'window.width'）
            default: 默认值
            
        Returns:
            配置值
        """
        try:
            keys = key.split('.')
            value: object = self._config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except Exception as e:
            print(self._translate("config_get_failed", key=key, error=str(e)))
            return default
    
    def set(self, key: str, value: object) -> bool:
        """设置配置项
        
        Args:
            key: 配置键名，支持点分隔符（如 'window.width'）
            value: 配置值
            
        Returns:
            是否设置成功
        """
        try:
            keys = key.split('.')
            config: object = self._config
            
            for i, k in enumerate(keys[:-1]):
                if isinstance(config, dict):
                    if k not in config:
                        config[k] = {}
                    elif not isinstance(config[k], dict):
                        print(self._translate("config_path_conflict", key='.'.join(keys[:i + 1])))
                        return False
                    config = config[k]
            
            if isinstance(config, dict):
                last_key = keys[-1]
                config[last_key] = value
            
            return self._save_config()
        except Exception as e:
            print(self._translate("config_set_failed", key=key, error=str(e)))
            return False
    
    def get_language(self) -> str:
        """获取当前语言设置
        
        Returns:
            语言代码
        """
        result = self.get('language', 'zh')
        return result if isinstance(result, str) else 'zh'
    
    def set_language(self, lang: str) -> bool:
        """设置语言
        
        Args:
            lang: 语言代码
            
        Returns:
            是否设置成功
        """
        if lang not in self.SUPPORTED_LANGUAGES:
            print(self._translate("unsupported_language", lang=lang))
            return False
        return self.set('language', lang)
    
    def get_window_size(self) -> tuple[int, int]:
        """获取窗口大小
        
        Returns:
            (宽度, 高度)
        """
        width_val = self.get('window.width', 1200)
        height_val = self.get('window.height', 800)
        width = width_val if isinstance(width_val, int) else 1200
        height = height_val if isinstance(height_val, int) else 800
        return (width, height)
    
    def set_window_size(self, width: int, height: int) -> bool:
        """设置窗口大小
        
        Args:
            width: 宽度
            height: 高度
            
        Returns:
            是否设置成功
        """
        if width < 800 or height < 600:
            print(self._translate("window_size_too_small"))
            return False
        
        success1 = self.set('window.width', width)
        success2 = self.set('window.height', height)
        return success1 and success2
    
    def get_window_maximized(self) -> bool:
        """获取窗口最大化状态
        
        Returns:
            是否最大化
        """
        result = self.get('window.maximized', False)
        return result if isinstance(result, bool) else False
    
    def set_window_maximized(self, maximized: bool) -> bool:
        """设置窗口最大化状态
        
        Args:
            maximized: 是否最大化
            
        Returns:
            是否设置成功
        """
        return self.set('window.maximized', maximized)
    
    def get_window_position(self) -> tuple[int, int] | None:
        """获取窗口位置
        
        Returns:
            (x, y) 坐标，如果未设置则返回 None
        """
        x_val = self.get('window.x')
        y_val = self.get('window.y')
        if isinstance(x_val, int) and isinstance(y_val, int):
            return (x_val, y_val)
        return None
    
    def set_window_position(self, x: int, y: int) -> bool:
        """设置窗口位置
        
        Args:
            x: x坐标
            y: y坐标
            
        Returns:
            是否设置成功
        """
        success1 = self.set('window.x', x)
        success2 = self.set('window.y', y)
        return success1 and success2
    
    def get_auto_backup_enabled(self) -> bool:
        """获取自动备份是否启用
        
        Returns:
            是否启用自动备份
        """
        result = self.get('auto_backup.enabled', True)
        return result if isinstance(result, bool) else True
    
    def set_auto_backup_enabled(self, enabled: bool) -> bool:
        """设置自动备份是否启用
        
        Args:
            enabled: 是否启用
            
        Returns:
            是否设置成功
        """
        return self.set('auto_backup.enabled', enabled)
    
    def get_auto_backup_frequency(self) -> str:
        """获取自动备份频率

        Returns:
            备份频率
        """
        default_frequency = self.DEFAULT_CONFIG['auto_backup']['frequency']
        result = self.get('auto_backup.frequency', default_frequency)
        return result if isinstance(result, str) else default_frequency
    
    def set_auto_backup_frequency(self, frequency: str) -> bool:
        """设置自动备份频率
        
        Args:
            frequency: 备份频率
            
        Returns:
            是否设置成功
        """
        if frequency not in self.SUPPORTED_BACKUP_FREQUENCIES:
            print(self._translate("unsupported_backup_frequency", frequency=frequency))
            return False
        return self.set('auto_backup.frequency', frequency)
    
    def get_ui_theme(self) -> str:
        """获取UI主题
        
        Returns:
            主题名称
        """
        result = self.get('ui.theme', 'vista')
        return result if isinstance(result, str) else 'vista'
    
    def set_ui_theme(self, theme: str) -> bool:
        """设置UI主题
        
        Args:
            theme: 主题名称（接受任何有效的Tkinter主题名称）
            
        Returns:
            是否设置成功
        """
        if not theme:
            print(f"无效的主题名称: {theme}")
            return False
        return self.set('ui.theme', theme)
    
    def get_ui_font_size(self) -> int:
        """获取UI字体大小
        
        Returns:
            字体大小
        """
        result = self.get('ui.font_size', 12)
        return result if isinstance(result, int) else 12
    
    def set_ui_font_size(self, font_size: int) -> bool:
        """设置UI字体大小
        
        Args:
            font_size: 字体大小
            
        Returns:
            是否设置成功
        """
        if font_size < 8 or font_size > 32:
            print(self._translate("font_size_range"))
            return False
        return self.set('ui.font_size', font_size)
    
    def get_ui_tab_order(self) -> list[str]:
        """获取标签页次序
        
        Returns:
            标签名称列表
        """
        result = self.get('ui.tab_order', [])
        if isinstance(result, list):
            return [item for item in result if isinstance(item, str)]
        return []
    
    def set_ui_tab_order(self, tab_order: list[str]) -> bool:
        """设置标签页次序
        
        Args:
            tab_order: 标签名称列表
            
        Returns:
            是否设置成功
        """
        return self.set('ui.tab_order', tab_order)
    
    def get_recent_files(self) -> list[str]:
        """获取最近打开的文件列表
        
        Returns:
            文件路径列表
        """
        result = self.get('recent_files', [])
        if isinstance(result, list):
            return [f for f in result if isinstance(f, str)]
        return []
    
    def add_recent_file(self, file_path: str, max_count: int = 10) -> bool:
        """添加最近打开的文件
        
        Args:
            file_path: 文件路径
            max_count: 最大记录数
            
        Returns:
            是否添加成功
        """
        recent_files = self.get_recent_files()
        
        # 移除重复项
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # 添加到开头
        recent_files.insert(0, file_path)
        
        # 限制数量
        recent_files = recent_files[:max_count]
        
        return self.set('recent_files', recent_files)
    
    def remove_recent_file(self, file_path: str) -> bool:
        """从最近文件列表中移除
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否移除成功
        """
        recent_files = self.get_recent_files()
        if file_path in recent_files:
            recent_files.remove(file_path)
            return self.set('recent_files', recent_files)
        return True
    
    def clear_recent_files(self) -> bool:
        """清空最近文件列表
        
        Returns:
            是否清空成功
        """
        return self.set('recent_files', [])
    
    def get_last_used_network(self) -> str | None:
        """获取上次使用的网络
        
        Returns:
            网络地址或 None
        """
        result = self.get('last_used_network')
        return result if isinstance(result, str) else None
    
    def set_last_used_network(self, network: str | None) -> bool:
        """设置上次使用的网络
        
        Args:
            network: 网络地址
            
        Returns:
            是否设置成功
        """
        return self.set('last_used_network', network)
    
    def reset_to_default(self) -> bool:
        """重置为默认配置
        
        Returns:
            是否重置成功
        """
        self._config = self._create_default_config()
        return self._save_config()
    
    def get_config_file_path(self) -> str:
        """获取配置文件路径
        
        Returns:
            配置文件的绝对路径
        """
        return os.path.abspath(self._config_file)
    
    def export_config(self, export_path: str) -> bool:
        """导出配置到指定文件
        
        Args:
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(self._translate("export_config_failed", error=str(e)))
            return False
    
    def import_config(self, import_path: str) -> bool:
        """从指定文件导入配置
        
        Args:
            import_path: 导入路径
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = cast(dict[str, object], json.load(f))
            
            # 迁移导入的配置
            self._config = self._migrate_config(imported_config)
            
            return self._save_config()
        except Exception as e:
            print(self._translate("import_config_failed", error=str(e)))
            return False


# 创建全局配置管理器实例
config_manager = ConfigManager()


# 便捷函数
def get_config() -> ConfigManager:
    """获取全局配置管理器实例"""
    return config_manager


def get_language() -> str:
    """获取当前语言"""
    return config_manager.get_language()


def set_language(lang: str) -> bool:
    """设置语言"""
    return config_manager.set_language(lang)


def get_window_size() -> tuple[int, int]:
    """获取窗口大小"""
    return config_manager.get_window_size()


def set_window_size(width: int, height: int) -> bool:
    """设置窗口大小"""
    return config_manager.set_window_size(width, height)


def get_auto_backup_frequency() -> str:
    """获取自动备份频率"""
    return config_manager.get_auto_backup_frequency()


def set_auto_backup_frequency(frequency: str) -> bool:
    """设置自动备份频率"""
    return config_manager.set_auto_backup_frequency(frequency)
