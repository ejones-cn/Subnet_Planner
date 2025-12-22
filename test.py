import tkinter as tk
from tkinter import ttk

# 创建主窗口
root = tk.Tk()
root.title("Treeview Example")

# 创建 Treeview 控件
tree = ttk.Treeview(root)
tree.pack(padx=10, pady=10, fill='both', expand=True)

# 配置 Treeview 样式以显示格线
style = ttk.Style()
style.configure('Treeview', rowheight=25)  # 设置行高
style.configure('Treeview.Row', background='white')  # 设置行背景色
style.map('Treeview', background=[('selected', 'lightblue')])  # 设置选中行的背景色

# 添加列
tree['columns'] = ('column1', 'column2')
tree.heading('column1', text='Column 1')
tree.heading('column2', text='Column 2')

# 插入数据
tree.insert('', 'end', values=('Item 1', 'Data 1'))
tree.insert('', 'end', values=('Item 2', 'Data 2'))

# 显示格线（在某些主题中可能不直接支持）
try:
    style.layout('Treeview', [('Treeview.treearea.treeitem', {'sticky': 'nswe'})])  # 这通常不直接影响格线显示
    style.configure('Treeview', fieldbackground='lightgrey')  # 设置字段背景色来模拟格线效果
except tk.TclError:
    print("Error: Unsupported style operation.")

# 主事件循环
root.mainloop()
