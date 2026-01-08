def toggle_info_bar_expand(self, event=None):
    """切换信息栏文本显示状态（完整/截断）"""
    if not hasattr(self, '_info_truncated') or not self._info_truncated:
        return
        
    # 切换显示状态
    self._info_currently_expanded = not self._info_currently_expanded
    
    if self._info_currently_expanded:
        # 获取当前字体设置
        from style_manager import get_current_font_settings
        font_family, _ = get_current_font_settings()
        font = tkfont.Font(family=font_family, size=10)
        
        # 获取当前信息栏宽度（保持不变）
        current_width = self.info_bar_frame.winfo_width()
        
        # 实现智能换行，避免标点符号出现在行首
        def smart_wrap_text(text, max_width):
            """智能换行文本，避免标点符号出现在行首，保护英文单词完整性"""
            # 定义中文标点符号，应该出现在行尾
            chinese_end_punct = "，。；：！？、）】》”’}" 
            # 定义英文标点符号，应该出现在行尾
            english_end_punct = ",.;:!?)]}"
            
            # 初始化结果行列表
            lines = []
            current_line = ""
            
            # 遍历文本中的每个字符
            for char in text:
                if char.isspace():
                    if current_line:
                        # 检查添加空格后的宽度
                        test_line = current_line + char
                        test_width = font.measure(test_line)
                        if test_width <= max_width:
                            current_line = test_line
                        else:
                            # 换行，确保行尾没有标点符号
                            lines.append(current_line.rstrip())
                            current_line = char  # 保留当前空格作为新行的开始
                else:
                    # 检查添加当前字符后的宽度
                    test_line = current_line + char
                    test_width = font.measure(test_line)
                    
                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        # 检查当前行是否可以换行
                        if current_line:
                            # 检查当前字符是否是标点符号
                            if char in chinese_end_punct + english_end_punct:
                                # 标点符号应该留在当前行
                                current_line = test_line
                            else:
                                # 检查当前行末尾是否有标点符号
                                if current_line and current_line[-1] in chinese_end_punct + english_end_punct:
                                    # 如果有，将标点符号留在当前行
                                    lines.append(current_line)
                                    current_line = char
                                else:
                                    # 检查当前行是否可以在空格处换行，避免英文单词分割
                                    last_space = current_line.rfind(' ')
                                    if last_space != -1:
                                        # 回溯到最近的空格，将空格前的内容作为一行
                                        lines.append(current_line[:last_space].rstrip())
                                        # 空格后的内容（包括当前字符）作为新行的开始
                                        current_line = current_line[last_space+1:] + char
                                    else:
                                        # 整个行就是一个很长的单词，无法避免分割
                                        lines.append(current_line)
                                        current_line = char
                        else:
                            # 空行直接添加
                            current_line = char
            
            if current_line:
                lines.append(current_line)
            
            return "\n".join(lines)
        
        # 显示完整文本，首行加上图标
        # 先将图标添加到文本开头
        text_with_icon = self._info_icon + self._full_info_text
        
        # 计算最大行宽（不包括额外边距）
        max_line_width = current_width - 34  # 减去左右内边距
        
        # 对带图标的完整文本进行智能换行处理
        final_text = smart_wrap_text(text_with_icon, max_line_width)
        
        # 使用Text组件的方法设置文本
        self.info_label.configure(state="normal")
        self.info_label.delete(1.0, tk.END)
        self.info_label.insert(tk.END, final_text, "justify")
        
        # 根据消息类型设置文本颜色
        if "Error" in self._info_label_style:
            self.info_label.configure(fg="#c62828")  # 错误信息显示红色
        else:
            self.info_label.configure(fg="#424242")  # 正确信息显示灰色
        
        self.info_label.configure(state="disabled")
        
        # 计算需要显示的行数
        line_count = final_text.count('\n') + 1
        self.info_label.configure(height=line_count)
        
        # 强制更新布局，让label计算出正确的高度
        self.root.update_idletasks()
        
        # 获取label的实际高度
        label_height = self.info_label.winfo_reqheight()
        
        # 计算新的信息栏高度，添加额外的上下边距以确保文本完整显示
        # 给最后一行文字留出足够空间，添加4px额外高度
        new_height = label_height + 4  # 额外添加4px高度，确保最后一行完整显示
        new_height = max(new_height, 30)  # 最小高度30px
        
        # 更新信息栏框架高度
        self.info_bar_frame.place_configure(height=new_height)
        
        # 更新spacer高度，确保有足够空间显示
        self.info_spacer.configure(height=new_height)
        
        # 展开时停止自动消失计时
        if hasattr(self, 'info_auto_hide_id') and self.info_auto_hide_id:
            self.root.after_cancel(self.info_auto_hide_id)
            self.info_auto_hide_id = None
    else:
        # 显示截断文本
        # 重新计算截断文本
        def calculate_pixel_width(text):
            from style_manager import get_current_font_settings
            font_family, _ = get_current_font_settings()
            font = tkfont.Font(family=font_family, size=10)
            return font.measure(text)
        
        def truncate_text_by_pixel(text, icon, max_pixel_width):
            icon_width = calculate_pixel_width(icon)
            available_width = max_pixel_width - icon_width
            full_text_with_icon = icon + text
            full_width = calculate_pixel_width(full_text_with_icon)
            
            if full_width <= max_pixel_width:
                return text
            
            ellipsis_width = calculate_pixel_width("...")
            low = 0
            high = len(text)
            best_length = 0
            
            while low <= high:
                mid = (low + high) // 2
                current_text = text[:mid]
                current_width = calculate_pixel_width(current_text)
                
                if current_width <= available_width - ellipsis_width:
                    best_length = mid
                    low = mid + 1
                else:
                    high = mid - 1
            
            truncated = text[:best_length]
            while best_length > 0:
                truncated = text[:best_length]
                truncated_width = calculate_pixel_width(truncated) + ellipsis_width + icon_width
                if truncated_width <= max_pixel_width:
                    return truncated + "..."
                best_length -= 1
            
            return "..."
        
        truncated_text = truncate_text_by_pixel(self._full_info_text, self._info_icon, self._info_max_pixel_width)
        
        # 使用Text组件的方法设置文本
        self.info_label.configure(state="normal")
        self.info_label.delete(1.0, tk.END)
        self.info_label.insert(tk.END, self._info_icon + truncated_text, "justify")
        
        # 根据消息类型设置文本颜色
        if "Error" in self._info_label_style:
            self.info_label.configure(fg="#c62828")  # 错误信息显示红色
        else:
            self.info_label.configure(fg="#424242")  # 正确信息显示灰色
        
        self.info_label.configure(state="disabled")
        
        # 恢复单行显示
        self.info_label.configure(height=1)
        
        # 恢复原始高度，宽度保持不变
        original_height = 30
        self.info_bar_frame.place_configure(height=original_height)
        self.info_spacer.configure(height=original_height)
        
        # 收起时重新开始自动消失计时
        if hasattr(self, 'root'):
            self.info_auto_hide_id = self.root.after(5000, lambda: self.hide_info_bar(from_timer=True))