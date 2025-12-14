#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本号自动更新脚本
用于自动递增IP子网切分工具的版本号
"""

import argparse
import os
import re
from datetime import datetime

VERSION_FILE = "version.py"
README_FILE = "README.md"
WEB_APP_FILE = "web_app.py"
WINDOWS_APP_FILE = "windows_app.py"


def read_current_version():
    """从version.py文件中读取当前版本号"""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取版本号信息
    match = re.search(r'__version__\s*=\s*"(\d+\.\d+\.\d+)"', content)
    if not match:
        raise ValueError("无法从version.py中读取版本号")

    version_str = match.group(1)
    major, minor, patch = map(int, version_str.split("."))

    return major, minor, patch, version_str


def update_version_file(major, minor, patch):
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
    if f'"{new_version}"':
        content = re.sub(
            rf'"{new_version}":\s*"\d{{4}}-\d{{2}}-\d{{2}}"', f'"{new_version}": "{today}"', content
        )
    else:
        # 如果版本号不存在，在RELEASE_DATES中添加
        new_release_line = f'"{new_version}": "{today}"' + ",\n"
        content = re.sub(
            r"RELEASE_DATES\s*=\s*\{", f"RELEASE_DATES = {{{new_release_line}", content
        )

    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    return new_version


def update_readme_file(new_version):
    """更新README.md文件中的版本号"""
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新标题中的版本号
    content = re.sub(
        r"# IP子网切分工具 v\d+\.\d+\.\d+", f"# IP子网切分工具 v{new_version}", content
    )

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def update_web_app_file(new_version):
    """更新web_app.py文件中的版本号"""
    with open(WEB_APP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新所有版本号引用
    content = re.sub(r"v\d+\.\d+\.\d+", f"v{new_version}", content)

    with open(WEB_APP_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def update_windows_app_file(new_version):
    """更新windows_app.py文件中的版本号"""
    with open(WINDOWS_APP_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新标题中的版本号
    content = re.sub(
        r'"IP子网切分工具 v\d+\.\d+\.\d+"', f'"IP子网切分工具 v{new_version}"', content
    )

    # 更新app_version变量
    content = re.sub(
        r'self\.app_version\s*=\s*"\d+\.\d+\.\d+"', f'self.app_version = "{new_version}"', content
    )

    with open(WINDOWS_APP_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def update_ip_subnet_calculator_file(new_version):
    """更新ip_subnet_calculator.py文件中的版本号"""
    with open("ip_subnet_calculator.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 更新版本号
    content = re.sub(
        r'__version__\s*=\s*"\d+\.\d+\.\d+"', f'__version__ = "{new_version}"', content
    )

    with open("ip_subnet_calculator.py", "w", encoding="utf-8") as f:
        f.write(content)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="IP子网切分工具版本号自动更新脚本")
    parser.add_argument("--major", action="store_true", help="递增主版本号")
    parser.add_argument("--minor", action="store_true", help="递增次版本号")
    parser.add_argument("--patch", action="store_true", help="递增修订版本号")
    parser.add_argument("--version", type=str, help="直接设置版本号")

    args = parser.parse_args()

    # 读取当前版本号
    major, minor, patch, current_version = read_current_version()

    print(f"当前版本号: {current_version}")

    # 处理版本号更新
    if args.version:
        # 直接设置版本号
        try:
            major, minor, patch = map(int, args.version.split("."))
        except ValueError:
            print("错误：版本号格式不正确，应为X.Y.Z格式")
            return 1
    else:
        # 递增版本号
        if args.major:
            major += 1
            minor = 0
            patch = 0
        elif args.minor:
            minor += 1
            patch = 0
        elif args.patch:
            patch += 1
        else:
            # 默认递增修订版本号
            patch += 1

    new_version = f"{major}.{minor}.{patch}"

    if new_version == current_version:
        print("版本号没有变化")
        return 0

    print(f"新的版本号: {new_version}")

    # 更新各个文件
    try:
        update_version_file(major, minor, patch)
        update_readme_file(new_version)
        update_web_app_file(new_version)
        update_windows_app_file(new_version)
        update_ip_subnet_calculator_file(new_version)

        print("版本号更新成功！")
        print(f"已更新版本号从 {current_version} 到 {new_version}")

    except Exception as e:
        print(f"版本号更新失败：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
