#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复PDF导出功能的脚本
用于修复windows_app.py中PDF导出时缺少reportlab模块的问题
"""

import os
import re

# 读取原始文件
file_path = "windows_app.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 定位PDF导出分支的开始位置
pdf_start_pattern = r"elif file_ext == \".pdf\":"
pdf_start_match = re.search(pdf_start_pattern, content)
if not pdf_start_match:
    print("未找到PDF导出分支")
    exit(1)

pdf_start_pos = pdf_start_match.start()

# 定位PDF导出分支的结束位置（即下一个elif或else分支的开始）
pdf_end_pattern = r"(?<=\n)\s*(elif|else)\s+"
pdf_end_match = re.search(pdf_end_pattern, content[pdf_start_pos:])
if not pdf_end_match:
    print("未找到PDF导出分支的结束位置")
    exit(1)

pdf_end_pos = pdf_start_pos + pdf_end_match.start()

# 提取原始PDF导出代码
original_pdf_code = content[pdf_start_pos:pdf_end_pos]

# 构造修复后的PDF导出代码
fixed_pdf_code = original_pdf_code.replace(
    "elif file_ext == \".pdf\":
                # PDF格式导出",
    "elif file_ext == \".pdf\":
                # PDF格式导出
                try:
                    from reportlab.lib.pagesizes import A4, landscape
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.platypus import (
                        Table,
                        TableStyle,
                        Paragraph,
                        Spacer,
                    )
                    from reportlab.lib import colors
                    from reportlab.pdfbase import pdfmetrics
                    from reportlab.lib.units import cm
                    from reportlab.lib.enums import TA_LEFT, TA_CENTER
                    import time
                    import subprocess
                    import sys
                    import traceback"
)

# 添加异常处理
fixed_pdf_code += "\n                except ImportError as e:\n                    print(f\"PDF导出失败: {type(e).__name__}: {e}\")\n                    # 捕获reportlab导入错误，提供友好的错误信息\n                    error_msg = f\"PDF导出失败: 缺少reportlab模块\\n\\n\"\\\n                                f\"当前Python解释器: {sys.executable}\\n\\n\"\\\n                                f\"解决方案:\\n\"\\\n                                f\"1. 打开命令行终端\\n\"\\\n                                f\"2. 执行以下命令安装reportlab:\\n\"\\\n                                f\"   {sys.executable} -m pip install reportlab\\n\"\\\n                                f\"3. 安装完成后重新运行程序\\n\\n\"\\\n                                f\"或者使用其他格式导出数据，如CSV、Excel等。\"\n                    self.show_error(\"PDF导出失败\", error_msg)\n                    return\n                except Exception as e:\n                    print(f\"PDF导出失败: {type(e).__name__}: {e}\")\n                    import traceback\n                    traceback.print_exc()\n                    # 其他PDF导出错误\n                    self.show_error(\"PDF导出失败\", f\"PDF导出失败: {str(e)}\")\n                    return"

# 替换原始内容
new_content = content[:pdf_start_pos] + fixed_pdf_code + content[pdf_end_pos:]

# 保存修复后的文件
with open(file_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("PDF导出功能修复完成！")
print("已添加reportlab模块缺失的错误处理")
print("现在程序在缺少reportlab模块时会显示友好的错误信息和解决方案")