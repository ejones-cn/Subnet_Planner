#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的树形布局算法
"""

import tkinter as tk
from tkinter import ttk
from visualization import NetworkTopologyVisualizer


def create_test_data():
    """创建测试网络数据，模拟样例图的结构"""
    # 创建根节点 (菱形 - router)
    root = {
        "id": "root",
        "name": "Root Router",
        "cidr": "10.0.0.0/8",
        "level": 0,
        "device_type": "router",
        "subnet_type": "network",
        "ip_info": {"total": 16777214, "allocated": 0, "reserved": 0},
        "children": []
    }
    
    # 第一层子节点 (椭圆 - switch)
    level1_node1 = {
        "id": "l1n1",
        "name": "Core Switch 1",
        "cidr": "10.1.0.0/16",
        "level": 1,
        "device_type": "switch",
        "subnet_type": "network",
        "parent_id": "root",
        "ip_info": {"total": 65534, "allocated": 0, "reserved": 0},
        "children": []
    }
    
    level1_node2 = {
        "id": "l1n2",
        "name": "Core Switch 2",
        "cidr": "10.2.0.0/16",
        "level": 1,
        "device_type": "switch",
        "subnet_type": "network",
        "parent_id": "root",
        "ip_info": {"total": 65534, "allocated": 0, "reserved": 0},
        "children": []
    }
    
    root["children"] = [level1_node1, level1_node2]
    
    # 为 level1_node1 添加子节点 (多个不同形状)
    l1n1_children = []
    for i in range(7):
        device_types = ["server", "switch2", "switch3", "wireless", "office", "client", "test"]
        subnet_types = ["server", "network", "management", "wireless", "office", "client", "test"]
        child = {
            "id": f"l2n1_{i}",
            "name": f"Device {i + 1}",
            "cidr": f"10.1.{i + 1}.0/24",
            "level": 2,
            "device_type": device_types[i],
            "subnet_type": subnet_types[i],
            "parent_id": "l1n1",
            "ip_info": {"total": 254, "allocated": 10 * (i + 1), "reserved": 5},
            "children": []
        }
        l1n1_children.append(child)
    
    # 为前两个子节点添加第三代
    for i in range(2):
        if i < len(l1n1_children):
            grandchild1 = {
                "id": f"l3n1_{i}_1",
                "name": f"Server {i + 1}-1",
                "cidr": f"10.1.{i + 1}.128/25",
                "level": 3,
                "device_type": "server",
                "subnet_type": "server",
                "parent_id": f"l2n1_{i}",
                "ip_info": {"total": 126, "allocated": 20, "reserved": 2}
            }
            grandchild2 = {
                "id": f"l3n1_{i}_2",
                "name": f"Client {i + 1}-2",
                "cidr": f"10.1.{i + 1}.192/26",
                "level": 3,
                "device_type": "client",
                "subnet_type": "client",
                "parent_id": f"l2n1_{i}",
                "ip_info": {"total": 62, "allocated": 15, "reserved": 1}
            }
            l1n1_children[i]["children"] = [grandchild1, grandchild2]
    
    level1_node1["children"] = l1n1_children
    
    # 为 level1_node2 添加子节点
    l1n2_children = []
    
    # 添加更多节点，确保各种形状都有体现
    device_types = ["switch", "wireless", "office", "production", "dmz", "storage", "backup"]
    subnet_types = ["network", "wireless", "office", "production", "dmz", "storage", "backup"]
    
    for i in range(len(device_types)):
        child = {
            "id": f"l2n2_{i}",
            "name": f"Branch {i + 1}",
            "cidr": f"10.2.{i + 1}.0/24",
            "level": 2,
            "device_type": device_types[i],
            "subnet_type": subnet_types[i],
            "parent_id": "l1n2",
            "ip_info": {"total": 254, "allocated": 30 * (i + 1), "reserved": 10},
            "children": []
        }
        l1n2_children.append(child)
    
    # 为第二个子节点添加更深的层级
    deep_child = {
        "id": "l3n2_1",
        "name": "Deep Device 1",
        "cidr": "10.2.2.128/25",
        "level": 3,
        "device_type": "server",
        "subnet_type": "server",
        "parent_id": "l2n2_1",
        "ip_info": {"total": 126, "allocated": 50, "reserved": 5},
        "children": []
    }
    l1n2_children[1]["children"] = [deep_child]
    
    # 再添加一层
    deeper_child = {
        "id": "l4n2_1",
        "name": "Deeper Device",
        "cidr": "10.2.2.192/26",
        "level": 4,
        "device_type": "client",
        "subnet_type": "client",
        "parent_id": "l3n2_1",
        "ip_info": {"total": 62, "allocated": 25, "reserved": 2}
    }
    deep_child["children"] = [deeper_child]
    
    level1_node2["children"] = l1n2_children
    
    return root


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    root.title("网络拓扑图 - 树形布局测试")
    root.geometry("1200x800")
    
    # 创建主框架
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 创建可视化器
    visualizer = NetworkTopologyVisualizer(main_frame)
    
    # 创建测试数据
    network_data = create_test_data()
    
    # 绘制拓扑图
    visualizer.draw_topology(network_data)
    
    # 自动缩放
    visualizer.auto_scale_to_fit()
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    main()
