# 测试翻译功能的脚本
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入翻译模块
from i18n import _, set_language, get_language, translate

# 测试翻译功能
print("测试翻译功能...")

# 检查当前语言
current_lang = get_language()
print(f"当前语言: {current_lang}")

# 测试几个常用翻译键
keys_to_test = [
    "app_name",
    "subnet_planning",
    "subnet_split",
    "advanced_tools",
    "parent_network_settings",
    "requirements_pool",
    "subnet_requirements",
    "execute_planning",
    "export_planning"
]

print("\n翻译测试结果:")
print("-" * 40)

for key in keys_to_test:
    translated = _(key)
    print(f"{key:<30} -> {translated}")
    # 验证翻译结果不是键本身
    if translated == key:
        print(f"  ⚠️  警告: {key} 没有被正确翻译")

# 测试不同语言
print("\n\n测试不同语言:")
print("-" * 40)

languages = [
    ("zh", "简体中文"),
    ("en", "English"),
    ("zh_tw", "繁体中文"),
    ("ja", "日本語"),
    ("ko", "한국어")
]

for lang_code, lang_name in languages:
    set_language(lang_code)
    print(f"\n{lang_name} ({lang_code}):")
    for key in ["app_name", "subnet_planning", "execute_planning"]:
        translated = _(key)
        print(f"  {key:<20} -> {translated}")

# 恢复默认语言
set_language("zh")
print(f"\n\n恢复默认语言: {get_language()}")

print("\n\n翻译功能测试完成！")
print("如果所有翻译都显示正常，说明翻译功能已恢复。")
