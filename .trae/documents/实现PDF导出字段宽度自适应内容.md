# 实现PDF导出字段宽度自适应内容

## 问题分析
当前PDF导出的字段宽度存在以下问题：
1. 当没有指定列宽时，使用平均分配列宽
2. 当指定了列宽时，直接使用指定的宽度，没有考虑内容长度
3. 字符串格式的列宽配置被解释为比例，而不是自适应内容
4. 导致某些列内容显示不完全，而某些列又太空旷

## 解决方案
实现基于内容自动调整列宽的功能，具体步骤如下：

### 1. 计算每列内容的最大宽度
- 遍历表格中所有单元格，计算每列中最长内容的宽度
- 使用reportlab的`stringWidth`函数获取文本宽度
- 考虑不同字体和字号对宽度的影响

### 2. 根据内容宽度分配列宽
- 计算每列内容的相对宽度比例
- 根据相对比例分配页面可用宽度
- 确保每列有最小宽度，保证表格美观

### 3. 实现自适应列宽逻辑
- 添加新的列宽处理选项：自适应内容
- 优先使用内容宽度，同时限制最大宽度
- 确保总宽度不超过页面宽度

### 4. 优化现有列宽处理逻辑
- 保留现有配置选项，添加自适应选项
- 确保向后兼容
- 添加调试信息，方便问题定位

## 具体修改点

### 1. 主表格列宽处理
- 文件: `windows_app.py`
- 方法: `_export_data()`
- 位置: 第2737-2793行

### 2. 剩余表格列宽处理
- 文件: `windows_app.py`
- 方法: `_export_data()`
- 位置: 第2857-2946行

### 3. 添加辅助函数
- 添加计算文本宽度的函数
- 添加计算自适应列宽的函数

## 技术实现

### 1. 导入必要模块
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
```

### 2. 实现自适应列宽计算
```python
def _calculate_auto_col_widths(self, table_data, table_cols, table_width, font_name, font_size):
    """根据内容计算自适应列宽"""
    # 初始化每列的最大宽度
    max_col_widths = [0] * table_cols
    
    # 遍历所有行和列，计算每列的最大宽度
    for row in table_data:
        for col_idx, cell in enumerate(row):
            # 获取单元格文本内容
            text = cell.text if hasattr(cell, 'text') else str(cell)
            # 计算文本宽度
            text_width = stringWidth(text, font_name, font_size)
            # 更新该列的最大宽度
            if text_width > max_col_widths[col_idx]:
                max_col_widths[col_idx] = text_width
    
    # 添加内边距
    max_col_widths = [width + 20 for width in max_col_widths]  # 20为左右内边距之和
    
    # 计算总宽度
    total_width = sum(max_col_widths)
    
    # 如果总宽度超过页面宽度，按比例缩放
    if total_width > table_width:
        scale_factor = table_width / total_width
        max_col_widths = [width * scale_factor for width in max_col_widths]
    
    # 确保每列有最小宽度
    min_width = table_width / table_cols * 0.5  # 最小宽度为平均宽度的一半
    max_col_widths = [max(width, min_width) for width in max_col_widths]
    
    return max_col_widths
```

### 3. 集成到现有代码
- 在创建Table对象之前调用自适应列宽计算函数
- 根据计算结果设置列宽
- 保留现有配置选项，添加自适应选项

## 预期效果
1. 每列宽度根据内容自动调整
2. 内容较长的列分配更多宽度
3. 内容较短的列分配较少宽度
4. 保持表格的整体美观
5. 支持现有配置选项

## 测试计划
1. 测试不同数据量的PDF导出
2. 测试不同长度内容的PDF导出
3. 测试混合数据类型的PDF导出
4. 测试不同字体和字号的PDF导出
5. 验证表格整体美观度和可读性

## 向后兼容性
- 保持现有配置选项不变
- 默认使用自适应列宽
- 支持手动指定列宽配置
- 支持字符串格式的列宽比例配置