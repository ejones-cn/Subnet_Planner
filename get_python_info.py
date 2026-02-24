#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
获取Python解释器信息
"""

import sys
import os

print("Python解释器路径:")
print(sys.executable)
print()
print("Python版本:")
print(sys.version)
print()
print("当前工作目录:")
print(os.getcwd())
