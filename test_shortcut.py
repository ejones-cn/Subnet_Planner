import tkinter as tk

def on_shortcut(event):
    print("Ctrl+Shift+I 快捷键被触发!")
    label.config(text="快捷键已触发!")

root = tk.Tk()
root.title("快捷键测试")
root.geometry("300x200")

label = tk.Label(root, text="按 Ctrl+Shift+I 测试快捷键", font=("Arial", 12))
label.pack(pady=50)

# 测试多种绑定方式
root.bind_all('<Control-Shift-I>', on_shortcut)
root.bind_all('<Control-Shift-i>', on_shortcut)
root.bind_all('<Control-Shift-KeyPress-I>', on_shortcut)
root.bind_all('<Control-Shift-KeyPress-i>', on_shortcut)

print("应用已启动，请按 Ctrl+Shift+I 测试")
root.mainloop()