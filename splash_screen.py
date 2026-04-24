import tkinter as tk
import random
from version import __version__

class SplashScreen:
    def __init__(self, parent=None):
        self.parent = parent
        self.splash = None
        self.status_text = None
        self.loading_text = None
        self.canvas = None
        self.stars = []
        self.star_offsets = []
        self.star_speed = []
        self.star_direction = []
        self.star_velocities = []  # 新增：用于存储星星速度
        self.star_count = 40
        self.mouse_x, self.mouse_y = -1000, -1000
        self._loading_text_anim_id = None
        self._star_anim_id = None
        self.update_queue = []
        self.loaded_modules = 0
        self.ip_labels = []
        
        self._create_splash()
    
    def _create_splash(self):
        self.splash = tk.Toplevel(self.parent)
        self.splash.title("")
        self.splash.geometry("800x450")
        self.splash.resizable(False, False)
        self.splash.overrideredirect(True)
        
        # 计算居中位置
        if self.parent:
            parent_x = self.parent.winfo_x()
            parent_y = self.parent.winfo_y()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            x = parent_x + (parent_width - 800) // 2
            y = parent_y + (parent_height - 450) // 2
        else:
            screen_width = self.splash.winfo_screenwidth()
            screen_height = self.splash.winfo_screenheight()
            x = (screen_width - 800) // 2
            y = (screen_height - 450) // 2
        
        self.splash.geometry(f"+{x}+{y}")
        
        main_frame = tk.Frame(self.splash, bg='#F1F5F9')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = tk.Frame(main_frame, bg='#F1F5F9', width=227, height=390)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=40, pady=30)
        left_frame.pack_propagate(False)  # 禁止Frame根据内容自动调整大小
        
        title_label = tk.Label(left_frame, text="子网规划师", font=('微软雅黑', 32, 'bold'), bg='#F1F5F9', fg='#1E293B')
        title_label.pack(pady=(0, 10))
        
        version_label = tk.Label(left_frame, text=f"v{__version__}", font=('微软雅黑', 14), bg='#F1F5F9', fg='#64748B')
        version_label.pack(pady=(0, 30))
        
        status_frame = tk.Frame(left_frame, bg='#F1F5F9')
        status_frame.pack(fill=tk.X)
        
        self.status_text = tk.Label(status_frame, text="正在加载资源...", font=('微软雅黑', 12), bg='#F1F5F9', fg='#475569')
        self.status_text.pack(anchor=tk.W, pady=(0, 5))
        
        self.loading_text = tk.Label(status_frame, text="加载中", font=('微软雅黑', 12), bg='#F1F5F9', fg='#0EA5E9')
        self.loading_text.pack(anchor=tk.W)
        
        self.right_frame = tk.Frame(main_frame, bg='#0F172A')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self._init_stars()
        self._start_animations()
    
    def _init_stars(self):
        # 调整画布比例为1:1.1（长方形）
        canvas_size = 450 * 493  # 长方形画布
        self.canvas = tk.Canvas(self.right_frame, width=canvas_size, height=canvas_size, bg='#0F172A', highlightthickness=0)
        self.canvas.pack(fill=tk.NONE, expand=False, padx=10, pady=10)  # 不填充，保持原大小
        
        for _ in range(self.star_count):
            x = random.randint(20, 473)  # 适应493宽度
            y = random.randint(20, 430)   # 适应450高度
            self.stars.append((x, y))
            self.star_offsets.append((0, 0))
            self.star_speed.append(random.uniform(0.3, 0.8))
            self.star_direction.append((random.uniform(-1, 1), random.uniform(-1, 1)))
            self.star_velocities.append((0, 0))  # 初始化速度为0
        
        self.mouse_x, self.mouse_y = -1000, -1000
        
        def on_mouse_move(event):
            self.mouse_x = event.x
            self.mouse_y = event.y

        def on_mouse_leave(event):
            # 鼠标离开画布，不再吸引星星
            self.mouse_x = -1000
            self.mouse_y = -1000
        
        self.canvas.bind('<Motion>', on_mouse_move)
        self.canvas.bind('<Leave>', on_mouse_leave)
        
        density_radius = 120
        star_densities = []
        
        for i in range(self.star_count):
            x, y = self.stars[i]
            count = 0
            for j in range(self.star_count):
                if i != j:
                    x2, y2 = self.stars[j]
                    distance = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
                    if distance < density_radius:
                        count += 1
            star_densities.append((i, count))
        
        star_densities.sort(key=lambda x: x[1])
        
        total_stars = len(star_densities)
        index_85 = int(total_stars * 0.85)
        index_70 = int(total_stars * 0.70)
        index_55 = int(total_stars * 0.55)
        index_40 = int(total_stars * 0.40)
        index_25 = int(total_stars * 0.25)
        
        self.ip_labels = [
            ('10.0.0.0/8', star_densities[-1][0]),         # IPv4最密集区域
            ('172.16.0.0/12', star_densities[index_85][0]), # IPv4较密集区域
            ('192.168.0.0/16', star_densities[index_70][0]),# IPv4中等密度区域
            ('100.64.0.0/10', star_densities[index_55][0]), # IPv4较松散区域
            ('2001:db8:85a3::/64', star_densities[index_40][0]), # IPv6全球单播地址
            ('2001:db8::/32', star_densities[index_25][0]), # IPv6文档示例地址
        ]
    
    def _start_animations(self):
        self._animate_loading_text()
        self._update_star_animation()
    
    def _stop_animations(self):
        if self._loading_text_anim_id and self.splash:
            try:
                self.splash.after_cancel(self._loading_text_anim_id)
            except Exception:
                pass
            self._loading_text_anim_id = None
        
        if hasattr(self, '_star_anim_id') and self._star_anim_id and self.splash:
            try:
                self.splash.after_cancel(self._star_anim_id)
            except Exception:
                pass
            self._star_anim_id = None
        
        if hasattr(self, 'canvas') and self.canvas:
            try:
                self.canvas.destroy()
                self.canvas = None
            except Exception:
                pass
    
    def _animate_loading_text(self):
        if not self.loading_text or not self.splash:
            return
        
        try:
            current_text = self.loading_text.cget('text')
            if current_text.endswith('...'):
                new_text = "加载中"
            else:
                new_text = current_text + '.'
            
            if not self.splash:
                return
                
            self.loading_text.config(text=new_text)
            self._loading_text_anim_id = self.splash.after(500, self._animate_loading_text)
        except Exception as e:
            print(f"Error in loading text animation: {str(e)}")
    
    def _update_star_animation(self):
        if not self.canvas or not self.splash:
            return
        
        try:
            self.canvas.delete('all')
            
            # 获取画布实际大小
            canvas_width = self.canvas.winfo_width() or 491
            canvas_height = self.canvas.winfo_height() or 450
            
            # 绘制12x10格的棋盘格，考虑边距后居中显示
            grid_cols = 11
            grid_rows = 10
            grid_size = 43  # 格子大小调整为45px
            
            # 计算棋盘格总大小
            total_grid_width = grid_cols * grid_size
            total_grid_height = grid_rows * grid_size
            
            # 考虑边距（画布边缘留出空间）
            margin = 0.1  # 边距调整为1像素
            available_width = canvas_width - margin * 2
            available_height = canvas_height - margin * 2
            
            # 如果棋盘格超过可用空间，则缩小
            scale = min(available_width / total_grid_width, available_height / total_grid_height, 1)
            if scale < 1:
                grid_size = int(grid_size * scale)
                total_grid_width = grid_cols * grid_size
                total_grid_height = grid_rows * grid_size
            
            # 计算居中偏移
            offset_x = (canvas_width - total_grid_width) // 2
            offset_y = (canvas_height - total_grid_height) // 2
            
            # 绘制棋盘格背景
            for i in range(grid_cols + 1):
                x = offset_x + i * grid_size
                self.canvas.create_line(x, offset_y, x, offset_y + total_grid_height, fill='#1E293B', width=1)
            for i in range(grid_rows + 1):
                y = offset_y + i * grid_size
                self.canvas.create_line(offset_x, y, offset_x + total_grid_width, y, fill='#1E293B', width=1)
            
            new_stars = []
            attraction_radius = 50
            
            attracted_star_index = None
            for i, (x, y) in enumerate(self.stars):
                off_x, off_y = self.star_offsets[i]
                mouse_distance = ((x + off_x - self.mouse_x) ** 2 + (y + off_y - self.mouse_y) ** 2) ** 0.5
                if mouse_distance < attraction_radius:
                    attracted_star_index = i
                    break
            
            for i, (x, y) in enumerate(self.stars):
                dx, dy = self.star_direction[i]
                new_dx = dx * self.star_speed[i]
                new_dy = dy * self.star_speed[i]
                
                off_x, off_y = self.star_offsets[i]
                new_off_x = off_x + new_dx
                new_off_y = off_y + new_dy
                
                max_offset = 15
                if abs(new_off_x) > max_offset:
                    self.star_direction[i] = (-dx, dy)
                    new_off_x = max_offset * (1 if new_off_x > 0 else -1)
                if abs(new_off_y) > max_offset:
                    self.star_direction[i] = (dx, -dy)
                    new_off_y = max_offset * (1 if new_off_y > 0 else -1)
                
                if random.random() < 0.1:
                    self.star_direction[i] = (random.uniform(-1, 1), random.uniform(-1, 1))
                
                mouse_distance = ((x + new_off_x - self.mouse_x) ** 2 + (y + new_off_y - self.mouse_y) ** 2) ** 0.5
                
                if mouse_distance < attraction_radius:
                    # 星星被吸附到鼠标位置，但要确保不超出画布边界
                    new_off_x = self.mouse_x - x
                    new_off_y = self.mouse_y - y
                    # 限制在画布范围内
                    final_x = x + new_off_x
                    final_y = y + new_off_y
                    if final_x < 0:
                        new_off_x = -x
                    elif final_x > canvas_width:
                        new_off_x = canvas_width - x
                    if final_y < 0:
                        new_off_y = -y
                    elif final_y > canvas_height:
                        new_off_y = canvas_height - y
                elif mouse_distance < 100:
                    # 50-100像素：强吸引力，越靠近速度越快，最终被吸入
                    distance_ratio = (100 - mouse_distance) / 50  # 从0到1
                    # 使用立方增长，让靠近时速度急剧增加，实现"吸入"效果
                    acceleration = 0.5 * (distance_ratio ** 3)  # 立方增长的加速度
                    
                    # 更新速度（累积），距离越近加速度越大
                    self.star_velocities[i] = (
                        self.star_velocities[i][0] + (self.mouse_x - (x + new_off_x)) * acceleration * 0.15,
                        self.star_velocities[i][1] + (self.mouse_y - (y + new_off_y)) * acceleration * 0.15
                    )
                    
                    # 应用速度，速度会持续累积，没有最大限制
                    new_off_x += self.star_velocities[i][0]
                    new_off_y += self.star_velocities[i][1]
                elif mouse_distance < 150:
                    # 100-150像素：弱吸引力，越靠近速度越快
                    distance_ratio = (150 - mouse_distance) / 50  # 从0到1
                    # 使用平方增长
                    acceleration = 0.2 * (distance_ratio ** 2)  # 平方增长的加速度
                    
                    # 更新速度（累积）
                    self.star_velocities[i] = (
                        self.star_velocities[i][0] + (self.mouse_x - (x + new_off_x)) * acceleration * 0.1,
                        self.star_velocities[i][1] + (self.mouse_y - (y + new_off_y)) * acceleration * 0.1
                    )
                    
                    # 应用速度
                    new_off_x += self.star_velocities[i][0]
                    new_off_y += self.star_velocities[i][1]
                else:
                    # 150像素以外：逐渐减速到正常漂移
                    self.star_velocities[i] = (
                        self.star_velocities[i][0] * 0.85,
                        self.star_velocities[i][1] * 0.85
                    )
                
                if attracted_star_index is not None and i != attracted_star_index:
                    attracted_x, attracted_y = self.stars[attracted_star_index]
                    attracted_off_x, attracted_off_y = self.star_offsets[attracted_star_index]
                    attracted_pos_x = attracted_x + attracted_off_x
                    attracted_pos_y = attracted_y + attracted_off_y
                    
                    distance_to_attracted = ((x + new_off_x - attracted_pos_x) ** 2 + (y + new_off_y - attracted_pos_y) ** 2) ** 0.5
                    
                    influence_radius = 120
                    if distance_to_attracted < influence_radius:
                        influence_strength = (influence_radius - distance_to_attracted) / influence_radius
                        influence_dx = (attracted_pos_x - (x + new_off_x)) * 0.01 * influence_strength
                        influence_dy = (attracted_pos_y - (y + new_off_y)) * 0.01 * influence_strength
                        new_off_x += influence_dx
                        new_off_y += influence_dy
                
                self.star_offsets[i] = (new_off_x, new_off_y)
                
                # 确保星星不会超出画布边界
                final_x = x + new_off_x
                final_y = y + new_off_y
                
                # 限制在画布范围内
                if final_x < 0:
                    final_x = 0
                elif final_x > canvas_width:
                    final_x = canvas_width
                if final_y < 0:
                    final_y = 0
                elif final_y > canvas_height:
                    final_y = canvas_height
                
                new_stars.append((final_x, final_y))
            
            for i in range(len(new_stars)):
                for j in range(i + 1, len(new_stars)):
                    x1, y1 = new_stars[i]
                    x2, y2 = new_stars[j]
                    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                    
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    mouse_to_mid = ((mid_x - self.mouse_x) ** 2 + (mid_y - self.mouse_y) ** 2) ** 0.5
                    
                    if distance < 100:
                        if mouse_to_mid < 30:
                            # 鼠标非常靠近，最粗最亮
                            color = '#22C55E'  # 亮绿色
                            width = max(1.1, 1.5 - distance / 75)  # 范围：1.1-1.5
                        elif mouse_to_mid < 80:
                            # 鼠标靠近，较粗
                            color = '#4ADE80'  # 鲜绿色
                            width = max(0.75, 1.1 - distance / 90)  # 范围：0.75-1.1
                        elif distance < 35:
                            # 近距离，中等偏粗
                            color = '#16A34A'  # 中绿色
                            width = max(0.35, 0.75 - distance / 43)  # 范围：0.35-0.75
                        elif distance < 70:
                            # 中距离，中等
                            color = '#065F46'  # 深绿色
                            width = max(0.12, 0.35 - distance / 190)  # 范围：0.12-0.35
                        else:
                            # 较远距离，最细
                            color = '#044E3C'  # 最深绿色
                            width = max(0.05, 0.12 - distance / 800)  # 范围：0.05-0.12
                        
                        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
            
            for i, (x, y) in enumerate(new_stars):
                distance_to_mouse = ((x - self.mouse_x) ** 2 + (y - self.mouse_y) ** 2) ** 0.5
                
                if distance_to_mouse < 4:
                    # 0-4像素：被吸附，亮黄色，大小4
                    star_size = 4
                    star_color = '#FEF9C3'  # 亮黄色（更白更亮，接近白色）
                    glow_color = '#FDE68A'   # 更黄的光晕颜色
                    glow_size = star_size * 2.2  # 统一光晕大小
                elif distance_to_mouse < 50:
                    # 5-50像素：金黄色，大小2.5-3.5渐变
                    min_size = 2.5
                    max_size = 3.5
                    star_size = min_size + (max_size - min_size) * (1 - (distance_to_mouse - 4) / 46)
                    star_color = '#FACC15'  # 金黄色
                    glow_color = '#FCD34D'   # 金黄色光晕
                    glow_size = star_size * 2.2  # 统一光晕大小
                elif distance_to_mouse < 100:
                    # 50-100像素：黄绿色，大小1.8-2.5渐变
                    min_size = 1.8
                    max_size = 2.5
                    star_size = min_size + (max_size - min_size) * (1 - (distance_to_mouse - 50) / 50)
                    star_color = '#A3E635'  # 黄绿色
                    glow_color = '#C4F241'   # 黄绿色光晕
                    glow_size = star_size * 2.2  # 统一光晕大小
                elif distance_to_mouse < 150:
                    # 100-150像素：绿色，大小1.2-1.8渐变
                    min_size = 1.2
                    max_size = 1.8
                    star_size = min_size + (max_size - min_size) * (1 - (distance_to_mouse - 100) / 50)
                    star_color = '#22C55E'  # 绿色
                    glow_color = None
                    glow_size = 0
                else:
                    # 150像素以外：灰色，大小1-1.2随机
                    star_size = random.uniform(1, 1.2)
                    star_color = '#94A3B8'
                    glow_color = None
                    glow_size = 0
                
                if glow_color:
                    self.canvas.create_oval(x - glow_size, y - glow_size,
                                           x + glow_size, y + glow_size,
                                           fill=glow_color, outline='')
                
                self.canvas.create_oval(x - star_size, y - star_size,
                                       x + star_size, y + star_size,
                                       fill=star_color, outline='')
            
            drawn_labels = []  # 记录已绘制标签的位置和尺寸
            
            for text, star_idx in self.ip_labels:
                if star_idx < len(new_stars):
                    x, y = new_stars[star_idx]
                    # 创建临时文本对象来获取尺寸，然后删除它
                    temp_text_id = self.canvas.create_text(0, 0, text=text, font=('微软雅黑', 9))
                    bbox = self.canvas.bbox(temp_text_id)
                    # 删除临时文本对象
                    self.canvas.delete(temp_text_id)
                    
                    if bbox:
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        padding = 4
                        label_x = x
                        label_y = y - 15
                        
                        margin = 2 * 1.5 
                        
                        # 边界检测
                        if label_x - text_width // 2 - padding < margin:
                            label_x = margin + text_width // 2 + padding
                        if label_x + text_width // 2 + padding > canvas_width - margin:
                            label_x = canvas_width - margin - text_width // 2 - padding
                        if label_y - text_height // 2 - padding < margin:
                            label_y = margin + text_height // 2 + padding
                        if label_y + text_height // 2 + padding > canvas_height - margin:
                            label_y = canvas_height - margin - text_height // 2 - padding
                        
                        # 标签重叠检测和避免
                        overlap_margin = 2 * 1.5  # 标签之间的最小间距
                        current_label_rect = (
                            label_x - text_width // 2 - padding - overlap_margin,
                            label_y - text_height // 2 - padding - overlap_margin,
                            label_x + text_width // 2 + padding + overlap_margin,
                            label_y + text_height // 2 + padding + overlap_margin
                        )
                        
                        for existing_rect in drawn_labels:
                            ex1, ey1, ex2, ey2 = existing_rect
                            cx1, cy1, cx2, cy2 = current_label_rect
                            
                            # 检测矩形重叠
                            if not (cx2 < ex1 or cx1 > ex2 or cy2 < ey1 or cy1 > ey2):
                                # 发生重叠，尝试调整位置
                                # 优先向下移动，其次向右移动
                                if label_y + text_height // 2 + padding + overlap_margin < canvas_height - margin:
                                    label_y = ey2 + overlap_margin + text_height // 2 + padding
                                elif label_x + text_width // 2 + padding + overlap_margin < canvas_width - margin:
                                    label_x = ex2 + overlap_margin + text_width // 2 + padding
                                elif label_y - text_height // 2 - padding - overlap_margin > margin:
                                    label_y = ey1 - text_height - padding * 2 - overlap_margin
                                elif label_x - text_width // 2 - padding - overlap_margin > margin:
                                    label_x = ex1 - text_width - padding * 2 - overlap_margin
                            
                            # 更新当前标签矩形位置
                            current_label_rect = (
                                label_x - text_width // 2 - padding - overlap_margin,
                                label_y - text_height // 2 - padding - overlap_margin,
                                label_x + text_width // 2 + padding + overlap_margin,
                                label_y + text_height // 2 + padding + overlap_margin
                            )
                        
                        # 记录当前标签位置
                        drawn_labels.append(current_label_rect)
                        
                        self.canvas.create_rectangle(
                            label_x - text_width // 2 - padding,
                            label_y - text_height // 2 - padding,
                            label_x + text_width // 2 + padding,
                            label_y + text_height // 2 + padding,
                            fill='#1E293B', outline='#334155'
                        )
                        self.canvas.create_text(label_x, label_y, text=text, fill='#22C55E', font=('微软雅黑', 9))
            
            self._star_anim_id = self.splash.after(30, self._update_star_animation)
            # 处理状态更新队列
            self._process_update_queue()
        
        except Exception as e:
            print(f"Error in star animation: {str(e)}")
    
    def update_progress(self, module_name):
        if not self.splash:
            return
        
        try:
            self.update_queue.append(module_name)
        except Exception as e:
            print(f"Error updating progress: {str(e)}")
    
    def _process_update_queue(self):
        try:
            if not self.splash:
                return
            
            while self.update_queue:
                module_name = self.update_queue.pop(0)
                self.loaded_modules += 1
                
                if self.status_text and self.splash:
                    try:
                        self.status_text.config(text=f"正在加载: {module_name}")
                    except Exception as e:
                        print(f"Error updating UI: {str(e)}")
                        self.update_queue.clear()
                        break
                
                if self.splash:
                    try:
                        self.splash.update()
                    except:
                        pass
        except Exception as e:
            print(f"Error processing update queue: {str(e)}")
    
    def close(self):
        self._stop_animations()
        
        self.update_queue.clear()
        
        if self.splash:
            try:
                self.splash.destroy()
            except Exception:
                pass
            self.splash = None