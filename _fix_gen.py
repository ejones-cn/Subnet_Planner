#!/usr/bin/env python3
"""临时脚本：修复 generate_package_list.py"""
import pathlib

content = '''#!/usr/bin/env python3
"""
生成打包文件清单，检查单文件程序中包含的所有文件
"""

import os
import json
from datetime import datetime
from typing import TypedDict


class FileInfo(TypedDict):
    """文件信息类型"""
    name: str
    size_bytes: int
    size_human: str


class DirectoryInfo(TypedDict):
    """目录信息类型"""
    name: str
    file_count: int
    total_size_bytes: int
    total_size_human: str


class RuntimeFile(TypedDict):
    """运行时文件类型"""
    name: str
    description: str


class PackageInfo(TypedDict):
    """打包信息类型"""
    generated_at: str
    exe_file: str
    included_files: list[FileInfo]
    excluded_files: list[str]
    directories: list[DirectoryInfo]
    runtime_generated: list[RuntimeFile]


def generate_package_list() -> PackageInfo:
    """生成打包文件清单"""
    package_info: PackageInfo = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exe_file": "SubnetPlannerV3.0.0.exe",
        "included_files": [],
        "excluded_files": [],
        "directories": []
    }

    included_data_files = [
        "translations.json",
        "Subnet_Planner.ico"
    ]

    included_dirs = [
        "Picture"
    ]

    excluded_items = [
        "ipam_data.db",
        "ipam_backups",
        "*.db"
    ]

    for f in included_data_files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            package_info["included_files"].append({
                "name": f,
                "size_bytes": size,
                "size_human": f"{size / 1024:.2f} KB"
            })

    for d in included_dirs:
        if os.path.exists(d):
            file_count = 0
            total_size = 0
            for root, _dirs, files in os.walk(d):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_count += 1
                    total_size += os.path.getsize(file_path)

            package_info["directories"].append({
                "name": d,
                "file_count": file_count,
                "total_size_bytes": total_size,
                "total_size_human": f"{total_size / 1024:.2f} KB"
            })

    for item in excluded_items:
        package_info["excluded_files"].append(item)

    runtime_files: list[RuntimeFile] = [
        {
            "name": "ipam_data.db",
            "description": "主数据库文件，运行时在程序所在目录创建"
        },
        {
            "name": "ipam_backups/",
            "description": "备份目录，运行时在程序所在目录创建"
        }
    ]
    package_info["runtime_generated"] = runtime_files

    print("=" * 60)
    print("\\U0001f4e6 Subnet Planner 打包文件清单")
    print("=" * 60)
    print(f"生成时间: {package_info['generated_at']}")
    print(f"主程序: {package_info['exe_file']}")
    print()

    print("\\U0001f4c1 包含的数据文件:")
    print("-" * 40)
    for f in package_info["included_files"]:
        print(f"  \\u2022 {f['name']} ({f['size_human']})")

    print()
    print("\\U0001f4c2 包含的目录:")
    print("-" * 40)
    for d in package_info["directories"]:
        print(f"  \\u2022 {d['name']}/")
        print(f"    \\u2514\\u2500 {d['file_count']} 个文件, {d['total_size_human']}")

    print()
    print("\\U0001f6ab 排除的文件/目录:")
    print("-" * 40)
    for item in package_info["excluded_files"]:
        print(f"  \\u2022 {item}")

    print()
    print("\\u26a1 运行时生成的文件:")
    print("-" * 40)
    for item in package_info["runtime_generated"]:
        print(f"  \\u2022 {item['name']}")
        print(f"    \\u2514\\u2500 {item['description']}")

    print()
    print("=" * 60)

    with open("package_list.json", "w", encoding="utf-8") as f:
        json.dump(package_info, f, indent=2, ensure_ascii=False)
    print("\\u2705 清单已保存到 package_list.json")

    return package_info


if __name__ == "__main__":
    _ = generate_package_list()
'''

p = pathlib.Path(r'e:\trae_projects\Subnet_Planner\generate_package_list.py')
p.write_text(content, encoding='utf-8')
print(f'Written {p.stat().st_size} bytes')
