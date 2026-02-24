#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证所有模块的版本号是否统一
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 要检查的核心模块
modules_to_check = [
    "version",
    "ip_subnet_calculator",
    "chart_utils",
    "export_utils",
    "style_manager",
    "i18n",
    "font_config",
    "windows_app"
]



def verify_versions() -> None:
    """验证所有模块的版本号是否统一"""
    print("开始验证所有模块的版本号...")
    print("=" * 50)
    
    # 首先获取version模块的版本号作为基准
    from version import get_version
    base_version = get_version()
    print(f"基准版本号: {base_version}")
    print("=" * 50)
    
    # 检查每个模块
    all_passed = True
    for module_name in modules_to_check:
        try:
            # 动态导入模块
            module = __import__(module_name)  # type: ignore
            
            # 检查是否有__version__属性
            if hasattr(module, "__version__"):  # type: ignore
                module_version: str = getattr(module, "__version__", "")  # type: ignore
                print(f"✅ {module_name}: {module_version}")
                
                # 验证版本号是否与基准一致
                if module_version != base_version:
                    print(f"❌ 错误: {module_name}的版本号与基准不一致")
                    all_passed = False
            else:
                print(f"❌ 错误: {module_name}没有__version__属性")
                all_passed = False
                
        except Exception as e:
            print(f"❌ 错误: 无法导入或检查{module_name}: {e}")
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 所有模块的版本号验证通过！")
        print(f"📌 统一版本号: {base_version}")
    else:
        print("💥 版本号验证失败！")
        sys.exit(1)



if __name__ == "__main__":
    verify_versions()
