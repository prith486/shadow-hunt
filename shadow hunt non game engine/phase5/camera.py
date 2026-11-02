from typing import Tuple
from cg_math import CGMath, Point, Points

class Camera:

    def __init__(self, screen_offset_x: float, screen_offset_y: float, viewport_w: float=720.0, viewport_h: float=520.0):
        self.screen_offset_x = float(screen_offset_x)
        self.screen_offset_y = float(screen_offset_y)
        self.viewport_w = float(viewport_w)
        self.viewport_h = float(viewport_h)
        self.x = 0.0
        self.y = 0.0

    def follow(self, target_x: float, target_y: float):
        self.x = target_x - self.viewport_w / 2.0
        self.y = target_y - self.viewport_h / 2.0

    def world_to_screen(self, pts: Points) -> Points:
        return CGMath.translate(pts, -self.x + self.screen_offset_x, -self.y + self.screen_offset_y)

    def world_to_screen_pt(self, wx: float, wy: float) -> Tuple[float, float]:
        pts = self.world_to_screen([(wx, wy)])
        return pts[0]

    def get_viewport_screen_bounds(self) -> Tuple[float, float, float, float]:
        xmin = self.screen_offset_x
        ymin = self.screen_offset_y
        xmax = self.screen_offset_x + self.viewport_w
        ymax = self.screen_offset_y + self.viewport_h
        return (xmin, ymin, xmax, ymax)
