#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证大网段（如/2前缀）的子网规划功能
"""

from ip_subnet_calculator import suggest_subnet_planning
import time

def test_large_network_planning():
    """测试大网段的子网规划功能"""
    print("=== 测试大网段子网规划功能 ===")
    
    # 测试用例
    test_cases = [
        ("10.21.48.0/2", "超大网段（/2前缀）"),
        ("10.0.0.0/8", "大网段（/8前缀）"),
        ("192.168.0.0/16", "中等网段（/16前缀）"),
    ]
    
    # 子网需求
    required_subnets = [
        {'name': '办公区', 'hosts': 200},
        {'name': '服务器区', 'hosts': 50},
        {'name': '研发部', 'hosts': 100},
    ]
    
    for parent_cidr, description in test_cases:
        print(f"\n--- 测试 {description}: {parent_cidr} ---")
        print(f"子网需求: {required_subnets}")
        
        try:
            start_time = time.time()
            
            # 调用子网规划函数
            plan_result = suggest_subnet_planning(parent_cidr, required_subnets)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if "error" in plan_result:
                print(f"❌ 规划失败: {plan_result['error']}")
            else:
                print(f"✅ 规划成功！")
                print(f"  执行时间: {execution_time:.2f} 秒")
                print(f"  已分配子网数: {len(plan_result['allocated_subnets'])}")
                print(f"  剩余子网数: {len(plan_result['remaining_subnets'])}")
                
                # 打印分配结果
                print("\n分配结果:")
                for subnet in plan_result['allocated_subnets']:
                    print(f"  - {subnet['name']}: {subnet['cidr']} (需求: {subnet['required_hosts']}, 可用: {subnet['available_hosts']})")
                
                if execution_time > 5:
                    print(f"\n⚠️  注意: 执行时间较长 ({execution_time:.2f} 秒)")
                elif execution_time > 1:
                    print(f"\n⚠️  注意: 执行时间略长 ({execution_time:.2f} 秒)")
                else:
                    print(f"\n✅ 执行速度正常 ({execution_time:.2f} 秒)")
                    
        except Exception as e:
            print(f"❌ 测试失败，发生异常: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_large_network_planning()
