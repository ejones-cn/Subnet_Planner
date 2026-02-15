# 测试IP版本不兼容错误处理的脚本
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入需要的模块
from ip_subnet_calculator import split_subnet  # noqa: E402
from i18n import set_language, get_language, _  # noqa: E402

# 测试不同语言下的错误处理
languages = [
    ("zh", "简体中文"),
    ("en", "English"),
    ("zh_tw", "繁体中文"),
    ("ja", "日本語"),
    ("ko", "한국어")
]

print("测试IP版本不兼容错误处理...")
print("=" * 60)

# 测试用例：混合使用IPv4和IPv6地址
parent_cidr = "2001:0db8::/32"  # IPv6
split_cidr = "10.21.50.0/23"   # IPv4

for lang_code, lang_name in languages:
    set_language(lang_code)
    print(f"\n{lang_name} ({lang_code}):")
    print("-" * 40)
    
    # 执行切分操作，预期会产生IP版本不兼容错误
    result = split_subnet(parent_cidr, split_cidr)
    
    if "error" in result:
        error_msg = result["error"]
        print("测试结果: 成功捕获错误")
        print(f"错误信息: {error_msg}")
        
        # 验证错误信息不是原始英文错误
        if "are not of the same version" not in error_msg:
            print("✅ 错误信息已正确翻译")
        else:
            print("❌ 错误信息未被翻译")
    else:
        print("❌ 没有捕获到预期的错误")
        print(f"结果: {result}")

# 恢复默认语言
set_language("zh")
print(f"\n\n恢复默认语言: {get_language()}")

print("\n\n测试完成！")
print("=" * 60)
