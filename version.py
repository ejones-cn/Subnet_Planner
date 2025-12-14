#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号管理模块
用于集中管理IP子网切分工具的版本号
"""

__version__ = "1.3.0"

MAJOR_VERSION = 1
MINOR_VERSION = 3
PATCH_VERSION = 0

VERSION_TUPLE = (MAJOR_VERSION, MINOR_VERSION, PATCH_VERSION)

# 版本发布日期
RELEASE_DATES = {
    "1.0.0": "2025-11-30",
    "1.1.0": "2025-12-05",
    "1.2.0": "2025-12-10",
    "1.2.1": "2025-12-11",
    "1.3.0": "2025-12-11",
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
