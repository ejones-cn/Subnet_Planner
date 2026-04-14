#!/usr/bin/env python3
import sys
import os

print("=== 路径测试 ===")
print(f"sys.executable: {sys.executable}")
print(f"sys.argv[0]: {sys.argv[0]}")
print(f"hasattr(sys, '_MEIPASS'): {hasattr(sys, '_MEIPASS')}")
if hasattr(sys, '_MEIPASS'):
    print(f"sys._MEIPASS: {sys._MEIPASS}")

# 测试获取EXE路径的方法
if hasattr(sys, '_MEIPASS'):
    # 方法1: 使用 sys.argv[0]
    exe_path = None
    if sys.argv and sys.argv[0]:
        exe_path = sys.argv[0]
        if not os.path.isabs(exe_path):
            exe_path = os.path.abspath(exe_path)
    print(f"\n方法1 (sys.argv[0]): {exe_path}")
    
    # 方法2: 使用 ctypes
    if exe_path is None or not os.path.exists(exe_path):
        try:
            import ctypes
            from ctypes import wintypes
            GetModuleFileNameW = ctypes.windll.kernel32.GetModuleFileNameW
            GetModuleFileNameW.argtypes = [wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD]
            GetModuleFileNameW.restype = wintypes.DWORD
            
            buffer = ctypes.create_unicode_buffer(260)
            if GetModuleFileNameW(None, buffer, 260) > 0:
                exe_path = buffer.value
        except Exception as e:
            print(f"ctypes error: {e}")
    print(f"方法2 (ctypes): {exe_path}")
    
    # 方法3: 使用 sys.executable
    if exe_path is None or not os.path.exists(exe_path):
        exe_path = sys.executable
    print(f"方法3 (sys.executable): {exe_path}")
    
    app_dir = os.path.dirname(exe_path)
    print(f"\n应用目录: {app_dir}")
    print(f"数据库路径: {os.path.join(app_dir, 'ipam_data.db')}")

input("\n按 Enter 键退出...")
