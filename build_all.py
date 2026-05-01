#!/usr/bin/env python3
"""
Subnet Planner One-Click Build Script
Combines compilation and installer generation
"""

import os
import sys
import subprocess
import argparse
import shutil


def _get_version() -> str:
    """从 version.py 获取版本号"""
    try:
        import version
        return version.get_version()
    except ImportError:
        version_file = os.path.join(os.getcwd(), "version.py")
        if os.path.exists(version_file):
            try:
                with open(version_file, "r", encoding="utf-8") as f:
                    content = f.read()
                import re
                match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
            except Exception:
                pass
    return "3.0.0"


def check_python():
    """检查 Python 版本"""
    print("=" * 50)
    print(" Subnet Planner Build All Script")
    print("=" * 50)
    print()

    print("[INFO] Python detected")
    print(f"[INFO] Python version: {sys.version}")
    print()


def run_compile(pfx_password=None, upx=False, signtool_path=None):
    """运行编译脚本

    Args:
        pfx_password: PFX 证书密码
        upx: 是否启用 UPX 压缩
        signtool_path: signtool.exe 路径
    """
    print("=" * 50)
    print(" Step 1/2: Compile Program")
    print("=" * 50)
    print()

    cmd = [sys.executable, "build_compile.py"]

    if upx:
        cmd.append("--upx")
        print("[INFO] UPX compression enabled")

    if signtool_path:
        cmd.extend(["--signtool-path", signtool_path])

    if pfx_password:
        print("[INFO] Certificate found: subnetplanner.pfx")
        print("[INFO] Password provided via command line")
        print("[INFO] Will sign code")
        cmd.extend([f"--pfx-password={pfx_password}"])
    elif os.path.exists("subnetplanner.pfx"):
        print("[INFO] Certificate found: subnetplanner.pfx")
        try:
            import getpass
            pfx_password = getpass.getpass("Enter PFX password (Enter to skip): ")
            if pfx_password:
                print("[INFO] Will sign code")
                cmd.extend([f"--pfx-password={pfx_password}"])
            else:
                print("[INFO] Skipping code signing")
        except Exception:
            print("[INFO] Skipping code signing")
    else:
        print("[INFO] Certificate not found, skipping signing")

    print()
    print(f"[INFO] Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=os.getcwd())

    if result.returncode != 0:
        print()
        print("[ERROR] Compilation failed!")
        return False

    print()
    print("[INFO] Compilation succeeded!")
    return True


def check_compile_output():
    """检查编译输出是否存在"""
    print()
    print("=" * 50)
    print(" Step 2/2: Generate Installer")
    print("=" * 50)
    print()

    if not os.path.exists("SubnetPlanner_Nuitka.dist"):
        print("[ERROR] Nuitka output directory not found")
        return False

    if not os.path.exists("SubnetPlanner_Nuitka.dist\\SubnetPlanner.exe"):
        print("[ERROR] Main executable not found")
        return False

    return True


def find_iscc():
    """查找 Inno Setup 编译器"""
    possible_paths = [
        "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
        "C:\\Program Files\\Inno Setup 6\\ISCC.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs\\Inno Setup 6\\ISCC.exe")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


def generate_installer(pfx_password=None):
    """生成安装包

    Args:
        pfx_password: PFX 证书密码，有则自动配置 SignTool 签名
    """
    iscc = find_iscc()

    if not iscc:
        print("[ERROR] Inno Setup 6 not found")
        return False

    print(f"[INFO] Using Inno Setup: {iscc}")
    print()

    os.makedirs("installer", exist_ok=True)

    version = _get_version()
    print(f"[INFO] Building installer for version {version}...")

    iscc_cmd = [iscc, f"/DMyAppVersion={version}"]

    signtool_exe = find_signtool()
    if pfx_password and signtool_exe and os.path.exists("subnetplanner.pfx"):
        sign_cmd = f'"{signtool_exe}" sign /f "subnetplanner.pfx" /p {pfx_password} /t http://timestamp.digicert.com /fd sha256 $f'
        iscc_cmd.extend([f"/Smysign={sign_cmd}"])
        print("[INFO] SignTool configured for Inno Setup")
    else:
        if not pfx_password:
            print("[INFO] No PFX password, skipping Inno Setup SignTool")
        elif not signtool_exe:
            print("[INFO] signtool.exe not found, skipping Inno Setup SignTool")
        elif not os.path.exists("subnetplanner.pfx"):
            print("[INFO] No PFX certificate, skipping Inno Setup SignTool")

    iscc_cmd.append("SubnetPlanner.iss")
    result = subprocess.run(iscc_cmd, cwd=os.getcwd())

    if result.returncode != 0:
        print()
        print("[ERROR] Installer compilation failed!")
        return False

    print()
    print("[INFO] Installer compiled!")
    return True


def find_signtool():
    """查找 signtool.exe"""
    base_dir = "C:\\Program Files (x86)\\Windows Kits\\10\\bin"

    if not os.path.exists(base_dir):
        return None

    versions = []
    for item in os.listdir(base_dir):
        if item.startswith("10.") and os.path.isdir(os.path.join(base_dir, item)):
            versions.append(item)

    versions.sort(reverse=True)

    for version in versions:
        signtool_path = os.path.join(base_dir, version, "x64", "signtool.exe")
        if os.path.exists(signtool_path):
            return signtool_path

    return None


def sign_installer(pfx_password):
    """签名安装包

    Args:
        pfx_password: PFX 证书密码
    """
    if not os.path.exists("subnetplanner.pfx"):
        return True

    if not pfx_password:
        print("[INFO] No password provided, skipping installer signing")
        return True

    print()
    print("[INFO] Starting installer code signing...")

    signtool = find_signtool()

    if not signtool:
        print("[WARNING] signtool.exe not found, skipping installer sign")
        return True

    version = _get_version()
    installer = f"installer\\SubnetPlannerV{version}_Setup.exe"

    if not os.path.exists(installer):
        print(f"[ERROR] Installer file not found: {installer}")
        return False

    print(f"[INFO] Signing installer: {installer}")
    print(f"[INFO] Using signtool: {signtool}")

    timestamp_servers = [
        "http://timestamp.digicert.com",
        "http://timestamp.sectigo.com"
    ]

    for ts_server in timestamp_servers:
        cmd = [
            signtool,
            "sign",
            "/fd", "SHA256",
            "/f", "subnetplanner.pfx",
            "/p", pfx_password,
            "/t", ts_server,
            installer
        ]

        try:
            result = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)
            if result.returncode == 0:
                print("[SUCCESS] Installer signed successfully!")
                return True
            else:
                print(f"[ERROR] Installer signing failed with error code: {result.returncode}")
                if result.stderr:
                    print(f"[ERROR] {result.stderr}")
        except Exception as e:
            print(f"[ERROR] {e}")

        if ts_server != timestamp_servers[-1]:
            print("[INFO] Trying alternative timestamp server...")

    print("[ERROR] Failed to sign installer with all timestamp servers")
    return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Subnet Planner One-Click Build Script")
    parser.add_argument("--pfx-password", "-p", help="PFX certificate password")
    parser.add_argument("--upx", action="store_true", default=False,
                        help="Enable UPX compression (may trigger antivirus false positives)")
    parser.add_argument("--signtool-path", "-s", help="Path to signtool.exe")

    args = parser.parse_args()

    check_python()

    if not run_compile(args.pfx_password, args.upx, args.signtool_path):
        print()
        input("Press Enter to continue...")
        sys.exit(1)

    if not check_compile_output():
        print()
        input("Press Enter to continue...")
        sys.exit(1)

    if not generate_installer(args.pfx_password):
        print()
        input("Press Enter to continue...")
        sys.exit(1)

    if os.path.exists("subnetplanner.pfx"):
        sign_installer(args.pfx_password)

    version = _get_version()
    installer_path = f"installer\\SubnetPlannerV{version}_Setup.exe"

    print()
    print("=" * 50)
    print(" Build All Completed!")
    print("=" * 50)
    print()
    print("Output:")
    if os.path.exists(installer_path):
        size_mb = os.path.getsize(installer_path) / (1024 * 1024)
        print(f"  Installer: {installer_path} ({size_mb:.1f} MB)")
    print("  Build: SubnetPlanner_Nuitka.dist\\")
    print()
    input("Press Enter to continue...")


if __name__ == "__main__":
    main()
