#include "core_graphics.h"

// ============================================================================
// INTERNAL HELPER: Pixel Plotting with Camera Viewport Bounds Checking
// ============================================================================
static inline void putPixelClamped(int wx, int wy, int color, int camX, int camY, int screenW, int screenH) {
    int sx = wx - camX;
    int sy = wy - camY;
    if (sx >= 0 && sx < screenW && sy >= 0 && sy < screenH) {
        putpixel(sx, sy, color);
    }
}

// ============================================================================
// DDA LINE ALGORITHM
//
// Matches assign1.cpp line 8-33:
// ey = abs(y1 - y2)
// ex = abs(x1 - x2)
// length = max(ey, ex)
// dx = ex / length
// dy = ey / length
// ============================================================================
void drawLineDDA(
    int x1, int y1, int x2, int y2,
    int color,
    int camX, int camY,
    int screenW, int screenH
) {
    float ey = std::abs((float)(y1 - y2));
    float ex = std::abs((float)(x1 - x2));
    float length = std::max(ey, ex);

    // Handle single-point edge case to avoid division by zero
    if (length == 0.0f) {
        putPixelClamped(x1, y1, color, camX, camY, screenW, screenH);
        return;
    }

    float dx = ex / length;
    float dy = ey / length;

    // Adjust signs based on coordinate direction
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

// ============================================================================
// BRESENHAM LINE ALGORITHM
//
// Matches assign1b.cpp lines 8-41:
// Decision parameter form:
// P = 2 * dy - dx
// If P < 0: P += 2*dy
// Else: P += 2*dy - 2*dx, Y++
//
// Generalized for all 8 octants as in graphics.py lines 35-71
// ============================================================================
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
        // Octants with |slope| <= 1 (step along X)
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
        // Octants with |slope| > 1 (step along Y)
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
