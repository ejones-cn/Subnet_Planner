# 分析问题：
# 1. self.split_frame包含两个主要部分：input_history_frame（上部）和result_frame（下部）
# 2. input_history_frame使用grid布局，result_frame使用pack布局
# 3. 当切换Notebook标签页时，会触发on_configure事件，导致整个split_frame布局重新计算
# 4. 混合使用grid和pack布局是导致上方面板宽度变化的根本原因

# 解决方案：
# 修改split_frame的布局，确保两个主要部分都使用pack布局，避免布局冲突

# 具体修改：
# 1. 确保input_history_frame使用pack布局，只水平填充，不垂直扩展
# 2. 确保result_frame使用pack布局，填充剩余空间
# 3. 移除可能导致布局重新计算的不必要代码