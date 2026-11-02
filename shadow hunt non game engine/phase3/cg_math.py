import math
from typing import List, Tuple, Union
Point = Tuple[float, float]
Points = List[Point]
Matrix3x3 = List[List[float]]
try:
    from transforms import identity_matrix, matmul_3x3, transform_point, transform_points, translation_matrix, scaling_matrix, rotation_matrix, translate, scale, rotate
except ImportError:
    from phase3.transforms import identity_matrix, matmul_3x3, transform_point, transform_points, translation_matrix, scaling_matrix, rotation_matrix, translate, scale, rotate

class CGMath:
    identity_matrix = staticmethod(identity_matrix)
    matmul_3x3 = staticmethod(matmul_3x3)
    transform_point = staticmethod(transform_point)
    transform_points = staticmethod(transform_points)
    translation_matrix = staticmethod(translation_matrix)
    scaling_matrix = staticmethod(scaling_matrix)
    rotation_matrix = staticmethod(rotation_matrix)
    translate = staticmethod(translate)
    scale = staticmethod(scale)
    rotate = staticmethod(rotate)

    @staticmethod
    def bresenham_line(x1: int, y1: int, x2: int, y2: int) -> List[Tuple[int, int]]:
        points = []
        dx, dy = (abs(x2 - x1), abs(y2 - y1))
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return points

    @staticmethod
    def bresenham_circle(xc: float, yc: float, r: float) -> List[Tuple[int, int]]:
        radius, cx, cy = (int(round(r)), int(round(xc)), int(round(yc)))
        if radius <= 0:
            return [(cx, cy)]
        x, y = (0, radius)
        d = 1 - 2 * radius
        circle_points = set()

        def add_octant_points(px, py):
            circle_points.update([(cx + px, cy + py), (cx - px, cy + py), (cx + px, cy - py), (cx - px, cy - py), (cx + py, cy + px), (cx - py, cy + px), (cx + py, cy - px), (cx - py, cy - px)])
        while x <= y:
            add_octant_points(x, y)
            if d < 0:
                d += 2 * x + 3
                x += 1
            else:
                d += 2 * (x - y) + 5
                x += 1
                y -= 1
        return sorted(list(circle_points))

    @staticmethod
    def point_in_polygon(x: float, y: float, polygon_points: Points) -> bool:
        n = len(polygon_points)
        if n < 3:
            return False
        inside = False
        p1x, p1y = polygon_points[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon_points[i % n]
            if min(p1y, p2y) < y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    x_inters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x if p1y != p2y else p1x
                    if p1x == p2x or x <= x_inters:
                        inside = not inside
            p1x, p1y = (p2x, p2y)
        return inside

    @staticmethod
    def distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def create_cone_polygon(origin_x: float, origin_y: float, facing_angle: float, fov_angle: float, length: float, num_arc_steps: int=12) -> Points:
        pts: Points = [(origin_x, origin_y)]
        start_ang = facing_angle - fov_angle / 2.0
        step_ang = fov_angle / float(num_arc_steps)
        for i in range(num_arc_steps + 1):
            curr_ang = start_ang + i * step_ang
            pts.append((origin_x + length * math.cos(curr_ang), origin_y + length * math.sin(curr_ang)))
        return pts
