"""
Phase 3 ΓÇö Hunter Assassin
=========================
2D Transformation Demo + Playable Game

This phase builds on Phase 1 (map + camera) and Phase 2
(player, enemies, HUD, FOV) by adding the 2D transformation
system from phase3core.cpp, translated to Python.

NEW IN PHASE 3
--------------
- transforms.py  : identity / multiply_matrix / translation_matrix /
                   scaling_matrix / rotation_matrix /
                   apply_transformation / build_composite
- Player movement via Translation Matrix
- Enemy patrol    via Translation Matrix
- Enemy rotation  via Rotation Matrix
- Enemy body/FOV drawn by applying Rotation + Translation matrices
- Interactive pre-game menu:
    Enter any polygon, choose Row/Column, apply T/S/R/Composite,
    see original (white) + transformed (red) drawn with Bresenham.
- Game HUD shows active transformation name each frame.

Controls (Game)
---------------
  W / A / S / D  or  Arrow Keys  ΓÇö Move player
  ESC                            ΓÇö Quit
"""

import sys
import pygame
import pygame

from game_map   import GameMap, MAP_WIDTH, MAP_HEIGHT, CELL_SIZE
from entities   import Player, Enemy
from graphics   import bresenham_line
from transforms import (
    translation_matrix,
    scaling_matrix,
    rotation_matrix,
    build_composite,
    apply_transformation,
    print_matrix,
    print_points,
    identity,
    run_interactive_tsr_demo,
)





# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
RED   = (200,  50,  50)
BLACK = (  0,   0,   0)


# ============================================================
# DRAW HUD
#
# Carries forward Phase 2 HUD + adds transformation label.
# All lines drawn via bresenham_line (no pygame.draw shortcuts
# for game objects).
# ============================================================

def draw_hud(screen, player, enemies, rep_type):

    font = pygame.font.SysFont("Consolas", 14, bold=True)

    # --------------------------------------------------------
    # HEALTH TEXT
    # --------------------------------------------------------

    health_text = font.render(
        f"HEALTH: {int(player.health)}%", True, WHITE
    )
    screen.blit(health_text, (15, 10))

    # --------------------------------------------------------
    # HEALTH BAR FRAME  (Bresenham lines)
    # --------------------------------------------------------

    bresenham_line(screen, 120, 12, 220, 12, WHITE)
    bresenham_line(screen, 220, 12, 220, 22, WHITE)
    bresenham_line(screen, 220, 22, 120, 22, WHITE)
    bresenham_line(screen, 120, 22, 120, 12, WHITE)

    # --------------------------------------------------------
    # HEALTH BAR FILL
    # --------------------------------------------------------

    fill_width = int(player.health)

    for y in range(14, 21):
        if fill_width > 0:
            bresenham_line(screen, 121, y, 120 + fill_width, y, WHITE)

    # --------------------------------------------------------
    # DETECTION STATUS
    # --------------------------------------------------------

    any_detected = any(e.is_player_detected for e in enemies)

    status_str = (
        "STATUS: ALERT - PLAYER DETECTED!"
        if any_detected else
        "STATUS: CLEAR"
    )

    status_text = font.render(status_str, True, WHITE)
    screen.blit(status_text, (250, 10))

    # --------------------------------------------------------
    # ACTIVE TRANSFORMATION LABEL  (Phase 3 addition)
    # --------------------------------------------------------

    rep_str  = "Row" if rep_type == 1 else "Column"

    tf_label = font.render(
        f"TRANSFORM: {player.current_transform}  |  REP: {rep_str} Matrix",
        True, WHITE
    )
    screen.blit(tf_label, (15, 30))





# ============================================================
# GAME LOOP
# ============================================================

def run_game(screen, clock, rep_type):
    """
    Full game combining Phase 1 + Phase 2 + Phase 3 gameplay.

    Player and enemies now use transformation matrices
    (translation, rotation) for all movement and drawing.
    """

    game_map = GameMap()

    player = Player(1.5 * CELL_SIZE, 1.5 * CELL_SIZE)

    # --------------------------------------------------------
    # ENEMIES  (same positions as Phase 2)
    # --------------------------------------------------------

    enemies = [
        Enemy(
            12.5 * CELL_SIZE,
            5.5  * CELL_SIZE,
            facing_angle_deg = 180,
            sight_radius     = 110
        ),
        Enemy(
            8.5  * CELL_SIZE,
            14.5 * CELL_SIZE,
            facing_angle_deg = 270,
            sight_radius     = 100
        ),
        Enemy(
            25.5 * CELL_SIZE,
            8.5  * CELL_SIZE,
            facing_angle_deg = 90,
            sight_radius     = 120
        ),
    ]

    # --------------------------------------------------------
    # SET PATROL WAYPOINTS
    #
    # Each enemy patrols between two world positions.
    # The patrol is driven by translation matrices each frame.
    # --------------------------------------------------------

    enemies[0].patrol_bx = 20.5 * CELL_SIZE
    enemies[0].patrol_by =  5.5 * CELL_SIZE

    # Enemy 1: patrol horizontally along row 14 (cols 4.5 <-> 8.5)
    # Row 14 is a long clear corridor ΓÇö all cells walkable between these cols.
    # OLD (broken): col 8 -> row 8 ΓÇö vertical path crossed 4 wall cells
    enemies[1].patrol_bx =  4.5 * CELL_SIZE
    enemies[1].patrol_by = 14.5 * CELL_SIZE

    # Enemy 2: patrol horizontally along row 8 within the valid stretch (cols 22.5 <-> 25.5)
    # Row 8 has a wall gap at cols 27-29, so patrol stays left of it.
    # OLD (broken): col 25 -> col 32 ΓÇö path crossed wall cells at cols 27, 28, 29
    enemies[2].patrol_bx = 22.5 * CELL_SIZE
    enemies[2].patrol_by =  8.5 * CELL_SIZE

    # --------------------------------------------------------
    # MAIN GAME LOOP
    # --------------------------------------------------------

    running     = True
    grace_frames = 120    # 2-second invincibility at game start (60 fps)

    while running:

        # ----------------------------------------------------
        # EVENTS
        # ----------------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ----------------------------------------------------
        # UPDATE PLAYER  (Translation Matrix)
        # ----------------------------------------------------

        keys = pygame.key.get_pressed()
        player.update(keys, game_map, rep_type)

        # ----------------------------------------------------
        # UPDATE ENEMIES
        #   - Patrol via Translation Matrix
        #   - Rotate facing via Rotation Matrix
        #   - Detect player (same as Phase 2)
        # ----------------------------------------------------

        for enemy in enemies:

            enemy.update_patrol(rep_type, game_map)
            enemy.update_rotation(rep_type)

            detected = enemy.update_detection(player)

            if detected and grace_frames <= 0:
                player.health = max(0.0, player.health - 0.2)

        # Tell the player whether any enemy is currently watching them.
        # This flag drives the scaling_matrix pulse in Player.draw().
        player.is_detected = any(e.is_player_detected for e in enemies)

        if grace_frames > 0:
            grace_frames -= 1

        # ----------------------------------------------------
        # COIN PICKUPS  (same as Phase 2)
        # ----------------------------------------------------

        player_r = player.radius

        game_map.coins = [
            (cx, cy) for cx, cy in game_map.coins
            if (cx - player.x) ** 2 + (cy - player.y) ** 2
               > (player_r + 4) ** 2
        ]

        # ----------------------------------------------------
        # HEALTH KIT PICKUPS  (same as Phase 2)
        # ----------------------------------------------------

        new_health_kits = []

        for hx, hy in game_map.health_kits:

            if (hx - player.x) ** 2 + (hy - player.y) ** 2 \
               <= (player_r + 8) ** 2:

                player.health = min(100.0, player.health + 30.0)

            else:
                new_health_kits.append((hx, hy))

        game_map.health_kits = new_health_kits

        # ----------------------------------------------------
        # GAME OVER CHECK
        # ----------------------------------------------------

        if player.health <= 0:
            print("\nGAME OVER ΓÇö Player health reached 0.")
            running = False

        # ----------------------------------------------------
        # RENDER
        # ----------------------------------------------------

        # game_map.draw() handles its own lock/unlock internally.
        game_map.draw(screen)

        # Lock once for all entity pixel drawing (Bresenham/circle set_at calls)
        screen.lock()
        player.draw(screen, rep_type)
        for enemy in enemies:
            enemy.draw(screen, rep_type)
        screen.unlock()

        # HUD uses surface.blit() for text ΓÇö must be done AFTER unlock
        draw_hud(screen, player, enemies, rep_type)

        pygame.display.flip()
        clock.tick(60)


# ============================================================
# ENTRY POINT
# ============================================================

def main():

    pygame.init()

    print("\n" + "=" * 65)
    print("   HUNTER ASSASSIN — PHASE 3: 2D TRANSFORMATION SUITE")
    print("=" * 65)
    print("1. Interactive 2D Transformation Visualizer (TSR & Composite)")
    print("2. Launch Hunter Assassin Game Directly")
    print("-" * 65)
    mode_choice = input("Enter choice [1=TSR Demo, 2=Game, default: 1]: ").strip()

    if mode_choice != "2":
        rep_type = run_interactive_tsr_demo(standalone=False)
        print("\nProceed to Hunter Assassin Game? (Y/N) [default: Y]: ", end="", flush=True)
        proceed = input().strip().lower()
        if proceed in ("n", "no", "q", "quit", "exit"):
            print("Exiting.")
            pygame.quit()
            sys.exit()
    else:
        rep_type = 2

    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
    pygame.display.set_caption(
        "Hunter Assassin — Phase 3: 2D Transformations"
    )

    clock = pygame.time.Clock()

    # --------------------------------------------------------
    # Start the actual game with the chosen rep_type
    # --------------------------------------------------------

    run_game(screen, clock, rep_type)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
