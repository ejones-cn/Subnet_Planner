#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试国际化功能
"""

from i18n import _, get_language, set_language

print(f"Current language: {get_language()}")
print(f"expired_ips_detected: {_('expired_ips_detected')}")
print(f"release_selected: {_('release_selected')}")
print(f"release_all: {_('release_all')}")

# 测试切换语言
print("\nTesting language switching:")

languages = ['zh', 'en', 'ja', 'zh_tw', 'ko']
for lang in languages:
    set_language(lang)
    print(f"Language: {lang}")
    print(f"  expired_ips_detected: {_('expired_ips_detected')}")
    print(f"  release_selected: {_('release_selected')}")
    print(f"  release_all: {_('release_all')}")
