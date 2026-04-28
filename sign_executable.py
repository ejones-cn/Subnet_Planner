#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess
import argparse


def is_file_locked(file_path: str) -> bool:
    """检查文件是否被其他进程锁定"""
    try:
        with open(file_path, 'r+b'):
            return False
    except PermissionError:
        return True
    except Exception:
        return False


def wait_for_file_release(file_path: str, max_wait_seconds: int = 30) -> bool:
    """等待文件被释放"""
    print(f"⏳ 等待文件释放，最多等待 {max_wait_seconds} 秒...")
    for i in range(max_wait_seconds):
        if not is_file_locked(file_path):
            print(f"✅ 文件已释放，等待了 {i} 秒")
            return True
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   等待中 ({i + 1}s)...")
    print(f"❌ 文件在 {max_wait_seconds} 秒内仍未释放")
    return False


def sign_executable(executable_path: str, pfx_password: str, pfx_file: str = "subnetplanner.pfx", signtool_path: str = None) -> bool:
    """使用PFX证书对可执行文件进行签名
    
    Args:
        executable_path: 可执行文件路径
        pfx_password: PFX证书密码
        pfx_file: PFX证书文件路径
        signtool_path: signtool.exe工具路径，None表示自动检测
    
    Returns:
        bool: 签名是否成功
    """
    if os.name != 'nt':
        print("❌ 代码签名仅支持Windows系统")
        return False
    
    if not os.path.exists(executable_path):
        print(f"❌ 可执行文件不存在: {executable_path}")
        return False
    
    print(f"\n🔐 正在签名可执行文件: {executable_path}")
    
    if signtool_path is None:
        possible_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
        ]
        
        signtool_path = None
        for path in possible_paths:
            if os.path.exists(path):
                signtool_path = path
                print(f"✅ 自动检测到signtool路径: {signtool_path}")
                break
    
    if not signtool_path:
        print("❌ 未找到 signtool.exe，请使用 --signtool-path 参数指定路径")
        return False
    
    if not os.path.exists(pfx_file):
        print(f"❌ 未找到证书文件: {pfx_file}")
        return False
    
    timestamp_servers = [
        "http://timestamp.digicert.com",
        "http://timestamp.globalsign.com/scripts/timestamp.dll",
        "http://tsa.starfieldtech.com",
        "http://timestamp.comodoca.com/authenticode",
        "http://timestamp.sectigo.com"
    ]
    
    max_retries = 3
    retry_delay = 5
    
    for ts_server in timestamp_servers:
        print(f"\n🔄 尝试使用时间戳服务器: {ts_server}")
        
        sign_cmd = [
            signtool_path,
            "sign",
            "/fd", "SHA256",
            "/f", pfx_file,
            "/p", pfx_password,
            "/t", ts_server,
            executable_path
        ]
        
        for retry in range(max_retries):
            if retry > 0:
                print(f"\n🔄 第 {retry + 1} 次重试签名...")
            
            if not wait_for_file_release(executable_path):
                if retry < max_retries - 1:
                    print(f"⏳ 等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print("❌ 文件持续被占用，跳过此时间戳服务器")
                    break
            
            try:
                print(f"📝 签名命令: {' '.join(sign_cmd[:-2])} [密码隐藏] {executable_path}")
                result = subprocess.run(sign_cmd, check=True, cwd=os.getcwd(), capture_output=True, text=True)
                print("✅ 代码签名成功!")
                return True
            except subprocess.CalledProcessError as e:
                stderr = getattr(e, 'stderr', str(e))
                if "being used by another process" in stderr or "文件正在被另一个进程使用" in stderr:
                    print(f"❌ 文件被占用: {stderr}")
                    if retry < max_retries - 1:
                        print(f"⏳ 等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"❌ 使用 {ts_server} 签名失败（文件被占用）")
                else:
                    print(f"❌ 使用 {ts_server} 签名失败: {stderr}")
                break
            except Exception as e:
                print(f"❌ 签名过程中发生错误: {e}")
                break
        
        print("🔄 尝试下一个时间戳服务器...")
    
    print("❌ 所有时间戳服务器均失败")
    return False


def main():
    parser = argparse.ArgumentParser(description="手动签名可执行文件")
    parser.add_argument("executable", help="要签名的可执行文件路径")
    parser.add_argument("-p", "--password", required=True, help="PFX证书密码")
    parser.add_argument("-c", "--cert", default="subnetplanner.pfx", help="PFX证书文件路径")
    parser.add_argument("-s", "--signtool-path", help="signtool.exe工具路径")
    
    args = parser.parse_args()
    
    if sign_executable(args.executable, args.password, args.cert, args.signtool_path):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

