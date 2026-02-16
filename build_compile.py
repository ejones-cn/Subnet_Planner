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
from typing import NamedTuple, cast
from enum import Enum


# 定义编译类型枚举
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
    
    # 检查 pip
    try:
        _ = subprocess.run([sys.executable, "-m", "pip", "--version"],
                      check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        print("❌ 错误: pip 未安装")
        sys.exit(1)
    
    # 根据编译类型安装依赖
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
    # 使用动态导入方式获取版本信息，保留完整的版本模块功能
    try:
        import version
        return version.get_version()
    except ImportError as e:
        print(f"⚠️  导入version模块失败: {e}")
        # 降级方案：文件读取方式获取版本号
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
    return "2.6.0"  # 默认版本



def sign_executable(executable_path: str, pfx_password: str | None = None, signtool_path: str | None = None) -> bool:
    """使用PFX证书对可执行文件进行签名
    
    Args:
        executable_path: 可执行文件路径
        pfx_password: PFX证书密码，None表示需要交互式输入
        signtool_path: signtool.exe工具路径，None表示自动检测
    
    Returns:
        bool: 签名是否成功
    """
    # 检查操作系统，非Windows系统跳过签名
    if os.name != 'nt':
        print(f"\n⚠️  代码签名仅支持Windows系统，跳过签名: {executable_path}")
        return True
    
    print(f"\n🔐 正在签名可执行文件: {executable_path}")
    
    # 1. 优先使用函数参数传入的路径
    if signtool_path and os.path.exists(signtool_path):
        print(f"✅ 使用参数指定的signtool路径: {signtool_path}")
    # 2. 其次检查环境变量SIGNTOOL_PATH
    elif os.environ.get('SIGNTOOL_PATH'):
        signtool_path = os.environ['SIGNTOOL_PATH']
        if os.path.exists(signtool_path):
            print(f"✅ 使用环境变量SIGNTOOL_PATH指定的路径: {signtool_path}")
        else:
            print(f"⚠️  环境变量SIGNTOOL_PATH指定的路径不存在: {signtool_path}")
            signtool_path = None
    # 3. 最后检查默认安装路径
    else:
        possible_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe",  # 新安装的路径
            r"C:\Program Files (x86)\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files\Windows Kits\10\bin\x64\signtool.exe",
            r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"  # App Certification Kit 路径
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
    
    # 检查PFX证书文件
    pfx_file = os.path.join(os.getcwd(), "subnetplanner.pfx")
    if not os.path.exists(pfx_file):
        print("⚠️  未找到证书文件 subnetplanner.pfx")
        return False
    
    # 获取密码
    if pfx_password is None:
        try:
            import getpass
            pfx_password = getpass.getpass("请输入PFX证书密码: ")
        except Exception as e:
            print(f"⚠️  获取密码失败: {e}")
            print("⚠️  继续执行，但可执行文件未签名")
            return False
    
    # 签名命令 - 尝试多个时间戳服务器
    timestamp_servers = [
        "http://timestamp.digicert.com",
        "http://timestamp.globalsign.com/scripts/timestamp.dll",
        "http://tsa.starfieldtech.com",
        "http://timestamp.comodoca.com/authenticode",
        "http://timestamp.sectigo.com"  # 原服务器，作为最后的备选
    ]
    
    for ts_server in timestamp_servers:
        print(f"\n🔄 尝试使用时间戳服务器: {ts_server}")
        
        # 签名命令
        sign_cmd: list[str] = [
            signtool_path,
            "sign",
            "/fd", "SHA256",
            "/f", pfx_file,
            "/p", pfx_password,  # 添加密码参数
            "/t", ts_server,  # 使用当前时间戳服务器
            executable_path
        ]
        
        try:
            print(f"📝 签名命令: {' '.join(sign_cmd[:-2])} [密码隐藏] {executable_path}")  # 隐藏密码
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



def compile_with_nuitka(output_dir: str = ".", pfx_password: str | None = None, signtool_path: str | None = None) -> bool:
    """使用Nuitka编译"""
    print("\n🚀 使用 Nuitka 编译...")
    
    # 获取版本信息
    version = get_version_info()
    output_filename = f"SubnetPlannerV{version}.exe"
    
    # 编译命令 - 优化配置以减少杀毒软件误报（仅使用稳定支持的选项）
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
        # 仅保留稳定支持的选项，减少可疑特征
        "--lto=no",  # 禁用链接时优化，减少可疑特征
        "--show-progress",  # 显示进度
        # 添加 Windows 可执行文件元数据
        "--product-name=Subnet Planner",
        f"--product-version={version}",
        f"--file-version={version}",
        "--file-description=Subnet Planner - 子网规划师",
        "--company-name=Subnet Planner Team",
        "--copyright=Copyright © 2025-2026 Subnet Planner Team",
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
            
            # 对可执行文件进行签名
            _ = sign_executable(output_file, pfx_password, signtool_path)
            
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



def compile_with_pyinstaller(output_dir: str = ".", pfx_password: str | None = None, signtool_path: str | None = None) -> bool:
    """使用PyInstaller编译"""
    print("\n🚀 使用 PyInstaller 编译...")
    
    # 获取版本信息
    version = get_version_info()
    
    # 生成新的spec文件，优化配置以减少杀毒软件误报
    print("📝 生成优化的spec文件...")
    
    # 构建spec文件内容
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['windows_app.py'],
             pathex=['{os.getcwd()}'],
             binaries=[],
             datas=[('translations.json', '.'), ('Subnet_Planner.ico', '.'), ('icon.ico', '.'), ('Picture', 'Picture')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[
                 'tkinter.test',
                 'unittest',
                 'pytest',
                 'doctest',
                 'numpy',
                 'scipy',
                 'matplotlib',
                 'pandas',
                 'PIL._tkinter_finder',
                 'PIL.ImageQt',
                 'PIL.TiffImagePlugin',
                 'PIL.JpegImagePlugin',
                 'PIL.PngImagePlugin',
                 'PIL.GifImagePlugin',
                 'email',
                 'smtplib',
                 'http',
                 'xmlrpc',
                 'urllib3',
                 'requests',
                 'socket',
                 'ssl',
                 'cryptography',
                 'cffi',
                 'pycparser',
                 'pyOpenSSL',
                 'tkinter.tix',
                 'tkinter.scrolledtext',
                 'tkinter.colorchooser',
                 'tkinter.filedialog',
                 'tkinter.messagebox',
                 'tkinter.commondialog',
                 'tkinter.dnd',
                 'tkinter.font',
                 'tkinter.ttk',
                 'tkinter.constants',
                 'tkinter.vars',
                 'tkinter.windows',
                 'tkinter.tk',
                 'tkinter.mainloop',
                 'tkinter',
                 'tcl',
                 'tk',
                 'winreg',
                 '_winreg',
                 'win32api',
                 'win32con',
                 'win32gui',
                 'win32process',
                 'win32security',
                 'win32service',
                 'win32serviceutil',
                 'win32event',
                 'win32evtlog',
                 'win32evtlogutil',
                 'win32clipboard',
                 'win32com',
                 'pythoncom',
                 'win32timezone',
                 'winsound',
                 'msvcrt',
                 'ctypes.wintypes',
                 'ctypes',
                 'os',
                 'sys',
                 'shutil',
                 'tempfile',
                 'glob',
                 're',
                 'json',
                 'datetime',
                 'time',
                 'calendar',
                 'math',
                 'random',
                 'string',
                 'collections',
                 'itertools',
                 'functools',
                 'operator',
                 'enum',
                 'typing',
                 'dataclasses',
                 'abc',
                 'contextlib',
                 'io',
                 'logging',
                 'traceback',
                 'inspect',
                 'importlib',
                 'pkgutil',
                 'site',
                 'sysconfig',
                 'platform',
                 'getpass',
                 'locale',
                 'codecs',
                 'encodings',
                 'unicodedata',
                 'stringprep',
                 'hashlib',
                 'hmac',
                 'base64',
                 'binascii',
                 'struct',
                 'array',
                 'heapq',
                 'bisect',
                 'pickle',
                 'copy',
                 'copyreg',
                 'marshal',
                 'shelve',
                 'dbm',
                 'sqlite3',
                 'zlib',
                 'gzip',
                 'bz2',
                 'lzma',
                 'zipfile',
                 'tarfile',
                 'filecmp',
                 'stat',
                 'fcntl',
                 'pwd',
                 'grp',
                 'spwd',
                 'errno',
                 'signal',
                 'atexit',
                 'resource',
                 'select',
                 'selectors',
                 'poll',
                 'epoll',
                 'kqueue',
                 'kevent',
                 'threading',
                 'multiprocessing',
                 'concurrent',
                 'asyncio',
                 'queue',
                 'sched',
                 'timeit',
                 'profile',
                 'pstats',
                 'cProfile',
                 'trace',
                 'dis',
                 'ast',
                 'compileall',
                 'py_compile',
                 'imp',
                 'modulefinder',
                 'runpy',
                 'pkg_resources',
                 'setuptools',
                 'distutils',
                 'ensurepip',
                 'venv',
                 'wheel',
                 'pip',
                 'easy_install',
                 'sitecustomize',
                 'usercustomize',
                 'idlelib',
                 'pydoc',
                 'doctest',
                 'test',
                 'lib2to3',
                 'debug',
                 'inspect',
                 'code',
                 'codeop',
                 'readline',
                 'rlcompleter',
                 'linecache',
                 'tracemalloc',
                 'gc',
                 'weakref',
                 'gc',
                 'gcmodule',
                 'faulthandler',
                 'syslog',
                 'logging.handlers',
                 'logging.config',
                 'logging.handlers.SysLogHandler',
                 'logging.handlers.HTTPHandler',
                 'logging.handlers.SMTPHandler',
                 'logging.handlers.RotatingFileHandler',
                 'logging.handlers.TimedRotatingFileHandler',
                 'logging.handlers.MemoryHandler',
                 'logging.handlers.SocketHandler',
                 'logging.handlers.WatchedFileHandler',
                 'logging.handlers.QueueHandler',
                 'logging.handlers.QueueListener',
                 'logging.handlers.NullHandler',
                 'logging.handlers.BufferingHandler',
                 'logging.handlers.StreamHandler',
                 'logging.handlers.FileHandler',
                 'logging.handlers.RotatingFileHandler',
                 'logging.handlers.TimedRotatingFileHandler',
                 'logging.handlers.SocketHandler',
                 'logging.handlers.DatagramHandler',
                 'logging.handlers.SysLogHandler',
                 'logging.handlers.NTEventLogHandler',
                 'logging.handlers.SMTPHandler',
                 'logging.handlers.MemoryHandler',
                 'logging.handlers.HTTPHandler',
                 'logging.handlers.BufferingHandler',
                 'logging.handlers.WatchedFileHandler',
                 'logging.handlers.QueueHandler',
                 'logging.handlers.QueueListener',
                 'logging.handlers.NullHandler',
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
        name='SubnetPlannerV{version}',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
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
        onefile=True)
'''
    
    # 写入spec文件
    spec_file = f"SubnetPlannerV{version}.spec"
    with open(spec_file, "w", encoding="utf-8") as f:
        _ = f.write(spec_content)
    print(f"✅ 生成 spec 文件: {spec_file}")
    
    # 编译命令 - 优化配置以减少杀毒软件误报
    cmd: list[str] = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--log-level=ERROR",
        spec_file
    ]
    
    # 执行编译
    try:
        print(f"📝 编译命令: {' '.join(cmd)}")
        _ = subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ PyInstaller 编译成功!")
        
        # 检查输出文件
        dist_dir = os.path.join(os.getcwd(), "dist")
        output_file = os.path.join(dist_dir, f"SubnetPlannerV{version}.exe")
        
        if os.path.exists(output_file):
            size = os.path.getsize(output_file) / (1024 * 1024)  # MB
            print(f"📦 输出文件: {output_file}")
            print(f"📏 文件大小: {size:.2f} MB")
            print(f"📅 创建时间: {datetime.fromtimestamp(os.path.getmtime(output_file))}")
            
            # 对可执行文件进行签名
            _ = sign_executable(output_file, pfx_password, signtool_path)
            
            # 如果指定了输出目录，复制文件
            if output_dir != "." and output_dir != os.getcwd():
                os.makedirs(output_dir, exist_ok=True)
                dest_file = os.path.join(output_dir, f"SubnetPlannerV{version}_PyInstaller.exe")
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
    clean_items = [
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
    _ = parser.add_argument("--pfx-password", "-p", help="PFX证书密码，不指定则交互式输入")
    _ = parser.add_argument("--signtool-path", "-s", help="signtool.exe工具路径，不指定则自动检测")
    args = parser.parse_args()
    
    # 使用cast明确指定args.type为字符串类型
    compile_type_str = cast(str, args.type)
    # 将字符串转换为CompileType枚举
    compile_type = CompileType(compile_type_str)
    
    # 将转换后的枚举值赋值回args.type
    args.type = compile_type
    
    # 使用cast为args对象添加类型注解，先转换为object再转换为Args
    args = cast(Args, cast(object, args))
    
    # 检查Python版本
    check_python_version()
    
    # 如果指定了清理，先清理
    if args.clean:
        clean_build_files()
        if not args.install_deps and args.type == CompileType.NUITKA:
            # 如果只是清理，不执行后续操作
            sys.exit(0)
    
    # 如果只是安装依赖
    if args.install_deps:
        check_and_install_dependencies(args.type)
        sys.exit(0)
    
    # 检查并安装依赖
    check_and_install_dependencies(args.type)
    
    # 创建输出目录
    if args.output != ".":
        os.makedirs(args.output, exist_ok=True)
    
    # 执行编译
    success = True
    
    if args.type == CompileType.NUITKA or args.type == CompileType.BOTH:
        success = compile_with_nuitka(args.output, args.pfx_password, args.signtool_path)
    
    if args.type == CompileType.PYINSTALLER or (args.type == CompileType.BOTH and success):
        success = compile_with_pyinstaller(args.output, args.pfx_password, args.signtool_path)
    
    # 清理临时文件（如果需要）
    if args.clean and success:
        # 只清理Nuitka的临时文件，保留PyInstaller的dist目录
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
