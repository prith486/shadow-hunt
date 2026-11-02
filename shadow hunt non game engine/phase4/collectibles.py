import math
from typing import List, Tuple, Optional
from cg_math import CGMath, Point, Points
from fill_algo import draw_filled_polygon

class FloatingText:

    def __init__(self, x: float, y: float, text: str, color: str='#facc15', duration_frames: int=60):
        self.x = float(x)
        self.y = float(y)
        self.text = text
        self.color = color
        self.life = duration_frames
        self.max_life = duration_frames
        self.vy = -1.4

    def update(self) -> bool:
        self.y += self.vy
        self.life -= 1
        return self.life > 0

    def render(self, canvas):
        font_size = 11 if self.life > 15 else 9
        canvas.create_text(self.x + 1, self.y + 1, text=self.text, fill='#000000', font=('Consolas', font_size, 'bold'), tags='floating_text_shadow')
        canvas.create_text(self.x, self.y, text=self.text, fill=self.color, font=('Consolas', font_size, 'bold'), tags='floating_text')

class Coin:

    def __init__(self, x: float, y: float, radius: float=10.0):
        self.x = float(x)
        self.y = float(y)
        self.base_radius = float(radius)
        self.pulse_phase = 0.0
        self.pulse_speed = 0.08
        self.base_polygon: Points = []
        num_segments = 16
        for i in range(num_segments):
            ang = 2.0 * math.pi / num_segments * i
            px = self.x + self.base_radius * math.cos(ang)
            py = self.y + self.base_radius * math.sin(ang)
            self.base_polygon.append((px, py))
        self.current_polygon: Points = list(self.base_polygon)
        self.current_aura_polygon: Points = list(self.base_polygon)
        self.current_scale = 1.0
        self._keep: List = []

    def update(self):
        self.pulse_phase += self.pulse_speed
        self.current_scale = round(1.0 + 0.18 * math.sin(self.pulse_phase), 2)
        self.current_polygon = CGMath.scale(self.base_polygon, self.current_scale, self.x, self.y)
        aura_scale = self.current_scale * 1.35
        self.current_aura_polygon = CGMath.scale(self.base_polygon, aura_scale, self.x, self.y)

    def collides_with_player_bresenham(self, player_hitbox_pts: List[Tuple[int, int]], player_x: float, player_y: float, player_r: float) -> bool:
        center_dist = CGMath.distance(self.x, self.y, player_x, player_y)
        if center_dist > player_r + self.base_radius * self.current_scale + 4.0:
            return False
        coin_hit_r_sq = (self.base_radius * self.current_scale) ** 2
        for bx, by in player_hitbox_pts:
            d_sq = (bx - self.x) ** 2 + (by - self.y) ** 2
            if d_sq <= coin_hit_r_sq:
                return True
        return center_dist <= player_r + self.base_radius

    def render(self, canvas):
        r = self.base_radius * self.current_scale
        canvas.create_oval(self.x - r * 1.35, self.y - r * 1.35, self.x + r * 1.35, self.y + r * 1.35, fill='#854d0e', outline='#ca8a04', stipple='gray25', tags='coin_glow')
        canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill='#eab308', outline='#fef08a', width=2, tags='coin_body')
        hi_r = r * 0.4
        canvas.create_oval(self.x - hi_r, self.y - hi_r, self.x + hi_r, self.y + hi_r, fill='#facc15', outline='#ffffff', width=1, tags='coin_inner')

class HealthKit:

    def __init__(self, x: float, y: float, size: float=20.0):
        self.x = float(x)
        self.y = float(y)
        self.size = float(size)
        self.radius = self.size / 2.0
        self.pulse_phase = 0.0
        self.pulse_speed = 0.05
        hw = 2.5
        hs = 7.0
        self.base_plus: Points = [(self.x - hw, self.y - hs), (self.x + hw, self.y - hs), (self.x + hw, self.y - hw), (self.x + hs, self.y - hw), (self.x + hs, self.y + hw), (self.x + hw, self.y + hw), (self.x + hw, self.y + hs), (self.x - hw, self.y + hs), (self.x - hw, self.y + hw), (self.x - hs, self.y + hw), (self.x - hs, self.y - hw), (self.x - hw, self.y - hw)]
        s = self.radius
        self.base_box: Points = [(self.x - s, self.y - s), (self.x + s, self.y - s), (self.x + s, self.y + s), (self.x - s, self.y + s)]
        self.current_plus = list(self.base_plus)
        self.current_box = list(self.base_box)
        self.current_scale = 1.0
        self._keep: List = []

    def update(self):
        self.pulse_phase += self.pulse_speed
        self.current_scale = round(1.0 + 0.1 * math.sin(self.pulse_phase), 2)
        self.current_plus = CGMath.scale(self.base_plus, self.current_scale, self.x, self.y)
        self.current_box = CGMath.scale(self.base_box, self.current_scale, self.x, self.y)

    def collides_with_player_bresenham(self, player_hitbox_pts: List[Tuple[int, int]], player_x: float, player_y: float, player_r: float) -> bool:
        center_dist = CGMath.distance(self.x, self.y, player_x, player_y)
        if center_dist > player_r + self.radius * self.current_scale + 4.0:
            return False
        kit_r_sq = (self.radius * self.current_scale) ** 2
        for bx, by in player_hitbox_pts:
            d_sq = (bx - self.x) ** 2 + (by - self.y) ** 2
            if d_sq <= kit_r_sq:
                return True
        return center_dist <= player_r + self.radius

    def render(self, canvas):
        s = self.radius * self.current_scale
        canvas.create_rectangle(self.x - s, self.y - s, self.x + s, self.y + s, fill='#f8fafc', outline='#cbd5e1', width=2, tags='medkit_box')
        pw = s * 0.35
        ph = s * 0.75
        canvas.create_rectangle(self.x - pw, self.y - ph, self.x + pw, self.y + ph, fill='#ef4444', outline='', tags='medkit_plus')
        canvas.create_rectangle(self.x - ph, self.y - pw, self.x + ph, self.y + pw, fill='#ef4444', outline='', tags='medkit_plus')

class CollectibleManager:

    def __init__(self):
        self.coins: List[Coin] = []
        self.health_kits: List[HealthKit] = []
        self.announcements: List[FloatingText] = []

    def populate_map(self, map_engine):
        ox = map_engine.ox
        oy = map_engine.oy
        wt = map_engine.WALL_THICKNESS
        pw = map_engine.PASSAGE_WIDTH
        bs = map_engine.BOX_SIZE
        col_centers = [ox + wt + pw / 2.0, ox + wt + pw + bs + pw / 2.0, ox + wt + 2 * pw + 2 * bs + pw / 2.0, ox + wt + 3 * pw + 3 * bs + pw / 2.0]
        row_centers = [oy + wt + pw / 2.0, oy + wt + pw + bs + pw / 2.0, oy + wt + 2 * pw + 2 * bs + pw / 2.0]
        box_col_centers = [ox + wt + pw + bs / 2.0, ox + wt + 2 * pw + 1.5 * bs, ox + wt + 3 * pw + 2.5 * bs]
        coin_positions = [(box_col_centers[0], row_centers[0]), (box_col_centers[1], row_centers[0]), (box_col_centers[2], row_centers[0]), (col_centers[3], row_centers[1]), (box_col_centers[0], row_centers[2]), (box_col_centers[1], row_centers[2]), (box_col_centers[2], row_centers[2])]
        for cx, cy in coin_positions:
            self.coins.append(Coin(cx, cy, radius=10.0))
        medkit_positions = [(col_centers[0], row_centers[1]), (col_centers[1], row_centers[1]), (col_centers[2], row_centers[1])]
        for mx, my in medkit_positions:
            self.health_kits.append(HealthKit(mx, my, size=20.0))

    def update_and_collide(self, player) -> Tuple[int, float]:
        score_gained = 0
        hp_healed = 0.0
        remaining_coins: List[Coin] = []
        for coin in self.coins:
            coin.update()
            if coin.collides_with_player_bresenham(player.hitbox_points, player.x, player.y, player.radius):
                score_gained += 10
                self.announcements.append(FloatingText(coin.x, coin.y - 12.0, '+10 SCORE', color='#facc15', duration_frames=60))
            else:
                remaining_coins.append(coin)
        self.coins = remaining_coins
        remaining_kits: List[HealthKit] = []
        for kit in self.health_kits:
            kit.update()
            if kit.collides_with_player_bresenham(player.hitbox_points, player.x, player.y, player.radius):
                heal_amount = 15.0
                player.heal(heal_amount)
                hp_healed += heal_amount
                self.announcements.append(FloatingText(kit.x, kit.y - 12.0, '+15% HP', color='#22c55e', duration_frames=60))
            else:
                remaining_kits.append(kit)
        self.health_kits = remaining_kits
        self.announcements = [a for a in self.announcements if a.update()]
        return (score_gained, hp_healed)

    def render(self, canvas):
        for coin in self.coins:
            coin.render(canvas)
        for kit in self.health_kits:
            kit.render(canvas)
        for announcement in self.announcements:
            announcement.render(canvas)
