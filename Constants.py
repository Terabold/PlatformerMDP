import pygame
# Game configuration
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h - 60 

DISPLAY_WIDTH = 320
DISPLAY_HEIGHT = 240
FPS = 60
TILE_SIZE = 16
BASE_IMG_PATH = 'data/images/'
RECT = 'data\Rect.png'
FONT = 'data\Menu.ttf'
FONT2 = r'data\font\Default.otf'
MENUBG = 'data\images\MenuBG.jpg'
MUSIC = 'data\sfx\Backgroundmusic.mp3'
MENUTXTCOLOR = (186,248,186)
# Game title
GAME_TITLE = 'ninja game'
EDITOR_TITLE = 'editor'
WHITE = (255,255,255)
# Physics
GRAVITY = 0.25
MAX_FALL_SPEED = 6
FRICTION = 0.1
GRAY = (30,30,30)
# Player physics
PLAYER_SIZE = (8, 15)
PLAYER_JUMP_POWER = 1.9
PLAYER_AIR_TIME_THRESHOLD = 4
PLAYER_WALL_SLIDE_SPEED = 0.5
PLAYER_DASH_DURATION = 30
PLAYER_DASH_SPEED = 3
PLAYER_DASH_SLOWDOWN = 1
PLAYER_WALL_JUMP_HORIZONTAL = 3.5
PLAYER_WALL_JUMP_VERTICAL = 2.5
PLAYER_ANIMATION_OFFSET = (-3, -3)
PLAYER_DASH_UPWARD_SPEED = 4

IDLE_ANIMATION_DURATION = 6
RUN_ANIMATION_DURATION = 4
PARTICLE_ANIMATION_DURATION = 6

# Camera
CAMERA_SPEED = 10

# Particle effects
PARTICLE_COUNT_DASH = 8
PARTICLE_SPEED_MIN = 0.5
PARTICLE_SPEED_MAX = 1.0

# Clouds
CLOUD_COUNT = 10
CLOUD_SPEED_MIN = 0.05
CLOUD_SPEED_MAX = 0.1
CLOUD_DEPTH_MIN = 0.2
CLOUD_DEPTH_MAX = 0.8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SILHOUETTE_COLOR = (0, 0, 0, 200)
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