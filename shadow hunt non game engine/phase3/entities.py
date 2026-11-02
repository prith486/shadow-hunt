import math
import pygame
from graphics import bresenham_line, bresenham_circle
from game_map import CELL_SIZE
from transforms import apply_transformation, translation_matrix, rotation_matrix, scaling_matrix, identity

class Player:

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 10
        self.speed = 2.5
        self.health = 100.0
        self.shield_radius = 14
        self.current_transform = 'None'
        self.facing_angle = -90.0
        self.is_detected = False

    def update(self, keys, game_map, rep_type):
        tx = 0.0
        ty = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            ty -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            ty += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            tx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            tx += self.speed
        if tx == 0.0 and ty == 0.0:
            self.current_transform = 'None'
            return
        self.current_transform = 'Translation'
        self.facing_angle = math.degrees(math.atan2(ty, tx))
        T = translation_matrix(tx, ty, rep_type)
        result = apply_transformation(T, [(self.x, self.y)], rep_type)
        new_x, new_y = result[0]
        if not self._collides(new_x, self.y, game_map):
            self.x = new_x
        if not self._collides(self.x, new_y, game_map):
            self.y = new_y

    def _collides(self, px, py, game_map):
        margin = self.radius
        corners = [(px - margin, py - margin), (px + margin, py - margin), (px - margin, py + margin), (px + margin, py + margin)]
        for cx, cy in corners:
            col = int(cx // CELL_SIZE)
            row = int(cy // CELL_SIZE)
            if game_map.is_wall(row, col):
                return True
        return False

    def draw(self, screen, rep_type):
        ix = int(round(self.x))
        iy = int(round(self.y))
        local_pts = [(8.0, 0.0), (-6.0, -6.0), (-6.0, 6.0)]
        if self.is_detected:
            pulse = 0.25 * math.sin(pygame.time.get_ticks() * 0.008)
            scale = 1.25 + pulse
            draw_color = (220, 50, 50)
        else:
            scale = 1.0
            draw_color = (255, 255, 255)
        S = scaling_matrix(scale, scale)
        scaled = apply_transformation(S, local_pts, rep_type)
        R = rotation_matrix(self.facing_angle, rep_type)
        rotated = apply_transformation(R, scaled, rep_type)
        T = translation_matrix(self.x, self.y, rep_type)
        pts = apply_transformation(T, rotated, rep_type)
        p1 = (int(round(pts[0][0])), int(round(pts[0][1])))
        p2 = (int(round(pts[1][0])), int(round(pts[1][1])))
        p3 = (int(round(pts[2][0])), int(round(pts[2][1])))
        bresenham_line(screen, p1[0], p1[1], p2[0], p2[1], draw_color)
        bresenham_line(screen, p2[0], p2[1], p3[0], p3[1], draw_color)
        bresenham_line(screen, p3[0], p3[1], p1[0], p1[1], draw_color)
        bresenham_circle(screen, ix, iy, self.shield_radius, draw_color)

class Enemy:

    def __init__(self, x, y, facing_angle_deg, sight_radius=100):
        self.x = float(x)
        self.y = float(y)
        self.facing_angle = float(facing_angle_deg)
        self.sight_radius = sight_radius
        self.fov_half_angle = 45.0
        self.is_player_detected = False
        self.target_x = 0.0
        self.target_y = 0.0
        self.patrol_ax = self.x
        self.patrol_ay = self.y
        self.patrol_bx = self.x
        self.patrol_by = self.y
        self.patrol_speed = 0.8
        self.patrol_going_b = True
        self.rotate_speed = 3.0

    def _collides(self, px, py, game_map):
        margin = 8
        for cx, cy in [(px - margin, py - margin), (px + margin, py - margin), (px - margin, py + margin), (px + margin, py + margin)]:
            col = int(cx // CELL_SIZE)
            row = int(cy // CELL_SIZE)
            if game_map.is_wall(row, col):
                return True
        return False

    def update_patrol(self, rep_type, game_map):
        if self.is_player_detected:
            tx_goal = self.target_x
            ty_goal = self.target_y
            speed = self.patrol_speed * 1.5
        elif self.patrol_going_b:
            tx_goal = self.patrol_bx
            ty_goal = self.patrol_by
            speed = self.patrol_speed
        else:
            tx_goal = self.patrol_ax
            ty_goal = self.patrol_ay
            speed = self.patrol_speed
        dx = tx_goal - self.x
        dy = ty_goal - self.y
        dist = math.hypot(dx, dy)
        if dist < speed:
            self.x = tx_goal
            self.y = ty_goal
            if not self.is_player_detected:
                self.patrol_going_b = not self.patrol_going_b
            return
        step_x = dx / dist * speed
        step_y = dy / dist * speed
        T = translation_matrix(step_x, step_y, rep_type)
        result = apply_transformation(T, [(self.x, self.y)], rep_type)
        new_x, new_y = result[0]
        blocked_x = self._collides(new_x, self.y, game_map)
        blocked_y = self._collides(self.x, new_y, game_map)
        if not blocked_x:
            self.x = new_x
        if not blocked_y:
            self.y = new_y
        if blocked_x and blocked_y:
            self.patrol_going_b = not self.patrol_going_b

    def update_rotation(self, rep_type):
        if self.is_player_detected:
            tx_goal = self.target_x
            ty_goal = self.target_y
        elif self.patrol_going_b:
            tx_goal = self.patrol_bx
            ty_goal = self.patrol_by
        else:
            tx_goal = self.patrol_ax
            ty_goal = self.patrol_ay
        goal_dx = tx_goal - self.x
        goal_dy = ty_goal - self.y
        dist = math.hypot(goal_dx, goal_dy)
        if dist < 1.0:
            return
        target_angle = math.degrees(math.atan2(goal_dy, goal_dx))
        delta = (target_angle - self.facing_angle + 180) % 360 - 180
        step = max(-self.rotate_speed, min(self.rotate_speed, delta))
        if abs(step) < 0.1:
            return
        R = rotation_matrix(step, rep_type)
        rad = math.radians(self.facing_angle)
        fwd_x = math.cos(rad)
        fwd_y = math.sin(rad)
        result = apply_transformation(R, [(fwd_x, fwd_y)], rep_type)
        new_fx, new_fy = result[0]
        self.facing_angle = math.degrees(math.atan2(new_fy, new_fx))

    def update_detection(self, player):
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.sight_radius:
            self.is_player_detected = False
            return False
        angle_to_player = math.degrees(math.atan2(dy, dx))
        rel_angle = (angle_to_player - self.facing_angle + 180) % 360 - 180
        if abs(rel_angle) <= self.fov_half_angle:
            self.is_player_detected = True
            self.target_x = player.x
            self.target_y = player.y
            return True
        else:
            self.is_player_detected = False
            return False

    def draw(self, screen, rep_type):
        ix = int(round(self.x))
        iy = int(round(self.y))
        color = (255, 255, 255)
        local_body = [(10.0, 0.0), (-8.0, -8.0), (-8.0, 8.0)]
        scale = 1.3 if self.is_player_detected else 1.0
        S = scaling_matrix(scale, scale)
        scaled_body = apply_transformation(S, local_body, rep_type)
        R = rotation_matrix(self.facing_angle, rep_type)
        rotated_body = apply_transformation(R, scaled_body, rep_type)
        T = translation_matrix(self.x, self.y, rep_type)
        world_body = apply_transformation(T, rotated_body, rep_type)
        p0 = (int(round(world_body[0][0])), int(round(world_body[0][1])))
        p1 = (int(round(world_body[1][0])), int(round(world_body[1][1])))
        p2 = (int(round(world_body[2][0])), int(round(world_body[2][1])))
        bresenham_line(screen, p0[0], p0[1], p1[0], p1[1], color)
        bresenham_line(screen, p1[0], p1[1], p2[0], p2[1], color)
        bresenham_line(screen, p2[0], p2[1], p0[0], p0[1], color)
        left_angle_rad = math.radians(self.facing_angle - self.fov_half_angle)
        right_angle_rad = math.radians(self.facing_angle + self.fov_half_angle)
        lx = ix + int(self.sight_radius * math.cos(left_angle_rad))
        ly = iy + int(self.sight_radius * math.sin(left_angle_rad))
        rx = ix + int(self.sight_radius * math.cos(right_angle_rad))
        ry = iy + int(self.sight_radius * math.sin(right_angle_rad))
        bresenham_line(screen, ix, iy, lx, ly, color)
        bresenham_line(screen, ix, iy, rx, ry, color)
        steps = 16
        for i in range(steps):
            a1 = math.radians(self.facing_angle - self.fov_half_angle + i * 90.0 / steps)
            a2 = math.radians(self.facing_angle - self.fov_half_angle + (i + 1) * 90.0 / steps)
            x1 = ix + int(self.sight_radius * math.cos(a1))
            y1 = iy + int(self.sight_radius * math.sin(a1))
            x2 = ix + int(self.sight_radius * math.cos(a2))
            y2 = iy + int(self.sight_radius * math.sin(a2))
            bresenham_line(screen, x1, y1, x2, y2, color)
