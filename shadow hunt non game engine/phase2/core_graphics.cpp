#include "core_graphics.h"

// Safe putpixel with window viewport clipping
static inline void safePutPixel(int x, int y, int color) {
    if (x >= 0 && x < getmaxx() && y >= 0 && y < getmaxy()) {
        putpixel(x, y, color);
    }
}

// ============================================================================
// DDA LINE ALGORITHM — Exact port of assign1.cpp & graphics.py dda_line
// ============================================================================
void drawLineDDA(int x1, int y1, int x2, int y2, int color) {
    float delx = (float)(x2 - x1);
    float dely = (float)(y2 - y1);
    float lngt = std::max(std::abs(delx), std::abs(dely));

    if (lngt == 0.0f) {
        safePutPixel(x1, y1, color);
        return;
    }

    float x_inc = delx / lngt;
    float y_inc = dely / lngt;

    float x = (float)x1;
    float y = (float)y1;

    for (int i = 0; i <= (int)lngt; i++) {
        safePutPixel((int)std::round(x), (int)std::round(y), color);
        x += x_inc;
        y += y_inc;
    }
}

// ============================================================================
// BRESENHAM LINE ALGORITHM — Exact port of assign1b.cpp & graphics.py
// ============================================================================
void drawBresenhamLine(int x1, int y1, int x2, int y2, int color) {
    int dx = std::abs(x2 - x1);
    int dy = std::abs(y2 - y1);
    int sx = (x2 > x1) ? 1 : -1;
    int sy = (y2 > y1) ? 1 : -1;
    int x = x1;
    int y = y1;

    if (dx >= dy) {
        int p = 2 * dy - dx;
        for (int i = 0; i <= dx; i++) {
            safePutPixel(x, y, color);
            if (p < 0) {
                p += 2 * dy;
            } else {
                y += sy;
                p += 2 * dy - 2 * dx;
            }
            x += sx;
        }
    } else {
        int p = 2 * dx - dy;
        for (int i = 0; i <= dy; i++) {
            safePutPixel(x, y, color);
            if (p < 0) {
                p += 2 * dx;
            } else {
                x += sx;
                p += 2 * dx - 2 * dy;
            }
            y += sy;
        }
    }
}

// ============================================================================
// MIDPOINT CIRCLE ALGORITHM — Exact port of assign2.cpp & graphics.py
// ============================================================================
static inline void drawSymmetricPoints(int xc, int yc, int x, int y, int color) {
    safePutPixel(xc + x, yc + y, color);
    safePutPixel(xc - x, yc + y, color);
    safePutPixel(xc + x, yc - y, color);
    safePutPixel(xc - x, yc - y, color);
    safePutPixel(xc + y, yc + x, color);
    safePutPixel(xc - y, yc + x, color);
    safePutPixel(xc + y, yc - x, color);
    safePutPixel(xc - y, yc - x, color);
}

void drawMidpointCircle(int xc, int yc, int r, int color) {
    if (r <= 0) {
        safePutPixel(xc, yc, color);
        return;
    }

    int x = 0;
    int y = r;
    int del = 2 * (1 - r);
    int sig, sig1;

    while (x <= y) {
        drawSymmetricPoints(xc, yc, x, y, color);

        if (del < 0) {
            sig = (2 * del) + (2 * y) - 1;
            if (sig <= 0) {
                x++;
                del = del + (2 * x) + 1;
            } else {
                x++;
                y--;
                del = del + (2 * x) - (2 * y) + 2;
            }
        } else if (del > 0) {
            sig1 = (2 * del) - (2 * x) - 1;
            if (sig1 > 0) {
                y--;
                del = del - (2 * y) + 1;
            } else {
                x++;
                y--;
                del = del + (2 * x) - (2 * y) + 2;
            }
        } else {
            x++;
            y--;
            del = del + (2 * x) - (2 * y) + 2;
        }
    }
}

// ============================================================================
// WIREFRAME POLYGON HELPER
// ============================================================================
void drawWireframePolygon(const std::vector<ScreenPoint>& points, int color) {
    size_t n = points.size();
    if (n < 2) return;
    for (size_t i = 0; i < n; i++) {
        const ScreenPoint& p1 = points[i];
        const ScreenPoint& p2 = points[(i + 1) % n];
        drawBresenhamLine((int)std::round(p1.x), (int)std::round(p1.y),
                          (int)std::round(p2.x), (int)std::round(p2.y), color);
    }
}

void drawPolyLine(const std::vector<ScreenPoint>& points, int color) {
    if (points.size() < 2) return;
    for (size_t i = 0; i < points.size() - 1; i++) {
        drawBresenhamLine((int)std::round(points[i].x), (int)std::round(points[i].y),
                          (int)std::round(points[i+1].x), (int)std::round(points[i+1].y), color);
    }
}
