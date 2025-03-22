import pygame
# Game configuration
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
TARGET_FPS = 60
RENDER_SCALE = 2.0
BASE_IMG_PATH = 'data/images/'

# Game title
GAME_TITLE = 'ninja game'
EDITOR_TITLE = 'editor'

# Physics
GRAVITY = 0.1
MAX_FALL_SPEED = 5
PLAYER_SPEED = 1
FRICTION = 0.1

# Player physics
PLAYER_SIZE = (8, 15)
PLAYER_JUMP_POWER = 2.5
PLAYER_AIR_TIME_THRESHOLD = 4
PLAYER_WALL_SLIDE_SPEED = 0.5
PLAYER_DASH_DURATION = 60
PLAYER_DASH_SPEED = 8
PLAYER_DASH_SLOWDOWN = 0.1
PLAYER_SLIDE_DURATION = 20
PLAYER_SLIDE_SPEED = 3.5
PLAYER_SLIDE_COOLDOWN = 30
PLAYER_SLIDE_WALL_STUN = 15
PLAYER_WALL_JUMP_HORIZONTAL = 3.5
PLAYER_WALL_JUMP_VERTICAL = 2.5
PLAYER_ANIMATION_OFFSET = (-3, -3)

# Animation durations (in frames)
IDLE_ANIMATION_DURATION = 6
RUN_ANIMATION_DURATION = 4
LEAF_PARTICLE_DURATION = 20
PARTICLE_ANIMATION_DURATION = 6

# Camera
CAMERA_SPEED = 30

# Particle effects
PARTICLE_COUNT_DASH = 20
PARTICLE_COUNT_SLIDE_IMPACT = 8
PARTICLE_SPEED_MIN = 0.5
PARTICLE_SPEED_MAX = 1.0
LEAF_SWAY_INTENSITY = 0.3
LEAF_SWAY_FREQUENCY = 0.035

# Clouds
CLOUD_COUNT = 16
CLOUD_SPEED_MIN = 0.05
CLOUD_SPEED_MAX = 0.1
CLOUD_DEPTH_MIN = 0.2
CLOUD_DEPTH_MAX = 0.8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SILHOUETTE_COLOR = (255, 255, 255, 180)
TRANSPARENT = (0, 0, 0, 0)

# Tile definitions
TILE_SIZE = 16
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

# Keyboard controls
KEY_LEFT = pygame.K_a
KEY_RIGHT = pygame.K_d
KEY_UP = pygame.K_w
KEY_DOWN = pygame.K_s
KEY_JUMP = pygame.K_SPACE
KEY_DASH = pygame.K_LSHIFT
KEY_SLIDE = pygame.K_RSHIFT
KEY_TOGGLE_GRID = pygame.K_g
KEY_AUTOTILE = pygame.K_t
KEY_SAVE = pygame.K_o
KEY_SHIFT = pygame.K_LSHIFT

# Map configuration
DEFAULT_MAP_PATH = 'map.json'

# Autotile mapping
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}

# Neighbor offsets for tile checking
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]