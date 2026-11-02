import math
from typing import List, Tuple
from cg_math import CGMath, Point, Points
from fill_algo import draw_filled_polygon, draw_bresenham_segment

class SecurityCamera:

    def __init__(self, x: float, y: float, base_angle: float, sweep_amplitude: float, sweep_speed: float=0.025, fov_angle: float=math.radians(65), cone_range: float=230.0):
        self.x = float(x)
        self.y = float(y)
        self.base_angle = float(base_angle)
        self.sweep_amplitude = float(sweep_amplitude)
        self.sweep_speed = float(sweep_speed)
        self.fov_angle = float(fov_angle)
        self.cone_range = float(cone_range)
        self.sweep_phase = 0.0
        self.current_angle = self.base_angle
        self.vision_polygon: Points = []
        self.is_alarm_triggered = False
        self._keep: List = []
        self._update_cone()

    def _update_cone(self):
        self.current_angle = self.base_angle + self.sweep_amplitude * math.sin(self.sweep_phase)
        self.vision_polygon = CGMath.create_cone_polygon(origin_x=self.x, origin_y=self.y, facing_angle=self.current_angle, fov_angle=self.fov_angle, length=self.cone_range, num_arc_steps=16)

    def update(self, player) -> bool:
        self.sweep_phase += self.sweep_speed
        self._update_cone()
        if not player.is_alive():
            return False
        detected = CGMath.point_in_polygon(player.x, player.y, self.vision_polygon)
        if detected:
            self.is_alarm_triggered = True
        return detected

    def render(self, canvas, alarm_active: bool=False):
        self._keep.clear()
        cone_fill = '#ef4444' if alarm_active or self.is_alarm_triggered else '#00e5ff'
        cone_outline = '#f87171' if alarm_active or self.is_alarm_triggered else '#38bdf8'
        cone_pts = [coord for pt in self.vision_polygon for coord in pt]
        canvas.create_polygon(cone_pts, fill=cone_fill, outline=cone_outline, stipple='gray25', tags='camera_cone')
        mount_r = 12.0
        mount = [(self.x + mount_r * math.cos(2 * math.pi * i / 16), self.y + mount_r * math.sin(2 * math.pi * i / 16)) for i in range(16)]
        draw_filled_polygon(canvas, mount, '#1e293b', '#475569', 'camera_mount', self._keep)
        lens_len = 16.0
        lx = self.x + lens_len * math.cos(self.current_angle)
        ly = self.y + lens_len * math.sin(self.current_angle)
        canvas.create_line(self.x, self.y, lx, ly, fill='#94a3b8', width=4, tags='camera_lens')
        led_color = '#ef4444' if alarm_active or self.is_alarm_triggered else '#22c55e'
        canvas.create_oval(self.x - 3.0, self.y - 3.0, self.x + 3.0, self.y + 3.0, fill=led_color, outline='#ffffff', tags='camera_led')
