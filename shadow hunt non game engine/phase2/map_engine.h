#ifndef MAP_ENGINE_H
#define MAP_ENGINE_H

#include <vector>
#include <string>
#include "cg_math.h"
#include "core_graphics.h"

struct Wall {
    float x1, y1, x2, y2;
    std::string wall_id;
    Wall(float _x1 = 0, float _y1 = 0, float _x2 = 0, float _y2 = 0, const std::string& id = "wall")
        : x1(std::min(_x1, _x2)), y1(std::min(_y1, _y2)),
          x2(std::max(_x1, _x2)), y2(std::max(_y1, _y2)), wall_id(id) {}

    bool collides_with_circle(float cx, float cy, float r) const;
    void render() const;
};

struct CrossedBox {
    float x1, y1, x2, y2;
    std::string box_id;
    float thickness;
    CrossedBox(float _x1 = 0, float _y1 = 0, float _x2 = 0, float _y2 = 0, const std::string& id = "box")
        : x1(std::min(_x1, _x2)), y1(std::min(_y1, _y2)),
          x2(std::max(_x1, _x2)), y2(std::max(_y1, _y2)), box_id(id), thickness(5.0f) {}

    bool collides_with_circle(float cx, float cy, float r) const;
    void render() const;
};

struct Door {
    float x1, y1, x2, y2;
    std::string door_id;
    float mid_x, mid_y;
    float trigger_radius;
    float slide_progress;
    bool is_open;

    Door(float _x1 = 0, float _y1 = 0, float _x2 = 0, float _y2 = 0, const std::string& id = "door", float trig_r = 75.0f)
        : x1(_x1), y1(_y1), x2(_x2), y2(_y2), door_id(id),
          mid_x((_x1 + _x2) / 2.0f), mid_y((_y1 + _y2) / 2.0f),
          trigger_radius(trig_r), slide_progress(0.0f), is_open(false) {}

    bool update_proximity(float player_x, float player_y);
    bool collides_with_circle(float cx, float cy, float r) const;
    void render() const;
};

struct ExitDoor {
    float x1, y1, x2, y2;
    float mid_x;
    ExitDoor(float _x1 = 0, float _y1 = 0, float _x2 = 0, float _y2 = 0)
        : x1(std::min(_x1, _x2)), y1(std::min(_y1, _y2)),
          x2(std::max(_x1, _x2)), y2(std::max(_y1, _y2)), mid_x((_x1 + _x2) / 2.0f) {}

    bool is_reached(float px, float py, float radius = 15.0f) const;
    void render(bool alarm_active = false) const;
};

class MapEngine {
public:
    static const float WALL_THICKNESS;
    static const float PASSAGE_WIDTH;
    static const float BOX_SIZE;

    float ox, oy;
    float room_w, room_h;

    std::vector<Wall> walls;
    std::vector<CrossedBox> boxes;
    std::vector<Door> doors;
    ExitDoor exit_door;

    MapEngine(float origin_x = 60.0f, float origin_y = 60.0f);

    void build_map();
    void update_doors(float px, float py);
    bool is_blocked(float cx, float cy, float radius = 15.0f) const;
    void render(bool alarm_active = false) const;
};

#endif

