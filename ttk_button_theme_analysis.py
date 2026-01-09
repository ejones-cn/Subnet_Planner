import tkinter as tk
from tkinter import ttk

# 创建临时root窗口
root = tk.Tk()
root.withdraw()  # 隐藏窗口

# 获取所有可用主题
style = ttk.Style()
themes = style.theme_names()

print("TTK Button Theme Analysis")
print("=" * 60)

# 测试所有主题
for theme in themes:
    print(f"\n{'='*20} Theme: {theme} {'='*20}")
    
    # 切换到当前主题
    style.theme_use(theme)
    
    # 获取按钮布局
    try:
        layout = style.layout("TButton")
        print(f"Layout: {layout}")
        
        # 分析布局元素
        print("\nLayout Elements:")
        for i, element in enumerate(layout):
            elem_name = element[0]
            elem_details = element[1]
            print(f"  Element {i+1}: {elem_name}")
            print(f"    Details: {elem_details}")
            
            # 检查是否有子元素
            if "children" in elem_details:
                children = elem_details["children"]
                print(f"    Children count: {len(children)}")
                for child in children:
                    print(f"      Child: {child[0]}")
        
        # 获取按钮的所有配置选项
        print("\nButton Configuration Options:")
        config_opts = style.configure("TButton")
        if isinstance(config_opts, dict):
            for key, value in config_opts.items():
                print(f"  {key}: {value}")
        else:
            print(f"  {config_opts}")
        
        # 获取元素的具体配置
        print("\nElement-Specific Configuration:")
        # 遍历布局中的所有元素
        processed_elements = set()
        
        def process_element(element):
            elem_name = element[0]
            if elem_name in processed_elements:
                return
            processed_elements.add(elem_name)
            
            print(f"\n  {elem_name}:")
            try:
                # 获取元素选项
                elem_options = style.element_options(elem_name)
                print(f"    Options: {elem_options}")
                
                # 尝试获取元素的具体配置
                print("    Configuration:")
                for opt in elem_options:
                    try:
                        value = style.lookup(elem_name, opt)
                        print(f"      {opt}: {value}")
                    except Exception as e:
                        print(f"      {opt}: Error - {e}")
            except Exception as e:
                print(f"    Error getting options: {e}")
            
            # 处理子元素
            elem_details = element[1]
            if "children" in elem_details:
                for child in elem_details["children"]:
                    process_element(child)
        
        # 处理根元素
        for element in layout:
            process_element(element)
        
        # 测试自定义样式
        print("\n" + "-"*40)
        print("Testing Custom Button Style:")
        # 创建自定义样式
        custom_style = "Custom.TButton"
        style.configure(
            custom_style,
            background="red",
            foreground="white",
            borderwidth=2,
            relief="raised"
        )
        
        # 获取自定义样式的配置
        custom_config = style.configure(custom_style)
        print(f"Custom style config: {custom_config}")
        
        # 测试元素配置
        print("\nCustom Element Config:")
        for element in layout:
            elem_name = element[0]
            full_elem_name = f"Custom.TButton.{elem_name.split('.')[-1]}"
            try:
                # 尝试配置元素
                style.configure(full_elem_name, background="blue")
                print(f"  Configured {full_elem_name}")
            except Exception as e:
                print(f"  Error configuring {full_elem_name}: {e}")
                
    except Exception as e:
        print(f"Error analyzing theme {theme}: {e}")

print("\n" + "=" * 60)
print("Analysis Complete")

# 销毁临时窗口
root.destroy()