import math


# ============================================================
# BRESENHAM'S LINE DRAWING ALGORITHM
# ============================================================

def bresenham_line(surface, x1, y1, x2, y2, color):
    """
    Bresenham's Line Drawing Algorithm.
    Identical implementation carried forward from Phase 1 & 2.
    """
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    
    steep = dy > dx
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dx, dy = dy, dx
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        
    P = 2 * dy - dx
    y_step = 1 if y1 < y2 else -1
    X = x1
    Y = y1
    Xend = x2
    
    def draw_pixel(curr_x, curr_y):
        if steep:
            if 0 <= curr_y < surface.get_width() and 0 <= curr_x < surface.get_height():
                surface.set_at((curr_y, curr_x), color)
        else:
            if 0 <= curr_x < surface.get_width() and 0 <= curr_y < surface.get_height():
                surface.set_at((curr_x, curr_y), color)
                
    draw_pixel(X, Y)
    while X < Xend:
        if P < 0:
            X += 1
            P = P + 2 * dy
        else:
            X += 1
            Y += y_step
            P = P + 2 * dy - 2 * dx
        draw_pixel(X, Y)


# ============================================================
# DDA LINE DRAWING ALGORITHM
# ============================================================

def dda_line(surface, x1, y1, x2, y2, color):
    """
    Digital Differential Analyzer (DDA) Line Algorithm.
    Carried forward from Phase 2.
    """
    x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
    
    delx = x2 - x1
    dely = y2 - y1
    
    lngt = max(abs(delx), abs(dely))
    
    # Safety check to prevent dividing by zero if the line is just a single dot!
    if lngt == 0:
        if 0 <= int(x1) < surface.get_width() and 0 <= int(y1) < surface.get_height():
            surface.set_at((int(x1), int(y1)), color)
        return

    x_incrmnt = delx / lngt
    y_incrmnt = dely / lngt
    
    x = x1
    y = y1

    for _ in range(int(lngt) + 1):
        ix, iy = int(round(x)), int(round(y))
        
        # Pygame requires checking if we are drawing outside the window screen
        if 0 <= ix < surface.get_width() and 0 <= iy < surface.get_height():
            surface.set_at((ix, iy), color)
            
        x += x_incrmnt
        y += y_incrmnt


# ============================================================
# BRESENHAM'S MIDPOINT CIRCLE ALGORITHM
# ============================================================

def bresenham_circle(surface, xc, yc, r, color):
    """
    Bresenham's / Midpoint Circle Algorithm.
    Uses 8-way symmetry. Carried forward from Phase 2.
    """

    xc = int(xc)
    yc = int(yc)
    r  = int(r)

    x = 0
    y = r
    d = 2*(1-r)


    # --------------------------------------------------------
    # HELPER: SET PIXEL SAFELY
    # --------------------------------------------------------

    def set_pixel(px, py):
        if (
            0 <= px < surface.get_width()
            and 0 <= py < surface.get_height()
        ):
            surface.set_at((px, py), color)


    # --------------------------------------------------------
    # HELPER: PLOT ALL 8 OCTANTS
    # --------------------------------------------------------

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
            d = d + 2 * (x - y) + 5
        else:
            d = d + 2 * x + 3

        plot_octants(xc, yc, x, y)
