import sys
import pygame
import pygame
from game_map import GameMap, MAP_WIDTH, MAP_HEIGHT, CELL_SIZE
from entities import Player, Enemy
from graphics import bresenham_line
from transforms import translation_matrix, scaling_matrix, rotation_matrix, build_composite, apply_transformation, print_matrix, print_points, identity, run_interactive_tsr_demo
WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLACK = (0, 0, 0)

def draw_hud(screen, player, enemies, rep_type):
    font = pygame.font.SysFont('Consolas', 14, bold=True)
    health_text = font.render(f'HEALTH: {int(player.health)}%', True, WHITE)
    screen.blit(health_text, (15, 10))
    bresenham_line(screen, 120, 12, 220, 12, WHITE)
    bresenham_line(screen, 220, 12, 220, 22, WHITE)
    bresenham_line(screen, 220, 22, 120, 22, WHITE)
    bresenham_line(screen, 120, 22, 120, 12, WHITE)
    fill_width = int(player.health)
    for y in range(14, 21):
        if fill_width > 0:
            bresenham_line(screen, 121, y, 120 + fill_width, y, WHITE)
    any_detected = any((e.is_player_detected for e in enemies))
    status_str = 'STATUS: ALERT - PLAYER DETECTED!' if any_detected else 'STATUS: CLEAR'
    status_text = font.render(status_str, True, WHITE)
    screen.blit(status_text, (250, 10))
    rep_str = 'Row' if rep_type == 1 else 'Column'
    tf_label = font.render(f'TRANSFORM: {player.current_transform}  |  REP: {rep_str} Matrix', True, WHITE)
    screen.blit(tf_label, (15, 30))

def run_game(screen, clock, rep_type):
    game_map = GameMap()
    player = Player(1.5 * CELL_SIZE, 1.5 * CELL_SIZE)
    enemies = [Enemy(12.5 * CELL_SIZE, 5.5 * CELL_SIZE, facing_angle_deg=180, sight_radius=110), Enemy(8.5 * CELL_SIZE, 14.5 * CELL_SIZE, facing_angle_deg=270, sight_radius=100), Enemy(25.5 * CELL_SIZE, 8.5 * CELL_SIZE, facing_angle_deg=90, sight_radius=120)]
    enemies[0].patrol_bx = 20.5 * CELL_SIZE
    enemies[0].patrol_by = 5.5 * CELL_SIZE
    enemies[1].patrol_bx = 4.5 * CELL_SIZE
    enemies[1].patrol_by = 14.5 * CELL_SIZE
    enemies[2].patrol_bx = 22.5 * CELL_SIZE
    enemies[2].patrol_by = 8.5 * CELL_SIZE
    running = True
    grace_frames = 120
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        keys = pygame.key.get_pressed()
        player.update(keys, game_map, rep_type)
        for enemy in enemies:
            enemy.update_patrol(rep_type, game_map)
            enemy.update_rotation(rep_type)
            detected = enemy.update_detection(player)
            if detected and grace_frames <= 0:
                player.health = max(0.0, player.health - 0.2)
        player.is_detected = any((e.is_player_detected for e in enemies))
        if grace_frames > 0:
            grace_frames -= 1
        player_r = player.radius
        game_map.coins = [(cx, cy) for cx, cy in game_map.coins if (cx - player.x) ** 2 + (cy - player.y) ** 2 > (player_r + 4) ** 2]
        new_health_kits = []
        for hx, hy in game_map.health_kits:
            if (hx - player.x) ** 2 + (hy - player.y) ** 2 <= (player_r + 8) ** 2:
                player.health = min(100.0, player.health + 30.0)
            else:
                new_health_kits.append((hx, hy))
        game_map.health_kits = new_health_kits
        if player.health <= 0:
            print('\nGAME OVER ΓÇö Player health reached 0.')
            running = False
        game_map.draw(screen)
        screen.lock()
        player.draw(screen, rep_type)
        for enemy in enemies:
            enemy.draw(screen, rep_type)
        screen.unlock()
        draw_hud(screen, player, enemies, rep_type)
        pygame.display.flip()
        clock.tick(60)

def main():
    pygame.init()
    print('\n' + '=' * 65)
    print('   HUNTER ASSASSIN — PHASE 3: 2D TRANSFORMATION SUITE')
    print('=' * 65)
    print('1. Interactive 2D Transformation Visualizer (TSR & Composite)')
    print('2. Launch Hunter Assassin Game Directly')
    print('-' * 65)
    mode_choice = input('Enter choice [1=TSR Demo, 2=Game, default: 1]: ').strip()
    if mode_choice != '2':
        rep_type = run_interactive_tsr_demo(standalone=False)
        print('\nProceed to Hunter Assassin Game? (Y/N) [default: Y]: ', end='', flush=True)
        proceed = input().strip().lower()
        if proceed in ('n', 'no', 'q', 'quit', 'exit'):
            print('Exiting.')
            pygame.quit()
            sys.exit()
    else:
        rep_type = 2
    screen = pygame.display.set_mode((MAP_WIDTH, MAP_HEIGHT))
    pygame.display.set_caption('Hunter Assassin — Phase 3: 2D Transformations')
    clock = pygame.time.Clock()
    run_game(screen, clock, rep_type)
    pygame.quit()
    sys.exit()
if __name__ == '__main__':
    main()
