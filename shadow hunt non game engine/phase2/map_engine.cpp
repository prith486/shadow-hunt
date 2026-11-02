#include "map_engine.h"
#include <sstream>

const float MapEngine::WALL_THICKNESS = 5.0f;
const float MapEngine::PASSAGE_WIDTH  = 100.0f;
const float MapEngine::BOX_SIZE       = 120.0f;

static inline void drawRectLines(float x1, float y1, float x2, float y2, int color) {
    int ix1 = (int)std::round(x1);
    int iy1 = (int)std::round(y1);
    int ix2 = (int)std::round(x2);
    int iy2 = (int)std::round(y2);

    drawBresenhamLine(ix1, iy1, ix2, iy1, color);
    drawBresenhamLine(ix2, iy1, ix2, iy2, color);
    drawBresenhamLine(ix2, iy2, ix1, iy2, color);
    drawBresenhamLine(ix1, iy2, ix1, iy1, color);
}

bool Wall::collides_with_circle(float cx, float cy, float r) const {
    float nearest_x = std::max(x1, std::min(cx, x2));
    float nearest_y = std::max(y1, std::min(cy, y2));
    float dx = cx - nearest_x;
    float dy = cy - nearest_y;
    return (dx * dx + dy * dy) <= (r * r);
}

void Wall::render() const {
    drawRectLines(x1, y1, x2, y2, COLOR_WIREFRAME_DARK);
}

bool CrossedBox::collides_with_circle(float cx, float cy, float r) const {
    float nearest_x = std::max(x1, std::min(cx, x2));
    float nearest_y = std::max(y1, std::min(cy, y2));
    float dx = cx - nearest_x;
    float dy = cy - nearest_y;
    return (dx * dx + dy * dy) <= (r * r);
}

void CrossedBox::render() const {

    drawRectLines(x1, y1, x2, y2, COLOR_WIREFRAME_MED);

    float ix1 = x1 + 7.0f;
    float iy1 = y1 + 7.0f;
    float ix2 = x2 - 7.0f;
    float iy2 = y2 - 7.0f;
    drawRectLines(ix1, iy1, ix2, iy2, COLOR_WIREFRAME_DIM);

    drawBresenhamLine((int)std::round(ix1), (int)std::round(iy1),
                      (int)std::round(ix2), (int)std::round(iy2), COLOR_WIREFRAME_DARK);
    drawBresenhamLine((int)std::round(ix1), (int)std::round(iy2),
                      (int)std::round(ix2), (int)std::round(iy1), COLOR_WIREFRAME_DARK);
}

bool Door::update_proximity(float player_x, float player_y) {
    is_open = (CGMath::distance(player_x, player_y, mid_x, mid_y) <= trigger_radius);
    return is_open;
}

bool Door::collides_with_circle(float cx, float cy, float r) const {
    if (slide_progress >= 0.75f) return false;
    float cur_x2 = x1 + (x2 - x1) * (1.0f - slide_progress);
    float cur_y2 = y1 + (y2 - y1) * (1.0f - slide_progress);
    float dx = cur_x2 - x1;
    float dy = cur_y2 - y1;
    float seg_len_sq = dx * dx + dy * dy;
    if (seg_len_sq == 0.0f) {
        return CGMath::distance(cx, cy, x1, y1) <= r;
    }
    float t = std::max(0.0f, std::min(1.0f, ((cx - x1) * dx + (cy - y1) * dy) / seg_len_sq));
    return CGMath::distance(cx, cy, x1 + t * dx, y1 + t * dy) <= (r + 2.5f);
}

void Door::render() const {
    float cur_x2 = x1 + (x2 - x1) * (1.0f - slide_progress);
    float cur_y2 = y1 + (y2 - y1) * (1.0f - slide_progress);

    if (slide_progress < 0.98f) {
        drawBresenhamLine((int)std::round(x1), (int)std::round(y1),
                          (int)std::round(cur_x2), (int)std::round(cur_y2), COLOR_WIREFRAME_WHITE);
    }

    int px1 = (int)std::round(x1);
    int py1 = (int)std::round(y1);
    int px2 = (int)std::round(x2);
    int py2 = (int)std::round(y2);
    drawBresenhamLine(px1 - 3, py1, px1 + 3, py1, COLOR_WIREFRAME_DARK);
    drawBresenhamLine(px1, py1 - 3, px1, py1 + 3, COLOR_WIREFRAME_DARK);
    drawBresenhamLine(px2 - 3, py2, px2 + 3, py2, COLOR_WIREFRAME_DARK);
    drawBresenhamLine(px2, py2 - 3, px2, py2 + 3, COLOR_WIREFRAME_DARK);
}

bool ExitDoor::is_reached(float px, float py, float radius) const {
    float nearest_x = std::max(x1, std::min(px, x2));
    float nearest_y = std::max(y1, std::min(py, y2));
    float dx = px - nearest_x;
    float dy = py - nearest_y;
    return (dx * dx + dy * dy) <= (radius * radius);
}

void ExitDoor::render(bool alarm_active) const {
    drawRectLines(x1, y1, x2, y2, COLOR_WIREFRAME_WHITE);

    for (int sx = (int)x1 + 8; sx < (int)x2 - 8; sx += 14) {
        drawBresenhamLine(sx, (int)y1 + 3, sx + 8, (int)y2 - 3, COLOR_WIREFRAME_MED);
    }

    setcolor(COLOR_WIREFRAME_WHITE);
    setbkcolor(BLACK);
    outtextxy((int)mid_x - 45, (int)y1 - 15, (char*)"[ EXIT DOOR ]");
}

MapEngine::MapEngine(float origin_x, float origin_y)
    : ox(origin_x), oy(origin_y), exit_door(0, 0, 0, 0) {
    build_map();
}

void MapEngine::build_map() {
    float wt = WALL_THICKNESS;
    float pw = PASSAGE_WIDTH;
    float bs = BOX_SIZE;

    room_w = 2 * wt + 4 * pw + 3 * bs;
    room_h = 2 * wt + 3 * pw + 2 * bs;

    walls.clear();

    walls.push_back(Wall(ox, oy, ox + room_w, oy + wt, "wall_top"));
    walls.push_back(Wall(ox, oy + room_h - wt, ox + room_w, oy + room_h, "wall_bottom"));
    walls.push_back(Wall(ox, oy, ox + wt, oy + room_h, "wall_left"));
    walls.push_back(Wall(ox + room_w - wt, oy, ox + room_w, oy + room_h, "wall_right"));

    boxes.clear();
    float col_x[3];
    for (int i = 0; i < 3; i++) {
        col_x[i] = ox + wt + pw + (float)i * (bs + pw);
    }
    float row_y[2];
    for (int j = 0; j < 2; j++) {
        row_y[j] = oy + wt + pw + (float)j * (bs + pw);
    }

    for (int c = 0; c < 3; c++) {
        for (int r = 0; r < 2; r++) {
            std::ostringstream ss;
            ss << "crate_" << c << "_" << r;
            boxes.push_back(CrossedBox(col_x[c], row_y[r], col_x[c] + bs, row_y[r] + bs, ss.str()));
        }
    }

    doors.clear();
    doors.push_back(Door(col_x[0] + bs, row_y[0] + bs / 2.0f, col_x[1], row_y[0] + bs / 2.0f, "door_1"));
    doors.push_back(Door(col_x[1] + bs, row_y[1] + bs / 2.0f, col_x[2], row_y[1] + bs / 2.0f, "door_2"));
    doors.push_back(Door(col_x[1] + bs / 2.0f, row_y[0] + bs, col_x[1] + bs / 2.0f, row_y[1], "door_3"));

    exit_door = ExitDoor(ox + room_w - wt - pw + 12.0f, oy + room_h - wt - 36.0f,
                         ox + room_w - wt - 12.0f,      oy + room_h - wt);
}

void MapEngine::update_doors(float px, float py) {
    for (size_t i = 0; i < doors.size(); i++) {
        doors[i].update_proximity(px, py);
    }
}

bool MapEngine::is_blocked(float cx, float cy, float radius) const {
    for (size_t i = 0; i < walls.size(); i++) {
        if (walls[i].collides_with_circle(cx, cy, radius)) return true;
    }
    for (size_t i = 0; i < boxes.size(); i++) {
        if (boxes[i].collides_with_circle(cx, cy, radius)) return true;
    }
    for (size_t i = 0; i < doors.size(); i++) {
        if (doors[i].collides_with_circle(cx, cy, radius)) return true;
    }
    return false;
}

void MapEngine::render(bool alarm_active) const {

    drawRectLines(ox, oy, ox + room_w, oy + room_h, COLOR_WIREFRAME_DIM);

    for (size_t i = 0; i < walls.size(); i++) {
        walls[i].render();
    }

    for (size_t i = 0; i < boxes.size(); i++) {
        boxes[i].render();
    }

    exit_door.render(alarm_active);

    for (size_t i = 0; i < doors.size(); i++) {
        doors[i].render();
    }
}

