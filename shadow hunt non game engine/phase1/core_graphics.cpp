#include "core_graphics.h"

static inline void putPixelClamped(int wx, int wy, int color, int camX, int camY, int screenW, int screenH) {
    int sx = wx - camX;
    int sy = wy - camY;
    if (sx >= 0 && sx < screenW && sy >= 0 && sy < screenH) {
        putpixel(sx, sy, color);
    }
}

void drawLineDDA(
    int x1, int y1, int x2, int y2,
    int color,
    int camX, int camY,
    int screenW, int screenH
) {
    float ey = std::abs((float)(y1 - y2));
    float ex = std::abs((float)(x1 - x2));
    float length = std::max(ey, ex);

    if (length == 0.0f) {
        putPixelClamped(x1, y1, color, camX, camY, screenW, screenH);
        return;
    }

    float dx = ex / length;
    float dy = ey / length;

    if (x2 < x1) dx = -dx;
    if (y2 < y1) dy = -dy;

    float x = (float)x1;
    float y = (float)y1;

    for (int i = 0; i <= (int)length; i++) {
        int ix = (int)std::round(x);
        int iy = (int)std::round(y);
        putPixelClamped(ix, iy, color, camX, camY, screenW, screenH);
        x += dx;
        y += dy;
    }
}

void drawBresenhamLine(
    int x1, int y1, int x2, int y2,
    int color,
    int camX, int camY,
    int screenW, int screenH
) {
    int dx = std::abs(x2 - x1);
    int dy = std::abs(y2 - y1);
    int sx = (x2 > x1) ? 1 : -1;
    int sy = (y2 > y1) ? 1 : -1;
    int x = x1;
    int y = y1;

    if (dx >= dy) {

        int p = 2 * dy - dx;
        for (int i = 0; i <= dx; i++) {
            putPixelClamped(x, y, color, camX, camY, screenW, screenH);
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
            putPixelClamped(x, y, color, camX, camY, screenW, screenH);
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

