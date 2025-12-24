# 我将重新设计子网合并列表区域的布局
# 使用grid布局来确保按钮固定在右下角

# 左侧上方：子网合并列表 - 使用grid布局
subnet_frame = ttk.LabelFrame(left_frame, text="子网合并列表", padding="10")
subnet_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

# 配置左侧面板的grid布局
left_frame.grid_rowconfigure(0, weight=1)  # 子网列表面板随窗体变化
left_frame.grid_rowconfigure(1, weight=0)  # IP地址范围面板固定高度
left_frame.grid_columnconfigure(0, weight=1)  # 第一列占满宽度

# 配置子网合并列表面板的grid布局
subnet_frame.grid_columnconfigure(0, weight=1)  # 文本框列
subnet_frame.grid_columnconfigure(1, weight=0)  # 滚动条列
subnet_frame.grid_rowconfigure(0, weight=1)  # 文本框行
subnet_frame.grid_rowconfigure(1, weight=0)  # 按钮行

# 子网合并列表输入文本框
self.subnet_merge_text = tk.Text(subnet_frame, height=8, width=25, font=('微软雅黑', 10))
self.subnet_merge_text.grid(row=0, column=0, sticky="nsew")

# 添加垂直滚动条
subnet_merge_scrollbar = ttk.Scrollbar(subnet_frame, orient=tk.VERTICAL, command=self.subnet_merge_text.yview)
subnet_merge_scrollbar.grid(row=0, column=1, sticky="ns")

# 配置文本框使用滚动条
self.subnet_merge_text.configure(yscrollcommand=subnet_merge_scrollbar.set)

# 插入初始文本
self.subnet_merge_text.insert(tk.END, "192.168.0.0/24\n192.168.1.0/24\n192.168.2.0/24")

# 子网合并按钮 - 固定在右下角
self.merge_btn = ttk.Button(subnet_frame, text="合并子网", command=self.execute_merge_subnets)
self.merge_btn.grid(row=1, column=0, columnspan=2, sticky="e", pady=(5, 0))