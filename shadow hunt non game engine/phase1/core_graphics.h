#ifndef CORE_GRAPHICS_H
#define CORE_GRAPHICS_H

#include <graphics.h>
#include <cmath>
#include <algorithm>

void drawLineDDA(
    int x1, int y1, int x2, int y2,
    int color = WHITE,
    int camX = 0, int camY = 0,
    int screenW = 900, int screenH = 600
);

void drawBresenhamLine(
    int x1, int y1, int x2, int y2,
    int color = WHITE,
    int camX = 0, int camY = 0,
    int screenW = 900, int screenH = 600
);

#endif

