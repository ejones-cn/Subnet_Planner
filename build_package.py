#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
一键打包脚本
编译项目并把所有文件打包到一个目录中
"""

import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: E402

from build_compile import (  # noqa: E402
    check_python_version,
    check_and_install_dependencies,
    compile_with_nuitka,
    prepare_version_info,
    CompileType
)

# 必要的配置文件
CONFIG_FILES = {'translations.json', 'SubnetPlanner_config.json'}


def get_version():
    """获取版本号"""
    version, _ = prepare_version_info()
    return version


def create_package_dir(package_name: str, output_dir: str = ".") -> str:
    """创建打包目录
    
    Args:
        package_name: 包目录名称
        output_dir: 输出目录
        
    Returns:
        str: 打包目录的完整路径
    """
    package_dir = os.path.join(output_dir, package_name)
    if os.path.exists(package_dir):
        print(f"⏳ 清理旧目录: {package_dir}")
        shutil.rmtree(package_dir)
    
    os.makedirs(package_dir, exist_ok=True)
    print(f"✅ 创建打包目录: {package_dir}")
    return package_dir


def copy_resource_files(package_dir: str) -> None:
    """复制必要的资源文件到打包目录
    
    这些资源可能不在编译产物中，需要额外复制
    
    Args:
        package_dir: 打包目录
    """
    print("\n📁 复制配置文件...")
    
    for config_file in CONFIG_FILES:
        src_path = os.path.join(os.getcwd(), config_file)
        dst_path = os.path.join(package_dir, config_file)
        if os.path.exists(src_path):
            if os.path.exists(dst_path):
                print(f"   ⚠️  跳过 (已存在): {config_file}")
            else:
                shutil.copy2(src_path, dst_path)
                print(f"   ✅ {config_file}")
        else:
            print(f"   ⚠️  跳过 (不存在): {config_file}")


def find_compiled_exe() -> str | None:
    """查找编译后的 exe 文件
    
    优先查找 Nuitka 目录模式的输出位置（根目录），
    如果找不到再查找 windows_app.dist 目录
    
    Returns:
        str: exe 文件路径，未找到返回 None
    """
    # 优先查找根目录（Nuitka --no-onefile 模式）
    project_root = os.getcwd()
    for file in os.listdir(project_root):
        if file.startswith('SubnetPlanner') and file.endswith('.exe'):
            exe_path = os.path.join(project_root, file)
            # 确保文件大小合理（排除 python*.dll 等）
            if os.path.getsize(exe_path) > 1024 * 1024:  # 大于 1MB
                print(f"   🔍 在根目录找到: {file} ({os.path.getsize(exe_path) / 1024 / 1024:.1f} MB)")
                return exe_path
    
    # 查找 windows_app.dist 目录
    dist_dir = os.path.join(project_root, "windows_app.dist")
    if os.path.exists(dist_dir):
        for file in os.listdir(dist_dir):
            if file.startswith('SubnetPlanner') and file.endswith('.exe'):
                if os.path.getsize(os.path.join(dist_dir, file)) > 1024 * 1024:
                    exe_path = os.path.join(dist_dir, file)
                    print(f"   🔍 在 windows_app.dist 找到: {file}")
                    return exe_path
    
    # 查找 dist 目录（PyInstaller 模式）
    dist_dir = os.path.join(project_root, "dist")
    if os.path.exists(dist_dir):
        for file in os.listdir(dist_dir):
            if file.startswith('SubnetPlanner') and file.endswith('.exe'):
                if os.path.getsize(os.path.join(dist_dir, file)) > 1024 * 1024:
                    exe_path = os.path.join(dist_dir, file)
                    print(f"   🔍 在 dist 找到: {file}")
                    return exe_path
    
    return None


def copy_dist_to_package(package_dir: str) -> bool:
    """复制编译产物到打包目录
    
    只复制必要的依赖文件：
    - 主 exe 文件
    - *.pyd (Python 扩展模块)
    - *.dll (动态链接库)
    - 资源目录 (Picture)
    
    Args:
        package_dir: 打包目录
        
    Returns:
        bool: 是否成功
    """
    exe_path = find_compiled_exe()
    
    if not exe_path:
        print("❌ 未找到编译后的 exe 文件")
        return False
    
    # 获取 exe 文件名和所在目录
    exe_name = os.path.basename(exe_path)
    exe_dir = os.path.dirname(exe_path)
    project_root = os.getcwd()
    
    # 复制 exe 文件
    shutil.copy2(exe_path, os.path.join(package_dir, exe_name))
    print(f"   ✅ {exe_name}")
    
    # 复制 Python 核心 DLL 和 VC++ 运行时 DLL
    python_dir = os.path.dirname(sys.executable)
    required_dlls = {
        'python3.dll': python_dir, 'python313.dll': python_dir,  # Python 核心 DLL
        'vcruntime140.dll': python_dir, 'vcruntime140_1.dll': python_dir, 'vcruntime140_2.dll': python_dir,  # VC++ 运行时
    }
    
    # msvcp140.dll 在系统目录
    system_dll_dir = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')
    required_dlls.update({
        'msvcp140.dll': system_dll_dir, 
        'msvcp140_1.dll': system_dll_dir, 
        'msvcp140_2.dll': system_dll_dir
    })
    
    for dll, src_dir in required_dlls.items():
        src_dll = os.path.join(src_dir, dll)
        dest_dll = os.path.join(package_dir, dll)
        if os.path.exists(src_dll) and not os.path.exists(dest_dll):
            shutil.copy2(src_dll, dest_dll)
            size = os.path.getsize(dest_dll) / 1024
            print(f"   ✅ {dll} ({size:.1f} KB)")
    
    # 定义必要的文件扩展名
    necessary_exts = {'.pyd', '.dll'}
    necessary_names = {'Picture'}  # 必要的目录
    
    # 扫描并复制必要文件
    if exe_dir == project_root:
        # exe 在根目录（Nuitka --no-onefile 模式）
        for item in os.listdir(exe_dir):
            item_path = os.path.join(exe_dir, item)
            
            # 跳过 exe 本身、源码和临时文件
            if item in {exe_name, 'windows_app.py', 'build_package.py', 'build_compile.py'}:
                continue
            if item.startswith('__pycache__') or item.startswith('.'):
                continue
            if item in {'windows_app.dist', 'windows_app.build', 'windows_app.onefile-build', 
                       'dist', 'build', 'SubnetPlanner_data.db'}:
                continue
            if item.endswith(('.py', '.pyc', '.md', '.txt', '.spec', '.log', '.json')) \
                    and item not in CONFIG_FILES:
                continue
            
            dest_path = os.path.join(package_dir, item)
            
            if os.path.isdir(item_path):
                if item in necessary_names:
                    try:
                        shutil.copytree(item_path, dest_path)
                        print(f"   ✅ {item}/")
                    except FileExistsError:
                        pass
            elif os.path.isfile(item_path):
                # 只复制必要的文件类型
                _, ext = os.path.splitext(item)
                if ext.lower() in necessary_exts:
                    shutil.copy2(item_path, dest_path)
                    size = os.path.getsize(item_path) / 1024
                    print(f"   ✅ {item} ({size:.1f} KB)")
    else:
        # exe 在子目录（PyInstaller 模式等）
        for item in os.listdir(exe_dir):
            item_path = os.path.join(exe_dir, item)
            dest_path = os.path.join(package_dir, item)
            
            if item == exe_name:
                continue
            
            if os.path.isdir(item_path):
                # Picture 目录需要复制
                if item == 'Picture':
                    try:
                        shutil.copytree(item_path, dest_path)
                        print(f"   ✅ {item}/")
                    except FileExistsError:
                        pass
            elif os.path.isfile(item_path):
                _, ext = os.path.splitext(item)
                if ext.lower() in necessary_exts:
                    shutil.copy2(item_path, dest_path)
                    size = os.path.getsize(item_path) / 1024
                    print(f"   ✅ {item} ({size:.1f} KB)")
    
    return True


def create_readme(package_dir: str, version: str) -> None:
    """创建 README 文件
    
    Args:
        package_dir: 打包目录
        version: 版本号
    """
    readme_content = f"""# 子网规划师 v{version}

## 简介

子网规划师是一个功能强大、易于使用的网络工具，帮助网络管理员快速进行IP地址规划和子网划分。

## 功能特性

- 完整的 IPv4 和 IPv6 支持
- CIDR 输入支持
- 子网规划和切分
- IP 地址管理（IPAM）
- 网络拓扑可视化
- 多国语言支持
- 结果导出功能

## 使用方法

直接运行 `SubnetPlannerV{version}.exe` 即可启动程序。

## 系统要求

- Windows 7 及以上版本
- 无需安装 Python 环境

## 版权声明

© 2025-2026 Subnet Planner Team. 保留所有权利。

## 联系方式

- 邮箱: ejones.cn@hotmail.com
- GitCode: https://gitcode.com/ejones-cn/Subnet_Planner
"""
    
    readme_path = os.path.join(package_dir, "README.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("   ✅ README.txt")


def parse_args():
    """解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Subnet Planner 一键打包脚本")
    parser.add_argument("-p", "--password", type=str, default=None,
                        help="PFX证书密码，用于代码签名")
    parser.add_argument("-s", "--signtool-path", type=str, default=None,
                        help="signtool.exe路径")
    parser.add_argument("-o", "--output", type=str, default=".",
                        help="输出目录")
    
    return parser.parse_args()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎯 Subnet Planner 一键打包脚本")
    print("=" * 60)
    
    # 解析参数
    args = parse_args()
    pfx_password = args.password
    signtool_path = args.signtool_path
    output_dir = args.output
    
    # 检查证书文件是否存在
    pfx_file = os.path.join(os.getcwd(), "subnetplanner.pfx")
    if os.path.exists(pfx_file) and pfx_password:
        print("\n🔐 检测到证书文件，将进行代码签名")
    elif os.path.exists(pfx_file) and not pfx_password:
        print("\n⚠️  证书文件存在，但未提供密码，将跳过签名")
        print("   如需签名，请使用: python build_package.py -p 你的密码")
    else:
        print("\n⚠️  未找到证书文件 subnetplanner.pfx，将跳过签名")
        print("   如需签名，请先准备 PFX 证书文件")
    
    # 1. 检查环境
    print("\n📋 检查环境...")
    check_python_version()
    
    # 2. 安装依赖
    print("\n📦 检查依赖...")
    check_and_install_dependencies(CompileType.NUITKA)
    
    # 3. 编译（目录模式）
    print("\n🔨 开始编译 (目录模式)...")
    success = compile_with_nuitka(
        output_dir=output_dir,
        pfx_password=pfx_password,
        signtool_path=signtool_path,
        onefile=False
    )
    
    if not success:
        print("\n❌ 编译失败！")
        sys.exit(1)
    
    # 4. 获取版本号
    version = get_version()
    package_name = f"SubnetPlannerV{version}_Package"
    
    # 5. 创建打包目录
    print("\n📁 创建打包目录...")
    package_dir = create_package_dir(package_name)
    
    # 6. 复制编译产物
    print("\n📋 复制编译产物...")
    if not copy_dist_to_package(package_dir):
        print("\n❌ 复制编译产物失败！")
        sys.exit(1)
    
    # 7. 复制资源文件
    print("\n📁 复制资源文件...")
    copy_resource_files(package_dir)
    
    # 8. 创建 README
    print("\n📝 创建说明文件...")
    create_readme(package_dir, version)
    
    # 8.5 代码签名
    if pfx_password:
        print("\n🔐 对 exe 文件进行代码签名...")
        exe_path = os.path.join(package_dir, f"SubnetPlannerV{version}.exe")
        if os.path.exists(exe_path):
            try:
                import subprocess as sign_subprocess
                signtool_path = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
                cmd = [
                    signtool_path, "sign", "/fd", "SHA256", "/a",
                    "/tr", "http://timestamp.digicert.com",  # 时间戳服务器
                    "/td", "sha256",
                    "/f", os.path.join(os.getcwd(), "subnetplanner.pfx"),
                    "/p", pfx_password, exe_path
                ]
                result = sign_subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ 代码签名成功")
                else:
                    print(f"   ⚠️  代码签名失败: {result.stderr}")
            except Exception as e:
                print(f"   ⚠️  代码签名出错: {e}")
        else:
            print("   ⚠️  exe 文件不存在，跳过签名")
    
    # 9. 清理临时文件
    print("\n🧹 清理临时文件...")
    temp_dirs = ["windows_app.dist", "windows_app.build", "windows_app.onefile-build"]
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"   ✅ 删除 {temp_dir}/")
    
    # 10. 完成
    print("\n" + "=" * 60)
    print("🎉 打包完成！")
    print(f"📂 输出目录: {os.path.abspath(package_dir)}")
    print("=" * 60)
    
    # 显示目录内容
    print("\n📦 包内容:")
    for item in sorted(os.listdir(package_dir)):
        item_path = os.path.join(package_dir, item)
        if os.path.isdir(item_path):
            file_count = sum(1 for _ in os.walk(item_path))
            print(f"   📁 {item}/ ({file_count} 层目录)")
        else:
            size = os.path.getsize(item_path) / 1024
            print(f"   📄 {item} ({size:.1f} KB)")


if __name__ == "__main__":
    main()
