# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['windows_app.py'],
    pathex=[],
    binaries=[],
    datas=[('translations.json', '.'), ('Subnet_Planner.ico', '.'), ('icon.ico', '.')],
    hiddenimports=['tkinter', 'reportlab', 'charset_normalizer', 'openpyxl', 'urllib', 'urllib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['winreg', '_winreg', 'win32service', 'win32timezone', 'xmlrpc', 'sqlite3', 'ssl', 'cryptography', 'hmac', 'winsound', 'win32api', 'win32con', 'win32gui', 'win32process', 'win32com', 'win32com.client', 'win32com.server', 'win32event', 'win32evtlog', 'win32evtlogutil', 'win32file', 'win32pipe', 'win32security', 'win32trace', 'win32wnet', 'asyncio', 'concurrent', 'multiprocessing', 'queue'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SubnetPlannerV2.5.5',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Subnet_Planner.ico'],
)
