#!/usr/bin/env python3
"""
生成打包文件清单，检查单文件程序中包含的所有文件
"""

import os
import json
from datetime import datetime
from typing import Any


def generate_package_list() -> dict[str, Any]:
    """生成打包文件清单"""
    package_info: dict[str, Any] = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exe_file": "SubnetPlannerV3.0.0.exe",
        "included_files": [],
        "excluded_files": [],
        "directories": []
    }
    
    # 获取明确包含的数据文件（从编译脚本中提取）
    included_data_files = [
        "translations.json",
        "Subnet_Planner.ico"
    ]
    
    # 获取包含的目录
    included_dirs = [
        "Picture"
    ]
    
    # 获取排除的文件和目录
    excluded_items = [
        "ipam_data.db",
        "ipam_backups",
        "*.db"
    ]
    
    # 添加包含的文件
    for f in included_data_files:
        if os.path.exists(f):
            size = os.path.getsize(f)
            package_info["included_files"].append({
                "name": f,
                "size_bytes": size,
                "size_human": f"{size / 1024:.2f} KB"
            })
    
    # 添加包含的目录
    for d in included_dirs:
        if os.path.exists(d):
            file_count = 0
            total_size = 0
            for root, dirs, files in os.walk(d):
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
    
    # 添加排除的项目
    for item in excluded_items:
        package_info["excluded_files"].append(item)
    
    # 添加运行时生成的文件
    runtime_files = [
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
    
    # 打印清单
    print("=" * 60)
    print("📦 Subnet Planner 打包文件清单")
    print("=" * 60)
    print(f"生成时间: {package_info['generated_at']}")
    print(f"主程序: {package_info['exe_file']}")
    print()
    
    print("📁 包含的数据文件:")
    print("-" * 40)
    for f in package_info["included_files"]:
        print(f"  • {f['name']} ({f['size_human']})")
    
    print()
    print("📂 包含的目录:")
    print("-" * 40)
    for d in package_info["directories"]:
        print(f"  • {d['name']}/")
        print(f"    └─ {d['file_count']} 个文件, {d['total_size_human']}")
    
    print()
    print("🚫 排除的文件/目录:")
    print("-" * 40)
    for item in package_info["excluded_files"]:
        print(f"  • {item}")
    
    print()
    print("⚡ 运行时生成的文件:")
    print("-" * 40)
    for item in package_info["runtime_generated"]:
        print(f"  • {item['name']}")
        print(f"    └─ {item['description']}")
    
    print()
    print("=" * 60)
    
    # 保存到文件
    with open("package_list.json", "w", encoding="utf-8") as f:
        json.dump(package_info, f, indent=2, ensure_ascii=False)
    print("✅ 清单已保存到 package_list.json")
    
    return package_info


if __name__ == "__main__":
    generate_package_list()
