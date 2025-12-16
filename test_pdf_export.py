import os
import sys
import tempfile
import subprocess

# 添加项目目录到Python路径
sys.path.append("d:/trae_projects/Netsub tools")

from windows_app import IPSubnetSplitterApp
import tkinter as tk
import webbrowser

def test_pdf_export():
    """测试PDF导出功能"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    app = IPSubnetSplitterApp(root)
    
    # 测试子网规划导出功能
    print("测试子网规划导出功能...")
    
    # 创建一个简单的测试数据
    # 直接调用_export_data函数来测试PDF导出
    from tkinter import ttk
    
    # 创建模拟的Treeview数据结构
    planning_result_tree = ttk.Treeview(root, columns=("name", "cidr", "network", "mask", "broadcast", "host_start", "host_end", "host_count", "desc"))
    planning_result_tree.heading("name", text="名称")
    planning_result_tree.heading("cidr", text="CIDR")
    planning_result_tree.heading("network", text="网络地址")
    planning_result_tree.heading("mask", text="子网掩码")
    planning_result_tree.heading("broadcast", text="广播地址")
    planning_result_tree.heading("host_start", text="可用地址开始")
    planning_result_tree.heading("host_end", text="可用地址结束")
    planning_result_tree.heading("host_count", text="可用主机数")
    planning_result_tree.heading("desc", text="描述")
    
    # 添加测试数据
    planning_result_tree.insert('', 'end', values=("子网1", "192.168.1.0/25", "192.168.1.0", "255.255.255.128", "192.168.1.127", "192.168.1.1", "192.168.1.126", "126", "测试子网1"))
    planning_result_tree.insert('', 'end', values=("子网2", "192.168.1.128/26", "192.168.1.128", "255.255.255.192", "192.168.1.191", "192.168.1.129", "192.168.1.190", "62", "测试子网2"))
    
    remaining_result_tree = ttk.Treeview(root, columns=("cidr", "network", "mask", "broadcast", "host_start", "host_end", "host_count"))
    remaining_result_tree.heading("cidr", text="CIDR")
    remaining_result_tree.heading("network", text="网络地址")
    remaining_result_tree.heading("mask", text="子网掩码")
    remaining_result_tree.heading("broadcast", text="广播地址")
    remaining_result_tree.heading("host_start", text="可用地址开始")
    remaining_result_tree.heading("host_end", text="可用地址结束")
    remaining_result_tree.heading("host_count", text="可用主机数")
    
    # 添加测试数据
    remaining_result_tree.insert('', 'end', values=("192.168.1.192/26", "192.168.1.192", "255.255.255.192", "192.168.1.255", "192.168.1.193", "192.168.1.254", "62"))
    
    # 测试PDF导出
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, "test_export.pdf")
    
    # 创建模拟数据源
    data_source = {
        "main_tree": planning_result_tree,
        "main_name": "已分配子网",
        "remaining_tree": remaining_result_tree,
        "remaining_name": "剩余网段",
        "pdf_title": "子网规划结果",
        "main_table_cols": "1:1:1:1:1:1:1:1:1",
        "remaining_table_cols": "1:1:1:1:1:1:1"
    }
    
    # 模拟文件对话框选择
    import tkinter.filedialog
    original_asksaveasfilename = tkinter.filedialog.asksaveasfilename
    
    def mock_asksaveasfilename(**kwargs):
        return temp_file
    
    tkinter.filedialog.asksaveasfilename = mock_asksaveasfilename
    
    try:
        # 执行导出
        # 使用反射调用私有方法_export_data
        result = app._export_data(data_source, "子网规划结果", "PDF导出成功", "PDF导出失败")
        
        if result:
            print(f"PDF导出成功: {result}")
            # 打开导出的文件进行验证
            webbrowser.open(result)
            return True
        else:
            print("PDF导出失败")
            return False
    except Exception as e:
        print(f"PDF导出错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始函数
        tkinter.filedialog.asksaveasfilename = original_asksaveasfilename
        root.destroy()

if __name__ == "__main__":
    print("测试子网规划PDF导出功能...")
    success = test_pdf_export()
    if success:
        print("测试通过！")
    else:
        print("测试失败！")
        sys.exit(1)