# 对话框创建规范

## 1. 统一使用 create_dialog 方法

所有新创建的对话框必须使用 `create_dialog` 方法，禁止直接使用 `tk.Toplevel` 创建对话框。

### 使用语法
```python
dialog = self.create_dialog(title, width, height, resizable=False, modal=True, parent=None)
```

### 参数说明
- `title`：对话框标题
- `width`：对话框宽度
- `height`：对话框高度
- `resizable`：是否允许调整大小（默认为 False）
- `modal`：是否为模态对话框（默认为 True）
- `parent`：父窗口对象，如果为 None 则使用主窗口

## 2. 子对话框居中规则

- **从主窗口打开的对话框**：不传入 `parent` 参数，默认居中在主窗口
- **从其他对话框打开的子对话框**：必须传入父对话框作为 `parent` 参数，使子对话框居中在父对话框上

### 示例代码
```python
# 从主窗口打开对话框
dialog = self.create_dialog(_('add_network'), 400, 200)

# 从其他对话框打开子对话框
child_dialog = self.create_dialog(_('resolve_conflict'), 500, 350, parent=parent_dialog)
```

## 3. 特殊情况处理

对于需要自定义父窗口的对话框，应使用 `create_dialog` 方法并传入 `parent` 参数。

## 4. 对话框设计原则

- **大小合理**：对话框大小应根据内容合理设置
- **风格一致**：使用 ttk 组件，保持与应用程序整体风格一致
- **用户体验**：确保对话框内容清晰易读，操作流程直观

## 5. 多国语支持

- 本项目已支持多国语，注意开发时使用翻译键及字典，避免直接使用字符串。

## 5. 禁止事项

- 禁止直接使用 `tk.Toplevel` 创建对话框
- 禁止手动设置对话框位置（由 `create_dialog` 方法自动处理）
- 禁止在对话框创建过程中产生屏幕左上角闪现的问题

## 6. 最佳实践

- 当创建从其他对话框打开的子对话框时，总是传入父对话框作为 `parent` 参数
- 保持对话框大小与内容匹配，避免过大或过小
- 使用有意义的标题，清晰表达对话框的目的