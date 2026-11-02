#ifndef GAME_MAP_H
#define GAME_MAP_H

#include <vector>
#include "core_graphics.h"

const int CELL_SIZE = 50;
const int MAP_ROWS = 20;
const int MAP_COLS = 36;
const int MAP_WIDTH = MAP_COLS * CELL_SIZE;
const int MAP_HEIGHT = MAP_ROWS * CELL_SIZE;
const int WALL_THICKNESS = 5;

const int DEFAULT_SCREEN_WIDTH = 900;
const int DEFAULT_SCREEN_HEIGHT = 600;

#define COLOR_WIREFRAME   COLOR(200, 200, 200)
#define COLOR_MAP_BG      COLOR(0, 0, 0)
#define COLOR_GRID        COLOR(185, 183, 177)

struct Rect {
    int x, y, width, height;
    Rect(int _x = 0, int _y = 0, int _w = 0, int _h = 0)
        : x(_x), y(_y), width(_w), height(_h) {}
};

struct WallSegment {
    int x1, y1, x2, y2;
    WallSegment(int _x1 = 0, int _y1 = 0, int _x2 = 0, int _y2 = 0)
        : x1(_x1), y1(_y1), x2(_x2), y2(_y2) {}
};

class GameMap {
private:
    int grid[MAP_ROWS][MAP_COLS];
    std::vector<WallSegment> wall_segments;
    std::vector<Rect> crates;
    std::vector<Rect> peach_blocks;
    int screenW;
    int screenH;

public:
    GameMap(int scrW = DEFAULT_SCREEN_WIDTH, int scrH = DEFAULT_SCREEN_HEIGHT);

    bool is_wall(int row, int col) const;

    void generate_walls();
    void generate_zero_objects();

    void draw_floor(int camX, int camY);
    void draw_wall(int x1, int y1, int x2, int y2, int camX, int camY);
    void draw_walls(int camX, int camY);

    void draw_crate(const Rect& rect, int camX, int camY);
    void draw_crates(int camX, int camY);

    void draw_peach_block(const Rect& rect, int camX, int camY);
    void draw_peach_blocks(int camX, int camY);

    void draw_character(int camX, int camY);
    void draw_debug_grid(int camX, int camY);

    void draw(int camX = 0, int camY = 0, bool showGrid = true);

    std::vector<Rect> get_collision_rects() const;

    const std::vector<WallSegment>& getWallSegments() const { return wall_segments; }
    const std::vector<Rect>& getCrates() const { return crates; }
    const std::vector<Rect>& getPeachBlocks() const { return peach_blocks; }
};

#endif

