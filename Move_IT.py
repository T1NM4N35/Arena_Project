import pygame
import random
import math

pygame.init()

# ============================
# CONFIGURATION
# ============================
tile_size = 32
map_size_option = "medium"  # Options: "small", "medium", "large"

if map_size_option == "small":
    map_width, map_height = 30, 30
elif map_size_option == "medium":
    map_width, map_height = 50, 50
else:
    map_width, map_height = 80, 80

screen_width, screen_height = 640, 480
fps = 60
player_move_delay = 150  # milliseconds between tile moves
vision_radius = 6
room_min_size = 5
room_max_size = 10
room_count = 15 if map_size_option == "small" else 25 if map_size_option == "medium" else 40

minimap_size = 150  # pixels
minimap_tile_size = minimap_size // map_width

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", tile_size)

# ============================
# MAP GENERATION
# ============================
dungeon_map = [[1 for _ in range(map_width)] for _ in range(map_height)]  # 1 = wall, 0 = floor
explored_tiles = [[False for _ in range(map_width)] for _ in range(map_height)]
room_list = []

class Room:
    def __init__(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.center = (x + width // 2, y + height // 2)

    def intersects(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

def carve_room(room):
    for y in range(room.y, room.y + room.height):
        for x in range(room.x, room.x + room.width):
            dungeon_map[y][x] = 0

def carve_corridor(x1, y1, x2, y2):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        dungeon_map[y1][x] = 0
    for y in range(min(y1, y2), max(y1, y2) + 1):
        dungeon_map[y][x2] = 0

def generate_dungeon():
    global room_list
    for _ in range(room_count):
        width = random.randint(room_min_size, room_max_size)
        height = random.randint(room_min_size, room_max_size)
        x = random.randint(1, map_width - width - 1)
        y = random.randint(1, map_height - height - 1)
        new_room = Room(x, y, width, height)

        if any(new_room.intersects(existing_room) for existing_room in room_list):
            continue

        carve_room(new_room)
        if room_list:
            previous_center = room_list[-1].center
            carve_corridor(previous_center[0], previous_center[1], new_room.center[0], new_room.center[1])
        room_list.append(new_room)

generate_dungeon()
start_room = room_list[0]
boss_room = max(room_list, key=lambda r: math.dist(r.center, start_room.center))

# ============================
# PLAYER CLASS
# ============================
class Player:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.rect = pygame.Rect(start_x * tile_size, start_y * tile_size, tile_size, tile_size)
        self.move_cooldown = 0

    def move(self, dx, dy):
        if self.move_cooldown > 0:
            return
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < map_width and 0 <= new_y < map_height and dungeon_map[new_y][new_x] == 0:
            self.x = new_x
            self.y = new_y
            self.rect.topleft = (self.x * tile_size, self.y * tile_size)
        self.move_cooldown = player_move_delay

player = Player(start_room.center[0], start_room.center[1])

# ============================
# CAMERA SYSTEM
# ============================
def get_camera_offset():
    camera_offset_x = player.rect.centerx - screen_width // 2
    camera_offset_y = player.rect.centery - screen_height // 2
    return camera_offset_x, camera_offset_y

# ============================
# VISIBILITY
# ============================
def update_visibility():
    for y in range(map_height):
        for x in range(map_width):
            distance = math.dist((x, y), (player.x, player.y))
            if distance <= vision_radius:
                explored_tiles[y][x] = True

# ============================
# DRAW CIRCULAR MINIMAP
# ============================
def draw_minimap():
    minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
    minimap_surface.fill((0, 0, 0, 0))

    # Draw explored tiles
    for y in range(map_height):
        for x in range(map_width):
            if explored_tiles[y][x]:
                color = (60, 60, 60) if dungeon_map[y][x] == 1 else (150, 150, 150)
                pygame.draw.rect(minimap_surface, color, (x * minimap_tile_size, y * minimap_tile_size, minimap_tile_size, minimap_tile_size))

    # Draw player
    pygame.draw.rect(minimap_surface, (0, 200, 255), (player.x * minimap_tile_size, player.y * minimap_tile_size, minimap_tile_size, minimap_tile_size))

    # Draw boss room
    pygame.draw.rect(minimap_surface, (200, 0, 0), (boss_room.center[0] * minimap_tile_size, boss_room.center[1] * minimap_tile_size, minimap_tile_size, minimap_tile_size))

    # Create circular mask
    mask_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
    pygame.draw.circle(mask_surface, (255, 255, 255, 255), (minimap_size // 2, minimap_size // 2), minimap_size // 2)
    minimap_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Draw border circle
    pygame.draw.circle(minimap_surface, (200, 200, 200), (minimap_size // 2, minimap_size // 2), minimap_size // 2, 3)

    # Blit to screen
    screen.blit(minimap_surface, (screen_width - minimap_size - 10, 10))

# ============================
# MAIN LOOP
# ============================
running = True
while running:
    dt = clock.tick(fps)
    if player.move_cooldown > 0:
        player.move_cooldown -= dt

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]:
        dy = -1
    elif keys[pygame.K_s]:
        dy = 1
    elif keys[pygame.K_a]:
        dx = -1
    elif keys[pygame.K_d]:
        dx = 1
    if dx or dy:
        player.move(dx, dy)

    update_visibility()
    camera_offset_x, camera_offset_y = get_camera_offset()

    # Draw main view
    screen.fill((0, 0, 0))
    for y in range(map_height):
        for x in range(map_width):
            world_x = x * tile_size
            world_y = y * tile_size
            screen_x = world_x - camera_offset_x
            screen_y = world_y - camera_offset_y
            if -tile_size < screen_x < screen_width and -tile_size < screen_y < screen_height:
                if explored_tiles[y][x]:
                    color = (60, 60, 60) if dungeon_map[y][x] == 1 else (100, 100, 100)
                else:
                    color = (10, 10, 10)
                pygame.draw.rect(screen, color, (screen_x, screen_y, tile_size, tile_size))

    # Draw player as '@'
    player_text = font.render("@", True, (0, 200, 255))
    screen.blit(player_text, (player.rect.x - camera_offset_x, player.rect.y - camera_offset_y))

    # Draw boss room marker if visible
    if explored_tiles[boss_room.center[1]][boss_room.center[0]]:
        boss_x = boss_room.center[0] * tile_size - camera_offset_x
        boss_y = boss_room.center[1] * tile_size - camera_offset_y
        pygame.draw.rect(screen, (200, 0, 0), (boss_x, boss_y, tile_size, tile_size))

    # Draw circular minimap
    draw_minimap()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()

pygame.quit()

