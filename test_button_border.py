import tkinter as tk
from tkinter import ttk

# 创建临时root窗口
root = tk.Tk()
root.withdraw()  # 隐藏窗口

# 获取所有可用主题
style = ttk.Style()
themes = style.theme_names()

print("TTK Button Border Analysis")
print("=" * 50)

# 测试所有主题
for theme in themes:
    print(f"\nTheme: {theme}")
    print("-" * 30)
    
    # 切换到当前主题
    style.theme_use(theme)
    
    # 获取按钮布局
    layout = style.layout("TButton")
    print(f"Layout: {layout}")
    
    # 查看按钮元素配置
    print("Elements Configuration:")
    for element in layout:
        elem_name = element[0]
        elem_details = element[1]
        print(f"  {elem_name}:")
        
        # 获取元素配置
        if "children" in elem_details:
            print(f"    Children: {elem_details['children']}")
        if "sticky" in elem_details:
            print(f"    Sticky: {elem_details['sticky']}")
    
    # 查看元素的具体配置
    print("\nElement Styles:")
    for element in layout:
        elem_name = element[0]
        if elem_name in ["Button.border", "Button.focus", "Button.padding", "Button.label"]:
            elem_style = style.element_options(elem_name)
            print(f"  {elem_name} options: {elem_style}")
            
            # 获取边框宽度配置
            try:
                borderwidth = style.lookup(elem_name, "borderwidth")
                print(f"    borderwidth: {borderwidth}")
            except:
                pass
            
            try:
                relief = style.lookup(elem_name, "relief")
                print(f"    relief: {relief}")
            except:
                pass
            
            try:
                background = style.lookup(elem_name, "background")
                print(f"    background: {background}")
            except:
                pass

print("\n" + "=" * 50)
print("Analysis Complete")

# 销毁临时窗口
root.destroy()