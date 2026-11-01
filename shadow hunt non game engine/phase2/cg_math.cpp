#include "cg_math.h"
#include <algorithm>

Matrix3x3 CGMath::identity_matrix() {
    Matrix3x3 id;
    return id;
}

Matrix3x3 CGMath::matmul_3x3(const Matrix3x3& a, const Matrix3x3& b) {
    Matrix3x3 res;
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            res.m[i][j] = a.m[i][0] * b.m[0][j] +
                          a.m[i][1] * b.m[1][j] +
                          a.m[i][2] * b.m[2][j];
        }
    }
    return res;
}

Point CGMath::transform_point(const Matrix3x3& matrix, const Point& point) {
    float x = point.x;
    float y = point.y;
    float nx = matrix.m[0][0] * x + matrix.m[0][1] * y + matrix.m[0][2];
    float ny = matrix.m[1][0] * x + matrix.m[1][1] * y + matrix.m[1][2];
    float w  = matrix.m[2][0] * x + matrix.m[2][1] * y + matrix.m[2][2];
    if (w != 1.0f && w != 0.0f) {
        nx /= w;
        ny /= w;
    }
    return Point(nx, ny);
}

std::vector<Point> CGMath::transform_points(const Matrix3x3& matrix, const std::vector<Point>& points) {
    std::vector<Point> out;
    out.reserve(points.size());
    for (size_t i = 0; i < points.size(); i++) {
        out.push_back(transform_point(matrix, points[i]));
    }
    return out;
}

Matrix3x3 CGMath::translation_matrix(float dx, float dy) {
    Matrix3x3 t = identity_matrix();
    t.m[0][2] = dx;
    t.m[1][2] = dy;
    return t;
}

std::vector<Point> CGMath::translate(const std::vector<Point>& points, float dx, float dy) {
    return transform_points(translation_matrix(dx, dy), points);
}

Matrix3x3 CGMath::rotation_matrix(float angle_rad) {
    Matrix3x3 r = identity_matrix();
    float c = std::cos(angle_rad);
    float s = std::sin(angle_rad);
    r.m[0][0] = c;
    r.m[0][1] = -s;
    r.m[1][0] = s;
    r.m[1][1] = c;
    return r;
}

std::vector<Point> CGMath::rotate(const std::vector<Point>& points, float angle_rad, float center_x, float center_y) {
    Matrix3x3 t_to_orig = translation_matrix(-center_x, -center_y);
    Matrix3x3 r_mat     = rotation_matrix(angle_rad);
    Matrix3x3 t_back    = translation_matrix(center_x, center_y);
    Matrix3x3 comp      = matmul_3x3(matmul_3x3(t_back, r_mat), t_to_orig);
    return transform_points(comp, points);
}

Matrix3x3 CGMath::scaling_matrix(float sx, float sy) {
    Matrix3x3 s = identity_matrix();
    s.m[0][0] = sx;
    s.m[1][1] = sy;
    return s;
}

std::vector<Point> CGMath::scale(const std::vector<Point>& points, float scale_factor, float center_x, float center_y) {
    Matrix3x3 t_to_orig = translation_matrix(-center_x, -center_y);
    Matrix3x3 s_mat     = scaling_matrix(scale_factor, scale_factor);
    Matrix3x3 t_back    = translation_matrix(center_x, center_y);
    Matrix3x3 comp      = matmul_3x3(matmul_3x3(t_back, s_mat), t_to_orig);
    return transform_points(comp, points);
}

float CGMath::distance(float x1, float y1, float x2, float y2) {
    float dx = x2 - x1;
    float dy = y2 - y1;
    return std::sqrt(dx * dx + dy * dy);
}

bool CGMath::point_in_polygon(float px, float py, const std::vector<Point>& polygon) {
    size_t n = polygon.size();
    if (n < 3) return false;
    bool inside = false;
    float p1x = polygon[0].x;
    float p1y = polygon[0].y;

    for (size_t i = 1; i <= n; i++) {
        const Point& p2 = polygon[i % n];
        float p2x = p2.x;
        float p2y = p2.y;

        if (std::min(p1y, p2y) < py && py <= std::max(p1y, p2y)) {
            if (px <= std::max(p1x, p2x)) {
                float x_inters = p1x;
                if (p1y != p2y) {
                    x_inters = (py - p1y) * (p2x - p1x) / (p2y - p1y) + p1x;
                }
                if (p1x == p2x || px <= x_inters) {
                    inside = !inside;
                }
            }
        }
        p1x = p2x;
        p1y = p2y;
    }
    return inside;
}

std::vector<Point> CGMath::create_cone_polygon(
    float origin_x, float origin_y,
    float facing_angle, float fov_angle,
    float length, int num_arc_steps
) {
    std::vector<Point> pts;
    pts.push_back(Point(origin_x, origin_y));
    float start_ang = facing_angle - (fov_angle / 2.0f);
    float step_ang  = fov_angle / (float)num_arc_steps;

    for (int i = 0; i <= num_arc_steps; i++) {
        float curr_ang = start_ang + i * step_ang;
        pts.push_back(Point(
            origin_x + length * std::cos(curr_ang),
            origin_y + length * std::sin(curr_ang)
        ));
    }
    return pts;
}

std::vector<ScreenPoint> CGMath::toScreenPoints(const std::vector<Point>& pts) {
    std::vector<ScreenPoint> spts;
    spts.reserve(pts.size());
    for (size_t i = 0; i < pts.size(); i++) {
        spts.push_back(ScreenPoint(pts[i].x, pts[i].y));
    }
    return spts;
}
