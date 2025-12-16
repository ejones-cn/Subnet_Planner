# 修复PDF导出异常问题

## 问题分析
根据代码分析，PDF导出时出现'>' not supported between instances of 'NoneType' and 'NoneType'错误的原因是：

1. 在`_export_data`方法中，列宽处理逻辑存在缺陷
2. 当`main_table_cols`或`remaining_table_cols`包含None值时，没有被正确处理
3. 列宽处理逻辑存在重复获取和覆盖变量的问题
4. 在比较列宽之前，没有确保所有列宽都是有效的数字

## 修复方案

### 1. 修复主表格列宽处理逻辑
- 统一列宽获取和处理流程
- 确保在所有情况下都不会出现None值
- 移除重复的列宽获取逻辑

### 2. 修复剩余表格列宽处理逻辑
- 应用相同的修复逻辑到剩余表格
- 确保所有列宽都是有效的数字

### 3. 强化列宽验证
- 在所有列宽处理步骤中添加None值检查
- 确保只有有效的数字值被用于PDF生成

## 具体修改点

1. **文件**: `windows_app.py`
2. **方法**: `_export_data`
3. **修改范围**: 
   - 第2538-2568行：主表格列宽处理
   - 第2666-2696行：剩余表格列宽处理

## 修复代码

### 主表格列宽处理修复
```python
# 使用指定的列宽或默认列宽
col_widths = data_source.get("main_table_cols")
if not col_widths or len(col_widths) != table_cols:
    if len(main_headers) == 2:  # 键值对格式
        col_widths = [table_width * 0.3, table_width * 0.7]
    else:
        # 默认平均分配列宽
        col_widths = [table_width / table_cols] * table_cols
else:
    # 确保所有列宽值都是有效的数字
    processed_col_widths = []
    for width in col_widths:
        try:
            # 尝试将宽度转换为数字
            numeric_width = float(width) if width is not None else table_width / table_cols
            if numeric_width <= 0:
                numeric_width = table_width / table_cols
            processed_col_widths.append(numeric_width)
        except (ValueError, TypeError):
            # 如果转换失败，使用默认宽度
            processed_col_widths.append(table_width / table_cols)
    
    col_widths = processed_col_widths
    # 确保列宽数组长度与表格列数一致
    if len(col_widths) != table_cols:
        col_widths = [table_width / table_cols] * table_cols
```

### 剩余表格列宽处理修复
```python
# 使用指定的列宽或默认列宽
col_widths = data_source.get("remaining_table_cols")
if not col_widths or len(col_widths) != table_cols:
    # 默认平均分配列宽
    col_widths = [table_width / table_cols] * table_cols
else:
    # 确保所有列宽值都是有效的数字
    processed_col_widths = []
    for width in col_widths:
        try:
            # 尝试将宽度转换为数字
            numeric_width = float(width) if width is not None else table_width / table_cols
            if numeric_width <= 0:
                numeric_width = table_width / table_cols
            processed_col_widths.append(numeric_width)
        except (ValueError, TypeError):
            # 如果转换失败，使用默认宽度
            processed_col_widths.append(table_width / table_cols)
    
    col_widths = processed_col_widths
    # 确保列宽数组长度与表格列数一致
    if len(col_widths) != table_cols:
        col_widths = [table_width / table_cols] * table_cols
```

## 预期结果
修复后，PDF导出功能应该能够正确处理包含None值的列宽配置，不会出现比较None值的错误，从而成功生成PDF文件。