import math
from typing import List, Tuple, Union
Point = Tuple[float, float]
Points = List[Point]
Matrix3x3 = List[List[float]]

class CGMath:

    @staticmethod
    def identity_matrix() -> Matrix3x3:
        return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

    @staticmethod
    def matmul_3x3(a: Matrix3x3, b: Matrix3x3) -> Matrix3x3:
        result = [[0.0, 0.0, 0.0] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                result[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j]
        return result

    @staticmethod
    def transform_point(matrix: Matrix3x3, point: Point) -> Point:
        x, y = point
        nx = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * 1.0
        ny = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * 1.0
        w = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * 1.0
        if w != 1.0 and w != 0.0:
            nx /= w
            ny /= w
        return (nx, ny)

    @staticmethod
    def transform_points(matrix: Matrix3x3, points: Points) -> Points:
        return [CGMath.transform_point(matrix, pt) for pt in points]

    @staticmethod
    def translation_matrix(dx: float, dy: float) -> Matrix3x3:
        return [[1.0, 0.0, float(dx)], [0.0, 1.0, float(dy)], [0.0, 0.0, 1.0]]

    @classmethod
    def translate(cls, points: Points, dx: float, dy: float) -> Points:
        t_mat = cls.translation_matrix(dx, dy)
        return cls.transform_points(t_mat, points)

    @staticmethod
    def rotation_matrix(angle_rad: float) -> Matrix3x3:
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]

    @classmethod
    def rotate(cls, points: Points, angle: float, center_x: float, center_y: float, in_degrees: bool=False) -> Points:
        angle_rad = math.radians(angle) if in_degrees else angle
        t_to_origin = cls.translation_matrix(-center_x, -center_y)
        r_mat = cls.rotation_matrix(angle_rad)
        t_back = cls.translation_matrix(center_x, center_y)
        m_composite = cls.matmul_3x3(cls.matmul_3x3(t_back, r_mat), t_to_origin)
        return cls.transform_points(m_composite, points)

    @staticmethod
    def scaling_matrix(sx: float, sy: float) -> Matrix3x3:
        return [[float(sx), 0.0, 0.0], [0.0, float(sy), 0.0], [0.0, 0.0, 1.0]]

    @classmethod
    def scale(cls, points: Points, scale_factor: Union[float, Tuple[float, float]], center_x: float, center_y: float) -> Points:
        if isinstance(scale_factor, (int, float)):
            sx = sy = float(scale_factor)
        else:
            sx, sy = (float(scale_factor[0]), float(scale_factor[1]))
        t_to_origin = cls.translation_matrix(-center_x, -center_y)
        s_mat = cls.scaling_matrix(sx, sy)
        t_back = cls.translation_matrix(center_x, center_y)
        m_composite = cls.matmul_3x3(cls.matmul_3x3(t_back, s_mat), t_to_origin)
        return cls.transform_points(m_composite, points)

    @staticmethod
    def bresenham_circle(xc: Union[int, float], yc: Union[int, float], r: Union[int, float]) -> List[Tuple[int, int]]:
        radius = int(round(r))
        cx = int(round(xc))
        cy = int(round(yc))
        if radius <= 0:
            return [(cx, cy)]
        x = 0
        y = radius
        d = 1 - 2 * radius
        circle_points = set()

        def add_octant_points(px: int, py: int):
            circle_points.add((cx + px, cy + py))
            circle_points.add((cx - px, cy + py))
            circle_points.add((cx + px, cy - py))
            circle_points.add((cx - px, cy - py))
            circle_points.add((cx + py, cy + px))
            circle_points.add((cx - py, cy + px))
            circle_points.add((cx + py, cy - px))
            circle_points.add((cx - py, cy - px))
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
                    if p1y != p2y:
                        x_inters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    else:
                        x_inters = p1x
                    if p1x == p2x or x <= x_inters:
                        inside = not inside
            p1x, p1y = (p2x, p2y)
        return inside

    @staticmethod
    def distance(x1: float, y1: float, x2: float, y2: float) -> float:
        return math.hypot(x2 - x1, y2 - y1)

    @staticmethod
    def flatten(points: Points) -> List[float]:
        flat = []
        for x, y in points:
            flat.extend([float(x), float(y)])
        return flat

    @staticmethod
    def create_cone_polygon(origin_x: float, origin_y: float, facing_angle: float, fov_angle: float, length: float, num_arc_steps: int=12) -> Points:
        pts: Points = [(origin_x, origin_y)]
        half_fov = fov_angle / 2.0
        start_ang = facing_angle - half_fov
        step_ang = fov_angle / float(num_arc_steps)
        for i in range(num_arc_steps + 1):
            curr_ang = start_ang + i * step_ang
            px = origin_x + length * math.cos(curr_ang)
            py = origin_y + length * math.sin(curr_ang)
            pts.append((px, py))
        return pts
if __name__ == '__main__':
    print('Running CGMath verification...')
    triangle = [(0, -10), (10, 10), (-10, 10)]
    t_res = CGMath.translate(triangle, 50, 100)
    assert t_res == [(50.0, 90.0), (60.0, 110.0), (40.0, 110.0)], f'Translation failed: {t_res}'
    print('[PASS] Translation')
    r_res = CGMath.rotate([(10, 0)], math.pi / 2, 0, 0)
    assert abs(r_res[0][0] - 0.0) < 1e-06 and abs(r_res[0][1] - 10.0) < 1e-06, f'Rotation failed: {r_res}'
    print('[PASS] Rotation')
    s_res = CGMath.scale([(15, 10)], 2.0, 10, 10)
    assert s_res == [(20.0, 10.0)], f'Scaling failed: {s_res}'
    print('[PASS] Scaling')
    circle_pts = CGMath.bresenham_circle(100, 100, 15)
    assert len(circle_pts) > 0, 'Bresenham circle generated no points'
    for cx, cy in circle_pts:
        dist = CGMath.distance(100, 100, cx, cy)
        assert 14.0 <= dist <= 16.0, f'Point out of expected radius bounds: ({cx}, {cy}) dist={dist}'
    print(f"[PASS] Bresenham's Circle (Generated {len(circle_pts)} raster boundary points, d0 = 1 - 2R)")
    cone = CGMath.create_cone_polygon(0, 0, 0.0, math.pi / 3, 100)
    assert CGMath.point_in_polygon(50, 0, cone) is True, 'Center of cone should be inside'
    assert CGMath.point_in_polygon(150, 0, cone) is False, 'Point beyond cone range should be outside'
    assert CGMath.point_in_polygon(50, 80, cone) is False, 'Point outside cone angle should be outside'
    print('[PASS] Point in Polygon')
    print('\nAll CGMath unit checks passed successfully!')
