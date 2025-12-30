#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的PyInstaller打包脚本
仅生成单文件版本，并支持添加数字签名
"""

import os
import shutil
import sys
import argparse

# 导入版本管理模块
from version import get_version


# 清理旧的打包文件
def clean_old_builds():
    print("清理旧的打包文件...")
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name} 目录")


# 创建新的打包配置
def create_pack_config(pack_type="onefile"):
    """创建打包配置

    Args:
        pack_type: 打包类型，'onefile'或'onedir'
    """
    print(f"创建{pack_type}版本打包配置...")
    
    # 获取版本号
    version = get_version()

    # 基础命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        f"--{pack_type}",  # 打包模式
        "--windowed",  # 窗口模式，无控制台
        "--icon=icon.ico",  # 指定图标
        f"--name=SubnetPlannerV{version}",  # 程序名称（英文版）包含版本号，使用V代替-
        "--distpath=dist",  # 输出目录
        "--workpath=build",  # 工作目录
        "--clean",  # 清理临时文件
        "--noconfirm",  # 覆盖现有文件
        "--hidden-import=tkinter",  # 确保tkinter被正确导入
        "--hidden-import=reportlab",  # 确保reportlab被正确导入
        "--hidden-import=charset_normalizer",  # reportlab的依赖项
        "--hidden-import=openpyxl",  # Excel导出功能依赖
        "--hidden-import=urllib"  # 确保urllib被正确导入
    ]

    # 针对单文件版本的优化参数，减少360误报
    if pack_type == "onefile":
        cmd.extend(
            [
                "--noupx",  # 不使用UPX压缩，减少被误报的概率
                "--disable-windowed-traceback",  # 禁用窗口回溯，减少敏感信息
                # 只排除那些真正可能导致误报的模块
                # 排除Windows特定模块，这些通常不会被应用程序使用
                "--exclude-module=winreg",
                "--exclude-module=_winreg",
                "--exclude-module=win32service",
                "--exclude-module=win32timezone",
                # 排除其他可能不使用的模块
                "--exclude-module=xmlrpc",
                "--exclude-module=sqlite3"
            ]
        )

    cmd.append("windows_app.py")  # 主程序文件

    return cmd


# 执行打包命令
def run_pack(cmd):
    print("执行打包命令...")
    import subprocess

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功！")
        print("标准输出:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
        print("标准错误:")
        print(e.stderr)
        return False


# 测试打包结果

def test_pack_result(sign_info=None):
    print("检查打包结果...")

    # 查找EXE文件 - 匹配包含版本号的文件名（使用V代替-）
    import glob

    exe_files = glob.glob(os.path.join("dist", "**", "SubnetPlannerV*.exe"), recursive=True)

    if exe_files:
        exe_path = exe_files[0]
        print(f"EXE文件已生成: {exe_path}")
        print(f"文件大小: {os.path.getsize(exe_path) / (1024 * 1024):.2f} MB")

        # 如果提供了签名信息，对EXE文件进行签名
        if sign_info:
            sign_exe(exe_path, sign_info)

        return exe_path
    else:
        print("EXE文件未生成！")
        return None


# 对EXE文件进行数字签名
def sign_exe(exe_path, sign_info):
    """
    使用SignTool对EXE文件进行数字签名

    Args:
        exe_path: EXE文件路径
        sign_info: 签名信息字典，包含证书路径和密码
    """
    print(f"\n开始对 {os.path.basename(exe_path)} 进行数字签名...")

    # 检查SignTool是否可用
    import subprocess

    try:
        result = subprocess.run(["signtool", "help"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ SignTool不可用，请确保已安装Windows SDK或Visual Studio")
            return False
    except FileNotFoundError:
        print("❌ SignTool未找到，请确保已安装Windows SDK或Visual Studio")
        return False

    # 构建签名命令
    sign_cmd = [
        "signtool",
        "sign",
        "/fd",
        "sha256",  # 使用SHA256哈希算法
        "/a",  # 自动选择合适的证书
        "/f",
        sign_info["cert_path"],  # 证书文件路径
        "/p",
        sign_info["password"],  # 证书密码
        exe_path,  # 要签名的EXE文件
    ]

    try:
        result = subprocess.run(sign_cmd, check=True, capture_output=True, text=True)
        print("✅ 数字签名成功！")
        print("标准输出:")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 数字签名失败: {e}")
        print("标准错误:")
        print(e.stderr)
        return False


# 主函数
def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="子网规划师打包程序 - 仅生成单文件版本")

    # 代码签名参数
    parser.add_argument("--sign", action="store_true", help="为生成的EXE文件添加数字签名")
    parser.add_argument("--cert-path", type=str, help="代码签名证书文件路径(.pfx格式)")
    parser.add_argument("--password", type=str, help="代码签名证书密码")

    # 解析命令行参数
    args = parser.parse_args()

    # 打印欢迎信息
    print("子网规划师打包程序")
    print("=" * 40)
    print("仅生成单文件版本 (--onefile) [独立运行，优化减少误报]")
    print("=" * 40)

    # 检查签名参数
    sign_info = None
    if args.sign:
        if not args.cert_path or not args.password:
            print("❌ 错误: 使用--sign参数时必须同时提供--cert-path和--password")
            return

        # 检查证书文件是否存在
        if not os.path.exists(args.cert_path):
            print(f"❌ 错误: 证书文件不存在: {args.cert_path}")
            return

        sign_info = {"cert_path": args.cert_path, "password": args.password}
        print(f"\n🔒 将使用证书 {os.path.basename(args.cert_path)} 进行数字签名")

    # 清理旧文件
    clean_old_builds()

    # 执行单文件版本打包
    print(f"\n{'=' * 40}")
    print("开始打包单文件版本...")
    print(f"{'=' * 40}")

    # 创建并执行打包命令
    cmd = create_pack_config("onefile")
    print(f"执行命令: {' '.join(cmd)}")

    if run_pack(cmd):
        # 测试打包结果并进行签名
        exe_path = test_pack_result(sign_info)
        if exe_path:
            print("\n✅ 打包完成！您可以在以下路径找到程序:")
            print(exe_path)

            print("\n💡 提示: 单文件版本已优化减少360误报")

            if sign_info:
                print("\n🔒 提示: 程序已进行数字签名，可降低360等安全软件的误报率")
        else:
            print("\n❌ 打包过程完成，但未找到生成的EXE文件。")
    else:
        print("\n❌ 打包过程失败，请检查错误信息。")

    print(f"\n{'=' * 40}")
    print("打包任务已完成！")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    main()
