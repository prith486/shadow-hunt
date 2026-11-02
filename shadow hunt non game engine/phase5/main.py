import tkinter as tk
import math
import random
from typing import Set, List, Optional
from cg_math import CGMath
from camera import Camera
from map_engine import MapEngine
from player import Player
from collectibles import CollectibleManager, FloatingText
from enemy import Enemy
from security_camera import SecurityCamera
from projectile import PlayerBolt
from live_clipping_visualizer import LiveClippingPanel

class GameApp:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title('SHADOW HUNT - Phase 5 (3-Level Tactical Campaign & Live Clipping Engine)')
        self.root.geometry('1360x840')
        self.root.resizable(False, False)
        self.root.configure(bg='#070a12')
        self.current_level = 0
        self.levels_count = 3
        self.score = 0
        self.show_hitbox = False
        self.game_over = False
        self.victory = False
        self.game_over_reason = ''
        self.alarm_active = False
        self.alarm_timer = 10.0
        self.alarm_flasher = 0.0
        self.player_bolts: List[PlayerBolt] = []
        self.shoot_cooldown = 0
        self.replay_btn_bounds = (380, 440, 560, 490)
        self.next_btn_bounds = (280, 440, 480, 490)
        self.replay_lvl_bounds = (500, 440, 700, 490)
        self.header_frame = tk.Frame(root, bg='#0d131f', height=54)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.title_label = tk.Label(self.header_frame, text='SHADOW HUNT', font=('Consolas', 13, 'bold'), fg='#10b981', bg='#0d131f')
        self.title_label.pack(side=tk.LEFT, padx=12, pady=8)
        self.level_label = tk.Label(self.header_frame, text='LVL 1/3', font=('Consolas', 11, 'bold'), fg='#a855f7', bg='#0d131f')
        self.level_label.pack(side=tk.LEFT, padx=6, pady=8)
        btn_box = tk.Frame(self.header_frame, bg='#0d131f')
        btn_box.pack(side=tk.LEFT, padx=4)
        self.btn_l1 = tk.Button(btn_box, text='L1', font=('Consolas', 8, 'bold'), fg='#ffffff', bg='#3b82f6', relief=tk.FLAT, padx=4, takefocus=False, command=lambda: self._select_level(0))
        self.btn_l1.pack(side=tk.LEFT, padx=2)
        self.btn_l2 = tk.Button(btn_box, text='L2', font=('Consolas', 8, 'bold'), fg='#ffffff', bg='#8b5cf6', relief=tk.FLAT, padx=4, takefocus=False, command=lambda: self._select_level(1))
        self.btn_l2.pack(side=tk.LEFT, padx=2)
        self.btn_l3 = tk.Button(btn_box, text='L3', font=('Consolas', 8, 'bold'), fg='#ffffff', bg='#ec4899', relief=tk.FLAT, padx=4, takefocus=False, command=lambda: self._select_level(2))
        self.btn_l3.pack(side=tk.LEFT, padx=2)
        self.health_label = tk.Label(self.header_frame, text='HP: 100%', font=('Consolas', 11, 'bold'), fg='#22c55e', bg='#0d131f')
        self.health_label.pack(side=tk.LEFT, padx=8, pady=8)
        self.score_label = tk.Label(self.header_frame, text='SCORE: 0', font=('Consolas', 11, 'bold'), fg='#facc15', bg='#0d131f')
        self.score_label.pack(side=tk.LEFT, padx=8, pady=8)
        self.enemy_label = tk.Label(self.header_frame, text='Targets: 2/2', font=('Consolas', 10, 'bold'), fg='#ef4444', bg='#0d131f')
        self.enemy_label.pack(side=tk.LEFT, padx=8, pady=8)
        self.items_label = tk.Label(self.header_frame, text='Coins: 7 | Meds: 3', font=('Consolas', 9), fg='#94a3b8', bg='#0d131f')
        self.items_label.pack(side=tk.LEFT, padx=8, pady=8)
        self.clip_btn = tk.Button(self.header_frame, text='📐 TOGGLE METHOD [C]', font=('Consolas', 9, 'bold'), fg='#070a12', bg='#22c55e', activebackground='#16a34a', padx=8, pady=2, relief=tk.FLAT, takefocus=False, command=self._toggle_clipping_method)
        self.clip_btn.pack(side=tk.RIGHT, padx=10, pady=8)
        self.security_label = tk.Label(self.header_frame, text='SECURE', font=('Consolas', 10, 'bold'), fg='#38bdf8', bg='#0d131f')
        self.security_label.pack(side=tk.RIGHT, padx=8, pady=8)
        self.content_container = tk.Frame(root, bg='#050811')
        self.content_container.pack(fill=tk.BOTH, expand=True)
        self.canvas_width = 980
        self.canvas_height = 730
        self.canvas = tk.Canvas(self.content_container, width=self.canvas_width, height=self.canvas_height, bg='#050811', highlightthickness=0, takefocus=True)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.live_clipping_panel = LiveClippingPanel(self.content_container, width=360, height=self.canvas_height, on_target_change=self._set_inspect_target)
        self.live_clipping_panel.frame.pack(side=tk.RIGHT, fill=tk.Y, padx=4, pady=2)
        self.inspect_target_mode = 1
        viewport_w, viewport_h = (760.0, 530.0)
        cam_offset_x = (self.canvas_width - viewport_w) / 2.0
        cam_offset_y = (self.canvas_height - viewport_h) / 2.0
        self.camera = Camera(screen_offset_x=cam_offset_x, screen_offset_y=cam_offset_y, viewport_w=viewport_w, viewport_h=viewport_h)
        self.keys_pressed: Set[str] = set()
        self.root.bind('<KeyPress>', self._on_key_press)
        self.root.bind('<KeyRelease>', self._on_key_release)
        self.canvas.bind('<Button-1>', self._on_canvas_click)
        self.footer_label = tk.Label(root, text='Controls: [WASD] Move | [SPACE/CLICK] Shoot Bolt | Click ANY colored element to inspect | [F] Slow-Mo Demo | [C] Toggle Method | [1-8/Tab] Targets | [R] Replay', font=('Consolas', 9, 'bold'), fg='#38bdf8', bg='#070a12')
        self.footer_label.pack(side=tk.BOTTOM, pady=4)
        self._reset_game(level_index=0)
        self.canvas.focus_set()
        self.update_loop()

    def _select_level(self, lvl_idx: int):
        self.keys_pressed.clear()
        self._reset_game(level_index=lvl_idx)
        self.canvas.focus_set()

    def _next_level(self):
        self.keys_pressed.clear()
        next_lvl = (self.current_level + 1) % self.levels_count
        self._reset_game(level_index=next_lvl)
        self.canvas.focus_set()

    def _reset_game(self, level_index: Optional[int]=None):
        if level_index is not None:
            self.current_level = max(0, min(level_index, self.levels_count - 1))
        self.keys_pressed.clear()
        self.player_bolts.clear()
        self.shoot_cooldown = 0
        self.game_over = False
        self.victory = False
        self.game_over_reason = ''
        self.alarm_active = False
        self.origin_x, self.origin_y = (60.0, 60.0)
        self.map_engine = MapEngine(origin_x=self.origin_x, origin_y=self.origin_y, level_index=self.current_level)
        self.alarm_timer = self.map_engine.level_data.alarm_seconds if self.map_engine.level_data else 10.0
        spawn_x, spawn_y = self.map_engine.level_data.player_spawn if self.map_engine.level_data else (115.0, 115.0)
        self.player = Player(spawn_x, spawn_y, speed=4.5)
        self.camera.follow(self.player.x, self.player.y)
        self.collectibles = CollectibleManager()
        self.collectibles.populate_map(self.map_engine)
        self.enemies: List[Enemy] = []
        if self.map_engine.level_data:
            for e_spec in self.map_engine.level_data.enemies:
                self.enemies.append(Enemy(path=list(e_spec['waypoints']), is_shielded=e_spec['is_shielded'], speed=e_spec['speed']))
        else:
            self.enemies.append(Enemy(path=[(220.0, 300.0), (600.0, 300.0)], is_shielded=False, speed=2.0))
        self.camera_sensors: List[SecurityCamera] = []
        if self.map_engine.level_data:
            for c_spec in self.map_engine.level_data.cameras:
                self.camera_sensors.append(SecurityCamera(x=c_spec['x'], y=c_spec['y'], base_angle=c_spec['base_angle'], sweep_amplitude=c_spec['sweep_amplitude'], sweep_speed=c_spec['sweep_speed'], cone_range=c_spec.get('cone_range', 230.0)))
        else:
            self.camera_sensors.append(SecurityCamera(x=self.origin_x + self.map_engine.room_w - 18.0, y=self.origin_y + 18.0, base_angle=2.45, sweep_amplitude=0.65, sweep_speed=0.022))
        lvl_name = self.map_engine.level_data.name if self.map_engine.level_data else f'Level {self.current_level + 1}'
        self.level_label.config(text=f'LVL {self.current_level + 1}/3: {lvl_name}')
        self.canvas.focus_set()

    def _fire_player_bolt(self, target_angle: Optional[float]=None):
        if not self.player.is_alive() or self.game_over or self.victory:
            return
        if self.shoot_cooldown > 0:
            return
        fire_angle = target_angle if target_angle is not None else self.player.angle
        self.player.angle = fire_angle
        self.player_bolts.append(PlayerBolt(self.player.x, self.player.y, fire_angle, speed=15.0, damage=25.0))
        self.shoot_cooldown = 12

    def _set_inspect_target(self, tid: int):
        self.inspect_target_mode = tid
        self.live_clipping_panel.set_target(tid, notify=False)

    def _toggle_clipping_method(self):
        new_m = 'Cohen-Sutherland' if self.live_clipping_panel.method_mode == 'Sutherland-Hodgman' else 'Sutherland-Hodgman'
        self.live_clipping_panel.set_method(new_m)
        self.canvas.focus_set()

    def _on_key_press(self, event):
        key = event.keysym.lower()
        self.keys_pressed.add(key)
        if key == 'h':
            self.show_hitbox = not self.show_hitbox
        elif key == 'r':
            self._reset_game()
        elif key == 'c':
            self._toggle_clipping_method()
        elif key == 'f':
            self.live_clipping_panel.trigger_slow_mo_demo()
        elif key in ('1', '2', '3', '4', '5', '6', '7', '8'):
            self._set_inspect_target(int(key))
        elif key == 'tab':
            next_t = self.inspect_target_mode % 8 + 1
            self._set_inspect_target(next_t)
        elif key == 'l':
            self._next_level()
        elif key == 'n' and self.victory:
            self._next_level()
        elif key == 'space':
            self._fire_player_bolt()

    def _on_key_release(self, event):
        self.keys_pressed.discard(event.keysym.lower())

    def _on_canvas_click(self, event):
        self.canvas.focus_set()
        if self.game_over:
            bx1, by1, bx2, by2 = self.replay_btn_bounds
            if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                self._reset_game()
        elif self.victory:
            if self.current_level < self.levels_count - 1:
                nx1, ny1, nx2, ny2 = self.next_btn_bounds
                if nx1 <= event.x <= nx2 and ny1 <= event.y <= ny2:
                    self._next_level()
                    return
                rx1, ry1, rx2, ry2 = self.replay_lvl_bounds
                if rx1 <= event.x <= rx2 and ny1 <= event.y <= ny2:
                    self._reset_game()
                    return
            else:
                bx1, by1, bx2, by2 = self.replay_btn_bounds
                if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                    self.score = 0
                    self._select_level(0)
        else:
            mx = self.camera.x + (event.x - self.camera.screen_offset_x)
            my = self.camera.y + (event.y - self.camera.screen_offset_y)
            if math.hypot(mx - self.player.x, my - self.player.y) <= self.player.radius + 12:
                self._set_inspect_target(1)
                return
            for idx, e in enumerate(self.enemies):
                if not e.is_alive:
                    continue
                if math.hypot(mx - e.x, my - e.y) <= e.radius + 15:
                    self._set_inspect_target(7 if e.is_shielded else 4)
                    return
                if CGMath.point_in_polygon(mx, my, e.vision_polygon):
                    self._set_inspect_target(2)
                    return
            for cam in self.camera_sensors:
                if math.hypot(mx - cam.x, my - cam.y) <= 25 or CGMath.point_in_polygon(mx, my, cam.vision_polygon):
                    self._set_inspect_target(3)
                    return
            if self.map_engine.exit_door:
                ed = self.map_engine.exit_door
                if ed.x1 <= mx <= ed.x2 and ed.y1 <= my <= ed.y2:
                    self._set_inspect_target(8)
                    return
            aim_angle = math.atan2(my - self.player.y, mx - self.player.x)
            self._fire_player_bolt(target_angle=aim_angle)
            self._set_inspect_target(1)

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
                dx *= 0.7071
                dy *= 0.7071
            dx *= self.player.speed
            dy *= self.player.speed
            self.player.move(dx, dy, self.map_engine)

    def _update_player_bolts(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        active_bolts = []
        for bolt in self.player_bolts:
            if not bolt.update(self.map_engine):
                continue
            hit_anything = False
            for enemy in self.enemies:
                res = bolt.check_enemy_hit(enemy)
                if res == 'hit':
                    hit_anything = True
                    self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 18.0, '-25 HP', color='#f97316'))
                    if not enemy.is_alive:
                        self.score += 150
                        self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 32.0, 'TARGET ELIMINATED! +150', color='#22c55e'))
                    break
                elif res == 'shield_blocked':
                    hit_anything = True
                    self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 18.0, 'SHIELD DEFLECT!', color='#38bdf8'))
                    break
            if not hit_anything and bolt.is_active:
                active_bolts.append(bolt)
        self.player_bolts = active_bolts

    def _update_camera_and_alarm(self):
        if self.game_over or self.victory:
            return
        any_camera_detected = False
        for cam in self.camera_sensors:
            if cam.update(self.player):
                any_camera_detected = True
        if any_camera_detected and (not self.alarm_active):
            self.alarm_active = True
            self.collectibles.announcements.append(FloatingText(self.player.x, self.player.y - 20.0, 'ALARM TRIGGERED!', color='#ef4444'))
            self.security_label.config(text='ALERT!', fg='#ef4444')
        if self.alarm_active:
            self.alarm_flasher += 0.15
            self.alarm_timer = max(0.0, self.alarm_timer - 1.0 / 60.0)
            if self.map_engine.exit_door and self.map_engine.exit_door.is_reached(self.player.x, self.player.y, self.player.radius):
                self.victory = True
                self.score += 250 * (self.current_level + 1)
            elif self.alarm_timer <= 0.0:
                self.game_over = True
                self.game_over_reason = f'LOCKDOWN SEALED - {int(self.map_engine.level_data.alarm_seconds)}s EVACUATION FAILED'
        all_enemies_dead = len(self.enemies) > 0 and all((not e.is_alive for e in self.enemies))
        if all_enemies_dead and (not self.victory):
            self.victory = True
            self.score += 500 * (self.current_level + 1)

    def _update_enemies_and_combat(self):
        if self.game_over or self.victory:
            return
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            event = enemy.update(self.player)
            if event == 'shot_player':
                if not self.player.is_alive():
                    self.game_over = True
                    self.game_over_reason = 'ELIMINATED IN COMBAT'
            elif event == 'pushed_player':
                self.collectibles.announcements.append(FloatingText(self.player.x, self.player.y - 15.0, 'BLOCKED BY SHIELD!', color='#f97316'))
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            dist = CGMath.distance(self.player.x, self.player.y, enemy.x, enemy.y)
            if dist < self.player.radius + enemy.radius + 6.0:
                if enemy.is_shielded:
                    dx = self.player.x - enemy.x
                    dy = self.player.y - enemy.y
                    approach_angle = math.atan2(dy, dx)
                    angle_diff = abs(CGMath.normalize_angle(approach_angle - enemy.angle))
                    if angle_diff > math.pi * 0.55:
                        enemy.take_damage(100.0)
                        self.score += 150
                        self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 20.0, 'BACKSTAB TAKEDOWN!', color='#10b981'))
                else:
                    enemy.take_damage(100.0)
                    self.score += 100
                    self.collectibles.announcements.append(FloatingText(enemy.x, enemy.y - 20.0, 'TAKEDOWN!', color='#10b981'))

    def render(self):
        self.canvas.delete('all')
        self.camera.follow(self.player.x, self.player.y)
        self.map_engine.render(self.canvas, self.camera, alarm_active=self.alarm_active)
        self.collectibles.render(self.canvas, self.camera)
        for cam in self.camera_sensors:
            cam.render(self.canvas, self.camera, alarm_active=self.alarm_active)
        for enemy in self.enemies:
            enemy.render(self.canvas, self.camera, show_hitbox=self.show_hitbox)
        for bolt in self.player_bolts:
            bolt.render(self.canvas, self.camera)
        if self.player.is_alive():
            self.player.render(self.canvas, self.camera, show_hitbox=self.show_hitbox)
        xmin, ymin, xmax, ymax = self.camera.get_viewport_screen_bounds()
        bounds = (xmin, ymin, xmax, ymax)
        self.canvas.create_rectangle(xmin, ymin, xmax, ymax, fill='', outline='#38bdf8', width=3, tags='viewport_frame')
        c_len = 16.0
        self.canvas.create_line(xmin, ymin, xmin + c_len, ymin, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmin, ymin, xmin, ymin + c_len, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmax, ymin, xmax - c_len, ymin, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmax, ymin, xmax, ymin + c_len, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmin, ymax, xmin + c_len, ymax, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmin, ymax, xmin, ymax - c_len, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmax, ymax, xmax - c_len, ymax, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_line(xmax, ymax, xmax, ymax - c_len, fill='#f59e0b', width=4, tags='corner_bracket')
        self.canvas.create_text(xmin + 180, ymin - 12, text=f'[ SUTHERLAND-HODGMAN & COHEN-SUTHERLAND CLIPPING VIEWPORT | LVL {self.current_level + 1} ]', fill='#38bdf8', font=('Consolas', 8, 'bold'))
        self.canvas.create_text(xmax - 110, ymin - 12, text=f'[{xmin:.0f}..{xmax:.0f}, {ymin:.0f}..{ymax:.0f}]', fill='#facc15', font=('Consolas', 8))
        if self.inspect_target_mode == 1:
            if self.player_bolts:
                bolt = self.player_bolts[-1]
                tail_x = bolt.x - math.cos(bolt.angle) * bolt.tail_len
                tail_y = bolt.y - math.sin(bolt.angle) * bolt.tail_len
                screen_pts = self.camera.world_to_screen([(tail_x, tail_y), (bolt.x, bolt.y)])
                self.live_clipping_panel.update_live_clipping(screen_pts, bounds, 'Player Laser Bolt (Flying Line)', '#38bdf8')
            else:
                facing_x = self.player.x + math.cos(self.player.angle) * 90.0
                facing_y = self.player.y + math.sin(self.player.angle) * 90.0
                screen_ray = self.camera.world_to_screen([(self.player.x, self.player.y), (facing_x, facing_y)])
                self.live_clipping_panel.update_live_clipping(screen_ray, bounds, 'Player Aim Ray (Cohen-Sutherland)', '#38bdf8')
        elif self.inspect_target_mode == 2 and self.enemies:
            alive_enemies = [e for e in self.enemies if e.is_alive]
            target_e = alive_enemies[0] if alive_enemies else self.enemies[0]
            cone_screen = self.camera.world_to_screen(target_e.vision_polygon)
            self.live_clipping_panel.update_live_clipping(cone_screen, bounds, 'Enemy FOV Vision Cone (Sutherland-Hodgman)', '#f59e0b')
        elif self.inspect_target_mode == 3 and self.camera_sensors:
            cam_screen = self.camera.world_to_screen(self.camera_sensors[0].vision_polygon)
            self.live_clipping_panel.update_live_clipping(cam_screen, bounds, 'Security Camera Sweep Cone (Sutherland-Hodgman)', '#06b6d4')
        elif self.inspect_target_mode == 4 and self.enemies:
            alive_enemies = [e for e in self.enemies if e.is_alive]
            target_e = alive_enemies[0] if alive_enemies else self.enemies[0]
            rotated_body = CGMath.rotate(target_e.local_triangle, target_e.angle, 0.0, 0.0)
            world_body = CGMath.translate(rotated_body, target_e.x, target_e.y)
            screen_body = self.camera.world_to_screen(world_body)
            self.live_clipping_panel.update_live_clipping(screen_body, bounds, 'Patrol Guard Body Triangle (Sutherland-Hodgman)', '#ef4444')
        elif self.inspect_target_mode == 5 and self.enemies:
            shooting_e = next((e for e in self.enemies if e.is_alive and e.laser_target is not None), None)
            if shooting_e is not None:
                screen_laser = self.camera.world_to_screen([(shooting_e.x, shooting_e.y), shooting_e.laser_target])
                self.live_clipping_panel.update_live_clipping(screen_laser, bounds, 'Enemy Sniper Laser Shot (Cohen-Sutherland)', '#f43f5e')
            else:
                target_e = self.enemies[0]
                lx = target_e.x + math.cos(target_e.angle) * 130.0
                ly = target_e.y + math.sin(target_e.angle) * 130.0
                screen_probe = self.camera.world_to_screen([(target_e.x, target_e.y), (lx, ly)])
                self.live_clipping_panel.update_live_clipping(screen_probe, bounds, 'Enemy Targeting Vector (Cohen-Sutherland)', '#f43f5e')
        elif self.inspect_target_mode == 6 and self.map_engine.boxes:
            box = self.map_engine.boxes[0]
            edge_screen = self.camera.world_to_screen([(box.x1, box.y1), (box.x2, box.y1)])
            self.live_clipping_panel.update_live_clipping(edge_screen, bounds, 'Obstacle Crate Top Edge (Cohen-Sutherland)', '#94a3b8')
        elif self.inspect_target_mode == 7 and self.enemies:
            shielded = next((e for e in self.enemies if e.is_alive and e.is_shielded), None)
            if shielded and len(shielded.local_shield_arc) > 1:
                rot_shield = CGMath.rotate(shielded.local_shield_arc, shielded.angle, 0.0, 0.0)
                world_shield = CGMath.translate(rot_shield, shielded.x, shielded.y)
                screen_shield = self.camera.world_to_screen(world_shield)
                chord = [screen_shield[0], screen_shield[-1]]
                self.live_clipping_panel.update_live_clipping(chord, bounds, 'Frontal Shield Arc Chord (Cohen-Sutherland)', '#00e5ff')
            else:
                target_e = self.enemies[0]
                cone_screen = self.camera.world_to_screen(target_e.vision_polygon)
                self.live_clipping_panel.update_live_clipping(cone_screen, bounds, 'Enemy Vision Cone (Sutherland-Hodgman)', '#f59e0b')
        elif self.inspect_target_mode == 8 and self.map_engine.exit_door:
            ed = self.map_engine.exit_door
            door_poly = [(ed.x1, ed.y1), (ed.x2, ed.y1), (ed.x2, ed.y2), (ed.x1, ed.y2)]
            door_screen = self.camera.world_to_screen(door_poly)
            self.live_clipping_panel.update_live_clipping(door_screen, bounds, 'Extraction Exit Pad (Sutherland-Hodgman)', '#22c55e')
        if self.game_over:
            self.canvas.create_rectangle(180, 240, 860, 520, fill='#0b0f19', outline='#ef4444', width=3)
            self.canvas.create_text(520, 290, text='G A M E   O V E R', fill='#ef4444', font=('Consolas', 24, 'bold'))
            self.canvas.create_text(520, 340, text=self.game_over_reason, fill='#ffffff', font=('Consolas', 12))
            bx1, by1, bx2, by2 = self.replay_btn_bounds
            self.canvas.create_rectangle(bx1, by1, bx2, by2, fill='#1e293b', outline='#ef4444', width=2)
            self.canvas.create_text((bx1 + bx2) / 2.0, (by1 + by2) / 2.0, text='[ REPLAY LEVEL ]', fill='#ffffff', font=('Consolas', 13, 'bold'))
        elif self.victory:
            border_c = '#22c55e'
            self.canvas.create_rectangle(180, 240, 860, 520, fill='#0b0f19', outline=border_c, width=3)
            if self.current_level < self.levels_count - 1:
                title_t = f'L E V E L   {self.current_level + 1}   C O M P L E T E !'
                sub_t = f'Sector Cleared! Proceed to Level {self.current_level + 2} or Replay'
                self.canvas.create_text(520, 290, text=title_t, fill=border_c, font=('Consolas', 22, 'bold'))
                self.canvas.create_text(520, 340, text=sub_t, fill='#ffffff', font=('Consolas', 12))
                nx1, ny1, nx2, ny2 = self.next_btn_bounds
                self.canvas.create_rectangle(nx1, ny1, nx2, ny2, fill='#15803d', outline=border_c, width=2)
                self.canvas.create_text((nx1 + nx2) / 2.0, (ny1 + ny2) / 2.0, text=f'[ NEXT LEVEL ({self.current_level + 2}) ]', fill='#ffffff', font=('Consolas', 12, 'bold'))
                rx1, ry1, rx2, ry2 = self.replay_lvl_bounds
                self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill='#1e293b', outline='#94a3b8', width=2)
                self.canvas.create_text((rx1 + rx2) / 2.0, (ry1 + ry2) / 2.0, text='[ REPLAY LEVEL ]', fill='#ffffff', font=('Consolas', 12, 'bold'))
            else:
                title_t = 'C A M P A I G N   V I C T O R Y !'
                sub_t = 'ALL 3 LEVELS CLEARED! Cyber Citadel Infiltration Mastered!'
                self.canvas.create_text(520, 290, text=title_t, fill='#facc15', font=('Consolas', 22, 'bold'))
                self.canvas.create_text(520, 340, text=sub_t, fill='#ffffff', font=('Consolas', 12))
                self.canvas.create_text(520, 380, text=f'FINAL SCORE: {self.score}', fill='#22c55e', font=('Consolas', 14, 'bold'))
                bx1, by1, bx2, by2 = self.replay_btn_bounds
                self.canvas.create_rectangle(bx1, by1, bx2, by2, fill='#15803d', outline='#22c55e', width=2)
                self.canvas.create_text((bx1 + bx2) / 2.0, (by1 + by2) / 2.0, text='[ REPLAY CAMPAIGN ]', fill='#ffffff', font=('Consolas', 12, 'bold'))
        hp_pct = max(0, int(self.player.health / self.player.max_health * 100))
        self.health_label.config(text=f'HP: {hp_pct}%')
        self.score_label.config(text=f'SCORE: {self.score}')
        alive_enemies = sum((1 for e in self.enemies if e.is_alive))
        total_enemies = len(self.enemies)
        self.enemy_label.config(text=f'Targets: {alive_enemies}/{total_enemies}')
        self.items_label.config(text=f'Coins: {len(self.collectibles.coins)} | Meds: {len(self.collectibles.health_kits)}')
        if not self.alarm_active:
            self.security_label.config(text='SECURE', fg='#38bdf8')
        else:
            self.security_label.config(text=f'ALARM: {self.alarm_timer:.1f}s', fg='#ef4444')

    def update_loop(self):
        self._process_player_movement()
        self._update_player_bolts()
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
