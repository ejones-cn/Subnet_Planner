import tkinter as tk
from tkinter import ttk

# 创建主窗口
root = tk.Tk()
root.title("简洁表格线示例")
root.geometry("500x300")

# 1. 关键步骤：切换到clam主题，它对网格线支持更好
style = ttk.Style()
style.theme_use("vista")

# 2. 配置Treeview样式
style.configure("Treeview",
                rowheight=25,
                fieldbackground="white",
                background="white",
                foreground="black",
                bordercolor="#d0d0d0",
                borderwidth=1)

# 3. 配置表头样式
style.configure("Treeview.Heading",
                background="#e0e0e0",
                foreground="black",
                relief="ridge",
                borderwidth=2,
                font=("Arial", 10, "bold"))

# 4. 配置Treeview布局，添加网格线
style.layout("Treeview", [
    ("Treeview.treearea", {
        "sticky": "nswe",
        "children": [
            ("Treeview.body", {
                "sticky": "nswe",
                "children": [
                    ("Treeview.row", {
                        "sticky": "nswe",
                        "children": [
                            ("Treeview.cell", {
                                "sticky": "nswe",
                                "border": "1"
                            })
                        ]
                    })
                ]
            })
        ]
    })
])

# 5. 创建Treeview组件
tree = ttk.Treeview(root, show="headings")

# 6. 定义列
tree["columns"] = ("id", "name", "value")

# 7. 配置每一列
for col in tree["columns"]:
    tree.column(col, width=150, anchor="center", stretch=True)
    tree.heading(col, text=col.capitalize(), anchor="center")

# 8. 添加数据
data = [
    (1, "Alice", "Engineer"),
    (2, "Bob", "Designer"),
    (3, "Charlie", "Developer"),
    (4, "Diana", "Manager")
]

for item in data:
    tree.insert("", "end", values=item)

# 9. 显示Treeview
tree.pack(padx=10, pady=10, expand=True, fill="both")

# 运行主循环
root.mainloop()