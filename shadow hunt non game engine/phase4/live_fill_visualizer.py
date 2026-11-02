from __future__ import annotations
import tkinter as tk
from typing import List, Tuple, Optional, Callable
from collections import deque
from PIL import Image, ImageTk
Point = Tuple[float, float]
Points = List[Point]
_EMPTY = 0
_BOUNDARY = 1
_FILL = 2

def _hex_to_rgba(color: str) -> Tuple[int, int, int, int]:
    c = color.lstrip('#')
    if len(c) == 8:
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16))
    if len(c) == 3:
        c = ''.join((ch * 2 for ch in c))
    return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255)

def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
    pts: List[Tuple[int, int]] = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    x, y = (x1, y1)
    if dx >= dy:
        p = 2 * dy - dx
        for _ in range(dx + 1):
            pts.append((x, y))
            if p < 0:
                p += 2 * dy
            else:
                y += sy
                p += 2 * dy - 2 * dx
            x += sx
    else:
        p = 2 * dx - dy
        for _ in range(dy + 1):
            pts.append((x, y))
            if p < 0:
                p += 2 * dx
            else:
                x += sx
                p += 2 * dx - 2 * dy
            y += sy
    return pts

def is_inside_polygon(px: int, py: int, xs: List[int], ys: List[int]) -> bool:
    n = len(xs)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = (xs[i], ys[i])
        xj, yj = (xs[j], ys[j])
        if (yi > py) != (yj > py):
            x_inters = xi + (py - yi) * (xj - xi) / (yj - yi)
            if px < x_inters:
                inside = not inside
        j = i
    return inside

def boundary_fill_4_connected(grid, width: int, height: int, sx: int, sy: int, record_steps: bool=False):
    if not (0 <= sx < width and 0 <= sy < height):
        return []
    fill_order: List[Tuple[int, int]] = []
    stack = deque([(sx, sy)])
    while stack:
        px, py = stack.pop()
        if px < 0 or py < 0 or px >= width or (py >= height):
            continue
        if grid[py][px] in (_BOUNDARY, _FILL):
            continue
        grid[py][px] = _FILL
        if record_steps:
            fill_order.append((px, py))
        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))
    return fill_order

class LivePolygonFillPanel:

    def __init__(self, parent_frame: tk.Frame, width: int=340, height: int=740, on_target_change: Optional[Callable[[int], None]]=None):
        self.frame = tk.Frame(parent_frame, bg='#0d131f', width=width, height=height)
        self.frame.pack_propagate(False)
        self.width = width
        self.height = height
        self.on_target_change = on_target_change
        self.animating = False
        self.anim_steps: List[Tuple[int, int]] = []
        self.anim_idx = 0
        self.anim_grid: Optional[List[List[int]]] = None
        self.anim_w = 0
        self.anim_h = 0
        self.anim_scale = 1
        self.target_name = 'Player Operative'
        self.fill_color = '#10b981'
        self.boundary_color = '#34d399'
        self._current_vertices: Points = []
        self._preview_image = None
        self.selected_target_id = 1
        self._build_ui()

    def _build_ui(self):
        title_box = tk.Frame(self.frame, bg='#111827', padx=8, pady=6)
        title_box.pack(fill=tk.X, side=tk.TOP)
        tk.Label(title_box, text='LIVE POLYGON FILL ENGINE', font=('Consolas', 11, 'bold'), fg='#38bdf8', bg='#111827').pack(anchor='w')
        tk.Label(title_box, text='4-Conn Boundary Fill • All Colored Entities', font=('Consolas', 8), fg='#94a3b8', bg='#111827').pack(anchor='w')
        sel_box = tk.LabelFrame(self.frame, text=' Select Target Entity ', font=('Consolas', 8, 'bold'), fg='#38bdf8', bg='#0d131f', padx=4, pady=4)
        sel_box.pack(fill=tk.X, padx=6, pady=4)
        btn_row1 = tk.Frame(sel_box, bg='#0d131f')
        btn_row1.pack(fill=tk.X, pady=1)
        btn_row2 = tk.Frame(sel_box, bg='#0d131f')
        btn_row2.pack(fill=tk.X, pady=1)
        self.btn_targets = {}
        targets = [(1, 'Player', '#10b981', btn_row1), (2, 'Guard', '#ef4444', btn_row1), (3, 'Shielded', '#00e5ff', btn_row1), (4, 'Enemy Cone', '#f59e0b', btn_row1), (5, 'Cam Cone', '#06b6d4', btn_row2), (6, 'Coin', '#facc15', btn_row2), (7, 'MedKit', '#f43f5e', btn_row2), (8, 'Exit Pad', '#22c55e', btn_row2)]
        for tid, name, color, row in targets:
            b = tk.Button(row, text=name, font=('Consolas', 7, 'bold'), bg='#1e293b', fg=color, activebackground='#334155', activeforeground='#ffffff', relief=tk.FLAT, padx=4, pady=2, command=lambda t=tid: self.set_target(t))
            b.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.btn_targets[tid] = b
        coord_box = tk.LabelFrame(self.frame, text=' Live Geometry Coordinates ', font=('Consolas', 8, 'bold'), fg='#facc15', bg='#0d131f', padx=6, pady=4)
        coord_box.pack(fill=tk.X, padx=6, pady=3)
        self.lbl_target = tk.Label(coord_box, text='Target: Player Operative', font=('Consolas', 9, 'bold'), fg='#10b981', bg='#0d131f', anchor='w')
        self.lbl_target.pack(fill=tk.X)
        self.lbl_v0 = tk.Label(coord_box, text='V0 (Head) : (---, ---)', font=('Consolas', 8), fg='#e2e8f0', bg='#0d131f', anchor='w')
        self.lbl_v0.pack(fill=tk.X)
        self.lbl_v1 = tk.Label(coord_box, text='V1 (Left) : (---, ---)', font=('Consolas', 8), fg='#e2e8f0', bg='#0d131f', anchor='w')
        self.lbl_v1.pack(fill=tk.X)
        self.lbl_v2 = tk.Label(coord_box, text='V2 (Notch): (---, ---)', font=('Consolas', 8), fg='#e2e8f0', bg='#0d131f', anchor='w')
        self.lbl_v2.pack(fill=tk.X)
        self.lbl_v3 = tk.Label(coord_box, text='V3 (Right): (---, ---)', font=('Consolas', 8), fg='#e2e8f0', bg='#0d131f', anchor='w')
        self.lbl_v3.pack(fill=tk.X)
        self.lbl_seed = tk.Label(coord_box, text='Seed Point: (---, ---)', font=('Consolas', 8, 'bold'), fg='#38bdf8', bg='#0d131f', anchor='w')
        self.lbl_seed.pack(fill=tk.X)
        canvas_box = tk.LabelFrame(self.frame, text=' Magnified Raster Fill Display ', font=('Consolas', 8, 'bold'), fg='#a78bfa', bg='#0d131f', padx=4, pady=4)
        canvas_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=3)
        self.preview_canvas = tk.Canvas(canvas_box, width=280, height=250, bg='#030712', highlightthickness=1, highlightbackground='#1f2937')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        stat_box = tk.Frame(self.frame, bg='#0d131f', padx=6, pady=2)
        stat_box.pack(fill=tk.X)
        self.lbl_stats = tk.Label(stat_box, text='Boundary: 0 px | Fill: 0 px\nStatus: LIVE TRACKING', font=('Consolas', 8), fg='#94a3b8', bg='#0d131f', justify=tk.LEFT, anchor='w')
        self.lbl_stats.pack(fill=tk.X)
        btn_box = tk.Frame(self.frame, bg='#0d131f', padx=6, pady=4)
        btn_box.pack(fill=tk.X, side=tk.BOTTOM)
        self.btn_step = tk.Button(btn_box, text='Slow-Mo Fill Animation [F]', font=('Consolas', 9, 'bold'), bg='#1e293b', fg='#38bdf8', activebackground='#334155', activeforeground='#ffffff', relief=tk.FLAT, pady=4, command=self.trigger_slow_mo_animation)
        self.btn_step.pack(fill=tk.X, pady=2)
        self.highlight_button(1)

    def highlight_button(self, tid: int):
        self.selected_target_id = tid
        for i, b in self.btn_targets.items():
            if i == tid:
                b.config(relief=tk.SUNKEN, bg='#334155')
            else:
                b.config(relief=tk.FLAT, bg='#1e293b')

    def set_target(self, tid: int):
        self.highlight_button(tid)
        if self.on_target_change:
            self.on_target_change(tid)

    def update_live_polygon(self, vertices: Points, target_name: str='Player Operative', fill_color: str='#10b981', boundary_color: str='#34d399'):
        if len(vertices) < 3:
            return
        self._current_vertices = list(vertices)
        self.target_name = target_name
        self.fill_color = fill_color
        self.boundary_color = boundary_color
        self.lbl_target.config(text=f'Target: {target_name}', fg=boundary_color)
        n = len(vertices)
        if n == 4:
            self.lbl_v0.config(text=f'V0 (Head) : ({vertices[0][0]:6.1f}, {vertices[0][1]:6.1f})')
            self.lbl_v1.config(text=f'V1 (Left) : ({vertices[1][0]:6.1f}, {vertices[1][1]:6.1f})')
            self.lbl_v2.config(text=f'V2 (Notch): ({vertices[2][0]:6.1f}, {vertices[2][1]:6.1f})')
            self.lbl_v3.config(text=f'V3 (Right): ({vertices[3][0]:6.1f}, {vertices[3][1]:6.1f})')
        elif n == 3:
            self.lbl_v0.config(text=f'V0: ({vertices[0][0]:6.1f}, {vertices[0][1]:6.1f})')
            self.lbl_v1.config(text=f'V1: ({vertices[1][0]:6.1f}, {vertices[1][1]:6.1f})')
            self.lbl_v2.config(text=f'V2: ({vertices[2][0]:6.1f}, {vertices[2][1]:6.1f})')
            self.lbl_v3.config(text='V3: N/A')
        else:
            self.lbl_v0.config(text=f'Total Verts: {n} points')
            self.lbl_v1.config(text=f'V0 (Start): ({vertices[0][0]:6.1f}, {vertices[0][1]:6.1f})')
            self.lbl_v2.config(text=f'V{n // 2} (Mid)  : ({vertices[n // 2][0]:6.1f}, {vertices[n // 2][1]:6.1f})')
            self.lbl_v3.config(text=f'V{n - 1} (End)  : ({vertices[-1][0]:6.1f}, {vertices[-1][1]:6.1f})')
        if not self.animating:
            self._render_raster_preview(vertices, step_mode=False)

    def trigger_slow_mo_animation(self):
        if not self._current_vertices or len(self._current_vertices) < 3:
            return
        self.animating = True
        self._render_raster_preview(self._current_vertices, step_mode=True)

    def _render_raster_preview(self, vertices: Points, step_mode: bool=False):
        pad = 2
        xs_f = [v[0] for v in vertices]
        ys_f = [v[1] for v in vertices]
        min_x, max_x = (min(xs_f), max(xs_f))
        min_y, max_y = (min(ys_f), max(ys_f))
        box_w = max_x - min_x
        box_h = max_y - min_y
        max_dim = max(box_w, box_h, 1.0)
        target_dim = 56.0
        fit_scale = target_dim / max_dim if max_dim > target_dim else 1.0
        xs = [int(round((v[0] - min_x) * fit_scale)) + pad for v in vertices]
        ys = [int(round((v[1] - min_y) * fit_scale)) + pad for v in vertices]
        w = max(xs) + 1 + pad
        h = max(ys) + 1 + pad
        if w <= 0 or h <= 0 or w > 200 or (h > 200):
            return
        n = len(xs)
        grid = [[_EMPTY] * w for _ in range(h)]
        boundary_count = 0
        for i in range(n):
            for px, py in bresenham_line(xs[i], ys[i], xs[(i + 1) % n], ys[(i + 1) % n]):
                if 0 <= px < w and 0 <= py < h:
                    if grid[py][px] != _BOUNDARY:
                        grid[py][px] = _BOUNDARY
                        boundary_count += 1
        seed_x = int(round(sum(xs) / n))
        seed_y = int(round(sum(ys) / n))
        if not is_inside_polygon(seed_x, seed_y, xs, ys):
            seed_x = seed_y = -1
            for py in range(h):
                for px in range(w):
                    if grid[py][px] == _EMPTY and is_inside_polygon(px, py, xs, ys):
                        seed_x, seed_y = (px, py)
                        break
                if seed_x >= 0:
                    break
        if seed_x < 0:
            return
        world_seed_x = int(round(min_x + (seed_x - pad) / fit_scale))
        world_seed_y = int(round(min_y + (seed_y - pad) / fit_scale))
        self.lbl_seed.config(text=f'Seed Point: ({world_seed_x}, {world_seed_y})')
        scale = max(2, min(240 // max(w, 1), 220 // max(h, 1)))
        scale = max(2, min(scale, 12))
        if step_mode:
            steps = boundary_fill_4_connected(grid, w, h, seed_x, seed_y, record_steps=True)
            self.anim_steps = steps
            self.anim_idx = 0
            self.anim_grid = [[_BOUNDARY if grid[py][px] == _BOUNDARY else _EMPTY for px in range(w)] for py in range(h)]
            self.anim_w = w
            self.anim_h = h
            self.anim_scale = scale
            self._animate_step()
        else:
            boundary_fill_4_connected(grid, w, h, seed_x, seed_y, record_steps=False)
            fill_count = sum((row.count(_FILL) for row in grid))
            self._draw_grid_to_canvas(grid, w, h, scale, seed_x, seed_y)
            self.lbl_stats.config(text=f'Boundary: {boundary_count} px | Filled: {fill_count} px\nStatus: LIVE 60 FPS (Coords Synced)', fg=self.boundary_color)

    def _animate_step(self):
        if not self.animating or self.anim_grid is None:
            return
        chunk = max(6, len(self.anim_steps) // 25)
        end_idx = min(self.anim_idx + chunk, len(self.anim_steps))
        for i in range(self.anim_idx, end_idx):
            px, py = self.anim_steps[i]
            self.anim_grid[py][px] = _FILL
        self.anim_idx = end_idx
        self._draw_grid_to_canvas(self.anim_grid, self.anim_w, self.anim_h, self.anim_scale)
        progress = int(self.anim_idx / max(1, len(self.anim_steps)) * 100)
        self.lbl_stats.config(text=f'Boundary: Active | Filled: {self.anim_idx}/{len(self.anim_steps)} px\nStatus: ANIMATING FILL ({progress}%)', fg='#facc15')
        if self.anim_idx < len(self.anim_steps):
            self.frame.after(16, self._animate_step)
        else:
            self.animating = False
            self.lbl_stats.config(text=f'Boundary: Complete | Filled: {len(self.anim_steps)} px\nStatus: DEMO COMPLETE (Resumed Live)', fg=self.boundary_color)

    def _draw_grid_to_canvas(self, grid, w: int, h: int, scale: int, seed_x: int=-1, seed_y: int=-1):
        img = Image.new('RGBA', (w, h), (3, 7, 18, 255))
        pix = img.load()
        col_bound = _hex_to_rgba(self.boundary_color)
        col_fill = _hex_to_rgba(self.fill_color)
        col_seed = (255, 255, 255, 255)
        for py in range(h):
            row = grid[py]
            for px in range(w):
                cell = row[px]
                if px == seed_x and py == seed_y:
                    pix[px, py] = col_seed
                elif cell == _FILL:
                    pix[px, py] = col_fill
                elif cell == _BOUNDARY:
                    pix[px, py] = col_bound
        if scale > 1:
            img = img.resize((w * scale, h * scale), resample=Image.Resampling.NEAREST)
        self._preview_image = ImageTk.PhotoImage(img)
        self.preview_canvas.delete('all')
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        if cw <= 1:
            cw = 280
        if ch <= 1:
            ch = 250
        cx = max(0, (cw - w * scale) // 2)
        cy = max(0, (ch - h * scale) // 2)
        self.preview_canvas.create_image(cx, cy, image=self._preview_image, anchor='nw')
