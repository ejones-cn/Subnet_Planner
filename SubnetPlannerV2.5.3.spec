# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['windows_app.py'],
    pathex=[],
    binaries=[],
    datas=[('translations.json', '.'), ('Subnet_Planner.ico', '.')],
    hiddenimports=['tkinter', 'reportlab', 'charset_normalizer', 'openpyxl', 'urllib'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['winreg', '_winreg', 'win32service', 'win32timezone', 'xmlrpc', 'sqlite3'],
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
    name='SubnetPlannerV2.5.3',
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
