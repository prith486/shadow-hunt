import tkinter as tk
import math
import random
from typing import Set, List, Optional
from cg_math import CGMath, Point, Points
from map_engine import MapEngine
from player import Player
from collectibles import CollectibleManager, FloatingText
from enemy import Enemy
from security_camera import SecurityCamera
from fill_algo import draw_filled_polygon
from live_fill_visualizer import LivePolygonFillPanel

class GameApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('SHADOW HUNT - Hunter Assassin (Phase 4: Live Polygon Fill)')
        self.root.geometry('1320x820')
        self.root.resizable(False, False)
        self.root.configure(bg='#070a12')
        self.score = 0
        self.show_hitbox = False
        self.game_over = False
        self.victory = False
        self.game_over_reason = ''
        self.alarm_active = False
        self.alarm_timer = 10.0
        self.alarm_flasher = 0.0
        self.replay_btn_bounds = (400, 440, 580, 490)
        self._ui_keep: List = []
        self.header_frame = tk.Frame(root, bg='#0d131f', height=52)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.title_label = tk.Label(self.header_frame, text='SHADOW HUNT', font=('Consolas', 14, 'bold'), fg='#10b981', bg='#0d131f')
        self.title_label.pack(side=tk.LEFT, padx=16, pady=8)
        self.health_label = tk.Label(self.header_frame, text='HP: 100%', font=('Consolas', 11, 'bold'), fg='#22c55e', bg='#0d131f')
        self.health_label.pack(side=tk.LEFT, padx=10, pady=8)
        self.score_label = tk.Label(self.header_frame, text='SCORE: 0', font=('Consolas', 12, 'bold'), fg='#facc15', bg='#0d131f')
        self.score_label.pack(side=tk.LEFT, padx=12, pady=8)
        self.enemy_label = tk.Label(self.header_frame, text='Targets: 2/2', font=('Consolas', 10, 'bold'), fg='#ef4444', bg='#0d131f')
        self.enemy_label.pack(side=tk.LEFT, padx=10, pady=8)
        self.items_label = tk.Label(self.header_frame, text='Coins: 7 | MedKits: 3', font=('Consolas', 10), fg='#94a3b8', bg='#0d131f')
        self.items_label.pack(side=tk.LEFT, padx=10, pady=8)
        self.security_label = tk.Label(self.header_frame, text='Status: SECURE', font=('Consolas', 10, 'bold'), fg='#38bdf8', bg='#0d131f')
        self.security_label.pack(side=tk.RIGHT, padx=16, pady=8)
        self.content_container = tk.Frame(root, bg='#050811')
        self.content_container.pack(fill=tk.BOTH, expand=True)
        self.canvas_width = 980
        self.canvas_height = 710
        self.canvas = tk.Canvas(self.content_container, width=self.canvas_width, height=self.canvas_height, bg='#050811', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.live_fill_panel = LivePolygonFillPanel(self.content_container, width=340, height=self.canvas_height, on_target_change=self._set_inspect_target)
        self.live_fill_panel.frame.pack(side=tk.RIGHT, fill=tk.Y, padx=4, pady=2)
        self.inspect_target_mode = 1
        self.origin_x = (self.canvas_width - 770) / 2.0
        self.origin_y = (self.canvas_height - 550) / 2.0
        self.keys_pressed: Set[str] = set()
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.footer_label = tk.Label(root, text='Controls: [WASD] Move | Click ANY colored entity on canvas to inspect! | [F] Slow-Mo Fill Demo | [1-8/Tab] Targets | [H] Hitbox', font=('Consolas', 9, 'bold'), fg='#38bdf8', bg='#070a12')
        self.footer_label.pack(side=tk.BOTTOM, pady=4)
        self._reset_game()
        self.update_loop()

    def _reset_game(self):
        self.score = 0
        self.game_over = False
        self.victory = False
        self.game_over_reason = ''
        self.alarm_active = False
        self.alarm_timer = 10.0
        self.map_engine = MapEngine(origin_x=self.origin_x, origin_y=self.origin_y)
        spawn_x = self.origin_x + 5.0 + 50.0
        spawn_y = self.origin_y + 5.0 + 50.0
        self.player = Player(spawn_x, spawn_y, speed=7.0)
        self.collectibles = CollectibleManager()
        self.collectibles.populate_map(self.map_engine)
        ox, oy = (self.origin_x, self.origin_y)
        self.enemies: List[Enemy] = []
        patrol_bottom_y = oy + 5.0 + 100.0 + 120.0 + 100.0 + 120.0 + 50.0
        path_guard = [(ox + 160.0, patrol_bottom_y), (ox + 610.0, patrol_bottom_y)]
        self.guard_enemy = Enemy(path_guard, is_shielded=False, speed=2.0)
        self.enemies.append(self.guard_enemy)
        patrol_mid_y = oy + 5.0 + 100.0 + 120.0 + 50.0
        path_shielded = [(ox + 220.0, patrol_mid_y), (ox + 550.0, patrol_mid_y)]
        self.shield_enemy = Enemy(path_shielded, is_shielded=True, speed=1.8)
        self.enemies.append(self.shield_enemy)
        cam_x = ox + self.map_engine.room_w - 18.0
        cam_y = oy + 18.0
        self.camera = SecurityCamera(x=cam_x, y=cam_y, base_angle=2.45, sweep_amplitude=0.65, sweep_speed=0.022, fov_angle=math.radians(65), cone_range=235.0)

    def _set_inspect_target(self, tid: int):
        self.inspect_target_mode = tid
        self.live_fill_panel.highlight_button(tid)

    def _on_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        if key == 'h':
            self.show_hitbox = not self.show_hitbox
        elif key == 'r':
            self._reset_game()
        elif key == 'f':
            self.live_fill_panel.trigger_slow_mo_animation()
        elif key in ('1', '2', '3', '4', '5', '6', '7', '8'):
            self._set_inspect_target(int(key))
        elif key == 'tab':
            self._set_inspect_target(self.inspect_target_mode % 8 + 1)

    def _on_key_release(self, event):
        key = event.keysym.lower()
        self.keys_pressed.discard(key)

    def _on_canvas_click(self, event):
        if self.game_over or self.victory:
            bx1, by1, bx2, by2 = self.replay_btn_bounds
            if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                self._reset_game()
                return
        mx, my = (float(event.x), float(event.y))
        if self.player.is_alive() and CGMath.distance(mx, my, self.player.x, self.player.y) <= 35.0:
            self._set_inspect_target(1)
            return
        if hasattr(self, 'guard_enemy') and self.guard_enemy.is_alive and (CGMath.distance(mx, my, self.guard_enemy.x, self.guard_enemy.y) <= 30.0):
            self._set_inspect_target(2)
            return
        if hasattr(self, 'shield_enemy') and self.shield_enemy.is_alive and (CGMath.distance(mx, my, self.shield_enemy.x, self.shield_enemy.y) <= 30.0):
            self._set_inspect_target(3)
            return
        if hasattr(self, 'guard_enemy') and self.guard_enemy.is_alive and CGMath.point_in_polygon(mx, my, self.guard_enemy.vision_polygon):
            self._set_inspect_target(4)
            return
        if hasattr(self, 'camera') and CGMath.point_in_polygon(mx, my, self.camera.vision_polygon):
            self._set_inspect_target(5)
            return
        if any((CGMath.distance(mx, my, c.x, c.y) <= 22.0 for c in self.collectibles.coins)):
            self._set_inspect_target(6)
            return
        if any((CGMath.distance(mx, my, k.x, k.y) <= 22.0 for k in self.collectibles.health_kits)):
            self._set_inspect_target(7)
            return
        if self.map_engine.exit_door:
            ed = self.map_engine.exit_door
            if ed.x1 <= mx <= ed.x2 and ed.y1 <= my <= ed.y2:
                self._set_inspect_target(8)
                return

    def _process_player_movement(self):
        if not self.player.is_alive() or self.game_over or self.victory:
            return
        dx, dy = (0.0, 0.0)
        if 'w' in self.keys_pressed or 'up' in self.keys_pressed:
            dy -= 1.0
        if 's' in self.keys_pressed or 'down' in self.keys_pressed:
            dy += 1.0
        if 'a' in self.keys_pressed or 'left' in self.keys_pressed:
            dx -= 1.0
        if 'd' in self.keys_pressed or 'right' in self.keys_pressed:
            dx += 1.0
        if dx != 0.0 or dy != 0.0:
            if dx != 0.0 and dy != 0.0:
                inv_len = 1.0 / 1.41421356
                dx *= inv_len
                dy *= inv_len
            dx *= self.player.speed
            dy *= self.player.speed
            self.player.move(dx, dy, self.map_engine)

    def _update_camera_and_alarm(self):
        if self.game_over or self.victory:
            return
        cam_detected = self.camera.update(self.player)
        if cam_detected and (not self.alarm_active):
            self.alarm_active = True
            self.collectibles.announcements.append(FloatingText(self.player.x, self.player.y - 20.0, 'ALARM TRIGGERED!', color='#ef4444', duration_frames=80))
        if self.alarm_active:
            self.alarm_flasher += 0.15
            self.alarm_timer = max(0.0, self.alarm_timer - 1.0 / 60.0)
            if self.map_engine.exit_door and self.map_engine.exit_door.is_reached(self.player.x, self.player.y, self.player.radius):
                self.victory = True
                self.score += 200
                self.collectibles.announcements.append(FloatingText(self.player.x, self.player.y - 20.0, 'ESCAPED! +200', color='#22c55e', duration_frames=120))
            elif self.alarm_timer <= 0.0:
                self.game_over = True
                self.game_over_reason = 'LOCKDOWN SEALED - 10s EVACUATION FAILED'

    def _update_enemies_and_combat(self):
        if self.game_over or self.victory:
            return
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            event = enemy.update(self.player)
            if event == 'shot_player':
                dmg = int(enemy.damage_per_shot)
                self.collectibles.announcements.append(FloatingText(self.player.x, self.player.y - 16.0, f'-{dmg}% HP', color='#f43f5e', duration_frames=45))
                if not self.player.is_alive():
                    self.game_over = True
                    self.game_over_reason = 'KIA - OPERATIVE ELIMINATED BY ENEMY FIRE'
            contact = enemy.check_player_contact(self.player)
            if contact == 'kill':
                if enemy.is_shielded:
                    self.score += 100
                    self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 18.0, 'STEALTH TAKEDOWN! +100', color='#38bdf8', duration_frames=70))
                else:
                    self.score += 50
                    self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 18.0, 'ASSASSINATED! +50', color='#22c55e', duration_frames=60))
            elif contact == 'shield_blocked':
                self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 18.0, 'SHIELD DEFLECTED!', color='#00e5ff', duration_frames=35))
                push_dx = math.cos(enemy.angle) * 8.0
                push_dy = math.sin(enemy.angle) * 8.0
                self.player.move(push_dx, push_dy, self.map_engine)
        alive_enemies = sum((1 for e in self.enemies if e.is_alive))
        if alive_enemies == 0 and self.map_engine.exit_door and self.map_engine.exit_door.is_reached(self.player.x, self.player.y, self.player.radius):
            if not self.victory:
                self.victory = True
                self.score += 150

    def _render_glitch_timer(self):
        text = f'LOCKDOWN: {self.alarm_timer:05.2f}s'
        cx = self.canvas_width / 2.0
        cy = 44.0
        rx_jitter = random.uniform(-4.0, 4.0)
        ry_jitter = random.uniform(-1.5, 1.5)
        red_pos = CGMath.translate([(cx, cy)], rx_jitter, ry_jitter)[0]
        self.canvas.create_text(red_pos[0], red_pos[1], text=text, fill='#ff0055', font=('Consolas', 26, 'bold'), tags='glitch_r')
        cx_jitter = random.uniform(-4.0, 4.0)
        cy_jitter = random.uniform(-1.5, 1.5)
        cyan_pos = CGMath.translate([(cx, cy)], cx_jitter, cy_jitter)[0]
        self.canvas.create_text(cyan_pos[0], cyan_pos[1], text=text, fill='#00f0ff', font=('Consolas', 26, 'bold'), tags='glitch_c')
        yx_jitter = random.uniform(-2.0, 2.0)
        yy_jitter = random.uniform(-2.0, 2.0)
        yellow_pos = CGMath.translate([(cx, cy)], yx_jitter, yy_jitter)[0]
        self.canvas.create_text(yellow_pos[0], yellow_pos[1], text=text, fill='#facc15', font=('Consolas', 26, 'bold'), tags='glitch_y')
        wx_jitter = random.uniform(-0.8, 0.8)
        wy_jitter = random.uniform(-0.8, 0.8)
        white_pos = CGMath.translate([(cx, cy)], wx_jitter, wy_jitter)[0]
        self.canvas.create_text(white_pos[0], white_pos[1], text=text, fill='#ffffff', font=('Consolas', 26, 'bold'), tags='glitch_w')
        sub_text = '>> EVACUATE TO EXIT DOOR BEFORE TIME EXPIRES << '
        sub_pos = CGMath.translate([(cx, cy + 28.0)], random.uniform(-1.5, 1.5), 0.0)[0]
        self.canvas.create_text(sub_pos[0], sub_pos[1], text=sub_text, fill='#ef4444', font=('Consolas', 10, 'bold'), tags='glitch_sub')

    def _render_replay_button(self, is_victory: bool=False):
        bx1, by1, bx2, by2 = self.replay_btn_bounds
        btn_outline = '#22c55e' if is_victory else '#ef4444'
        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill='#1e293b', outline=btn_outline, width=2, tags='replay_btn')
        self.canvas.create_text((bx1 + bx2) / 2.0, (by1 + by2) / 2.0, text='[ REPLAY ]', fill='#ffffff', font=('Consolas', 13, 'bold'), tags='replay_btn_txt')

    def render(self):
        self.canvas.delete('all')
        self._ui_keep.clear()
        if self.alarm_active and (not (self.game_over or self.victory)):
            if math.sin(self.alarm_flasher) > 0.0:
                self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill='#3b0707', outline='', tags='alarm_strobe')
        self.map_engine.render(self.canvas, alarm_active=self.alarm_active)
        self.collectibles.render(self.canvas)
        self.camera.render(self.canvas, alarm_active=self.alarm_active)
        for enemy in self.enemies:
            enemy.render(self.canvas, show_hitbox=self.show_hitbox)
        if self.player.is_alive():
            self.player.render(self.canvas, show_hitbox=self.show_hitbox)
            if self.inspect_target_mode == 1:
                body_world = self.player.get_transformed_vertices(self.player.local_body_triangle)
                self.live_fill_panel.update_live_polygon(body_world, 'Player Operative (Chevron Triangle)', '#10b981', '#34d399')
            elif self.inspect_target_mode == 2 and hasattr(self, 'guard_enemy') and self.guard_enemy.is_alive:
                g = self.guard_enemy
                world_guard = CGMath.translate(CGMath.rotate(g.local_triangle, g.angle, 0.0, 0.0), g.x, g.y)
                self.live_fill_panel.update_live_polygon(world_guard, 'Patrol Guard Body (Red Triangle)', '#ef4444', '#f87171')
            elif self.inspect_target_mode == 3 and hasattr(self, 'shield_enemy') and self.shield_enemy.is_alive:
                s = self.shield_enemy
                world_shield = CGMath.translate(CGMath.rotate(s.local_triangle, s.angle, 0.0, 0.0), s.x, s.y)
                self.live_fill_panel.update_live_polygon(world_shield, 'Shielded Enforcer Body', '#dc2626', '#00e5ff')
            elif self.inspect_target_mode == 4 and hasattr(self, 'guard_enemy') and self.guard_enemy.is_alive and (len(self.guard_enemy.vision_polygon) >= 3):
                self.live_fill_panel.update_live_polygon(self.guard_enemy.vision_polygon, 'Enemy FOV Vision Cone (Amber)', '#d97706', '#f59e0b')
            elif self.inspect_target_mode == 5 and hasattr(self, 'camera') and (len(self.camera.vision_polygon) >= 3):
                self.live_fill_panel.update_live_polygon(self.camera.vision_polygon, 'Security Camera Vision Cone (Cyan)', '#0891b2', '#06b6d4')
            elif self.inspect_target_mode == 6 and len(self.collectibles.coins) > 0:
                self.live_fill_panel.update_live_polygon(self.collectibles.coins[0].base_polygon, 'Golden Coin (16-gon Circle)', '#eab308', '#facc15')
            elif self.inspect_target_mode == 7 and len(self.collectibles.health_kits) > 0:
                self.live_fill_panel.update_live_polygon(self.collectibles.health_kits[0].base_plus, 'Health Kit Plus Symbol (12-gon)', '#ef4444', '#ffffff')
            elif self.inspect_target_mode == 8 and self.map_engine.exit_door:
                ed = self.map_engine.exit_door
                exit_poly = [(ed.x1, ed.y1), (ed.x2, ed.y1), (ed.x2, ed.y2), (ed.x1, ed.y2)]
                self.live_fill_panel.update_live_polygon(exit_poly, 'Extraction Exit Door Pad (Emerald)', '#059669', '#22c55e')
            else:
                body_world = self.player.get_transformed_vertices(self.player.local_body_triangle)
                self.live_fill_panel.update_live_polygon(body_world, 'Player Operative', '#10b981', '#34d399')
        else:
            dead = [(self.player.x + 10 * math.cos(2 * math.pi * i / 12), self.player.y + 10 * math.sin(2 * math.pi * i / 12)) for i in range(12)]
            draw_filled_polygon(self.canvas, dead, '#450a0a', '#991b1b', 'player_dead', self._ui_keep)
            self.canvas.create_text(self.player.x, self.player.y, text='KIA', fill='#f87171', font=('Consolas', 9, 'bold'), tags='player_dead')
        if self.alarm_active and (not (self.game_over or self.victory)):
            self._render_glitch_timer()
        if self.game_over:
            self.canvas.create_rectangle(160, 240, 820, 520, fill='#0b0f19', outline='#ef4444', width=2, tags='modal_bg')
            self.canvas.create_text(490, 290, text='G A M E   O V E R', fill='#ef4444', font=('Consolas', 22, 'bold'), tags='modal_title')
            self.canvas.create_text(490, 340, text=self.game_over_reason, fill='#fca5a5', font=('Consolas', 12), tags='modal_reason')
            self.canvas.create_text(490, 385, text=f'Final Score: {self.score}', fill='#facc15', font=('Consolas', 14, 'bold'), tags='modal_score')
            self._render_replay_button(is_victory=False)
        elif self.victory:
            self.canvas.create_rectangle(160, 240, 820, 520, fill='#0b0f19', outline='#22c55e', width=2, tags='modal_bg')
            self.canvas.create_text(490, 290, text='M I S S I O N   S U C C E S S', fill='#22c55e', font=('Consolas', 22, 'bold'), tags='modal_title')
            self.canvas.create_text(490, 340, text='OPERATIVE ESCAPED EXTRACTION ZONE SAFELY', fill='#86efac', font=('Consolas', 12), tags='modal_reason')
            self.canvas.create_text(490, 385, text=f'Total Score: {self.score}', fill='#facc15', font=('Consolas', 14, 'bold'), tags='modal_score')
            self._render_replay_button(is_victory=True)
        hp_pct = max(0, int(self.player.health / self.player.max_health * 100))
        self.health_label.config(text=f'HP: {hp_pct}%', fg='#22c55e' if hp_pct > 50 else '#eab308' if hp_pct > 25 else '#ef4444')
        self.score_label.config(text=f'SCORE: {self.score}')
        alive_enemies = sum((1 for e in self.enemies if e.is_alive))
        self.enemy_label.config(text=f'Targets: {alive_enemies}/2', fg='#ef4444' if alive_enemies > 0 else '#22c55e')
        self.items_label.config(text=f'Coins: {len(self.collectibles.coins)} | MedKits: {len(self.collectibles.health_kits)}')
        if self.game_over:
            status_text = 'FAILED'
            status_color = '#ef4444'
        elif self.victory:
            status_text = 'ESCAPED'
            status_color = '#22c55e'
        elif self.alarm_active:
            status_text = f'LOCKDOWN ({self.alarm_timer:04.1f}s)'
            status_color = '#f43f5e'
        else:
            status_text = 'SECURE'
            status_color = '#38bdf8'
        self.security_label.config(text=f'Status: {status_text}', fg=status_color)

    def update_loop(self):
        self._process_player_movement()
        self.map_engine.update_doors(self.player.x, self.player.y)
        if not self.game_over and (not self.victory):
            score_earned, _ = self.collectibles.update_and_collide(self.player)
            self.score += score_earned
        self._update_camera_and_alarm()
        self._update_enemies_and_combat()
        self.render()
        self.root.after(16, self.update_loop)

def main():
    root = tk.Tk()
    app = GameApp(root)
    root.mainloop()
if __name__ == '__main__':
    main()
