#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用于修复_export_data函数的脚本，删除旧的重复代码
"""

import os

# 读取文件内容
with open('windows_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到_export_data函数中旧数据准备代码的位置
start_line = None
end_line = None
in_old_code = False

for i, line in enumerate(lines):
    # 找到开始位置：第5508行之后的代码
    if 'main_data, main_headers, remaining_data, remaining_headers = self._prepare_export_data(data_source)' in line:
        start_line = i + 1
        in_old_code = True
        continue
    
    # 找到结束位置：# 根据文件扩展名选择导出格式
    if in_old_code and '# 根据文件扩展名选择导出格式' in line:
        end_line = i
        break

# 如果找到了开始和结束位置，删除旧代码
if start_line is not None and end_line is not None:
    # 保存原始代码行数
    original_lines = len(lines)
    
    # 删除旧代码
    del lines[start_line:end_line]
    
    # 将修改后的内容写回文件
    with open('windows_app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"已删除旧数据准备代码，从行 {start_line + 1} 到行 {end_line + 1}")
    print(f"删除了 {end_line - start_line} 行代码")
    print(f"文件现在有 {len(lines)} 行")
else:
    print("未找到旧数据准备代码")

# 现在替换JSON、TXT、CSV、Excel导出代码
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换JSON导出代码
json_old = '''            if file_ext == ".json":
                # JSON格式导出

                if data_source["main_name"] == "切分网段信息":
                    # 子网切分结果特殊处理
                    export_data = {"split_info": dict(main_data), "remaining_subnets": remaining_data}
                else:
                    # 子网规划结果格式
                    export_data = {
                        f"{data_source['main_name']}": [dict(zip(main_headers, item)) for item in main_data],
                        "remaining_subnets": remaining_data,
                    }

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)'''

json_new = '''            if file_ext == ".json":
                # JSON格式导出
                self._export_to_json(file_path, data_source, main_data, main_headers, remaining_data)'''

content = content.replace(json_old, json_new)

# 替换TXT导出代码
# 注意：这里只替换开始部分，因为TXT导出代码很长
# 我们将在后续步骤中继续替换

txt_old = '''            elif file_ext == ".txt":
                # 文本格式导出
                with open(file_path, "w", encoding="utf-8") as f:
                    # 写入主数据
                    f.write(f"{data_source['main_name']}\n")
                    f.write("=" * 80 + "\n")

                    # 如果是键值对格式（如切分网段信息）
                    if len(main_headers) == 2 and main_headers[0] == "项目" and main_headers[1] == "值":
                        for values in main_data:
                            f.write(f"{values[0]:<20}: {values[1]}\n")
                    else:
                        # 写入列标题
                        for header in main_headers:
                            f.write(f"{header:<15}")
                        f.write("\n")
                        f.write("-" * 80 + "\n")

                        # 写入数据
                        for values in main_data:
                            for value in values:
                                f.write(f"{str(value):<15}")
                            f.write("\n")

                    # 写入剩余数据
                    f.write(f"\n\n{data_source['remaining_name']}\n")
                    f.write("=" * 80 + "\n")

                    # 写入剩余数据列标题
                    for header in remaining_headers:
                        f.write(f"{header:<15}")
                    f.write("\n")
                    f.write("-" * 80 + "\n")

                    # 写入剩余数据
                    for item in remaining_tree.get_children():
                        values = remaining_tree.item(item, "values")
                        for value in values:
                            f.write(f"{str(value):<15}")
                        f.write("\n")'''

txt_new = '''            elif file_ext == ".txt":
                # 文本格式导出
                self._export_to_txt(file_path, data_source, main_data, main_headers, data_source["remaining_tree"], remaining_headers)'''

content = content.replace(txt_old, txt_new)

# 替换CSV和Excel导出代码
csv_xlsx_old = '''            elif file_ext == ".pdf":'''

csv_xlsx_new = '''            elif file_ext == ".csv":
                # CSV格式导出
                self._export_to_csv(file_path, main_data, main_headers, data_source["remaining_tree"])

            elif file_ext == ".xlsx":
                # Excel格式导出
                self._export_to_excel(file_path, main_data, main_headers, data_source["remaining_tree"], remaining_headers)

            elif file_ext == ".pdf":'''

content = content.replace(csv_xlsx_old, csv_xlsx_new)

# 将修改后的内容写回文件
with open('windows_app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已替换JSON、TXT、CSV、Excel导出代码")
