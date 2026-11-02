from typing import List, Tuple, Dict, Any

class LevelData:

    def __init__(self, name: str, level_index: int, room_w: float, room_h: float, player_spawn: Tuple[float, float], exit_bounds: Tuple[float, float, float, float], alarm_seconds: float, walls: List[Tuple[float, float, float, float, str]], boxes: List[Tuple[float, float, float, float, str]], doors: List[Tuple[float, float, float, float, str, str]], enemies: List[Dict[str, Any]], cameras: List[Dict[str, Any]], coin_positions: List[Tuple[float, float]], medkit_positions: List[Tuple[float, float]]):
        self.name = name
        self.level_index = level_index
        self.room_w = room_w
        self.room_h = room_h
        self.player_spawn = player_spawn
        self.exit_bounds = exit_bounds
        self.alarm_seconds = alarm_seconds
        self.walls = walls
        self.boxes = boxes
        self.doors = doors
        self.enemies = enemies
        self.cameras = cameras
        self.coin_positions = coin_positions
        self.medkit_positions = medkit_positions

def build_level_1(ox: float=60.0, oy: float=60.0) -> LevelData:
    wt = 5.0
    pw = 100.0
    bs = 120.0
    room_w = 2 * wt + 4 * pw + 3 * bs
    room_h = 2 * wt + 3 * pw + 2 * bs
    walls = [(ox, oy, ox + room_w, oy + wt, 'wall_top'), (ox, oy + room_h - wt, ox + room_w, oy + room_h, 'wall_bottom'), (ox, oy, ox + wt, oy + room_h, 'wall_left'), (ox + room_w - wt, oy, ox + room_w, oy + room_h, 'wall_right')]
    col_x = [ox + wt + pw + i * (bs + pw) for i in range(3)]
    row_y = [oy + wt + pw + j * (bs + pw) for j in range(2)]
    boxes = []
    for c_i, bx in enumerate(col_x):
        for r_i, by in enumerate(row_y):
            boxes.append((bx, by, bx + bs, by + bs, f'crate_{c_i}_{r_i}'))
    doors = [(col_x[0] + bs, row_y[0] + bs * 0.5, col_x[1], row_y[0] + bs * 0.5, 'door_1', '#00e5ff'), (col_x[1] + bs, row_y[1] + bs * 0.5, col_x[2], row_y[1] + bs * 0.5, 'door_2', '#ff9100'), (col_x[1] + bs * 0.5, row_y[0] + bs, col_x[1] + bs * 0.5, row_y[1], 'door_3', '#a855f7')]
    player_spawn = (ox + wt + pw * 0.5, oy + wt + pw * 0.5)
    exit_bounds = (ox + room_w - wt - pw + 12.0, oy + room_h - wt - 36.0, ox + room_w - wt - 12.0, oy + room_h - wt)
    patrol_bottom_y = oy + wt + pw + bs + pw + bs + 50.0
    patrol_mid_y = oy + wt + pw + bs + 50.0
    enemies = [{'name': 'Guard_Alpha', 'waypoints': [(ox + 160.0, patrol_bottom_y), (ox + 610.0, patrol_bottom_y)], 'is_shielded': False, 'speed': 2.0}, {'name': 'Enforcer_Bravo', 'waypoints': [(ox + 220.0, patrol_mid_y), (ox + 550.0, patrol_mid_y)], 'is_shielded': True, 'speed': 1.8}]
    cameras = [{'x': ox + room_w - 18.0, 'y': oy + 18.0, 'base_angle': 2.45, 'sweep_amplitude': 0.65, 'sweep_speed': 0.022, 'cone_range': 230.0}]
    coin_positions = [(col_x[0] + bs * 0.5, oy + wt + pw * 0.5), (col_x[1] + bs * 0.5, oy + wt + pw * 0.5), (col_x[2] + bs * 0.5, oy + wt + pw * 0.5), (ox + room_w - wt - pw * 0.5, row_y[0] + bs * 0.5), (col_x[0] + bs * 0.5, oy + room_h - wt - pw * 0.5), (col_x[1] + bs * 0.5, oy + room_h - wt - pw * 0.5), (col_x[2] + bs * 0.5, oy + room_h - wt - pw * 0.5)]
    medkit_positions = [(ox + wt + pw * 0.5, row_y[0] + bs * 0.5), (col_x[0] + bs + pw * 0.5, row_y[1] + bs * 0.5), (col_x[1] + bs + pw * 0.5, row_y[0] + bs * 0.5)]
    return LevelData(name='Level 1: Facility Infiltration', level_index=0, room_w=room_w, room_h=room_h, player_spawn=player_spawn, exit_bounds=exit_bounds, alarm_seconds=10.0, walls=walls, boxes=boxes, doors=doors, enemies=enemies, cameras=cameras, coin_positions=coin_positions, medkit_positions=medkit_positions)

def build_level_2(ox: float=60.0, oy: float=60.0) -> LevelData:
    wt = 5.0
    pw = 88.0
    bs = 110.0
    room_w = 2 * wt + 5 * pw + 4 * bs
    room_h = 2 * wt + 4 * pw + 3 * bs
    walls = [(ox, oy, ox + room_w, oy + wt, 'wall_top'), (ox, oy + room_h - wt, ox + room_w, oy + room_h, 'wall_bottom'), (ox, oy, ox + wt, oy + room_h, 'wall_left'), (ox + room_w - wt, oy, ox + room_w, oy + room_h, 'wall_right')]
    col_x = [ox + wt + pw + i * (bs + pw) for i in range(4)]
    row_y = [oy + wt + pw + j * (bs + pw) for j in range(3)]
    walls.append((col_x[0] + bs * 0.25, row_y[0] - pw * 0.35, col_x[0] + bs * 0.75, row_y[0] - pw * 0.35 + wt, 'stub_h1'))
    walls.append((col_x[2] - pw * 0.4, row_y[1] + bs * 0.15, col_x[2] - pw * 0.4 + wt, row_y[1] + bs * 0.85, 'stub_v1'))
    walls.append((ox + wt + pw * 0.15, row_y[2] + bs * 0.5 - wt * 0.5, ox + wt + pw * 0.55, row_y[2] + bs * 0.5 + wt * 0.5, 'stub_h2'))
    walls.append((col_x[3] + bs * 0.1, row_y[0] - pw * 0.45, col_x[3] + bs * 0.9, row_y[0] - pw * 0.45 + wt, 'stub_h3'))
    boxes = []
    for c_i, bx in enumerate(col_x):
        for r_i, by in enumerate(row_y):
            boxes.append((bx, by, bx + bs, by + bs, f'crate_{c_i}_{r_i}'))
    doors = [(col_x[0] + bs, row_y[0] + bs * 0.5, col_x[1], row_y[0] + bs * 0.5, 'door_2a', '#00e5ff'), (col_x[1] + bs, row_y[1] + bs * 0.5, col_x[2], row_y[1] + bs * 0.5, 'door_2b', '#ff9100'), (col_x[2] + bs, row_y[2] + bs * 0.5, col_x[3], row_y[2] + bs * 0.5, 'door_2c', '#a855f7'), (col_x[1] + bs * 0.5, row_y[0] + bs, col_x[1] + bs * 0.5, row_y[1], 'door_2d', '#22c55e'), (col_x[3] + bs * 0.5, row_y[1] + bs, col_x[3] + bs * 0.5, row_y[2], 'door_2e', '#ec4899')]
    player_spawn = (ox + wt + pw * 0.5, oy + wt + pw * 0.5)
    exit_bounds = (ox + room_w - wt - pw + 10.0, oy + room_h - wt - 40.0, ox + room_w - wt - 10.0, oy + room_h - wt)
    lx = [ox + wt + pw * 0.5 + i * (bs + pw) for i in range(5)]
    ly = [oy + wt + pw * 0.5 + j * (bs + pw) for j in range(4)]
    enemies = [{'name': 'Guard_South', 'waypoints': [(lx[0], ly[0]), (lx[2], ly[0]), (lx[2], ly[1])], 'is_shielded': False, 'speed': 2.1}, {'name': 'Guard_Mid', 'waypoints': [(lx[4], ly[1]), (lx[1], ly[1]), (lx[1], ly[2])], 'is_shielded': False, 'speed': 2.0}, {'name': 'Guard_North', 'waypoints': [(lx[0], ly[3]), (lx[3], ly[3]), (lx[3], ly[2])], 'is_shielded': False, 'speed': 2.2}, {'name': 'Enforcer_Vault', 'waypoints': [(lx[2], ly[1]), (lx[3], ly[1]), (lx[3], ly[2])], 'is_shielded': True, 'speed': 1.7}]
    cameras = [{'x': ox + room_w - 18.0, 'y': oy + 18.0, 'base_angle': 2.45, 'sweep_amplitude': 0.65, 'sweep_speed': 0.024, 'cone_range': 240.0}, {'x': ox + 18.0, 'y': oy + room_h - 18.0, 'base_angle': -0.75, 'sweep_amplitude': 0.7, 'sweep_speed': 0.026, 'cone_range': 240.0}]
    coin_positions = [(lx[0] + 16, ly[0]), (lx[2], ly[0]), (lx[4] - 16, ly[0]), (lx[1], ly[1]), (lx[3], ly[1]), (lx[0] + 12, ly[2]), (lx[2], ly[2]), (lx[4] - 12, ly[2]), (lx[1], ly[3]), (lx[3], ly[3]), (col_x[0] + bs * 0.5, row_y[0] + bs * 0.5 - 30), (col_x[2] + bs * 0.5, row_y[2] + bs * 0.5 + 30)]
    medkit_positions = [(lx[0], ly[1]), (lx[2], ly[1]), (lx[4], ly[3] - 12), (lx[3], ly[0])]
    return LevelData(name='Level 2: Deep Vault Sweep', level_index=1, room_w=room_w, room_h=room_h, player_spawn=player_spawn, exit_bounds=exit_bounds, alarm_seconds=12.0, walls=walls, boxes=boxes, doors=doors, enemies=enemies, cameras=cameras, coin_positions=coin_positions, medkit_positions=medkit_positions)

def build_level_3(ox: float=60.0, oy: float=60.0) -> LevelData:
    wt = 5.0
    pw = 80.0
    bs = 115.0
    room_w = 2 * wt + 6 * pw + 5 * bs
    room_h = 2 * wt + 4 * pw + 3 * bs
    walls = [(ox, oy, ox + room_w, oy + wt, 'wall_top'), (ox, oy + room_h - wt, ox + room_w, oy + room_h, 'wall_bottom'), (ox, oy, ox + wt, oy + room_h, 'wall_left'), (ox + room_w - wt, oy, ox + room_w, oy + room_h, 'wall_right')]
    col_x = [ox + wt + pw + i * (bs + pw) for i in range(5)]
    row_y = [oy + wt + pw + j * (bs + pw) for j in range(3)]
    boxes = []
    for c_i, bx in enumerate(col_x):
        for r_i, by in enumerate(row_y):
            boxes.append((bx, by, bx + bs, by + bs, f'crate_{c_i}_{r_i}'))
    vault_left = col_x[2] - pw * 0.35
    vault_right = col_x[2] + bs + pw * 0.35
    walls.append((vault_left, row_y[1] - pw * 0.4, vault_left + wt, row_y[1] + bs * 0.2, 'vault_w1'))
    walls.append((vault_left, row_y[1] + bs * 0.8, vault_left + wt, row_y[1] + bs + pw * 0.4, 'vault_w2'))
    walls.append((vault_right, row_y[1] - pw * 0.4, vault_right + wt, row_y[1] + bs * 0.2, 'vault_w3'))
    walls.append((vault_right, row_y[1] + bs * 0.8, vault_right + wt, row_y[1] + bs + pw * 0.4, 'vault_w4'))
    doors = [(col_x[0] + bs, row_y[0] + bs * 0.5, col_x[1], row_y[0] + bs * 0.5, 'door_3a', '#00e5ff'), (col_x[1] + bs, row_y[0] + bs * 0.5, col_x[2], row_y[0] + bs * 0.5, 'door_3b', '#ff9100'), (col_x[2] + bs, row_y[1] + bs * 0.5, col_x[3], row_y[1] + bs * 0.5, 'door_3c', '#a855f7'), (col_x[3] + bs, row_y[2] + bs * 0.5, col_x[4], row_y[2] + bs * 0.5, 'door_3d', '#22c55e'), (col_x[1] + bs * 0.5, row_y[1] + bs, col_x[1] + bs * 0.5, row_y[2], 'door_3e', '#ec4899'), (col_x[3] + bs * 0.5, row_y[0] + bs, col_x[3] + bs * 0.5, row_y[1], 'door_3f', '#eab308'), (col_x[2] + bs * 0.5, row_y[1] + bs, col_x[2] + bs * 0.5, row_y[2], 'door_3g', '#f43f5e')]
    player_spawn = (ox + wt + pw * 0.5, oy + wt + pw * 0.5)
    exit_bounds = (ox + room_w - wt - pw + 8.0, oy + room_h - wt - 42.0, ox + room_w - wt - 8.0, oy + room_h - wt)
    lx = [ox + wt + pw * 0.5 + i * (bs + pw) for i in range(6)]
    ly = [oy + wt + pw * 0.5 + j * (bs + pw) for j in range(4)]
    enemies = [{'name': 'Guard_West', 'waypoints': [(lx[0], ly[0]), (lx[0], ly[2]), (lx[1], ly[2])], 'is_shielded': False, 'speed': 2.3}, {'name': 'Guard_East', 'waypoints': [(lx[5], ly[1]), (lx[5], ly[3]), (lx[4], ly[3])], 'is_shielded': False, 'speed': 2.3}, {'name': 'Guard_NorthSector', 'waypoints': [(lx[1], ly[0]), (lx[4], ly[0]), (lx[4], ly[1])], 'is_shielded': False, 'speed': 2.2}, {'name': 'Guard_SouthSector', 'waypoints': [(lx[1], ly[3]), (lx[3], ly[3]), (lx[3], ly[2])], 'is_shielded': False, 'speed': 2.2}, {'name': 'Enforcer_VaultCore', 'waypoints': [(lx[2], ly[1]), (lx[3], ly[1]), (lx[3], ly[2])], 'is_shielded': True, 'speed': 1.9}, {'name': 'Enforcer_ExtractionPad', 'waypoints': [(lx[4], ly[2]), (lx[5], ly[2]), (lx[5], ly[3])], 'is_shielded': True, 'speed': 1.9}]
    cameras = [{'x': ox + room_w - 18.0, 'y': oy + 18.0, 'base_angle': 2.45, 'sweep_amplitude': 0.7, 'sweep_speed': 0.028, 'cone_range': 250.0}, {'x': ox + 18.0, 'y': oy + room_h - 18.0, 'base_angle': -0.75, 'sweep_amplitude': 0.7, 'sweep_speed': 0.026, 'cone_range': 250.0}, {'x': col_x[2] + bs * 0.5, 'y': oy + wt + pw * 0.5, 'base_angle': 1.57, 'sweep_amplitude': 0.55, 'sweep_speed': 0.03, 'cone_range': 220.0}]
    coin_positions = [(lx[0], ly[1]), (lx[1], ly[0]), (lx[2], ly[0]), (lx[3], ly[0]), (lx[4], ly[0]), (lx[1], ly[1]), (lx[2], ly[1]), (lx[3], ly[1]), (lx[4], ly[1]), (lx[0], ly[2]), (lx[1], ly[2]), (lx[3], ly[2]), (lx[4], ly[2]), (lx[5], ly[2]), (lx[1], ly[3]), (lx[2], ly[3]), (lx[3], ly[3]), (lx[4], ly[3])]
    medkit_positions = [(lx[0], ly[3]), (lx[5], ly[0]), (col_x[2] + bs * 0.5, row_y[1] + bs * 0.5), (lx[2], ly[2]), (lx[3], ly[3]), (lx[5], ly[1])]
    return LevelData(name='Level 3: Cyber Citadel Lockdown', level_index=2, room_w=room_w, room_h=room_h, player_spawn=player_spawn, exit_bounds=exit_bounds, alarm_seconds=15.0, walls=walls, boxes=boxes, doors=doors, enemies=enemies, cameras=cameras, coin_positions=coin_positions, medkit_positions=medkit_positions)
LEVEL_BUILDERS = [build_level_1, build_level_2, build_level_3]

def get_level(index: int, ox: float=60.0, oy: float=60.0) -> LevelData:
    clamped_idx = max(0, min(index, len(LEVEL_BUILDERS) - 1))
    return LEVEL_BUILDERS[clamped_idx](ox, oy)
