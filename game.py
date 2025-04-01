import sys
import pygame
from scripts.utils import load_image, load_images, Animation
from player import Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.Background import Backgrounds
from scripts.particle import Particle
from Constants import *

class Game:
    def __init__(self, screen = None):
        pygame.init()

        pygame.display.set_caption(GAME_TITLE)
        self.screen = screen
        
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background3.png'),
            'clouds': load_images('clouds'),
            'backgrounds': load_images('backgrounds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=IDLE_ANIMATION_DURATION),
            'player/run': Animation(load_images('entities/player/run'), img_dur=RUN_ANIMATION_DURATION),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=PARTICLE_ANIMATION_DURATION, loop=False),
        }
        
        self.music = pygame.mixer.Sound(MUSIC)
        self.music.set_volume(0.05)

        self.clouds = Clouds(self.assets['clouds'], count=CLOUD_COUNT)
        self.backgrounds = Backgrounds(self.assets['backgrounds'], count=1)

        self.tilemap = Tilemap(self, tile_size=TILE_SIZE)
        self.tilemap.load(DEFAULT_MAP_PATH)

        self.pos = self.tilemap.extract([('spawners', 0), ('spawners', 1)])
        default_pos = self.pos[0]['pos'] if self.pos else [10, 10]
        self.player = Player(self, default_pos, PLAYER_SIZE)
                    
        self.particles = []
        self.scroll = [10,10]
        
    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            self.music.play(-1)
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / CAMERA_SPEED
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() *0.65 - self.scroll[1]) / CAMERA_SPEED
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            #fps
            fps = str(int(self.clock.get_fps()))
            font = pygame.font.Font(FONT, 10)  
            fps_t = font.render(fps, True, pygame.Color("RED"))
            self.display.blit(fps_t, (0, 0))

            self.backgrounds.update()
            self.backgrounds.render(self.display, offset=render_scroll)

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            # Create a temporary surface for rendering player and particles
            temp_surface = pygame.Surface((self.display.get_width(), self.display.get_height()), pygame.SRCALPHA)
            
            # Render player to temporary surface
            movement_x = 0
            if self.movement[0]:  # Left movement
                movement_x -= 1
            if self.movement[1]:  # Right movement
                movement_x += 1
            self.player.update(self.tilemap, (movement_x, 0))
            self.player.render(temp_surface, offset=render_scroll)
            
            # Render particles to temporary surface
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(temp_surface, offset=render_scroll)          
                if kill:
                    self.particles.remove(particle)
            
            # outline
            temp_mask = pygame.mask.from_surface(temp_surface)   
            white_silhouette = temp_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=TRANSPARENT)
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
            