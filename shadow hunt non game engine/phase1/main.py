import pygame
from map import GameMap, MAP_WIDTH, MAP_HEIGHT
pygame.init()
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Hunter Assassin - Maze Map')
clock = pygame.time.Clock()
game_map = GameMap()
camera_x = 0
camera_y = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((30, 30, 30))
    camera_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    world_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    game_map.draw(world_surface)
    camera_surface.blit(world_surface, (-camera_x, -camera_y))
    screen.blit(camera_surface, (0, 0))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
