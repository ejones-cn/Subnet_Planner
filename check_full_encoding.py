#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def check_file_encoding(file_path):
    """检查文件中的中文乱码"""
    print(f"\n=== 完整检查文件: {file_path} ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        print(f"✅ 成功以UTF-8编码打开，共{len(lines)}行")
        
        # 检查每一行是否包含可能的乱码
        # 乱码通常表现为连续的非中文字符（不在\u4e00-\u9fff范围内的非ASCII字符）
        problematic_lines = []
        
        for i, line in enumerate(lines):
            # 跳过空行
            if not line.strip():
                continue
            
            # 检查是否包含非ASCII字符
            non_ascii_chars = [c for c in line if ord(c) > 127]
            if non_ascii_chars:
                # 检查非ASCII字符中是否有不在中文范围内的字符
                problematic_chars = [c for c in non_ascii_chars if not ('\u4e00' <= c <= '\u9fff')]
                
                # 如果有超过3个连续的问题字符，可能是乱码
                if problematic_chars:
                    # 检查是否有连续的问题字符
                    has_consecutive = False
                    consecutive_count = 0
                    for c in line:
                        if c in problematic_chars:
                            consecutive_count += 1
                            if consecutive_count >= 3:
                                has_consecutive = True
                                break
                        else:
                            consecutive_count = 0
                    
                    if has_consecutive:
                        problematic_lines.append((i+1, line))
        
        if problematic_lines:
            print(f"❌ 发现{len(problematic_lines)}行可能包含乱码:")
            for line_num, line in problematic_lines:
                print(f"   第{line_num}行: {line[:100]}...")
        else:
            print("✅ 未发现乱码问题")
            
            # 随机抽查几行中文内容，确认显示正常
            print("\n抽查中文内容示例:")
            chinese_lines = [line for line in lines if any('\u4e00' <= c <= '\u9fff' for c in line)]
            if chinese_lines:
                import random
                sample_lines = random.sample(chinese_lines, min(10, len(chinese_lines)))
                for line in sample_lines[:5]:
                    print(f"   {line[:100]}")
        
        return problematic_lines
        
    except UnicodeDecodeError as e:
        print(f"❌ UTF-8解码失败: {e}")
        return [(0, f"文件编码错误: {e}")]
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return [(0, f"文件读取错误: {e}")]

# 检查windows_app.py文件
if __name__ == "__main__":
    check_file_encoding("windows_app.py")
