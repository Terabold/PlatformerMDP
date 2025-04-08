# Modified portion of environment.py
import pygame
from Constants import *
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from player import Player
from scripts.particle import Particle
from scripts.deathanim import DeathAnimation
import random

class Environment:
    def __init__(self, game, display, player1=None, player2=None):
        self.game = game
        self.display = display
        self.assets = game.assets

        self.player1 = player1

        self.clouds = Clouds(self.assets['clouds'], count=CLOUD_COUNT)
        self.tilemap = Tilemap(game, tile_size=TILE_SIZE)
        self.tilemap.load(DEFAULT_MAP_PATH)
        
        self.pos = self.tilemap.extract([('spawners', 0), ('spawners', 1)])
        self.default_pos = self.pos[0]['pos'] if self.pos else [10, 10]
        self.player = Player(game, self.default_pos, PLAYER_SIZE)
        
        self.particles = []
        self.scroll = [10, 10]
        
        self.death_animation = DeathAnimation(game)

    def update(self):
        reset_player = self.death_animation.update()
        if reset_player is True:
            self.player.pos = self.default_pos.copy()
            self.player.reset()
        
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / CAMERA_SPEED
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() * 0.65 - self.scroll[1]) / CAMERA_SPEED
        
        self.clouds.update()
        
        if not self.death_animation.is_dying:
            self.player.handle_movement(self.tilemap)
            
            if self.tilemap.spike_check(self.player.rect()):
                self.trigger_death()
        
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
                
        self.handle_finish()
        
        return (int(self.scroll[0]), int(self.scroll[1]))
    
    def trigger_death(self):
        if not self.death_animation.is_dying:
            self.death_animation.start(self.player.rect().center)
            
            for _ in range(20):
                self.particles.append(
                    Particle(self.game, 'particle', 
                            self.death_animation.death_pos, 
                            velocity=[random.uniform(-2, 2), random.uniform(-2, 2)], 
                            frame=random.randint(0, 7))
                )
    
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
        
        self.death_animation.render(display, self.scroll)

    def handle_finish(self):
        if self.tilemap.finishline_check(self.player.rect()):
            pass  
    
    def reset(self):
        self.player.pos = self.default_pos.copy()
        self.player.reset()
        self.particles.clear()
        self.scroll = [10, 10]
        self.death_animation.start(None) 
    
    def move(self, action, state):
        self.player.stop_movement()
        
        if action is None:
            return
        
        if action in [3, 5, 7]:  
            self.player.move_left(True)
        elif action in [4, 6, 8]:  
            self.player.move_right(True)
        
        if action in [1, 5, 6]:  
            self.player.start_jump(True)
        elif action in [2, 7, 8]:  
            self.player.start_grab(True)  
        
        if state == 1:  
            self.player.start_dash(True)
        elif state == 2:  
            self.player.start_grab(True)
        
    def create_particle(self, particle_type, pos, velocity=None, frame=0):
        if velocity is None:
            velocity = [0, 0]
        self.particles.append(
            Particle(self.game, particle_type, pos, velocity=velocity, frame=frame)
        )