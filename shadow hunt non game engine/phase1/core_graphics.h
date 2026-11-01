#ifndef CORE_GRAPHICS_H
#define CORE_GRAPHICS_H

#include <graphics.h>
#include <cmath>
#include <algorithm>

// ============================================================================
// CORE COMPUTER GRAPHICS ALGORITHMS (PHASE 1)
// Ports of:
// - assign1.cpp (DDA Line Drawing Algorithm)
// - assign1b.cpp (Bresenham's Line Drawing Algorithm)
//
// These algorithms calculate pixels step-by-step using fundamental line equations
// and decision parameters (p = 2*dy - dx) without any high-level engine shortcuts.
// ============================================================================

/**
 * DDA Line Drawing Algorithm
 * Exact port of assign1.cpp & graphics.py dda_line.
 * Uses floating point increments dx and dy based on max(|ex|, |ey|).
 */
void drawLineDDA(
    int x1, int y1, int x2, int y2,
    int color = WHITE,
    int camX = 0, int camY = 0,
    int screenW = 900, int screenH = 600
);

/**
 * Bresenham's Line Drawing Algorithm
 * Exact port of assign1b.cpp & graphics.py bresenham_line.
 * Uses integer arithmetic with decision parameter p = 2*dy - dx, generalized
 * across all octants for complete map coverage.
 */
void drawBresenhamLine(
    int x1, int y1, int x2, int y2,
    int color = WHITE,
    int camX = 0, int camY = 0,
    int screenW = 900, int screenH = 600
);

#endif // CORE_GRAPHICS_H
