#ifndef CORE_GRAPHICS_H
#define CORE_GRAPHICS_H

#include <graphics.h>
#include <cmath>
#include <vector>
#include <algorithm>

#define COLOR_WIREFRAME_WHITE    COLOR(255, 255, 255)
#define COLOR_WIREFRAME_LIGHT    COLOR(220, 220, 220)
#define COLOR_WIREFRAME_MED      COLOR(170, 170, 170)
#define COLOR_WIREFRAME_DARK     COLOR(119, 119, 119)
#define COLOR_WIREFRAME_DIM      COLOR(85, 85, 85)
#define COLOR_ALERT_RED          COLOR(255, 60, 60)
#define COLOR_CONE_DIM           COLOR(102, 102, 102)

struct ScreenPoint {
    float x, y;
    ScreenPoint(float _x = 0.0f, float _y = 0.0f) : x(_x), y(_y) {}
};

void drawLineDDA(int x1, int y1, int x2, int y2, int color = WHITE);

void drawBresenhamLine(int x1, int y1, int x2, int y2, int color = WHITE);

void drawMidpointCircle(int xc, int yc, int r, int color = WHITE);

void drawWireframePolygon(const std::vector<ScreenPoint>& points, int color = WHITE);

void drawPolyLine(const std::vector<ScreenPoint>& points, int color = WHITE);

#endif

