def bresenham_line(surface, x1, y1, x2, y2, color):
    x1, y1, x2, y2 = (int(x1), int(y1), int(x2), int(y2))
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
    X = x1
    Y = y1
    Xend = x2

    def draw_pixel(curr_x, curr_y):
        if steep:
            if 0 <= curr_y < surface.get_width() and 0 <= curr_x < surface.get_height():
                surface.set_at((curr_y, curr_x), color)
        elif 0 <= curr_x < surface.get_width() and 0 <= curr_y < surface.get_height():
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

def dda_line(surface, x1, y1, x2, y2, color):
    x1, y1, x2, y2 = (float(x1), float(y1), float(x2), float(y2))
    delx = x2 - x1
    dely = y2 - y1
    lngt = max(abs(delx), abs(dely))
    if lngt == 0:
        if 0 <= int(x1) < surface.get_width() and 0 <= int(y1) < surface.get_height():
            surface.set_at((int(x1), int(y1)), color)
        return
    x_incrmnt = delx / lngt
    y_incrmnt = dely / lngt
    x = x1
    y = y1
    for _ in range(int(lngt) + 1):
        ix, iy = (int(round(x)), int(round(y)))
        if 0 <= ix < surface.get_width() and 0 <= iy < surface.get_height():
            surface.set_at((ix, iy), color)
        x += x_incrmnt
        y += y_incrmnt

def midpoint_circle(surface, xc, yc, r, color):
    x1, y1, radius = (int(xc), int(yc), int(r))
    if radius <= 0:
        if 0 <= x1 < surface.get_width() and 0 <= y1 < surface.get_height():
            surface.set_at((x1, y1), color)
        return
    x = 0
    y = radius
    del_param = 2 * (1 - radius)

    def set_pixel(px, py):
        if 0 <= px < surface.get_width() and 0 <= py < surface.get_height():
            surface.set_at((px, py), color)

    def draw_symmetric_points(px, py):
        set_pixel(x1 + px, y1 + py)
        set_pixel(x1 - px, y1 + py)
        set_pixel(x1 + px, y1 - py)
        set_pixel(x1 - px, y1 - py)
        set_pixel(x1 + py, y1 + px)
        set_pixel(x1 - py, y1 + px)
        set_pixel(x1 + py, y1 - px)
        set_pixel(x1 - py, y1 - px)
    while x <= y:
        draw_symmetric_points(x, y)
        if del_param < 0:
            sig = 2 * del_param + 2 * y - 1
            if sig <= 0:
                x += 1
                del_param = del_param + 2 * x + 1
            else:
                x += 1
                y -= 1
                del_param = del_param + 2 * x - 2 * y + 2
        elif del_param > 0:
            sig1 = 2 * del_param - 2 * x - 1
            if sig1 > 0:
                y -= 1
                del_param = del_param - 2 * y + 1
            else:
                x += 1
                y -= 1
                del_param = del_param + 2 * x - 2 * y + 2
        else:
            x += 1
            y -= 1
            del_param = del_param + 2 * x - 2 * y + 2
bresenham_circle = midpoint_circle
