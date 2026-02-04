#!/usr/bin/env python3
"""
Subnet Planner 编译脚本
支持 Nuitka 和 PyInstaller 两种编译方式
"""

import os
import sys
import subprocess
import argparse
import shutil
from datetime import datetime


def check_python_version() -> None:
    """检查Python版本"""
    version_ok = sys.version_info >= (3, 10)
    if not version_ok:
        print("❌ 错误: 需要 Python 3.10 或更高版本")
        sys.exit(1)
    print(f"✅ Python 版本: {sys.version.split()[0]}")


def install_package(package_name: str, index_url: str = "https://pypi.tuna.tsinghua.edu.cn/simple") -> bool:
    """安装Python包"""
    try:
        _ = subprocess.run([sys.executable, "-m", "pip", "install", package_name, "-i", index_url],
                      check=True, capture_output=True, text=True)
        print(f"✅ 成功安装 {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        # 简化错误处理，避免直接访问stderr属性
        print(f"❌ 安装 {package_name} 失败: {str(e)}")
        return False


def check_and_install_dependencies(compile_type: str) -> None:
    """检查并安装必要的依赖"""
    print("\n📦 检查依赖...")
    
    # 检查 pip
    try:
        _ = subprocess.run([sys.executable, "-m", "pip", "--version"],
                         check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        print("❌ 错误: pip 未安装")
        sys.exit(1)
    
    # 根据编译类型安装依赖
    if compile_type == "nuitka" or compile_type == "both":
        try:
            _ = subprocess.run([sys.executable, "-m", "nuitka", "--version"],
                             check=True, capture_output=True, text=True)
            print("✅ Nuitka 已安装")
        except subprocess.CalledProcessError:
            print("⏳ 正在安装 Nuitka...")
            if not install_package("nuitka"):
                print("❌ 无法继续编译")
                sys.exit(1)
    
    if compile_type == "pyinstaller" or compile_type == "both":
        try:
            _ = subprocess.run([sys.executable, "-m", "PyInstaller", "--version"],
                             check=True, capture_output=True, text=True)
            print("✅ PyInstaller 已安装")
        except subprocess.CalledProcessError:
            print("⏳ 正在安装 PyInstaller...")
            if not install_package("PyInstaller"):
                print("❌ 无法继续编译")
                sys.exit(1)


def get_version_info() -> str:
    """从version.py获取版本信息"""
    # 读取version.py文件获取版本号
    version_file = os.path.join(os.getcwd(), "version.py")
    if os.path.exists(version_file):
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                content = f.read()
            # 提取版本号
            import re
            version_match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
            if version_match:
                return version_match.group(1)
        except Exception as e:
            print(f"⚠️  读取版本信息失败: {e}")
    return "2.5.5"  # 默认版本


def compile_with_nuitka(output_dir: str = ".") -> bool:
    """使用Nuitka编译"""
    print("\n🚀 使用 Nuitka 编译...")
    
    # 获取版本信息
    version = get_version_info()
    output_filename = f"SubnetPlannerV{version}.exe"
    
    # 编译命令
    cmd: list[str] = [
        sys.executable, "-m", "nuitka",
        "--onefile",
        "--windows-console-mode=disable",
        "--windows-icon-from-ico=Subnet_Planner.ico",
        "--include-data-file=translations.json=translations.json",
        "--include-data-file=Subnet_Planner.ico=Subnet_Planner.ico",
        "--include-data-file=icon.ico=icon.ico",
        "--include-data-dir=Picture=Picture",
        "--enable-plugin=tk-inter",
        "--disable-cache=dll-dependencies",
        f"--output-filename={output_filename}",
        "windows_app.py"
    ]
    
    # 执行编译
    try:
        print(f"📝 编译命令: {' '.join(cmd)}")
        _ = subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ Nuitka 编译成功!")
        
        # 检查输出文件
        output_file = os.path.join(os.getcwd(), output_filename)
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"📦 输出文件: {output_file}")
            print(f"📏 文件大小: {size:.2f} MB")
            print(f"📅 创建时间: {datetime.fromtimestamp(os.path.getmtime(output_file))}")
            
            # 如果指定了输出目录，复制文件
            if output_dir != "." and output_dir != os.getcwd():
                os.makedirs(output_dir, exist_ok=True)
                dest_file = os.path.join(output_dir, output_filename)
                _ = shutil.copy2(output_file, dest_file)
                print(f"📋 已复制到: {dest_file}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Nuitka 编译失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 编译过程中发生错误: {e}")
        return False


def compile_with_pyinstaller(output_dir: str = ".") -> bool:
    """使用PyInstaller编译"""
    print("\n🚀 使用 PyInstaller 编译...")
    
    # 检查spec文件是否存在
    spec_file = "SubnetPlannerV2.5.5.spec"
    if not os.path.exists(spec_file):
        print(f"❌ 错误: 找不到 spec 文件 {spec_file}")
        return False
    
    # 编译命令
    cmd: list[str] = [
        sys.executable, "-m", "PyInstaller",
        spec_file
    ]
    
    # 执行编译
    try:
        print(f"📝 编译命令: {' '.join(cmd)}")
        _ = subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ PyInstaller 编译成功!")
        
        # 检查输出文件
        dist_dir = os.path.join(os.getcwd(), "dist")
        output_file = os.path.join(dist_dir, "SubnetPlannerV2.5.5.exe")
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"📦 输出文件: {output_file}")
            print(f"📏 文件大小: {size:.2f} MB")
            print(f"📅 创建时间: {datetime.fromtimestamp(os.path.getmtime(output_file))}")
            
            # 如果指定了输出目录，复制文件
            if output_dir != "." and output_dir != os.getcwd():
                os.makedirs(output_dir, exist_ok=True)
                dest_file = os.path.join(output_dir, "SubnetPlanner_PyInstaller.exe")
                _ = shutil.copy2(output_file, dest_file)
                print(f"📋 已复制到: {dest_file}")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 编译失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 编译过程中发生错误: {e}")
        return False


def clean_build_files() -> None:
    """清理构建文件"""
    print("\n🧹 清理构建文件...")
    
    # 需要清理的目录和文件
    clean_items: list[str] = [
        "build",
        "dist",
        "__pycache__",
        "*.spec",
        "*.log",
        "windows_app.build",
        "windows_app.dist",
        "windows_app.onefile-build",
        "SubnetPlannerV*.exe"  # 清理所有版本的Nuitka输出文件
    ]
    
    for item in clean_items:
        if "*" in item:
            # 处理通配符
            import glob
            for file in glob.glob(item):
                if os.path.isfile(file):
                    os.remove(file)
                    print(f"🗑️ 删除文件: {file}")
        elif os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
                print(f"🗑️ 删除目录: {item}")
            else:
                os.remove(item)
                print(f"🗑️ 删除文件: {item}")
    
    print("✅ 清理完成")


def main() -> None:
    """主函数"""
    print("\n🎯 Subnet Planner 编译脚本")
    print("=" * 50)
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="Subnet Planner 编译脚本")
    _ = parser.add_argument("--type", "-t", choices=["nuitka", "pyinstaller", "both"], 
                          default="nuitka", help="编译方式")
    _ = parser.add_argument("--output", "-o", default=".", help="输出目录")
    _ = parser.add_argument("--clean", action="store_true", help="清理构建文件")
    _ = parser.add_argument("--install-deps", action="store_true", help="仅安装依赖")
    args: argparse.Namespace = parser.parse_args()
    
    # 从args中提取所有需要的变量，并添加类型注解
    type_arg: str = getattr(args, 'type', 'nuitka')
    output: str = getattr(args, 'output', '.')
    clean: bool = getattr(args, 'clean', False)
    install_deps: bool = getattr(args, 'install_deps', False)
    
    # 检查Python版本
    check_python_version()
    
    # 如果指定了清理，先清理
    if clean:
        clean_build_files()
        if not install_deps and type_arg == "nuitka":
            # 如果只是清理，不执行后续操作
            sys.exit(0)
    
    # 如果只是安装依赖
    if install_deps:
        check_and_install_dependencies(type_arg)
        sys.exit(0)
    
    # 检查并安装依赖
    check_and_install_dependencies(type_arg)
    
    # 创建输出目录
    if output != ".":
        os.makedirs(output, exist_ok=True)
    
    # 执行编译
    success: bool = True
    
    if type_arg == "nuitka" or type_arg == "both":
        success = compile_with_nuitka(output)
    
    if type_arg == "pyinstaller" or (type_arg == "both" and success):
        success = compile_with_pyinstaller(output)
    
    # 清理临时文件（如果需要）
    if clean and success:
        # 只清理Nuitka的临时文件，保留PyInstaller的dist目录
        clean_items: list[str] = ["windows_app.build", "windows_app.dist", "windows_app.onefile-build"]
        for item in clean_items:
            if os.path.exists(item):
                shutil.rmtree(item)
                print(f"🗑️ 清理临时目录: {item}")
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 编译成功! 🎉")
        sys.exit(0)
    else:
        print("💥 编译失败! 💥")
        sys.exit(1)


if __name__ == "__main__":
    main()
