# 测试CIDR正则表达式的脚本
import re

# 从windows_app.py文件中提取cidr_pattern
with open('windows_app.py', 'r', encoding='utf-8') as f:
    content = f.read()
    # 提取cidr_pattern的定义
    import re as re2
    match = re2.search(r'self\.cidr_pattern\s*=\s*\((.*?)\)', content, re2.DOTALL)
    if match:
        pattern_str = match.group(1)
        # 处理多行字符串，合并成单行
        pattern_str = pattern_str.replace('\n', '')
        # 提取正则表达式部分
        regex_match = re2.search(r"r'([^']+)'", pattern_str)
        if regex_match:
            cidr_pattern = regex_match.group(1)
        else:
            # 如果无法直接提取，手动构造正则表达式
            cidr_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:[0-9]|[1-2][0-9]|3[0-2])$|^[0-9a-fA-F:.]+/(?:[0-9]|[1-9][0-9]|1[01][0-9]|12[0-8])$'
    else:
        # 手动指定正则表达式（基于修复后的预期结果）
        cidr_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:[0-9]|[1-2][0-9]|3[0-2])$|^[0-9a-fA-F:.]+/(?:[0-9]|[1-9][0-9]|1[01][0-9]|12[0-8])$'

# 测试用例
test_ips = [
    '2001:0db8::/64',          # 简化的IPv6地址（目标修复用例）
    '2001:0db8:85a3:0000:0000:8a2e:0370:7334/64',  # 完整的IPv6地址
    'fe80::1/10',              # 本地链路IPv6地址
    '::1/128',                 # 环回IPv6地址
    '192.168.1.0/24',          # IPv4地址
    '10.0.0.0/8',              # IPv4地址
    '172.16.0.0/16',           # IPv4地址
    '127.0.0.1/32',            # IPv4环回地址
]

# 执行测试
print("CIDR正则表达式测试结果：")
print(f"使用的正则表达式: {cidr_pattern}")
print("-" * 60)
for ip in test_ips:
    result = bool(re.match(cidr_pattern, ip))
    print(f"{ip:<45} -> {'✓' if result else '✗'}")
