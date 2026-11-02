#ifndef CG_MATH_H
#define CG_MATH_H

#include <vector>
#include <cmath>
#include "core_graphics.h"

struct Point {
    float x, y;
    Point(float _x = 0.0f, float _y = 0.0f) : x(_x), y(_y) {}
};

struct Matrix3x3 {
    float m[3][3];
    Matrix3x3() {
        for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++)
                m[i][j] = (i == j) ? 1.0f : 0.0f;
    }
};

class CGMath {
public:
    static Matrix3x3 identity_matrix();
    static Matrix3x3 matmul_3x3(const Matrix3x3& a, const Matrix3x3& b);
    static Point transform_point(const Matrix3x3& matrix, const Point& point);
    static std::vector<Point> transform_points(const Matrix3x3& matrix, const std::vector<Point>& points);

    static Matrix3x3 translation_matrix(float dx, float dy);
    static std::vector<Point> translate(const std::vector<Point>& points, float dx, float dy);

    static Matrix3x3 rotation_matrix(float angle_rad);
    static std::vector<Point> rotate(const std::vector<Point>& points, float angle_rad, float center_x, float center_y);

    static Matrix3x3 scaling_matrix(float sx, float sy);
    static std::vector<Point> scale(const std::vector<Point>& points, float scale_factor, float center_x, float center_y);

    static float distance(float x1, float y1, float x2, float y2);

    static bool point_in_polygon(float px, float py, const std::vector<Point>& polygon);

    static std::vector<Point> create_cone_polygon(
        float origin_x, float origin_y,
        float facing_angle, float fov_angle,
        float length, int num_arc_steps = 12
    );

    static std::vector<ScreenPoint> toScreenPoints(const std::vector<Point>& pts);
};

#endif

