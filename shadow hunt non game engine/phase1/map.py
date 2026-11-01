import pygame

from graphics import bresenham_line, dda_line


# ============================================================
# MAP SETTINGS
# ============================================================

CELL_SIZE = 50

# Matrix = 20 rows x 36 columns
ROWS = 20
COLS = 36

MAP_WIDTH = COLS * CELL_SIZE
MAP_HEIGHT = ROWS * CELL_SIZE

# Wall thickness = 5 pixels
WALL_THICKNESS = 5


# ============================================================
# COLORS
# ============================================================

# ------------------------------------------------------------
# WIREFRAME COLORS
# ------------------------------------------------------------

WIREFRAME_COLOR = (200, 200, 200)
BACKGROUND_COLOR = (0, 0, 0)


# ------------------------------------------------------------
# DEBUG GRID
# ------------------------------------------------------------

GRID_COLOR = (185, 183, 177)


# ============================================================
# MAP MATRIX
#
# 0 = WALL / BLOCKED
# 1 = WALKABLE PATH
# ============================================================

MAP_MATRIX = [

    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],

    [0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0],

    [0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0],

    [0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,0,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0],

    [0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0],

    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],

    [0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0],

    [0,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,0],

    [0,1,1,1,1,1,0,0,1,1,1,1,0,1,0,0,1,1,1,1,0,0,1,0,1,1,1,0,0,0,1,1,1,1,1,0],

    [0,1,1,0,0,1,0,1,1,0,1,0,0,1,0,0,1,0,0,1,1,1,1,0,0,1,0,1,1,0,1,0,0,0,0,0],

    [0,0,1,0,0,1,0,0,0,0,1,0,0,1,1,1,1,0,0,1,0,0,1,0,0,1,0,0,1,1,1,0,0,0,0,0],

    [0,1,1,1,1,1,0,0,0,1,1,1,0,1,0,0,1,1,1,1,0,0,1,0,1,1,1,0,0,0,1,1,1,1,1,0],

    [0,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,0,1,0],

    [0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,0],

    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],

    [0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,0,1,1,0,1,0,1,1,0,0,1,0,0,0],

    [0,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,1,0,0,1,1,0,1,1,1,1,1,0,1,1,1,0,1,1,1,0],

    [0,1,0,1,0,1,0,1,0,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,0,1,0,1,0,1,0,1,0],

    [0,1,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,0,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,0],

    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]


# ============================================================
# GAME MAP
# ============================================================

class GameMap:

    def __init__(self):

        self.grid = MAP_MATRIX

        self.rows = ROWS
        self.cols = COLS

        # Wall boundaries
        self.wall_segments = []

        # 2-3 connected zero cells
        self.crates = []

        # Single isolated zero cells
        self.peach_blocks = []

        # Generate map objects
        self.generate_walls()
        self.generate_zero_objects()


    # ========================================================
    # CHECK WHETHER CELL IS WALL
    # ========================================================

    def is_wall(self, row, col):

        # Outside the map is also treated as wall
        if row < 0 or row >= self.rows:
            return True

        if col < 0 or col >= self.cols:
            return True

        return self.grid[row][col] == 0


    # ========================================================
    # GENERATE WALL BOUNDARIES
    # ========================================================

    def generate_walls(self):

        self.wall_segments.clear()

        for row in range(self.rows):

            for col in range(self.cols):

                # Only create wall boundaries around
                # walkable cells.

                if self.grid[row][col] != 1:
                    continue

                x = col * CELL_SIZE
                y = row * CELL_SIZE


                # ------------------------------------------------
                # TOP WALL
                # ------------------------------------------------

                if self.is_wall(row - 1, col):

                    self.wall_segments.append(
                        (
                            x,
                            y,
                            x + CELL_SIZE,
                            y
                        )
                    )


                # ------------------------------------------------
                # BOTTOM WALL
                # ------------------------------------------------

                if self.is_wall(row + 1, col):

                    self.wall_segments.append(
                        (
                            x,
                            y + CELL_SIZE,
                            x + CELL_SIZE,
                            y + CELL_SIZE
                        )
                    )


                # ------------------------------------------------
                # LEFT WALL
                # ------------------------------------------------

                if self.is_wall(row, col - 1):

                    self.wall_segments.append(
                        (
                            x,
                            y,
                            x,
                            y + CELL_SIZE
                        )
                    )


                # ------------------------------------------------
                # RIGHT WALL
                # ------------------------------------------------

                if self.is_wall(row, col + 1):

                    self.wall_segments.append(
                        (
                            x + CELL_SIZE,
                            y,
                            x + CELL_SIZE,
                            y + CELL_SIZE
                        )
                    )


    # ========================================================
    # GENERATE OBJECTS FROM ZERO CELLS
    #
    # SINGLE ZERO
    #       -> PEACH BLOCK
    #
    # 2 OR 3 CONNECTED ZEROS
    #       -> WOODEN CRATES
    #
    # 4+ CONNECTED ZEROS
    #       -> NORMAL WALL
    # ========================================================

    def generate_zero_objects(self):

        self.crates.clear()
        self.peach_blocks.clear()

        visited = set()


        for row in range(self.rows):

            for col in range(self.cols):

                # Only process zero cells
                if self.grid[row][col] != 0:
                    continue

                # Already processed
                if (row, col) in visited:
                    continue


                # ------------------------------------------------
                # FIND CONNECTED ZERO GROUP
                # ------------------------------------------------

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


                    # Up
                    stack.append((r - 1, c))

                    # Down
                    stack.append((r + 1, c))

                    # Left
                    stack.append((r, c - 1))

                    # Right
                    stack.append((r, c + 1))


                # ------------------------------------------------
                # OUTER BORDER
                #
                # Border zeros remain normal wall.
                # ------------------------------------------------

                touches_boundary = False


                for r, c in group:

                    if (
                        r == 0
                        or r == self.rows - 1
                        or c == 0
                        or c == self.cols - 1
                    ):

                        touches_boundary = True
                        break


                if touches_boundary:
                    continue


                # ------------------------------------------------
                # SINGLE ZERO
                # ------------------------------------------------

                if len(group) == 1:

                    r, c = group[0]

                    x = c * CELL_SIZE
                    y = r * CELL_SIZE


                    self.peach_blocks.append(
                        pygame.Rect(
                            x,
                            y,
                            CELL_SIZE,
                            CELL_SIZE
                        )
                    )


                # ------------------------------------------------
                # 2 OR 3 ZERO CELLS
                # ------------------------------------------------

                elif len(group) <= 3:

                    for r, c in group:

                        x = c * CELL_SIZE
                        y = r * CELL_SIZE


                        self.crates.append(
                            pygame.Rect(
                                x,
                                y,
                                CELL_SIZE,
                                CELL_SIZE
                            )
                        )


                # ------------------------------------------------
                # 4+ ZERO CELLS
                # ------------------------------------------------
                #
                # Nothing is added here.
                # They remain normal wall.
                # ------------------------------------------------

                else:

                    pass


    # ========================================================
    # DRAW FLOOR
    #
    # 1 = LIGHT GREY WALKABLE AREA
    # 0 = DARK BACKGROUND
    # ========================================================

    def draw_floor(self, screen):

        # Start with pure black background for wireframe mode
        screen.fill(BACKGROUND_COLOR)
        
        # Floor doesn't need to be drawn in wireframe, walls are sufficient!


    # ========================================================
    # DRAW WALL USING BRESENHAM
    #
    # WALL_THICKNESS = 5 pixels
    # ========================================================

    def draw_wall(
        self,
        screen,
        x1,
        y1,
        x2,
        y2
    ):

        half = WALL_THICKNESS // 2


        # ------------------------------------------------
        # HORIZONTAL WALL
        # ------------------------------------------------

        if y1 == y2:

            for offset in range(
                -half,
                half + 1
            ):

                bresenham_line(
                    screen,
                    x1,
                    y1 + offset,
                    x2,
                    y2 + offset,
                    WIREFRAME_COLOR
                )


        # ------------------------------------------------
        # VERTICAL WALL
        # ------------------------------------------------

        else:

            for offset in range(
                -half,
                half + 1
            ):

                bresenham_line(
                    screen,
                    x1 + offset,
                    y1,
                    x2 + offset,
                    y2,
                    WIREFRAME_COLOR
                )


    # ========================================================
    # DRAW ALL WALLS
    # ========================================================

    def draw_walls(self, screen):

        for x1, y1, x2, y2 in self.wall_segments:

            self.draw_wall(
                screen,
                x1,
                y1,
                x2,
                y2
            )


    # ========================================================
    # DRAW 50x50 WOODEN CRATE
    # ========================================================

    def draw_crate(self, screen, rect):

        x = rect.x
        y = rect.y

        w = rect.width
        h = rect.height

        # ------------------------------------------------
        # WIREFRAME BOX (using Bresenham)
        # ------------------------------------------------

        bresenham_line(screen, x, y, x + w, y, WIREFRAME_COLOR)
        bresenham_line(screen, x + w, y, x + w, y + h, WIREFRAME_COLOR)
        bresenham_line(screen, x + w, y + h, x, y + h, WIREFRAME_COLOR)
        bresenham_line(screen, x, y + h, x, y, WIREFRAME_COLOR)

        # ------------------------------------------------
        # X PATTERN
        # ------------------------------------------------

        bresenham_line(
            screen,
            x,
            y,
            x + w,
            y + h,
            WIREFRAME_COLOR
        )

        bresenham_line(
            screen,
            x + w,
            y,
            x,
            y + h,
            WIREFRAME_COLOR
        )


    # ========================================================
    # DRAW ALL CRATES
    # ========================================================

    def draw_crates(self, screen):

        for crate in self.crates:

            self.draw_crate(
                screen,
                crate
            )


    # ========================================================
    # DRAW SINGLE PEACH BLOCK
    #
    # EXACT SIZE = 50x50
    # ========================================================

    def draw_peach_block(self, screen, rect):

        x = rect.x
        y = rect.y

        w = rect.width
        h = rect.height

        # ------------------------------------------------
        # WIREFRAME BOX (using DDA)
        # ------------------------------------------------

        dda_line(screen, x, y, x + w, y, WIREFRAME_COLOR)
        dda_line(screen, x + w, y, x + w, y + h, WIREFRAME_COLOR)
        dda_line(screen, x + w, y + h, x, y + h, WIREFRAME_COLOR)
        dda_line(screen, x, y + h, x, y, WIREFRAME_COLOR)

        # ------------------------------------------------
        # CROSSHAIR (+) TEXTURE
        # ------------------------------------------------

        dda_line(
            screen,
            x + w // 2,
            y,
            x + w // 2,
            y + h,
            WIREFRAME_COLOR
        )

        dda_line(
            screen,
            x,
            y + h // 2,
            x + w,
            y + h // 2,
            WIREFRAME_COLOR
        )


    # ========================================================
    # DRAW ALL PEACH BLOCKS
    # ========================================================

    def draw_peach_blocks(self, screen):

        for block in self.peach_blocks:

            self.draw_peach_block(
                screen,
                block
            )


    # ========================================================
    # DEBUG GRID
    #
    # Useful while designing the map.
    # Keep disabled in normal gameplay.
    # ========================================================

    def draw_debug_grid(self, screen):

        for x in range(
            0,
            MAP_WIDTH + 1,
            CELL_SIZE
        ):

            bresenham_line(
                screen,
                x,
                0,
                x,
                MAP_HEIGHT,
                GRID_COLOR
            )


        for y in range(
            0,
            MAP_HEIGHT + 1,
            CELL_SIZE
        ):

            dda_line(
                screen,
                0,
                y,
                MAP_WIDTH,
                y,
                GRID_COLOR
            )


    # ========================================================
    # DRAW STATIC CHARACTER OUTLINE
    # ========================================================

    def draw_character(self, screen):
        
        # Draw a simple triangle-based character at the top-left (cell 1,1)
        # Center at x=75, y=75
        cx, cy = 75, 75

        # Character Body (using Bresenham)
        bresenham_line(screen, cx, cy - 15, cx + 15, cy + 15, WIREFRAME_COLOR)
        bresenham_line(screen, cx + 15, cy + 15, cx - 15, cy + 15, WIREFRAME_COLOR)
        bresenham_line(screen, cx - 15, cy + 15, cx, cy - 15, WIREFRAME_COLOR)

        # Character Weapon/Crosshair (using DDA)
        dda_line(screen, cx, cy - 15, cx, cy - 30, WIREFRAME_COLOR)
        dda_line(screen, cx - 5, cy - 25, cx + 5, cy - 25, WIREFRAME_COLOR)


    # ========================================================
    # DRAW COMPLETE MAP
    # ========================================================

    def draw(self, screen):

        # ------------------------------------------------
        # 1. FLOOR
        # ------------------------------------------------

        self.draw_floor(screen)


        # ------------------------------------------------
        # 2. WALLS
        # ------------------------------------------------

        self.draw_walls(screen)


        # ------------------------------------------------
        # 3. WOODEN CRATES
        # ------------------------------------------------

        self.draw_crates(screen)


        # ------------------------------------------------
        # 4. SINGLE ZERO PEACH BLOCKS
        # ------------------------------------------------

        self.draw_peach_blocks(screen)


        # ------------------------------------------------
        # 5. STATIC CHARACTER OUTLINE
        # ------------------------------------------------

        self.draw_character(screen)


        # ------------------------------------------------
        # DEBUG GRID
        # ------------------------------------------------
        #
        # Uncomment this only if you want to see
        # the 50x50 cell structure.
        #
        self.draw_debug_grid(screen)


    # ========================================================
    # GET COLLISION RECTANGLES
    # ========================================================

    def get_collision_rects(self):

        collision_rects = []


        # ------------------------------------------------
        # WALLS
        # ------------------------------------------------

        for x1, y1, x2, y2 in self.wall_segments:

            if y1 == y2:

                rect = pygame.Rect(
                    min(x1, x2),
                    y1 - WALL_THICKNESS // 2,
                    abs(x2 - x1),
                    WALL_THICKNESS
                )


            else:

                rect = pygame.Rect(
                    x1 - WALL_THICKNESS // 2,
                    min(y1, y2),
                    WALL_THICKNESS,
                    abs(y2 - y1)
                )


            collision_rects.append(rect)


        # ------------------------------------------------
        # WOODEN CRATES
        # ------------------------------------------------

        collision_rects.extend(
            self.crates
        )


        # ------------------------------------------------
        # PEACH BLOCKS
        # ------------------------------------------------

        collision_rects.extend(
            self.peach_blocks
        )


        return collision_rects
