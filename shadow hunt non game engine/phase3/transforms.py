import math
from typing import List, Tuple, Union, Optional
Point = Tuple[float, float]
Points = List[Point]
Matrix3x3 = List[List[float]]
PI = math.pi

def identity() -> Matrix3x3:
    return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
identity_matrix = identity

def multiply_matrix(A: Matrix3x3, B: Matrix3x3) -> Matrix3x3:
    C = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                C[i][j] += A[i][k] * B[k][j]
    return C
matmul_3x3 = multiply_matrix

def translation_matrix(tx: float, ty: float, rep_type: int=2) -> Matrix3x3:
    T = identity()
    if rep_type == 1:
        T[2][0] = float(tx)
        T[2][1] = float(ty)
    else:
        T[0][2] = float(tx)
        T[1][2] = float(ty)
    return T

def scaling_matrix(sx: float, sy: Optional[float]=None, rep_type: int=2) -> Matrix3x3:
    if sy is None:
        sy = sx
    T = identity()
    T[0][0] = float(sx)
    T[1][1] = float(sy)
    return T

def rotation_matrix(angle: float, rep_type: int=2, is_deg: Optional[bool]=None) -> Matrix3x3:
    if is_deg is None:
        is_deg = abs(angle) > 2.0 * math.pi
    rad = math.radians(angle) if is_deg else float(angle)
    c = math.cos(rad)
    s = math.sin(rad)
    T = identity()
    if rep_type == 1:
        T[0][0] = c
        T[0][1] = -s
        T[1][0] = s
        T[1][1] = c
    else:
        T[0][0] = c
        T[0][1] = s
        T[1][0] = -s
        T[1][1] = c
    return T

def transform_point(T: Matrix3x3, point: Point, rep_type: int=2) -> Point:
    x, y = point
    P = [float(x), float(y), 1.0]
    result = [0.0, 0.0, 0.0]
    if rep_type == 1:
        for j in range(3):
            for k in range(3):
                result[j] += P[k] * T[k][j]
    else:
        for j in range(3):
            for k in range(3):
                result[j] += T[j][k] * P[k]
    w = result[2]
    if w != 1.0 and w != 0.0:
        return (result[0] / w, result[1] / w)
    return (result[0], result[1])

def transform_points(T: Matrix3x3, points: Points, rep_type: int=2) -> Points:
    return [transform_point(T, pt, rep_type) for pt in points]
apply_transformation = transform_points

def translate(points: Points, dx: float, dy: float, rep_type: int=2) -> Points:
    T = translation_matrix(dx, dy, rep_type)
    return transform_points(T, points, rep_type)

def scale(points: Points, sx: float, sy: Optional[float]=None, center_x: float=0.0, center_y: float=0.0, rep_type: int=2) -> Points:
    if sy is None:
        sy = sx
    if center_x == 0.0 and center_y == 0.0:
        S = scaling_matrix(sx, sy, rep_type)
        return transform_points(S, points, rep_type)
    t_to = translation_matrix(-center_x, -center_y, rep_type)
    s_mat = scaling_matrix(sx, sy, rep_type)
    t_back = translation_matrix(center_x, center_y, rep_type)
    if rep_type == 1:
        Comp = multiply_matrix(multiply_matrix(t_to, s_mat), t_back)
    else:
        Comp = multiply_matrix(multiply_matrix(t_back, s_mat), t_to)
    return transform_points(Comp, points, rep_type)

def rotate(points: Points, angle: float, center_x: float=0.0, center_y: float=0.0, is_deg: Optional[bool]=None, rep_type: int=2) -> Points:
    r_mat = rotation_matrix(angle, rep_type=rep_type, is_deg=is_deg)
    if center_x == 0.0 and center_y == 0.0:
        return transform_points(r_mat, points, rep_type)
    t_to = translation_matrix(-center_x, -center_y, rep_type)
    t_back = translation_matrix(center_x, center_y, rep_type)
    if rep_type == 1:
        Comp = multiply_matrix(multiply_matrix(t_to, r_mat), t_back)
    else:
        Comp = multiply_matrix(multiply_matrix(t_back, r_mat), t_to)
    return transform_points(Comp, points, rep_type)

def print_matrix(A: Matrix3x3):
    print()
    for i in range(3):
        row_str = ''
        for j in range(3):
            row_str += f'{A[i][j]:.4f}\t'
        print(row_str)

def print_points(points: Points):
    print('\nCoordinate Matrix\n')
    print('X\t\tY\t\t1')
    for x, y in points:
        print(f'{x:.4f}\t\t{y:.4f}\t\t1')

def build_composite(rep_type: int=2, input_func=input) -> Matrix3x3:
    Final = identity()
    print('\nEnter sequence (e.g. TSR, TRS, ST):')
    seq = input_func('Sequence: ').strip()
    if not seq:
        print('Empty sequence. Using identity matrix.')
        return Final
    step_num = 1
    for ch in seq:
        if ch in ('T', 't'):
            tx = float(input_func('Enter tx: '))
            ty = float(input_func('Enter ty: '))
            step_mat = translation_matrix(tx, ty, rep_type)
        elif ch in ('S', 's'):
            sx = float(input_func('Enter sx: '))
            sy = float(input_func('Enter sy: '))
            step_mat = scaling_matrix(sx, sy, rep_type)
        elif ch in ('R', 'r'):
            ang = float(input_func('Enter Angle (degrees): '))
            d_str = input_func('Direction (1=AntiCW, 2=CW): ').strip()
            if d_str == '2':
                ang = -ang
            step_mat = rotation_matrix(ang, rep_type=rep_type, is_deg=True)
        else:
            continue
        if rep_type == 1:
            Final = multiply_matrix(Final, step_mat)
        else:
            Final = multiply_matrix(step_mat, Final)
        step_num += 1
    return Final
try:
    from graphics import bresenham_line, bresenham_circle
except ImportError:
    try:
        from phase3.graphics import bresenham_line, bresenham_circle
    except ImportError:

        def bresenham_line(surface, x1, y1, x2, y2, color):
            x1, y1, x2, y2 = (int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)))
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            steep = dy > dx
            if steep:
                x1, y1 = (y1, x1)
                x2, y2 = (y2, x2)
                dx, dy = (dy, dx)
            if x1 > x2:
                x1, x2 = (x2, x1)
                y1, y2 = (y2, y1)
            P = 2 * dy - dx
            y_step = 1 if y1 < y2 else -1
            X, Y, Xend = (x1, y1, x2)

            def draw_pixel(cx, cy):
                if steep:
                    if 0 <= cy < surface.get_width() and 0 <= cx < surface.get_height():
                        surface.set_at((cy, cx), color)
                elif 0 <= cx < surface.get_width() and 0 <= cy < surface.get_height():
                    surface.set_at((cx, cy), color)
            draw_pixel(X, Y)
            while X < Xend:
                if P < 0:
                    X += 1
                    P += 2 * dy
                else:
                    X += 1
                    Y += y_step
                    P += 2 * dy - 2 * dx
                draw_pixel(X, Y)

        def bresenham_circle(surface, xc, yc, r, color):
            xc, yc, r = (int(round(xc)), int(round(yc)), int(round(r)))
            if r <= 0:
                if 0 <= xc < surface.get_width() and 0 <= yc < surface.get_height():
                    surface.set_at((xc, yc), color)
                return
            x, y = (0, r)
            d = 2 * (1 - r)

            def set_pixel(px, py):
                if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                    surface.set_at((px, py), color)

            def plot_octants(cx, cy, px, py):
                set_pixel(cx + px, cy + py)
                set_pixel(cx - px, cy + py)
                set_pixel(cx + px, cy - py)
                set_pixel(cx - px, cy - py)
                set_pixel(cx + py, cy + px)
                set_pixel(cx - py, cy + px)
                set_pixel(cx + py, cy - px)
                set_pixel(cx - py, cy - px)
            plot_octants(xc, yc, x, y)
            while y >= x:
                x += 1
                if d > 0:
                    y -= 1
                    d += 2 * (x - y) + 5
                else:
                    d += 2 * x + 3
                plot_octants(xc, yc, x, y)

def draw_dashed_line(surface, x1, y1, x2, y2, color, dash_len=5, gap_len=4):
    x1, y1, x2, y2 = (int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)))
    dist = math.hypot(x2 - x1, y2 - y1)
    if dist < 1.0:
        return
    dx = (x2 - x1) / dist
    dy = (y2 - y1) / dist
    curr_dist = 0.0
    drawing = True
    seg_step = 0.0
    while curr_dist < dist:
        px = int(round(x1 + dx * curr_dist))
        py = int(round(y1 + dy * curr_dist))
        if drawing:
            if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
                surface.set_at((px, py), color)
        seg_step += 1.0
        curr_dist += 1.0
        if drawing and seg_step >= dash_len:
            drawing = False
            seg_step = 0.0
        elif not drawing and seg_step >= gap_len:
            drawing = True
            seg_step = 0.0

def run_interactive_tsr_demo(screen=None, clock=None, standalone=True):
    import pygame
    import sys
    owns_pygame = False
    if screen is None:
        pygame.init()
        screen = pygame.display.set_mode((1060, 740))
        pygame.display.set_caption('Hunter Assassin — Phase 3: 2D Transformation Visualizer (TSR & Composite)')
        clock = pygame.time.Clock()
        owns_pygame = True
    COLOR_BG = (11, 15, 25)
    COLOR_GRID = (22, 30, 46)
    COLOR_AXIS = (45, 62, 90)
    COLOR_ORIGINAL = (255, 255, 255)
    COLOR_TRANS = (0, 240, 255)
    COLOR_VECTOR = (255, 160, 40)
    COLOR_HUD_BG = (16, 22, 36)
    COLOR_HUD_LINE = (36, 52, 80)
    COLOR_TEXT = (220, 225, 235)
    COLOR_DIM = (125, 140, 165)
    COLOR_YELLOW = (255, 215, 0)
    COLOR_GREEN = (60, 220, 120)
    COLOR_MODAL_BG = (18, 26, 42)
    COLOR_MODAL_BORDER = (0, 240, 255)
    font_title = pygame.font.SysFont('Consolas', 14, bold=True)
    font_body = pygame.font.SysFont('Consolas', 12)
    font_bold = pygame.font.SysFont('Consolas', 12, bold=True)
    font_small = pygame.font.SysFont('Consolas', 11)
    font_btn = pygame.font.SysFont('Consolas', 11, bold=True)
    font_dialog = pygame.font.SysFont('Consolas', 13, bold=True)
    PRESETS = [('Triangle', [(220.0, 220.0), (460.0, 220.0), (340.0, 420.0)]), ('Quad / Box', [(220.0, 220.0), (440.0, 220.0), (440.0, 380.0), (220.0, 380.0)]), ('House Pentagon', [(240.0, 380.0), (420.0, 380.0), (420.0, 260.0), (330.0, 180.0), (240.0, 260.0)]), ('Diamond', [(330.0, 180.0), (450.0, 300.0), (330.0, 420.0), (210.0, 300.0)])]
    preset_idx = 0
    original_points = list(PRESETS[preset_idx][1])
    transformed_points = list(original_points)
    rep_type = 2
    current_matrix = identity()
    current_op_label = 'IDENTITY (Initial State)'

    def get_centroid(pts):
        if not pts:
            return (0.0, 0.0)
        return (sum((p[0] for p in pts)) / len(pts), sum((p[1] for p in pts)) / len(pts))

    def print_transformation_summary(title, mat, orig_pts, trans_pts, rep):
        rep_str = "Row Matrix [P' = P * T]" if rep == 1 else "Column Matrix [P' = T * P]"
        print('\n' + '=' * 65)
        print(f'  {title.upper()}  [{rep_str}]')
        print('=' * 65)
        print('3x3 Homogeneous Transformation Matrix:')
        print_matrix(mat)
        print('\nTransformed Coordinates:')
        print("Point\tOriginal (X, Y)\t\tTransformed (X', Y')")
        print('-' * 55)
        for i, (op, tp) in enumerate(zip(orig_pts, trans_pts)):
            print(f'P{i + 1}\t({op[0]:>7.2f}, {op[1]:>7.2f})\t->\t({tp[0]:>7.2f}, {tp[1]:>7.2f})')
        print('-' * 55 + '\n')
    print('\n' + '=' * 70)
    print('      COMPUTER GRAPHICS — PHASE 3: 2D TRANSFORMATION ENGINE')
    print('=' * 70)
    print('Visualizer Running at 60 FPS in GUI Window.')
    print('Use On-Screen Buttons or Keyboard Shortcuts:')
    print('  [T] Translate   [S] Scale   [R] Rotate   [C] Composite (TSR)')
    print('  [Space] Reset   [P] Cycle Preset   [M] Toggle Row/Col Matrix')
    print('  [N] Custom Points   [Esc] Exit')
    print('-' * 70)
    print_transformation_summary('Initial State', current_matrix, original_points, transformed_points, rep_type)
    modal = None

    def open_modal(modal_type):
        nonlocal modal
        if modal_type == 'translate':
            modal = {'type': 'translate', 'title': 'TRANSLATION (T)', 'fields': [{'label': 'tx (X displacement):', 'val': '60.0'}, {'label': 'ty (Y displacement):', 'val': '40.0'}], 'active_field': 0}
        elif modal_type == 'scale':
            modal = {'type': 'scale', 'title': 'SCALING (S)', 'fields': [{'label': 'sx (X factor):', 'val': '1.5'}, {'label': 'sy (Y factor):', 'val': '1.5'}, {'label': 'Pivot (1=Centroid, 2=Origin):', 'val': '1'}], 'active_field': 0}
        elif modal_type == 'rotate':
            modal = {'type': 'rotate', 'title': 'ROTATION (R)', 'fields': [{'label': 'Angle (degrees):', 'val': '45.0'}, {'label': 'Direction (1=AntiCW, 2=Clockwise):', 'val': '1'}, {'label': 'Pivot (1=Centroid, 2=Origin):', 'val': '1'}], 'active_field': 0}
        elif modal_type == 'composite':
            modal = {'type': 'composite', 'title': 'COMPOSITE TRANSFORMATION (TSR)', 'fields': [{'label': 'Sequence (e.g. TSR, TRS, ST):', 'val': 'TSR'}, {'label': 'tx, ty (Translation):', 'val': '50.0 30.0'}, {'label': 'sx, sy (Scaling):', 'val': '1.2 1.2'}, {'label': 'Angle (deg) & Dir (1=CCW,2=CW):', 'val': '30.0 1'}], 'active_field': 0}
        elif modal_type == 'custom_pts':
            modal = {'type': 'custom_pts', 'title': 'CUSTOM POLYGON VERTICES', 'fields': [{'label': 'Enter points (x1 y1, x2 y2, ...):', 'val': '200 200, 450 200, 325 400'}], 'active_field': 0}

    def apply_modal():
        nonlocal modal, current_matrix, transformed_points, current_op_label, original_points
        if not modal:
            return
        mtype = modal['type']
        fields = modal['fields']
        try:
            if mtype == 'translate':
                tx = float(fields[0]['val']) if fields[0]['val'] else 50.0
                ty = float(fields[1]['val']) if fields[1]['val'] else 30.0
                T = translation_matrix(tx, ty, rep_type)
                current_matrix = T
                current_op_label = f'Translation (tx={tx:.1f}, ty={ty:.1f})'
                transformed_points = apply_transformation(T, original_points, rep_type)
                print_transformation_summary(current_op_label, current_matrix, original_points, transformed_points, rep_type)
            elif mtype == 'scale':
                sx = float(fields[0]['val']) if fields[0]['val'] else 1.2
                sy = float(fields[1]['val']) if fields[1]['val'] else 1.2
                pivot_choice = fields[2]['val'].strip()
                use_centroid = pivot_choice != '2'
                S = scaling_matrix(sx, sy)
                if use_centroid:
                    cx, cy = get_centroid(original_points)
                    T_to = translation_matrix(-cx, -cy, rep_type)
                    T_back = translation_matrix(cx, cy, rep_type)
                    if rep_type == 1:
                        Comp = multiply_matrix(T_to, S)
                        current_matrix = multiply_matrix(Comp, T_back)
                    else:
                        Comp = multiply_matrix(S, T_to)
                        current_matrix = multiply_matrix(T_back, Comp)
                    current_op_label = f'Scale about Centroid (sx={sx:.2f}, sy={sy:.2f})'
                else:
                    current_matrix = S
                    current_op_label = f'Scale about Origin (sx={sx:.2f}, sy={sy:.2f})'
                transformed_points = apply_transformation(current_matrix, original_points, rep_type)
                print_transformation_summary(current_op_label, current_matrix, original_points, transformed_points, rep_type)
            elif mtype == 'rotate':
                ang = float(fields[0]['val']) if fields[0]['val'] else 45.0
                dir_c = fields[1]['val'].strip()
                if dir_c == '2':
                    ang = -ang
                pivot_choice = fields[2]['val'].strip()
                use_centroid = pivot_choice != '2'
                R = rotation_matrix(ang, rep_type)
                dir_label = 'CW' if dir_c == '2' else 'CCW'
                if use_centroid:
                    cx, cy = get_centroid(original_points)
                    T_to = translation_matrix(-cx, -cy, rep_type)
                    T_back = translation_matrix(cx, cy, rep_type)
                    if rep_type == 1:
                        Comp = multiply_matrix(T_to, R)
                        current_matrix = multiply_matrix(Comp, T_back)
                    else:
                        Comp = multiply_matrix(R, T_to)
                        current_matrix = multiply_matrix(T_back, Comp)
                    current_op_label = f'Rotate about Centroid ({dir_label} {abs(ang):.1f}°)'
                else:
                    current_matrix = R
                    current_op_label = f'Rotate about Origin ({dir_label} {abs(ang):.1f}°)'
                transformed_points = apply_transformation(current_matrix, original_points, rep_type)
                print_transformation_summary(current_op_label, current_matrix, original_points, transformed_points, rep_type)
            elif mtype == 'composite':
                seq = fields[0]['val'].strip().upper() or 'TSR'
                t_parts = fields[1]['val'].replace(',', ' ').split()
                tx = float(t_parts[0]) if len(t_parts) > 0 else 50.0
                ty = float(t_parts[1]) if len(t_parts) > 1 else 30.0
                s_parts = fields[2]['val'].replace(',', ' ').split()
                sx = float(s_parts[0]) if len(s_parts) > 0 else 1.2
                sy = float(s_parts[1]) if len(s_parts) > 1 else 1.2
                r_parts = fields[3]['val'].replace(',', ' ').split()
                ang = float(r_parts[0]) if len(r_parts) > 0 else 30.0
                if len(r_parts) > 1 and r_parts[1] == '2':
                    ang = -ang
                Final = identity()
                for ch in seq:
                    if ch == 'T':
                        step_mat = translation_matrix(tx, ty, rep_type)
                    elif ch == 'S':
                        step_mat = scaling_matrix(sx, sy)
                    elif ch == 'R':
                        step_mat = rotation_matrix(ang, rep_type)
                    else:
                        continue
                    if rep_type == 1:
                        Final = multiply_matrix(Final, step_mat)
                    else:
                        Final = multiply_matrix(step_mat, Final)
                current_matrix = Final
                current_op_label = f'Composite Sequence [{seq}]'
                transformed_points = apply_transformation(current_matrix, original_points, rep_type)
                print_transformation_summary(f'Composite Transformation [{seq}]', current_matrix, original_points, transformed_points, rep_type)
            elif mtype == 'custom_pts':
                raw = fields[0]['val'].replace(',', ' ').split()
                pts = []
                for i in range(0, len(raw) - 1, 2):
                    try:
                        pts.append((float(raw[i]), float(raw[i + 1])))
                    except ValueError:
                        pass
                if len(pts) >= 2:
                    original_points = pts
                    transformed_points = list(original_points)
                    current_matrix = identity()
                    current_op_label = f'Custom Polygon ({len(pts)} vertices)'
                    print_transformation_summary('Custom Polygon Defined', current_matrix, original_points, transformed_points, rep_type)
        except Exception as e:
            print(f'Input Error: {e}')
        modal = None
    drag_vertex_idx = -1
    running = True
    while running:
        w, h = screen.get_size()
        mouse_pos = pygame.mouse.get_pos()
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
                    elif event.unicode and (event.unicode.isprintable() or event.unicode in ('-', '.', ' ')):
                        act = modal['active_field']
                        modal['fields'][act]['val'] += event.unicode
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_t, pygame.K_1):
                    open_modal('translate')
                elif event.key in (pygame.K_s, pygame.K_2):
                    open_modal('scale')
                elif event.key in (pygame.K_r, pygame.K_3):
                    open_modal('rotate')
                elif event.key in (pygame.K_c, pygame.K_4):
                    open_modal('composite')
                elif event.key in (pygame.K_SPACE, pygame.K_5):
                    current_matrix = identity()
                    transformed_points = list(original_points)
                    current_op_label = 'Reset to Original'
                    print_transformation_summary('Reset to Original', current_matrix, original_points, transformed_points, rep_type)
                elif event.key in (pygame.K_p, pygame.K_6):
                    preset_idx = (preset_idx + 1) % len(PRESETS)
                    original_points = list(PRESETS[preset_idx][1])
                    transformed_points = list(original_points)
                    current_matrix = identity()
                    current_op_label = f'Preset: {PRESETS[preset_idx][0]}'
                    print_transformation_summary(f'Preset Loaded: {PRESETS[preset_idx][0]}', current_matrix, original_points, transformed_points, rep_type)
                elif event.key in (pygame.K_m, pygame.K_7):
                    rep_type = 1 if rep_type == 2 else 2
                    transformed_points = apply_transformation(current_matrix, original_points, rep_type)
                    rep_name = 'Row Matrix (P * T)' if rep_type == 1 else 'Column Matrix (T * P)'
                    print_transformation_summary(f'Switched to {rep_name}', current_matrix, original_points, transformed_points, rep_type)
                elif event.key in (pygame.K_n, pygame.K_8):
                    open_modal('custom_pts')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    if modal:
                        modal_w, modal_h = (480, 240 + len(modal['fields']) * 40)
                        modal_x, modal_y = ((w - modal_w) // 2, (h - modal_h) // 2)
                        apply_rect = pygame.Rect(modal_x + 40, modal_y + modal_h - 45, 180, 32)
                        cancel_rect = pygame.Rect(modal_x + 260, modal_y + modal_h - 45, 180, 32)
                        if apply_rect.collidepoint(mx, my):
                            apply_modal()
                        elif cancel_rect.collidepoint(mx, my):
                            modal = None
                        else:
                            fy = modal_y + 65
                            for f_i in range(len(modal['fields'])):
                                f_box = pygame.Rect(modal_x + 30, fy + 18, modal_w - 60, 26)
                                if f_box.collidepoint(mx, my):
                                    modal['active_field'] = f_i
                                    break
                                fy += 50
                    else:
                        for i, (ox, oy) in enumerate(original_points):
                            if math.hypot(ox - mx, oy - my) <= 12:
                                drag_vertex_idx = i
                                break
                        if drag_vertex_idx == -1 and my >= h - 60:
                            btn_w = (w - 30) // 8
                            btn_idx = (mx - 15) // btn_w
                            if 0 <= btn_idx < 8:
                                if btn_idx == 0:
                                    open_modal('translate')
                                elif btn_idx == 1:
                                    open_modal('scale')
                                elif btn_idx == 2:
                                    open_modal('rotate')
                                elif btn_idx == 3:
                                    open_modal('composite')
                                elif btn_idx == 4:
                                    current_matrix = identity()
                                    transformed_points = list(original_points)
                                    current_op_label = 'Reset to Original'
                                    print_transformation_summary('Reset to Original', current_matrix, original_points, transformed_points, rep_type)
                                elif btn_idx == 5:
                                    preset_idx = (preset_idx + 1) % len(PRESETS)
                                    original_points = list(PRESETS[preset_idx][1])
                                    transformed_points = list(original_points)
                                    current_matrix = identity()
                                    current_op_label = f'Preset: {PRESETS[preset_idx][0]}'
                                    print_transformation_summary(f'Preset Loaded: {PRESETS[preset_idx][0]}', current_matrix, original_points, transformed_points, rep_type)
                                elif btn_idx == 6:
                                    rep_type = 1 if rep_type == 2 else 2
                                    transformed_points = apply_transformation(current_matrix, original_points, rep_type)
                                    rep_name = 'Row Matrix (P * T)' if rep_type == 1 else 'Column Matrix (T * P)'
                                    print_transformation_summary(f'Switched to {rep_name}', current_matrix, original_points, transformed_points, rep_type)
                                elif btn_idx == 7:
                                    open_modal('custom_pts')
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drag_vertex_idx = -1
            elif event.type == pygame.MOUSEMOTION:
                if drag_vertex_idx != -1 and (not modal):
                    mx, my = event.pos
                    mx = max(80, min(w - 360, mx))
                    my = max(70, min(h - 80, my))
                    original_points[drag_vertex_idx] = (float(mx), float(my))
                    transformed_points = apply_transformation(current_matrix, original_points, rep_type)
        screen.fill(COLOR_BG)
        for gx in range(0, w - 340, 40):
            pygame.draw.line(screen, COLOR_GRID, (gx, 0), (gx, h - 60), 1)
        for gy in range(0, h - 60, 40):
            pygame.draw.line(screen, COLOR_GRID, (0, gy), (w - 340, gy), 1)
        origin_x, origin_y = (60, 50)
        pygame.draw.line(screen, COLOR_AXIS, (origin_x, origin_y), (w - 340, origin_y), 2)
        pygame.draw.line(screen, COLOR_AXIS, (origin_x, origin_y), (origin_x, h - 70), 2)
        for tx in range(100, w - 340, 100):
            pygame.draw.line(screen, COLOR_AXIS, (tx, origin_y - 4), (tx, origin_y + 4), 1)
            tick_txt = font_small.render(str(tx), True, COLOR_DIM)
            screen.blit(tick_txt, (tx - 10, origin_y - 18))
        for ty in range(100, h - 70, 100):
            pygame.draw.line(screen, COLOR_AXIS, (origin_x - 4, ty), (origin_x + 4, ty), 1)
            tick_txt = font_small.render(str(ty), True, COLOR_DIM)
            screen.blit(tick_txt, (origin_x - 28, ty - 6))
        num_pts = len(original_points)
        for i in range(num_pts):
            ox, oy = original_points[i]
            tx, ty = transformed_points[i]
            draw_dashed_line(screen, ox, oy, tx, ty, COLOR_VECTOR)
        for i in range(num_pts):
            p1 = original_points[i]
            p2 = original_points[(i + 1) % num_pts]
            bresenham_line(screen, p1[0], p1[1], p2[0], p2[1], COLOR_ORIGINAL)
            bresenham_circle(screen, p1[0], p1[1], 4, COLOR_ORIGINAL)
            lbl = font_bold.render(f'P{i + 1}', True, COLOR_ORIGINAL)
            screen.blit(lbl, (p1[0] + 6, p1[1] - 16))
        for i in range(num_pts):
            p1 = transformed_points[i]
            p2 = transformed_points[(i + 1) % num_pts]
            bresenham_line(screen, p1[0], p1[1], p2[0], p2[1], COLOR_TRANS)
            bresenham_circle(screen, p1[0], p1[1], 5, COLOR_TRANS)
            lbl = font_bold.render(f"P{i + 1}'", True, COLOR_TRANS)
            screen.blit(lbl, (p1[0] + 8, p1[1] + 4))
        cx, cy = get_centroid(original_points)
        bresenham_circle(screen, cx, cy, 3, COLOR_YELLOW)
        c_lbl = font_small.render('C (Centroid)', True, COLOR_YELLOW)
        screen.blit(c_lbl, (cx + 6, cy - 6))
        header_rect = pygame.Rect(0, 0, w, 42)
        pygame.draw.rect(screen, (15, 20, 32), header_rect)
        pygame.draw.line(screen, COLOR_HUD_LINE, (0, 42), (w, 42), 2)
        t_lbl = font_title.render('PHASE 3: 2D TRANSFORMATION VISUALIZER (TSR & COMPOSITE)', True, COLOR_ORIGINAL)
        screen.blit(t_lbl, (15, 12))
        rep_str = 'Row Matrix [P * T]' if rep_type == 1 else 'Column Matrix [T * P]'
        r_lbl = font_bold.render(f'MODE: {rep_str}', True, COLOR_TRANS)
        screen.blit(r_lbl, (w - 290, 12))
        card_w = 330
        card_x = w - card_w - 10
        card_rect = pygame.Rect(card_x, 50, card_w, h - 120)
        pygame.draw.rect(screen, COLOR_HUD_BG, card_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_HUD_LINE, card_rect, width=1, border_radius=6)
        c_title = font_bold.render('3x3 HOMOGENEOUS MATRIX', True, COLOR_YELLOW)
        screen.blit(c_title, (card_x + 14, 62))
        op_txt = font_small.render(f'OP: {current_op_label}', True, COLOR_ORIGINAL)
        screen.blit(op_txt, (card_x + 14, 84))
        my = 110
        for row in range(3):
            r_str = f'│ {current_matrix[row][0]:>8.4f}  {current_matrix[row][1]:>8.4f}  {current_matrix[row][2]:>8.4f} │'
            m_rendered = font_body.render(r_str, True, COLOR_TRANS)
            screen.blit(m_rendered, (card_x + 14, my))
            my += 20
        pygame.draw.line(screen, COLOR_HUD_LINE, (card_x + 10, my + 8), (card_x + card_w - 10, my + 8), 1)
        cy_pos = my + 18
        c_head = font_bold.render("Pt   Original (X, Y)    Transformed (X', Y')", True, COLOR_YELLOW)
        screen.blit(c_head, (card_x + 10, cy_pos))
        cy_pos += 22
        for i in range(min(num_pts, 8)):
            ox, oy = original_points[i]
            tx, ty = transformed_points[i]
            pt_line = f'P{i + 1:<2}  ({ox:>5.1f}, {oy:>5.1f})   ->   ({tx:>5.1f}, {ty:>5.1f})'
            line_rendered = font_small.render(pt_line, True, COLOR_TEXT)
            screen.blit(line_rendered, (card_x + 10, cy_pos))
            cy_pos += 18
        hint_y = card_rect.bottom - 95
        pygame.draw.line(screen, COLOR_HUD_LINE, (card_x + 10, hint_y), (card_x + card_w - 10, hint_y), 1)
        h1 = font_small.render('Tip: Click & Drag original vertex P1-Pn', True, COLOR_GREEN)
        h2 = font_small.render('     to reshape polygon interactively!', True, COLOR_GREEN)
        h3 = font_small.render('Tip: Press T, S, R, C, Space, M, P, N', True, COLOR_DIM)
        screen.blit(h1, (card_x + 10, hint_y + 10))
        screen.blit(h2, (card_x + 10, hint_y + 26))
        screen.blit(h3, (card_x + 10, hint_y + 44))
        bar_rect = pygame.Rect(0, h - 56, w, 56)
        pygame.draw.rect(screen, (15, 20, 32), bar_rect)
        pygame.draw.line(screen, COLOR_HUD_LINE, (0, h - 56), (w, h - 56), 2)
        buttons = [('1: Translate [T]', 'translate'), ('2: Scale [S]', 'scale'), ('3: Rotate [R]', 'rotate'), ('4: Composite [C]', 'composite'), ('5: Reset [Spc]', 'reset'), ('6: Shape [P]', 'preset'), ('7: Rep [M]', 'rep'), ('8: Custom [N]', 'custom')]
        btn_w = (w - 30) // len(buttons)
        for i, (b_label, b_act) in enumerate(buttons):
            bx = 15 + i * btn_w
            b_box = pygame.Rect(bx + 2, h - 48, btn_w - 4, 38)
            is_hover = b_box.collidepoint(mouse_pos)
            btn_bg = (28, 40, 62) if is_hover else (20, 28, 44)
            btn_edge = COLOR_TRANS if is_hover else COLOR_HUD_LINE
            btn_col = COLOR_TRANS if is_hover else COLOR_TEXT
            pygame.draw.rect(screen, btn_bg, b_box, border_radius=4)
            pygame.draw.rect(screen, btn_edge, b_box, width=1, border_radius=4)
            txt = font_btn.render(b_label, True, btn_col)
            tw, th = txt.get_size()
            screen.blit(txt, (b_box.centerx - tw // 2, b_box.centery - th // 2))
        if modal:
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            modal_w = 480
            modal_h = 160 + len(modal['fields']) * 50
            modal_x = (w - modal_w) // 2
            modal_y = (h - modal_h) // 2
            m_box = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
            pygame.draw.rect(screen, COLOR_MODAL_BG, m_box, border_radius=8)
            pygame.draw.rect(screen, COLOR_MODAL_BORDER, m_box, width=2, border_radius=8)
            t_surf = font_dialog.render(modal['title'], True, COLOR_YELLOW)
            screen.blit(t_surf, (modal_x + 20, modal_y + 16))
            pygame.draw.line(screen, COLOR_HUD_LINE, (modal_x + 15, modal_y + 44), (modal_x + modal_w - 15, modal_y + 44), 1)
            fy = modal_y + 58
            for f_i, field in enumerate(modal['fields']):
                f_lbl = font_body.render(field['label'], True, COLOR_TEXT)
                screen.blit(f_lbl, (modal_x + 25, fy))
                input_box = pygame.Rect(modal_x + 25, fy + 20, modal_w - 50, 26)
                is_focused = modal['active_field'] == f_i
                ib_bg = (12, 18, 30) if is_focused else (18, 26, 40)
                ib_border = COLOR_TRANS if is_focused else COLOR_HUD_LINE
                pygame.draw.rect(screen, ib_bg, input_box, border_radius=3)
                pygame.draw.rect(screen, ib_border, input_box, width=1, border_radius=3)
                val_surf = font_body.render(field['val'], True, COLOR_ORIGINAL)
                screen.blit(val_surf, (input_box.x + 8, input_box.y + 5))
                if is_focused and pygame.time.get_ticks() // 500 % 2 == 0:
                    cursor_x = input_box.x + 8 + val_surf.get_width() + 2
                    pygame.draw.line(screen, COLOR_TRANS, (cursor_x, input_box.y + 4), (cursor_x, input_box.y + 22), 2)
                fy += 50
            apply_rect = pygame.Rect(modal_x + 35, modal_y + modal_h - 45, 190, 32)
            cancel_rect = pygame.Rect(modal_x + 255, modal_y + modal_h - 45, 190, 32)
            is_app_hover = apply_rect.collidepoint(mouse_pos)
            is_can_hover = cancel_rect.collidepoint(mouse_pos)
            pygame.draw.rect(screen, (0, 160, 200) if is_app_hover else (0, 110, 150), apply_rect, border_radius=4)
            pygame.draw.rect(screen, (50, 60, 80) if is_can_hover else (35, 45, 60), cancel_rect, border_radius=4)
            app_txt = font_btn.render('Apply [Enter]', True, COLOR_ORIGINAL)
            can_txt = font_btn.render('Cancel [Esc]', True, COLOR_DIM)
            screen.blit(app_txt, (apply_rect.centerx - app_txt.get_width() // 2, apply_rect.centery - app_txt.get_height() // 2))
            screen.blit(can_txt, (cancel_rect.centerx - can_txt.get_width() // 2, cancel_rect.centery - can_txt.get_height() // 2))
        pygame.display.flip()
        clock.tick(60)
    if owns_pygame:
        pygame.quit()
    return rep_type
if __name__ == '__main__':
    run_interactive_tsr_demo()
