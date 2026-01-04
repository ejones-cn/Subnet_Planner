#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号管理模块
用于集中管理子网规划师的版本号
"""

__version__ = "2.5.0"

MAJOR_VERSION = 2
MINOR_VERSION = 5
PATCH_VERSION = 0

VERSION_TUPLE = (MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION)

# 版本发布日期
RELEASE_DATES = {
    "2.5.0": "2026-01-04",
    "2.1.0": "2026-01-04",
    "2.0.2": "2026-01-04",
    "2.0.1": "2025-12-30",
    "2.0.0": "2025-12-29",
    "1.4.5": "2025-12-22",
    "1.4.4": "2025-12-22",
    "1.4.2": "2025-12-21",    
    "1.4.1": "2025-12-20",
    "1.4.0": "2025-12-19",
    "1.3.0": "2025-12-11",
    "1.2.1": "2025-12-11",
    "1.2.0": "2025-12-10",
    "1.1.0": "2025-12-05",
    "1.0.0": "2025-11-30",
}


def get_version():
    """获取当前版本号字符串"""
    return __version__


def get_version_tuple():
    """获取当前版本号元组"""
    return VERSION_TUPLE


def get_release_date(version=None):
    """获取指定版本的发布日期，默认为当前版本"""
    if version is None:
        version = __version__
    return RELEASE_DATES.get(version, "未知")
