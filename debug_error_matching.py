# 调试IP版本不兼容错误匹配的脚本

# 模拟错误信息
error_msg = "10.21.50.0/23 and 2001:db8::/32 are not of the same version"

# 测试我们的匹配函数
match_func = lambda msg: "are not of the same version" in msg
print(f"错误信息: {error_msg}")
print(f"匹配结果: {match_func(error_msg)}")
print(f"'are not of the same version' in error_msg: {'are not of the same version' in error_msg}")
print(f"完整匹配函数调用结果: {match_func(error_msg)}")

# 调试精确的字符串匹配
substring = "are not of the same version"
print(f"\n子字符串 '{substring}' 在错误信息中的位置: {error_msg.find(substring)}")
print(f"子字符串长度: {len(substring)}")
print(f"错误信息长度: {len(error_msg)}")

# 测试其他可能的匹配方式
print(f"\n使用字符串包含: {'version' in error_msg}")
print(f"使用正则表达式: {bool(re.search(r"are not of the same version", error_msg))}")

# 导入正则表达式模块
import re

# 测试我们在代码中使用的完整错误模式列表
print("\n\n测试完整的错误模式列表:")
error_patterns = [
    # ... 其他错误模式 ...
    (lambda msg: "are not of the same version" in msg, 'ip_versions_not_compatible'),
    # ... 其他错误模式 ...
    (lambda msg: "IPv6" in msg or ("colon" in msg.lower() and "hex" in msg.lower()), 'invalid_ipv6_format'),
]

# 模拟错误处理函数的匹配过程
print("\n模拟错误处理函数的匹配过程:")
for match_func, translation_key in error_patterns:
    if match_func(error_msg):
        print(f"匹配到错误模式: {translation_key}")
        break
else:
    print("没有匹配到任何错误模式")

# 检查是否有其他匹配的模式
print("\n检查所有可能匹配的模式:")
for match_func, translation_key in error_patterns:
    if match_func(error_msg):
        print(f"匹配到: {translation_key}")
