#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鍙鍖栨ā鍧?
瀹炵幇缃戠粶鎷撴墤鍥惧拰IP鍦板潃鍒嗛厤鍙鍖栧姛鑳?

妯″潡璇存槑:
- NetworkTopologyVisualizer: 缃戠粶鎷撴墤鍙鍖栫被锛屾敮鎸佸崟涓€缁煎悎鎬х綉缁滄嫇鎵戝浘
- IPAllocationVisualizer: IP鍦板潃鍒嗛厤鍙鍖栫被

浣跨敤绀轰緥:
python
# 鍒涘缓鍙鍖栧櫒
visualizer = NetworkTopologyVisualizer(parent_frame)

# 璁剧疆鏁版嵁鍥炶皟鍑芥暟
def get_network_data():
    # 杩斿洖缃戠粶鎷撴墤鏁版嵁
    return network_data

visualizer.set_data_callback(get_network_data)

# 缁樺埗鎷撴墤鍥?
visualizer.draw_topology(network_data)

# 寮€濮嬭嚜鍔ㄦ洿鏂?
visualizer.start_auto_update(interval=60000)  # 60绉掑埛鏂颁竴娆?

# 鎵嬪姩鍒锋柊
visualizer.refresh_data()

# 璁剧疆杩囨护绾у埆
visualizer.set_filter_level(2)  # 鍙樉绀?绾у強浠ヤ笅鑺傜偣

"""

import tkinter as tk
from tkinter import Canvas, Frame, Scrollbar
from typing import Callable
from style_manager import get_current_font_settings
from i18n import _ as translate

# 妯″潡鐗堟湰
__version__ = "1.0.0"


# 妯″潡鎺ュ彛瀹氫箟
class VisualizationError(Exception):
    """鍙鍖栨ā鍧楀紓锟?""
    pass


# 瀹氫箟棰滆壊甯搁噺 - 浼橀泤閰嶈壊鏂规
NODE_COLOR = "#4a6fa5"
NODE_BORDER_COLOR = "#aaaaaa"
LINK_COLOR = "#6c757d"
TEXT_COLOR = "#ffffff"
BACKGROUND_COLOR = "#2c3e50"
HIGHLIGHT_COLOR = "#3498db"

# 瀹氫箟鑺傜偣澶у皬
NODE_WIDTH = 150
NODE_HEIGHT = 70
NODE_SPACING = 230  # 璋冩暣鑺傜偣闂磋窛锛屼娇甯冨眬鏇寸揣锟?

# 瀹氫箟缃戞绫诲瀷棰滆壊 - 涓板瘜閰嶈壊鏂规
SUBNET_TYPE_COLORS = {
    "default": "#f4a261",      # 鏌斿拰姗欒壊锛堥粯璁わ級
    "server": "#e76f51",        # 鏆栨鑹诧紙鏈嶅姟鍣級
    "client": "#2a9d8f",        # 闈掔豢鑹诧紙瀹㈡埛绔級
    "network": "#f4a261",        # 鏌斿拰姗欒壊锛堢綉缁滐級
    "management": "#9c89b8",      # 鏌斿拰绱壊锛堢鐞嗭級
    "large": "#f97316",         # 姗欒壊锛堝ぇ缃戞锟?
    "medium": "#f59e0b",        # 姗欒壊锛堜腑绛夌綉娈碉級
    "small": "#9333ea",         # 绱壊锛堝皬缃戞锟?
    "extra_large": "#ef4444",    # 绾㈣壊锛堣秴澶х綉娈碉級
    "wireless": "#8b5cf6",       # 绱壊锛堟棤绾跨綉娈碉級
    "office": "#10b981",         # 缁胯壊锛堝姙鍏綉娈碉級
    "production": "#f59e0b",     # 姗欒壊锛堢敓浜х綉娈碉級
    "test": "#ec4899",           # 绮夎壊锛堟祴璇曠綉娈碉級
    "dmz": "#ec4899",            # 绮夎壊锛圖MZ缃戞锟?
    "storage": "#f97316",         # 姗欒壊锛堝瓨鍌ㄧ綉娈碉級
    "backup": "#22c55e"          # 缁胯壊锛堝浠界綉娈碉級
}

# 瀹氫箟璁惧绫诲瀷褰㈢姸
DEVICE_SHAPES = {
    "default": "rectangle",
    "router": "diamond",
    "switch": "ellipse",
    "switch2": "rounded_rectangle",
    "switch3": "rectangle",
    "server": "rectangle",
    "client": "triangle",
    "wireless": "hexagon",
    "office": "pentagon",
    "production": "octagon",
    "test": "circle",
    "dmz": "star",
    "storage": "trapezoid",
    "backup": "parallelogram"
}


class NetworkTopologyVisualizer:
    """缃戠粶鎷撴墤鍙鍖栫被"""
    
    def __init__(self, parent: tk.BaseWidget) -> None:
        """鍒濆鍖栧彲瑙嗗寲锟?
        
        Args:
            parent: 鐖跺锟?
        """
        self.parent: tk.BaseWidget = parent
        self.canvas_frame: Frame = Frame(parent)
        
        # 閰嶇疆 canvas_frame 浠ュ～鍏呯埗瀹瑰櫒
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 鍒涘缓鐢诲竷锛堢Щ闄ゆ粴鍔ㄦ潯锟?
        self.canvas: Canvas = Canvas(
            self.canvas_frame,
            bg=BACKGROUND_COLOR
        )
        
        # 鏀剧疆缁勪欢
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 鍒涘缓鍏ㄥ睆鎸夐挳
        self._create_fullscreen_button()
        
        # 鍒濆鍖栨暟锟?
        self.nodes: dict[str, dict[str, object]] = {}
        self.links: list[dict[str, object]] = []
        
        # 缁戝畾浜嬩欢
        _ = self.canvas.bind("<ButtonPress-1>", self.start_drag)
        _ = self.canvas.bind("<B1-Motion>", self.drag)
        _ = self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        _ = self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        _ = self.canvas.bind("<Motion>", self.on_mouse_move)
        _ = self.canvas.bind("<Leave>", self.on_canvas_leave)
        
        # 缁戝畾閰嶇疆浜嬩欢锛屽綋鐖跺鍣ㄥぇ灏忓彉鍖栨椂璋冩暣鐢诲竷澶у皬
        _ = self.canvas_frame.bind("<Configure>", self.on_canvas_frame_configure)
        
        # 鎷栨嫿鐘讹拷?
        self.dragging: bool = False
        self.drag_start_x: int = 0
        self.drag_start_y: int = 0
        self.last_x: int = 0
        self.last_y: int = 0
        
        # 缂╂斁鍥犲瓙
        self.scale: float = 1.0
        
        # 鑺傜偣鎮仠鐘讹拷?
        self.hovered_node: dict[str, object] | None = None
        self.tooltip: tk.Toplevel | None = None
        self.tooltip_timer: int | None = None  # 寤惰繜鏄剧ず瀹氭椂锟?
        self._hover_poll_job: int | None = None  # 鎮仠杞妫€娴嬪畾鏃跺櫒
        self.last_mouse_x: int = 0  # 璁板綍榧犳爣浣嶇疆
        self.last_mouse_y: int = 0
        
        # 鏁版嵁鏇存柊鐩稿叧
        self.update_interval: int = 30000  # 榛樿 30 绉掑埛鏂颁竴锟?
        self.update_timer: int | None = None
        self.data_callback: Callable[[], object] | None = None
        self.auto_update: bool = False
        
        # 鎬ц兘浼樺寲鐩稿叧
        self.batch_drawing: bool = True  # 鍚敤鎵归噺缁樺埗
        self.max_nodes: int = 500  # 鏈€澶ц妭鐐规暟
        self.filter_level: int = 10  # 杩囨护绾у埆锟? 琛ㄧず鏄剧ず鎵€鏈夎妭锟?
        self.visible_nodes: set[str] = set()  # 鍙鑺傜偣闆嗗悎
        
    def start_drag(self, event: tk.Event) -> None:
        """寮€濮嬫嫋锟?""
        self.dragging = True
        self.drag_start_x: int = event.x
        self.drag_start_y: int = event.y
        self.last_x: int = event.x
        self.last_y: int = event.y
    
    def drag(self, event: tk.Event) -> None:
        """鎷栨嫿鎿嶄綔"""
        if self.dragging:
            dx: int = event.x - self.last_x
            dy: int = event.y - self.last_y
            self.canvas.move(tk.ALL, dx, dy)
            self.last_x: int = event.x
            self.last_y: int = event.y
    
    def stop_drag(self, event: tk.Event) -> None:
        """鍋滄鎷栨嫿"""
        self.dragging = False
    
    def on_mouse_wheel(self, event: tk.Event) -> None:
        """榧犳爣婊氳疆缂╂斁"""
        # 璁＄畻缂╂斁鍥犲瓙
        if event.delta > 0:
            new_scale: float = self.scale * 1.1
        else:
            new_scale: float = self.scale * 0.9
        
        # 闄愬埗缂╂斁鑼冨洿
        new_scale = max(0.5, min(new_scale, 1.0))
        
        # 璁＄畻缂╂斁姣斾緥
        scale_factor: float = new_scale / self.scale
        self.scale = new_scale
        
        # 缂╂斁鐢诲竷鍐呭
        self.canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)
    
    def _create_shadow(self, points: list[float], shadow_x: float, shadow_y: float, width: float, height: float, smooth: bool = False) -> int:
        """閫氱敤闃村奖鍒涘缓鏂规硶
        
        Args:
            points: 椤剁偣鍧愭爣鍒楄〃锛堢浉瀵逛簬 x, y 鐨勫亸绉婚噺锛屼娇锟?0-1 涔嬮棿鐨勭浉瀵瑰潗鏍囷級
            shadow_x: 闃村奖璧峰 x 鍧愭爣
            shadow_y: 闃村奖璧峰 y 鍧愭爣
            width: 瀹藉害
            height: 楂樺害
            smooth: 鏄惁浣跨敤骞虫粦锛堝渾瑙掞級
        
        Returns:
            int: 闃村奖瀵硅薄 ID
        """
        # 灏嗙浉瀵瑰潗鏍囪浆鎹负闃村奖鐨勭粷瀵瑰潗锟?
        shadow_points = []
        for i in range(0, len(points), 2):
            px = shadow_x + points[i] * width
            py = shadow_y + points[i + 1] * height
            shadow_points.extend([px, py])
        
        if smooth:
            return self.canvas.create_polygon(*shadow_points, fill="#000000", outline="", smooth=True)
        else:
            return self.canvas.create_polygon(*shadow_points, fill="#000000", outline="")
    
    def create_node_shape(self, x, y, width, height, shape="rectangle", fill=NODE_COLOR, outline=NODE_BORDER_COLOR, border_width=2, node_tag=None):
        """鍒涘缓涓嶅悓褰㈢姸鐨勮妭锟?
        
        Args:
            x: x 鍧愭爣
            y: y 鍧愭爣
            width: 瀹藉害
            height: 楂樺害
            shape: 褰㈢姸绫诲瀷
            fill: 濉厖棰滆壊
            outline: 杈规棰滆壊
            border_width: 杈规瀹藉害
            node_tag: 鑺傜偣 tag锛岀敤浜庣粦瀹氶槾褰卞眰
        
        Returns:
            tuple: (shape_id, gradient_items, shadow_items) shape_id 鏄竟妗嗗璞＄殑 ID锛実radient_items 鏄墍鏈夋笎鍙樺～鍏呭眰锟?ID 鍒楄〃锛宻hadow_items 鏄墍鏈夐槾褰卞眰锟?ID 鍒楄〃
        """
        # 鏀堕泦鎵€鏈夊垱寤虹殑娓愬彉濉厖灞傚锟?ID
        gradient_items = []
        # 瀹氫箟鍚勫舰鐘剁殑椤剁偣鍧愭爣锛堜娇锟?0-1 鐨勭浉瀵瑰潗鏍囷級
        SHAPE_POINTS = {
            "rectangle": [0.1, 0, 0.9, 0, 1, 0.1, 1, 0.9, 0.9, 1, 0.1, 1, 0, 0.9, 0, 0.1],  # 鍦嗚鐭╁舰杩戜技
            "rounded_rectangle": [0.15, 0, 0.85, 0, 1, 0.15, 1, 0.85, 0.85, 1, 0.15, 1, 0, 0.85, 0, 0.15],
            "ellipse": None,  # 妞渾鐗规畩澶勭悊
            "circle": None,  # 鍦嗗舰鐗规畩澶勭悊
            "diamond": [0.5, 0, 1, 0.5, 0.5, 1, 0, 0.5],
            "triangle": [0.5, 0, 1, 1, 0, 1],
            "hexagon": [0.5, 0, 1, 0.33, 1, 0.67, 0.5, 1, 0, 0.67, 0, 0.33],
            "pentagon": [0.5, 0, 1, 0.5, 0.8, 1, 0.2, 1, 0, 0.5],
            "octagon": [0.3, 0, 0.7, 0, 1, 0.3, 1, 0.7, 0.7, 1, 0.3, 1, 0, 0.7, 0, 0.3],
            "star": [0.5, 0, 0.6, 0.35, 1, 0.35, 0.65, 0.5, 1, 0.65, 0.6, 0.65, 0.5, 1, 0.4, 0.65, 0, 0.65, 0.35, 0.5, 0, 0.35, 0.4, 0.35],
            "trapezoid": [0.15, 0, 0.85, 0, 1, 1, 0, 1],
            "parallelogram": [0.2, 0, 1, 0, 0.8, 1, 0, 1]
        }
        
        # 鏀堕泦鎵€鏈夊垱寤虹殑闃村奖灞傚锟?ID
        shadow_items = []
        
        # 娣诲姞闃村奖鏁堟灉
        shadow_offset = 3
        
        for i in range(3):
            shadow_x = x + shadow_offset * (i + 1)
            shadow_y = y + shadow_offset * (i + 1)
            
            # 浣跨敤閫氱敤鏂规硶鍒涘缓闃村奖
            if shape in ["ellipse", "circle"]:
                # 妞渾鍜屽渾褰㈢壒娈婂锟?
                shadow_id = self.canvas.create_oval(
                    shadow_x, shadow_y, shadow_x + width, shadow_y + height,
                    fill="#000000",
                    outline=""
                )
            elif shape in ["rectangle", "rounded_rectangle"]:
                # 鐭╁舰鍜屽渾瑙掔煩褰㈤渶瑕佸钩婊戞晥锟?
                shadow_id = self._create_shadow(SHAPE_POINTS[shape], shadow_x, shadow_y, width, height, smooth=True)
            elif shape in SHAPE_POINTS:
                # 浣跨敤閫氱敤鏂规硶鍒涘缓澶氳竟褰㈤槾锟?
                shadow_id = self._create_shadow(SHAPE_POINTS[shape], shadow_x, shadow_y, width, height)
            else:
                # 榛樿浣跨敤鐭╁舰
                shadow_id = self._create_shadow(SHAPE_POINTS.get("rectangle", []), shadow_x, shadow_y, width, height, smooth=True)
            
            shadow_items.append(shadow_id)
            # 濡傛灉鎻愪緵锟?node_tag锛岀珛鍗崇粦锟?
            if node_tag:
                self.canvas.itemconfig(shadow_id, tags=(node_tag,))
        
        # 鍒涘缓涓诲舰锟?
        if shape == "rectangle":
            # 鍒涘缓鍦嗚鐭╁舰
            radius = 10
            # 鍒涘缓娓愬彉鏁堟灉锛堜娇鐢ㄥ灞傚彔鍔狅級
            for i in range(3):
                alpha = 0.3 + i * 0.2
                gradient_fill = fill
                if i > 0:
                    # 绋嶅井浜竴鐐圭殑棰滆壊浣滀负娓愬彉
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + radius, y + i,
                    x + width - radius, y + i,
                    x + width - i, y + radius,
                    x + width - i, y + height - radius,
                    x + width - radius, y + height - i,
                    x + radius, y + height - i,
                    x + i, y + height - radius,
                    x + i, y + radius,
                    fill=gradient_fill,
                    outline="",
                    smooth=True
                )
                gradient_items.append(item)
                # 缁戝畾 tag 鍒版笎鍙樺眰
                if node_tag:
                    self.canvas.itemconfig(item, tags=(node_tag,))
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                x + radius, y,
                x + width - radius, y,
                x + width, y + radius,
                x + width, y + height - radius,
                x + width - radius, y + height,
                x + radius, y + height,
                x, y + height - radius,
                x, y + radius,
                fill="",
                outline=outline,
                width=border_width + 1,
                smooth=True
            )
            # 缁戝畾 tag 鍒拌竟锟?
            if node_tag:
                self.canvas.itemconfig(shape_id, tags=(node_tag,))
            return shape_id, gradient_items, shadow_items, shadow_items
        elif shape == "ellipse":
            # 鍒涘缓娓愬彉鏁堟灉 - 濉厖灞傚厛鍒涘缓
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_oval(
                    x + i, y + i, x + width - i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
                # 缁戝畾 tag 鍒版笎鍙樺眰
                if node_tag:
                    self.canvas.itemconfig(item, tags=(node_tag,))
            
            # 杈规灞傛渶鍚庡垱寤猴紝骞舵彁鍗囧埌鏈€椤跺眰锛岀‘淇濋紶鏍囦簨浠朵紭鍏堝懡涓竟锟?
            shape_id = self.canvas.create_oval(
                x, y, x + width, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            # 鍏抽敭锛氬皢杈规鎻愬崌鍒版墍鏈夊～鍏呭眰涔嬩笂锛岃В鍐虫き鍦嗗唴閮ㄦ棤娉曡Е鍙戞偓鍋滅殑闂
            # 缁戝畾 tag 鍒拌竟锟?
            if node_tag:
                self.canvas.itemconfig(shape_id, tags=(node_tag,))
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "diamond":
            # 鍒涘缓鑿卞舰 - 鍥涗釜椤剁偣鍒嗗埆鍦ㄨ竟鐣屾鐨勫洓杈逛腑锟?
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + width / 2, y,          # 涓婇《锟?
                    x + width, y + height / 2,  # 鍙抽《锟?
                    x + width / 2, y + height,  # 涓嬮《锟?
                    x, y + height / 2,          # 宸﹂《锟?
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
                # 缁戝畾 tag 鍒版笎鍙樺眰
                if node_tag:
                    self.canvas.itemconfig(item, tags=(node_tag,))
            
            # 杈规灞傛渶鍚庡垱寤哄苟鎻愬崌鍒版渶椤跺眰
            shape_id = self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height / 2,
                x + width / 2, y + height,
                x, y + height / 2,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            # 缁戝畾 tag 鍒拌竟锟?
            if node_tag:
                self.canvas.itemconfig(shape_id, tags=(node_tag,))
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "triangle":
            # 鍒涘缓涓夎锟?- 椤剁偣鍦ㄨ竟鐣屾鐨勪笂杈逛腑鐐瑰拰搴曡竟涓よ
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + width / 2, y,              # 涓婇《锟?
                    x + width, y + height,          # 鍙充笅锟?
                    x, y + height,                  # 宸︿笅锟?
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 杈规灞傛渶鍚庡垱寤哄苟鎻愬崌鍒版渶椤跺眰
            shape_id = self.canvas.create_polygon(
                x + width / 2, y,
                x + width, y + height,
                x, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "rounded_rectangle":
            # 鍒涘缓鍦嗚鐭╁舰
            radius = 15
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + radius, y + i,
                    x + width - radius, y + i,
                    x + width - i, y + radius,
                    x + width - i, y + height - radius,
                    x + width - radius, y + height - i,
                    x + radius, y + height - i,
                    x + i, y + height - radius,
                    x + i, y + radius,
                    fill=gradient_fill,
                    outline="",
                    smooth=True
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                x + radius, y,
                x + width - radius, y,
                x + width, y + radius,
                x + width, y + height - radius,
                x + width - radius, y + height,
                x + radius, y + height,
                x, y + height - radius,
                x, y + radius,
                fill="",
                outline=outline,
                width=border_width + 1,
                smooth=True
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "hexagon":
            # 鍒涘缓鍏竟锟?- 椤剁偣鍦ㄨ竟鐣屾鐨勮竟锟?
            # 宸﹀彸椤剁偣鍦ㄥ乏鍙宠竟鐣屼笂锛岀‘淇濅笌鍏朵粬褰㈢姸瀵归綈
            points = [
                x + width / 2, y,                  # 锟?
                x + width, y + height / 3,         # 鍙充笂
                x + width, y + height * 2 / 3,     # 鍙充笅
                x + width / 2, y + height,         # 锟?
                x, y + height * 2 / 3,             # 宸︿笅
                x, y + height / 3                  # 宸︿笂
            ]
            
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "pentagon":
            # 鍒涘缓浜旇竟锟?- 椤剁偣鍦ㄨ竟鐣屾鐨勮竟锟?
            # 浜旇竟褰細涓婇《鐐瑰湪涓婅竟涓偣锛屽乏鍙抽《鐐瑰湪宸﹀彸杈逛腑鐐癸紝搴曢儴涓や釜椤剁偣鍦ㄥ簳锟?
            points = [
                x + width / 2, y,                  # 锟?
                x + width, y + height / 2,          # 鍙充腑
                x + width * 0.8, y + height,        # 鍙充笅
                x + width * 0.2, y + height,        # 宸︿笅
                x, y + height / 2                   # 宸︿腑
            ]
            
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "octagon":
            # 鍒涘缓鍏竟锟?- 椤剁偣鍦ㄨ竟鐣屾杈圭紭
            # 宸﹀彸涓や晶鏈夊瀭鐩寸殑杈癸紝纭繚杩炴帴绾垮彲浠ュ锟?
            points = [
                x + width * 0.3, y,                # 涓婁腑锟?
                x + width * 0.7, y,                # 涓婁腑锟?
                x + width, y + height * 0.3,       # 鍙充笂
                x + width, y + height * 0.7,       # 鍙充笅
                x + width * 0.7, y + height,       # 涓嬩腑锟?
                x + width * 0.3, y + height,       # 涓嬩腑锟?
                x, y + height * 0.7,               # 宸︿笅
                x, y + height * 0.3                # 宸︿笂
            ]
            
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "circle":
            # 鍒涘缓鍦嗗舰
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_oval(
                    x + i, y + i, x + width - i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_oval(
                x, y, x + width, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "star":
            # 鍒涘缓鏄熷舰 - 绠€鍖栫増鏈紝浣跨敤杈圭晫妗嗚竟锟?
            points = [
                x + width / 2, y,                  # 锟?
                x + width * 0.6, y + height * 0.35,  # 澶栫偣
                x + width, y + height * 0.35,      # 锟?
                x + width * 0.65, y + height * 0.5,  # 鍐呯偣
                x + width, y + height * 0.65,      # 鍙充笅
                x + width * 0.6, y + height * 0.65,  # 澶栫偣
                x + width / 2, y + height,          # 锟?
                x + width * 0.4, y + height * 0.65,  # 澶栫偣
                x, y + height * 0.65,              # 宸︿笅
                x + width * 0.35, y + height * 0.5,  # 鍐呯偣
                x, y + height * 0.35,              # 锟?
                x + width * 0.4, y + height * 0.35   # 澶栫偣
            ]
            
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    *points,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                *points,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "trapezoid":
            # 鍒涘缓姊舰
            top_width = width * 0.7
            bottom_width = width
            
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + (width - top_width) / 2 + i, y + i,
                    x + (width + top_width) / 2 - i, y + i,
                    x + width - i, y + height - i,
                    x + i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                x + (width - top_width) / 2, y,
                x + (width + top_width) / 2, y,
                x + width, y + height,
                x, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        elif shape == "parallelogram":
            # 鍒涘缓骞宠鍥涜竟锟?
            skew = width * 0.2
            
            # 鍒涘缓娓愬彉鏁堟灉
            for i in range(3):
                gradient_fill = fill
                if i > 0:
                    gradient_fill = "#" + "".join([f"{min(255, int(c, 16) + 20):02x}" for c in [fill[1:3], fill[3:5], fill[5:7]]])
                
                item = self.canvas.create_polygon(
                    x + skew + i, y + i,
                    x + width + i, y + i,
                    x + width - skew - i, y + height - i,
                    x - i, y + height - i,
                    fill=gradient_fill,
                    outline=""
                )
                gradient_items.append(item)
            
            # 鍒涘缓杈规
            shape_id = self.canvas.create_polygon(
                x + skew, y,
                x + width, y,
                x + width - skew, y + height,
                x, y + height,
                fill="",
                outline=outline,
                width=border_width + 1
            )
            self.canvas.tag_raise(shape_id)
            return shape_id, gradient_items, shadow_items
        else:
            shape_id = self.canvas.create_rectangle(
                x, y, x + width, y + height,
                fill=fill,
                outline=outline,
                width=border_width
            )
            return shape_id, gradient_items, shadow_items
    
    def add_node(self, name, subnet, level=0, subnet_type="default", device_type="default", ip_info=None, parent_id=None):
        """娣诲姞鑺傜偣
        
        Args:
            name: 鑺傜偣鍚嶇О
            subnet: 瀛愮綉淇℃伅
            level: 灞傜骇
            subnet_type: 缃戞绫诲瀷
            device_type: 璁惧绫诲瀷
            ip_info: IP鍦板潃淇℃伅
            parent_id: 鐖惰妭鐐笽D
        
        Returns:
            str: 鑺傜偣ID
        """
        node_id = f"node_{len(self.nodes)}"
        
        # 璁＄畻鑺傜偣浣嶇疆锛堜娇鐢ㄦ敼杩涚殑鏍戝舰甯冨眬锟?
        if parent_id and parent_id in self.nodes:
            # 濡傛灉鏈夌埗鑺傜偣锛屽熀浜庣埗鑺傜偣浣嶇疆璁＄畻
            parent_node = self.nodes[parent_id]
            x = parent_node["x"] + NODE_SPACING  # 姘村钩闂磋窛
            # 璁＄畻鐖惰妭鐐圭殑瀛愯妭鐐规暟閲忥紝纭繚瀛愯妭鐐瑰潎鍖€鍒嗗竷
            child_count = sum(1 for n in self.nodes.values() if n.get("parent_id") == parent_id)
            # 璁＄畻瀛愯妭鐐圭殑鍨傜洿浣嶇疆锛岀‘淇濈埗鑺傜偣灞呬腑
            y = parent_node["y"] + (child_count - 1) * (NODE_HEIGHT + 60) - (child_count * (NODE_HEIGHT + 60)) / 2 + NODE_HEIGHT / 2
        else:
            # 鏍硅妭鐐规垨娌℃湁鐖惰妭鐐圭殑鑺傜偣
            x = 100 + level * NODE_SPACING  # 姘村钩闂磋窛
            # 璁＄畻鍚屼竴灞傜骇鑺傜偣鐨勬暟锟?
            same_level_nodes = len([n for n in self.nodes.values() if n.get("level") == level])
            # 璁＄畻鍨傜洿浣嶇疆锛岀‘淇濊妭鐐瑰瀭鐩村垎锟?
            y = 100 + same_level_nodes * (NODE_HEIGHT + 40)  # 閫傚綋鐨勫瀭鐩撮棿锟?
        
        # 鏍规嵁缃戞绫诲瀷鑾峰彇棰滆壊
        node_color = SUBNET_TYPE_COLORS.get(subnet_type, NODE_COLOR)
        
        # 鏍规嵁璁惧绫诲瀷鑾峰彇褰㈢姸
        node_shape = DEVICE_SHAPES.get(device_type, "rectangle")
        
        # 鍒涘缓鑺傜偣褰㈢姸
        shape_tuple = self.create_node_shape(
            x, y, NODE_WIDTH, NODE_HEIGHT, 
            shape=node_shape, 
            fill=node_color,
            outline=NODE_BORDER_COLOR,
            border_width=2,
            node_tag=node_id  # 浼犲叆 node_id锛岃闃村奖灞備篃缁戝畾 tag
        )
        shape_id = shape_tuple[0]
        gradient_items = shape_tuple[1] if len(shape_tuple) > 1 else []
        shadow_items = shape_tuple[2] if len(shape_tuple) > 2 else []
        
        # 鑾峰彇瀛椾綋璁剧疆
        font_family, font_size = get_current_font_settings()
        
        # 鍒涘缓鑺傜偣鏂囨湰
        text_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT / 4,
            text=name,
            font=(font_family, font_size - 2, "bold"),
            fill=TEXT_COLOR
        )
        
        # 鍒涘缓瀛愮綉鏂囨湰
        subnet_text = str(subnet)
        if len(subnet_text) > 20:
            subnet_text = subnet_text[:17] + "..."
        
        subnet_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT / 2,
            text=subnet_text,
            font=(font_family, font_size - 3),
            fill=TEXT_COLOR
        )
        
        # 鍒涘缓IP淇℃伅鏂囨湰
        ip_info_text = ""
        if ip_info:
            total_ips = ip_info.get("total", 0)
            allocated = ip_info.get("allocated", 0)
            reserved = ip_info.get("reserved", 0)
            used_ips = allocated + reserved
            ip_info_text = f"{used_ips}/{total_ips}"
        
        ip_info_id = self.canvas.create_text(
            x + NODE_WIDTH / 2, y + NODE_HEIGHT * 3 / 4,
            text=ip_info_text,
            font=(font_family, font_size - 4),
            fill=TEXT_COLOR
        )
        
        # 鍏抽敭锛氬皢鎵€鏈夊睘浜庤鑺傜偣鐨勭敾甯冨璞＄粦瀹氬埌缁熶竴锟?tag
        # 鍖呮嫭锛氬舰鐘惰竟妗嗗眰 + 娓愬彉濉厖锟?+ 闃村奖锟?+ 鏂囨湰瀵硅薄
        all_node_items = [shape_id, text_id, subnet_id, ip_info_id] + gradient_items + shadow_items
        for item_id in all_node_items:
            self.canvas.itemconfig(item_id, tags=(node_id,))
        
        # 瀛樺偍鑺傜偣淇℃伅
        self.nodes[node_id] = {
            "id": node_id,
            "name": name,
            "subnet": subnet,
            "subnet_type": subnet_type,
            "device_type": device_type,
            "ip_info": ip_info,
            "shape": shape_id,
            "text": text_id,
            "subnet_text": subnet_id,
            "ip_info_text": ip_info_id,
            "x": x,
            "y": y,
            "level": level,
            "parent_id": parent_id
        }
        
        return node_id
    
    def add_link(self, source_node_id, target_node_id):
        """娣诲姞杩炴帴
        
        Args:
            source_node_id: 婧愯妭鐐笽D
            target_node_id: 鐩爣鑺傜偣ID
        """
        if source_node_id in self.nodes and target_node_id in self.nodes:
            source = self.nodes[source_node_id]
            target = self.nodes[target_node_id]
            
            # 璁＄畻杩炴帴绾垮潗锟?
            x1 = source["x"] + NODE_WIDTH
            y1 = source["y"] + NODE_HEIGHT / 2
            x2 = target["x"]
            y2 = target["y"] + NODE_HEIGHT / 2
            
            # 鍒涘缓杩炴帴绾匡紝娣诲姞绠ご鍜屽姩鐢绘晥锟?
            link_id = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=LINK_COLOR,
                width=2,
                arrow=tk.LAST,
                arrowshape=(10, 15, 5),  # 绠ご褰㈢姸锟?绠ご闀垮害, 绠ご瀹藉害, 绠ご瑙掑害)
                smooth=True
            )
            
            # 瀛樺偍杩炴帴淇℃伅
            self.links.append({
                "id": link_id,
                "source": source_node_id,
                "target": target_node_id
            })
            
            # 灏嗚繛鎺ョ嚎缃簬鑺傜偣涓嬫柟
            self.canvas.tag_lower(link_id)

    def clear(self):
        """娓呯┖鐢诲竷"""
        # 鍋滄杞妫€锟?
        self._stop_hover_polling()
        
        self.canvas.delete(tk.ALL)
        self.nodes = {}
        self.links = []
        self.visible_nodes = set()
        self.scale = 1.0
        self.hovered_node = None
    
    def draw_topology(self, network_data):
        """缁樺埗缁煎悎缃戠粶鎷撴墤锟?
        
        Args:
            network_data: 缃戠粶鏁版嵁锛屽寘鍚墍鏈夌綉缁滅粨鏋勪俊锟?
        """
        # 閲嶇疆缂╂斁鏍囧織锛屽厑璁告柊鐨勮嚜閫傚簲缂╂斁
        self._scaled = False
        self.clear()
        
        # 瀛樺偍鑺傜偣ID鏄犲皠
        node_id_map = {}
        
        # 杩囨护鑺傜偣
        filtered_data = self._filter_nodes(network_data)
        
        # 闄愬埗鑺傜偣鏁伴噺
        if len(filtered_data) > self.max_nodes:
            filtered_data = filtered_data[:self.max_nodes]
        
        # 鏋勫缓缃戠粶灞傛缁撴瀯锛屽厛澶勭悊鐖惰妭鐐癸紝鍐嶅鐞嗗瓙鑺傜偣
        # 鎸夊眰绾ф帓搴忕綉缁滄暟锟?
        sorted_data = sorted(filtered_data, key=lambda x: x.get("level", 0))
        
        # 閬嶅巻缃戠粶鏁版嵁锛屾瀯寤鸿妭鐐瑰拰杩炴帴
        for network in sorted_data:
            # 妫€鏌ヨ妭鐐圭骇鍒槸鍚﹀湪杩囨护鑼冨洿锟?
            if network.get("level", 0) <= self.filter_level or self.filter_level == 0:
                # 鏌ユ壘鐖惰妭鐐笽D
                parent_network_id = network.get("parent_id")
                parent_node_id = node_id_map.get(parent_network_id) if parent_network_id else None
                
                # 娣诲姞缃戠粶鑺傜偣
                node_id = self.add_node(
                    network.get("name", "Network"),
                    network.get("cidr", ""),
                    level=network.get("level", 0),
                    subnet_type=network.get("subnet_type", network.get("type", "default")),
                    device_type=network.get("device_type", "default"),
                    ip_info=network.get("ip_info", {}),
                    parent_id=parent_node_id
                )
                node_id_map[network.get("id", node_id)] = node_id
                self.visible_nodes.add(node_id)
        
        # 娣诲姞杩炴帴
        for network in sorted_data:
            node_id = node_id_map.get(network.get("id"))
            if node_id and node_id in self.visible_nodes:
                # 閬嶅巻瀛愯妭鐐癸紝鑾峰彇瀛愯妭鐐笽D
                for child in network.get("children", []):
                    if isinstance(child, dict):
                        child_id = child.get("id")
                        if child_id in node_id_map and node_id_map[child_id] in self.visible_nodes:
                            self.add_link(node_id, node_id_map[child_id])
                    elif isinstance(child, str):
                        # 濡傛灉瀛愯妭鐐规槸瀛楃涓睮D锛岀洿鎺ユ煡锟?
                        if child in node_id_map and node_id_map[child] in self.visible_nodes:
                            self.add_link(node_id, node_id_map[child])
        
        # 閲嶆柊璁＄畻鎵€鏈夎妭鐐圭殑浣嶇疆锛岀‘淇濈埗鑺傜偣鍨傜洿灞呬腑鍦ㄥ瓙鑺傜偣涓棿
        self._reposition_all_nodes()
        
        # 寮哄埗鏇存柊鐢诲竷
        self.canvas.update()
        
        # 鏇存柊婊氬姩鍖哄煙
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox(tk.ALL)
        if bbox:
            # 鎵╁睍杈圭晫妗嗭紝纭繚鎵€鏈夎妭鐐归兘鑳借鐪嬪埌
            x1, y1, x2, y2 = bbox
            padding = 100  # 澧炲姞杈硅窛
            self.canvas.config(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))
            
            # 婊氬姩鍒扮敾甯冨乏涓婅锛岀‘淇濈敤鎴峰彲浠ヤ粠寮€濮嬫煡锟?
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
        else:
            # 濡傛灉娌℃湁鑺傜偣锛岃缃粯璁ゆ粴鍔ㄥ尯锟?
            self.canvas.config(scrollregion=(0, 0, 1000, 800))
    
    def _reposition_all_nodes(self):
        """閲嶆柊璁＄畻鎵€鏈夎妭鐐圭殑浣嶇疆锛屽疄鐜版爲褰㈠眰绾у竷灞€
        
        甯冨眬瑙勫垯:
        1. 鏍硅妭鐐瑰湪鏈€宸︿晶
        2. 灞傜骇浠庡乏鍒板彸灞曞紑锛屾瘡锟?X 鍧愭爣鍥哄畾
        3. 鐖惰妭鐐逛笌绗竴涓瓙鑺傜偣鍨傜洿瀵归綈
        4. 鍚岀骇鑺傜偣鍨傜洿绱у噾鎺掑垪
        5. 浣跨敤鐩磋鎶樼嚎杩炴帴
        """
        if not self.nodes:
            return
        
        # 鏋勫缓鐖跺瓙鍏崇郴鏄犲皠
        parent_to_children = {}
        root_nodes = []
        
        for node_id, node in self.nodes.items():
            parent_id = node.get("parent_id")
            if parent_id is None or parent_id not in self.nodes:
                root_nodes.append(node)
            else:
                if parent_id not in parent_to_children:
                    parent_to_children[parent_id] = []
                parent_to_children[parent_id].append(node)
        
        if not root_nodes:
            return
        
        # 瀵规瘡涓埗鑺傜偣鐨勫瓙鑺傜偣锟?ID 鎺掑簭锛岀‘淇濋『搴忎竴锟?
        for parent_id in parent_to_children:
            parent_to_children[parent_id].sort(key=lambda x: x["id"])
        
        # 璁＄畻姣忎釜灞傜骇鐨勬按骞充綅锟?
        level_x = {}
        max_level = max(node.get("level", 0) for node in self.nodes.values())
        for level in range(max_level + 1):
            level_x[level] = 100 + level * NODE_SPACING
        
        vertical_spacing = 15  # 瀛愯妭鐐逛箣闂寸殑鍨傜洿闂磋窛
        
        # 鑾峰彇鑺傜偣鐨勫疄闄呴珮搴︼紙鑰冭檻鐗规畩褰㈢姸锟?
        def get_node_height(node):
            device_type = node.get("device_type", "default")
            base_height = NODE_HEIGHT
            # 鎵€鏈夊舰鐘剁殑瀹為檯杈圭晫妗嗛珮搴﹂兘锟?NODE_HEIGHT
            # 涓嶉渶瑕侀澶栫┖闂达紝鍥犱负鎵€鏈夊舰鐘剁殑椤剁偣閮藉湪杈圭晫妗嗚竟锟?
            return base_height
        
        # 鑾峰彇褰㈢姸鐨勯噸锟?Y 鍋忕Щ锛堢浉瀵逛簬褰㈢姸杈圭晫妗嗛《閮級
        def get_center_offset(node):
            """杩斿洖褰㈢姸閲嶅績鐩稿浜庤竟鐣屾涓績锟?Y 鍋忕Щ锟?""
            device_type = node.get("device_type", "default")
            # 妞渾銆佺煩褰€佽彵褰€佸叚杈瑰舰鐨勯噸蹇冨湪涓績
            if device_type in ["ellipse", "circle", "rectangle", "rounded_rectangle", "diamond", "hexagon"]:
                return 0
            # 涓夎褰㈢殑閲嶅績鍦ㄤ粠搴曢儴锟?1/3 楂樺害澶勶紝鍗充粠椤堕儴锟?2/3 楂樺害锟?
            # 杈圭晫妗嗕腑蹇冨湪 height/2锛岄噸蹇冨湪 2*height/3锛屽亸锟?= 2*height/3 - height/2 = height/6
            elif device_type == "triangle":
                return NODE_HEIGHT / 6
            # 浜旇竟褰㈢殑閲嶅績鐣ュ亸锟?
            elif device_type == "pentagon":
                return NODE_HEIGHT / 12
            # 鏄熷舰鐨勯噸蹇冪暐鍋忎笂
            elif device_type == "star":
                return NODE_HEIGHT / 12
            # 姊舰鐨勯噸蹇冪暐鍋忎笅
            elif device_type == "trapezoid":
                return -NODE_HEIGHT / 12
            return 0
        
        # 閫掑綊璁＄畻瀛愭爲楂樺害
        def calculate_subtree_height(node):
            children = parent_to_children.get(node["id"], [])
            if not children:
                return get_node_height(node)
            total = sum(calculate_subtree_height(child) for child in children)
            return total + vertical_spacing * (len(children) - 1)
        
        # 閫掑綊鍒嗛厤浣嶇疆
        def assign_positions(node, start_y):
            node["x"] = level_x.get(node.get("level", 0), 100)
            children = parent_to_children.get(node["id"], [])
            node_height = get_node_height(node)
            
            if not children:
                # 鍙跺瓙鑺傜偣
                node["y"] = start_y
                return node_height
            
            # 鏈夊瓙鑺傜偣锛氬厛璁＄畻鎵€鏈夊瓙鑺傜偣鐨勪綅锟?
            current_y = start_y
            for i, child in enumerate(children):
                child_height = assign_positions(child, current_y)
                if i == 0:
                    # 鐖惰妭鐐逛笌绗竴涓瓙鑺傜偣瀵归綈
                    node["y"] = current_y
                current_y += child_height + vertical_spacing
            
            return current_y - start_y
        
        # 浠庢牴鑺傜偣寮€濮嬪竷灞€
        current_y = 50
        for root in root_nodes:
            height = calculate_subtree_height(root)
            # 鍨傜洿灞呬腑 - 浣跨敤 800 浣滀负鐢诲竷楂樺害锛岃€屼笉锟?600
            start_y = current_y + (800 - height) / 2 if height < 800 else current_y
            assign_positions(root, start_y)
            current_y += height + 50
        
        # 绉诲姩鑺傜偣鍒版柊浣嶇疆
        self._move_all_nodes_to_new_positions()
    
    def _move_all_nodes_to_new_positions(self):
        """绉诲姩鎵€鏈夎妭鐐瑰拰杩炴帴绾垮埌鏂扮殑浣嶇疆"""
        # 鍒犻櫎鎵€鏈夎繛鎺ョ嚎
        for link in self.links:
            self.canvas.delete(link.get("id"))
        self.links = []
        
        # 绉诲姩姣忎釜鑺傜偣鍒版柊浣嶇疆
        for node_id, node in self.nodes.items():
            try:
                # 浣跨敤 bbox 鑾峰彇杈圭晫妗嗭紝鑰屼笉锟?coords锛坈oords 杩斿洖鐨勬槸椤剁偣鍧愭爣锛屼笉鏄竟鐣屾锟?
                bbox = self.canvas.bbox(node["shape"])
                if bbox:
                    current_x = bbox[0]  # 宸﹁竟锟?
                    current_y = bbox[1]  # 涓婅竟锟?
                else:
                    continue
            except (IndexError, TypeError, ValueError):
                continue
            dx = node["x"] - current_x
            dy = node["y"] - current_y
            # 娣诲姞 Y 杞村亸绉婚噺锛屽悜涓婄Щ锟?3 鍍忕礌锛屼慨姝ｈ繛鎺ョ嚎浣嶇疆
            dy -= 3
            # 绉诲姩鎵€鏈夌粦瀹氫簡 node_id tag 鐨勫锟?
            items_to_move = self.canvas.find_withtag(node_id)
            for item in items_to_move:
                self.canvas.move(item, dx, dy)
        
        # 閲嶆柊缁樺埗杩炴帴锟?
        self._redraw_all_links()
    
    def _redraw_all_links(self):
        """閲嶆柊缁樺埗鎵€鏈夎繛鎺ョ嚎锛堜娇鐢ㄧ洿瑙掓姌绾匡級"""
        # 鍏堝垹闄ゆ墍鏈夋棫鐨勮繛鎺ョ嚎
        for item in self.canvas.find_withtag("link"):
            self.canvas.delete(item)
        
        # 娓呯┖ links 鍒楄〃
        self.links = []
        
        # 閲嶆柊缁樺埗鎵€鏈夎繛鎺ョ嚎
        for node_id, node in self.nodes.items():
            parent_id = node.get("parent_id")
            if parent_id and parent_id in self.nodes:
                source_node = self.nodes[parent_id]
                target_node = node
                
                # 璁＄畻杩炴帴鐐癸紙浠庢簮鑺傜偣鍙充晶鍒扮洰鏍囪妭鐐瑰乏渚э級
                # 鎵€鏈夊舰鐘剁殑宸﹀彸椤剁偣閮藉湪杈圭晫妗嗚竟缂橈紝缁熶竴浣跨敤杈圭晫妗嗗潗锟?
                # 娣诲姞 3 鍍忕礌鍋忕Щ閲忥紝閬垮厤杩炴帴绾跨┛鍏ヨ妭锟?
                x1 = source_node["x"] + NODE_WIDTH + 13  # 婧愯妭鐐瑰彸锟?+ 13 鍍忕礌鍋忕Щ
                y1 = source_node["y"] + NODE_HEIGHT / 2  # 鍨傜洿涓績
                x2 = target_node["x"] - 0  # 鐩爣鑺傜偣宸︿晶 - 0 鍍忕礌鍋忕Щ
                y2 = target_node["y"] + NODE_HEIGHT / 2  # 鍨傜洿涓績
                
                # 鍒涘缓鐩磋鎶樼嚎
                mid_x = x1 + (x2 - x1) / 2  # 杞姌锟?X 鍧愭爣
                
                # 缁樺埗鎶樼嚎锛氭按锟?锟?鍨傜洿 锟?姘村钩
                line = self.canvas.create_line(
                    x1, y1,          # 璧风偣锛堟簮鑺傜偣鍙充晶涓績锟?
                    mid_x, y1,       # 杞姌锟?1锛堟按骞冲欢浼革級
                    mid_x, y2,       # 杞姌锟?2锛堝瀭鐩村悜锟?涓婏級
                    x2, y2,          # 缁堢偣锛堢洰鏍囪妭鐐瑰乏渚т腑蹇冿級
                    arrow=tk.LAST,
                    width=2,
                    fill="#CCCCCC",
                    smooth=False,  # 涓嶄娇鐢ㄥ钩婊戯紝淇濇寔鐩磋
                    tags="link"
                )
                self.links.append({
                    "source": parent_id,
                    "target": node_id,
                    "line": line
                })
        
        # 灏嗘墍鏈夎繛鎺ョ嚎鎻愬崌鍒版渶涓婂眰锛岀‘淇濊繛鎺ョ嚎涓嶈鑺傜偣閬尅
        for link in self.links:
            self.canvas.tag_raise(link["line"])
    
    def auto_scale_to_fit(self, retry_count=0):
        """鑷姩缂╂斁鐢诲竷浠ラ€傚簲鎵€鏈夎妭锟?""
        bbox = self.canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        # 纭繚鐢诲竷宸插畬鍏ㄥ垵濮嬪寲
        self.canvas.update_idletasks()
        
        # 鑾峰彇鐢诲竷灏哄
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 濡傛灉鐢诲竷灏哄杩樻病鏈夋纭幏鍙栵紝灏濊瘯浠庣埗瀹瑰櫒鑾峰彇
        if canvas_width <= 1 or canvas_height <= 1:
            # 鍏堟洿鏂扮埗瀹瑰櫒
            if self.canvas_frame:
                self.canvas_frame.update_idletasks()
                canvas_width = self.canvas_frame.winfo_width()
                canvas_height = self.canvas_frame.winfo_height()
        
        # 濡傛灉杩樻槸娌℃湁姝ｇ‘鑾峰彇灏哄锛屽欢杩熼噸璇曪紙鏈€澶氶噸锟?0娆★紝姣忔50ms锛屽叡2.5绉掞級
        if canvas_width <= 1 or canvas_height <= 1:
            if retry_count < 50:
                # 寤惰繜閲嶈瘯锛岀瓑寰匞UI鍒濆鍖栧畬锟?
                self.canvas.after(50, lambda: self.auto_scale_to_fit(retry_count + 1))
                return
            else:
                # 澶氭閲嶈瘯鍚庝粛鏃犳硶鑾峰彇灏哄锛岃褰曟棩蹇楀苟杩斿洖
                print(f"璀﹀憡: 鏃犳硶鑾峰彇鐢诲竷灏哄锛岄噸璇曟锟? {retry_count}")
                return
        
        # 璁＄畻鎵€鏈夎妭鐐圭殑杈圭晫锟?
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        
        if content_width <= 0 or content_height <= 0:
            return
        
        # 璁＄畻缂╂斁姣斾緥锛屼娇鐢ㄦ洿灏忕殑杈硅窛浠ュ厖鍒嗗埄鐢ㄧ┖锟?
        margin = 15  # 鏈€灏忚竟璺濓紝璁╁唴瀹规洿锟?
        scale_x = (canvas_width - 2 * margin) / content_width
        scale_y = (canvas_height - 2 * margin) / content_height
        scale_factor = min(scale_x, scale_y)
        
        # 闄愬埗缂╂斁鑼冨洿锛堝厑璁告洿澶х殑缂╂斁姣斾緥锛屾渶澶у彲鏀惧ぇ鍒板師濮嬬殑1鍊嶏級
        scale_factor = max(0.5, min(scale_factor, 1.0))
        
        # 搴旂敤缂╂斁
        if scale_factor != 1.0:
            # 璁＄畻缂╂斁涓績锛堝唴瀹逛腑蹇冿級
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            # 缂╂斁鎵€鏈夊唴锟?
            self.canvas.scale(tk.ALL, center_x, center_y, scale_factor, scale_factor)
        
        # 鏇存柊婊氬姩鍖哄煙
        self.canvas.update_idletasks()
        new_bbox = self.canvas.bbox(tk.ALL)
        if new_bbox:
            x1, y1, x2, y2 = new_bbox
            
            # 鑾峰彇鐢诲竷瀹為檯灏哄
            actual_width = self.canvas.winfo_width()
            actual_height = self.canvas.winfo_height()
            
            # 璁＄畻鍐呭瀹為檯鍗犳嵁鐨勫尯锟?
            content_width = x2 - x1
            content_height = y2 - y1
            
            # 濡傛灉鍐呭灏忎簬鐢诲竷灏哄锛屼笉娣诲姞棰濆杈硅窛锛岄伩鍏嶆樉绀烘粴鍔ㄦ潯
            if content_width < actual_width and content_height < actual_height:
                # 鍐呭宸茬粡閫傚悎鐢诲竷锛屼娇鐢ㄦ渶灏忚竟璺濓紝纭繚婊氬姩鍖哄煙涓嶈秴杩囩敾锟?
                padding = 15
            else:
                # 鍐呭瓒呭嚭鐢诲竷锛屾坊鍔犻€傚綋杈硅窛
                padding = 30
            
            self.canvas.config(scrollregion=(x1 - padding, y1 - padding, x2 + padding, y2 + padding))
        
        # 鏇存柊缂╂斁鍥犲瓙
        self.scale *= scale_factor
        
        # 婊氬姩鍒扮敾甯冨乏涓婅锛岀‘淇濈敤鎴峰彲浠ヤ粠寮€濮嬫煡锟?
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
    
    def _filter_nodes(self, network_data):
        """杩囨护鑺傜偣
        
        Args:
            network_data: 缃戠粶鏁版嵁
        
        Returns:
            list: 杩囨护鍚庣殑鑺傜偣鍒楄〃
        """
        def collect_nodes(data):
            """閫掑綊鏀堕泦鎵€鏈夎妭锟?""
            nodes = []
            nodes.append(data)
            if "children" in data and data["children"]:
                for child in data["children"]:
                    if isinstance(child, dict):
                        child["parent_id"] = data["id"]  # 娣诲姞鐖惰妭鐐笽D
                        nodes.extend(collect_nodes(child))
            return nodes
        
        # 鏀堕泦鎵€鏈夎妭锟?
        nodes = []
        if isinstance(network_data, list):
            # 濡傛灉network_data鏄垪琛紝閬嶅巻姣忎釜鍏冪礌
            for item in network_data:
                if isinstance(item, dict):
                    nodes.extend(collect_nodes(item))
        elif isinstance(network_data, dict):
            # 濡傛灉network_data鏄瓧鍏革紝鐩存帴鏀堕泦
            nodes = collect_nodes(network_data)
        
        # 杩欓噷鍙互瀹炵幇鏇村鏉傜殑杩囨护閫昏緫
        # 渚嬪鏍规嵁鑺傜偣绫诲瀷銆佺姸鎬佺瓑杩涜杩囨护
        return nodes
    
    def set_filter_level(self, level):
        """璁剧疆杩囨护绾у埆
        
        Args:
            level: 杩囨护绾у埆锟?琛ㄧず鏄剧ず鎵€鏈夎妭鐐癸紝1琛ㄧず鍙樉绀轰竴绾ц妭鐐癸紝浠ユ绫绘帹
        """
        self.filter_level = level
        if self.data_callback:
            self.refresh_data()
    
    def set_max_nodes(self, max_nodes):
        """璁剧疆鏈€澶ц妭鐐规暟
        
        Args:
            max_nodes: 鏈€澶ц妭鐐规暟
        """
        self.max_nodes = max_nodes
        if self.data_callback:
            self.refresh_data()
    
    def on_mouse_move(self, event):
        """榧犳爣绉诲姩浜嬩欢锛岀敤浜庢樉绀鸿妭鐐规偓鍋滆鎯呭拰鎮仠鏁堟灉"""
        # 灏嗙獥鍙ｅ潗鏍囪浆鎹负鐢诲竷鍧愭爣锛堣€冭檻婊氬姩锟?
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # 鏌ユ壘榧犳爣涓嬫柟鐨勮妭锟?
        hovered_node = None
        
        # 浣跨敤 find_overlapping 鏌ユ壘涓庨紶鏍囦綅缃噸鍙犵殑鎵€鏈夊锟?
        overlapping = self.canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
        
        # 閫氳繃 tag 鍖归厤鑺傜偣锛堜笉鍐嶅彧渚濊禆 shape 瀵硅薄锟?
        # 鍥犱负妞渾绛夊舰鐘剁殑杈规锟?fill="" 鏃犳硶瑕嗙洊鍐呴儴鍖哄煙锟?
        # 鎵€浠ユ敼鐢ㄧ粺涓€ tag 鏉ヨ瘑鍒紶鏍囨墍鍦ㄧ殑鑺傜偣
        for item_id in reversed(list(overlapping)):
            tags = self.canvas.gettags(item_id)
            for tag in tags:
                if tag in self.nodes:  # tag 灏辨槸 node_id锛堝 "node_0"锟?
                    hovered_node = self.nodes[tag]
                    break
            if hovered_node:
                break
        
        # 鍙湪鎮仠鑺傜偣鍙戠敓鍙樺寲鏃舵墠澶勭悊鏍峰紡鍒囨崲
        if hovered_node != self.hovered_node:
            # 鎭㈠涔嬪墠鎵€鏈夎妭鐐圭殑鍘熷鏍峰紡
            self._restore_all_hover_styles()
            
            # 鍋滄鏃х殑杞瀹氭椂锟?
            self._stop_hover_polling()
            
            # 鏇存柊鎮仠鐘讹拷?
            self.hovered_node = hovered_node
            
            if hovered_node:
                # 搴旂敤鏂拌妭鐐圭殑鎮仠鏍峰紡
                self._apply_hover_style(hovered_node)
                self.last_mouse_x = event.x_root
                self.last_mouse_y = event.y_root
                
                # 寤惰繜鏄剧ず鎻愮ず
                if self.tooltip_timer:
                    try:
                        self.canvas.after_cancel(self.tooltip_timer)
                    except Exception:
                        pass
                self.tooltip_timer = self.canvas.after(100, self._delayed_show_tooltip)
                
                # 鍚姩杞妫€娴嬪畾鏃跺櫒锛堝叧閿細瑙ｅ喅榧犳爣鍋滃湪绌虹櫧澶勪笉瑙﹀彂Motion鐨勯棶棰橈級
                self._start_hover_polling()
            else:
                # 榧犳爣涓嶅湪浠讳綍鑺傜偣涓婏紝闅愯棌鎻愮ず
                if self.tooltip_timer:
                    try:
                        self.canvas.after_cancel(self.tooltip_timer)
                    except Exception:
                        pass
                self.tooltip_timer = None
                self.hide_tooltip()

    def _start_hover_polling(self):
        """鍚姩鎮仠杞妫€娴嬪畾鏃跺櫒
        
        锟?0ms妫€娴嬩竴娆￠紶鏍囨槸鍚︿粛鍦ㄥ綋鍓嶆偓鍋滆妭鐐逛笂锟?
        瑙ｅ喅榧犳爣鍋滃湪鐢诲竷绌虹櫧澶勪笉鍐嶈Е鍙慚otion浜嬩欢瀵艰嚧楂樹寒娈嬬暀鐨勯棶锟?
        """
        self._stop_hover_polling()
        self._hover_poll_job = self.canvas.after(50, self._check_hover_state)

    def _stop_hover_polling(self):
        """鍋滄鎮仠杞妫€娴嬪畾鏃跺櫒"""
        if self._hover_poll_job:
            try:
                self.canvas.after_cancel(self._hover_poll_job)
            except Exception:
                pass
            self._hover_poll_job = None

    def _check_hover_state(self):
        """杞妫€娴嬪綋鍓嶉紶鏍囦綅缃槸鍚︿粛鍦ㄦ偓鍋滆妭鐐逛笂
        
        濡傛灉榧犳爣宸茬寮€褰撳墠鎮仠鑺傜偣锛岀珛鍗虫仮澶嶆牱寮忓苟闅愯棌tooltip
        """
        if not self.hovered_node:
            return
        
        try:
            # 鑾峰彇褰撳墠榧犳爣鍦ㄧ敾甯冧笂鐨勫潗锟?
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            
            # 杞崲涓虹敾甯冨潗锟?
            canvas_x = self.canvas.canvasx(x)
            canvas_y = self.canvas.canvasy(y)
            
            # 妫€鏌ラ紶鏍囨槸鍚︿粛鍦ㄥ綋鍓嶆偓鍋滆妭鐐逛笂锛堥€氳繃 tag 鍖归厤锟?
            overlapping = self.canvas.find_overlapping(canvas_x, canvas_y, canvas_x, canvas_y)
            still_on_node = False
            for item_id in overlapping:
                tags = self.canvas.gettags(item_id)
                if self.hovered_node["id"] in tags:  # 妫€锟?tag 鏄惁鍖呭惈褰撳墠鑺傜偣锟?node_id
                    still_on_node = True
                    break
            
            if not still_on_node:
                # 榧犳爣宸茬寮€鑺傜偣锛屾仮澶嶆墍鏈夋牱锟?
                self._restore_all_hover_styles()
                self.hovered_node = None
                self.hide_tooltip()
                return
            
            # 浠嶅湪鑺傜偣涓婏紝缁х画杞
            self._hover_poll_job = self.canvas.after(50, self._check_hover_state)
        except (tk.TclError, Exception):
            # 鐢诲竷鍙兘宸茶閿€姣侊紝鍋滄杞
            pass

    def _restore_all_hover_styles(self):
        """鎭㈠鎵€鏈夊浜庢偓鍋滅姸鎬佺殑鑺傜偣鐨勫師濮嬫牱锟?""
        for node_id, node in list(self.nodes.items()):
            if "original_style" in node:
                self._restore_node_style(node)

    def _apply_hover_style(self, node):
        """搴旂敤鑺傜偣鎮仠鏍峰紡
        
        Args:
            node: 鑺傜偣淇℃伅
        """
        # 淇濆瓨鍘熷鏍峰紡
        if "original_style" not in node:
            # 鑾峰彇瀹藉害鍊硷紝澶勭悊绌哄瓧绗︿覆鍜屾诞鐐规暟鎯呭喌
            width_str = self.canvas.itemcget(node["shape"], "width")
            try:
                line_width = int(float(width_str)) if width_str else 2
            except (ValueError, TypeError):
                line_width = 2
            node["original_style"] = {
                "outline": self.canvas.itemcget(node["shape"], "outline"),
                "line_width": line_width
            }
        
        # 鏇存敼鑺傜偣鏍峰紡 - 浠呬慨鏀硅竟妗嗗拰瀹藉害
        self.canvas.itemconfig(node["shape"], 
                             outline="#ffffff", 
                             width=3)
        
        # 鎻愬崌鑺傜偣鍒伴《锟?
        self.canvas.tag_raise(node["shape"])
        self.canvas.tag_raise(node["text"])
        self.canvas.tag_raise(node["subnet_text"])
        self.canvas.tag_raise(node["ip_info_text"])

    def _restore_node_style(self, node):
        """鎭㈠鑺傜偣鍘熷鏍峰紡
        
        Args:
            node: 鑺傜偣淇℃伅
        """
        if "original_style" in node:
            original = node["original_style"]
            
            # 鎭㈠鑺傜偣鏍峰紡
            self.canvas.itemconfig(node["shape"], 
                                 outline=original["outline"], 
                                 width=original["line_width"])
            
            # 鍒犻櫎鍘熷鏍峰紡灞烇拷?
            del node["original_style"]
    
    def _delayed_show_tooltip(self):
        """寤惰繜鏄剧ず鎻愮ず绐楀彛"""
        self.tooltip_timer = None
        if self.hovered_node:
            self.show_tooltip(self.last_mouse_x, self.last_mouse_y, self.hovered_node)
    
    def show_tooltip(self, x_root, y_root, node):
        """鏄剧ず鑺傜偣鎮仠鎻愮ず
        
        Args:
            x_root: 榧犳爣鍦ㄥ睆骞曚笂锟?x 鍧愭爣
            y_root: 榧犳爣鍦ㄥ睆骞曚笂锟?y 鍧愭爣
            node: 鑺傜偣淇℃伅
        """
        # 鍏堥攢姣佹棫鐨則ooltip
        self.hide_tooltip()
        
        # 鍒涘缓鎻愮ず绐楀彛
        self.tooltip = tk.Toplevel(self.parent)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x_root + 15}+{y_root + 10}")
        
        # 鍒涘缓鎻愮ず鍐呭
        frame = tk.Frame(self.tooltip, bg="#333", padx=10, pady=5)
        frame.pack()
        
        # 缁戝畾tooltip鐨凩eave浜嬩欢锛氬綋榧犳爣绂诲紑tooltip鏃朵篃鎭㈠鏍峰紡
        def on_tooltip_leave(event):
            self._restore_all_hover_styles()
            self.hovered_node = None
            self.hide_tooltip()
            self._stop_hover_polling()
        
        self.tooltip.bind("<Leave>", on_tooltip_leave)
        
        # 鑾峰彇瀛椾綋璁剧疆
        font_family, font_size = get_current_font_settings()
        
        # 娣诲姞鎻愮ず鏂囨湰
        tk.Label(
            frame, 
            text=node["name"], 
            font=(font_family, font_size, "bold"), 
            fg="#fff", 
            bg="#333"
        ).pack(anchor=tk.W)
        
        tk.Label(
            frame, 
            text=str(node["subnet"]), 
            font=(font_family, font_size - 1), 
            fg="#ddd", 
            bg="#333"
        ).pack(anchor=tk.W)
        
        if node["ip_info"]:
            allocated = node["ip_info"].get("allocated", 0)
            reserved = node["ip_info"].get("reserved", 0)
            available = node["ip_info"].get("available", 0)
            total = node["ip_info"].get("total", 0)
            # 璁＄畻鍓╀綑IP鏁帮細鎬籌P锟?- 缃戠粶鍦板潃鍜屽箍鎾湴鍧€ - 宸插垎閰岻P - 宸蹭繚鐣橧P
            # 缃戠粶鍦板潃鍜屽箍鎾湴鍧€鍚勫崰1涓狪P
            network_broadcast = 2 if total > 2 else 0
            remaining = max(0, total - network_broadcast - allocated - reserved)
            tk.Label(
                frame, 
                text=f"宸插垎锟? {allocated}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"宸蹭繚锟? {reserved}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"宸查噴锟? {available}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"鍓╀綑IP: {remaining}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
            tk.Label(
                frame, 
                text=f"鎬籌P: {total}", 
                font=(font_family, font_size - 1), 
                fg="#ddd", 
                bg="#333"
            ).pack(anchor=tk.W)
    
    def hide_tooltip(self):
        """闅愯棌鎻愮ず绐楀彛"""
        # 鍙栨秷瀹氭椂锟?
        if self.tooltip_timer:
            try:
                self.canvas.after_cancel(self.tooltip_timer)
            except Exception:
                pass
            self.tooltip_timer = None
        
        # 閿€姣佹彁绀虹獥锟?
        if hasattr(self, 'tooltip') and self.tooltip:
            try:
                self.tooltip.destroy()
            except Exception:
                pass
            self.tooltip = None
    
    def on_canvas_leave(self, event):
        """榧犳爣绂诲紑鐢诲竷浜嬩欢澶勭悊"""
        # 鍋滄杞妫€锟?
        self._stop_hover_polling()
        
        # 鎭㈠鎵€鏈夎妭鐐圭殑鍘熷鏍峰紡
        self._restore_all_hover_styles()
        
        # 闅愯棌鎻愮ず绐楀彛
        self.hide_tooltip()
    
    def on_canvas_frame_configure(self, event):
        """褰撶埗瀹瑰櫒澶у皬鍙樺寲鏃惰皟鏁寸敾甯冨ぇ锟?""
        # 鑾峰彇鐖跺鍣ㄧ殑鏂板ぇ锟?
        width = event.width
        height = event.height
        
        # 璋冩暣鐢诲竷澶у皬
        self.canvas.config(width=width, height=height)
        
        # 閲嶇疆鎮仠鐘讹拷?
        self.hovered_node = None
        
        # 鏇存柊鍏ㄥ睆鎸夐挳浣嶇疆
        self._update_fullscreen_button_position()
    
    def _create_fullscreen_button(self):
        """鍒涘缓鍏ㄥ睆鏄剧ず鎸夐挳"""
        self.fullscreen_button = tk.Button(
            self.canvas_frame,
            text="锟?,
            command=self.toggle_fullscreen,
            bg="#3498db",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=4,
            pady=2,
            font=("Arial", 10),
            cursor="hand2"
        )
        self.fullscreen_button.place(relx=0.985, rely=0.01, anchor=tk.NE)
        self.fullscreen_button.bind("<Enter>", lambda e: self.fullscreen_button.config(bg="#2980b9"))
        self.fullscreen_button.bind("<Leave>", lambda e: self.fullscreen_button.config(bg="#3498db"))
        
        # 鍏ㄥ睆鐘讹拷?
        self.is_fullscreen = False
    
    def _update_fullscreen_button_position(self):
        """鏇存柊鍏ㄥ睆鎸夐挳浣嶇疆"""
        if hasattr(self, 'fullscreen_button'):
            self.fullscreen_button.place(relx=0.97, rely=0.02, anchor=tk.NE)
    
    def toggle_fullscreen(self):
        """鍒囨崲鍏ㄥ睆鏄剧ず鐘讹拷?""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """杩涘叆鍏ㄥ睆鏄剧ず妯″紡"""
        # 淇濆瓨褰撳墠鐘讹拷?
        self.original_parent = self.canvas_frame.winfo_parent()
        self.original_geometry = self.canvas_frame.winfo_toplevel().geometry()
        # 淇濆瓨褰撳墠缂╂斁鍥犲瓙
        self.original_scale = self.scale
        
        # 鑾峰彇灞忓箷灏哄
        screen_width = self.canvas.winfo_screenwidth()
        screen_height = self.canvas.winfo_screenheight()
        
        # 鍒涘缓鍏ㄥ睆椤跺眰绐楀彛
        self.fullscreen_window = tk.Toplevel()
        self.fullscreen_window.title("缃戠粶鎷撴墤锟?- 鍏ㄥ睆妯″紡")
        self.fullscreen_window.attributes("-fullscreen", True)
        self.fullscreen_window.config(bg=BACKGROUND_COLOR)
        
        # 鍒涘缓鏂扮殑鐢诲竷妗嗘灦
        self.fullscreen_canvas_frame = Frame(self.fullscreen_window, bg=BACKGROUND_COLOR)
        self.fullscreen_canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 鍒涘缓鏂扮敾锟?
        self.fullscreen_canvas = Canvas(
            self.fullscreen_canvas_frame,
            bg=BACKGROUND_COLOR
        )
        self.fullscreen_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 澶嶅埗褰撳墠鐢诲竷鍐呭鍒板叏灞忕敾锟?
        self._copy_canvas_content(self.canvas, self.fullscreen_canvas)
        
        # 閲嶇疆缂╂斁鍥犲瓙锟?.0锛堝師濮嬪ぇ灏忥級锛岀‘淇濊嚜閫傚簲缂╂斁鍩轰簬鍘熷灏哄璁＄畻
        self.scale = 1.0
        
        # 鍏ㄥ睆妯″紡涓嬭繘琛岃嚜閫傚簲缂╂斁
        self._auto_scale_to_fit_fullscreen()
        
        # 娣诲姞閫€鍑哄叏灞忔寜锟?
        self.exit_fullscreen_button = tk.Button(
            self.fullscreen_canvas_frame,
            text="锟?,
            command=self.exit_fullscreen,
            bg="#e74c3c",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=4,
            pady=2,
            font=("Arial", 10),
            cursor="hand2"
        )
        self.exit_fullscreen_button.place(relx=0.99, rely=0.01, anchor=tk.NE)
        self.exit_fullscreen_button.bind("<Enter>", lambda e: self.exit_fullscreen_button.config(bg="#c0392b"))
        self.exit_fullscreen_button.bind("<Leave>", lambda e: self.exit_fullscreen_button.config(bg="#e74c3c"))
        
        # 鍒涘缓缂╂斁鎺у埗闈㈡澘
        self._create_fullscreen_controls()
        
        # 缁戝畾浜嬩欢
        self.fullscreen_canvas.bind("<ButtonPress-1>", self.start_drag_fullscreen)
        self.fullscreen_canvas.bind("<B1-Motion>", self.drag_fullscreen)
        self.fullscreen_canvas.bind("<MouseWheel>", self.on_mouse_wheel_fullscreen)
        
        # 鏇存柊鐘讹拷?
        self.is_fullscreen = True
    
    def exit_fullscreen(self):
        """閫€鍑哄叏灞忔樉绀烘ā锟?""
        if hasattr(self, 'fullscreen_window') and self.fullscreen_window.winfo_exists():
            # 閿€姣佸叏灞忕獥锟?
            self.fullscreen_window.destroy()
            del self.fullscreen_window
            
            # 鎭㈠鍘熷缂╂斁鍥犲瓙
            if hasattr(self, 'original_scale'):
                self.scale = self.original_scale
            
            # 鏇存柊鐘讹拷?
            self.is_fullscreen = False
    
    def _copy_canvas_content(self, source_canvas, target_canvas):
        """澶嶅埗鐢诲竷鍐呭"""
        # 娓呯┖鐩爣鐢诲竷
        target_canvas.delete(tk.ALL)
        
        # 鑾峰彇婧愮敾甯冪殑鎵€鏈夐」锟?
        items = source_canvas.find_all()
        
        for item in items:
            # 鑾峰彇椤圭洰绫诲瀷
            item_type = source_canvas.type(item)
            
            # 鑾峰彇椤圭洰灞烇拷?
            coords = source_canvas.coords(item)
            
            if item_type == "polygon":
                fill = source_canvas.itemcget(item, "fill")
                outline = source_canvas.itemcget(item, "outline")
                smooth = source_canvas.itemcget(item, "smooth")
                target_canvas.create_polygon(*coords, fill=fill, outline=outline, smooth=smooth)
            elif item_type == "oval":
                fill = source_canvas.itemcget(item, "fill")
                outline = source_canvas.itemcget(item, "outline")
                width = source_canvas.itemcget(item, "width")
                target_canvas.create_oval(*coords, fill=fill, outline=outline, width=width)
            elif item_type == "line":
                fill = source_canvas.itemcget(item, "fill")
                width = source_canvas.itemcget(item, "width")
                target_canvas.create_line(*coords, fill=fill, width=width)
            elif item_type == "text":
                text = source_canvas.itemcget(item, "text")
                fill = source_canvas.itemcget(item, "fill")
                font = source_canvas.itemcget(item, "font")
                anchor = source_canvas.itemcget(item, "anchor")
                target_canvas.create_text(*coords, text=text, fill=fill, font=font, anchor=anchor)
    
    def _create_fullscreen_controls(self):
        """鍒涘缓鍏ㄥ睆妯″紡涓嬬殑缂╂斁鎺у埗闈㈡澘"""
        # 鍒涘缓鎺у埗闈㈡澘妗嗘灦
        self.control_frame = tk.Frame(self.fullscreen_canvas_frame, bg="#34495e", bd=1, relief=tk.SUNKEN)
        self.control_frame.place(relx=0.99, rely=0.99, anchor=tk.SE)
        
        # 鍒涘缓鏀惧ぇ鎸夐挳
        self.zoom_in_button = tk.Button(
            self.control_frame,
            text="锟?,
            command=lambda: self._zoom_fullscreen(1.1),
            bg="#27ae60",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )
        self.zoom_in_button.grid(row=0, column=0, padx=2, pady=2)
        self.zoom_in_button.bind("<Enter>", lambda e: self.zoom_in_button.config(bg="#2ecc71"))
        self.zoom_in_button.bind("<Leave>", lambda e: self.zoom_in_button.config(bg="#27ae60"))
        
        # 鍒涘缓缂╁皬鎸夐挳
        self.zoom_out_button = tk.Button(
            self.control_frame,
            text="锟?,
            command=lambda: self._zoom_fullscreen(0.9),
            bg="#e67e22",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            font=("Arial", 12, "bold"),
            cursor="hand2"
        )
        self.zoom_out_button.grid(row=1, column=0, padx=2, pady=2)
        self.zoom_out_button.bind("<Enter>", lambda e: self.zoom_out_button.config(bg="#f39c12"))
        self.zoom_out_button.bind("<Leave>", lambda e: self.zoom_out_button.config(bg="#e67e22"))
        
        # 鍒涘缓閲嶇疆鎸夐挳
        self.reset_button = tk.Button(
            self.control_frame,
            text="锟?,
            command=self._reset_fullscreen_view,
            bg="#95a5a6",
            fg="white",
            borderwidth=0,
            relief=tk.FLAT,
            padx=8,
            pady=4,
            font=("Arial", 12),
            cursor="hand2"
        )
        self.reset_button.grid(row=2, column=0, padx=2, pady=2)
        self.reset_button.bind("<Enter>", lambda e: self.reset_button.config(bg="#bdc3c7"))
        self.reset_button.bind("<Leave>", lambda e: self.reset_button.config(bg="#95a5a6"))
        
        # 鍒涘缓缂╂斁姣斾緥鏄剧ず
        self.scale_label = tk.Label(
            self.control_frame,
            text=f"{int(self.scale * 100)}%",
            bg="#34495e",
            fg="white",
            font=("Arial", 10),
            padx=6,
            pady=2
        )
        self.scale_label.grid(row=3, column=0, padx=2, pady=2)
    
    def _zoom_fullscreen(self, factor):
        """鍏ㄥ睆妯″紡涓嬬缉鏀惧浘锟?""
        new_scale = self.scale * factor
        new_scale = max(0.5, min(new_scale, 2.0))
        
        scale_factor = new_scale / self.scale
        self.scale = new_scale
        
        # 鑾峰彇榧犳爣浣嶇疆浣滀负缂╂斁涓績锛堜娇鐢ㄧ敾甯冧腑蹇冿級
        bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if bbox:
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            self.fullscreen_canvas.scale(tk.ALL, center_x, center_y, scale_factor, scale_factor)
        
        # 鏇存柊缂╂斁姣斾緥鏄剧ず
        self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _reset_fullscreen_view(self):
        """閲嶇疆鍏ㄥ睆瑙嗗浘鍒版渶浣虫樉绀虹姸锟?""
        # 娓呯┖鐢诲竷骞堕噸鏂颁粠鍘熷鐢诲竷澶嶅埗鍐呭锛堟仮澶嶅埌鍘熷澶у皬锟?
        self.fullscreen_canvas.delete(tk.ALL)
        self._copy_canvas_content(self.canvas, self.fullscreen_canvas)
        
        # 閲嶇疆缂╂斁鍥犲瓙锟?.0锛堝師濮嬪ぇ灏忥級
        self.scale = 1.0
        
        # 鑾峰彇鐢诲竷灏哄
        self.fullscreen_canvas.update_idletasks()
        canvas_width = self.fullscreen_canvas.winfo_width()
        canvas_height = self.fullscreen_canvas.winfo_height()
        
        # 鑾峰彇鍘熷鍐呭杈圭晫妗嗭紙姝ゆ椂鏄湭缂╂斁鐨勫師濮嬪ぇ灏忥級
        bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        
        # 璁＄畻鏈€浣崇缉鏀炬瘮渚嬶紙淇濇寔30鍍忕礌杈硅窛锟?
        margin = 30
        scale_x = (canvas_width - 2 * margin) / content_width
        scale_y = (canvas_height - 2 * margin) / content_height
        scale_factor = min(scale_x, scale_y)
        
        # 闄愬埗缂╂斁鑼冨洿锛堝叏灞忔ā寮忓厑璁告洿澶х殑缂╂斁鑼冨洿锟?
        scale_factor = max(0.5, min(scale_factor, 2.0))
        
        # 浠ュ唴瀹瑰乏涓婅涓哄師鐐硅繘琛岀缉锟?
        self.fullscreen_canvas.scale(tk.ALL, x1, y1, scale_factor, scale_factor)
        
        # 鑾峰彇缂╂斁鍚庣殑鏂拌竟鐣屾
        new_bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if new_bbox:
            new_x1, new_y1, _, _ = new_bbox
            # 灏嗗唴瀹圭Щ鍔ㄥ埌宸︿笂瑙掞紝淇濇寔30鍍忕礌杈硅窛
            dx = margin - new_x1
            dy = margin - new_y1
            self.fullscreen_canvas.move(tk.ALL, dx, dy)
        
        # 鏇存柊缂╂斁鍥犲瓙鍜屾樉锟?
        self.scale = scale_factor
        self.scale_label.config(text=f"{int(self.scale * 100)}%")
    
    def _auto_scale_to_fit_fullscreen(self):
        """鍏ㄥ睆妯″紡涓嬭嚜鍔ㄧ缉鏀剧敾甯冧互閫傚簲鍏ㄥ睆绐楀彛锛屽乏涓婂锟?""
        bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if not bbox:
            return
        
        # 纭繚鐢诲竷宸插畬鍏ㄥ垵濮嬪寲
        self.fullscreen_canvas.update_idletasks()
        
        # 鑾峰彇鍏ㄥ睆鐢诲竷灏哄
        canvas_width = self.fullscreen_canvas.winfo_width()
        canvas_height = self.fullscreen_canvas.winfo_height()
        
        # 濡傛灉鐢诲竷灏哄杩樻病鏈夋纭幏鍙栵紝灏濊瘯浠庣埗瀹瑰櫒鑾峰彇
        if canvas_width <= 1 or canvas_height <= 1:
            if self.fullscreen_canvas_frame:
                self.fullscreen_canvas_frame.update_idletasks()
                canvas_width = self.fullscreen_canvas_frame.winfo_width()
                canvas_height = self.fullscreen_canvas_frame.winfo_height()
        
        # 濡傛灉杩樻槸娌℃湁姝ｇ‘鑾峰彇灏哄锛屽欢杩熼噸锟?
        if canvas_width <= 1 or canvas_height <= 1:
            self.fullscreen_canvas.after(50, self._auto_scale_to_fit_fullscreen)
            return
        
        # 璁＄畻鎵€鏈夎妭鐐圭殑杈圭晫锟?
        x1, y1, x2, y2 = bbox
        content_width = x2 - x1
        content_height = y2 - y1
        
        if content_width <= 0 or content_height <= 0:
            return
        
        # 璁＄畻缂╂斁姣斾緥锛屼娇锟?0鍍忕礌杈硅窛
        margin = 30
        scale_x = (canvas_width - 2 * margin) / content_width
        scale_y = (canvas_height - 2 * margin) / content_height
        scale_factor = min(scale_x, scale_y)
        
        # 闄愬埗缂╂斁鑼冨洿锛堝叏灞忔ā寮忓厑璁告洿澶х殑缂╂斁鑼冨洿锟?
        scale_factor = max(0.5, min(scale_factor, 2.0))
        
        # 搴旂敤缂╂斁锛堜互鍐呭宸︿笂瑙掍负鍘熺偣杩涜缂╂斁锟?
        if scale_factor != 1.0:
            self.fullscreen_canvas.scale(tk.ALL, x1, y1, scale_factor, scale_factor)
        
        # 鑾峰彇缂╂斁鍚庣殑鏂拌竟鐣屾
        new_bbox = self.fullscreen_canvas.bbox(tk.ALL)
        if new_bbox:
            new_x1, new_y1, _, _ = new_bbox
            # 灏嗗唴瀹圭Щ鍔ㄥ埌宸︿笂瑙掞紝淇濇寔30鍍忕礌杈硅窛
            dx = margin - new_x1
            dy = margin - new_y1
            self.fullscreen_canvas.move(tk.ALL, dx, dy)
        
        # 鏇存柊缂╂斁鍥犲瓙
        self.scale = scale_factor
    
    def start_drag_fullscreen(self, event):
        """鍏ㄥ睆妯″紡涓嬪紑濮嬫嫋锟?""
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y
    
    def drag_fullscreen(self, event):
        """鍏ㄥ睆妯″紡涓嬫嫋鎷芥搷锟?""
        if self.dragging:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.fullscreen_canvas.move(tk.ALL, dx, dy)
            self.last_x = event.x
            self.last_y = event.y
    
    def on_mouse_wheel_fullscreen(self, event):
        """鍏ㄥ睆妯″紡涓嬮紶鏍囨粴杞缉锟?""
        if event.delta > 0:
            new_scale = self.scale * 1.1
        else:
            new_scale = self.scale * 0.9
        
        # 缁熶竴缂╂斁鑼冨洿锟?0%-200%
        new_scale = max(0.5, min(new_scale, 2.0))
        scale_factor = new_scale / self.scale
        self.scale = new_scale
        
        self.fullscreen_canvas.scale(tk.ALL, event.x, event.y, scale_factor, scale_factor)


    def set_data_callback(self, callback):
        """璁剧疆鏁版嵁鍥炶皟鍑芥暟
        
        Args:
            callback: 鏁版嵁鍥炶皟鍑芥暟锛岃繑鍥炵綉缁滄嫇鎵戞暟锟?
        """
        self.data_callback = callback
    
    def start_auto_update(self, interval=None):
        """寮€濮嬭嚜鍔ㄦ洿锟?
        
        Args:
            interval: 鏇存柊闂撮殧锛堟绉掞級锛岄粯锟?0锟?
        """
        if interval:
            self.update_interval = interval
        
        self.auto_update = True
        self._schedule_update()
    
    def stop_auto_update(self):
        """鍋滄鑷姩鏇存柊"""
        self.auto_update = False
        if self.update_timer:
            try:
                self.canvas.after_cancel(self.update_timer)
            except Exception:
                pass
            self.update_timer = None
    
    def refresh_data(self):
        """鎵嬪姩鍒锋柊鏁版嵁"""
        if self.data_callback:
            try:
                network_data = self.data_callback()
                self.draw_topology(network_data)
            except Exception as e:
                print(f"鍒锋柊鏁版嵁澶辫触: {e}")
    
    def _schedule_update(self):
        """瀹夋帓涓嬩竴娆℃洿锟?""
        if self.auto_update:
            self.refresh_data()
            self.update_timer = self.canvas.after(self.update_interval, self._schedule_update)


class IPAllocationVisualizer:
    """IP鍦板潃鍒嗛厤鍙鍖栫被"""
    
    def __init__(self, parent):
        """鍒濆鍖栧彲瑙嗗寲锟?
        
        Args:
            parent: 鐖跺锟?
        """
        self.parent = parent
        self.canvas_frame = Frame(parent)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # 鍒涘缓婊氬姩锟?
        self.v_scrollbar = Scrollbar(self.canvas_frame, orient=tk.VERTICAL)
        
        # 鍒涘缓鐢诲竷
        self.canvas = Canvas(
            self.canvas_frame,
            bg=BACKGROUND_COLOR,
            yscrollcommand=self.v_scrollbar.set
        )
        
        # 閰嶇疆婊氬姩锟?
        self.v_scrollbar.config(command=self.canvas.yview)
        
        # 鏀剧疆缁勪欢
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def draw_ip_allocation(self, network, ip_list):
        """缁樺埗IP鍦板潃鍒嗛厤鍙锟?
        
        Args:
            network: 缃戠粶鍦板潃
            ip_list: IP鍦板潃鍒楄〃
        """
        self.canvas.delete(tk.ALL)
        
        # 鑾峰彇瀛椾綋璁剧疆
        font_family, font_size = get_current_font_settings()
        
        # 璁＄畻鐢诲竷灏哄
        width = self.canvas.winfo_width() or 800
        height = 50 + len(ip_list) * 30
        
        # 缁樺埗鏍囬
        self.canvas.create_text(
            width / 2, 20,
            text=f"{translate('ip_allocation_visualization')}: {network}",
            font=(font_family, font_size, "bold"),
            fill=TEXT_COLOR
        )
        
        # 缁樺埗IP鍦板潃鍒楄〃
        for i, ip_info in enumerate(ip_list):
            y = 60 + i * 30
            
            # 鏍规嵁鐘舵€佽缃锟?
            if ip_info["status"] == "allocated":
                color = "#27ae60"
            elif ip_info["status"] == "reserved":
                color = "#f39c12"
            else:
                color = "#95a5a6"
            
            # 缁樺埗IP鍦板潃锟?
            self.canvas.create_rectangle(
                50, y, width - 50, y + 25,
                fill=color,
                outline="#34495e",
                width=1
            )
            
            # 缁樺埗IP鍦板潃鏂囨湰
            self.canvas.create_text(
                70, y + 12,
                text=ip_info["ip_address"],
                font=(font_family, font_size - 1),
                fill=TEXT_COLOR,
                anchor=tk.W
            )
            
            # 缁樺埗涓绘満鍚嶅拰鎻忚堪
            if ip_info.get("hostname"):
                hostname = ip_info["hostname"]
                if len(hostname) > 20:
                    hostname = hostname[:17] + "..."
                
                self.canvas.create_text(
                    200, y + 12,
                    text=hostname,
                    font=(font_family, font_size - 1),
                    fill=TEXT_COLOR,
                    anchor=tk.W
                )
            
            # 缁樺埗鐘讹拷?
            self.canvas.create_text(
                width - 70, y + 12,
                text=ip_info["status"],
                font=(font_family, font_size - 1),
                fill=TEXT_COLOR,
                anchor=tk.E
            )
        
        # 鏇存柊婊氬姩鍖哄煙
        self.canvas.config(scrollregion=(0, 0, width, height))

