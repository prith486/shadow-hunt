from __future__ import annotations
import tkinter as tk
import math
from typing import List, Tuple, Optional, Callable
Point = Tuple[float, float]
Points = List[Point]
_CS_INSIDE = 0
_CS_LEFT = 1
_CS_RIGHT = 2
_CS_BOTTOM = 4
_CS_TOP = 8

def get_cs_outcode(x: float, y: float, xmin: float, ymin: float, xmax: float, ymax: float) -> int:
    code = _CS_INSIDE
    if x < xmin:
        code |= _CS_LEFT
    elif x > xmax:
        code |= _CS_RIGHT
    if y < ymin:
        code |= _CS_TOP
    elif y > ymax:
        code |= _CS_BOTTOM
    return code

def outcode_to_str(code: int) -> str:
    t = '1' if code & _CS_TOP else '0'
    b = '1' if code & _CS_BOTTOM else '0'
    r = '1' if code & _CS_RIGHT else '0'
    l = '1' if code & _CS_LEFT else '0'
    bit_str = f'[{t}{b}{r}{l}]'
    labels = []
    if code & _CS_TOP:
        labels.append('TOP')
    if code & _CS_BOTTOM:
        labels.append('BTM')
    if code & _CS_RIGHT:
        labels.append('RGT')
    if code & _CS_LEFT:
        labels.append('LFT')
    if not labels:
        labels.append('IN')
    return f"{bit_str} ({'-'.join(labels)})"

def sutherland_hodgman_detailed(polygon: Points, xmin: float, ymin: float, xmax: float, ymax: float) -> Tuple[List[Tuple[str, Points, List[Point]]], Points, List[Point]]:
    if not polygon or len(polygon) < 3:
        return ([], [], [])

    def intersection(p1: Point, p2: Point, edge_type: int) -> Point:
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        if edge_type == 0:
            x = xmin
            y = y1 + dy * (xmin - x1) / dx if dx != 0 else y1
        elif edge_type == 1:
            x = xmax
            y = y1 + dy * (xmax - x1) / dx if dx != 0 else y1
        elif edge_type == 2:
            y = ymin
            x = x1 + dx * (ymin - y1) / dy if dy != 0 else x1
        else:
            y = ymax
            x = x1 + dx * (ymax - y1) / dy if dy != 0 else x1
        return (x, y)
    stage_names = ['Stage 1: Clip Left  (x >= xmin)', 'Stage 2: Clip Right (x <= xmax)', 'Stage 3: Clip Top   (y >= ymin)', 'Stage 4: Clip Bottom(y <= ymax)']
    stages: List[Tuple[str, Points, List[Point]]] = []
    current_poly = list(polygon)
    all_intersections: List[Point] = []
    for edge_type in range(4):
        clipped: Points = []
        stage_inters: List[Point] = []
        if not current_poly:
            stages.append((stage_names[edge_type], [], []))
            continue
        s = current_poly[-1]
        for p in current_poly:
            if edge_type == 0:
                s_in = s[0] >= xmin
                p_in = p[0] >= xmin
            elif edge_type == 1:
                s_in = s[0] <= xmax
                p_in = p[0] <= xmax
            elif edge_type == 2:
                s_in = s[1] >= ymin
                p_in = p[1] >= ymin
            else:
                s_in = s[1] <= ymax
                p_in = p[1] <= ymax
            if p_in:
                if not s_in:
                    pt_i = intersection(s, p, edge_type)
                    clipped.append(pt_i)
                    stage_inters.append(pt_i)
                    all_intersections.append(pt_i)
                clipped.append(p)
            elif s_in:
                pt_i = intersection(s, p, edge_type)
                clipped.append(pt_i)
                stage_inters.append(pt_i)
                all_intersections.append(pt_i)
            s = p
        current_poly = clipped
        stages.append((stage_names[edge_type], list(current_poly), stage_inters))
    return (stages, current_poly, all_intersections)

def cohen_sutherland_detailed(x1: float, y1: float, x2: float, y2: float, xmin: float, ymin: float, xmax: float, ymax: float) -> Tuple[Optional[Tuple[float, float, float, float]], int, int, List[Point], str]:
    code1 = get_cs_outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = get_cs_outcode(x2, y2, xmin, ymin, xmax, ymax)
    intersections: List[Point] = []
    if code1 | code2 == 0:
        return ((x1, y1, x2, y2), code1, code2, [], 'TRIVIAL ACCEPT (Both Inside)')
    if code1 & code2 != 0:
        return (None, code1, code2, [], 'TRIVIAL REJECT (Outside Same Side)')
    cx1, cy1 = (x1, y1)
    cx2, cy2 = (x2, y2)
    c1, c2 = (code1, code2)
    for _ in range(6):
        if c1 | c2 == 0:
            return ((cx1, cy1, cx2, cy2), code1, code2, intersections, 'CLIPPED (Iterative Accept)')
        if c1 & c2 != 0:
            return (None, code1, code2, intersections, 'CLIPPED (Iterative Reject)')
        code_out = c1 if c1 != 0 else c2
        x, y = (0.0, 0.0)
        if code_out & _CS_TOP:
            if abs(cy2 - cy1) < 1e-09:
                break
            x = cx1 + (cx2 - cx1) * (ymin - cy1) / (cy2 - cy1)
            y = ymin
        elif code_out & _CS_BOTTOM:
            if abs(cy2 - cy1) < 1e-09:
                break
            x = cx1 + (cx2 - cx1) * (ymax - cy1) / (cy2 - cy1)
            y = ymax
        elif code_out & _CS_RIGHT:
            if abs(cx2 - cx1) < 1e-09:
                break
            y = cy1 + (cy2 - cy1) * (xmax - cx1) / (cx2 - cx1)
            x = xmax
        elif code_out & _CS_LEFT:
            if abs(cx2 - cx1) < 1e-09:
                break
            y = cy1 + (cy2 - cy1) * (xmin - cx1) / (cx2 - cx1)
            x = xmin
        intersections.append((x, y))
        if code_out == c1:
            cx1, cy1 = (x, y)
            c1 = get_cs_outcode(cx1, cy1, xmin, ymin, xmax, ymax)
        else:
            cx2, cy2 = (x, y)
            c2 = get_cs_outcode(cx2, cy2, xmin, ymin, xmax, ymax)
    return ((cx1, cy1, cx2, cy2), code1, code2, intersections, 'CLIPPED (Boundary Intersected)')

class LiveClippingPanel:

    def __init__(self, parent_frame: tk.Frame, width: int=360, height: int=720, on_target_change: Optional[Callable[[int], None]]=None):
        self.frame = tk.Frame(parent_frame, bg='#0d131f', width=width, height=height)
        self.frame.pack_propagate(False)
        self.width = width
        self.height = height
        self.on_target_change = on_target_change
        self.selected_target_id = 1
        self.method_mode = 'Sutherland-Hodgman'
        self.animating = False
        self.anim_stage_idx = 0
        self.anim_stages: List[Tuple[str, Points, List[Point]]] = []
        self._current_vertices: Points = []
        self._current_window: Tuple[float, float, float, float] = (110.0, 90.0, 870.0, 630.0)
        self.target_name = 'Player Laser Bolt'
        self.theme_color = '#38bdf8'
        self._build_ui()

    def _build_ui(self):
        title_box = tk.Frame(self.frame, bg='#111827', padx=8, pady=6)
        title_box.pack(fill=tk.X, side=tk.TOP)
        tk.Label(title_box, text='LIVE CLIPPING ENGINE', font=('Consolas', 11, 'bold'), fg='#22c55e', bg='#111827').pack(anchor='w')
        tk.Label(title_box, text='Sutherland-Hodgman & Cohen-Sutherland • Phase 5', font=('Consolas', 8), fg='#94a3b8', bg='#111827').pack(anchor='w')
        sel_box = tk.LabelFrame(self.frame, text=' Select Target to Clip ', font=('Consolas', 8, 'bold'), fg='#38bdf8', bg='#0d131f', padx=4, pady=4)
        sel_box.pack(fill=tk.X, padx=6, pady=3)
        btn_row1 = tk.Frame(sel_box, bg='#0d131f')
        btn_row1.pack(fill=tk.X, pady=1)
        btn_row2 = tk.Frame(sel_box, bg='#0d131f')
        btn_row2.pack(fill=tk.X, pady=1)
        self.btn_targets = {}
        targets = [(1, 'Player Bolt', '#38bdf8', btn_row1), (2, 'Enemy Cone', '#f59e0b', btn_row1), (3, 'Cam Cone', '#06b6d4', btn_row1), (4, 'Guard Body', '#ef4444', btn_row1), (5, 'Enemy Laser', '#f43f5e', btn_row2), (6, 'Crate Edge', '#94a3b8', btn_row2), (7, 'Shield Arc', '#00e5ff', btn_row2), (8, 'Exit Pad', '#22c55e', btn_row2)]
        for tid, name, color, row in targets:
            b = tk.Button(row, text=name, font=('Consolas', 7, 'bold'), bg='#1e293b', fg=color, activebackground='#334155', activeforeground='#ffffff', relief=tk.FLAT, padx=3, pady=2, command=lambda t=tid: self.set_target(t))
            b.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
            self.btn_targets[tid] = b
        method_row = tk.Frame(self.frame, bg='#0d131f', padx=6, pady=2)
        method_row.pack(fill=tk.X)
        self.btn_m_sh = tk.Button(method_row, text='Sutherland-Hodgman (Polygon)', font=('Consolas', 8, 'bold'), bg='#334155', fg='#22c55e', relief=tk.SUNKEN, command=lambda: self.set_method('Sutherland-Hodgman'))
        self.btn_m_sh.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        self.btn_m_cs = tk.Button(method_row, text='Cohen-Sutherland (Line)', font=('Consolas', 8, 'bold'), bg='#1e293b', fg='#38bdf8', relief=tk.FLAT, command=lambda: self.set_method('Cohen-Sutherland'))
        self.btn_m_cs.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        diag_box = tk.LabelFrame(self.frame, text=' Live Clipping Diagnostics ', font=('Consolas', 8, 'bold'), fg='#facc15', bg='#0d131f', padx=6, pady=3)
        diag_box.pack(fill=tk.X, padx=6, pady=2)
        self.lbl_target = tk.Label(diag_box, text='Target: Player Bolt', font=('Consolas', 9, 'bold'), fg='#38bdf8', bg='#0d131f', anchor='w')
        self.lbl_target.pack(fill=tk.X)
        self.lbl_window = tk.Label(diag_box, text='Window: [X: 110..870 | Y: 90..630]', font=('Consolas', 8), fg='#cbd5e1', bg='#0d131f', anchor='w')
        self.lbl_window.pack(fill=tk.X)
        self.lbl_v_in = tk.Label(diag_box, text='Input Verts  : 2 pts -> [(---, ---), (---, ---)]', font=('Consolas', 8), fg='#94a3b8', bg='#0d131f', anchor='w')
        self.lbl_v_in.pack(fill=tk.X)
        self.lbl_v_out = tk.Label(diag_box, text='Clipped Verts: 2 pts -> [(---, ---), (---, ---)]', font=('Consolas', 8, 'bold'), fg='#22c55e', bg='#0d131f', anchor='w')
        self.lbl_v_out.pack(fill=tk.X)
        self.lbl_status = tk.Label(diag_box, text='Status: FULLY INSIDE VIEWPORT', font=('Consolas', 8, 'bold'), fg='#38bdf8', bg='#0d131f', anchor='w')
        self.lbl_status.pack(fill=tk.X)
        self.cs_box = tk.LabelFrame(self.frame, text=' Cohen-Sutherland 4-Bit Outcodes [T B R L] ', font=('Consolas', 8, 'bold'), fg='#38bdf8', bg='#0d131f', padx=6, pady=2)
        self.cs_box.pack(fill=tk.X, padx=6, pady=2)
        self.lbl_p1_code = tk.Label(self.cs_box, text='P1 Outcode: [0000] (INSIDE)', font=('Consolas', 8, 'bold'), fg='#22c55e', bg='#0d131f', anchor='w')
        self.lbl_p1_code.pack(fill=tk.X)
        self.lbl_p2_code = tk.Label(self.cs_box, text='P2 Outcode: [0000] (INSIDE)', font=('Consolas', 8, 'bold'), fg='#22c55e', bg='#0d131f', anchor='w')
        self.lbl_p2_code.pack(fill=tk.X)
        self.lbl_bitwise = tk.Label(self.cs_box, text='Bitwise: (C1 & C2) = 0000 | (C1 | C2) = 0000', font=('Consolas', 7), fg='#94a3b8', bg='#0d131f', anchor='w')
        self.lbl_bitwise.pack(fill=tk.X)
        canvas_box = tk.LabelFrame(self.frame, text=' Magnified Clipping Preview ', font=('Consolas', 8, 'bold'), fg='#a78bfa', bg='#0d131f', padx=4, pady=2)
        canvas_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)
        self.preview_canvas = tk.Canvas(canvas_box, width=320, height=200, bg='#030712', highlightthickness=1, highlightbackground='#1f2937')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        ctrl_box = tk.Frame(self.frame, bg='#0d131f', padx=6, pady=3)
        ctrl_box.pack(fill=tk.X, side=tk.BOTTOM)
        self.btn_slow_mo = tk.Button(ctrl_box, text='Slow-Mo 4-Stage Clipping Demo [F]', font=('Consolas', 9, 'bold'), bg='#1e293b', fg='#22c55e', activebackground='#334155', activeforeground='#ffffff', relief=tk.FLAT, pady=3, command=self.trigger_slow_mo_demo)
        self.btn_slow_mo.pack(fill=tk.X, pady=1)
        self.highlight_button(1)

    def highlight_button(self, tid: int):
        self.selected_target_id = tid
        for i, b in self.btn_targets.items():
            if i == tid:
                b.config(relief=tk.SUNKEN, bg='#334155')
            else:
                b.config(relief=tk.FLAT, bg='#1e293b')

    def set_target(self, tid: int, notify: bool=True):
        self.highlight_button(tid)
        if tid in (1, 5, 6, 7):
            self.set_method('Cohen-Sutherland', notify=False)
        else:
            self.set_method('Sutherland-Hodgman', notify=False)
        if notify and self.on_target_change:
            self.on_target_change(tid)

    def set_method(self, method: str, notify: bool=True):
        self.method_mode = method
        if method == 'Sutherland-Hodgman':
            self.btn_m_sh.config(relief=tk.SUNKEN, bg='#334155')
            self.btn_m_cs.config(relief=tk.FLAT, bg='#1e293b')
            self.btn_slow_mo.config(text='Slow-Mo 4-Stage Clipping Demo [F]')
        else:
            self.btn_m_cs.config(relief=tk.SUNKEN, bg='#334155')
            self.btn_m_sh.config(relief=tk.FLAT, bg='#1e293b')
            self.btn_slow_mo.config(text='Slow-Mo Line Intersection Demo [F]')
        if self._current_vertices:
            self._render_preview()

    def update_live_clipping(self, vertices: Points, window: Tuple[float, float, float, float], target_name: str, theme_color: str='#38bdf8'):
        if not vertices or len(vertices) < 2:
            return
        self._current_vertices = list(vertices)
        self._current_window = window
        self.target_name = target_name
        self.theme_color = theme_color
        xmin, ymin, xmax, ymax = window
        self.lbl_target.config(text=f'Target: {target_name}', fg=theme_color)
        self.lbl_window.config(text=f'Window: [X: {xmin:.0f}..{xmax:.0f} | Y: {ymin:.0f}..{ymax:.0f}]')
        n_in = len(vertices)
        if n_in == 2:
            p1, p2 = (vertices[0], vertices[1])
            self.lbl_v_in.config(text=f'In : P1({p1[0]:.1f}, {p1[1]:.1f}) -> P2({p2[0]:.1f}, {p2[1]:.1f})')
        else:
            self.lbl_v_in.config(text=f'In : {n_in} Verts -> V0({vertices[0][0]:.0f},{vertices[0][1]:.0f}) ... V{n_in - 1}({vertices[-1][0]:.0f},{vertices[-1][1]:.0f})')
        if not self.animating:
            self._render_preview()

    def _render_preview(self):
        vertices = self._current_vertices
        if not vertices or len(vertices) < 2:
            return
        xmin, ymin, xmax, ymax = self._current_window
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        if cw <= 1:
            cw = 320
        if ch <= 1:
            ch = 200
        self.preview_canvas.delete('all')
        all_x = [v[0] for v in vertices] + [xmin, xmax]
        all_y = [v[1] for v in vertices] + [ymin, ymax]
        min_gx, max_gx = (min(all_x), max(all_x))
        min_gy, max_gy = (min(all_y), max(all_y))
        span_x = max(1.0, max_gx - min_gx)
        span_y = max(1.0, max_gy - min_gy)
        margin = 24.0
        scale = min((cw - margin * 2) / span_x, (ch - margin * 2) / span_y)
        cx_off = (cw - span_x * scale) / 2.0
        cy_off = (ch - span_y * scale) / 2.0

        def to_pv(x: float, y: float) -> Tuple[float, float]:
            return (cx_off + (x - min_gx) * scale, cy_off + (y - min_gy) * scale)
        wx1, wy1 = to_pv(xmin, ymin)
        wx2, wy2 = to_pv(xmax, ymax)
        self.preview_canvas.create_rectangle(wx1, wy1, wx2, wy2, outline='#f59e0b', width=2, dash=(4, 3), tags='pv_window')
        self.preview_canvas.create_text((wx1 + wx2) / 2.0, wy1 - 8, text=f'CLIPPING WINDOW [{xmin:.0f}..{xmax:.0f}, {ymin:.0f}..{ymax:.0f}]', fill='#f59e0b', font=('Consolas', 7, 'bold'), tags='pv_win_lbl')
        if self.method_mode == 'Sutherland-Hodgman' and len(vertices) >= 3:
            stages, clipped_poly, inters = sutherland_hodgman_detailed(vertices, xmin, ymin, xmax, ymax)
            n_out = len(clipped_poly)
            pv_orig = [to_pv(x, y) for x, y in vertices]
            flat_orig = [c for pt in pv_orig for c in pt]
            self.preview_canvas.create_polygon(flat_orig, fill='', outline='#64748b', width=1, dash=(3, 2), tags='pv_orig')
            if n_out >= 3:
                pv_clipped = [to_pv(x, y) for x, y in clipped_poly]
                flat_clip = [c for pt in pv_clipped for c in pt]
                self.preview_canvas.create_polygon(flat_clip, fill='#065f46', outline=self.theme_color, width=2, tags='pv_clipped')
                for idx, (px, py) in enumerate(pv_clipped):
                    self.preview_canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill='#22c55e', outline='#ffffff', width=1)
                self.lbl_v_out.config(text=f'Out: {n_out} Verts -> V0({clipped_poly[0][0]:.0f},{clipped_poly[0][1]:.0f}) ... V{n_out - 1}({clipped_poly[-1][0]:.0f},{clipped_poly[-1][1]:.0f})', fg='#22c55e')
                self.lbl_status.config(text=f'Status: CLIPPED ({len(vertices)} in -> {n_out} out | {len(inters)} cuts)', fg='#22c55e')
            else:
                self.lbl_v_out.config(text='Out: 0 Verts (CULLED - Outside Viewport)', fg='#ef4444')
                self.lbl_status.config(text='Status: COMPLETELY OUTSIDE (Culled)', fg='#ef4444')
            for ix, iy in inters:
                px, py = to_pv(ix, iy)
                self.preview_canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill='#ef4444', outline='#ffffff', width=1.5, tags='pv_inter')
            cx_poly = sum((v[0] for v in vertices)) / len(vertices)
            cy_poly = sum((v[1] for v in vertices)) / len(vertices)
            c_code = get_cs_outcode(cx_poly, cy_poly, xmin, ymin, xmax, ymax)
            self.lbl_p1_code.config(text=f'Centroid Code: {outcode_to_str(c_code)}', fg='#facc15')
            self.lbl_p2_code.config(text=f'Sutherland-Hodgman: 4 Stages Evaluated (L, R, T, B)', fg='#38bdf8')
            self.lbl_bitwise.config(text=f'Total Intersections Generated: {len(inters)} points on boundary lines', fg='#cbd5e1')
        else:
            p1, p2 = (vertices[0], vertices[1])
            clipped_line, c1, c2, inters, status_text = cohen_sutherland_detailed(p1[0], p1[1], p2[0], p2[1], xmin, ymin, xmax, ymax)
            p1_v = to_pv(p1[0], p1[1])
            p2_v = to_pv(p2[0], p2[1])
            self.preview_canvas.create_line(p1_v[0], p1_v[1], p2_v[0], p2_v[1], fill='#64748b', width=1.5, dash=(3, 2), tags='pv_orig_line')
            if clipped_line:
                cp1_v = to_pv(clipped_line[0], clipped_line[1])
                cp2_v = to_pv(clipped_line[2], clipped_line[3])
                self.preview_canvas.create_line(cp1_v[0], cp1_v[1], cp2_v[0], cp2_v[1], fill=self.theme_color, width=3, capstyle='round', tags='pv_clip_line')
                self.lbl_v_out.config(text=f'Out: ({clipped_line[0]:.1f}, {clipped_line[1]:.1f}) -> ({clipped_line[2]:.1f}, {clipped_line[3]:.1f})', fg='#22c55e')
            else:
                self.lbl_v_out.config(text='Out: None (Line Segment Rejected)', fg='#ef4444')
            self.lbl_status.config(text=f'Status: {status_text}', fg='#22c55e' if clipped_line else '#ef4444')
            c1_str = outcode_to_str(c1)
            c2_str = outcode_to_str(c2)
            c1_col = '#22c55e' if c1 == 0 else '#f43f5e'
            c2_col = '#22c55e' if c2 == 0 else '#f43f5e'
            self.lbl_p1_code.config(text=f'P1 Code: {c1_str}', fg=c1_col)
            self.lbl_p2_code.config(text=f'P2 Code: {c2_str}', fg=c2_col)
            bit_and = f'{c1 & c2:04b}'
            bit_or = f'{c1 | c2:04b}'
            self.lbl_bitwise.config(text=f"(C1 & C2)={bit_and} {('[REJECT]' if c1 & c2 else '[TEST]')} | (C1 | C2)={bit_or} {('[ALL IN]' if c1 | c2 == 0 else '')}", fg='#38bdf8')
            self.preview_canvas.create_oval(p1_v[0] - 3, p1_v[1] - 3, p1_v[0] + 3, p1_v[1] + 3, fill=c1_col, outline='#ffffff')
            self.preview_canvas.create_oval(p2_v[0] - 3, p2_v[1] - 3, p2_v[0] + 3, p2_v[1] + 3, fill=c2_col, outline='#ffffff')
            for ix, iy in inters:
                px, py = to_pv(ix, iy)
                self.preview_canvas.create_oval(px - 4, py - 4, px + 4, py + 4, fill='#ef4444', outline='#ffffff', width=1.5, tags='pv_inter')

    def trigger_slow_mo_demo(self):
        if not self._current_vertices or len(self._current_vertices) < 3:
            return
        xmin, ymin, xmax, ymax = self._current_window
        stages, _, _ = sutherland_hodgman_detailed(self._current_vertices, xmin, ymin, xmax, ymax)
        self.anim_stages = stages
        self.anim_stage_idx = 0
        self.animating = True
        self._animate_stage()

    def _animate_stage(self):
        if not self.animating or self.anim_stage_idx >= len(self.anim_stages):
            self.animating = False
            self.lbl_status.config(text='Status: 4-STAGE DEMO COMPLETE', fg='#22c55e')
            return
        stage_name, stage_poly, stage_inters = self.anim_stages[self.anim_stage_idx]
        self.lbl_status.config(text=f'DEMO: {stage_name}', fg='#facc15')
        cw = self.preview_canvas.winfo_width()
        ch = self.preview_canvas.winfo_height()
        if cw <= 1:
            cw = 320
        if ch <= 1:
            ch = 200
        xmin, ymin, xmax, ymax = self._current_window
        all_x = [v[0] for v in self._current_vertices] + [xmin, xmax]
        all_y = [v[1] for v in self._current_vertices] + [ymin, ymax]
        min_gx, max_gx = (min(all_x), max(all_x))
        min_gy, max_gy = (min(all_y), max(all_y))
        span_x = max(1.0, max_gx - min_gx)
        span_y = max(1.0, max_gy - min_gy)
        margin = 24.0
        scale = min((cw - margin * 2) / span_x, (ch - margin * 2) / span_y)
        cx_off = (cw - span_x * scale) / 2.0
        cy_off = (ch - span_y * scale) / 2.0

        def to_pv(x: float, y: float) -> Tuple[float, float]:
            return (cx_off + (x - min_gx) * scale, cy_off + (y - min_gy) * scale)
        self.preview_canvas.delete('all')
        wx1, wy1 = to_pv(xmin, ymin)
        wx2, wy2 = to_pv(xmax, ymax)
        bdry_colors = ['#ef4444', '#38bdf8', '#22c55e', '#facc15']
        cur_bdry_col = bdry_colors[self.anim_stage_idx % 4]
        self.preview_canvas.create_rectangle(wx1, wy1, wx2, wy2, outline='#475569', width=1, dash=(3, 3))
        if self.anim_stage_idx == 0:
            self.preview_canvas.create_line(wx1, 0, wx1, ch, fill=cur_bdry_col, width=3)
        elif self.anim_stage_idx == 1:
            self.preview_canvas.create_line(wx2, 0, wx2, ch, fill=cur_bdry_col, width=3)
        elif self.anim_stage_idx == 2:
            self.preview_canvas.create_line(0, wy1, cw, wy1, fill=cur_bdry_col, width=3)
        else:
            self.preview_canvas.create_line(0, wy2, cw, wy2, fill=cur_bdry_col, width=3)
        pv_orig = [to_pv(x, y) for x, y in self._current_vertices]
        flat_orig = [c for pt in pv_orig for c in pt]
        self.preview_canvas.create_polygon(flat_orig, fill='', outline='#64748b', width=1, dash=(2, 2))
        if len(stage_poly) >= 3:
            pv_stage = [to_pv(x, y) for x, y in stage_poly]
            flat_stage = [c for pt in pv_stage for c in pt]
            self.preview_canvas.create_polygon(flat_stage, fill='#1e293b', outline=cur_bdry_col, width=2)
            for px, py in pv_stage:
                self.preview_canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill=cur_bdry_col, outline='#ffffff')
        for ix, iy in stage_inters:
            px, py = to_pv(ix, iy)
            self.preview_canvas.create_oval(px - 5, py - 5, px + 5, py + 5, fill='#ef4444', outline='#ffffff', width=2)
        self.anim_stage_idx += 1
        self.frame.after(750, self._animate_stage)
