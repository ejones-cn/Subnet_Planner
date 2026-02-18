#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 版本资源文件
用于 PyInstaller 打包
"""

from pyinstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)

VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(2, 6, 5),
        prodvers=(2, 6, 5),
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
                        StringStruct('FileVersion', '2.6.5'),
                        StringStruct('InternalName', 'Subnet Planner'),
                        StringStruct('LegalCopyright', 'Copyright © 2025-2026 Subnet Planner Team'),
                        StringStruct('OriginalFilename', 'SubnetPlanner.exe'),
                        StringStruct('ProductName', '子网规划师'),
                        StringStruct('ProductVersion', '2.6.5'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [2052, 1200])])
    ]
)
