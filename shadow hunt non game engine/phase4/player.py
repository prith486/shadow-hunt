"""
Player Class for 2D Top-Down Stealth Game (Hunter Assassin inspired)
Strict Constraints:
- Green triangle (base size ~30 pixels) with one vertex acting as the 'head'.
- Instantly rotated using CGMath.rotate to point 'head' in direction of movement.
- Translated using CGMath.translate for positional movement.
- Starts with 100% health.
- Invisible circular hitbox generated via CGMath.bresenham_circle (with 1 - 2R parameter).
"""

import math
from typing import List, Tuple, Optional
from cg_math import CGMath, Point, Points
from fill_algo import draw_filled_polygon
import math as _math


class Player:
    """
    Player entity rendered as a green triangle with directional facing.
    All transformations strictly use CGMath (affine matrices & Bresenham's circle).
    """

    def __init__(self, x: float, y: float, speed: float = 4.5):
        self.x = float(x)
        self.y = float(y)
        self.speed = float(speed)

        # Health attributes
        self.max_health = 100.0
        self.health = 100.0

        # Base size ~30px: radius = 15px
        self.radius = 15.0

        # Facing direction in radians (0.0 = Facing Right along +X axis)
        self.angle = 0.0
        self._keep: List = []

        # Local canonical triangle coordinates centered at (0, 0):
        # Vertex 0: Head vertex pointing forward along +X
        # Vertex 1 & 2: Base rear corners
        # Size footprint: Length = 28px (-12 to +16), Width = 22px (-11 to +11)
        self.local_body_triangle: Points = [
            (16.0, 0.0),    # Head tip (forward)
            (-12.0, -11.0), # Rear-left
            (-6.0, 0.0),    # Inset notch for tactical chevron shape
            (-12.0, 11.0)   # Rear-right
        ]

        # Inner highlight triangle
        self.local_inner_triangle: Points = [
            (11.0, 0.0),
            (-7.0, -6.0),
            (-3.0, 0.0),
            (-7.0, 6.0)
        ]

        # Invisible circular hitbox points computed via Bresenham's Circle
        self.hitbox_points: List[Tuple[int, int]] = []
        self._update_hitbox()

    def _update_hitbox(self):
        """Generates invisible circular hitbox perimeter using CGMath.bresenham_circle."""
        self.hitbox_points = CGMath.bresenham_circle(self.x, self.y, self.radius)

    def get_transformed_vertices(self, local_pts: Points) -> Points:
        """
        Transforms local points to world coordinates:
        1. Rotate around local origin (0, 0) by self.angle using CGMath.rotate.
        2. Translate to world position (self.x, self.y) using CGMath.translate.
        """
        # Step 1: CGMath.rotate
        rotated = CGMath.rotate(local_pts, self.angle, 0.0, 0.0)
        # Step 2: CGMath.translate
        world_pts = CGMath.translate(rotated, self.x, self.y)
        return world_pts

    def set_facing(self, dx: float, dy: float):
        """
        Instantly rotates the triangle to point the 'head' vertex in
        the direction of movement (dx, dy).
        """
        if dx != 0.0 or dy != 0.0:
            self.angle = math.atan2(dy, dx)

    def move(self, dx: float, dy: float, map_engine) -> bool:
        """
        Moves the player using CGMath.translate with wall and door collision checks.
        Instantly rotates to face movement direction using CGMath.rotate.
        """
        if dx == 0.0 and dy == 0.0:
            return False

        # 1. Instantly orient head vertex towards movement vector
        self.set_facing(dx, dy)

        # 2. Axis-independent sliding collision check
        moved = False

        # Check X-axis movement
        target_x = self.x + dx
        if not map_engine.is_blocked(target_x, self.y, self.radius):
            # Translate position along X
            translated = CGMath.translate([(self.x, self.y)], dx, 0.0)
            self.x, self.y = translated[0]
            moved = True

        # Check Y-axis movement
        target_y = self.y + dy
        if not map_engine.is_blocked(self.x, target_y, self.radius):
            # Translate position along Y
            translated = CGMath.translate([(self.x, self.y)], 0.0, dy)
            self.x, self.y = translated[0]
            moved = True

        # 3. Update invisible circular hitbox
        if moved:
            self._update_hitbox()

        return moved

    def take_damage(self, amount: float):
        """Applies damage to player health."""
        self.health = max(0.0, self.health - amount)

    def heal(self, amount: float):
        """Heals player up to 100% max health."""
        self.health = min(self.max_health, self.health + amount)

    def is_alive(self) -> bool:
        return self.health > 0.0

    def render(self, canvas, show_hitbox: bool = False):
        """
        Renders the green player triangle and HUD elements on the tkinter.Canvas.
        """
        body_world = self.get_transformed_vertices(self.local_body_triangle)
        self._keep.clear()

        if show_hitbox:
            for hx, hy in self.hitbox_points[::3]:
                canvas.create_rectangle(hx, hy, hx + 2, hy + 2, fill="#38bdf8", outline="#38bdf8", tags="player_hitbox")

        # Soft stealth aura
        canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#062e20", outline="#059669", tags="player_aura"
        )

        # Operative Body Chevron Triangle via Ass4 Boundary Fill
        draw_filled_polygon(canvas, body_world, "#10b981", "#34d399", "player_body", self._keep, bypass_cache=True)

        inner_world = self.get_transformed_vertices(self.local_inner_triangle)
        draw_filled_polygon(canvas, inner_world, "#047857", "#6ee7b7", "player_core", self._keep, bypass_cache=True)

        # Head indicator
        head = body_world[0]
        canvas.create_oval(head[0] - 2.5, head[1] - 2.5, head[0] + 2.5, head[1] + 2.5,
                           fill="#ffffff", outline="#a7f3d0", tags="player_head")

        # Tactical mini HP bar
        bar_w, bar_h = 26.0, 3.5
        bx, by = self.x - bar_w / 2.0, self.y - self.radius - 8.0
        canvas.create_rectangle(bx, by, bx + bar_w, by + bar_h, fill="#1f2937", outline="#111827", tags="player_hp_bg")
        hp_pct = max(0.0, min(1.0, self.health / self.max_health))
        hp_color = "#22c55e" if hp_pct > 0.5 else ("#eab308" if hp_pct > 0.25 else "#ef4444")
        if hp_pct > 0:
            canvas.create_rectangle(bx, by, bx + bar_w * hp_pct, by + bar_h, fill=hp_color, outline="", tags="player_hp_fill")
