#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试format_large_number函数的修复
"""

# 导入要测试的函数
from ip_subnet_calculator import format_large_number


def test_format_large_number():
    """测试format_large_number函数的各种情况"""
    print("=== 测试format_large_number函数 ===")
    
    # 测试用例
    test_cases = [
        # (输入数值, 预期输出应该包含...),
        (1000000, "=1.00e+6"),  # 刚好100万，应该显示=1.00e+6
        (1000001, "≈1.00e+6"),  # 超过100万，应该显示≈1.00e+6
        (1234567, "≈1.23e+6"),  # 123万，应该显示≈1.23e+6
        (1234999, "≈1.23e+6"),  # 123.4999万，应该显示≈1.23e+6
        (1235000, "≈1.23e+6"),  # 123.5万，应该显示≈1.23e+6
        (1000000000, "=1.00e+9"),  # 10亿，应该显示=1.00e+9
        (1234567890, "≈1.23e+9"),  # 12.3456789亿，应该显示≈1.23e+9
        (999999, "999,999"),  # 小于100万，应该使用千位分隔符
        (0, "0"),  # 0，应该显示0
        (123, "123"),  # 小数字，应该直接显示
        ("1000000", "=1.00e+6"),  # 字符串输入，应该能正确转换
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected_contains) in enumerate(test_cases):
        result = format_large_number(input_val)
        if expected_contains in result:
            print(f"✓ 测试 {i + 1}: 输入 {input_val} → 输出 {result} (预期包含 {expected_contains})")
            passed += 1
        else:
            print(f"✗ 测试 {i + 1}: 输入 {input_val} → 输出 {result} (预期包含 {expected_contains})")
            failed += 1
    
    print("\n=== 测试结果 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总测试用例: {len(test_cases)}")
    
    return failed == 0


if __name__ == "__main__":
    success = test_format_large_number()
    if success:
        print("\n🎉 所有测试通过！format_large_number函数修复成功！")
    else:
        print("\n❌ 测试失败！format_large_number函数还需要进一步修复！")
        exit(1)
