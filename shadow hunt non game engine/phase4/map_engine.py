import math
from typing import List, Tuple, Optional, Dict
from cg_math import CGMath, Point, Points
from fill_algo import rasterize_filled_polygon, draw_filled_polygon, draw_bresenham_segment

def _rect_poly(x1, y1, x2, y2) -> Points:
    return [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]

def _circle_poly(cx: float, cy: float, r: float, n: int=16) -> Points:
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]

class Wall:

    def __init__(self, x1: float, y1: float, x2: float, y2: float, wall_id: str='wall'):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.wall_id = wall_id
        self._photo = None
        self._ox = self._oy = 0

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    def collides_with_circle(self, cx: float, cy: float, r: float) -> bool:
        closest_x = max(self.x1, min(cx, self.x2))
        closest_y = max(self.y1, min(cy, self.y2))
        dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
        return dist_sq <= r * r

    def bake(self, fill_color='#334155', border_color='#64748b'):
        res = rasterize_filled_polygon(_rect_poly(self.x1, self.y1, self.x2, self.y2), fill_color, border_color)
        if res:
            self._photo, self._ox, self._oy = res

    def render(self, canvas, fill_color='#334155', border_color='#64748b'):
        if self._photo is None:
            self.bake(fill_color, border_color)
        if self._photo is not None:
            canvas.create_image(self._ox, self._oy, image=self._photo, anchor='nw', tags='wall')

class CrossedBox:

    def __init__(self, x1: float, y1: float, x2: float, y2: float, box_id: str='box'):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.box_id = box_id
        self.thickness = 5.0
        self._body = None
        self._inner = None
        self._body_ox = self._body_oy = 0
        self._inner_ox = self._inner_oy = 0
        self._keep: List = []

    @property
    def width(self) -> float:
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        return self.y2 - self.y1

    def collides_with_circle(self, cx: float, cy: float, r: float) -> bool:
        closest_x = max(self.x1, min(cx, self.x2))
        closest_y = max(self.y1, min(cy, self.y2))
        dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
        return dist_sq <= r * r

    def bake(self):
        body = rasterize_filled_polygon(_rect_poly(self.x1, self.y1, self.x2, self.y2), '#1e2433', '#475569')
        if body:
            self._body, self._body_ox, self._body_oy = body
        inset = self.thickness + 2.0
        ix1, iy1 = (self.x1 + inset, self.y1 + inset)
        ix2, iy2 = (self.x2 - inset, self.y2 - inset)
        inner = rasterize_filled_polygon(_rect_poly(ix1, iy1, ix2, iy2), '#151b27', '#334155')
        if inner:
            self._inner, self._inner_ox, self._inner_oy = inner

    def render(self, canvas):
        canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, fill='#1e2433', outline='#475569', width=2, tags='obstacle')
        inset = self.thickness + 2.0
        ix1, iy1 = (self.x1 + inset, self.y1 + inset)
        ix2, iy2 = (self.x2 - inset, self.y2 - inset)
        canvas.create_rectangle(ix1, iy1, ix2, iy2, fill='#151b27', outline='#334155', width=1, tags='obstacle_inner')
        canvas.create_line(ix1, iy1, ix2, iy2, fill='#475569', width=3, tags='obstacle_cross')
        canvas.create_line(ix1, iy2, ix2, iy1, fill='#475569', width=3, tags='obstacle_cross')
        rivet_r = 2.0
        for rx, ry in [(ix1 + 5, iy1 + 5), (ix2 - 5, iy1 + 5), (ix1 + 5, iy2 - 5), (ix2 - 5, iy2 - 5)]:
            canvas.create_oval(rx - rivet_r, ry - rivet_r, rx + rivet_r, ry + rivet_r, fill='#94a3b8', outline='#94a3b8', tags='obstacle_rivet')

class Door:

    def __init__(self, x1: float, y1: float, x2: float, y2: float, door_id: str, color: str='#00f0ff', trigger_radius: float=75.0):
        self.x1 = float(x1)
        self.y1 = float(y1)
        self.x2 = float(x2)
        self.y2 = float(y2)
        self.door_id = door_id
        self.color = color
        self.trigger_radius = trigger_radius
        self.mid_x = (self.x1 + self.x2) / 2.0
        self.mid_y = (self.y1 + self.y2) / 2.0
        self.slide_progress = 0.0
        self.is_open = False
        self.slide_speed = 0.12
        self._keep: List = []

    def update_proximity(self, player_x: float, player_y: float) -> bool:
        dist = CGMath.distance(player_x, player_y, self.mid_x, self.mid_y)
        self.is_open = dist <= self.trigger_radius
        target = 1.0 if self.is_open else 0.0
        if self.slide_progress < target:
            self.slide_progress = min(1.0, self.slide_progress + self.slide_speed)
        elif self.slide_progress > target:
            self.slide_progress = max(0.0, self.slide_progress - self.slide_speed)
        return self.is_open

    def is_blocking(self) -> bool:
        return self.slide_progress < 0.75

    def collides_with_circle(self, cx: float, cy: float, r: float) -> bool:
        if not self.is_blocking():
            return False
        cur_x2 = self.x1 + (self.x2 - self.x1) * (1.0 - self.slide_progress)
        cur_y2 = self.y1 + (self.y2 - self.y1) * (1.0 - self.slide_progress)
        dx = cur_x2 - self.x1
        dy = cur_y2 - self.y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq == 0:
            return CGMath.distance(cx, cy, self.x1, self.y1) <= r
        t = max(0.0, min(1.0, ((cx - self.x1) * dx + (cy - self.y1) * dy) / seg_len_sq))
        proj_x = self.x1 + t * dx
        proj_y = self.y1 + t * dy
        return CGMath.distance(cx, cy, proj_x, proj_y) <= r + 2.5

    def render(self, canvas):
        cur_x2 = self.x1 + (self.x2 - self.x1) * (1.0 - self.slide_progress)
        cur_y2 = self.y1 + (self.y2 - self.y1) * (1.0 - self.slide_progress)
        jamb_radius = 4.0
        canvas.create_oval(self.x1 - jamb_radius, self.y1 - jamb_radius, self.x1 + jamb_radius, self.y1 + jamb_radius, fill='#64748b', outline='#94a3b8', tags='door_jamb')
        canvas.create_oval(self.x2 - jamb_radius, self.y2 - jamb_radius, self.x2 + jamb_radius, self.y2 + jamb_radius, fill='#64748b', outline='#94a3b8', tags='door_jamb')
        if self.slide_progress < 0.98:
            canvas.create_line(self.x1, self.y1, cur_x2, cur_y2, fill=self.color, width=5, tags='door')
        led_color = '#22c55e' if self.is_open else '#ef4444'
        canvas.create_oval(self.mid_x - 3.0, self.mid_y - 3.0, self.mid_x + 3.0, self.mid_y + 3.0, fill=led_color, outline='#ffffff', tags='door_led')

class ExitDoor:

    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.mid_x = (self.x1 + self.x2) / 2.0
        self.mid_y = (self.y1 + self.y2) / 2.0
        self.pulse = 0.0
        self._secure = None
        self._alarm = None
        self._ox = self._oy = 0
        self._keep: List = []

    def is_reached(self, px: float, py: float, radius: float=15.0) -> bool:
        closest_x = max(self.x1, min(px, self.x2))
        closest_y = max(self.y1, min(py, self.y2))
        d_sq = (px - closest_x) ** 2 + (py - closest_y) ** 2
        return d_sq <= radius * radius

    def bake(self):
        poly = _rect_poly(self.x1, self.y1, self.x2, self.y2)
        s = rasterize_filled_polygon(poly, '#064e3b', '#34d399')
        a = rasterize_filled_polygon(poly, '#047857', '#22c55e')
        if s:
            self._secure, self._ox, self._oy = s
        if a:
            self._alarm, _, _ = a

    def render(self, canvas, alarm_active: bool=False):
        if self._secure is None:
            self.bake()
        self._keep.clear()
        self.pulse += 0.1
        border_color = '#34d399' if not alarm_active else '#22c55e' if math.sin(self.pulse) > 0 else '#ffffff'
        photo = self._alarm if alarm_active and self._alarm else self._secure
        if photo is not None:
            canvas.create_image(self._ox, self._oy, image=photo, anchor='nw', tags='exit_door')
        for sx in range(int(self.x1) + 8, int(self.x2) - 8, 14):
            canvas.create_line(sx, self.y1 + 3, sx + 8, self.y2 - 3, fill='#34d399', width=2, tags='exit_chevrons')
        canvas.create_text(self.mid_x, self.y1 - 12, text='[ EXIT DOOR ]', fill=border_color, font=('Consolas', 9, 'bold'), tags='exit_text')

class MapEngine:
    WALL_THICKNESS = 5.0
    PASSAGE_WIDTH = 100.0
    BOX_SIZE = 120.0

    def __init__(self, origin_x: float=60.0, origin_y: float=60.0):
        self.ox = origin_x
        self.oy = origin_y
        self.walls: List[Wall] = []
        self.boxes: List[CrossedBox] = []
        self.doors: List[Door] = []
        self.exit_door: Optional[ExitDoor] = None
        self._floor = None
        self._floor_ox = self._floor_oy = 0
        self._grid_keep: List = []
        self._baked = False
        self._build_map()

    def _bake_static(self):
        if self._baked:
            return
        floor = rasterize_filled_polygon(_rect_poly(self.ox, self.oy, self.ox + self.room_w, self.oy + self.room_h), '#0b0f19', '#1e293b')
        if floor:
            self._floor, self._floor_ox, self._floor_oy = floor
        for wall in self.walls:
            wall.bake()
        for box in self.boxes:
            box.bake()
        if self.exit_door:
            self.exit_door.bake()
        self._baked = True

    def _build_map(self):
        wt = self.WALL_THICKNESS
        pw = self.PASSAGE_WIDTH
        bs = self.BOX_SIZE
        room_w = 2 * wt + 4 * pw + 3 * bs
        room_h = 2 * wt + 3 * pw + 2 * bs
        self.room_w = room_w
        self.room_h = room_h
        self.walls.append(Wall(self.ox, self.oy, self.ox + room_w, self.oy + wt, 'wall_top'))
        self.walls.append(Wall(self.ox, self.oy + room_h - wt, self.ox + room_w, self.oy + room_h, 'wall_bottom'))
        self.walls.append(Wall(self.ox, self.oy, self.ox + wt, self.oy + room_h, 'wall_left'))
        self.walls.append(Wall(self.ox + room_w - wt, self.oy, self.ox + room_w, self.oy + room_h, 'wall_right'))
        col_x = [self.ox + wt + pw + i * (bs + pw) for i in range(3)]
        row_y = [self.oy + wt + pw + j * (bs + pw) for j in range(2)]
        for col_idx, bx in enumerate(col_x):
            for row_idx, by in enumerate(row_y):
                box_id = f'crate_c{col_idx + 1}_r{row_idx + 1}'
                self.boxes.append(CrossedBox(bx, by, bx + bs, by + bs, box_id))
        d1_x1 = col_x[0] + bs
        d1_x2 = col_x[1]
        d1_y = row_y[0] + bs / 2.0
        self.doors.append(Door(d1_x1, d1_y, d1_x2, d1_y, 'door_1', color='#00e5ff', trigger_radius=70.0))
        d2_x1 = col_x[1] + bs
        d2_x2 = col_x[2]
        d2_y = row_y[1] + bs / 2.0
        self.doors.append(Door(d2_x1, d2_y, d2_x2, d2_y, 'door_2', color='#ff9100', trigger_radius=70.0))
        d3_y1 = row_y[0] + bs
        d3_y2 = row_y[1]
        d3_x = col_x[1] + bs / 2.0
        self.doors.append(Door(d3_x, d3_y1, d3_x, d3_y2, 'door_3', color='#a855f7', trigger_radius=70.0))
        exit_x1 = self.ox + self.room_w - wt - pw + 12.0
        exit_x2 = self.ox + self.room_w - wt - 12.0
        exit_y2 = self.oy + self.room_h - wt
        exit_y1 = exit_y2 - 36.0
        self.exit_door = ExitDoor(exit_x1, exit_y1, exit_x2, exit_y2)

    def update_doors(self, player_x: float, player_y: float):
        for door in self.doors:
            door.update_proximity(player_x, player_y)

    def is_blocked(self, cx: float, cy: float, radius: float=15.0) -> bool:
        for wall in self.walls:
            if wall.collides_with_circle(cx, cy, radius):
                return True
        for box in self.boxes:
            if box.collides_with_circle(cx, cy, radius):
                return True
        for door in self.doors:
            if door.collides_with_circle(cx, cy, radius):
                return True
        return False

    def render(self, canvas, alarm_active: bool=False):
        self._bake_static()
        if self._floor is not None:
            canvas.create_image(self._floor_ox, self._floor_oy, image=self._floor, anchor='nw', tags='floor')
        for wall in self.walls:
            wall.render(canvas)
        for box in self.boxes:
            box.render(canvas)
        if self.exit_door:
            self.exit_door.render(canvas, alarm_active=alarm_active)
        for door in self.doors:
            door.render(canvas)
