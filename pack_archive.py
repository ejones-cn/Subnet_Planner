#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压缩打包脚本
用于将项目阶段性成果压缩到父目录，支持从配置文件读取排除规则
"""

import os
import json
import zipfile
import datetime
import re


def read_version(version_file: str) -> str:
    """从版本文件中读取当前版本号
    
    Args:
        version_file: 版本文件路径
        
    Returns:
        版本号字符串
    """
    with open(version_file, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'__version__ = "([^"]+)"', content)
    if match:
        return match.group(1)
    raise ValueError("无法从版本文件中读取版本号")


def main():
    """主函数"""
    # 读取配置文件
    config_path = os.path.join(os.getcwd(), 'pack_archive_config.json')
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
        return 1
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 获取配置参数
    source_path = config['source_path']
    destination_dir = config['destination_dir']
    exclude_items = config['exclude_items']
    version_file = os.path.join(source_path, config['version_file'])
    timestamp_format = config['timestamp_format'].replace('yyyy', '%Y').replace('MM', '%m').replace('dd', '%d').replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')
    filename_prefix = config['filename_prefix']
    
    # 生成版本号和时间戳
    version = read_version(version_file)
    timestamp = datetime.datetime.now().strftime(timestamp_format)
    
    # 生成压缩包文件名
    zip_filename = f"{filename_prefix}_V{version}_{timestamp}.zip"
    zip_path = os.path.join(destination_dir, zip_filename)
    
    print(f"=== 压缩打包配置 ===")
    print(f"源路径: {source_path}")
    print(f"目标目录: {destination_dir}")
    print(f"排除项: {', '.join(exclude_items)}")
    print(f"版本号: {version}")
    print(f"时间戳: {timestamp}")
    print(f"输出文件: {zip_filename}")
    print(f"文件路径: {zip_path}")
    print("====================")
    
    # 执行压缩
    try:
        print("开始压缩...")
        
        # 清理之前的临时目录
        temp_dir_pattern = os.path.join(os.getcwd(), "temp_pack_*")
        import glob
        for temp_dir in glob.glob(temp_dir_pattern):
            if os.path.isdir(temp_dir):
                print(f"清理旧临时目录: {temp_dir}")
                for root, dirs, files in os.walk(temp_dir, topdown=False):
                    for name in files:
                        file_path = os.path.join(root, name)
                        os.chmod(file_path, 0o777)
                        os.remove(file_path)
                    for name in dirs:
                        dir_path = os.path.join(root, name)
                        os.rmdir(dir_path)
                os.rmdir(temp_dir)
        
        # 使用zipfile直接创建zip文件
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 获取源目录的基本路径长度，用于生成相对路径
            base_len = len(source_path) + 1
            
            # 遍历源目录中的所有文件和子目录
            for root, dirs, files in os.walk(source_path):
                # 计算当前目录的相对路径
                relative_dir = os.path.relpath(root, source_path)
                
                # 如果是根目录，relative_dir会是"."，需要特殊处理
                if relative_dir == ".":
                    relative_dir = ""
                
                # 检查当前目录是否需要排除
                dir_name = os.path.basename(root)
                if dir_name in exclude_items:
                    print(f"跳过目录: {os.path.relpath(root, source_path)}")
                    # 从dirs列表中移除所有子目录，避免继续遍历
                    dirs[:] = []
                    continue
                
                # 检查父目录是否被排除
                parent_excluded = False
                current_path = root
                while current_path != source_path:
                    parent_dir = os.path.basename(current_path)
                    if parent_dir in exclude_items:
                        parent_excluded = True
                        break
                    current_path = os.path.dirname(current_path)
                
                if parent_excluded:
                    continue
                
                # 添加当前目录到zip文件（如果不是根目录）
                if relative_dir:
                    zipf.write(root, relative_dir)
                
                # 添加文件到zip文件
                for file in files:
                    # 跳过临时文件
                    if file.startswith("temp_pack_"):
                        continue
                    
                    file_path = os.path.join(root, file)
                    relative_file = os.path.relpath(file_path, source_path)
                    
                    # 检查文件是否在排除目录中
                    file_dir = os.path.dirname(file_path)
                    file_in_excluded_dir = False
                    while file_dir != source_path:
                        dir_name = os.path.basename(file_dir)
                        if dir_name in exclude_items:
                            file_in_excluded_dir = True
                            break
                        file_dir = os.path.dirname(file_dir)
                    
                    if not file_in_excluded_dir:
                        zipf.write(file_path, relative_file)
        
        print(f"压缩完成！")
        print(f"文件大小: {os.path.getsize(zip_path) / (1024 * 1024):.2f} MB")
        return 0
    except Exception as e:
        print(f"压缩失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())