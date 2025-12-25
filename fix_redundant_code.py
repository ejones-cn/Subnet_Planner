# 修复冗余代码的脚本

# 读取文件内容
with open('f:/trae_projects/Netsub tools/windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到TXT导出部分的开始和结束位置
start_pattern = '            elif file_ext == ".txt":'
end_pattern = '            elif file_ext == ".csv":'

start_idx = content.find(start_pattern)
if start_idx != -1:
    # 找到TXT导出部分的结束位置
    end_idx = content.find(end_pattern, start_idx + len(start_pattern))
    if end_idx != -1:
        # 构建新的TXT导出部分
        new_txt_section = '''            elif file_ext == ".txt":
                # 文本格式导出
                self._export_to_txt(file_path, data_source, main_data, main_headers, remaining_headers)
'''
        
        # 替换原TXT导出部分
        new_content = content[:start_idx] + new_txt_section + content[end_idx:]
        
        # 写回文件
        with open('f:/trae_projects/Netsub tools/windows_app.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print('替换完成')
    else:
        print('未找到CSV导出部分')
else:
    print('未找到TXT导出部分')
