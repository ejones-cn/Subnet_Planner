#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPAM 多个记录测试用例
测试同一个 IP 多个记录的处理逻辑
"""

import unittest
import os
import tempfile
from ipam_sqlite import IPAMSQLite


class TestIPAMMultipleRecords(unittest.TestCase):
    """测试 IPAM 多个记录处理逻辑"""
    
    def setUp(self):
        """设置测试环境"""
        # 创建临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.ipam = IPAMSQLite(self.temp_db.name)
        
        # 添加测试网络
        self.network = "192.168.1.0/24"
        self.ipam.add_network(self.network, "测试网络")
    
    def tearDown(self):
        """清理测试环境"""
        # 删除临时数据库文件
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_allocate_ip_with_multiple_records(self):
        """测试分配 IP 地址，处理多个记录的情况"""
        ip_address = "192.168.1.100"
        
        # 第一次分配
        result1, msg1 = self.ipam.allocate_ip(self.network, ip_address, "host1", "测试主机1")
        self.assertTrue(result1, f"第一次分配失败: {msg1}")
        
        # 释放 IP
        result_release, msg_release = self.ipam.release_ip(ip_address)
        self.assertTrue(result_release, f"释放失败: {msg_release}")
        
        # 第二次分配（应该使用同一个记录）
        result2, msg2 = self.ipam.allocate_ip(self.network, ip_address, "host2", "测试主机2")
        self.assertTrue(result2, f"第二次分配失败: {msg2}")
        
        # 检查记录数
        records = self.ipam.get_all_ip_records(ip_address)
        self.assertEqual(len(records), 1, "应该只有一个记录")
    
    def test_release_ip_with_different_strategies(self):
        """测试不同的释放策略"""
        ip_address = "192.168.1.101"
        
        # 分配 IP
        result1, msg1 = self.ipam.allocate_ip(self.network, ip_address, "host1", "测试主机1")
        self.assertTrue(result1, f"分配失败: {msg1}")
        
        # 释放 IP（使用 all 策略）
        result_release, msg_release = self.ipam.release_ip(ip_address, "all")
        self.assertTrue(result_release, f"释放失败: {msg_release}")
        
        # 检查状态
        status = self.ipam.get_ip_status(ip_address)
        self.assertEqual(status, "available", "IP 应该变为可用状态")
    
    def test_reserve_ip_with_multiple_records(self):
        """测试保留 IP 地址，处理多个记录的情况"""
        ip_address = "192.168.1.102"
        
        # 第一次保留
        result1, msg1 = self.ipam.reserve_ip(self.network, ip_address, "保留描述1")
        self.assertTrue(result1, f"第一次保留失败: {msg1}")
        
        # 释放 IP
        result_release, msg_release = self.ipam.release_ip(ip_address)
        self.assertTrue(result_release, f"释放失败: {msg_release}")
        
        # 第二次保留（应该使用同一个记录）
        result2, msg2 = self.ipam.reserve_ip(self.network, ip_address, "保留描述2")
        self.assertTrue(result2, f"第二次保留失败: {msg2}")
        
        # 检查记录数
        records = self.ipam.get_all_ip_records(ip_address)
        self.assertEqual(len(records), 1, "应该只有一个记录")
    
    def test_ip_conflict_detection(self):
        """测试 IP 地址冲突检测"""
        ip_address = "192.168.1.103"
        
        # 这里需要模拟多个记录的情况
        # 由于数据库结构中 ip_address 字段是唯一的，我们需要通过其他方式测试
        # 这里我们测试冲突检测函数的基本功能
        conflicts = self.ipam.check_ip_conflicts(ip_address)
        self.assertEqual(len(conflicts), 0, "初始状态应该没有冲突")
    
    def test_ip_record_management(self):
        """测试 IP 地址记录管理"""
        ip_address = "192.168.1.104"
        
        # 分配 IP
        result, msg = self.ipam.allocate_ip(self.network, ip_address, "host1", "测试主机")
        self.assertTrue(result, f"分配失败: {msg}")
        
        # 获取所有记录
        records = self.ipam.get_all_ip_records(ip_address)
        self.assertEqual(len(records), 1, "应该只有一个记录")
        
        # 更新记录
        record_id = records[0]['id']
        result_update, msg_update = self.ipam.update_ip_record(record_id, "host_updated", "更新后的描述")
        self.assertTrue(result_update, f"更新失败: {msg_update}")
        
        # 检查更新结果
        updated_records = self.ipam.get_all_ip_records(ip_address)
        self.assertEqual(updated_records[0]['hostname'], "host_updated", "主机名应该已更新")
        self.assertEqual(updated_records[0]['description'], "更新后的描述", "描述应该已更新")


if __name__ == '__main__':
    unittest.main()
