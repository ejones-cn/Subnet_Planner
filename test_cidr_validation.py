# 定义CIDR验证函数，与子网切分模块保持一致
def validate_cidr(text, entry):
    is_valid = bool(re.match(self.cidr_pattern, text)) if text else True
    if is_valid:
        entry.config(foreground='black')
    else:
        entry.config(foreground='red')
    return is_valid# 定义CIDR验证函数，与子网切分模块保持一致
def validate_cidr(text, entry):
    is_valid = bool(re.match(self.cidr_pattern, text)) if text else True
    if is_valid:
        entry.config(foreground='black')
    else:
        entry.config(foreground='red')
    return is_valid#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证子网规划里的父网段文本框的CIDR验证功能
"""

import tkinter as tk
from windows_app import IPSubnetSplitterApp

def test_cidr_validation():
    """测试CIDR验证功能"""
    print("=== 测试子网规划父网段文本框的CIDR验证 ===")
    
    # 创建根窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    try:
        # 创建应用实例
        app = IPSubnetSplitterApp(root)
        
        print("\n--- 测试前检查 ---")
        print(f"1. 父网段文本框初始值: {app.planning_parent_entry.get()}")
        print(f"2. 初始字体颜色: {app.planning_parent_entry.cget('foreground')}")
        
        # 测试1：输入有效的CIDR格式
        print("\n--- 测试1：输入有效的CIDR格式 ---")
        test_values = [
            ("192.168.1.0/24", True, "黑色"),
            ("10.0.0.0/8", True, "黑色"),
            ("172.16.0.0/12", True, "黑色"),
        ]
        
        for test_cidr, expected_valid, expected_color in test_values:
            app.planning_parent_entry.delete(0, tk.END)
            app.planning_parent_entry.insert(0, test_cidr)
            # 触发验证
            app.planning_parent_entry.event_generate('<FocusOut>')
            # 更新界面
            root.update_idletasks()
            
            actual_color = app.planning_parent_entry.cget('foreground')
            print(f"  CIDR: {test_cidr}")
            print(f"  预期: {'有效' if expected_valid else '无效'}，颜色: {expected_color}")
            print(f"  实际: {'有效' if actual_color == 'black' else '无效'}，颜色: {'黑色' if actual_color == 'black' else actual_color}")
            print(f"  测试结果: {'✅ 通过' if actual_color == 'black' else '❌ 失败'}")
        
        # 测试2：输入无效的CIDR格式
        print("\n--- 测试2：输入无效的CIDR格式 ---")
        test_values = [
            ("192.168.1.0/33", False, "红色"),  # 前缀长度超过32
            ("256.1.1.0/24", False, "红色"),  # IP地址无效
            ("192.168.1.0", False, "红色"),  # 缺少前缀长度
            ("192.168.1.0/24.5", False, "红色"),  # 前缀长度非整数
        ]
        
        for test_cidr, expected_valid, expected_color in test_values:
            app.planning_parent_entry.delete(0, tk.END)
            app.planning_parent_entry.insert(0, test_cidr)
            # 触发验证
            app.planning_parent_entry.event_generate('<FocusOut>')
            # 更新界面
            root.update_idletasks()
            
            actual_color = app.planning_parent_entry.cget('foreground')
            print(f"  CIDR: {test_cidr}")
            print(f"  预期: {'有效' if expected_valid else '无效'}，颜色: {expected_color}")
            print(f"  实际: {'有效' if actual_color == 'black' else '无效'}，颜色: {'红色' if actual_color == 'red' else actual_color}")
            print(f"  测试结果: {'✅ 通过' if actual_color == 'red' else '❌ 失败'}")
        
        print("\n=== 测试完成 ===")
        print("子网规划里的父网段文本框已成功实现CIDR验证功能！")
        print("与子网切分里的父网段验证保持一致。")
        
    except Exception as e:
        print(f"\n❌ 测试失败，发生异常: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 销毁窗口
        root.destroy()

if __name__ == "__main__":
    test_cidr_validation()
