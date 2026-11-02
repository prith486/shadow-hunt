#include "game_map.h"
#include <algorithm>
#include <queue>
#include <stack>

static const int INITIAL_MAP_MATRIX[MAP_ROWS][MAP_COLS] = {
    {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0},
    {0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0},
    {0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0},
    {0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,0,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0},
    {0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0},
    {0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
    {0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0},
    {0,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,0},
    {0,1,1,1,1,1,0,0,1,1,1,1,0,1,0,0,1,1,1,1,0,0,1,0,1,1,1,0,0,0,1,1,1,1,1,0},
    {0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,0,1,0,1,1,0,1,0,0,0,0,0},
    {0,0,1,0,0,1,0,0,0,0,1,0,0,1,1,1,1,0,0,1,0,0,1,0,0,1,0,0,1,1,1,0,0,0,0,0},
    {0,1,1,1,1,1,0,0,0,1,1,1,0,1,0,0,1,1,1,1,0,0,1,0,1,1,1,0,0,0,1,1,1,1,1,0},
    {0,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,0},
    {0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0},
    {0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0},
    {0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0},
    {0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,0,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0},
    {0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0},
    {0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0},
    {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0}
};

GameMap::GameMap(int scrW, int scrH)
    : screenW(scrW), screenH(scrH) {
    for (int r = 0; r < MAP_ROWS; r++) {
        for (int c = 0; c < MAP_COLS; c++) {
            grid[r][c] = INITIAL_MAP_MATRIX[r][c];
        }
    }
    generate_walls();
    generate_zero_objects();
}

bool GameMap::is_wall(int row, int col) const {
    if (row < 0 || row >= MAP_ROWS) return true;
    if (col < 0 || col >= MAP_COLS) return true;
    return grid[row][col] == 0;
}

void GameMap::generate_walls() {
    wall_segments.clear();

    for (int row = 0; row < MAP_ROWS; row++) {
        for (int col = 0; col < MAP_COLS; col++) {
            if (grid[row][col] != 1) continue;

            int x = col * CELL_SIZE;
            int y = row * CELL_SIZE;

            if (is_wall(row - 1, col)) {
                wall_segments.push_back(WallSegment(x, y, x + CELL_SIZE, y));
            }

            if (is_wall(row + 1, col)) {
                wall_segments.push_back(WallSegment(x, y + CELL_SIZE, x + CELL_SIZE, y + CELL_SIZE));
            }

            if (is_wall(row, col - 1)) {
                wall_segments.push_back(WallSegment(x, y, x, y + CELL_SIZE));
            }

            if (is_wall(row, col + 1)) {
                wall_segments.push_back(WallSegment(x + CELL_SIZE, y, x + CELL_SIZE, y + CELL_SIZE));
            }
        }
    }
}

void GameMap::generate_zero_objects() {
    crates.clear();
    peach_blocks.clear();

    bool visited[MAP_ROWS][MAP_COLS] = {false};

    for (int row = 0; row < MAP_ROWS; row++) {
        for (int col = 0; col < MAP_COLS; col++) {
            if (grid[row][col] != 0 || visited[row][col]) continue;

            std::stack<std::pair<int, int> > s;
            std::vector<std::pair<int, int> > group;

            s.push(std::make_pair(row, col));

            while (!s.empty()) {
                std::pair<int, int> cur = s.top();
                s.pop();
                int r = cur.first;
                int c = cur.second;

                if (r < 0 || r >= MAP_ROWS || c < 0 || c >= MAP_COLS) continue;
                if (visited[r][c] || grid[r][c] != 0) continue;

                visited[r][c] = true;
                group.push_back(std::make_pair(r, c));

                s.push(std::make_pair(r - 1, c));
                s.push(std::make_pair(r + 1, c));
                s.push(std::make_pair(r, c - 1));
                s.push(std::make_pair(r, c + 1));
            }

            bool touches_boundary = false;
            for (size_t i = 0; i < group.size(); i++) {
                int r = group[i].first;
                int c = group[i].second;
                if (r == 0 || r == MAP_ROWS - 1 || c == 0 || c == MAP_COLS - 1) {
                    touches_boundary = true;
                    break;
                }
            }

            if (touches_boundary) continue;

            if (group.size() == 1) {
                int r = group[0].first;
                int c = group[0].second;
                peach_blocks.push_back(Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE));
            } else if (group.size() <= 3) {
                for (size_t i = 0; i < group.size(); i++) {
                    int r = group[i].first;
                    int c = group[i].second;
                    crates.push_back(Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE));
                }
            }
        }
    }
}

void GameMap::draw_floor(int camX, int camY) {

}

void GameMap::draw_wall(int x1, int y1, int x2, int y2, int camX, int camY) {
    int half = WALL_THICKNESS / 2;
    if (y1 == y2) {
        for (int offset = -half; offset <= half; offset++) {
            drawBresenhamLine(x1, y1 + offset, x2, y2 + offset, COLOR_WIREFRAME, camX, camY, screenW, screenH);
        }
    } else {
        for (int offset = -half; offset <= half; offset++) {
            drawBresenhamLine(x1 + offset, y1, x2 + offset, y2, COLOR_WIREFRAME, camX, camY, screenW, screenH);
        }
    }
}

void GameMap::draw_walls(int camX, int camY) {
    for (size_t i = 0; i < wall_segments.size(); i++) {
        draw_wall(wall_segments[i].x1, wall_segments[i].y1, wall_segments[i].x2, wall_segments[i].y2, camX, camY);
    }
}

void GameMap::draw_crate(const Rect& rect, int camX, int camY) {
    int x = rect.x;
    int y = rect.y;
    int w = rect.width;
    int h = rect.height;

    drawBresenhamLine(x, y, x + w, y, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawBresenhamLine(x + w, y, x + w, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawBresenhamLine(x + w, y + h, x, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawBresenhamLine(x, y + h, x, y, COLOR_WIREFRAME, camX, camY, screenW, screenH);

    drawBresenhamLine(x, y, x + w, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawBresenhamLine(x + w, y, x, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
}

void GameMap::draw_crates(int camX, int camY) {
    for (size_t i = 0; i < crates.size(); i++) {
        draw_crate(crates[i], camX, camY);
    }
}

void GameMap::draw_peach_block(const Rect& rect, int camX, int camY) {
    int x = rect.x;
    int y = rect.y;
    int w = rect.width;
    int h = rect.height;

    drawLineDDA(x, y, x + w, y, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawLineDDA(x + w, y, x + w, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawLineDDA(x + w, y + h, x, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawLineDDA(x, y + h, x, y, COLOR_WIREFRAME, camX, camY, screenW, screenH);

    drawLineDDA(x + w / 2, y, x + w / 2, y + h, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawLineDDA(x, y + h / 2, x + w, y + h / 2, COLOR_WIREFRAME, camX, camY, screenW, screenH);
}

void GameMap::draw_peach_blocks(int camX, int camY) {
    for (size_t i = 0; i < peach_blocks.size(); i++) {
        draw_peach_block(peach_blocks[i], camX, camY);
    }
}

void GameMap::draw_character(int camX, int camY) {
    int cx = 75;
    int cy = 75;

    drawBresenhamLine(cx, cy - 15, cx + 15, cy + 15, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawBresenhamLine(cx + 15, cy + 15, cx - 15, cy + 15, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawBresenhamLine(cx - 15, cy + 15, cx, cy - 15, COLOR_WIREFRAME, camX, camY, screenW, screenH);

    drawLineDDA(cx, cy - 15, cx, cy - 30, COLOR_WIREFRAME, camX, camY, screenW, screenH);
    drawLineDDA(cx - 5, cy - 25, cx + 5, cy - 25, COLOR_WIREFRAME, camX, camY, screenW, screenH);
}

void GameMap::draw_debug_grid(int camX, int camY) {
    for (int x = 0; x <= MAP_WIDTH; x += CELL_SIZE) {
        drawBresenhamLine(x, 0, x, MAP_HEIGHT, COLOR_GRID, camX, camY, screenW, screenH);
    }
    for (int y = 0; y <= MAP_HEIGHT; y += CELL_SIZE) {
        drawLineDDA(0, y, MAP_WIDTH, y, COLOR_GRID, camX, camY, screenW, screenH);
    }
}

void GameMap::draw(int camX, int camY, bool showGrid) {
    draw_floor(camX, camY);
    draw_walls(camX, camY);
    draw_crates(camX, camY);
    draw_peach_blocks(camX, camY);
    draw_character(camX, camY);
    if (showGrid) {
        draw_debug_grid(camX, camY);
    }
}

std::vector<Rect> GameMap::get_collision_rects() const {
    std::vector<Rect> collision_rects;

    for (size_t i = 0; i < wall_segments.size(); i++) {
        const WallSegment& seg = wall_segments[i];
        if (seg.y1 == seg.y2) {
            collision_rects.push_back(Rect(
                std::min(seg.x1, seg.x2),
                seg.y1 - WALL_THICKNESS / 2,
                std::abs(seg.x2 - seg.x1),
                WALL_THICKNESS
            ));
        } else {
            collision_rects.push_back(Rect(
                seg.x1 - WALL_THICKNESS / 2,
                std::min(seg.y1, seg.y2),
                WALL_THICKNESS,
                std::abs(seg.y2 - seg.y1)
            ));
        }
    }

    collision_rects.insert(collision_rects.end(), crates.begin(), crates.end());
    collision_rects.insert(collision_rects.end(), peach_blocks.begin(), peach_blocks.end());

    return collision_rects;
}

