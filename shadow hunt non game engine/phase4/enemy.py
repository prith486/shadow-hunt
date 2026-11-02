import math
from typing import List, Tuple, Optional
from cg_math import CGMath, Point, Points
from fill_algo import draw_filled_polygon, draw_bresenham_segment

class Enemy:

    def __init__(self, path: List[Point], is_shielded: bool=False, speed: float=2.0):
        self.path = [tuple(p) for p in path]
        self.is_shielded = is_shielded
        self.speed = float(speed)
        self.x, self.y = self.path[0]
        self.current_wp_index = 1
        self.path_direction = 1
        self.radius = 15.0
        self.is_alive = True
        self.angle = 0.0
        self.damage_per_shot = 7.0 if self.is_shielded else 5.0
        self.shoot_cooldown_max = 35
        self.shoot_timer = 0
        self.is_alert = False
        self.laser_target: Optional[Point] = None
        self.laser_linger_frames = 0
        self._keep: List = []
        self.fov_angle = math.pi / 2.0
        self.cone_range = 165.0
        self.vision_polygon: Points = []
        self.local_triangle: Points = [(16.0, 0.0), (-12.0, -11.0), (-6.0, 0.0), (-12.0, 11.0)]
        self.local_shield_arc: Points = []
        if self.is_shielded:
            shield_radius = 20.0
            num_arc_steps = 14
            for i in range(num_arc_steps + 1):
                ang = -math.pi / 2.0 + math.pi / num_arc_steps * i
                sx = shield_radius * math.cos(ang)
                sy = shield_radius * math.sin(ang)
                self.local_shield_arc.append((sx, sy))
        self.hitbox_points: List[Tuple[int, int]] = []
        self._update_geometry()

    def _update_geometry(self):
        self.hitbox_points = CGMath.bresenham_circle(self.x, self.y, self.radius)
        head_world = CGMath.transform_point(CGMath.matmul_3x3(CGMath.translation_matrix(self.x, self.y), CGMath.rotation_matrix(self.angle)), self.local_triangle[0])
        self.vision_polygon = CGMath.create_cone_polygon(origin_x=head_world[0], origin_y=head_world[1], facing_angle=self.angle, fov_angle=self.fov_angle, length=self.cone_range, num_arc_steps=12)

    def _patrol_step(self):
        if len(self.path) < 2 or not self.is_alive:
            return
        target_x, target_y = self.path[self.current_wp_index]
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist <= self.speed:
            self.x = target_x
            self.y = target_y
            next_idx = self.current_wp_index + self.path_direction
            if next_idx >= len(self.path):
                self.path_direction = -1
                self.current_wp_index = len(self.path) - 2
            elif next_idx < 0:
                self.path_direction = 1
                self.current_wp_index = 1
            else:
                self.current_wp_index = next_idx
            target_x, target_y = self.path[self.current_wp_index]
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
        if dist > 0.001:
            step_dx = dx / dist * self.speed
            step_dy = dy / dist * self.speed
            self.angle = math.atan2(step_dy, step_dx)
            translated = CGMath.translate([(self.x, self.y)], step_dx, step_dy)
            self.x, self.y = translated[0]
        self._update_geometry()

    def update(self, player) -> Optional[str]:
        if not self.is_alive:
            return None
        if self.laser_linger_frames > 0:
            self.laser_linger_frames -= 1
            if self.laser_linger_frames == 0:
                self.laser_target = None
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
        self._patrol_step()
        if player.is_alive():
            self.is_alert = CGMath.point_in_polygon(player.x, player.y, self.vision_polygon)
        else:
            self.is_alert = False
        if self.is_alert and player.is_alive():
            if self.shoot_timer == 0:
                player.take_damage(self.damage_per_shot)
                self.shoot_timer = self.shoot_cooldown_max
                self.laser_target = (player.x, player.y)
                self.laser_linger_frames = 6
                return 'shot_player'
        return None

    def check_player_contact(self, player) -> Optional[str]:
        if not self.is_alive or not player.is_alive():
            return None
        center_dist = CGMath.distance(self.x, self.y, player.x, player.y)
        if center_dist > self.radius + player.radius:
            return None
        if not self.is_shielded:
            self.is_alive = False
            return 'kill'
        else:
            fx = math.cos(self.angle)
            fy = math.sin(self.angle)
            vx = player.x - self.x
            vy = player.y - self.y
            dot = fx * vx + fy * vy
            if dot <= 0.0:
                self.is_alive = False
                return 'kill'
            else:
                return 'shield_blocked'

    def render(self, canvas, show_hitbox: bool=False):
        self._keep.clear()
        if not self.is_alive:
            dead = [(self.x + 8 * math.cos(2 * math.pi * i / 12), self.y + 8 * math.sin(2 * math.pi * i / 12)) for i in range(12)]
            draw_filled_polygon(canvas, dead, '#3f1212', '#7f1d1d', 'enemy_dead', self._keep)
            canvas.create_text(self.x, self.y, text='X', fill='#ef4444', font=('Consolas', 10, 'bold'), tags='enemy_dead')
            return
        cone_fill = '#ef4444' if self.is_alert else '#eab308'
        cone_outline = '#f87171' if self.is_alert else '#fde047'
        cone_pts = [coord for pt in self.vision_polygon for coord in pt]
        canvas.create_polygon(cone_pts, fill=cone_fill, outline=cone_outline, stipple='gray25', tags='enemy_vision')
        if self.laser_target is not None:
            draw_bresenham_segment(canvas, self.x, self.y, self.laser_target[0], self.laser_target[1], '#f43f5e', 'enemy_laser', self._keep, width=4)
            draw_bresenham_segment(canvas, self.x, self.y, self.laser_target[0], self.laser_target[1], '#ffffff', 'enemy_laser_core', self._keep, width=2)
        if show_hitbox:
            for hx, hy in self.hitbox_points[::3]:
                canvas.create_rectangle(hx, hy, hx + 2, hy + 2, fill='#f87171', outline='#f87171', tags='enemy_hitbox')
        rotated_body = CGMath.rotate(self.local_triangle, self.angle, 0.0, 0.0)
        world_body = CGMath.translate(rotated_body, self.x, self.y)
        draw_filled_polygon(canvas, world_body, '#dc2626', '#f87171', 'enemy_body', self._keep)
        head_pt = world_body[0]
        canvas.create_oval(head_pt[0] - 2.5, head_pt[1] - 2.5, head_pt[0] + 2.5, head_pt[1] + 2.5, fill='#ffffff', outline='#fca5a5', tags='enemy_head')
        if self.is_shielded and len(self.local_shield_arc) > 0:
            rotated_shield = CGMath.rotate(self.local_shield_arc, self.angle, 0.0, 0.0)
            world_shield = CGMath.translate(rotated_shield, self.x, self.y)
            for i in range(len(world_shield) - 1):
                a, b = (world_shield[i], world_shield[i + 1])
                draw_bresenham_segment(canvas, a[0], a[1], b[0], b[1], '#00e5ff', 'enemy_shield', self._keep, width=3)
        type_str = 'SHIELDED' if self.is_shielded else 'GUARD'
        type_color = '#38bdf8' if self.is_shielded else '#fca5a5'
        canvas.create_text(self.x, self.y - 20, text=type_str, fill=type_color, font=('Consolas', 7, 'bold'), tags='enemy_label')
