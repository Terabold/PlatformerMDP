import pygame
from Constants import *
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from player import Player
from scripts.particle import Particle
import random

class Environment:
    def __init__(self, game, display):
        self.game = game
        self.display = display
        self.assets = game.assets
        
        self.clouds = Clouds(self.assets['clouds'], count=CLOUD_COUNT)
        self.tilemap = Tilemap(game, tile_size=TILE_SIZE)
        self.tilemap.load(DEFAULT_MAP_PATH)
        
        self.pos = self.tilemap.extract([('spawners', 0), ('spawners', 1)])
        default_pos = self.pos[0]['pos'] if self.pos else [10, 10]
        self.player = Player(game, default_pos, PLAYER_SIZE)
        
        self.particles = []
        self.scroll = [10, 10]
    
    def update(self, movement):
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / CAMERA_SPEED
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() * 0.65 - self.scroll[1]) / CAMERA_SPEED
        
        self.clouds.update()
        
        movement_x = 0
        if movement[0]:  
            movement_x -= 1
        if movement[1]: 
            movement_x += 1
            
        self.player.update(self.tilemap, (movement_x, 0))
        if self.tilemap.spike_check(self.player.rect()):
            for _ in range(20):
                self.particles.append(
                    Particle(self.game, 'particle', 
                            self.player.rect().center, 
                            velocity=[random.uniform(-2, 2), random.uniform(-2, 2)], 
                            frame=random.randint(0, 7))
                )
            
            self.reset()
            return True
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
                
        self.handle_finish()
        
        return (int(self.scroll[0]), int(self.scroll[1]))
    
    def render(self, display, debug=False):
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
        
        display.blit(self.assets['background'], (0, 0))
        
        if debug:
            fps = str(int(self.game.clock.get_fps()))
            font = pygame.font.Font(FONT, 10)  
            fps_text = font.render(fps, True, pygame.Color("RED"))
            display.blit(fps_text, (0, 0))
        
        self.clouds.render(display, offset=render_scroll)
        
        self.tilemap.render(display, offset=render_scroll)
        
        temp_surface = pygame.Surface((display.get_width(), display.get_height()), pygame.SRCALPHA)
        
        self.player.render(temp_surface, offset=render_scroll)
        
        for particle in self.particles:
            particle.render(temp_surface, offset=render_scroll)
        
        temp_mask = pygame.mask.from_surface(temp_surface)   
        white_silhouette = temp_mask.to_surface(setcolor=(255, 255, 255), unsetcolor=TRANSPARENT)
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            display.blit(white_silhouette, offset)
            
        display.blit(temp_surface, (0, 0))
    
    def handle_finish(self):
        if self.tilemap.finishline_check(self.player.rect()):
            pass
    
    def reset(self):
        self.player.reset()
        self.particles.clear()
        self.scroll = [10, 10]
        
    def create_particle(self, particle_type, pos, velocity=None, frame=0):
        if velocity is None:
            velocity = [0, 0]
        self.particles.append(
            Particle(self.game, particle_type, pos, velocity=velocity, frame=frame)
        )