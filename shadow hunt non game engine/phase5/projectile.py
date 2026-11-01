"""
Projectile Module (Phase 5 - Player Shooting & Cohen-Sutherland Line Clipping)
=============================================================================
- High-velocity laser bolts fired by player
- Clipped using Cohen-Sutherland Line Clipping (CGMath.clip_line_cohen_sutherland)
- Real-time collision with map obstacles (walls, crates, doors)
- Damage & frontal shield deflection mechanics against patrolling enemies
"""

import math
from typing import Tuple, Optional
from cg_math import CGMath, Point

class PlayerBolt:
    def __init__(self, x: float, y: float, angle: float, speed: float = 14.0, damage: float = 25.0):
        self.x = float(x)
        self.y = float(y)
        self.angle = float(angle)
        self.speed = float(speed)
        self.damage = float(damage)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.tail_len = 16.0
        self.is_active = True
        self.max_life = 80 # frames
        self.life = self.max_life

    def update(self, map_engine) -> bool:
        if not self.is_active:
            return False

        self.life -= 1
        if self.life <= 0:
            self.is_active = False
            return False

        # Move bolt
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        # Check collision with walls / crates / doors
        if map_engine.is_blocked(new_x, new_y, radius=3.0):
            self.is_active = False
            return False

        self.x = new_x
        self.y = new_y
        return True

    def check_enemy_hit(self, enemy) -> Optional[str]:
        """
        Returns:
        - 'hit': Normal damage dealt
        - 'shield_blocked': Hit enemy's frontal shield (deflected)
        - None: No hit
        """
        if not self.is_active or not enemy.is_alive:
            return None

        dist = math.hypot(self.x - enemy.x, self.y - enemy.y)
        if dist <= (enemy.radius + 7.0):
            self.is_active = False
            if enemy.is_shielded:
                # Check impact angle relative to enemy facing angle
                impact_angle = math.atan2(self.y - enemy.y, self.x - enemy.x)
                angle_diff = abs(CGMath.normalize_angle(impact_angle - enemy.angle))
                if angle_diff < (math.pi * 0.45): # Hit front shield!
                    return "shield_blocked"

            # Normal hit
            enemy.take_damage(self.damage)
            return "hit"

        return None

    def render(self, canvas, camera):
        if not self.is_active:
            return

        xmin, ymin, xmax, ymax = camera.get_viewport_screen_bounds()

        # Tail and tip in world space
        tip_x, tip_y = self.x, self.y
        tail_x = self.x - math.cos(self.angle) * self.tail_len
        tail_y = self.y - math.sin(self.angle) * self.tail_len

        # Screen coordinates
        screen_pts = camera.world_to_screen([(tail_x, tail_y), (tip_x, tip_y)])
        p_tail, p_tip = screen_pts[0], screen_pts[1]

        # Cohen-Sutherland line clipping against camera viewport!
        c_bolt = CGMath.clip_line_cohen_sutherland(
            p_tail[0], p_tail[1], p_tip[0], p_tip[1],
            xmin, ymin, xmax, ymax
        )

        if c_bolt:
            canvas.create_line(c_bolt[0], c_bolt[1], c_bolt[2], c_bolt[3], fill="#38bdf8", width=4, capstyle="round", tags="player_bolt")
            canvas.create_line(c_bolt[0], c_bolt[1], c_bolt[2], c_bolt[3], fill="#ffffff", width=2, capstyle="round", tags="player_bolt_core")
