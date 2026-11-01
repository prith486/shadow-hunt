"""
Assignment 4 algorithms ONLY (Assignment 4.pdf / boundary fill):
- Bresenham drawLine for polygon outlines
- Even-odd isInsidePolygon
- Iterative 4-connected boundaryFillFrom

No Tkinter create_polygon/oval/rectangle fills — shapes are rasterized here.
"""

from __future__ import annotations

from collections import deque
from typing import List, Tuple, Optional

from PIL import Image, ImageTk

Point = Tuple[float, float]
Points = List[Point]
_EMPTY, _BOUNDARY, _FILL = 0, 1, 2

# Cache raster results for static environment obstacles (walls/crates) to maintain 60 FPS
_FILL_CACHE: dict = {}
_LINE_CACHE: dict = {}
_CACHE_LIMIT = 250


def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
    """Ass4 drawLine — Bresenham all octants."""
    pts: List[Tuple[int, int]] = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    x, y = x1, y1
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
    """Ass4 even-odd inside test to verify interior seed point."""
    n = len(xs)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = xs[i], ys[i]
        xj, yj = xs[j], ys[j]
        if (yi > py) != (yj > py):
            x_i = xi + (py - yi) * (xj - xi) / (yj - yi)
            if px < x_i:
                inside = not inside
        j = i
    return inside


def boundary_fill_from(grid, width: int, height: int, sx: int, sy: int) -> None:
    """
    Ass4 iterative 4-connected boundary fill.
    Pushes 4 neighbors: (px + 1, py), (px - 1, py), (px, py + 1), (px, py - 1)
    Matches assign4/boundaryFill.cpp.
    """
    if not (0 <= sx < width and 0 <= sy < height):
        return
    st = deque([(sx, sy)])
    while st:
        px, py = st.pop()
        if px < 0 or py < 0 or px >= width or py >= height:
            continue
        if grid[py][px] in (_BOUNDARY, _FILL):
            continue
        grid[py][px] = _FILL
        st.append((px + 1, py))
        st.append((px - 1, py))
        st.append((px, py + 1))
        st.append((px, py - 1))


def _hex_rgb(color: str) -> Tuple[int, int, int, int]:
    c = color.lstrip("#")
    if len(c) == 8:  # RRGGBBAA
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), int(c[6:8], 16)
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16), 255


def _quantize_verts(vertices: Points, step: int = 1) -> Tuple[Tuple[int, int], ...]:
    return tuple((int(round(v[0] / step) * step), int(round(v[1] / step) * step)) for v in vertices)


def _cache_put(cache: dict, key, value):
    if key in cache:
        cache[key] = value
        return
    if len(cache) >= _CACHE_LIMIT:
        for _ in range(max(1, _CACHE_LIMIT // 4)):
            cache.pop(next(iter(cache)), None)
    cache[key] = value


def rasterize_filled_polygon(
    vertices: Points,
    fill_color: str,
    boundary_color: str,
    pad: int = 1,
    bypass_cache: bool = False,
) -> Optional[Tuple[ImageTk.PhotoImage, int, int]]:
    if len(vertices) < 3:
        return None

    qverts = _quantize_verts(vertices, step=1)
    cache_key = (qverts, fill_color, boundary_color, pad)

    if not bypass_cache:
        hit = _FILL_CACHE.get(cache_key)
        if hit is not None:
            return hit

    xs_f = [v[0] for v in qverts]
    ys_f = [v[1] for v in qverts]
    ox = int(min(xs_f)) - pad
    oy = int(min(ys_f)) - pad
    w = int(max(xs_f)) - ox + 1 + pad
    h = int(max(ys_f)) - oy + 1 + pad
    if w <= 0 or h <= 0:
        return None

    xs = [int(v[0]) - ox for v in qverts]
    ys = [int(v[1]) - oy for v in qverts]
    n = len(xs)
    grid = [[_EMPTY] * w for _ in range(h)]

    # Draw boundary using Bresenham line algorithm
    for i in range(n):
        for px, py in bresenham_line(xs[i], ys[i], xs[(i + 1) % n], ys[(i + 1) % n]):
            if 0 <= px < w and 0 <= py < h:
                grid[py][px] = _BOUNDARY

    # Find interior seed point using Even-Odd inside polygon test
    seed_x = int(round(sum(xs) / n))
    seed_y = int(round(sum(ys) / n))
    if not is_inside_polygon(seed_x, seed_y, xs, ys):
        seed_x = seed_y = -1
        for py in range(h):
            for px in range(w):
                if grid[py][px] == _EMPTY and is_inside_polygon(px, py, xs, ys):
                    seed_x, seed_y = px, py
                    break
            if seed_x >= 0:
                break
    if seed_x < 0:
        return None

    # Execute 4-Connected Boundary Fill
    boundary_fill_from(grid, w, h, seed_x, seed_y)

    fr, fg, fb, fa = _hex_rgb(fill_color)
    br, bg, bb, ba = _hex_rgb(boundary_color)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pix = img.load()
    for py in range(h):
        row = grid[py]
        for px in range(w):
            cell = row[px]
            if cell == _FILL:
                pix[px, py] = (fr, fg, fb, fa)
            elif cell == _BOUNDARY:
                pix[px, py] = (br, bg, bb, ba)
    result = (ImageTk.PhotoImage(img), ox, oy)
    if not bypass_cache:
        _cache_put(_FILL_CACHE, cache_key, result)
    return result


def draw_filled_polygon(
    canvas, vertices: Points, fill: str, border: str, tags: str, keep: List, bypass_cache: bool = False
) -> bool:
    res = rasterize_filled_polygon(vertices, fill, border, bypass_cache=bypass_cache)
    if res is None:
        return False
    photo, ox, oy = res
    keep.append(photo)
    canvas.create_image(ox, oy, image=photo, anchor="nw", tags=tags)
    return True


def draw_bresenham_segment(canvas, x1, y1, x2, y2, color: str, tags: str, keep: List, width: int = 1) -> None:
    """Draw a line using Ass4 Bresenham only (no create_line)."""
    ix1, iy1 = int(round(x1)), int(round(y1))
    ix2, iy2 = int(round(x2)), int(round(y2))
    cache_key = (ix1, iy1, ix2, iy2, color, width)
    hit = _LINE_CACHE.get(cache_key)
    if hit is not None:
        photo, ox, oy = hit
        keep.append(photo)
        canvas.create_image(ox, oy, image=photo, anchor="nw", tags=tags)
        return

    pts = bresenham_line(ix1, iy1, ix2, iy2)
    if not pts:
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ox, oy = min(xs), min(ys)
    w, h = max(xs) - ox + 1, max(ys) - oy + 1
    r, g, b, a = _hex_rgb(color)
    img = Image.new("RGBA", (w + width, h + width), (0, 0, 0, 0))
    pix = img.load()
    for x, y in pts:
        for t in range(max(1, width)):
            px, py = x - ox + t // 2, y - oy + t // 2
            if 0 <= px < img.size[0] and 0 <= py < img.size[1]:
                pix[px, py] = (r, g, b, a)
    photo = ImageTk.PhotoImage(img)
    _cache_put(_LINE_CACHE, cache_key, (photo, ox, oy))
    keep.append(photo)
    canvas.create_image(ox, oy, image=photo, anchor="nw", tags=tags)
