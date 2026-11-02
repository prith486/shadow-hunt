#include "entities.h"
#include <cmath>
#include <cstdio>

Player::Player(float start_x, float start_y, float spd)
    : x(start_x), y(start_y), speed(spd),
      max_health(100.0f), health(100.0f), radius(15.0f), angle(0.0f) {

    local_body_triangle.push_back(Point(16.0f, 0.0f));
    local_body_triangle.push_back(Point(-12.0f, -11.0f));
    local_body_triangle.push_back(Point(-6.0f, 0.0f));
    local_body_triangle.push_back(Point(-12.0f, 11.0f));

    local_inner_triangle.push_back(Point(11.0f, 0.0f));
    local_inner_triangle.push_back(Point(-7.0f, -6.0f));
    local_inner_triangle.push_back(Point(-3.0f, 0.0f));
    local_inner_triangle.push_back(Point(-7.0f, 6.0f));
}

std::vector<Point> Player::get_transformed_vertices(const std::vector<Point>& local_pts) const {
    std::vector<Point> rotated = CGMath::rotate(local_pts, angle, 0.0f, 0.0f);
    return CGMath::translate(rotated, x, y);
}

void Player::take_damage(float amount) {
    health = std::max(0.0f, health - amount);
}

void Player::heal(float amount) {
    health = std::min(max_health, health + amount);
}

void Player::render(bool show_hitbox) const {
    if (!is_alive()) {

        drawBresenhamLine((int)x - 10, (int)y - 10, (int)x + 10, (int)y + 10, COLOR_WIREFRAME_MED);
        drawBresenhamLine((int)x - 10, (int)y + 10, (int)x + 10, (int)y - 10, COLOR_WIREFRAME_MED);
        return;
    }

    std::vector<Point> body_world  = get_transformed_vertices(local_body_triangle);
    std::vector<Point> inner_world = get_transformed_vertices(local_inner_triangle);

    if (show_hitbox) {
        drawMidpointCircle((int)std::round(x), (int)std::round(y), (int)std::round(radius), COLOR_WIREFRAME_DIM);
    }

    drawWireframePolygon(CGMath::toScreenPoints(body_world), COLOR_WIREFRAME_WHITE);
    drawWireframePolygon(CGMath::toScreenPoints(inner_world), COLOR_WIREFRAME_LIGHT);

    if (!body_world.empty()) {
        int hx = (int)std::round(body_world[0].x);
        int hy = (int)std::round(body_world[0].y);
        drawBresenhamLine(hx - 2, hy, hx + 2, hy, COLOR_WIREFRAME_WHITE);
        drawBresenhamLine(hx, hy - 2, hx, hy + 2, COLOR_WIREFRAME_WHITE);
    }

    float bar_w = 26.0f;
    float bar_h = 3.5f;
    float bx = x - 13.0f;
    float by = y - radius - 8.0f;
    drawBresenhamLine((int)bx, (int)by, (int)(bx + bar_w), (int)by, COLOR_WIREFRAME_DIM);
    drawBresenhamLine((int)bx, (int)(by + bar_h), (int)(bx + bar_w), (int)(by + bar_h), COLOR_WIREFRAME_DIM);

    float hp_pct = std::max(0.0f, std::min(1.0f, health / max_health));
    if (hp_pct > 0.0f) {
        float fill_len = bar_w * hp_pct;
        drawBresenhamLine((int)bx, (int)by + 1, (int)(bx + fill_len), (int)by + 1, COLOR_WIREFRAME_WHITE);
    }
}

Enemy::Enemy(const std::vector<Point>& path_points, bool shielded, float spd)
    : path(path_points), is_shielded(shielded), speed(spd), radius(15.0f),
      is_alive(true), angle(0.0f), shoot_cooldown_max(35), shoot_timer(0),
      is_alert(false), has_laser(false), laser_linger_frames(0),
      fov_angle(3.14159265f / 2.0f), cone_range(165.0f) {
    damage_per_shot = is_shielded ? 7.0f : 5.0f;
    if (!path.empty()) {
        x = path[0].x;
        y = path[0].y;
    }
    if (path.size() > 1) {
        float dx = path[1].x - path[0].x;
        float dy = path[1].y - path[0].y;
        angle = std::atan2(dy, dx);
    }

    local_triangle.push_back(Point(16.0f, 0.0f));
    local_triangle.push_back(Point(-12.0f, -11.0f));
    local_triangle.push_back(Point(-6.0f, 0.0f));
    local_triangle.push_back(Point(-12.0f, 11.0f));

    if (is_shielded) {
        float shield_radius = 20.0f;
        int num_arc_steps = 14;
        for (int i = 0; i <= num_arc_steps; i++) {
            float ang = -3.14159265f / 2.0f + (3.14159265f / (float)num_arc_steps) * (float)i;
            local_shield_arc.push_back(Point(shield_radius * std::cos(ang), shield_radius * std::sin(ang)));
        }
    }

    update_geometry();
}

void Enemy::update_geometry() {
    Point head_local = local_triangle[0];
    Matrix3x3 comp = CGMath::matmul_3x3(CGMath::translation_matrix(x, y), CGMath::rotation_matrix(angle));
    Point head_world = CGMath::transform_point(comp, head_local);
    vision_polygon = CGMath::create_cone_polygon(head_world.x, head_world.y, angle, fov_angle, cone_range, 12);
}

std::string Enemy::update(Player& player) {
    if (!is_alive) return "";
    if (laser_linger_frames > 0) {
        laser_linger_frames--;
        if (laser_linger_frames == 0) has_laser = false;
    }
    if (shoot_timer > 0) shoot_timer--;

    is_alert = player.is_alive() && CGMath::point_in_polygon(player.x, player.y, vision_polygon);

    if (is_alert && player.is_alive() && shoot_timer == 0) {
        player.take_damage(damage_per_shot);
        shoot_timer = shoot_cooldown_max;
        laser_target = Point(player.x, player.y);
        has_laser = true;
        laser_linger_frames = 6;
        return "shot_player";
    }
    return "";
}

std::string Enemy::check_player_contact(Player& player) {
    if (!is_alive || !player.is_alive()) return "";
    if (CGMath::distance(x, y, player.x, player.y) > (radius + player.radius)) return "";

    if (!is_shielded) {
        is_alive = false;
        return "kill";
    }
    float dot = std::cos(angle) * (player.x - x) + std::sin(angle) * (player.y - y);
    if (dot <= 0.0f) {
        is_alive = false;
        return "kill";
    }
    return "shield_blocked";
}

void Enemy::render(bool show_hitbox) const {
    if (!is_alive) {

        drawBresenhamLine((int)x - 8, (int)y - 8, (int)x + 8, (int)y + 8, COLOR_WIREFRAME_DARK);
        drawBresenhamLine((int)x - 8, (int)y + 8, (int)x + 8, (int)y - 8, COLOR_WIREFRAME_DARK);
        return;
    }

    int cone_color = is_alert ? COLOR_WIREFRAME_WHITE : COLOR_CONE_DIM;
    drawWireframePolygon(CGMath::toScreenPoints(vision_polygon), cone_color);

    if (has_laser) {
        drawBresenhamLine((int)x, (int)y, (int)laser_target.x, (int)laser_target.y, COLOR_WIREFRAME_WHITE);
    }

    if (show_hitbox) {
        drawMidpointCircle((int)std::round(x), (int)std::round(y), (int)std::round(radius), COLOR_WIREFRAME_MED);
    }

    std::vector<Point> world_body = CGMath::translate(CGMath::rotate(local_triangle, angle, 0.0f, 0.0f), x, y);
    drawWireframePolygon(CGMath::toScreenPoints(world_body), COLOR_WIREFRAME_LIGHT);

    if (is_shielded && !local_shield_arc.empty()) {
        std::vector<Point> shield_pts = CGMath::translate(CGMath::rotate(local_shield_arc, angle, 0.0f, 0.0f), x, y);
        drawPolyLine(CGMath::toScreenPoints(shield_pts), COLOR_WIREFRAME_WHITE);
    }

    setcolor(COLOR_WIREFRAME_MED);
    setbkcolor(BLACK);
    outtextxy((int)x - 20, (int)y - 22, is_shielded ? (char*)"SHIELDED" : (char*)"GUARD");
}

SecurityCamera::SecurityCamera(float cx, float cy, float base_ang, float sweep_amp, float sweep_spd,
                               float fov_ang, float cone_r)
    : x(cx), y(cy), base_angle(base_ang), sweep_amplitude(sweep_amp), sweep_speed(sweep_spd),
      fov_angle(fov_ang), cone_range(cone_r), sweep_phase(0.0f), current_angle(base_ang),
      is_alarm_triggered(false) {
    update_cone();
}

void SecurityCamera::update_cone() {
    current_angle = base_angle + sweep_amplitude * std::sin(sweep_phase);
    vision_polygon = CGMath::create_cone_polygon(x, y, current_angle, fov_angle, cone_range, 16);
}

bool SecurityCamera::update(const Player& player) {
    update_cone();
    if (!player.is_alive()) return false;
    bool detected = CGMath::point_in_polygon(player.x, player.y, vision_polygon);
    if (detected) is_alarm_triggered = true;
    return detected;
}

void SecurityCamera::render(bool alarm_active) const {
    int cone_color = (alarm_active || is_alarm_triggered) ? COLOR_WIREFRAME_WHITE : COLOR_CONE_DIM;
    drawWireframePolygon(CGMath::toScreenPoints(vision_polygon), cone_color);

    float lx = x + 16.0f * std::cos(current_angle);
    float ly = y + 16.0f * std::sin(current_angle);
    drawBresenhamLine((int)x, (int)y, (int)lx, (int)ly, COLOR_WIREFRAME_MED);
}

Coin::Coin(float _x, float _y, float r)
    : x(_x), y(_y), base_radius(r) {
    int num_segments = 16;
    for (int i = 0; i < num_segments; i++) {
        float ang = (2.0f * 3.14159265f / (float)num_segments) * (float)i;
        base_polygon.push_back(Point(x + base_radius * std::cos(ang), y + base_radius * std::sin(ang)));
    }
}

bool Coin::collides_with_player(float px, float py, float pr) const {
    return CGMath::distance(x, y, px, py) <= (pr + base_radius);
}

void Coin::render() const {
    drawWireframePolygon(CGMath::toScreenPoints(base_polygon), COLOR_WIREFRAME_LIGHT);
}

HealthKit::HealthKit(float _x, float _y, float size)
    : x(_x), y(_y), radius(size / 2.0f) {
    float hw = 2.5f;
    float hs = 7.0f;
    float s  = radius;

    base_plus.push_back(Point(x - hw, y - hs));
    base_plus.push_back(Point(x + hw, y - hs));
    base_plus.push_back(Point(x + hw, y - hw));
    base_plus.push_back(Point(x + hs, y - hw));
    base_plus.push_back(Point(x + hs, y + hw));
    base_plus.push_back(Point(x + hw, y + hw));
    base_plus.push_back(Point(x + hw, y + hs));
    base_plus.push_back(Point(x - hw, y + hs));
    base_plus.push_back(Point(x - hw, y + hw));
    base_plus.push_back(Point(x - hs, y + hw));
    base_plus.push_back(Point(x - hs, y - hw));
    base_plus.push_back(Point(x - hw, y - hw));

    base_box.push_back(Point(x - s, y - s));
    base_box.push_back(Point(x + s, y - s));
    base_box.push_back(Point(x + s, y + s));
    base_box.push_back(Point(x - s, y + s));
}

bool HealthKit::collides_with_player(float px, float py, float pr) const {
    return CGMath::distance(x, y, px, py) <= (pr + radius);
}

void HealthKit::render() const {
    drawWireframePolygon(CGMath::toScreenPoints(base_box), COLOR_WIREFRAME_MED);
    drawWireframePolygon(CGMath::toScreenPoints(base_plus), COLOR_WIREFRAME_WHITE);
}

CollectibleManager::CollectibleManager() {}

void CollectibleManager::populate_map(const MapEngine& map_engine) {
    coins.clear();
    health_kits.clear();

    float ox = map_engine.ox;
    float oy = map_engine.oy;
    float wt = MapEngine::WALL_THICKNESS;
    float pw = MapEngine::PASSAGE_WIDTH;
    float bs = MapEngine::BOX_SIZE;

    float col_centers[4] = {
        ox + wt + pw / 2.0f,
        ox + wt + pw + bs + pw / 2.0f,
        ox + wt + 2.0f * pw + 2.0f * bs + pw / 2.0f,
        ox + wt + 3.0f * pw + 3.0f * bs + pw / 2.0f
    };
    float row_centers[3] = {
        oy + wt + pw / 2.0f,
        oy + wt + pw + bs + pw / 2.0f,
        oy + wt + 2.0f * pw + 2.0f * bs + pw / 2.0f
    };
    float box_col_centers[3] = {
        ox + wt + pw + bs / 2.0f,
        ox + wt + 2.0f * pw + 1.5f * bs,
        ox + wt + 3.0f * pw + 2.5f * bs
    };

    coins.push_back(Coin(box_col_centers[0], row_centers[0]));
    coins.push_back(Coin(box_col_centers[1], row_centers[0]));
    coins.push_back(Coin(box_col_centers[2], row_centers[0]));
    coins.push_back(Coin(col_centers[3],     row_centers[1]));
    coins.push_back(Coin(box_col_centers[0], row_centers[2]));
    coins.push_back(Coin(box_col_centers[1], row_centers[2]));
    coins.push_back(Coin(box_col_centers[2], row_centers[2]));

    health_kits.push_back(HealthKit(col_centers[0], row_centers[1]));
    health_kits.push_back(HealthKit(col_centers[1], row_centers[1]));
    health_kits.push_back(HealthKit(col_centers[2], row_centers[1]));
}

void CollectibleManager::update_and_collide(Player& player, int& score_out) {
    std::vector<Coin> rem_coins;
    for (size_t i = 0; i < coins.size(); i++) {
        if (coins[i].collides_with_player(player.x, player.y, player.radius)) {
            score_out += 10;
        } else {
            rem_coins.push_back(coins[i]);
        }
    }
    coins = rem_coins;

    std::vector<HealthKit> rem_kits;
    for (size_t i = 0; i < health_kits.size(); i++) {
        if (health_kits[i].collides_with_player(player.x, player.y, player.radius)) {
            player.heal(15.0f);
        } else {
            rem_kits.push_back(health_kits[i]);
        }
    }
    health_kits = rem_kits;
}

void CollectibleManager::render() const {
    for (size_t i = 0; i < coins.size(); i++) {
        coins[i].render();
    }
    for (size_t i = 0; i < health_kits.size(); i++) {
        health_kits[i].render();
    }
}

