"""
Assignment 1 algorithms ONLY — ports of assign1.cpp (DDA) and assign1b.cpp (Bresenham).
No pygame.draw.* shortcuts. Pixels via surface.set_at (putpixel equivalent).
"""


def dda_line(surface, x1, y1, x2, y2, color):
    """DDA — same structure as assign1.cpp drawLineDDA."""
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    ey = abs(y1 - y2)
    ex = abs(x1 - x2)
    length = max(ey, ex)

    if length == 0:
        if 0 <= x1 < surface.get_width() and 0 <= y1 < surface.get_height():
            surface.set_at((x1, y1), color)
        return

    dx = ex / length
    dy = ey / length
    if x2 < x1:
        dx = -dx
    if y2 < y1:
        dy = -dy

    x, y = float(x1), float(y1)
    for _ in range(int(length) + 1):
        ix, iy = int(round(x)), int(round(y))
        if 0 <= ix < surface.get_width() and 0 <= iy < surface.get_height():
            surface.set_at((ix, iy), color)
        x += dx
        y += dy


def bresenham_line(surface, x1, y1, x2, y2, color):
    """
    Bresenham line — all octants (assignment game needs full coverage).
    Decision parameter form matches assign1b.cpp: P = 2*dy - dx style updates.
    """
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    x, y = x1, y1

    def put(px, py):
        if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
            surface.set_at((px, py), color)

    if dx >= dy:
        p = 2 * dy - dx
        for _ in range(dx + 1):
            put(x, y)
            if p < 0:
                p += 2 * dy
            else:
                y += sy
                p += 2 * dy - 2 * dx
            x += sx
    else:
        p = 2 * dx - dy
        for _ in range(dy + 1):
            put(x, y)
            if p < 0:
                p += 2 * dx
            else:
                x += sx
                p += 2 * dx - 2 * dy
            y += sy
