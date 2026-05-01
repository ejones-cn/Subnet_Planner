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

def check_python():
    """Check Python version"""
    print("=" * 50)
    print(" Subnet Planner Build All Script")
    print("=" * 50)
    print()
    
    print("[INFO] Python detected")
    print(f"[INFO] Python version: {sys.version}")
    print()

def run_compile(pfx_password=None):
    """Run the compilation script"""
    print("=" * 50)
    print(" Step 1/2: Compile Program")
    print("=" * 50)
    print()
    
    cmd = [sys.executable, "build_compile.py"]
    
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
        except:
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
    """Check if compilation output exists"""
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
    """Find Inno Setup compiler"""
    possible_paths = [
        "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
        "C:\\Program Files\\Inno Setup 6\\ISCC.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs\\Inno Setup 6\\ISCC.exe")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def generate_installer():
    """Generate the installer"""
    iscc = find_iscc()
    
    if not iscc:
        print("[ERROR] Inno Setup 6 not found")
        return False
    
    print(f"[INFO] Using Inno Setup: {iscc}")
    print()
    
    os.makedirs("installer", exist_ok=True)
    
    print("[INFO] Compiling installer...")
    result = subprocess.run([iscc, "SubnetPlanner.iss"], cwd=os.getcwd())
    
    if result.returncode != 0:
        print()
        print("[ERROR] Installer compilation failed!")
        return False
    
    print()
    print("[INFO] Installer compiled!")
    return True

def find_signtool():
    """Find signtool.exe"""
    import glob
    
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
    """Sign the installer"""
    if not os.path.exists("subnetplanner.pfx"):
        return True
    
    if not pfx_password:
        print("[INFO] No password provided, skipping installer signing")
        return True
    
    print()
    print("[INFO] Starting code signing...")
    
    signtool = find_signtool()
    
    if not signtool:
        print("[WARNING] signtool.exe not found, skipping installer sign")
        return True
    
    installer = "installer\\SubnetPlannerV3.0.0_Setup.exe"
    
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
    parser = argparse.ArgumentParser(description="Subnet Planner One-Click Build Script")
    parser.add_argument("--pfx-password", "-p", help="PFX certificate password")
    
    args = parser.parse_args()
    
    check_python()
    
    if not run_compile(args.pfx_password):
        print()
        input("Press Enter to continue...")
        sys.exit(1)
    
    if not check_compile_output():
        print()
        input("Press Enter to continue...")
        sys.exit(1)
    
    if not generate_installer():
        print()
        input("Press Enter to continue...")
        sys.exit(1)
    
    if os.path.exists("subnetplanner.pfx"):
        sign_installer(args.pfx_password)
    
    print()
    print("=" * 50)
    print(" Build All Completed!")
    print("=" * 50)
    print()
    print("Output:")
    if os.path.exists("installer\\SubnetPlannerV3.0.0_Setup.exe"):
        print("  Installer: installer\\SubnetPlannerV3.0.0_Setup.exe")
    print("  Build: SubnetPlanner_Nuitka.dist\\")
    print()
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
