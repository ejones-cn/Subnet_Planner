#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号统一更新脚本
用于同步更新所有版本相关文件
"""

import os
import re
import json
from datetime import datetime


def update_version(version):
    """更新所有版本相关文件
    
    Args:
        version: 新的版本号，格式为 "x.y.z"
    """
    # 解析版本号
    major, minor, patch = map(int, version.split('.'))
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 更新 version.py
    version_py_path = "version.py"
    if os.path.exists(version_py_path):
        with open(version_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新版本字符串
        content = re.sub(r'__version__ = "\d+\.\d+\.\d+"', f'__version__ = "{version}"', content)
        # 更新主要版本号
        content = re.sub(r'MAJOR_VERSION = \d+', f'MAJOR_VERSION = {major}', content)
        # 更新次要版本号
        content = re.sub(r'MINOR_VERSION = \d+', f'MINOR_VERSION = {minor}', content)
        # 更新补丁版本号
        content = re.sub(r'PATCH_VERSION = \d+', f'PATCH_VERSION = {patch}', content)
        # 更新版本元组
        content = re.sub(r'VERSION_TUPLE = \(\d+, \d+, \d+\)', f'VERSION_TUPLE = ({major}, {minor}, {patch})', content)
        # 更新发布日期
        content = re.sub(r'RELEASE_DATES = \{\n    ".*": ".*",', f'RELEASE_DATES = {{\n    "{version}": "{today}",', content)
        
        with open(version_py_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 更新 {version_py_path} 成功")
    
    # 2. 更新 version_info.py
    version_info_py_path = "version_info.py"
    if os.path.exists(version_info_py_path):
        with open(version_info_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 更新 filevers
        content = re.sub(r'filevers=\(\d+, \d+, \d+\)', f'filevers=({major}, {minor}, {patch})', content)
        # 更新 prodvers
        content = re.sub(r'prodvers=\(\d+, \d+, \d+\)', f'prodvers=({major}, {minor}, {patch})', content)
        # 更新 FileVersion
        content = re.sub(r'StringStruct\(\'FileVersion\', \'\d+\.\d+\.\d+\'\)', f"StringStruct('FileVersion', '{version}')", content)
        # 更新 ProductVersion
        content = re.sub(r'StringStruct\(\'ProductVersion\', \'\d+\.\d+\.\d+\'\)', f"StringStruct('ProductVersion', '{version}')", content)
        
        with open(version_info_py_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 更新 {version_info_py_path} 成功")
    
    # 3. 更新 translations.json
    translations_json_path = "translations.json"
    if os.path.exists(translations_json_path):
        with open(translations_json_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        
        content["__version__"] = version
        
        with open(translations_json_path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        print(f"✅ 更新 {translations_json_path} 成功")
    
    # 4. 更新 README.md
    readme_path = "README.md"
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 只更新标题中的版本号（匹配行首的#或### 子网规划师 vx.y.z）
        content = re.sub(r'^# 子网规划师 v\d+\.\d+\.\d+', f'# 子网规划师 v{version}', content, flags=re.MULTILINE)
        # 只更新可执行文件名中的版本号（匹配 SubnetPlannerVx.y.z.exe）
        content = re.sub(r'SubnetPlannerV\d+\.\d+\.\d+\.exe', f'SubnetPlannerV{version}.exe', content)
        # 只更新文档正文中提及的当前版本（如"在v2.7.0及后续版本中"）
        # 使用lambda函数来避免捕获组引用与版本号拼接的问题
        content = re.sub(r'(在v)\d+\.\d+\.\d+(及后续版本中)', lambda m: f'{m.group(1)}{version}{m.group(2)}', content)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ 更新 {readme_path} 成功")
    
    print(f"\n🎉 所有版本相关文件已成功更新到版本 {version}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <version>")
        print(f"示例: {sys.argv[0]} 2.7.0")
        sys.exit(1)
    
    version = sys.argv[1]
    # 验证版本号格式
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        print("错误: 版本号格式不正确，应为 x.y.z")
        sys.exit(1)
    
    update_version(version)
