#ifndef ENTITIES_H
#define ENTITIES_H

#include <vector>
#include <string>
#include "cg_math.h"
#include "map_engine.h"

// ============================================================================
// GAME ENTITIES (PHASE 2)
// Player (Assassin), Enemy (Guard & Shielded Enforcer), Security Camera, Collectibles
// ============================================================================

class Player {
public:
    float x, y, speed;
    float max_health, health, radius, angle;
    std::vector<Point> local_body_triangle;
    std::vector<Point> local_inner_triangle;

    Player(float start_x = 0.0f, float start_y = 0.0f, float spd = 4.5f);

    std::vector<Point> get_transformed_vertices(const std::vector<Point>& local_pts) const;
    void take_damage(float amount);
    void heal(float amount);
    bool is_alive() const { return health > 0.0f; }

    void render(bool show_hitbox = false) const;
};

class Enemy {
public:
    float x, y;
    std::vector<Point> path;
    bool is_shielded;
    float speed, radius;
    bool is_alive;
    float angle;
    float damage_per_shot;
    int shoot_cooldown_max;
    int shoot_timer;
    bool is_alert;
    Point laser_target;
    bool has_laser;
    int laser_linger_frames;
    float fov_angle, cone_range;
    std::vector<Point> vision_polygon;
    std::vector<Point> local_triangle;
    std::vector<Point> local_shield_arc;

    Enemy(const std::vector<Point>& path_points, bool shielded = false, float spd = 2.0f);

    void update_geometry();
    std::string update(Player& player);
    std::string check_player_contact(Player& player);
    void render(bool show_hitbox = false) const;
};

class SecurityCamera {
public:
    float x, y;
    float base_angle, sweep_amplitude, sweep_speed;
    float fov_angle, cone_range;
    float sweep_phase, current_angle;
    std::vector<Point> vision_polygon;
    bool is_alarm_triggered;

    SecurityCamera(float cx, float cy, float base_ang, float sweep_amp, float sweep_spd = 0.025f,
                   float fov_ang = 1.134f, float cone_r = 230.0f);

    void update_cone();
    bool update(const Player& player);
    void render(bool alarm_active = false) const;
};

class Coin {
public:
    float x, y, base_radius;
    std::vector<Point> base_polygon;

    Coin(float _x, float _y, float r = 10.0f);
    bool collides_with_player(float px, float py, float pr) const;
    void render() const;
};

class HealthKit {
public:
    float x, y, radius;
    std::vector<Point> base_plus;
    std::vector<Point> base_box;

    HealthKit(float _x, float _y, float size = 20.0f);
    bool collides_with_player(float px, float py, float pr) const;
    void render() const;
};

class CollectibleManager {
public:
    std::vector<Coin> coins;
    std::vector<HealthKit> health_kits;

    CollectibleManager();
    void populate_map(const MapEngine& map_engine);
    void update_and_collide(Player& player, int& score_out);
    void render() const;
};

#endif // ENTITIES_H
