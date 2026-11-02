import sys
import os
import math
from typing import List, Tuple, Optional
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)
from cg_math import CGMath
try:
    import pygame
except ImportError:
    print('[ERROR] Pygame is required for the visualizer. Install via: pip install pygame')
    sys.exit(1)
Point = Tuple[float, float]
Points = List[Point]
COLOR_BG = (7, 10, 18)
COLOR_GRID = (22, 29, 44)
COLOR_AXIS = (45, 55, 75)
COLOR_ORIGINAL = (210, 220, 235)
COLOR_ORIG_FILL = (148, 163, 184, 30)
COLOR_CLIPPED = (34, 197, 94)
COLOR_CLIP_FILL = (34, 197, 94, 65)
COLOR_CS_LINE = (56, 189, 248)
COLOR_WINDOW_BOX = (245, 158, 11)
COLOR_WINDOW_BG = (16, 24, 39, 40)
COLOR_INTERSECT = (239, 68, 68)
COLOR_TEXT = (241, 245, 249)
COLOR_DIM = (100, 116, 139)
COLOR_YELLOW = (250, 204, 21)
COLOR_HUD_BG = (13, 19, 31)
COLOR_HUD_LINE = (30, 41, 59)
COLOR_BTN_BG = (24, 34, 53)
COLOR_BTN_HOVER = (37, 51, 79)
COLOR_OUTCODE = (180, 83, 9)
PRESET_POLYGONS = [('Triangle (Crossing)', [(140.0, 130.0), (460.0, 170.0), (290.0, 470.0)]), ('Convex Pentagon', [(280.0, 110.0), (500.0, 210.0), (440.0, 460.0), (150.0, 430.0), (120.0, 230.0)]), ('Concave Star (10 Vertices)', [(300.0, 90.0), (345.0, 210.0), (470.0, 210.0), (370.0, 280.0), (410.0, 410.0), (300.0, 330.0), (190.0, 410.0), (230.0, 280.0), (130.0, 210.0), (255.0, 210.0)]), ('Vision Cone (Assassin Game)', [(120.0, 280.0), (480.0, 140.0), (510.0, 210.0), (520.0, 280.0), (510.0, 350.0), (480.0, 420.0)]), ('Arrow / Dart', [(140.0, 230.0), (360.0, 120.0), (360.0, 200.0), (480.0, 200.0), (480.0, 260.0), (360.0, 260.0), (360.0, 340.0)]), ('Box / Quad (Angled)', [(150.0, 150.0), (480.0, 130.0), (450.0, 420.0), (120.0, 380.0)])]
METHODS = [('Sutherland-Hodgman', 'Sutherland-Hodgman Polygon Clipping (Closed Polygon)'), ('Cohen-Sutherland', 'Cohen-Sutherland Line Clipping (Edge-by-Edge)'), ('Dual Comparison', 'Simultaneous Comparison (Sutherland-Hodgman vs Cohen-Sutherland)')]
VIEWPORT_PRESETS = [('Standard Window', (180.0, 160.0, 440.0, 390.0)), ('Camera Viewport', (150.0, 140.0, 480.0, 420.0)), ('Tight Center', (220.0, 200.0, 380.0, 340.0))]

def polygon_area(pts: Points) -> float:
    if len(pts) < 3:
        return 0.0
    area = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) * 0.5

def run_interactive_clipping_demo():
    pygame.init()
    pygame.font.init()
    WIDTH, HEIGHT = (1120, 720)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Phase 5: Interactive Polygon & Line Clipping Visualizer')
    font_title = pygame.font.SysFont('Consolas', 15, bold=True)
    font_bold = pygame.font.SysFont('Consolas', 12, bold=True)
    font_body = pygame.font.SysFont('Consolas', 11)
    font_small = pygame.font.SysFont('Consolas', 10)
    font_code = pygame.font.SysFont('Consolas', 10, bold=True)
    clock = pygame.time.Clock()
    preset_poly_idx = 0
    method_idx = 0
    vp_preset_idx = 0
    original_points: Points = list(PRESET_POLYGONS[preset_poly_idx][1])
    xmin, ymin, xmax, ymax = VIEWPORT_PRESETS[vp_preset_idx][1]
    pipeline_step = 0
    drag_poly_pt = -1
    drag_win_corner = -1
    hover_win_corner = -1
    modal: Optional[dict] = None

    def open_modal(mtype: str):
        nonlocal modal
        if mtype == 'custom_pts':
            val_str = ', '.join((f'{int(round(p[0]))} {int(round(p[1]))}' for p in original_points))
            modal = {'type': 'custom_pts', 'title': 'USER INPUT: Enter Polygon Vertices', 'subtitle': 'Format: x1 y1, x2 y2, x3 y3, ... (minimum 3 points)', 'fields': [{'label': 'Vertices Coordinates', 'val': val_str}], 'active_field': 0}
        elif mtype == 'custom_win':
            modal = {'type': 'custom_win', 'title': 'USER INPUT: Custom Viewport Bounds', 'subtitle': 'Specify clipping window bounds [xmin, ymin, xmax, ymax]', 'fields': [{'label': 'X Min (Left)', 'val': str(int(round(xmin)))}, {'label': 'Y Min (Top)', 'val': str(int(round(ymin)))}, {'label': 'X Max (Right)', 'val': str(int(round(xmax)))}, {'label': 'Y Max (Bottom)', 'val': str(int(round(ymax)))}], 'active_field': 0}

    def apply_modal():
        nonlocal modal, original_points, xmin, ymin, xmax, ymax
        if not modal:
            return
        mtype = modal['type']
        fields = modal['fields']
        try:
            if mtype == 'custom_pts':
                raw_text = fields[0]['val'].replace(';', ',').replace('\n', ',')
                tokens = raw_text.split(',')
                new_pts: Points = []
                for tok in tokens:
                    parts = tok.strip().split()
                    if len(parts) >= 2:
                        px = float(parts[0])
                        py = float(parts[1])
                        new_pts.append((px, py))
                if len(new_pts) >= 3:
                    original_points = new_pts
                    print(f'[INPUT ACCEPTED] Custom polygon with {len(new_pts)} vertices loaded.')
                else:
                    print('[INPUT ERROR] Minimum 3 vertices required for a polygon.')
            elif mtype == 'custom_win':
                nx1 = float(fields[0]['val'])
                ny1 = float(fields[1]['val'])
                nx2 = float(fields[2]['val'])
                ny2 = float(fields[3]['val'])
                if nx1 < nx2 and ny1 < ny2:
                    xmin, ymin, xmax, ymax = (nx1, ny1, nx2, ny2)
                    print(f'[VIEWPORT UPDATED] xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}')
                else:
                    print('[INPUT ERROR] xmin must be < xmax and ymin < ymax.')
        except Exception as err:
            print(f'[MODAL ERROR] {err}')
        modal = None

    def compute_sutherland_stages(poly: Points, x1: float, y1: float, x2: float, y2: float) -> List[Points]:
        stages = [poly]
        curr = poly

        def intersection(p1: Point, p2: Point, edge_type: int) -> Point:
            px1, py1 = p1
            px2, py2 = p2
            dx = px2 - px1
            dy = py2 - py1
            if edge_type == 0:
                x = x1
                y = py1 + dy * (x1 - px1) / dx if dx != 0 else py1
            elif edge_type == 1:
                x = x2
                y = py1 + dy * (x2 - px1) / dx if dx != 0 else py1
            elif edge_type == 2:
                y = y1
                x = px1 + dx * (y1 - py1) / dy if dy != 0 else px1
            else:
                y = y2
                x = px1 + dx * (y2 - py1) / dy if dy != 0 else px1
            return (x, y)
        for edge_type in range(4):
            clipped = []
            if not curr:
                stages.append([])
                continue
            s = curr[-1]
            for p in curr:
                if edge_type == 0:
                    s_in = s[0] >= x1
                    p_in = p[0] >= x1
                elif edge_type == 1:
                    s_in = s[0] <= x2
                    p_in = p[0] <= x2
                elif edge_type == 2:
                    s_in = s[1] >= y1
                    p_in = p[1] >= y1
                else:
                    s_in = s[1] <= y2
                    p_in = p[1] <= y2
                if p_in:
                    if not s_in:
                        clipped.append(intersection(s, p, edge_type))
                    clipped.append(p)
                elif s_in:
                    clipped.append(intersection(s, p, edge_type))
                s = p
            curr = clipped
            stages.append(curr)
        return stages

    def compute_cohen_sutherland_edges(poly: Points, x1: float, y1: float, x2: float, y2: float):
        edges = []
        n = len(poly)
        if n < 2:
            return edges
        for i in range(n):
            p1 = poly[i]
            p2 = poly[(i + 1) % n]
            res = CGMath.clip_line_cohen_sutherland(p1[0], p1[1], p2[0], p2[1], x1, y1, x2, y2)
            c1 = CGMath.get_code(p1[0], p1[1], x1, y1, x2, y2)
            c2 = CGMath.get_code(p2[0], p2[1], x1, y1, x2, y2)
            edges.append((p1, p2, res, c1, c2))
        return edges
    running = True
    while running:
        w, h = screen.get_size()
        mouse_pos = pygame.mouse.get_pos()
        canvas_w = w - 360
        canvas_h = h - 60
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if modal:
                    if event.key == pygame.K_ESCAPE:
                        modal = None
                    elif event.key == pygame.K_RETURN:
                        apply_modal()
                    elif event.key == pygame.K_TAB:
                        modal['active_field'] = (modal['active_field'] + 1) % len(modal['fields'])
                    elif event.key == pygame.K_BACKSPACE:
                        act = modal['active_field']
                        modal['fields'][act]['val'] = modal['fields'][act]['val'][:-1]
                    elif event.unicode and (event.unicode.isprintable() or event.unicode in ('-', '.', ' ', ',')):
                        act = modal['active_field']
                        modal['fields'][act]['val'] += event.unicode
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_1, pygame.K_p):
                    preset_poly_idx = (preset_poly_idx + 1) % len(PRESET_POLYGONS)
                    original_points = list(PRESET_POLYGONS[preset_poly_idx][1])
                    pipeline_step = 0
                elif event.key in (pygame.K_2, pygame.K_m):
                    method_idx = (method_idx + 1) % len(METHODS)
                elif event.key in (pygame.K_3, pygame.K_u):
                    open_modal('custom_pts')
                elif event.key in (pygame.K_4, pygame.K_w):
                    open_modal('custom_win')
                elif event.key in (pygame.K_5, pygame.K_s):
                    pipeline_step = (pipeline_step + 1) % 5
                elif event.key in (pygame.K_SPACE, pygame.K_r):
                    original_points = list(PRESET_POLYGONS[preset_poly_idx][1])
                    pipeline_step = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not modal and event.button == 1:
                    mx, my = event.pos
                    if my >= h - 56:
                        btn_clicked = mx // (w // 7)
                        if btn_clicked == 0:
                            preset_poly_idx = (preset_poly_idx + 1) % len(PRESET_POLYGONS)
                            original_points = list(PRESET_POLYGONS[preset_poly_idx][1])
                            pipeline_step = 0
                        elif btn_clicked == 1:
                            method_idx = (method_idx + 1) % len(METHODS)
                        elif btn_clicked == 2:
                            open_modal('custom_pts')
                        elif btn_clicked == 3:
                            open_modal('custom_win')
                        elif btn_clicked == 4:
                            pipeline_step = (pipeline_step + 1) % 5
                        elif btn_clicked == 5:
                            vp_preset_idx = (vp_preset_idx + 1) % len(VIEWPORT_PRESETS)
                            xmin, ymin, xmax, ymax = VIEWPORT_PRESETS[vp_preset_idx][1]
                        elif btn_clicked == 6:
                            original_points = list(PRESET_POLYGONS[preset_poly_idx][1])
                            pipeline_step = 0
                    else:
                        found_vertex = False
                        for i, pt in enumerate(original_points):
                            if math.hypot(pt[0] - mx, pt[1] - my) <= 12:
                                drag_poly_pt = i
                                found_vertex = True
                                break
                        if not found_vertex:
                            corners = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
                            for ci, (cx, cy) in enumerate(corners):
                                if math.hypot(cx - mx, cy - my) <= 12:
                                    drag_win_corner = ci
                                    break
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drag_poly_pt = -1
                    drag_win_corner = -1
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if drag_poly_pt != -1:
                    cmx = max(60.0, min(float(canvas_w - 40), float(mx)))
                    cmy = max(60.0, min(float(canvas_h - 40), float(my)))
                    original_points[drag_poly_pt] = (cmx, cmy)
                elif drag_win_corner != -1:
                    cmx = max(60.0, min(float(canvas_w - 40), float(mx)))
                    cmy = max(60.0, min(float(canvas_h - 40), float(my)))
                    if drag_win_corner == 0:
                        xmin = min(cmx, xmax - 40)
                        ymin = min(cmy, ymax - 40)
                    elif drag_win_corner == 1:
                        xmax = max(cmx, xmin + 40)
                        ymin = min(cmy, ymax - 40)
                    elif drag_win_corner == 2:
                        xmax = max(cmx, xmin + 40)
                        ymax = max(cmy, ymin + 40)
                    elif drag_win_corner == 3:
                        xmin = min(cmx, xmax - 40)
                        ymax = max(cmy, ymin + 40)
        sh_stages = compute_sutherland_stages(original_points, xmin, ymin, xmax, ymax)
        final_sh_poly = sh_stages[4]
        active_display_poly = sh_stages[pipeline_step] if pipeline_step > 0 else final_sh_poly
        cs_edges = compute_cohen_sutherland_edges(original_points, xmin, ymin, xmax, ymax)
        screen.fill(COLOR_BG)
        for gx in range(40, canvas_w, 40):
            pygame.draw.line(screen, COLOR_GRID, (gx, 45), (gx, canvas_h), 1)
        for gy in range(45, canvas_h, 40):
            pygame.draw.line(screen, COLOR_GRID, (40, gy), (canvas_w, gy), 1)
        pygame.draw.line(screen, COLOR_AXIS, (40, 45), (canvas_w, 45), 2)
        pygame.draw.line(screen, COLOR_AXIS, (40, 45), (40, canvas_h), 2)
        for tx in range(100, canvas_w, 100):
            pygame.draw.line(screen, COLOR_AXIS, (tx, 41), (tx, 49), 1)
            t_lbl = font_small.render(str(tx), True, COLOR_DIM)
            screen.blit(t_lbl, (tx - 10, 28))
        for ty in range(100, canvas_h, 100):
            pygame.draw.line(screen, COLOR_AXIS, (36, ty), (44, ty), 1)
            t_lbl = font_small.render(str(ty), True, COLOR_DIM)
            screen.blit(t_lbl, (12, ty - 6))

        def draw_dashed(x_start, y_start, x_end, y_end):
            dist = math.hypot(x_end - x_start, y_end - y_start)
            if dist < 1:
                return
            steps = int(dist // 8)
            dx = (x_end - x_start) / max(steps, 1)
            dy = (y_end - y_start) / max(steps, 1)
            for s in range(0, steps, 2):
                sx1 = x_start + s * dx
                sy1 = y_start + s * dy
                sx2 = x_start + min(s + 1, steps) * dx
                sy2 = y_start + min(s + 1, steps) * dy
                pygame.draw.line(screen, (35, 45, 65), (sx1, sy1), (sx2, sy2), 1)
        draw_dashed(xmin, 45, xmin, canvas_h)
        draw_dashed(xmax, 45, xmax, canvas_h)
        draw_dashed(40, ymin, canvas_w, ymin)
        draw_dashed(40, ymax, canvas_w, ymax)
        codes = [('1001 (TL)', xmin - 55, ymin - 25), ('1000 (TOP)', (xmin + xmax) / 2 - 35, ymin - 25), ('1010 (TR)', xmax + 15, ymin - 25), ('0001 (LEFT)', xmin - 65, (ymin + ymax) / 2 - 8), ('0000 (VIEWPORT)', (xmin + xmax) / 2 - 45, (ymin + ymax) / 2 - 8), ('0010 (RIGHT)', xmax + 15, (ymin + ymax) / 2 - 8), ('0101 (BL)', xmin - 55, ymax + 12), ('0100 (BOTTOM)', (xmin + xmax) / 2 - 42, ymax + 12), ('0110 (BR)', xmax + 15, ymax + 12)]
        for ctext, cx, cy in codes:
            if 40 <= cx <= canvas_w and 45 <= cy <= canvas_h:
                clbl = font_code.render(ctext, True, COLOR_OUTCODE)
                screen.blit(clbl, (cx, cy))
        vp_rect = pygame.Rect(int(xmin), int(ymin), int(xmax - xmin), int(ymax - ymin))
        vp_surf = pygame.Surface((vp_rect.width, vp_rect.height), pygame.SRCALPHA)
        vp_surf.fill(COLOR_WINDOW_BG)
        screen.blit(vp_surf, (vp_rect.x, vp_rect.y))
        pygame.draw.rect(screen, COLOR_WINDOW_BOX, vp_rect, 2)
        corners = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        for cx, cy in corners:
            pygame.draw.circle(screen, COLOR_WINDOW_BOX, (int(cx), int(cy)), 5)
        w_lbl1 = font_small.render(f'({int(xmin)}, {int(ymin)})', True, COLOR_WINDOW_BOX)
        w_lbl2 = font_small.render(f'({int(xmax)}, {int(ymax)})', True, COLOR_WINDOW_BOX)
        screen.blit(w_lbl1, (xmin + 6, ymin + 6))
        screen.blit(w_lbl2, (xmax - 95, ymax - 18))
        num_orig = len(original_points)
        if num_orig >= 3:
            orig_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(orig_surf, COLOR_ORIG_FILL, original_points)
            screen.blit(orig_surf, (0, 0))
            for i in range(num_orig):
                p1 = original_points[i]
                p2 = original_points[(i + 1) % num_orig]
                pygame.draw.line(screen, COLOR_ORIGINAL, p1, p2, 1)
            for i, p in enumerate(original_points):
                pygame.draw.circle(screen, COLOR_ORIGINAL, (int(p[0]), int(p[1])), 6)
                pygame.draw.circle(screen, (15, 23, 42), (int(p[0]), int(p[1])), 3)
                v_code = CGMath.get_code(p[0], p[1], xmin, ymin, xmax, ymax)
                v_str = f'P{i + 1} [{v_code:04b}]'
                v_lbl = font_bold.render(v_str, True, COLOR_ORIGINAL)
                screen.blit(v_lbl, (p[0] + 8, p[1] - 16))
        current_method = METHODS[method_idx][0]
        if current_method in ('Sutherland-Hodgman', 'Dual Comparison'):
            if len(active_display_poly) >= 3:
                clip_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(clip_surf, COLOR_CLIP_FILL, active_display_poly)
                screen.blit(clip_surf, (0, 0))
                n_clip = len(active_display_poly)
                for i in range(n_clip):
                    cp1 = active_display_poly[i]
                    cp2 = active_display_poly[(i + 1) % n_clip]
                    pygame.draw.line(screen, COLOR_CLIPPED, cp1, cp2, 3)
                for i, cp in enumerate(active_display_poly):
                    is_new = not any((math.hypot(cp[0] - op[0], cp[1] - op[1]) < 1.0 for op in original_points))
                    dot_color = COLOR_INTERSECT if is_new else COLOR_CLIPPED
                    pygame.draw.circle(screen, dot_color, (int(cp[0]), int(cp[1])), 6)
                    pygame.draw.circle(screen, (15, 23, 42), (int(cp[0]), int(cp[1])), 2)
                    pt_tag = f'I{i + 1}' if is_new else f'C{i + 1}'
                    lbl = font_bold.render(f'{pt_tag} ({int(cp[0])},{int(cp[1])})', True, dot_color)
                    screen.blit(lbl, (cp[0] + 8, cp[1] + 4))
        if current_method in ('Cohen-Sutherland', 'Dual Comparison'):
            for p1, p2, res, c1, c2 in cs_edges:
                if res is not None:
                    cx1, cy1, cx2, cy2 = res
                    pygame.draw.line(screen, COLOR_CS_LINE, (cx1, cy1), (cx2, cy2), 4)
                    if c1 != 0:
                        pygame.draw.circle(screen, COLOR_INTERSECT, (int(cx1), int(cy1)), 6)
                    if c2 != 0:
                        pygame.draw.circle(screen, COLOR_INTERSECT, (int(cx2), int(cy2)), 6)
        header_rect = pygame.Rect(0, 0, w, 44)
        pygame.draw.rect(screen, (13, 19, 31), header_rect)
        pygame.draw.line(screen, COLOR_HUD_LINE, (0, 44), (w, 44), 2)
        t_lbl = font_title.render('PHASE 5: ADVANCED POLYGON & LINE CLIPPING SUITE', True, COLOR_ORIGINAL)
        screen.blit(t_lbl, (15, 12))
        poly_lbl = font_bold.render(f'POLY: {PRESET_POLYGONS[preset_poly_idx][0]}', True, COLOR_YELLOW)
        screen.blit(poly_lbl, (460, 14))
        method_lbl = font_bold.render(f'METHOD: {METHODS[method_idx][0]}', True, COLOR_CLIPPED)
        screen.blit(method_lbl, (750, 14))
        card_w = 340
        card_x = w - card_w - 10
        card_rect = pygame.Rect(card_x, 52, card_w, h - 120)
        pygame.draw.rect(screen, COLOR_HUD_BG, card_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_HUD_LINE, card_rect, width=1, border_radius=6)
        cy_pos = 62
        c_title = font_bold.render('CLIPPING ENGINE ANALYTICS', True, COLOR_YELLOW)
        screen.blit(c_title, (card_x + 14, cy_pos))
        cy_pos += 22
        m_txt = font_small.render(f'Active Algorithm: {METHODS[method_idx][0]}', True, COLOR_TEXT)
        screen.blit(m_txt, (card_x + 14, cy_pos))
        cy_pos += 18
        vp_str = f'Viewport: [{int(xmin)}, {int(ymin)}] -> [{int(xmax)}, {int(ymax)}]'
        screen.blit(font_small.render(vp_str, True, COLOR_WINDOW_BOX), (card_x + 14, cy_pos))
        cy_pos += 20
        pygame.draw.line(screen, COLOR_HUD_LINE, (card_x + 10, cy_pos), (card_x + card_w - 10, cy_pos), 1)
        cy_pos += 10
        orig_area = polygon_area(original_points)
        clip_area = polygon_area(final_sh_poly)
        screen.blit(font_bold.render('METRIC                 ORIGINAL       CLIPPED', True, COLOR_YELLOW), (card_x + 14, cy_pos))
        cy_pos += 18
        s1 = f'Vertex Count           {len(original_points):<14} {len(final_sh_poly)}'
        screen.blit(font_small.render(s1, True, COLOR_TEXT), (card_x + 14, cy_pos))
        cy_pos += 16
        s2 = f'Polygon Area (sq px)   {int(orig_area):<14} {int(clip_area)}'
        screen.blit(font_small.render(s2, True, COLOR_TEXT), (card_x + 14, cy_pos))
        cy_pos += 16
        coverage = clip_area / orig_area * 100.0 if orig_area > 0 else 0.0
        s3 = f'Area Retained (%)      100.0%         {coverage:.1f}%'
        screen.blit(font_small.render(s3, True, COLOR_CLIPPED), (card_x + 14, cy_pos))
        cy_pos += 22
        pygame.draw.line(screen, COLOR_HUD_LINE, (card_x + 10, cy_pos), (card_x + card_w - 10, cy_pos), 1)
        cy_pos += 10
        screen.blit(font_bold.render('SUTHERLAND-HODGMAN PIPELINE', True, COLOR_YELLOW), (card_x + 14, cy_pos))
        cy_pos += 18
        stages_labels = [('All (Final Output)', len(final_sh_poly)), ('Stage 1: Clip Left (x >= xmin)', len(sh_stages[1])), ('Stage 2: Clip Right (x <= xmax)', len(sh_stages[2])), ('Stage 3: Clip Top (y >= ymin)', len(sh_stages[3])), ('Stage 4: Clip Bottom (y <= ymax)', len(sh_stages[4]))]
        for s_idx, (s_name, s_pts) in enumerate(stages_labels):
            is_active = pipeline_step == s_idx
            bullet = '>> ' if is_active else '   '
            color = COLOR_CLIPPED if is_active else COLOR_DIM
            st_str = f'{bullet}{s_name}: {s_pts} pts'
            screen.blit(font_small.render(st_str, True, color), (card_x + 14, cy_pos))
            cy_pos += 15
        cy_pos += 6
        pygame.draw.line(screen, COLOR_HUD_LINE, (card_x + 10, cy_pos), (card_x + card_w - 10, cy_pos), 1)
        cy_pos += 10
        screen.blit(font_bold.render('COHEN-SUTHERLAND EDGE TABLE', True, COLOR_YELLOW), (card_x + 14, cy_pos))
        cy_pos += 18
        screen.blit(font_code.render('Edge   Code1  Code2  Status', True, COLOR_DIM), (card_x + 14, cy_pos))
        cy_pos += 16
        for i, (p1, p2, res, c1, c2) in enumerate(cs_edges[:6]):
            if c1 | c2 == 0:
                status_str = 'ACCEPTED'
                s_color = COLOR_CLIPPED
            elif c1 & c2 != 0:
                status_str = 'REJECTED'
                s_color = COLOR_INTERSECT
            else:
                status_str = 'CLIPPED '
                s_color = COLOR_CS_LINE
            e_line = f'E{i + 1:<2}   {c1:04b}   {c2:04b}   {status_str}'
            screen.blit(font_code.render(e_line, True, s_color), (card_x + 14, cy_pos))
            cy_pos += 15
        hint_y = card_rect.bottom - 75
        pygame.draw.line(screen, COLOR_HUD_LINE, (card_x + 10, hint_y), (card_x + card_w - 10, hint_y), 1)
        screen.blit(font_small.render('Drag vertices P1-Pn to reshape polygon', True, COLOR_CLIPPED), (card_x + 14, hint_y + 8))
        screen.blit(font_small.render('Drag viewport corners to resize window', True, COLOR_WINDOW_BOX), (card_x + 14, hint_y + 24))
        screen.blit(font_small.render('Keys: 1=Poly, 2=Method, 3=Coords, 4=Window', True, COLOR_DIM), (card_x + 14, hint_y + 42))
        bar_rect = pygame.Rect(0, h - 56, w, 56)
        pygame.draw.rect(screen, (13, 19, 31), bar_rect)
        pygame.draw.line(screen, COLOR_HUD_LINE, (0, h - 56), (w, h - 56), 2)
        buttons = [('1. Poly Type', 'Cycle preset polygons'), ('2. Method', 'Toggle clipping algorithms'), ('3. Custom Coords', 'Input polygon vertices'), ('4. Custom Window', 'Input viewport coordinates'), ('5. Step Pipeline', 'Step Sutherland-Hodgman'), ('6. Window Presets', 'Cycle viewport sizes'), ('7. Reset', 'Reset to original points')]
        btn_w = w // len(buttons)
        for i, (btn_title, btn_sub) in enumerate(buttons):
            bx = i * btn_w
            b_rect = pygame.Rect(bx + 2, h - 52, btn_w - 4, 48)
            is_hover = b_rect.collidepoint(mouse_pos) and (not modal)
            bg_col = COLOR_BTN_HOVER if is_hover else COLOR_BTN_BG
            pygame.draw.rect(screen, bg_col, b_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_HUD_LINE, b_rect, width=1, border_radius=4)
            bt_surf = font_bold.render(btn_title, True, COLOR_ORIGINAL if not is_hover else COLOR_YELLOW)
            screen.blit(bt_surf, (bx + (btn_w - bt_surf.get_width()) // 2, h - 46))
            bs_surf = font_small.render(btn_sub, True, COLOR_DIM)
            screen.blit(bs_surf, (bx + (btn_w - bs_surf.get_width()) // 2, h - 26))
        if modal:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            mw, mh = (620, 240 + len(modal['fields']) * 50)
            mx = (w - mw) // 2
            my = (h - mh) // 2
            m_rect = pygame.Rect(mx, my, mw, mh)
            pygame.draw.rect(screen, (15, 23, 42), m_rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_YELLOW, m_rect, width=2, border_radius=8)
            m_title = font_title.render(modal['title'], True, COLOR_YELLOW)
            screen.blit(m_title, (mx + 20, my + 16))
            m_sub = font_small.render(modal['subtitle'], True, COLOR_DIM)
            screen.blit(m_sub, (mx + 20, my + 40))
            fy = my + 70
            for idx, f in enumerate(modal['fields']):
                is_act = idx == modal['active_field']
                f_lbl = font_bold.render(f['label'], True, COLOR_ORIGINAL if not is_act else COLOR_YELLOW)
                screen.blit(f_lbl, (mx + 20, fy))
                box_rect = pygame.Rect(mx + 20, fy + 20, mw - 40, 32)
                pygame.draw.rect(screen, (7, 10, 18), box_rect, border_radius=4)
                border_color = COLOR_YELLOW if is_act else COLOR_HUD_LINE
                pygame.draw.rect(screen, border_color, box_rect, width=1, border_radius=4)
                val_rendered = font_body.render(f['val'] + ('|' if is_act else ''), True, COLOR_TEXT)
                screen.blit(val_rendered, (mx + 28, fy + 26))
                fy += 60
            info_txt = font_small.render('[Enter] Submit Input   |   [Tab] Next Field   |   [Esc] Cancel', True, COLOR_DIM)
            screen.blit(info_txt, (mx + 20, mh + my - 32))
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
if __name__ == '__main__':
    run_interactive_clipping_demo()
