#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号管理工具
整合版本号递增、更新和同步功能
"""

import argparse
from argparse import Namespace
import os
import re
import sys
import json
from datetime import datetime

# 配置文件路径
VERSION_FILE = "version.py"
README_FILE = "README.md"
WINDOWS_APP_FILE = "windows_app.py"
TRANSLATIONS_FILE = "translations.json"
VERSION_INFO_FILE = "version_info.py"
IP_SUBNET_CALCULATOR_FILE = "ip_subnet_calculator.py"

# 核心模块列表
CORE_MODULES = [
    "chart_utils.py",
    "export_utils.py",
    "style_manager.py",
    "i18n.py",
    "font_config.py"
]


def read_version_from_version_py():
    """从version.py文件中读取当前版本号"""
    version_file = os.path.join(os.path.dirname(__file__), VERSION_FILE)
    
    with open(version_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 匹配__version__ = "x.y.z"格式
    version_match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    if version_match:
        return version_match.group(1)
    else:
        print("❌ 错误：无法从version.py中读取版本号")
        sys.exit(1)


def read_current_version():
    """从version.py文件中读取当前版本号（包含主次修订号）"""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取版本号信息
    match = re.search(r'__version__\s*=\s*"(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("无法从version.py中读取版本号")

    version_str = match.group(1)
    major, minor, patch = map(int, version_str.split("."))

    return major, minor, patch, version_str


def update_version_file(major: int, minor: int, patch: int) -> str:
    """更新version.py文件中的版本号"""
    new_version = f"{major}.{minor}.{patch}"

    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新版本号
    content = re.sub(
        r'__version__\s*=\s*"\d+\.\d+\.\d+"', f'__version__ = "{new_version}"', content
    )
    content = re.sub(r"MAJOR_VERSION\s*=\s*\d+", f"MAJOR_VERSION = {major}", content)
    content = re.sub(r"MINOR_VERSION\s*=\s*\d+", f"MINOR_VERSION = {minor}", content)
    content = re.sub(r"PATCH_VERSION\s*=\s*\d+", f"PATCH_VERSION = {patch}", content)
    content = re.sub(
        r"VERSION_TUPLE\s*=\s*\(\d+,\s*\d+,\s*\d+\)",
        f"VERSION_TUPLE = ({major}, {minor}, {patch})",
        content,
    )

    # 更新或添加发布日期
    today = datetime.now().strftime("%Y-%m-%d")
    if f'"{new_version}":' in content:
        content = re.sub(
            rf'"{new_version}":\s*"\d{{4}}-\d{{2}}-\d{{2}}"', f'"{new_version}": "{today}"', content
        )
    else:
        # 如果版本号不存在，在RELEASE_DATES字典开头添加
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'RELEASE_DATES = {' in line:
                # 保留现有的缩进
                indent = ' ' * (len(line) - len(line.lstrip()))
                
                # 检查当前行是否包含版本号
                if '"' in line:
                    # 如果当前行包含版本号，在等号和大括号后面插入新版本号
                    brace_pos = line.find('{')
                    if brace_pos != -1:
                        # 将当前行拆分为两部分：大括号前和大括号后
                        before_brace = line[:brace_pos + 1]
                        after_brace = line[brace_pos + 1:].strip()
                        
                        # 更新当前行为只有大括号前的部分
                        lines[i] = before_brace
                        
                        # 在当前行后面添加新版本号
                        lines.insert(i + 1, f'{indent}    "{new_version}": "{today}",')
                        
                        # 如果大括号后有内容，将其添加到新版本号的下一行
                        if after_brace:
                            lines.insert(i + 2, f'{indent}    {after_brace}')
                else:
                    # 查找第一个版本号的位置
                    first_version_line = i + 1
                    for j in range(i + 1, len(lines)):
                        if '"' in lines[j]:
                            first_version_line = j
                            break
                        elif lines[j].strip() == '':
                            continue
                        else:
                            first_version_line = j
                            break
                    # 在第一个版本号前面添加新版本号
                    lines.insert(first_version_line, f'{indent}    "{new_version}": "{today}",')
                break
        content = '\n'.join(lines)

    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        _ = f.write(content)

    return new_version


def update_readme_file(new_version: str) -> None:
    """更新README.md文件中的版本号"""
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新标题中的版本号
    content = re.sub(
        r"# 子网规划师 v\d+\.\d+\.\d+", f"# 子网规划师 v{new_version}", content
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        _ = f.write(content)
    
    print(f"✅ 已更新 {README_FILE} 中的版本号为 {new_version}")


def update_windows_app_file(new_version: str) -> None:
    """更新windows_app.py文件中的版本号"""
    with open(WINDOWS_APP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新标题中的版本号
    content = re.sub(
        r'"子网规划师 v\d+\.\d+\.\d+"', f'"子网规划师 v{new_version}"', content
    )

    # 更新app_version变量
    content = re.sub(
        r'self\.app_version\s*=\s*"\d+\.\d+\.\d+"', f'self.app_version = "{new_version}"', content
    )

    with open(WINDOWS_APP_FILE, "w", encoding="utf-8") as f:
        _ = f.write(content)
    
    print(f"✅ 已更新 {WINDOWS_APP_FILE} 中的版本号为 {new_version}")


def update_ip_subnet_calculator_file(new_version: str) -> None:
    """更新ip_subnet_calculator.py文件中的版本号"""
    with open(IP_SUBNET_CALCULATOR_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新版本号
    content = re.sub(
        r'__version__\s*=\s*"\d+\.\d+\.\d+"', f'__version__ = "{new_version}"', content
    )

    with open(IP_SUBNET_CALCULATOR_FILE, "w", encoding="utf-8") as f:
        _ = f.write(content)
    
    print(f"✅ 已更新 {IP_SUBNET_CALCULATOR_FILE} 中的版本号为 {new_version}")


def update_core_modules_version(new_version: str) -> None:
    """更新核心模块中的版本注释"""
    for module in CORE_MODULES:
        try:
            with open(module, "r", encoding="utf-8") as f:
                content = f.read()

            # 更新文档字符串中的版本号
            content = re.sub(
                r'项目版本：v\d+\.\d+\.\d+', f'项目版本：v{new_version}', content
            )

            with open(module, "w", encoding="utf-8") as f:
                _ = f.write(content)
            
            print(f"✅ 已更新 {module} 中的版本注释为 v{new_version}")
        except Exception as e:
            print(f"❌ 更新 {module} 版本注释失败：{e}")


def update_translations_json(version: str) -> None:
    """更新translations.json文件中的版本号"""
    translations_file = os.path.join(os.path.dirname(__file__), TRANSLATIONS_FILE)
    
    with open(translations_file, "r", encoding="utf-8") as f:
        translations = json.load(f)  # type: ignore
    
    # 更新__version__字段
    if "__version__" in translations:  # type: ignore
        translations["__version__"] = version  # type: ignore
    
    with open(translations_file, "w", encoding="utf-8") as f:
        _ = json.dump(translations, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已更新 {TRANSLATIONS_FILE} 中的版本号为 {version}")


def update_version_info_py(version: str) -> None:
    """更新version_info.py文件中的版本号"""
    version_info_file = os.path.join(os.path.dirname(__file__), VERSION_INFO_FILE)
    
    with open(version_info_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 将版本号转换为元组格式，如"2.6.0" -> "(2, 6, 0)"
    version_parts: list[str] = version.split('.')
    version_tuple = f"({', '.join(version_parts)})"
    
    # 更新filevers和prodvers
    updated_content = re.sub(r'filevers=\([0-9,\s]+\)', f'filevers={version_tuple}', content)
    updated_content = re.sub(r'prodvers=\([0-9,\s]+\)', f'prodvers={version_tuple}', content)
    
    # 更新字符串版本号
    updated_content = re.sub(r"FileVersion',\s*'[0-9.]+'", f"FileVersion', '{version}'", updated_content)
    updated_content = re.sub(r"ProductVersion',\s*'[0-9.]+'", f"ProductVersion', '{version}'", updated_content)
    
    with open(version_info_file, "w", encoding="utf-8") as f:
        _ = f.write(updated_content)
    
    print(f"✅ 已更新 {VERSION_INFO_FILE} 中的版本号为 {version}")


def bump_version(args: Namespace) -> int:  # type: ignore
    """递增版本号"""
    print("🔄 开始递增版本号...")
    print("=" * 50)
    
    # 读取当前版本号
    major, minor, patch, current_version = read_current_version()  # type: ignore[reportUnknownVariableType]
    print(f"📌 当前版本号：{current_version}")
    
    # 处理版本号更新
    if getattr(args, 'version', None):  # type: ignore[reportUnknownMemberType]
        # 直接设置版本号
        try:
            version_arg = getattr(args, 'version', None)  # type: ignore[reportUnknownMemberType]
            version_str: str = str(version_arg)  # type: ignore[reportUnknownArgumentType]
            version_parts: list[str] = version_str.split(".")
            major, minor, patch = map(int, version_parts)  # type: ignore[reportUnknownArgumentType]
        except ValueError:
            print("❌ 错误：版本号格式不正确，应为X.Y.Z格式")
            return 1
    else:
        # 递增版本号
        if getattr(args, 'major', False):  # type: ignore[reportUnknownMemberType]
            major += 1  # type: ignore[reportUnknownVariableType]
            minor = 0  # type: ignore[reportUnknownVariableType]
            patch = 0  # type: ignore[reportUnknownVariableType]
        elif getattr(args, 'minor', False):  # type: ignore[reportUnknownMemberType]
            minor += 1  # type: ignore[reportUnknownVariableType]
            patch = 0  # type: ignore[reportUnknownVariableType]
        elif getattr(args, 'patch', False):  # type: ignore[reportUnknownMemberType]
            patch += 1  # type: ignore[reportUnknownVariableType]
        else:
            # 默认递增修订版本号
            patch += 1  # type: ignore[reportUnknownVariableType]
    
    new_version = f"{major}.{minor}.{patch}"  # type: ignore[reportUnknownVariableType]
    
    if new_version == current_version:  # type: ignore[reportUnknownArgumentType]
        print("ℹ️ 版本号没有变化")
        return 0
    
    print(f"📌 新的版本号：{new_version}")
    print("=" * 50)
    
    # 更新各个文件
    try:
        # 更新version.py
        _ = update_version_file(major, minor, patch)  # type: ignore
        print(f"✅ 已更新 {VERSION_FILE} 中的版本号为 {new_version}")
        
        # 更新README.md
        update_readme_file(new_version)
        
        # 更新windows_app.py
        update_windows_app_file(new_version)
        
        # 更新ip_subnet_calculator.py
        update_ip_subnet_calculator_file(new_version)
        
        # 更新核心模块版本注释
        update_core_modules_version(new_version)
        
        # 更新translations.json
        update_translations_json(new_version)
        
        # 更新version_info.py
        update_version_info_py(new_version)
        
        print("=" * 50)
        print("🎉 版本号更新成功！")
        print(f"📌 已将版本号从 {current_version} 更新为 {new_version}")
        
    except Exception as e:
        print(f"❌ 版本号更新失败：{e}")
        return 1
    
    return 0


def sync_versions() -> int:
    """同步现有版本号到所有文件"""
    print("🔄 开始同步版本号...")
    print("=" * 50)
    
    # 从version.py中读取当前版本号
    current_version = read_version_from_version_py()
    print(f"📌 当前版本号：{current_version}")
    
    # 更新各个文件
    try:
        # 更新README.md
        update_readme_file(current_version)
        
        # 更新windows_app.py
        update_windows_app_file(current_version)
        
        # 更新ip_subnet_calculator.py
        update_ip_subnet_calculator_file(current_version)
        
        # 更新核心模块版本注释
        update_core_modules_version(current_version)
        
        # 更新translations.json
        update_translations_json(current_version)
        
        # 更新version_info.py
        update_version_info_py(current_version)
        
        print("=" * 50)
        print("🎉 版本号同步完成！")
        print(f"📌 所有文件的版本号已同步为 {current_version}")
        
    except Exception as e:
        print(f"❌ 版本号同步失败：{e}")
        return 1
    
    return 0


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description="子网规划师版本号管理工具")
    
    # 创建子命令解析器
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # bump命令 - 递增版本号
    bump_parser = subparsers.add_parser("bump", help="递增版本号")
    _ = bump_parser.add_argument("--major", action="store_true", help="递增主版本号")
    _ = bump_parser.add_argument("--minor", action="store_true", help="递增次版本号")
    _ = bump_parser.add_argument("--patch", action="store_true", help="递增修订版本号")
    _ = bump_parser.add_argument("--version", type=str, help="直接设置版本号")
    
    # sync命令 - 同步版本号
    _ = subparsers.add_parser("sync", help="同步现有版本号到所有文件")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查是否提供了命令
    command: str = str(getattr(args, 'command', ''))
    if not command:
        parser.print_help()
        return 1
    
    # 执行相应的命令
    if command == "bump":
        return bump_version(args)
    elif command == "sync":
        return sync_versions()
    
    return 0


if __name__ == "__main__":
    exit(main())
