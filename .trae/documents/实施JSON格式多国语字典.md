# 实施JSON格式多国语字典

## 实施目标
1. 将当前Python代码中的翻译字典迁移到外部JSON文件
2. 保持现有翻译函数接口不变，确保向后兼容
3. 支持未来轻松扩展18国语言
4. 便于翻译人员使用专业工具编辑

## 实施步骤

### 1. 创建JSON翻译文件

**文件路径**：`f:\trae_projects\Subnet_Planner\translations.json`

**内容**：将现有`TRANSLATIONS`字典转换为JSON格式，结构保持不变

**格式要求**：
- 使用UTF-8编码
- 每个翻译项的语言键值对拆分为多行，提高可读性
- 保留现有注释结构（转换为JSON注释或单独文档）

### 2. 修改i18n.py文件

**主要修改**：
1. 添加JSON文件读取逻辑
2. 移除硬编码的`TRANSLATIONS`字典
3. 保持所有函数接口不变
4. 添加错误处理机制

**关键代码修改**：
```python
import json
import os

# 读取翻译文件
translations_file = os.path.join(os.path.dirname(__file__), 'translations.json')
try:
    with open(translations_file, 'r', encoding='utf-8') as f:
        TRANSLATIONS = json.load(f)
except FileNotFoundError:
    print(f"翻译文件未找到: {translations_file}")
    TRANSLATIONS = {}  # 空字典作为降级方案
except json.JSONDecodeError as e:
    print(f"翻译文件解析错误: {e}")
    TRANSLATIONS = {}  # 空字典作为降级方案
```

### 3. 保持向后兼容性

**关键要点**：
- 翻译函数`_()`接口保持不变
- `set_language()`和`get_language()`函数不变
- `get_supported_languages()`函数需从JSON文件动态生成

**修改`get_supported_languages()`函数**：
```python
def get_supported_languages():
    """
    获取支持的语言列表，从翻译文件动态生成
    
    Returns:
        支持的语言列表，格式为 [(语言代码, 语言名称)]
    """
    # 如果翻译字典为空，返回默认语言列表
    if not TRANSLATIONS:
        return [
            ("zh", "中文"),
            ("en", "English"),
            ("ja", "日本語")
        ]
    
    # 从翻译文件中提取所有唯一语言代码
    all_languages = set()
    for translation in TRANSLATIONS.values():
        all_languages.update(translation.keys())
    
    # 语言代码到语言名称的映射
    lang_names = {
        "zh": "中文",
        "en": "English",
        "ja": "日本語"
        # 未来添加新语言时，只需在此添加映射
    }
    
    # 生成支持的语言列表
    return [(lang, lang_names.get(lang, lang)) for lang in sorted(all_languages)]
```

### 4. 测试验证

**测试场景**：
1. **基本功能测试**：验证翻译函数正常工作
2. **语言切换测试**：验证三种语言（中文、英文、日语）切换正常
3. **带参数翻译测试**：验证`{file_path}`等占位符正常工作
4. **错误处理测试**：验证JSON文件不存在时的降级处理
5. **支持语言列表测试**：验证`get_supported_languages()`返回正确结果

**测试脚本**：
```python
# test_json_translations.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from i18n import set_language, _, get_language, get_supported_languages

# 测试1: 基本翻译功能
print("=== 测试基本翻译功能 ===")
languages = ["zh", "en", "ja"]
for lang in languages:
    set_language(lang)
    print(f"{lang}: error = {_('error')}, ok = {_('ok')}, cancel = {_('cancel')}")

# 测试2: 带参数翻译
print("\n=== 测试带参数翻译 ===")
set_language("zh")
print(_("result_successfully_exported", file_path="test.txt"))
set_language("en")
print(_("result_successfully_exported", file_path="test.txt"))
set_language("ja")
print(_("result_successfully_exported", file_path="test.txt"))

# 测试3: 支持的语言列表
print("\n=== 测试支持的语言列表 ===")
supported_langs = get_supported_languages()
for lang_code, lang_name in supported_langs:
    print(f"{lang_code}: {lang_name}")
```

### 5. 文档更新

**更新内容**：
1. 更新`i18n.py`模块的文档字符串
2. 添加`translations.json`文件的维护说明
3. 提供添加新语言的操作指南
4. 推荐使用的JSON编辑工具

## 预期效果

1. **代码结构更清晰**：翻译数据与代码分离
2. **易于扩展**：添加新语言只需编辑JSON文件
3. **支持专业工具**：翻译人员可以使用JSON编辑器或翻译管理平台
4. **向后兼容**：现有代码无需修改
5. **支持18国语言**：轻松扩展到多种语言

## 风险与应对

1. **JSON文件读取失败**：添加降级处理，确保程序不会崩溃
2. **编码问题**：显式指定UTF-8编码，避免乱码
3. **性能影响**：JSON读取只需加载一次，对性能影响极小
4. **版本控制冲突**：JSON格式结构化清晰，合并冲突风险低

## 实施时间线

1. **准备阶段**：15分钟
   - 创建JSON文件结构
   - 编写i18n.py修改代码

2. **实施阶段**：30分钟
   - 转换现有翻译数据到JSON
   - 修改i18n.py文件

3. **测试阶段**：15分钟
   - 运行测试脚本
   - 验证所有功能正常

4. **文档更新**：10分钟
   - 更新模块文档
   - 编写维护指南

## 后续建议

1. **添加JSON Schema验证**：确保翻译文件格式正确
2. **考虑按模块拆分**：如果翻译数据过大，可按功能模块拆分为多个JSON文件
3. **集成翻译管理平台**：对于18国语言，建议使用专业翻译管理工具
4. **添加自动同步机制**：实现翻译平台与JSON文件的自动同步

## 验收标准

1. ✅ 翻译文件成功创建
2. ✅ i18n.py修改完成
3. ✅ 所有测试用例通过
4. ✅ 现有应用功能正常
5. ✅ 支持语言列表正确生成
6. ✅ 文档更新完成