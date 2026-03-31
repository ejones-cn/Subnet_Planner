#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络拓扑可视化功能测试脚本
"""

import tkinter as tk
from visualization import NetworkTopologyVisualizer

# 生成测试数据
def generate_test_data():
    """生成测试网络数据"""
    return [
        {
            "id": "net1",
            "name": "核心网络",
            "cidr": "10.0.0.0/16",
            "level": 0,
            "type": "network",
            "device_type": "router",
            "ip_info": {"total": 65536, "used": 1200, "available": 64336},
            "children": ["net2", "net3"]
        },
        {
            "id": "net2",
            "name": "服务器网络",
            "cidr": "10.0.1.0/24",
            "level": 1,
            "type": "server",
            "device_type": "server",
            "ip_info": {"total": 256, "used": 50, "available": 206},
            "children": []
        },
        {
            "id": "net3",
            "name": "客户端网络",
            "cidr": "10.0.2.0/24",
            "level": 1,
            "type": "client",
            "device_type": "switch",
            "ip_info": {"total": 256, "used": 150, "available": 106},
            "children": ["net4"]
        },
        {
            "id": "net4",
            "name": "管理网络",
            "cidr": "10.0.2.128/26",
            "level": 2,
            "type": "management",
            "device_type": "client",
            "ip_info": {"total": 64, "used": 20, "available": 44},
            "children": []
        }
    ]

# 测试函数
def test_visualization():
    """测试网络拓扑可视化功能"""
    # 创建主窗口
    root = tk.Tk()
    root.title("网络拓扑可视化测试")
    root.geometry("1000x800")
    
    # 创建可视化器
    visualizer = NetworkTopologyVisualizer(root)
    
    # 生成测试数据
    test_data = generate_test_data()
    
    # 绘制拓扑图
    visualizer.draw_topology(test_data)
    
    # 测试数据回调
    def data_callback():
        return generate_test_data()
    
    visualizer.set_data_callback(data_callback)
    
    # 测试自动更新（5秒刷新一次）
    visualizer.start_auto_update(interval=5000)
    
    # 测试过滤功能
    def test_filter():
        visualizer.set_filter_level(1)  # 只显示1级及以下节点
    
    # 添加测试按钮
    frame = tk.Frame(root)
    frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    
    filter_btn = tk.Button(frame, text="测试过滤（只显示1级及以下）", command=test_filter)
    filter_btn.pack(side=tk.LEFT, padx=5)
    
    refresh_btn = tk.Button(frame, text="手动刷新", command=visualizer.refresh_data)
    refresh_btn.pack(side=tk.LEFT, padx=5)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    test_visualization()
