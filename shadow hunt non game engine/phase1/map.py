import pygame
from graphics import bresenham_line, dda_line
CELL_SIZE = 50
ROWS = 20
COLS = 36
MAP_WIDTH = COLS * CELL_SIZE
MAP_HEIGHT = ROWS * CELL_SIZE
WALL_THICKNESS = 5
WIREFRAME_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)
GRID_COLOR = (185, 183, 177)
MAP_MATRIX = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0], [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0], [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0], [0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0], [0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0], [0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0], [0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0], [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0], [0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0], [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0], [0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0], [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

class GameMap:

    def __init__(self):
        self.grid = MAP_MATRIX
        self.rows = ROWS
        self.cols = COLS
        self.wall_segments = []
        self.crates = []
        self.peach_blocks = []
        self.generate_walls()
        self.generate_zero_objects()

    def is_wall(self, row, col):
        if row < 0 or row >= self.rows:
            return True
        if col < 0 or col >= self.cols:
            return True
        return self.grid[row][col] == 0

    def generate_walls(self):
        self.wall_segments.clear()
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != 1:
                    continue
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                if self.is_wall(row - 1, col):
                    self.wall_segments.append((x, y, x + CELL_SIZE, y))
                if self.is_wall(row + 1, col):
                    self.wall_segments.append((x, y + CELL_SIZE, x + CELL_SIZE, y + CELL_SIZE))
                if self.is_wall(row, col - 1):
                    self.wall_segments.append((x, y, x, y + CELL_SIZE))
                if self.is_wall(row, col + 1):
                    self.wall_segments.append((x + CELL_SIZE, y, x + CELL_SIZE, y + CELL_SIZE))

    def generate_zero_objects(self):
        self.crates.clear()
        self.peach_blocks.clear()
        visited = set()
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != 0:
                    continue
                if (row, col) in visited:
                    continue
                stack = [(row, col)]
                group = []
                while stack:
                    r, c = stack.pop()
                    if (r, c) in visited:
                        continue
                    if r < 0 or r >= self.rows:
                        continue
                    if c < 0 or c >= self.cols:
                        continue
                    if self.grid[r][c] != 0:
                        continue
                    visited.add((r, c))
                    group.append((r, c))
                    stack.append((r - 1, c))
                    stack.append((r + 1, c))
                    stack.append((r, c - 1))
                    stack.append((r, c + 1))
                touches_boundary = False
                for r, c in group:
                    if r == 0 or r == self.rows - 1 or c == 0 or (c == self.cols - 1):
                        touches_boundary = True
                        break
                if touches_boundary:
                    continue
                if len(group) == 1:
                    r, c = group[0]
                    x = c * CELL_SIZE
                    y = r * CELL_SIZE
                    self.peach_blocks.append(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
                elif len(group) <= 3:
                    for r, c in group:
                        x = c * CELL_SIZE
                        y = r * CELL_SIZE
                        self.crates.append(pygame.Rect(x, y, CELL_SIZE, CELL_SIZE))
                else:
                    pass

    def draw_floor(self, screen):
        screen.fill(BACKGROUND_COLOR)

    def draw_wall(self, screen, x1, y1, x2, y2):
        half = WALL_THICKNESS // 2
        if y1 == y2:
            for offset in range(-half, half + 1):
                bresenham_line(screen, x1, y1 + offset, x2, y2 + offset, WIREFRAME_COLOR)
        else:
            for offset in range(-half, half + 1):
                bresenham_line(screen, x1 + offset, y1, x2 + offset, y2, WIREFRAME_COLOR)

    def draw_walls(self, screen):
        for x1, y1, x2, y2 in self.wall_segments:
            self.draw_wall(screen, x1, y1, x2, y2)

    def draw_crate(self, screen, rect):
        x = rect.x
        y = rect.y
        w = rect.width
        h = rect.height
        bresenham_line(screen, x, y, x + w, y, WIREFRAME_COLOR)
        bresenham_line(screen, x + w, y, x + w, y + h, WIREFRAME_COLOR)
        bresenham_line(screen, x + w, y + h, x, y + h, WIREFRAME_COLOR)
        bresenham_line(screen, x, y + h, x, y, WIREFRAME_COLOR)
        bresenham_line(screen, x, y, x + w, y + h, WIREFRAME_COLOR)
        bresenham_line(screen, x + w, y, x, y + h, WIREFRAME_COLOR)

    def draw_crates(self, screen):
        for crate in self.crates:
            self.draw_crate(screen, crate)

    def draw_peach_block(self, screen, rect):
        x = rect.x
        y = rect.y
        w = rect.width
        h = rect.height
        dda_line(screen, x, y, x + w, y, WIREFRAME_COLOR)
        dda_line(screen, x + w, y, x + w, y + h, WIREFRAME_COLOR)
        dda_line(screen, x + w, y + h, x, y + h, WIREFRAME_COLOR)
        dda_line(screen, x, y + h, x, y, WIREFRAME_COLOR)
        dda_line(screen, x + w // 2, y, x + w // 2, y + h, WIREFRAME_COLOR)
        dda_line(screen, x, y + h // 2, x + w, y + h // 2, WIREFRAME_COLOR)

    def draw_peach_blocks(self, screen):
        for block in self.peach_blocks:
            self.draw_peach_block(screen, block)

    def draw_debug_grid(self, screen):
        for x in range(0, MAP_WIDTH + 1, CELL_SIZE):
            bresenham_line(screen, x, 0, x, MAP_HEIGHT, GRID_COLOR)
        for y in range(0, MAP_HEIGHT + 1, CELL_SIZE):
            dda_line(screen, 0, y, MAP_WIDTH, y, GRID_COLOR)

    def draw_character(self, screen):
        cx, cy = (75, 75)
        bresenham_line(screen, cx, cy - 15, cx + 15, cy + 15, WIREFRAME_COLOR)
        bresenham_line(screen, cx + 15, cy + 15, cx - 15, cy + 15, WIREFRAME_COLOR)
        bresenham_line(screen, cx - 15, cy + 15, cx, cy - 15, WIREFRAME_COLOR)
        dda_line(screen, cx, cy - 15, cx, cy - 30, WIREFRAME_COLOR)
        dda_line(screen, cx - 5, cy - 25, cx + 5, cy - 25, WIREFRAME_COLOR)

    def draw(self, screen):
        self.draw_floor(screen)
        self.draw_walls(screen)
        self.draw_crates(screen)
        self.draw_peach_blocks(screen)
        self.draw_character(screen)
        self.draw_debug_grid(screen)

    def get_collision_rects(self):
        collision_rects = []
        for x1, y1, x2, y2 in self.wall_segments:
            if y1 == y2:
                rect = pygame.Rect(min(x1, x2), y1 - WALL_THICKNESS // 2, abs(x2 - x1), WALL_THICKNESS)
            else:
                rect = pygame.Rect(x1 - WALL_THICKNESS // 2, min(y1, y2), WALL_THICKNESS, abs(y2 - y1))
            collision_rects.append(rect)
        collision_rects.extend(self.crates)
        collision_rects.extend(self.peach_blocks)
        return collision_rects
