#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查各模块版本号的脚本
用于验证所有版本相关文件的版本号是否一致
"""

import os
import re
import json
import version
from typing import cast


def check_all_versions():
    """检查所有模块的版本号"""
    print("🔍 正在检查各模块版本号...")
    print("=" * 50)
    
    # 1. 检查version模块版本号
    try:
        version_module_version = version.get_version()
        print(f"✅ version模块版本号: {version_module_version}")
        version_tuple = version.get_version_tuple()
        print(f"✅ version模块版本号元组: {version_tuple}")
        release_date = version.get_release_date()
        print(f"✅ version模块发布日期: {release_date}")
    except Exception as e:
        print(f"❌ 检查version模块版本号失败: {e}")
    
    print("-" * 50)
    
    # 2. 检查translations.json文件版本号
    try:
        translations_path = "translations.json"
        if os.path.exists(translations_path):
            with open(translations_path, "r", encoding="utf-8") as f:
                try:
                    # 读取并解析JSON文件
                    translations_json = f.read()
                    # 解析JSON数据，使用cast函数指定类型
                    raw_data = cast(dict[str, object], json.loads(translations_json))
                    # 检查__version__字段是否存在且为字符串
                    if "__version__" in raw_data and isinstance(raw_data["__version__"], str):
                        translations_version = raw_data["__version__"]
                        print(f"✅ translations.json版本号: {translations_version}")
                    else:
                        print("✅ translations.json版本号: 未知")
                except (json.JSONDecodeError, ValueError, TypeError, AttributeError) as e:
                    print(f"❌ translations.json格式错误，无法解析: {e}")
        else:
            print(f"❌ 文件不存在: {translations_path}")
    except Exception as e:
        print(f"❌ 检查translations.json版本号失败: {e}")
    
    print("-" * 50)
    
    # 3. 检查version_info.py文件版本号
    try:
        version_info_path = "version_info.py"
        if os.path.exists(version_info_path):
            with open(version_info_path, "r", encoding="utf-8") as f:
                version_info_content = f.read()
                # 提取FileVersion
                file_version_match = re.search(r"StringStruct\('FileVersion', '(\d+\.\d+\.\d+)'\)", version_info_content)
                if file_version_match:
                    file_version = file_version_match.group(1)
                    print(f"✅ version_info.py FileVersion: {file_version}")
                else:
                    print("❌ 未找到FileVersion")
                
                # 提取ProductVersion
                product_version_match = re.search(r"StringStruct\('ProductVersion', '(\d+\.\d+\.\d+)'\)", version_info_content)
                if product_version_match:
                    product_version = product_version_match.group(1)
                    print(f"✅ version_info.py ProductVersion: {product_version}")
                else:
                    print("❌ 未找到ProductVersion")
        else:
            print(f"❌ 文件不存在: {version_info_path}")
    except Exception as e:
        print(f"❌ 检查version_info.py版本号失败: {e}")
    
    print("-" * 50)
    
    # 4. 检查README.md文件版本号
    try:
        readme_path = "README.md"
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                # 提取标题中的版本号
                title_version_match = re.search(r"v(\d+\.\d+\.\d+)", first_line)
                if title_version_match:
                    title_version = title_version_match.group(1)
                    print(f"✅ README.md标题版本号: {title_version}")
                else:
                    print(f"⚠️  未从标题中提取到版本号: {first_line}")
                    
                # 读取文件内容，查找可执行文件名
                _ = f.seek(0)
                readme_content = f.read()
                exe_name_match = re.search(r"`SubnetPlannerV(\d+\.\d+\.\d+)\.exe`", readme_content)
                if exe_name_match:
                    exe_version = exe_name_match.group(1)
                    print(f"✅ README.md可执行文件名版本号: {exe_version}")
                else:
                    print("⚠️  未找到可执行文件名")
        else:
            print(f"❌ 文件不存在: {readme_path}")
    except Exception as e:
        print(f"❌ 检查README.md版本号失败: {e}")
    
    print("=" * 50)
    print("🎉 版本号检查完成!")


if __name__ == "__main__":
    check_all_versions()
