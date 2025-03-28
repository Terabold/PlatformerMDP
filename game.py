import sys
import math
import random
import pygame
from scripts.utils import load_image, load_images, Animation
from scripts.player import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from Constants import *

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption(GAME_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.jpg'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=IDLE_ANIMATION_DURATION),
            'player/run': Animation(load_images('entities/player/run'), img_dur=RUN_ANIMATION_DURATION),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=PARTICLE_ANIMATION_DURATION, loop=False),
        }
        
        self.clouds = Clouds(self.assets['clouds'], count=CLOUD_COUNT)
        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)
        self.tilemap.load(DEFAULT_MAP_PATH)
        
        self.player = Player(self, self.get_player_spawn(), PLAYER_SIZE)
        
        self.particles = []
        self.scroll = [0, 0]
    
    def get_player_spawn(self):
        for tile in self.tilemap.tilemap.values():
            if tile['type'] == 'spawn': 
                return [
                    tile['pos'][0] * self.tilemap.tile_size + self.tilemap.tile_size // 2,
                    tile['pos'][1] * self.tilemap.tile_size + self.tilemap.tile_size // 2
                ]
        return [50, 50]
        
    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / CAMERA_SPEED
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() *0.6 - self.scroll[1]) / CAMERA_SPEED
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            # self.clouds.update()
            # self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            # Create a temporary surface for rendering player and particles
            temp_surface = pygame.Surface((self.display.get_width(), self.display.get_height()), pygame.SRCALPHA)
            
            # Render player to temporary surface
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(temp_surface, offset=render_scroll)
            
            # Render particles to temporary surface
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(temp_surface, offset=render_scroll)          
                if kill:
                    self.particles.remove(particle)
            
            # outline
            temp_mask = pygame.mask.from_surface(temp_surface)   
            white_silhouette = temp_mask.to_surface(setcolor=SILHOUETTE_COLOR, unsetcolor=TRANSPARENT)
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display.blit(white_silhouette, offset)         
            self.display.blit(temp_surface, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == KEY_LEFT:
                        self.movement[0] = True
                    if event.key == KEY_RIGHT:
                        self.movement[1] = True
                    if event.key == KEY_JUMP:
                        self.player.jump()
                    if event.key == KEY_DASH:
                        self.player.dash()
                    if event.key == KEY_SLIDE: 
                        self.player.slide()
                if event.type == pygame.KEYUP:
                    if event.key == KEY_LEFT:
                        self.movement[0] = False
                    if event.key == KEY_RIGHT:
                        self.movement[1] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)
            
Game().run()