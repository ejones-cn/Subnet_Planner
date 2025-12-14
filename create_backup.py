#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建项目的压缩备份
"""

import os
import zipfile
import datetime
import shutil


def create_project_backup():
    """创建项目的压缩备份"""
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 获取项目目录信息
    project_dir = os.path.abspath(".")
    project_name = os.path.basename(project_dir)
    parent_dir = os.path.dirname(project_dir)
    
    # 创建备份文件名
    backup_filename = f"{project_name.replace(' ', '')}_StageBackup_{timestamp}.zip"
    backup_path = os.path.join(parent_dir, backup_filename)
    
    print(f"创建项目备份: {backup_path}")
    print(f"项目目录: {project_dir}")
    
    # 要排除的文件和目录
    exclude_patterns = [
        '.git',
        'build',
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.log',
        '*.swp',
        '*.bak',
        '.vscode',
        '.idea',
        '*.zip'  # 排除已有的备份文件
    ]
    
    # 创建压缩文件
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历项目目录
        for root, dirs, files in os.walk(project_dir):
            # 过滤排除目录
            dirs[:] = [d for d in dirs if not any(
                exclude in os.path.relpath(os.path.join(root, d), project_dir)
                for exclude in exclude_patterns
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 过滤排除文件
                if any(
                    exclude in file or exclude in os.path.relpath(file_path, project_dir)
                    for exclude in exclude_patterns
                ):
                    continue
                
                # 计算归档路径
                arcname = os.path.relpath(file_path, project_dir)
                zipf.write(file_path, arcname)
                print(f"  添加: {arcname}")
    
    print(f"\n✅ 备份创建成功！")
    print(f"备份文件: {backup_path}")
    print(f"文件大小: {os.path.getsize(backup_path) / (1024*1024):.2f} MB")
    
    return backup_path


if __name__ == "__main__":
    create_project_backup()