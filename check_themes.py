import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

root = tk.Tk()
style = ThemedStyle(root)

# 打印所有可用主题
print("可用主题列表：")
for theme in style.theme_names():
    print(f"- {theme}")

root.destroy()
