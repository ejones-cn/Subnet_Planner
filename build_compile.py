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
import time
from datetime import datetime
from typing import NamedTuple, cast
from enum import Enum

# Windows 终端默认 GBK 编码无法输出 emoji，强制使用 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # pyright: ignore[reportAttributeAccessIssue]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # pyright: ignore[reportAttributeAccessIssue]


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


def _clean_dist_directory(dist_dir: str) -> None:
    """清理 dist 目录中不必要的文件，减小体积和文件数
    
    Args:
        dist_dir: dist 目录路径
    """
    print("\n🧹 清理 dist 目录中不必要的文件...")
    
    removed_count = 0
    removed_size = 0
    
    # 1. 清理 tcl/tzdata - 只保留 Asia 和 Etc 目录（中国用户需要）
    tzdata_dir = os.path.join(dist_dir, "tcl", "tzdata")
    if os.path.exists(tzdata_dir):
        for item in os.listdir(tzdata_dir):
            item_path = os.path.join(tzdata_dir, item)
            if os.path.isdir(item_path) and item not in ("Asia", "Etc"):
                try:
                    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(item_path, onerror=lambda e: None) for f in fn)
                    removed_size += size
                    removed_count += sum(1 for _, _, fn in os.walk(item_path, onerror=lambda e: None) for _ in fn)
                    shutil.rmtree(item_path, ignore_errors=True)
                except OSError:
                    pass
    
    # 2. 清理 tcl/tzdata - 保留中日韩及常用地区
    if os.path.exists(tzdata_dir):
        # 保留：Asia（中日韩）、Etc（UTC等）、Pacific、America（少量）
        keep_regions = {"Asia", "Etc", "Pacific"}
        for item in os.listdir(tzdata_dir):
            item_path = os.path.join(tzdata_dir, item)
            if os.path.isdir(item_path) and item not in keep_regions:
                try:
                    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(item_path, onerror=lambda e: None) for f in fn)
                    removed_size += size
                    removed_count += sum(1 for _, _, fn in os.walk(item_path, onerror=lambda e: None) for _ in fn)
                    shutil.rmtree(item_path, ignore_errors=True)
                except OSError:
                    pass
    
    # 3. 清理 tcl/tzdata/Asia - 保留中日韩相关时区
    asia_dir = os.path.join(tzdata_dir, "Asia")
    if os.path.exists(asia_dir):
        # 简中/繁中/日/韩/英相关时区
        keep_zones = {
            "Shanghai", "Hong_Kong", "Taipei", "Macao",       # 中
            "Tokyo", "Seoul", "Singapore",                     # 日韩
            "Kolkata", "Bangkok", "Dubai", "Manila",           # 常用亚洲
        }
        for item in os.listdir(asia_dir):
            item_path = os.path.join(asia_dir, item)
            if os.path.isfile(item_path):
                zone_name = item.replace(".msg", "")
                if zone_name not in keep_zones:
                    removed_size += os.path.getsize(item_path)
                    removed_count += 1
                    os.remove(item_path)
    
    # 4. 清理 tcl/tzdata/Pacific - 只保留常用
    pacific_dir = os.path.join(tzdata_dir, "Pacific")
    if os.path.exists(pacific_dir):
        keep_zones = {"Auckland", "Fiji"}
        for item in os.listdir(pacific_dir):
            item_path = os.path.join(pacific_dir, item)
            if os.path.isfile(item_path):
                zone_name = item.replace(".msg", "")
                if zone_name not in keep_zones:
                    removed_size += os.path.getsize(item_path)
                    removed_count += 1
                    os.remove(item_path)
    
    # 5. 清理 tcl/msgs - 保留中日韩英消息文件
    for msgs_dir in [
        os.path.join(dist_dir, "tcl", "msgs"),
        os.path.join(dist_dir, "tk", "msgs"),
    ]:
        if os.path.exists(msgs_dir):
            # 保留：简中、繁中、日、韩、英的消息文件
            keep_prefixes = ("zh_cn", "zh_tw", "zh_hk", "ja", "ko", "en")
            for item in os.listdir(msgs_dir):
                item_path = os.path.join(msgs_dir, item)
                if os.path.isfile(item_path):
                    item_lower = item.lower()
                    if not any(item_lower.startswith(p) for p in keep_prefixes):
                        removed_size += os.path.getsize(item_path)
                        removed_count += 1
                        os.remove(item_path)
    
    # 4. 清理 tk/images - 删除不必要的大图片
    tk_images_dir = os.path.join(dist_dir, "tk", "images")
    if os.path.exists(tk_images_dir):
        for item in os.listdir(tk_images_dir):
            item_path = os.path.join(tk_images_dir, item)
            if os.path.isfile(item_path):
                removed_size += os.path.getsize(item_path)
                removed_count += 1
                os.remove(item_path)
        if not os.listdir(tk_images_dir):
            os.rmdir(tk_images_dir)
    
    # 6. 清理 tcl/encoding 目录 - 保留中日韩英必需编码
    encoding_dir = os.path.join(dist_dir, "tcl", "encoding")
    if not os.path.exists(encoding_dir):
        encoding_dir = os.path.join(dist_dir, "encoding")
    if os.path.exists(encoding_dir):
        keep_encodings = {
            # 中文编码
            "cp936.enc", "gb2312.enc", "gbk.enc", "gb18030.enc",
            "big5.enc", "cp950.enc",                                    # 繁中
            # 日韩编码
            "cp932.enc", "shiftjis.enc", "euc-jp.enc",                 # 日
            "cp949.enc", "euc-kr.enc", "ksc5601.enc",                  # 韩
            # 通用编码
            "utf-8.enc", "ascii.enc", "iso8859-1.enc", "cp1252.enc",
            "symbol.enc", "dingbats.enc",                               # 字体符号
        }
        for item in os.listdir(encoding_dir):
            item_path = os.path.join(encoding_dir, item)
            if os.path.isfile(item_path) and item not in keep_encodings:
                removed_size += os.path.getsize(item_path)
                removed_count += 1
                os.remove(item_path)
        if os.path.exists(encoding_dir) and not os.listdir(encoding_dir):
            try:
                os.rmdir(encoding_dir)
            except OSError:
                pass
    
    # 7. 清理 tcl 脚本 - 删除开发/调试用脚本（auto.tcl/clock.tcl 是运行时必需的，不能删除）
    tcl_dir = os.path.join(dist_dir, "tcl")
    if os.path.exists(tcl_dir):
        remove_tcl_files = {
            "parray.tcl", "tm.tcl",
            "safe.tcl", "safetk.tcl",
            "tcltest-2.5.3.tm", "tcltest.tcl",
            "pkgIndex.tcl", "package.tcl",
            "history.tcl", "word.tcl",
            "obsolete.tcl", "unsupported.tcl",
        }
        for root, _, files in os.walk(tcl_dir, onerror=lambda e: None):
            for f in files:
                if f in remove_tcl_files:
                    fpath = os.path.join(root, f)
                    if os.path.exists(fpath):
                        removed_size += os.path.getsize(fpath)
                        removed_count += 1
                        os.remove(fpath)
    
    # 8. 清理无扩展名的文件（Nuitka 生成的编译缓存）
    for item in os.listdir(dist_dir):
        item_path = os.path.join(dist_dir, item)
        if os.path.isfile(item_path) and not os.path.splitext(item)[1]:
            if os.path.getsize(item_path) < 100:
                continue
            removed_size += os.path.getsize(item_path)
            removed_count += 1
            os.remove(item_path)
    
    # 9. 删除空目录
    for root, dirs, _ in os.walk(dist_dir, topdown=False, onerror=lambda e: None):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except OSError:
                pass
    
    removed_size_mb = removed_size / (1024 * 1024)
    print(f"   🗑️  删除了 {removed_count} 个文件，节省 {removed_size_mb:.1f} MB")
    
    # UPX 压缩 DLL 和 PYD 文件
    _upx_compress_dist(dist_dir)


def _upx_compress_dist(dist_dir: str) -> None:
    """使用 UPX 压缩 dist 目录中的 DLL 和 PYD 文件
    
    Args:
        dist_dir: dist 目录路径
    """
    # 查找 UPX
    upx_path = None

    # 1. 先用 shutil.which 查找（可能返回 junction point 路径）
    which_result = shutil.which("upx")
    if which_result:
        # 解析 junction point 获取真实路径，避免 WinError 448
        real_path = os.path.realpath(which_result)
        if os.path.isfile(real_path):
            try:
                result = subprocess.run([real_path, "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    upx_path = real_path
                    print(f"   ✅ 找到 UPX: {real_path}")
            except (OSError, subprocess.TimeoutExpired):
                pass

    # 2. 检查常见安装路径（包括 WinGet）
    if not upx_path:
        local_appdata = os.environ.get("LOCALAPPDATA", "")
        common_paths = [
            # WinGet 安装路径（遍历 Packages 子目录查找）
            os.path.join(local_appdata, "Microsoft", "WinGet", "Packages"),
            # 传统安装路径
            os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "UPX", "upx.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "UPX", "upx.exe"),
            os.path.join(local_appdata, "Programs", "UPX", "upx.exe"),
        ]
        for p in common_paths:
            if not os.path.exists(p):
                continue
            # 如果是目录（如 WinGet Packages），遍历查找 upx.exe
            if os.path.isdir(p) and "Packages" in p:
                for root, _, files in os.walk(p, onerror=lambda e: None):
                    for f in files:
                        if f.lower() == "upx.exe":
                            candidate = os.path.realpath(os.path.join(root, f))
                            try:
                                result = subprocess.run([candidate, "--version"], capture_output=True, text=True, timeout=5)
                                if result.returncode == 0:
                                    upx_path = candidate
                                    print(f"   ✅ 找到 UPX: {candidate}")
                                    break
                            except (OSError, subprocess.TimeoutExpired):
                                continue
                    if upx_path:
                        break
            elif os.path.isfile(p):
                real_p = os.path.realpath(p)
                try:
                    result = subprocess.run([real_p, "--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        upx_path = real_p
                        print(f"   ✅ 找到 UPX: {real_p}")
                        break
                except (OSError, subprocess.TimeoutExpired):
                    continue
    
    if not upx_path:
        print("   ℹ️  UPX 未安装，跳过 DLL/PYD 压缩")
        print("      安装 UPX 可进一步减小 50-70% 体积: https://upx.github.io/")
        return
    
    print("   🗜️  使用 UPX 压缩 DLL/PYD 文件...")
    
    # 收集目标文件
    targets = []
    target_exts = (".dll", ".pyd")
    for root, _, files in os.walk(dist_dir, onerror=lambda e: None):
        for f in files:
            if f.lower().endswith(target_exts):
                targets.append(os.path.realpath(os.path.join(root, f)))
    
    if not targets:
        print("   ℹ️  未找到 DLL/PYD 文件，跳过压缩")
        return
    
    before_size = sum(os.path.getsize(t) for t in targets if os.path.exists(t))
    compressed_count = 0
    
    # 压缩（排除无法压缩或不建议压缩的文件）
    import re
    # python3XX.dll: 压缩后可能导致启动问题
    # vcruntime*.dll / msvcp*.dll: MSVC 运行时，UPX 无法压缩
    exclude_pattern = re.compile(
        r"^(python3\d*|vcruntime\d+(_\d+)?|msvcp\d+(_\d+)?)\.dll$",
        re.IGNORECASE
    )
    for target in targets:
        if exclude_pattern.match(os.path.basename(target)):
            continue
        try:
            result = subprocess.run(
                [upx_path, "--best", target],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                compressed_count += 1
            elif "already packed" in result.stderr.lower():
                pass  # 已压缩过，跳过
            else:
                print(f"      ⚠️  压缩失败: {os.path.basename(target)}")
        except (OSError, subprocess.TimeoutExpired):
            pass
    
    after_size = sum(os.path.getsize(t) for t in targets if os.path.exists(t))
    saved_mb = (before_size - after_size) / (1024 * 1024)
    ratio = (1 - after_size / before_size) * 100 if before_size > 0 else 0
    print(f"   ✅ UPX 压缩完成: {compressed_count} 个文件，节省 {saved_mb:.1f} MB (压缩率 {ratio:.0f}%)")


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
        datas = [["translations.json", "."], ["Picture", "Picture"], ["SubnetPlanner_config.json", "."]]
    
    excludes_str = ",\n                 ".join(f"'{module}'" for module in excludes)
    datas_str = ",\n             ".join(f"('{data[0]}', '{data[1]}')" for data in datas)
    
    exe_name = output_filename.rsplit('.', 1)[0]
    
    return f'''# -*- mode: python ; coding: utf-8 -*-

VERSION_STRING = '{version}'

block_cipher = None

a = Analysis(['windows_app.py'],
             pathex=[r'{os.getcwd()}'],
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
        icon='icon.ico',
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
    
    max_retries = 3
    retry_delay = 5
    
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
                _ = subprocess.run(sign_cmd, check=True, cwd=os.getcwd(), capture_output=True, text=True)
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
    
    # 禁用 clcache 避免预处理器错误
    os.environ['CLCACHE_DISABLE'] = '1'
    print("📝 已禁用 clcache 缓存")
    
    try:
        # Nuitka 2.x 使用 --mode 参数：standalone=目录模式，onefile=单文件模式
        if onefile:
            mode_arg = "--mode=onefile"
        else:
            mode_arg = "--mode=standalone"
        
        cmd: list[str] = [
            sys.executable, "-m", "nuitka",
            mode_arg,
            "--follow-imports",  # 自动包含所有导入的模块
            "--include-module=splash_screen",
            "--include-module=font_config",
            "--include-module=style_manager",
            "--include-module=chart_utils",
            "--include-module=visualization",
            "--include-module=tkcalendar",  # 显式包含日历组件（通过try-except导入）
            "--windows-icon-from-ico=icon.ico",
            "--include-data-file=translations.json=translations.json",
            "--include-data-file=SubnetPlanner_config.json=SubnetPlanner_config.json",
            "--include-data-dir=Picture=Picture",
            "--enable-plugin=tk-inter",
            "--windows-console-mode=attach",
            "--assume-yes-for-downloads",
            "--enable-plugin=anti-bloat",
            # 排除不必要的包，减小体积
            "--nofollow-import-to=babel",
            "--nofollow-import-to=tzdata",
            "--nofollow-import-to=setuptools",
            "--nofollow-import-to=pip",
            "--nofollow-import-to=charset_normalizer",
            "--nofollow-import-to=urllib3",
            "--nofollow-import-to=certifi",
            "--nofollow-import-to=requests",
            # 排除大型科学计算库（未使用但可能被间接依赖）
            "--nofollow-import-to=numpy",
            "--nofollow-import-to=scipy",
            "--nofollow-import-to=matplotlib",
            "--nofollow-import-to=pandas",
            "--nofollow-import-to=sklearn",
            f"--product-name={version_resource['product_name']}",
            f"--product-version={version}",
            f"--file-version={version}",
            f"--company-name={version_resource['company_name']}",
            f"--copyright={version_resource['copyright']}",
            f"--file-description={version_resource['file_description']}",
            f"--output-filename={output_filename if onefile else 'SubnetPlanner.exe'}",
            "windows_app.py"
        ]
        
        cmd = [option for option in cmd if option]
        
        print(f"📝 编译命令: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=os.getcwd())
        print("✅ Nuitka 编译成功!")
        
        if onefile:
            # 单文件模式：查找 exe
            output_file = os.path.join(os.getcwd(), output_filename)
            if not os.path.exists(output_file):
                for item in os.listdir(os.getcwd()):
                    if item.endswith('.exe') and 'SubnetPlanner' in item:
                        output_file = os.path.join(os.getcwd(), item)
                        break
            return process_output_file(output_file, output_filename, output_dir, pfx_password, signtool_path)
        else:
            # standalone 模式：Nuitka 生成 windows_app.dist 目录
            dist_dir = os.path.join(os.getcwd(), "windows_app.dist")
            if not os.path.exists(dist_dir):
                # 尝试查找其他 .dist 目录
                for item in os.listdir(os.getcwd()):
                    if item.endswith('.dist'):
                        dist_dir = os.path.join(os.getcwd(), item)
                        break
            
            if not os.path.exists(dist_dir):
                print("❌ 未找到编译输出目录 (.dist)")
                return False
            
            # 先清理源目录中的不必要文件（在复制前清理更高效）
            try:
                _clean_dist_directory(dist_dir)
            except OSError as e:
                print(f"   ⚠️  清理过程中遇到文件系统问题（已跳过）: {e}")
            
            # 重命名目录中的 exe（目录模式不带版本号，方便升级替换）
            # Nuitka 通过 --output-filename 可能已直接命名为 SubnetPlanner.exe
            standalone_exe_name = "SubnetPlanner.exe"
            old_exe = os.path.join(dist_dir, "windows_app.exe")
            if os.path.exists(old_exe):
                os.rename(old_exe, os.path.join(dist_dir, standalone_exe_name))
            
            # 对 exe 进行签名（在源目录中签名）
            src_exe = os.path.join(dist_dir, standalone_exe_name)
            if os.path.exists(src_exe):
                sign_executable(src_exe, pfx_password, signtool_path)
            
            # 重命名目录为目标名称（目录模式不带版本号，方便升级替换）
            dest_dir = os.path.join(output_dir, "SubnetPlanner_Nuitka.dist")
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir, ignore_errors=True)
            
            # 直接重命名目录（比复制快且避免挂载点问题）
            try:
                os.rename(dist_dir, dest_dir)
            except OSError:
                # 如果跨盘符无法重命名，则复制
                try:
                    shutil.copytree(dist_dir, dest_dir, ignore_dangling_symlinks=True, dirs_exist_ok=True)
                except TypeError:
                    # Python 3.12 以下不支持 dirs_exist_ok
                    shutil.copytree(dist_dir, dest_dir)
            
            # 计算总大小
            total_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(dest_dir, onerror=lambda e: None) for f in fn)
            size_mb = total_size / (1024 * 1024)
            print(f"📦 输出目录: {dest_dir}")
            print(f"📏 目录总大小: {size_mb:.2f} MB")
            return True
        
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
        
        # 目录模式下，output_file 是目录
        if onefile:
            dest_filename = f"{output_filename.rsplit('.', 1)[0]}_PyInstaller.exe"
            return process_output_file(output_file, output_filename, output_dir, pfx_password, signtool_path, dest_filename)
        else:
            # 目录模式：复制整个目录
            import shutil
            dest_dir = os.path.join(output_dir, f"{output_filename.rsplit('.', 1)[0]}_PyInstaller.dist")
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(output_file, dest_dir)
            
            # 对目录中的 exe 进行签名
            exe_path = os.path.join(dest_dir, output_filename)
            if os.path.exists(exe_path):
                sign_executable(exe_path, pfx_password, signtool_path)
            
            # 计算总大小
            total_size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fn in os.walk(dest_dir, onerror=lambda e: None) for f in fn)
            size_mb = total_size / (1024 * 1024)
            print(f"📦 输出目录: {dest_dir}")
            print(f"📏 目录总大小: {size_mb:.2f} MB")
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
                       default="nuitka", help="编译方式（默认：nuitka，目录模式）")
    _ = parser.add_argument("--output", "-o", default=".", help="输出目录")
    _ = parser.add_argument("--clean", action="store_true", help="清理构建文件")
    _ = parser.add_argument("--install-deps", action="store_true", help="仅安装依赖")
    _ = parser.add_argument("--pfx-password", "-p", help="PFX证书密码，不指定则交互式输入")
    _ = parser.add_argument("--signtool-path", "-s", help="signtool.exe工具路径，不指定则自动检测")
    _ = parser.add_argument("--onefile", action="store_true", default=False, help="使用单文件编译模式（默认：否，使用Nuitka目录模式）")
    _ = parser.add_argument("--no-onefile", action="store_false", dest="onefile", help="不使用单文件编译模式")
    args = parser.parse_args()
    
    compile_type_str = cast(str, args.type)
    compile_type = CompileType(compile_type_str)
    
    args.type = compile_type
    
    args = cast(Args, cast(object, args))
    
    check_python_version()
    
    if args.clean:
        clean_build_files()
        sys.exit(0)
    
    if args.install_deps:
        check_and_install_dependencies(args.type)
        sys.exit(0)
    
    check_and_install_dependencies(args.type)
    
    if args.output != ".":
        os.makedirs(args.output, exist_ok=True)
    
    success = True
    
    # 优先使用 Nuitka（真正的二进制编译）
    if args.type == CompileType.NUITKA or args.type == CompileType.BOTH:
        success = compile_with_nuitka(args.output, args.pfx_password, args.signtool_path, args.onefile)
    
    # 如果需要才使用 PyInstaller
    if args.type == CompileType.PYINSTALLER:
        success = compile_with_pyinstaller(args.output, args.pfx_password, args.signtool_path, args.onefile)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 编译成功! 🎉")
        sys.exit(0)
    else:
        print("💥 编译失败! 💥")
        sys.exit(1)



if __name__ == "__main__":
    main()
