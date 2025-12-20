import tkinter as tk
from tkinter import ttk
import os

# 手动添加Azure主题的tcl文件路径
azure_theme_path = "Azure-ttk-theme/azure.tcl"

root = tk.Tk()

# 检查主题文件是否存在
if os.path.exists(azure_theme_path):
    # 加载Azure主题
    root.tk.call("source", azure_theme_path)
    
    # 设置主题
    style = ttk.Style()
    style.theme_use("azure")
    
    # 创建测试窗口
    root.title("Azure Theme Test")
    root.geometry("400x300")
    
    # 添加测试组件
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="Azure Theme Test", font=("Arial", 16)).pack(pady=20)
    ttk.Button(frame, text="Button").pack(pady=10)
    ttk.Entry(frame).pack(pady=10)
    
    # 创建Treeview测试
    tree = ttk.Treeview(frame, columns=("column1", "column2"), show="headings")
    tree.heading("column1", text="Column 1")
    tree.heading("column2", text="Column 2")
    tree.insert("", tk.END, values=("Item 1", "Value 1"))
    tree.insert("", tk.END, values=("Item 2", "Value 2"))
    tree.pack(pady=20, fill=tk.BOTH, expand=True)
    
    root.mainloop()
else:
    print(f"Azure主题文件不存在: {azure_theme_path}")
    print("请先从GitHub下载Azure-ttk-theme项目")
    root.destroy()