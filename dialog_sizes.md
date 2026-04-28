# 对话框大小类别表

## 1. 小型对话框 (400x200)

| 对话框名称    | 功能描述       | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| -------- | ---------- | ------- | ----- | -------- | ------- |
| 添加子网需求   | 添加新的子网需求   | 400x200 | 否     | ComplexDialog | 需要调用 show() |
| 导入数据     | 导入子网数据     | 400x200 | 否     | ComplexDialog | 需要调用 show() |
| 添加网络     | 添加新的网络     | 400x200 | 否     | ComplexDialog | 需要调用 show() |
| 批量迁移     | 批量迁移IP地址   | 400x200 | 否     | ComplexDialog | 需要调用 show() |
| 批量设置过期日期 | 批量设置IP过期日期 | 400x200 | 否     | ComplexDialog | 需要调用 show() |
| 扩展过期日期   | 扩展IP地址过期日期 | 400x200 | 否     | ComplexDialog | 需要调用 show() |

## 2. 中型对话框

| 对话框名称   | 功能描述      | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| ------- | --------- | ------- | ----- | -------- | ------- |
| 网络导入/导出 | 网络数据的导入导出 | 500x370 | 否     | ComplexDialog | 需要调用 show() |
| 解决冲突    | 解决IP冲突     | 400x260 | 否     | ComplexDialog | 需要调用 show() |

## 3. 网络扫描对话框

| 对话框名称  | 功能描述            | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| ------ | --------------- | ------- | ----- | -------- | ------- |
| 自动扫描网络 | 扫描配置对话框         | 440x200 | 否     | create_dialog | 自动显示 |
| 网络扫描进度 | 显示扫描进度和结果       | 800x600 | 是     | create_dialog | 自动显示 |

## 4. 大型对话框 (700x500)

| 对话框名称 | 功能描述        | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| ----- | ----------- | ------- | ----- | -------- | ------- |
| 备份/恢复 | 备份和恢复IPAM数据 | 700x500 | 否     | ComplexDialog | 需要调用 show() |

## 5. 数据表对话框 (800x600)

| 对话框名称  | 功能描述        | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| ------ | ----------- | ------- | ----- | -------- | ------- |
| 导入数据   | 导入子网数据（详细）  | 800x600 | 是     | ComplexDialog | 需要调用 show() |
| IP冲突   | IP地址冲突管理    | 800x600 | 是     | ComplexDialog | 需要调用 show() |
| 可用IP检测 | 检测并显示可用IP地址 | 800x600 | 是     | ComplexDialog | 需要调用 show() |
| 过期IP检测 | 检测并显示过期IP地址 | 800x600 | 是     | ComplexDialog | 需要调用 show() |
| 网络导入数据 | 导入网络数据（详细）  | 800x600 | 是     | ComplexDialog | 需要调用 show() |

## 6. 特殊对话框

| 对话框名称   | 功能描述       | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| ------- | ---------- | ------- | ----- | -------- | ------- |
| 功能调试    | 功能调试面板     | 600x600 | 否     | ComplexDialog | 自动显示（非模态） |
| 分配/保留IP | 分配或保留IP地址  | 420x290 | 否     | create_dialog | 自动显示 |

## 7. IP隐藏信息对话框

| 对话框名称   | 功能描述       | 大小      | 可调整大小 | 创建方式 | 显示方式 |
| ------- | ---------- | ------- | ----- | -------- | ------- |
| IP地址隐藏信息 | 管理IP地址的隐藏敏感信息 | 720x480 | 是     | create_dialog | 自动显示 |
| 隐藏信息编辑  | 添加/编辑隐藏信息记录 | 420x360 | 否     | create_dialog | 自动显示 |

## 8. 系统对话框

| 对话框类型         | 功能描述    | 大小   | 可调整大小 | 创建方式 | 显示方式 |
| ------------- | ------- | ---- | ----- | -------- | ------- |
| InfoDialog    | 信息提示对话框 | 自动调整 | 否     | DialogBase子类 | 需要调用 show() |
| ConfirmDialog | 确认对话框   | 自动调整 | 否     | DialogBase子类 | 需要调用 show() |
| InputDialog   | 输入对话框   | 自动调整 | 否     | DialogBase子类 | 需要调用 show() |
| SelectDialog  | 选择对话框   | 自动调整 | 否     | DialogBase子类 | 需要调用 show() |

## 9. 特例对话框

| 对话框名称   | 功能描述    | 大小    | 创建方式 | 显示方式 |
| ------- | ------- | ------- | -------- | ------- |
| 关于对话框   | 显示关于信息  | 400x380 | ComplexDialog | 需要调用 show() |
| 扫码捐赠对话框 | 显示捐赠二维码 | 420x420 | ComplexDialog | 需要调用 show() |

## 设计建议

1. **统一尺寸规范**：
   - 小型对话框：400x200，适用于简单的输入和操作
   - 中型对话框：500x300~370，适用于中等复杂度的操作
   - 大型对话框：700x500，适用于需要更多控件的操作
   - 数据表对话框：800x600，适用于显示大量数据的操作
2. **可调整性**：
   - 数据表类对话框建议设置为可调整大小，以便用户根据需要查看更多数据
   - **最小尺寸限制**：所有可调整大小的对话框均设置了最小尺寸限制，防止用户将对话框缩小到内容无法正常显示
3. **特殊情况处理**：
   - 关于和捐赠对话框使用固定尺寸
   - 分配/保留IP对话框使用420x290的尺寸（根据操作类型动态调整高度）
4. **一致性**：
   - 所有对话框使用统一的创建方法和布局风格
   - 标签文本统一添加冒号，保持视觉一致性
   - 按钮布局和样式保持一致
5. **ESC键支持**：
   - 使用 `ComplexDialog` 或 `DialogBase` 子类创建的对话框自动获得 ESC 键支持（通过 DialogBase）
   - 使用 `create_dialog` 创建的对话框需要手动绑定 ESC 键

## 显示方式说明

### 模态对话框 (modal=True)
- **ComplexDialog**：创建后不会自动显示，必须调用 `dialog.show()` 方法才能显示
- **create_dialog**：创建后会自动显示

### 非模态对话框 (modal=False)
- **ComplexDialog**：创建后会自动显示（用于功能调试面板等需要一直显示的面板）

## 维护说明

- 当添加新对话框时，请参考此规范选择合适的尺寸和创建方式
- 优先使用 `ComplexDialog` 创建对话框，以自动获得 ESC 键支持和标准布局
- 仅在需要高度定制化布局或特殊生命周期管理时使用 `create_dialog`
- 使用 `ComplexDialog` 创建模态对话框时，务必在创建完成后调用 `dialog.show()` 方法
- 如有特殊需求需要调整对话框尺寸，请在本文件中更新记录
- 定期检查对话框尺寸是否符合当前规范，确保界面一致性

## 代码映射表

| 对话框名称    | 代码位置 (行号) | 实际创建方式 | 说明 |
| -------- | ----------- | -------- | ---- |
| 添加子网需求   | windows_app.py:3722 | ComplexDialog(self.root, _, 400, 200) | 标准小型对话框 |
| 导入数据     | windows_app.py:3969 | ComplexDialog(self.root, _, 400, 200) | 导入选项对话框 |
| 添加网络     | windows_app.py:13708 | ComplexDialog(self.root, _, 400, 200) | 标准小型对话框 |
| 批量迁移     | windows_app.py:17556 | ComplexDialog(self.root, _, 400, 200) | 标准小型对话框 |
| 批量设置过期日期 | windows_app.py:17633 | ComplexDialog(self.root, _, 400, 200) | 标准小型对话框 |
| 扩展过期日期   | windows_app.py:17338 | ComplexDialog(parent_dialog.dialog, _, 400, 200) | 子对话框，需传入parent |
| 网络导入/导出 | windows_app.py:12353 | ComplexDialog(self.root, _, 500, 370) | 尺寸调整为500x370 |
| 解决冲突    | windows_app.py:12101 | ComplexDialog(parent_dialog.dialog, _, 400, 260) | 子对话框，尺寸400x260 |
| 自动扫描网络 | windows_app.py:12978 | create_dialog(_, 440, 200) | 使用create_dialog |
| 网络扫描进度 | windows_app.py:13243 | create_dialog(_, 800, 600, resizable=True) | 可调整大小 |
| 备份/恢复 | windows_app.py:12723 | ComplexDialog(self.root, _, 700, 500) | 标准大型对话框 |
| 导入数据（详细） | windows_app.py:4180, 12492 | ComplexDialog(self.root, _, 800, 600, resizable=True) | 数据表对话框 |
| IP冲突     | windows_app.py:11950 | ComplexDialog(self.root, _, 800, 600, resizable=True) | 数据表对话框 |
| 可用IP检测 | windows_app.py:16765 | ComplexDialog(self.root, _, 800, 600, resizable=True) | 数据表对话框 |
| 过期IP检测 | windows_app.py:17053 | ComplexDialog(self.root, _, 800, 600, resizable=True) | 数据表对话框 |
| 功能调试    | windows_app.py:8476 | ComplexDialog(self.root, _, 600, 600, modal=False) | 非模态对话框 |
| 分配/保留IP | windows_app.py:17740 | create_dialog(title, 420, height) | 高度根据操作类型动态调整(260/290) |
| IP地址隐藏信息 | windows_app.py:8878 | create_dialog(_, 720, 480) | 使用create_dialog |
| 隐藏信息编辑  | windows_app.py:9091 | create_dialog(title, 420, 360) | 子对话框 |
| 关于对话框   | windows_app.py:10456 | ComplexDialog(self.root, _, 400, 380) | 特例对话框 |
| 扫码捐赠对话框 | windows_app.py:10594 | ComplexDialog(self.root, _, 420, 420) | 特例对话框 |
| InfoDialog   | windows_app.py:4528, 4551, 4556, 4561 | InfoDialog(self.root, title, message, type) | 系统对话框 |
| ConfirmDialog | windows_app.py:4532, 4617, 13818 | ConfirmDialog(self.root, title, message, yes, no) | 系统对话框 |
