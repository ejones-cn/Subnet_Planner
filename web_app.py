#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Web应用程序，提供子网规划和计算功能。"""

import ipaddress
import json
import re
from flask import Flask, request, render_template_string
from ip_subnet_calculator import split_subnet, suggest_subnet_planning, ipv4_to_ipv6, ipv6_to_ipv4, merge_subnets, get_ip_info, range_to_cidr, check_subnet_overlap
from web_version import __version__

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>子网规划师</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f8ff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        h2 {
            color: #444;
            margin-top: 30px;
        }
        h3 {
            color: #555;
            margin-top: 20px;
        }
        h4 {
            color: #666;
            margin-top: 15px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"],
        input[type="number"] {
            width: 300px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #2980b9;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .error {
            color: red;
            margin-bottom: 20px;
        }
        .info-row {
            margin-bottom: 10px;
        }
        .info-label {
            display: inline-block;
            width: 120px;
            font-weight: bold;
            color: #555;
        }
        .info-value {
            display: inline-block;
        }
        .subnet-info {
            background-color: white;
            padding: 15px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        .tabs {
            display: flex;
            margin-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        /* 最顶级功能标签页样式 */
        .tab {
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            margin-right: 5px;
            border-radius: 4px 4px 0 0;
            transition: all 0.3s ease;
        }
        /* 子网切分标签页颜色 */
        .tab:nth-child(1) {
            background-color: rgba(52, 152, 219, 0.3); /* 浅蓝色背景 */
            color: #2980b9;
        }
        .tab:nth-child(1).active {
            background-color: #3498db; /* 蓝色激活状态 */
            color: white;
        }
        /* 子网规划建议标签页颜色 */
        .tab:nth-child(2) {
            background-color: rgba(46, 204, 113, 0.3); /* 浅绿色背景 */
            color: #27ae60;
        }
        .tab:nth-child(2).active {
            background-color: #2ecc71; /* 绿色激活状态 */
            color: white;
        }
        /* 切分结果内部标签页样式 */
        .result-tab {
            border: none;
            padding: 8px 16px;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
            margin-right: 5px;
            transition: all 0.3s ease;
        }
        /* 切分结果内部标签页颜色 */
        .result-tab:nth-child(1) {
            background-color: rgba(52, 152, 219, 0.3); /* 浅蓝色背景 */
            color: #2980b9;
        }
        .result-tab:nth-child(1).active {
            background-color: #3498db; /* 蓝色激活状态 */
            color: white;
            font-weight: bold;
        }
        .result-tab:nth-child(2) {
            background-color: rgba(46, 204, 113, 0.3); /* 浅绿色背景 */
            color: #27ae60;
        }
        .result-tab:nth-child(2).active {
            background-color: #2ecc71; /* 绿色激活状态 */
            color: white;
            font-weight: bold;
        }
        .result-tab:nth-child(3) {
            background-color: rgba(230, 126, 34, 0.3); /* 浅橙色背景 */
            color: #d35400;
        }
        .result-tab:nth-child(3).active {
            background-color: #e67e22; /* 橙色激活状态 */
            color: white;
            font-weight: bold;
        }
        .tool-content {
            display: none;
        }
        .tool-content.active {
            display: block;
        }
        .subnet-requirement {
            margin: 15px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }
        .subnet-requirement input[type="text"],
        .subnet-requirement input[type="number"] {
            width: 200px;
            margin: 0 10px 10px 0;
        }
        .table-container {
            border: 1px solid #ddd;
        }
        .subnet-table {
            width: 100%;
            min-width: 100%;
            border-collapse: collapse;
            table-layout: auto;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .subnet-table th, .subnet-table td {
            padding: 6px 8px;
            text-align: center;
            vertical-align: middle;
            height: auto;
            line-height: 1.4;
            white-space: nowrap;
            max-width: 180px;
        }
        .subnet-table th {
            background-color: #555;
            color: white;
            font-weight: bold;
            white-space: nowrap;
            font-size: 14px;
            letter-spacing: 0.3px;
            min-width: 70px;
        }
        .subnet-table tr {
            border-bottom: 1px solid #e8e8e8;
            transition: background-color 0.2s ease;
        }
        .subnet-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .subnet-table tr:hover {
            background-color: #e3f2fd;
        }
        .subnet-table input[type="text"],
        .subnet-table input[type="number"] {
            box-sizing: border-box;
            padding: 8px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.2s ease;
            width: 100%;
            height: 32px;
            vertical-align: middle;
            display: inline-block;
            margin: auto;
        }
        .subnet-table input[type="text"]:focus,
        .subnet-table input[type="number"]:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }
        .subnet-table button {
            transition: all 0.2s ease;
            font-weight: 500;
            height: 32px;
            line-height: 16px;
            margin: auto;
            display: block;
        }
        .subnet-table button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        .table-container {
            border: none;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>子网规划师 v{{ version }}</h1>
        
        <!-- 功能选项卡 -->
        <div class="tabs">
            <button class="tab {{ 'active' if active_tab == 'subnet-split' else '' }}" data-target="subnet-split">子网切分</button>
            <button class="tab {{ 'active' if active_tab == 'subnet-plan' else '' }}" data-target="subnet-plan">子网规划</button>
            <button class="tab {{ 'active' if active_tab == 'ipv4-to-ipv6' else '' }}" data-target="ipv4-to-ipv6">IPv4转IPv6</button>
            <button class="tab {{ 'active' if active_tab == 'ipv6-to-ipv4' else '' }}" data-target="ipv6-to-ipv4">IPv6转IPv4</button>
            <button class="tab {{ 'active' if active_tab == 'ip-info' else '' }}" data-target="ip-info">IP地址信息</button>
            <button class="tab {{ 'active' if active_tab == 'subnet-merge' else '' }}" data-target="subnet-merge">子网合并</button>
            <button class="tab {{ 'active' if active_tab == 'range-to-cidr' else '' }}" data-target="range-to-cidr">IP范围转CIDR</button>
            <button class="tab {{ 'active' if active_tab == 'subnet-overlap' else '' }}" data-target="subnet-overlap">子网重叠检查</button>
        </div>
        
        <!-- 子网切分功能 -->
        <div id="subnet-split" class="tool-content {{ 'active' if active_tab == 'subnet-split' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="subnet-split">
                <div class="form-group">
                    <label for="parent">父网段 (如：10.0.0.0/8)</label>
                    <input type="text" id="parent" name="parent" value="{{ parent if parent else '10.0.0.0/8' }}" required>
                </div>
                <div class="form-group">
                    <label for="split">要切分的子网 (如：10.21.60.0/23)</label>
                    <input type="text" id="split" name="split" value="{{ split if split else '10.21.60.0/23' }}" required>
                </div>
                <button type="submit" name="action" value="split">执行切分</button>
            </form>
            
            <!-- 子网切分结果展示 -->
            {% if result %}
                <div class="result">
                    {% if result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ result.error }}
                        </div>
                    {% else %}
                        <h2>切分结果</h2>
                        
                        <!-- 标签页控制 -->
                        <div class="tabs result-tabs">
                            <button class="result-tab active" onclick="openResultTab(event, 'split-info')">切分网段信息</button>
                            <button class="result-tab" onclick="openResultTab(event, 'remaining-subnets')">剩余网段列表</button>
                            <button class="result-tab" onclick="openResultTab(event, 'subnet-chart')">网段分布图表</button>
                        </div>
                        
                        <!-- 切分网段信息标签页 -->
                        <div id="split-info" class="tab-content active" style="background-color: #fff; padding: 15px; border-radius: 4px; border: 1px solid #ddd;">
                            <div class="subnet-info">
                                <h3>网段详细信息</h3>
                                <div class="table-container">
                                    <table class="subnet-table">
                                        <tr>
                                            <th>信息类型</th>
                                            <th>父网段</th>
                                            <th>切分网段</th>
                                        </tr>
                                        <tr>
                                            <td>网段</td>
                                            <td>{{ result.parent }}</td>
                                            <td>{{ result.split }}</td>
                                        </tr>
                                        <tr>
                                            <td>网络地址</td>
                                            <td>{{ result.parent_info.network }}</td>
                                            <td>{{ result.split_info.network }}</td>
                                        </tr>
                                        <tr>
                                            <td>子网掩码</td>
                                            <td>{{ result.parent_info.netmask }}</td>
                                            <td>{{ result.split_info.netmask }}</td>
                                        </tr>
                                        <tr>
                                            <td>广播地址</td>
                                            <td>{{ result.parent_info.broadcast }}</td>
                                            <td>{{ result.split_info.broadcast }}</td>
                                        </tr>
                                        <tr>
                                            <td>地址总数</td>
                                            <td>{{ result.parent_info.num_addresses }}</td>
                                            <td>{{ result.split_info.num_addresses }}</td>
                                        </tr>
                                        <tr>
                                            <td>可用地址</td>
                                            <td>{{ result.parent_info.usable_addresses }}</td>
                                            <td>{{ result.split_info.usable_addresses }}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            

                        </div>
                        
                        <!-- 剩余网段列表标签页 -->
                        <div id="remaining-subnets" class="tab-content" style="background-color: #fff; padding: 15px; border-radius: 4px; border: 1px solid #ddd;">
                            <div class="content-container">
                                <h3>剩余网段 ({{ result.remaining_subnets_info|length }} 个)</h3>
                                
                                <div class="table-container">
                                    <table class="subnet-table">
                                        <tr>
                                            <th>序号</th>
                                            <th>CIDR</th>
                                            <th>网络地址</th>
                                            <th>子网掩码</th>
                                            <th>通配符掩码</th>
                                            <th>广播地址</th>
                                            <th>可用地址</th>
                                        </tr>
                                        {% for subnet in result.remaining_subnets_info %}
                                            <tr>
                                                <td>{{ loop.index }}</td>
                                                <td>{{ subnet.cidr }}</td>
                                                <td>{{ subnet.network }}</td>
                                                <td>{{ subnet.netmask }}</td>
                                                <td>{{ subnet.wildcard }}</td>
                                                <td>{{ subnet.broadcast }}</td>
                                                <td>{{ subnet.usable_addresses }}</td>
                                            </tr>
                                        {% endfor %}
                                    </table>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 网段分布图表标签页 -->
                        <div id="subnet-chart" class="tab-content" style="background-color: #fff; padding: 15px; border-radius: 4px; border: 1px solid #ddd;">
                            <div style="width: 100%; overflow: hidden;">
                                <canvas id="subnetChartCanvas"></canvas>
                            </div>
                            <script>
                                function drawSubnetChart() {
                                    try {
                                        console.log('=== 开始绘制网段图表 ===');
                                        
                                        // 1. 获取canvas元素
                                        var canvas = document.getElementById('subnetChartCanvas');
                                        if (!canvas) {
                                            console.error('❌ Canvas元素不存在');
                                            return;
                                        }
                                        console.log('✅ Canvas元素:', canvas);
                                        
                                        // 2. 获取绘图上下文
                                        var ctx = canvas.getContext('2d');
                                        if (!ctx) {
                                            console.error('❌ 无法获取Canvas上下文');
                                            return;
                                        }
                                        console.log('✅ Canvas上下文:', ctx);
                                        
                                        // 3. 设置画布尺寸
                                        var containerWidth = canvas.parentElement.clientWidth || 800;
                                        canvas.width = containerWidth;
                                        console.log('✅ 画布宽度设置完成:', canvas.width);
                                        
                                        // 4. 清空画布
                                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                                        // 设置白色背景
                                        ctx.fillStyle = '#fff';
                                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                                        
                                        // 5. 获取数据 - 使用默认数据作为备用
                                        var parentCidr, splitInfo, remainingSubnets;
                                        try {
                                            // 从模板获取数据
                                            parentCidr = "{{ result.parent if result else '192.168.0.0/16' }}";
                                            splitInfo = {
                                                network: "{{ result.split_info.network if (result and result.split_info) else '192.168.0.0' }}",
                                                cidr: "{{ result.split_info.cidr if (result and result.split_info) else '192.168.0.0/18' }}",
                                                prefixlen: {{ result.split_info.prefixlen if (result and result.split_info) else 18 }},
                                                num_addresses: {{ result.split_info.num_addresses if (result and result.split_info) else 16384 }},
                                                usable_addresses: {{ result.split_info.usable_addresses if (result and result.split_info) else 16382 }}
                                            };
                                            
                                            remainingSubnets = [
                                                {% if result and result.remaining_subnets_info %}
                                                {% for subnet in result.remaining_subnets_info %}
                                                    {
                                                        network: "{{ subnet.network }}",
                                                        cidr: "{{ subnet.cidr }}",
                                                        prefixlen: {{ subnet.prefixlen }},
                                                        num_addresses: {{ subnet.num_addresses }},
                                                        usable_addresses: {{ subnet.usable_addresses }}
                                                    }{{ ',' if not loop.last else '' }}
                                                {% endfor %}
                                                {% else %}
                                                    {
                                                        network: '192.168.64.0',
                                                        cidr: '192.168.64.0/18',
                                                        prefixlen: 18,
                                                        num_addresses: 16384,
                                                        usable_addresses: 16382
                                                    }
                                                {% endif %}
                                            ];
                                            
                                            console.log('✅ 从模板获取数据:', {
                                                parentCidr: parentCidr,
                                                splitInfo: splitInfo,
                                                remainingSubnets: remainingSubnets
                                            });
                                        } catch (e) {
                                            console.error('❌ 从模板获取数据失败:', e);
                                            // 使用默认数据
                                            parentCidr = '192.168.0.0/16';
                                            splitInfo = {
                                                network: '192.168.0.0',
                                                cidr: '192.168.0.0/18',
                                                prefixlen: 18,
                                                num_addresses: 16384,
                                                usable_addresses: 16382
                                            };
                                            remainingSubnets = [
                                                {
                                                    network: '192.168.64.0',
                                                    cidr: '192.168.64.0/18',
                                                    prefixlen: 18,
                                                    num_addresses: 16384,
                                                    usable_addresses: 16382
                                                }
                                            ];
                                            console.log('ℹ️ 使用默认测试数据');
                                        }
                                        
                                        // 确保数据有效性
                                        if (!parentCidr) parentCidr = '192.168.0.0/16';
                                        if (!splitInfo) {
                                            splitInfo = {
                                                network: '192.168.0.0',
                                                cidr: '192.168.0.0/18',
                                                prefixlen: 18,
                                                num_addresses: 16384,
                                                usable_addresses: 16382
                                            };
                                        }
                                        if (!remainingSubnets || remainingSubnets.length === 0) {
                                            remainingSubnets = [
                                                {
                                                    network: '192.168.64.0',
                                                    cidr: '192.168.64.0/18',
                                                    prefixlen: 18,
                                                    num_addresses: 16384,
                                                    usable_addresses: 16382
                                                }
                                            ];
                                        }
                                        
                                        // 6. 计算父网段的总地址数和比例尺
                                        var parentPrefix = parseInt(parentCidr.split('/')[1]);
                                        var parentTotalAddresses = Math.pow(2, 32 - parentPrefix);
                                        
                                        // 使用对数比例尺来更好地显示差距巨大的网段大小
                                        var logMax = Math.log10(parentTotalAddresses);
                                        var logMin = 3; // 最小显示3个数量级（1000个地址）
                                        
                                        // 为小网段设置最小显示宽度
                                        var minBarWidth = 50;
                                        
                                        // 7. 绘制配置
                                        var x = 50;
                                        var y = 50;
                                        var barHeight = 40;
                                        var padding = 20;
                                        var availableWidth = canvas.width - 100;
                                        
                                        // 8. 动态调整画布高度：父网段 + 切分网段 + 剩余网段列表 + 图例
                                        var totalBars = 2 + remainingSubnets.length + 3; // 父+切分+剩余+图例+标题
                                        canvas.height = Math.max(600, totalBars * (barHeight + padding) + 100);
                                        console.log('✅ 画布尺寸设置完成:', canvas.width, 'x', canvas.height);
                                        
                                        // 9. 重新清空画布（因为高度可能变化）
                                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                                        
                                        // 10. 绘制父网段
                                        ctx.fillStyle = '#95a5a6'; // 灰色表示父网段
                                        var parentBarWidth = availableWidth; // 父网段占满整个宽度
                                        ctx.fillRect(x, y, parentBarWidth, barHeight);
                                        
                                        // 绘制父网段文本
                                        ctx.fillStyle = '#000000';
                                        ctx.font = '16px Arial';
                                        ctx.textBaseline = 'middle';
                                        ctx.strokeStyle = '#ffffff';
                                        ctx.lineWidth = 2;
                                        
                                        var segmentText = '父网段: ' + parentCidr;
                                        var addressText = '可用地址: ' + parentTotalAddresses.toLocaleString();
                                        var addressX = x + 250;
                                        
                                        ctx.strokeText(segmentText, x + 15, y + barHeight / 2);
                                        ctx.fillText(segmentText, x + 15, y + barHeight / 2);
                                        ctx.strokeText(addressText, addressX, y + barHeight / 2);
                                        ctx.fillText(addressText, addressX, y + barHeight / 2);
                                        
                                        y += barHeight + padding;
                                        
                                        // 11. 绘制切分网段
                                        // 使用对数比例尺计算宽度
                                        var splitLogValue = Math.max(logMin, Math.log10(splitInfo.num_addresses));
                                        var splitBarWidth = Math.max(minBarWidth, ((splitLogValue - logMin) / (logMax - logMin)) * availableWidth);
                                        
                                        ctx.fillStyle = '#3498db'; // 蓝色表示切分网段
                                        ctx.fillRect(x, y, splitBarWidth, barHeight);
                                        
                                        // 绘制切分网段文本
                                        ctx.fillStyle = '#000000';
                                        ctx.font = '16px Arial';
                                        ctx.textBaseline = 'middle';
                                        ctx.strokeStyle = '#ffffff';
                                        ctx.lineWidth = 2;
                                        
                                        // 绘制网段信息（左对齐）
                                        var segmentText = '切分网段: ' + splitInfo.cidr;
                                        var addressText = '可用地址: ' + splitInfo.usable_addresses.toLocaleString();
                                        
                                        // 网段信息左对齐，地址数在固定位置对齐
                                        var addressX = x + 250; // 固定地址数的起始位置
                                        
                                        ctx.strokeText(segmentText, x + 15, y + barHeight / 2);
                                        ctx.fillText(segmentText, x + 15, y + barHeight / 2);
                                        ctx.strokeText(addressText, addressX, y + barHeight / 2);
                                        ctx.fillText(addressText, addressX, y + barHeight / 2);
                                        
                                        y += barHeight + padding + 20;
                                        
                                        // 12. 绘制剩余网段标题
                                        ctx.fillStyle = '#34495e';
                                        ctx.font = '18px Arial';
                                        ctx.fillText('剩余网段 (' + remainingSubnets.length + ' 个):', x, y);
                                        
                                        y += 20;
                                        
                                        // 13. 绘制剩余网段
                                        var colors = ['#27ae60', '#e74c3c', '#f39c12', '#8e44ad', '#16a085', '#2c3e50'];
                                        for (var i = 0; i < remainingSubnets.length; i++) {
                                            var subnet = remainingSubnets[i];
                                            
                                            // 使用对数比例尺计算宽度
                                            var subnetLogValue = Math.max(logMin, Math.log10(subnet.num_addresses));
                                            var subnetBarWidth = Math.max(minBarWidth, ((subnetLogValue - logMin) / (logMax - logMin)) * availableWidth);
                                            
                                            ctx.fillStyle = colors[i % colors.length];
                                            ctx.fillRect(x, y, subnetBarWidth, barHeight);
                                            
                                            // 绘制网段信息
                                            ctx.fillStyle = '#000000';
                                            ctx.font = '16px Arial';
                                            ctx.textBaseline = 'middle';
                                            ctx.strokeStyle = '#ffffff';
                                            ctx.lineWidth = 2;
                                            
                                            // 绘制网段信息（左对齐）
                                            var segmentText = '网段 ' + (i + 1) + ': ' + subnet.cidr;
                                            var addressText = '可用地址: ' + subnet.usable_addresses.toLocaleString();
                                            
                                            // 网段信息左对齐，地址数在固定位置对齐
                                            var addressX = x + 250; // 固定地址数的起始位置
                                            
                                            ctx.strokeText(segmentText, x + 15, y + barHeight / 2);
                                            ctx.fillText(segmentText, x + 15, y + barHeight / 2);
                                            ctx.strokeText(addressText, addressX, y + barHeight / 2);
                                            ctx.fillText(addressText, addressX, y + barHeight / 2);
                                            
                                            y += barHeight + padding;
                                        }
                                        
                                        // 13. 绘制图例
                                        y += 20;
                                        ctx.fillStyle = '#34495e';
                                        ctx.font = '14px Arial';
                                        ctx.fillText('图例:', x, y);
                                        
                                        y += 10;
                                        ctx.fillStyle = '#95a5a6';
                                        ctx.fillRect(x, y, 20, 15);
                                        ctx.fillStyle = '#000000';
                                        ctx.font = '12px Arial';
                                        ctx.textBaseline = 'middle';
                                        ctx.fillText('父网段', x + 30, y + 7);
                                        
                                        ctx.fillStyle = '#3498db';
                                        ctx.fillRect(x + 100, y, 20, 15);
                                        ctx.fillStyle = '#000000';
                                        ctx.fillText('切分网段', x + 130, y + 7);
                                        
                                        ctx.fillStyle = '#27ae60';
                                        ctx.fillRect(x + 200, y, 20, 15);
                                        ctx.fillStyle = '#000000';
                                        ctx.fillText('剩余网段', x + 230, y + 7);
                                        
                                        console.log('✅ 图表绘制完成');
                                    } catch (error) {
                                        console.error('绘制图表时发生错误:', error);
                                        
                                        // 尝试获取canvas元素并显示错误信息
                                        var canvas = document.getElementById('subnetChartCanvas');
                                        if (canvas) {
                                            var ctx = canvas.getContext('2d');
                                            if (ctx) {
                                                // 设置最小高度以显示错误信息
                                                canvas.height = 200;
                                                ctx.clearRect(0, 0, canvas.width, canvas.height);
                                                ctx.fillStyle = '#e74c3c';
                                                ctx.font = '16px Arial';
                                                ctx.textAlign = 'center';
                                                ctx.fillText('图表加载失败: ' + error.message, canvas.width / 2, canvas.height / 2);
                                            }}
                                    }
                                }
                            
                            // 页面加载完成后绘制图表
                            window.onload = function() {
                                // 检查是否有结果数据
                                {% if result and not result.error %}
                                    drawSubnetChart();
                                {% endif %}
                            };
                            
                            // 监听标签页切换事件，当切换到图表标签页时重新绘制
                            document.addEventListener('DOMContentLoaded', function() {
                                // 监听所有标签页按钮，包括功能选项卡和结果标签页
                                var tabs = document.querySelectorAll('.tab, .result-tab');
                                tabs.forEach(function(tab) {
                                    tab.addEventListener('click', function(e) {
                                        if (e.target.textContent === '网段分布图表' || e.target.innerHTML === '网段分布图表') {
                                            setTimeout(function() {
                                                console.log('切换到图表标签页，重新绘制图表');
                                                drawSubnetChart();
                                            }, 100);
                                        }
                                    });
                                });
                            });
                              </script>
                          </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IPv4转IPv6功能 -->
        <div id="ipv4-to-ipv6" class="tool-content {{ 'active' if active_tab == 'ipv4-to-ipv6' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="ipv4-to-ipv6">
                <div class="form-group">
                    <label for="ipv4">IPv4地址</label>
                    <input type="text" id="ipv4" name="ipv4" placeholder="例如：192.168.1.1">
                </div>
                <button type="submit" name="action" value="ipv4-to-ipv6">转换为IPv6</button>
            </form>
            
            {% if ipv6_result %}
                <div class="result">
                    {% if ipv6_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ ipv6_result.error }}
                        </div>
                    {% else %}
                        <h3>转换结果</h3>
                        <div class="info-row">
                            <div class="info-label">IPv4地址:</div>
                            <div class="info-value">{{ ipv4 }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">IPv6地址:</div>
                            <div class="info-value">{{ ipv6_result }}</div>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IPv6转IPv4功能 -->
        <div id="ipv6-to-ipv4" class="tool-content {{ 'active' if active_tab == 'ipv6-to-ipv4' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="ipv6-to-ipv4">
                <div class="form-group">
                    <label for="ipv6">IPv6地址</label>
                    <input type="text" id="ipv6" name="ipv6" placeholder="例如：::ffff:192.168.1.1">
                </div>
                <button type="submit" name="action" value="ipv6-to-ipv4">转换为IPv4</button>
            </form>
            
            {% if ipv4_result %}
                <div class="result">
                    {% if ipv4_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ ipv4_result.error }}
                        </div>
                    {% else %}
                        <h3>转换结果</h3>
                        <div class="info-row">
                            <div class="info-label">IPv6地址:</div>
                            <div class="info-value">{{ ipv6 }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">IPv4地址:</div>
                            <div class="info-value">{{ ipv4_result }}</div>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IP地址信息查询功能 -->
        <div id="ip-info" class="tool-content {{ 'active' if active_tab == 'ip-info' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="ip-info">
                <div class="form-group">
                    <label for="ip_query">IP地址</label>
                    <input type="text" id="ip_query" name="ip_query" placeholder="例如：192.168.1.1">
                </div>
                <button type="submit" name="action" value="ip-info">查询IP信息</button>
            </form>
            
            {% if ip_info_result %}
                <div class="result">
                    {% if ip_info_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ ip_info_result.error }}
                        </div>
                    {% else %}
                        <h3>IP信息</h3>
                        <div class="info-row">
                            <div class="info-label">IP地址:</div>
                            <div class="info-value">{{ ip_info_result.ip }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">IP分类:</div>
                            <div class="info-value">{{ ip_info_result.ip_class }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否私有IP:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_private else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否回环地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_loopback else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否链路本地地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_link_local else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否组播地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_multicast else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否保留地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_reserved else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">整数表示:</div>
                            <div class="info-value">{{ ip_info_result.integer }}</div>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IP范围转CIDR功能 -->
        <div id="range-to-cidr" class="tool-content {{ 'active' if active_tab == 'range-to-cidr' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="range-to-cidr">
                <div class="form-group">
                    <label for="start_ip">起始IP地址</label>
                    <input type="text" id="start_ip" name="start_ip" placeholder="例如：192.168.0.0">
                </div>
                <div class="form-group">
                    <label for="end_ip">结束IP地址</label>
                    <input type="text" id="end_ip" name="end_ip" placeholder="例如：192.168.0.255">
                </div>
                <button type="submit" name="action" value="range-to-cidr">转换为CIDR</button>
            </form>
            
            {% if range_result %}
                <div class="result">
                    {% if range_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ range_result.error }}
                        </div>
                    {% else %}
                        <h3>转换结果</h3>
                        <div class="info-row">
                            <div class="info-label">起始IP地址:</div>
                            <div class="info-value">{{ range_result.start_ip }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">结束IP地址:</div>
                            <div class="info-value">{{ range_result.end_ip }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">总地址数:</div>
                            <div class="info-value">{{ range_result.total_addresses }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">转换后的CIDR数量:</div>
                            <div class="info-value">{{ range_result.cidr_count }}</div>
                        </div>
                        
                        <h4>CIDR列表</h4>
                        <div class="table-container">
                            <table class="subnet-table">
                                <tr>
                                    <th>序号</th>
                                    <th>CIDR</th>
                                </tr>
                                {% for cidr in range_result.cidr_list %}
                                    <tr>
                                        <td>{{ loop.index }}</td>
                                        <td>{{ cidr }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- 子网重叠检查功能 -->
        <div id="subnet-overlap" class="tool-content {{ 'active' if active_tab == 'subnet-overlap' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="subnet-overlap">
                <div class="form-group">
                    <label for="overlap_subnets">子网列表（支持换行、逗号或空格分隔）</label>
                    <textarea id="overlap_subnets" name="overlap_subnets" rows="5" cols="50" placeholder="例如：
192.168.0.0/24
192.168.1.0/24
192.168.0.128/25"></textarea>
                </div>
                <button type="submit" name="action" value="check-overlap">检查重叠</button>
            </form>
            
            {% if overlap_result %}
                <div class="result">
                    {% if overlap_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ overlap_result.error }}
                        </div>
                    {% else %}
                        <h3>检查结果</h3>
                        <div class="info-row">
                            <div class="info-label">检查的子网数量:</div>
                            <div class="info-value">{{ overlap_result.subnets | length }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否存在重叠:</div>
                            <div class="info-value">{{ '是' if overlap_result.has_overlap else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">重叠数量:</div>
                            <div class="info-value">{{ overlap_result.overlap_count }}</div>
                        </div>
                        
                        {% if overlap_result.has_overlap %}
                            <h4>重叠详情</h4>
                            <div class="table-container">
                                <table class="subnet-table">
                                    <tr>
                                        <th>序号</th>
                                        <th>子网1</th>
                                        <th>子网2</th>
                                        <th>重叠类型</th>
                                    </tr>
                                    {% for overlap in overlap_result.overlaps %}
                                        <tr>
                                            <td>{{ loop.index }}</td>
                                            <td>{{ overlap.subnet1 }}</td>
                                            <td>{{ overlap.subnet2 }}</td>
                                            <td>{{ overlap.type }}</td>
                                        </tr>
                                    {% endfor %}
                                </table>
                            </div>
                        {% endif %}
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- 子网合并功能 -->
        <div id="subnet-merge" class="tool-content {{ 'active' if active_tab == 'subnet-merge' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="subnet-merge">
                <div class="form-group">
                    <label for="merge_subnets">子网列表（支持换行、逗号或空格分隔）</label>
                    <textarea id="merge_subnets" name="merge_subnets" rows="5" cols="50" placeholder="例如：
192.168.0.0/24
192.168.1.0/24
192.168.2.0/24
192.168.3.0/24"></textarea>
                </div>
                <button type="submit" name="action" value="merge">合并子网</button>
            </form>
            
            {% if merge_result %}
                <div class="result">
                    {% if merge_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ merge_result.error }}
                        </div>
                    {% else %}
                        <h3>合并结果</h3>
                        <div class="info-row">
                            <div class="info-label">原始子网数量:</div>
                            <div class="info-value">{{ merge_result.original_count }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">合并后子网数量:</div>
                            <div class="info-value">{{ merge_result.merged_count }}</div>
                        </div>
                        
                        <h4>合并后子网列表</h4>
                        <div class="table-container">
                            <table class="subnet-table">
                                <tr>
                                    <th>序号</th>
                                    <th>CIDR</th>
                                    <th>网络地址</th>
                                    <th>子网掩码</th>
                                    <th>可用地址</th>
                                </tr>
                                {% for subnet in merge_result.merged_subnets_info %}
                                    <tr>
                                        <td>{{ loop.index }}</td>
                                        <td>{{ subnet.cidr }}</td>
                                        <td>{{ subnet.network }}</td>
                                        <td>{{ subnet.netmask }}</td>
                                        <td>{{ subnet.usable_addresses }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IPv4转IPv6功能 -->
        <div id="ipv4-to-ipv6" class="tool-content {{ 'active' if active_tab == 'ipv4-to-ipv6' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="ipv4-to-ipv6">
                <div class="form-group">
                    <label for="ipv4">IPv4地址 (如：192.168.1.1)</label>
                    <input type="text" id="ipv4" name="ipv4" value="{{ ipv4 if ipv4 else '192.168.1.1' }}" required>
                </div>
                <button type="submit" name="action" value="ipv4-to-ipv6">转换为IPv6</button>
            </form>
            
            {% if ipv4_to_ipv6_result %}
                <div class="result">
                    {% if ipv4_to_ipv6_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ ipv4_to_ipv6_result.error }}
                        </div>
                    {% else %}
                        <div class="info-row">
                            <div class="info-label">IPv4地址:</div>
                            <div class="info-value">{{ ipv4_to_ipv6_result.ipv4 }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">IPv6地址:</div>
                            <div class="info-value">{{ ipv4_to_ipv6_result.ipv6 }}</div>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IPv6转IPv4功能 -->
        <div id="ipv6-to-ipv4" class="tool-content {{ 'active' if active_tab == 'ipv6-to-ipv4' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="ipv6-to-ipv4">
                <div class="form-group">
                    <label for="ipv6">IPv6地址 (如：::ffff:192.168.1.1)</label>
                    <input type="text" id="ipv6" name="ipv6" value="{{ ipv6 if ipv6 else '::ffff:192.168.1.1' }}" required>
                </div>
                <button type="submit" name="action" value="ipv6-to-ipv4">转换为IPv4</button>
            </form>
            
            {% if ipv6_to_ipv4_result %}
                <div class="result">
                    {% if ipv6_to_ipv4_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ ipv6_to_ipv4_result.error }}
                        </div>
                    {% else %}
                        <div class="info-row">
                            <div class="info-label">IPv6地址:</div>
                            <div class="info-value">{{ ipv6_to_ipv4_result.ipv6 }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">IPv4地址:</div>
                            <div class="info-value">{{ ipv6_to_ipv4_result.ipv4 }}</div>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IP地址信息功能 -->
        <div id="ip-info" class="tool-content {{ 'active' if active_tab == 'ip-info' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="ip-info">
                <div class="form-group">
                    <label for="ip">IP地址 (如：192.168.1.1)</label>
                    <input type="text" id="ip" name="ip" value="{{ ip if ip else '192.168.1.1' }}" required>
                </div>
                <button type="submit" name="action" value="ip-info">获取IP信息</button>
            </form>
            
            {% if ip_info_result %}
                <div class="result">
                    {% if ip_info_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ ip_info_result.error }}
                        </div>
                    {% else %}
                        <div class="info-row">
                            <div class="info-label">IP地址:</div>
                            <div class="info-value">{{ ip_info_result.ip }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">IP分类:</div>
                            <div class="info-value">{{ ip_info_result.ip_class }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否私有IP:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_private else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否回环地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_loopback else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否链路本地地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_link_local else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否组播地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_multicast else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否保留地址:</div>
                            <div class="info-value">{{ '是' if ip_info_result.is_reserved else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">整数表示:</div>
                            <div class="info-value">{{ ip_info_result.integer }}</div>
                        </div>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- 子网合并功能 -->
        <div id="subnet-merge" class="tool-content {{ 'active' if active_tab == 'subnet-merge' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="subnet-merge">
                <div class="form-group">
                    <label for="merge-subnets">子网列表 (每行一个，如：192.168.1.0/24)</label>
                    <textarea id="merge-subnets" name="merge-subnets" rows="5" cols="50" required>{{ merge_subnets_input if merge_subnets_input else '192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24\n192.168.3.0/24' }}</textarea>
                </div>
                <button type="submit" name="action" value="merge-subnets">合并子网</button>
            </form>
            
            {% if merge_subnets_result %}
                <div class="result">
                    {% if merge_subnets_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ merge_subnets_result.error }}
                        </div>
                    {% else %}
                        <div class="info-row">
                            <div class="info-label">原始子网数量:</div>
                            <div class="info-value">{{ merge_subnets_result.original_count }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">合并后子网数量:</div>
                            <div class="info-value">{{ merge_subnets_result.merged_count }}</div>
                        </div>
                        
                        <h3>原始子网列表</h3>
                        <ul>
                            {% for subnet in merge_subnets_result.original_subnets %}
                                <li>{{ subnet }}</li>
                            {% endfor %}
                        </ul>
                        
                        <h3>合并后子网列表</h3>
                        <ul>
                            {% for subnet in merge_subnets_result.merged_subnets %}
                                <li>{{ subnet }}</li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- IP范围转CIDR功能 -->
        <div id="range-to-cidr" class="tool-content {{ 'active' if active_tab == 'range-to-cidr' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="range-to-cidr">
                <div class="form-group">
                    <label for="start-ip">起始IP地址 (如：192.168.1.0)</label>
                    <input type="text" id="start-ip" name="start-ip" value="{{ start_ip if start_ip else '192.168.1.0' }}" required>
                </div>
                <div class="form-group">
                    <label for="end-ip">结束IP地址 (如：192.168.1.255)</label>
                    <input type="text" id="end-ip" name="end-ip" value="{{ end_ip if end_ip else '192.168.1.255' }}" required>
                </div>
                <button type="submit" name="action" value="range-to-cidr">转换为CIDR</button>
            </form>
            
            {% if range_to_cidr_result %}
                <div class="result">
                    {% if range_to_cidr_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ range_to_cidr_result.error }}
                        </div>
                    {% else %}
                        <div class="info-row">
                            <div class="info-label">起始IP:</div>
                            <div class="info-value">{{ range_to_cidr_result.start_ip }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">结束IP:</div>
                            <div class="info-value">{{ range_to_cidr_result.end_ip }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">CIDR数量:</div>
                            <div class="info-value">{{ range_to_cidr_result.cidr_count }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">总地址数:</div>
                            <div class="info-value">{{ range_to_cidr_result.total_addresses }}</div>
                        </div>
                        
                        <h3>转换后的CIDR列表</h3>
                        <ul>
                            {% for cidr in range_to_cidr_result.cidr_list %}
                                <li>{{ cidr }}</li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- 子网重叠检查功能 -->
        <div id="subnet-overlap" class="tool-content {{ 'active' if active_tab == 'subnet-overlap' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="subnet-overlap">
                <div class="form-group">
                    <label for="overlap-subnets">子网列表 (每行一个，如：192.168.1.0/24)</label>
                    <textarea id="overlap-subnets" name="overlap-subnets" rows="5" cols="50" required>{{ overlap_subnets_input if overlap_subnets_input else '192.168.1.0/24\n192.168.1.128/25\n192.168.2.0/24' }}</textarea>
                </div>
                <button type="submit" name="action" value="check-overlap">检查重叠</button>
            </form>
            
            {% if overlap_subnets_result %}
                <div class="result">
                    {% if overlap_subnets_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ overlap_subnets_result.error }}
                        </div>
                    {% else %}
                        <div class="info-row">
                            <div class="info-label">检查的子网数量:</div>
                            <div class="info-value">{{ overlap_subnets_result.subnets|length }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">是否存在重叠:</div>
                            <div class="info-value">{{ '是' if overlap_subnets_result.has_overlap else '否' }}</div>
                        </div>
                        <div class="info-row">
                            <div class="info-label">重叠数量:</div>
                            <div class="info-value">{{ overlap_subnets_result.overlap_count }}</div>
                        </div>
                        
                        {% if overlap_subnets_result.overlaps %}
                            <h3>重叠详情</h3>
                            <table class="subnet-table">
                                <tr>
                                    <th>序号</th>
                                    <th>子网1</th>
                                    <th>子网2</th>
                                    <th>重叠类型</th>
                                </tr>
                                {% for idx, overlap in enumerate(overlap_subnets_result.overlaps, 1) %}
                                    <tr>
                                        <td>{{ idx }}</td>
                                        <td>{{ overlap.subnet1 }}</td>
                                        <td>{{ overlap.subnet2 }}</td>
                                        <td>{{ overlap.type }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                        {% endif %}
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <!-- 子网规划建议功能 -->
        <div id="subnet-plan" class="tool-content {{ 'active' if active_tab == 'subnet-plan' else '' }}">
            <form method="POST">
                <input type="hidden" name="active_tab" value="subnet-plan">
                <div class="form-group">
                    <label for="plan-parent">父网段 (CIDR格式):</label>
                    <input type="text" id="plan-parent" name="plan-parent" value="{{ plan_parent or '192.168.0.0/16' }}" placeholder="例如: 192.168.0.0/16">
                </div>
                
                <div class="table-container">
                    <table class="subnet-table" id="subnet-requirements-table">
                        <thead>
                            <tr>
                                <th style="width: 60px;">序号</th>
                                <th style="width: 40%;">子网名称</th>
                                <th style="width: 30%;">所需主机数</th>
                                <th style="width: 100px;">操作</th>
                            </tr>
                        </thead>
                        <tbody id="subnet-requirements">
                            {% if subnet_requirements %}
                                {% for name, hosts in subnet_requirements %}
                                    <tr class="subnet-requirement">
                                        <td>{{ loop.index }}</td>
                                        <td><input type="text" name="subnet-name[]" value="{{ name }}" placeholder="例如: 办公区"></td>
                                        <td><input type="number" name="subnet-hosts[]" value="{{ hosts }}" placeholder="例如: 200" min="1"></td>
                                        <td>
                                            <button type="button" onclick="removeSubnetRequirement(this)" style="background-color: #e74c3c; color: white; border: none; padding: 6px 12px; cursor: pointer; border-radius: 4px; font-size: 14px; width: 100%;">
                                                删除
                                            </button>
                                        </td>
                                    </tr>
                                {% endfor %}
                            {% else %}
                                <tr class="subnet-requirement">
                                    <td>1</td>
                                    <td><input type="text" name="subnet-name[]" placeholder="例如: 办公区"></td>
                                    <td><input type="number" name="subnet-hosts[]" placeholder="例如: 200" min="1"></td>
                                    <td>
                                        <button type="button" onclick="removeSubnetRequirement(this)" style="background-color: #e74c3c; color: white; border: none; padding: 6px 12px; cursor: pointer; border-radius: 4px; font-size: 14px; width: 100%;">
                                            删除
                                        </button>
                                    </td>
                                </tr>
                            {% endif %}
                        </tbody>
                    </table>
                </div>
                <button type="button" onclick="addSubnetRequirement()" style="background-color: #27ae60; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; margin-top: 10px; font-size: 14px; font-weight: 500; transition: all 0.2s ease;">+ 添加子网</button>
                
                <button type="submit" name="action" value="plan" style="background-color: #3498db; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 4px; margin-top: 20px; font-size: 14px; font-weight: 500; transition: all 0.2s ease;">生成规划</button>
            </form>
            
            <!-- 子网规划结果展示 -->
            {% if plan_result %}
                <div class="result">
                    <h2>子网规划</h2>
                    
                    {% if plan_result.error %}
                        <div class="error">
                            <strong>错误：</strong>{{ plan_result.error }}
                        </div>
                    {% else %}
                        <div class="subnet-info">
                            <h3>规划概览</h3>
                            <div class="info-row">
                                <div class="info-label">父网段:</div>
                                <div class="info-value">{{ plan_result.parent_cidr }}</div>
                            </div>
                        </div>
                    
                    <h3>已分配子网</h3>
                    <div class="table-container">
                        <table class="subnet-table">
                            <tr>
                                <th>序号</th>
                                <th>名称</th>
                                <th>CIDR</th>
                                <th>需求主机数</th>
                                <th>可用主机数</th>
                                <th>网络地址</th>
                                <th>广播地址</th>
                                <th>起始IP</th>
                                <th>结束IP</th>
                                <th>子网掩码</th>
                            </tr>
                            {% for subnet in plan_result.allocated_subnets %}
                                <tr>
                                    <td>{{ loop.index }}</td>
                                    <td>{{ subnet.name }}</td>
                                    <td>{{ subnet.cidr }}</td>
                                    <td>{{ subnet.required_hosts }}</td>
                                    <td>{{ subnet.available_hosts }}</td>
                                    <td>{{ subnet.info.network }}</td>
                                    <td>{{ subnet.info.broadcast }}</td>
                                    <td>{{ subnet.info.host_range_start }}</td>
                                    <td>{{ subnet.info.host_range_end }}</td>
                                    <td>{{ subnet.info.netmask }}</td>
                                </tr>
                            {% endfor %}
                        </table>
                    </div>
                    
                    {% if plan_result.remaining_subnets %}
                        <h3>剩余可用网段</h3>
                        <div class="table-container">
                            <table class="subnet-table">
                                <tr>
                                    <th>序号</th>
                                    <th>网段</th>
                                    <th>可用地址</th>
                                </tr>
                                {% for subnet in plan_result.remaining_subnets %}
                                    {% set info = plan_result.remaining_subnets_info[loop.index0] %}
                                    <tr>
                                        <td>{{ loop.index }}</td>
                                        <td>{{ subnet }}</td>
                                        <td>{{ info.usable_addresses }}</td>
                                    </tr>
                                {% endfor %}
                            </table>
                        </div>
                    {% endif %}
                    {% endif %}
                </div>
            {% endif %}
        </div>
        
        <script>
            // 从localStorage加载保存的表单数据和当前激活的标签页
            let formData = JSON.parse(localStorage.getItem('formData')) || {
                'subnet-split': {},
                'subnet-plan': {}
            };
            let currentActiveTab = localStorage.getItem('currentActiveTab') || 'subnet-split';
            
            // 保存当前页面的表单数据
            function saveFormData() {
                // 获取当前激活的标签页
                const activeTab = document.querySelector('.tool-content.active');
                if (!activeTab) return;
                
                const tabId = activeTab.id;
                const data = {};
                
                // 保存普通输入字段
                const singleInputs = activeTab.querySelectorAll('input[type="text"], input[type="number"], textarea, select');
                singleInputs.forEach(input => {
                    if (input.name && !input.name.endsWith('[]')) {
                        data[input.name] = input.value;
                    }
                });
                
                // 特殊处理子网规划中的数组输入字段
                if (tabId === 'subnet-plan') {
                    const requirementRows = activeTab.querySelectorAll('.subnet-requirement');
                    const subnetNames = [];
                    const subnetHosts = [];
                    
                    requirementRows.forEach(row => {
                        const nameInput = row.querySelector('input[name="subnet-name[]"]');
                        const hostsInput = row.querySelector('input[name="subnet-hosts[]"]');
                        
                        if (nameInput && hostsInput) {
                            subnetNames.push(nameInput.value.trim());
                            subnetHosts.push(hostsInput.value.trim());
                        }
                    });
                    
                    // 保存子网名称和主机数数组
                    data['subnet-name'] = subnetNames;
                    data['subnet-hosts'] = subnetHosts;
                }
                
                formData[tabId] = data;
                
                // 保存到localStorage
                localStorage.setItem('formData', JSON.stringify(formData));
            }
            
            // 恢复表单数据
            function restoreFormData(tabId) {
                const data = formData[tabId];
                if (!data) return;
                
                const targetTab = document.getElementById(tabId);
                if (!targetTab) return;
                
                // 恢复普通输入字段
                Object.keys(data).forEach(fieldName => {
                    const value = data[fieldName];
                    
                    if (!Array.isArray(value)) {
                        const inputs = targetTab.querySelectorAll(`input[name="${fieldName}"]`);
                        inputs.forEach(input => {
                            input.value = value;
                        });
                    }
                });
                
                // 特殊处理子网规划中的数组输入字段
                if (tabId === 'subnet-plan') {
                    // 先清除现有输入行
                    const container = document.getElementById('subnet-requirements');
                    if (container) {
                        // 保留标题行，移除其他行
                        const rows = container.querySelectorAll('tr.subnet-requirement');
                        rows.forEach(row => row.remove());
                        
                        // 获取子网名称和主机数数组
                        const subnetNames = data['subnet-name'] || [];
                        const subnetHosts = data['subnet-hosts'] || [];
                        
                        // 添加新的输入行并填充数据
                        const maxLength = Math.max(subnetNames.length, subnetHosts.length);
                        for (let i = 0; i < maxLength; i++) {
                            addSubnetRequirement();
                        }
                        
                        // 填充数据到新添加的输入行
                        const newRows = container.querySelectorAll('tr.subnet-requirement');
                        newRows.forEach((row, index) => {
                            const nameInput = row.querySelector('input[name="subnet-name[]"]');
                            const hostsInput = row.querySelector('input[name="subnet-hosts[]"]');
                            
                            if (nameInput && subnetNames[index]) {
                                nameInput.value = subnetNames[index];
                            }
                            if (hostsInput && subnetHosts[index]) {
                                hostsInput.value = subnetHosts[index];
                            }
                        });
                    }
                }
            }
            
            // 通用标签页激活函数
            function activateTab(button, targetId, isToolTab = true) {
                // 移除所有激活状态
                if (isToolTab) {
                    document.querySelectorAll('.tabs button[data-target]').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    document.querySelectorAll('.tool-content').forEach(content => {
                        content.classList.remove('active');
                    });
                } else {
                    document.querySelectorAll('.result-tab').forEach(btn => {
                        btn.classList.remove('active');
                    });
                    document.querySelectorAll('.tab-content').forEach(content => {
                        content.classList.remove('active');
                    });
                }
                
                // 添加当前激活状态
                button.classList.add('active');
                const targetTab = document.getElementById(targetId);
                if (targetTab) {
                    targetTab.classList.add('active');
                }
                
                // 如果是工具标签页，保存状态和数据
                if (isToolTab) {
                    // 恢复目标页面的表单数据
                    restoreFormData(targetId);
                }
            }
            
            // 功能选项卡切换
            document.querySelectorAll('.tabs button[data-target]').forEach(button => {
                button.addEventListener('click', () => {
                    // 保存当前表单数据
                    saveFormData();
                    
                    const targetId = button.getAttribute('data-target');
                    activateTab(button, targetId, true);
                    
                    // 更新当前激活的标签页
                    currentActiveTab = targetId;
                    localStorage.setItem('currentActiveTab', currentActiveTab);
                });
            });
            
            // 页面加载完成后初始化
            document.addEventListener('DOMContentLoaded', function() {
                // 如果有保存的当前激活标签页，恢复它
                if (currentActiveTab) {
                    // 恢复工具标签页
                    const button = document.querySelector(`.tabs button[data-target="${currentActiveTab}"]`);
                    const targetTab = document.getElementById(currentActiveTab);
                    
                    if (button && targetTab) {
                        activateTab(button, currentActiveTab, true);
                    }
                }
                
                // 监听表单提交事件，保存数据并添加所有页面的数据到表单
            const forms = document.querySelectorAll('form');
            forms.forEach(form => {
                form.addEventListener('submit', function(event) {
                    saveFormData();
                    
                    // 创建隐藏输入字段，将所有表单数据发送给后端
                    const formDataInput = document.createElement('input');
                    formDataInput.type = 'hidden';
                    formDataInput.name = 'allFormData';
                    formDataInput.value = JSON.stringify(formData);
                    form.appendChild(formDataInput);
                    
                    // 创建隐藏输入字段，将当前激活的标签页发送给后端
                    const activeTabInput = document.createElement('input');
                    activeTabInput.type = 'hidden';
                    activeTabInput.name = 'currentActiveTab';
                    activeTabInput.value = currentActiveTab;
                    form.appendChild(activeTabInput);
                });
            });
            });
            
            // 监听页面卸载事件，保存数据
            window.addEventListener('beforeunload', function() {
                saveFormData();
            });
            
            // 内层结果标签页切换函数（仅影响切分结果内部的标签页）
            function openResultTab(evt, tabName) {
                // 使用通用标签页激活函数
                activateTab(evt.currentTarget, tabName, false);
                
                // 如果切换到图表标签页，重新绘制图表
                if (tabName === 'subnet-chart') {
                    setTimeout(drawSubnetChart, 100);
                }
            }
            
            // 添加子网需求
            function addSubnetRequirement() {
                var container = document.getElementById("subnet-requirements");
                var newRow = document.createElement("tr");
                newRow.className = "subnet-requirement";
                var count = container.children.length + 1;
                
                newRow.innerHTML = `
                    <td>${count}</td>
                    <td><input type="text" name="subnet-name[]" placeholder="例如: 办公区"></td>
                    <td><input type="number" name="subnet-hosts[]" placeholder="例如: 200" min="1"></td>
                    <td>
                        <button type="button" onclick="removeSubnetRequirement(this)" style="background-color: #e74c3c; color: white; border: none; padding: 6px 12px; cursor: pointer; border-radius: 4px; font-size: 14px; width: 100%;">
                            删除
                        </button>
                    </td>
                `;
                
                container.appendChild(newRow);
            }
            
            // 删除子网需求
            function removeSubnetRequirement(button) {
                var row = button.closest("tr");
                var container = document.getElementById("subnet-requirements");
                
                // 确保至少保留一行
                if (container.children.length > 1) {
                    row.remove();
                    updateSubnetIndices();
                } else {
                    alert("至少需要保留一个子网需求");
                }
            }
            
            // 更新子网序号
            function updateSubnetIndices() {
                var container = document.getElementById("subnet-requirements");
                const rows = container.querySelectorAll('.subnet-requirement');
                
                rows.forEach((row, index) => {
                    // 更新序号列
                    const indexCell = row.querySelector('td:first-child');
                    if (indexCell) {
                        indexCell.textContent = index + 1;
                    }
                });
            }
        </script>
        
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 14px;">
            版本: v{{ version }}
        </div>
    </div>
</body>
</html>
'''


@app.route("/", methods=["GET", "POST"])
def index():
    # 默认值设置为None，只有当表单提交包含特定字段时才更新
    parent = None
    split = None
    result = None
    plan_result = None
    plan_parent = None
    subnet_names = []
    host_counts = []
    active_tab = request.form.get('currentActiveTab', request.args.get('active_tab', 'subnet-split'))  # 默认显示子网切分标签页
    
    # IPv4转IPv6相关变量
    ipv4 = None
    ipv6_result = None
    ipv6 = None
    ipv4_result = None
    
    # IP信息查询相关变量
    ip_query = None
    ip_info_result = None
    
    # 子网合并相关变量
    merge_subnets_list = None
    merge_result = None
    
    # IP范围转CIDR相关变量
    start_ip = None
    end_ip = None
    range_result = None
    
    # 子网重叠检查相关变量
    overlap_subnets_list = None
    overlap_result = None

    # 辅助函数：过滤和转换子网需求数据
    def process_subnet_requirements(names, hosts):
        """过滤和转换子网需求数据，返回过滤后的名称和主机数列表"""
        filtered_names = []
        filtered_hosts = []
        valid = True
        
        for i in range(len(hosts)):
            host_count = hosts[i]
            if isinstance(host_count, str):
                host_count = host_count.strip()
            
            if not host_count:
                continue
                
            name = names[i] if i < len(names) else f"子网{i + 1}"
            if isinstance(name, str):
                name = name.strip()
            
            try:
                filtered_hosts.append(int(host_count))
                filtered_names.append(name)
            except ValueError:
                valid = False
                break
        
        return filtered_names, filtered_hosts, valid
    
    
    if request.method == "POST":
        # 尝试获取所有表单数据
        all_form_data = request.form.get('allFormData')
        if all_form_data:
            try:
                # 解析所有表单数据
                all_form_data = json.loads(all_form_data)
                
                # 恢复子网切分页面的数据
                if 'subnet-split' in all_form_data and all_form_data['subnet-split']:
                    split_data = all_form_data['subnet-split']
                    if 'parent' in split_data:
                        parent = split_data['parent']
                    if 'split' in split_data:
                        split = split_data['split']
                
                # 恢复子网规划页面的数据
                if 'subnet-plan' in all_form_data and all_form_data['subnet-plan']:
                    plan_data = all_form_data['subnet-plan']
                    if 'plan-parent' in plan_data:
                        plan_parent = plan_data['plan-parent']
                    if 'subnet-name' in plan_data and 'subnet-hosts' in plan_data:
                        subnet_names, host_counts, _ = process_subnet_requirements(
                            plan_data['subnet-name'], plan_data['subnet-hosts']
                        )
            except json.JSONDecodeError:
                pass
        
        action = request.form.get('action')
        if action == 'split':
            # 只有子网切分表单提交时才更新这些值
            parent = request.form.get("parent", parent or "10.0.0.0/8")
            split = request.form.get("split", split or "10.21.60.0/23")
            # 执行切分
            result = split_subnet(parent, split)
        elif action == 'plan':
            # 只有子网规划表单提交时才更新这些值
            plan_parent = request.form.get('plan-parent', plan_parent or "192.168.0.0/16")
            subnet_names_input = request.form.getlist('subnet-name[]')
            host_counts_input = request.form.getlist('subnet-hosts[]')
            
            # 如果表单中有新的输入，使用新的输入
            if subnet_names_input and host_counts_input:
                # 使用辅助函数处理子网需求数据
                filtered_names, filtered_hosts, valid = process_subnet_requirements(
                    subnet_names_input, host_counts_input
                )
                
                # 如果所有输入都是有效的，构造required_subnets参数并调用函数
                if valid:
                    # 更新要传递给模板的变量
                    subnet_names = filtered_names
                    host_counts = filtered_hosts
                    
                    # 构造required_subnets参数：列表中的每个元素是包含name和hosts字段的字典
                    required_subnets = [{"name": name, "hosts": hosts} for name, hosts in zip(subnet_names, host_counts)]
                    
                    # 调用子网规划建议函数
                    plan_result = suggest_subnet_planning(plan_parent, required_subnets)
                else:
                    # 如果有无效输入，返回错误信息
                    plan_result = {"error": "请确保所有子网的主机数字段都填写了有效的整数"}
        elif action == 'ipv4-to-ipv6':
            # IPv4转IPv6功能
            ipv4 = request.form.get('ipv4', '')
            if ipv4:
                ipv6_result = ipv4_to_ipv6(ipv4)
        elif action == 'ipv6-to-ipv4':
            # IPv6转IPv4功能
            ipv6 = request.form.get('ipv6', '')
            if ipv6:
                ipv4_result = ipv6_to_ipv4(ipv6)
        elif action == 'ip-info':
            # IP信息查询功能
            ip_query = request.form.get('ip_query', '')
            if ip_query:
                ip_info_result = get_ip_info(ip_query)
        elif action == 'merge':
            # 子网合并功能
            merge_subnets_text = request.form.get('merge_subnets', '')
            if merge_subnets_text:
                # 处理输入的子网列表，支持换行、逗号、空格分隔
                subnets_list = []
                lines = merge_subnets_text.strip().split('\n')
                for line in lines:
                    parts = re.split('[ ,]+', line.strip())
                    subnets_list.extend([part for part in parts if part])
                if subnets_list:
                    merge_result = merge_subnets(subnets_list)
        elif action == 'ipv6-to-ipv4':
            ipv6 = request.form.get('ipv6', '')
            if ipv6:
                ipv4_result = ipv6_to_ipv4(ipv6)
        elif action == 'ip-info':
            ip_query = request.form.get('ip_query', '')
            if ip_query:
                ip_info_result = get_ip_info(ip_query)
        elif action == 'merge':
            subnets_text = request.form.get('merge_subnets', '')
            if subnets_text:
                # 处理输入的子网列表，支持换行、逗号、空格分隔
                subnets_list = []
                # 先按换行分割
                lines = subnets_text.strip().split('\n')
                for line in lines:
                    # 再按逗号和空格分割
                    parts = re.split('[ ,]+', line.strip())
                    subnets_list.extend([part for part in parts if part])
                if subnets_list:
                    merge_result = merge_subnets(subnets_list)
        elif action == 'range-to-cidr':
            start_ip = request.form.get('start_ip', '')
            end_ip = request.form.get('end_ip', '')
            if start_ip and end_ip:
                range_result = range_to_cidr(start_ip, end_ip)
        elif action == 'check-overlap':
            overlap_subnets_text = request.form.get('overlap_subnets', '')
            if overlap_subnets_text:
                # 处理输入的子网列表，支持换行、逗号、空格分隔
                subnets_list = []
                # 先按换行分割
                lines = overlap_subnets_text.strip().split('\n')
                for line in lines:
                    # 再按逗号和空格分割
                    parts = re.split('[ ,]+', line.strip())
                    subnets_list.extend([part for part in parts if part])
                if subnets_list:
                    overlap_result = check_subnet_overlap(subnets_list)

    # 在渲染模板前，确保所有必要的变量都有合理的默认值
    # 这些默认值只在首次加载或未提交对应表单时使用
    if parent is None:
        parent = request.args.get('parent', "10.0.0.0/8")
    if split is None:
        split = request.args.get('split', "10.21.60.0/23")
    if plan_parent is None:
        plan_parent = request.args.get('plan_parent', "192.168.0.0/16")
    
    # 将 subnet_names 和 host_counts 组合成列表传递给模板
    subnet_requirements = list(zip(subnet_names, host_counts)) if subnet_names and host_counts else []
    return render_template_string(HTML_TEMPLATE, parent=parent, split=split, result=result, plan_result=plan_result, plan_parent=plan_parent, subnet_requirements=subnet_requirements, version=__version__, active_tab=active_tab, ipv4=ipv4, ipv6_result=ipv6_result, ipv6=ipv6, ipv4_result=ipv4_result, ip_query=ip_query, ip_info_result=ip_info_result, merge_result=merge_result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
