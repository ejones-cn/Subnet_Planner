#!/usr/bin/env python3
"""
Subnet Planner 编译脚本
支持 Nuitka 和 PyInstaller 两种编译方式
"""

import os
import sys
import json
import subprocess
import argparse
import shutil
from datetime import datetime
from typing import NamedTuple, cast
from enum import Enum


class CompileType(Enum):
    NUITKA = "nuitka"
    PYINSTALLER = "pyinstaller"
    BOTH = "both"



class Args(NamedTuple):
    type: CompileType
    output: str
    clean: bool
    install_deps: bool
    pfx_password: str | None
    signtool_path: str | None
    onefile: bool



def check_python_version() -> None:
    """检查Python版本"""
    required_version = (3, 10)
    if sys.version_info < required_version:
        print(f"❌ 错误: 需要 Python {required_version[0]}.{required_version[1]} 或更高版本")
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
        print(f"❌ 安装 {package_name} 失败: {getattr(e, 'stderr', str(e))}")
        return False


def check_and_install_dependencies(compile_type: CompileType) -> None:
    """检查并安装必要的依赖"""
    print("\n📦 检查依赖...")
    
    try:
        _ = subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        print("❌ 错误: pip 未安装")
        sys.exit(1)
    
    if compile_type == CompileType.NUITKA or compile_type == CompileType.BOTH:
        try:
            _ = subprocess.run([sys.executable, "-m", "nuitka", "--version"],
                          check=True, capture_output=True, text=True)
            print("✅ Nuitka 已安装")
        except subprocess.CalledProcessError:
            print("⏳ 正在安装 Nuitka...")
            if not install_package("nuitka"):
                print("❌ 无法继续编译")
                sys.exit(1)
    
    if compile_type == CompileType.PYINSTALLER or compile_type == CompileType.BOTH:
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
    try:
        import version
        return version.get_version()
    except ImportError as e:
        print(f"⚠️  导入version模块失败: {e}")
        version_file = os.path.join(os.getcwd(), "version.py")
        if os.path.exists(version_file):
            try:
                with open(version_file, "r", encoding="utf-8") as f:
                    content = f.read()
                import re
                version_match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
                if version_match:
                    return version_match.group(1)
            except Exception as e:
                print(f"⚠️  读取版本信息失败: {e}")
    return "2.6.0"


def generate_version_info():
    """从version.py动态生成version_info.py文件
    
    每次编译前更新version_info.py，确保版本信息与version.py一致
    """
    try:
        import version
        
        version_string = version.get_version()
        version_tuple = version.get_version_tuple()
        
        version_info_content = f"""VSVersionInfo(
    ffi=FixedFileInfo(
        filevers={version_tuple + (0,)},
        prodvers={version_tuple + (0,)},
        mask=0x0,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    '080404b0',
                    [
                        StringStruct('CompanyName', 'Subnet Planner Team'),
                        StringStruct('FileDescription', '子网规划师 - IP子网规划工具'),
                        StringStruct('FileVersion', '{version_string}'),
                        StringStruct('InternalName', 'Subnet Planner'),
                        StringStruct('LegalCopyright', 'Copyright © 2025-2026 Subnet Planner Team'),
                        StringStruct('OriginalFilename', 'SubnetPlannerV{version_string}.exe'),
                        StringStruct('ProductName', '子网规划师'),
                        StringStruct('ProductVersion', '{version_string}'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [2052, 1200])])
    ]
)"""
        
        with open("version_info.py", "w", encoding="utf-8") as f:
            _ = f.write(version_info_content)
        print(f"✅ 已更新 version_info.py，版本: {version_string}")
    except Exception as e:
        print(f"⚠️  无法生成 version_info.py: {e}")


def get_version_resource_info() -> dict[str, str]:
    """从version.py获取版本资源信息
    
    Returns:
        dict: 包含公司名称、产品名称、版权信息、文件描述等版本资源信息
    """
    version = get_version_info()
    return {
        "company_name": "Subnet Planner Team",
        "product_name": "Subnet Planner",
        "copyright": "Copyright © 2025-2026 Subnet Planner Team",
        "file_description": "子网规划师 - IP子网规划工具",
        "internal_name": "Subnet Planner",
        "original_filename": f"SubnetPlannerV{version}.exe",
        "file_version": version,
        "product_version": version
    }


def prepare_version_info() -> tuple[str, dict[str, str]]:
    """准备版本信息，生成version_info.py并获取版本号和资源信息
    
    Returns:
        tuple: (版本号, 版本资源字典)
    """
    generate_version_info()
    version = get_version_info()
    version_resource = get_version_resource_info()
    return version, version_resource


def process_output_file(
    output_file: str,
    output_filename: str,
    output_dir: str,
    pfx_password: str | None = None,
    signtool_path: str | None = None,
    dest_filename: str | None = None
) -> bool:
    """处理输出文件：验证、签名、复制
    
    Args:
        output_file: 输出文件路径
        output_filename: 输出文件名
        output_dir: 输出目录
        pfx_password: PFX证书密码
        signtool_path: signtool.exe路径
        dest_filename: 复制时的目标文件名，None则使用output_filename
    
    Returns:
        bool: 处理是否成功
    """
    if not os.path.exists(output_file):
        print(f"❌ 输出文件未找到: {output_file}")
        return False
    
    size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"📦 输出文件: {output_file}")
    print(f"📏 文件大小: {size:.2f} MB")
    print(f"📅 创建时间: {datetime.fromtimestamp(os.path.getmtime(output_file))}")
    
    if not sign_executable(output_file, pfx_password, signtool_path):
        print("⚠️  文件未签名，但继续执行")
    
    if output_dir != "." and output_dir != os.getcwd():
        os.makedirs(output_dir, exist_ok=True)
        final_dest_filename = dest_filename if dest_filename else output_filename
        dest_file = os.path.join(output_dir, final_dest_filename)
        shutil.copy2(output_file, dest_file)
        print(f"📋 已复制到: {dest_file}")
    
    return True


def _restore_database_and_backups(
    temp_db_dir: str,
    original_db: str,
    original_backup_dir: str
) -> None:
    """恢复数据库和备份目录
    
    Args:
        temp_db_dir: 临时目录路径
        original_db: 原始数据库文件名
        original_backup_dir: 原始备份目录名
    """
    temp_db = os.path.join(temp_db_dir, original_db)
    temp_backup_dir = os.path.join(temp_db_dir, original_backup_dir)
    
    if os.path.exists(temp_db):
        try:
            moved_path = shutil.move(temp_db, original_db)
            print(f"✅ 恢复数据库文件成功: {moved_path}")
        except Exception as e:
            print(f"❌ 恢复数据库文件失败: {original_db}, 错误: {e}")
    
    if os.path.exists(temp_backup_dir):
        try:
            moved_path = shutil.move(temp_backup_dir, original_backup_dir)
            print(f"✅ 恢复备份目录成功: {moved_path}")
        except Exception as e:
            print(f"❌ 恢复备份目录失败: {original_backup_dir}, 错误: {e}")


def _generate_spec_content(version: str, output_filename: str, onefile: bool) -> str:
    """生成PyInstaller spec文件内容
    
    Args:
        version: 版本号
        output_filename: 输出文件名
        onefile: 是否单文件模式
    
    Returns:
        str: spec文件内容
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyinstaller_config.json")
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        excludes = config.get("excludes", [])
        datas = config.get("datas", [])
    else:
        print(f"⚠️  配置文件不存在: {config_path}，使用默认配置")
        excludes = [
            "tkinter.test", "unittest", "pytest", "doctest",
            "numpy", "scipy", "matplotlib", "pandas",
            "PIL._tkinter_finder", "PIL.ImageQt", "PIL.TiffImagePlugin",
            "PIL.JpegImagePlugin", "PIL.PngImagePlugin", "PIL.GifImagePlugin",
            "xmlrpc", "urllib3", "requests", "cryptography",
            "cffi", "pycparser", "pyOpenSSL",
            "winreg", "_winreg", "win32api", "win32con", "win32gui",
            "win32process", "win32security", "win32service", "win32serviceutil",
            "win32event", "win32evtlog", "win32evtlogutil", "win32clipboard",
            "win32com", "pythoncom", "win32timezone", "winsound",
            "msvcrt", "fcntl", "pwd", "grp", "spwd", "resource",
            "imp", "modulefinder", "sitecustomize", "usercustomize",
            "idlelib", "pydoc", "test", "lib2to3",
            "debug", "code", "codeop", "readline", "rlcompleter",
        ]
        datas = [["translations.json", "."], ["Subnet_Planner.ico", "."], ["Picture", "Picture"]]
    
    excludes_str = ",\n                 ".join(f"'{module}'" for module in excludes)
    datas_str = ",\n             ".join(f"('{data[0]}', '{data[1]}')" for data in datas)
    
    exe_name = output_filename.rsplit('.', 1)[0]
    
    return f'''# -*- mode: python ; coding: utf-8 -*-

VERSION_STRING = '{version}'

block_cipher = None

a = Analysis(['windows_app.py'],
             pathex=['{os.getcwd()}'],
             binaries=[],
             datas=[{datas_str}],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                 {excludes_str}
             ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='{exe_name}',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        icon='Subnet_Planner.ico',
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        uac_admin=False,
        uac_uiaccess=False,
        onefile={onefile},
        version='version_info.py')
'''


def sign_executable(executable_path: str, pfx_password: str | None = None, signtool_path: str | None = None) -> bool:
    """使用PFX证书对可执行文件进行签名
    
    Args:
        executable_path: 可执行文件路径
        pfx_password: PFX证书密码，None表示需要交互式输入
        signtool_path: signtool.exe工具路径，None表示自动检测
    
    Returns:
        bool: 签名是否成功
    """
    if os.name != 'nt':
        print(f"\n⚠️  代码签名仅支持Windows系统，跳过签名: {executable_path}")
        return True
    
    print(f"\n🔐 正在签名可执行文件: {executable_path}")
    
    if signtool_path and os.path.exists(signtool_path):
        print(f"✅ 使用参数指定的signtool路径: {signtool_path}")
    elif os.environ.get('SIGNTOOL_PATH'):
        signtool_path = os.environ['SIGNTOOL_PATH']
        if os.path.exists(signtool_path):
            print(f"✅ 使用环境变量SIGNTOOL_PATH指定的路径: {signtool_path}")
        else:
            print(f"⚠️  环境变量SIGNTOOL_PATH指定的路径不存在: {signtool_path}")
            signtool_path = None
    else:
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
        print("⚠️  未找到 signtool.exe，无法进行代码签名")
        return False
    
    pfx_file = os.path.join(os.getcwd(), "subnetplanner.pfx")
    if not os.path.exists(pfx_file):
        print("⚠️  未找到证书文件 subnetplanner.pfx")
        return False
    
    if pfx_password is None:
        try:
            import getpass
            pfx_password = getpass.getpass("请输入PFX证书密码: ")
        except Exception as e:
            print(f"⚠️  获取密码失败: {e}")
            print("⚠️  继续执行，但可执行文件未签名")
            return False
    
    timestamp_servers = [
        "http://timestamp.digicert.com",
        "http://timestamp.globalsign.com/scripts/timestamp.dll",
        "http://tsa.starfieldtech.com",
        "http://timestamp.comodoca.com/authenticode",
        "http://timestamp.sectigo.com"
    ]
    
    for ts_server in timestamp_servers:
        print(f"\n🔄 尝试使用时间戳服务器: {ts_server}")
        
        sign_cmd: list[str] = [
            signtool_path,
            "sign",
            "/fd", "SHA256",
            "/f", pfx_file,
            "/p", pfx_password,
            "/t", ts_server,
            executable_path
        ]
        
        try:
            print(f"📝 签名命令: {' '.join(sign_cmd[:-2])} [密码隐藏] {executable_path}")
            _ = subprocess.run(sign_cmd, check=True, cwd=os.getcwd(), capture_output=True, text=True)
            print("✅ 代码签名成功!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 使用 {ts_server} 签名失败: {getattr(e, 'stderr', str(e))}")
            print("🔄 尝试下一个时间戳服务器...")
            continue
        except Exception as e:
            print(f"❌ 签名过程中发生错误: {e}")
            print("🔄 尝试下一个时间戳服务器...")
            continue
    
    print("❌ 所有时间戳服务器均失败")
    print("⚠️  继续执行，但可执行文件未签名")
    return False



def compile_with_nuitka(output_dir: str = ".", pfx_password: str | None = None, signtool_path: str | None = None, onefile: bool = True) -> bool:
    """使用Nuitka编译"""
    print("\n🚀 使用 Nuitka 编译...")
    
    version, version_resource = prepare_version_info()
    output_filename = f"SubnetPlannerV{version}.exe"
    
    temp_db_dir = os.path.join(os.path.expanduser("~"), ".subnet_planner_temp")
    original_db = "SubnetPlanner_data.db"
    original_backup_dir = "ipam_backups"
    should_restore = False
    
    if os.path.exists(original_db) or os.path.exists(original_backup_dir):
        os.makedirs(temp_db_dir, exist_ok=True)
        should_restore = True
        
        if os.path.exists(original_db):
            moved_path = shutil.move(original_db, os.path.join(temp_db_dir, original_db))
            print(f"⏳ 临时移动数据库文件: {original_db} -> {moved_path}")
        
        if os.path.exists(original_backup_dir):
            moved_path = shutil.move(original_backup_dir, os.path.join(temp_db_dir, original_backup_dir))
            print(f"⏳ 临时移动备份目录: {original_backup_dir} -> {moved_path}")
    
    try:
        cmd: list[str] = [
            sys.executable, "-m", "nuitka",
            "--onefile" if onefile else "",
            "--windows-icon-from-ico=Subnet_Planner.ico",
            "--include-data-file=translations.json=translations.json",
            "--include-data-file=Subnet_Planner.ico=Subnet_Planner.ico",
            "--include-data-dir=Picture=Picture",
            "--enable-plugin=tk-inter",
            "--windows-console-mode=disable",
            "--include-windows-runtime-dlls=no",
            "--noinclude-default-mode=error",
            "--assume-yes-for-downloads",
            "--enable-plugin=anti-bloat",
            f"--product-name={version_resource['product_name']}",
            f"--product-version={version}",
            f"--file-version={version}",
            f"--company-name={version_resource['company_name']}",
            f"--copyright={version_resource['copyright']}",
            f"--file-description={version_resource['file_description']}",
            f"--output-filename={output_filename}",
            "windows_app.py"
        ]
        
        cmd = [option for option in cmd if option]
        
        print(f"📝 编译命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ Nuitka 编译成功!")
        
        if onefile:
            output_file = os.path.join(os.getcwd(), output_filename)
        else:
            output_file = os.path.join(os.getcwd(), output_filename)
            if not os.path.exists(output_file):
                for root, _, files in os.walk(os.getcwd()):
                    for file in files:
                        if file.endswith('.exe') and 'SubnetPlanner' in file:
                            output_file = os.path.join(root, file)
                            break
                    if os.path.exists(output_file):
                        break
        
        return process_output_file(output_file, output_filename, output_dir, pfx_password, signtool_path)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Nuitka 编译失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 编译过程中发生错误: {e}")
        return False
    finally:
        if should_restore:
            _restore_database_and_backups(temp_db_dir, original_db, original_backup_dir)



def compile_with_pyinstaller(output_dir: str = ".", pfx_password: str | None = None, signtool_path: str | None = None, onefile: bool = True) -> bool:
    """使用PyInstaller编译"""
    print("\n🚀 使用 PyInstaller 编译...")
    
    version, _ = prepare_version_info()
    output_filename = f"SubnetPlannerV{version}.exe"
    
    print("📝 生成优化的spec文件...")
    spec_content = _generate_spec_content(version, output_filename, onefile)
    
    spec_file = f"{output_filename.rsplit('.', 1)[0]}.spec"
    with open(spec_file, "w", encoding="utf-8") as f:
        _ = f.write(spec_content)
    print(f"✅ 生成 spec 文件: {spec_file}")
    
    try:
        cmd: list[str] = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--log-level=ERROR",
            spec_file
        ]
        
        print(f"📝 编译命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ PyInstaller 编译成功!")
        
        dist_dir = os.path.join(os.getcwd(), "dist")
        output_file = os.path.join(dist_dir, output_filename)
        
        dest_filename = f"{output_filename.rsplit('.', 1)[0]}_PyInstaller.exe"
        return process_output_file(output_file, output_filename, output_dir, pfx_password, signtool_path, dest_filename)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller 编译失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 编译过程中发生错误: {e}")
        return False



def clean_build_files() -> None:
    """清理构建文件"""
    print("\n🧹 清理构建文件...")
    
    clean_items = [
        "build",
        "__pycache__",
        "*.log",
        "windows_app.build",
        "windows_app.dist",
        "windows_app.onefile-build",
        "SubnetPlanner.exe"
    ]
    
    for item in clean_items:
        if "*" in item:
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
    
    parser = argparse.ArgumentParser(description="Subnet Planner 编译脚本")
    _ = parser.add_argument("--type", "-t", choices=["nuitka", "pyinstaller", "both"], 
                       default="nuitka", help="编译方式")
    _ = parser.add_argument("--output", "-o", default=".", help="输出目录")
    _ = parser.add_argument("--clean", action="store_true", help="清理构建文件")
    _ = parser.add_argument("--install-deps", action="store_true", help="仅安装依赖")
    _ = parser.add_argument("--pfx-password", "-p", help="PFX证书密码，不指定则交互式输入")
    _ = parser.add_argument("--signtool-path", "-s", help="signtool.exe工具路径，不指定则自动检测")
    _ = parser.add_argument("--onefile", action="store_true", default=True, help="使用单文件编译模式（默认：是）")
    _ = parser.add_argument("--no-onefile", action="store_false", dest="onefile", help="不使用单文件编译模式")
    args = parser.parse_args()
    
    compile_type_str = cast(str, args.type)
    compile_type = CompileType(compile_type_str)
    
    args.type = compile_type
    
    args = cast(Args, cast(object, args))
    
    check_python_version()
    
    if args.clean:
        clean_build_files()
        if not args.install_deps and args.type == CompileType.NUITKA:
            sys.exit(0)
    
    if args.install_deps:
        check_and_install_dependencies(args.type)
        sys.exit(0)
    
    check_and_install_dependencies(args.type)
    
    if args.output != ".":
        os.makedirs(args.output, exist_ok=True)
    
    success = True
    
    if args.type == CompileType.NUITKA or args.type == CompileType.BOTH:
        success = compile_with_nuitka(args.output, args.pfx_password, args.signtool_path, args.onefile)
    
    if args.type == CompileType.PYINSTALLER or (args.type == CompileType.BOTH and success):
        success = compile_with_pyinstaller(args.output, args.pfx_password, args.signtool_path, args.onefile)
    
    if args.clean and success:
        for item in ["windows_app.build", "windows_app.dist", "windows_app.onefile-build"]:
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
