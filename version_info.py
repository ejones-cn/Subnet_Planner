#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 版本资源文件
用于 PyInstaller 打包
"""

VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(2, 0, 0, 0),
        prodvers=(2, 0, 0, 0),
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
                        StringStruct('CompanyName', 'Netsub'),
                        StringStruct('FileDescription', '子网规划师 - IP子网计算工具'),
                        StringStruct('FileVersion', '2.0.0.0'),
                        StringStruct('InternalName', 'SubnetPlanner'),
                        StringStruct('LegalCopyright', 'Copyright © 2025 Netsub'),
                        StringStruct('OriginalFilename', '子网规划师.exe'),
                        StringStruct('ProductName', '子网规划师'),
                        StringStruct('ProductVersion', '2.0.0.0'),
                    ]
                )
            ]
        ),
        VarFileInfo([VarStruct('Translation', [2052, 1200])])
    ]
)
