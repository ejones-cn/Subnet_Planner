# 获取_setup_scrollbar方法的完整实现
with open('windows_app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'def _setup_scrollbar' in line:
            print(f'Line {i+1}: {line.strip()}')
            # 读取方法的完整内容，直到遇到下一个def或缩进结束
            for j in range(i+1, len(lines)):
                current_line = lines[j]
                print(f'Line {j+1}: {current_line.rstrip()}')
                # 检查是否是下一个方法的开始
                if current_line.strip().startswith('def ') and current_line.startswith('    def '):
                    break
                # 检查是否是方法结束（空行且缩进为4个空格）
                if not current_line.strip() and lines[j-1].rstrip() != ':' and not lines[j-1].strip().endswith('\\'):
                    break
