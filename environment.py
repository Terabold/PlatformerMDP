import pygame
from Constants import *
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from player import Player
from scripts.particle import Particle
import random
from scripts.deathanim import reveal_effect

class Environment:
    def __init__(self, game, display):
        self.game = game
        self.display = display
        self.assets = game.assets
        
        self.clouds = Clouds(self.assets['clouds'], count=CLOUD_COUNT)
        self.tilemap = Tilemap(game, tile_size=TILE_SIZE)
        self.tilemap.load(DEFAULT_MAP_PATH)
        
        self.pos = self.tilemap.extract([('spawners', 0), ('spawners', 1)])
        self.default_pos = self.pos[0]['pos'] if self.pos else [10, 10]
        self.player = Player(game, self.default_pos, PLAYER_SIZE)
        
        self.particles = []
        self.scroll = [10, 10]
        
        # Reveal animation settings
        self.reveal_timer = 0
        self.death_anim_duration = 8
        self.black_screen_duration = 23  
        self.respawn_anim_duration = 45  
        self.total_anim_duration = self.death_anim_duration + self.black_screen_duration + self.respawn_anim_duration
        
        self.death_pos = None  
        self.max_radius = 300  
        self.min_radius = 0   
        self.death_radius = self.max_radius  
        self.respawn_radius = self.min_radius  

        self.revealing = False  
        self.is_dying = False  
        
        self.start_reveal_animation()

    def update(self, movement):
        # Handle the reveal animation
        if self.revealing:
            self.reveal_timer += 1
            
            # Phase 1: Shrinking hole animation (death)
            if self.reveal_timer <= self.death_anim_duration:
                progress = self.reveal_timer / self.death_anim_duration
                self.death_radius = self.max_radius * (1 - progress)
            
            # Phase 3: Expanding hole animation (respawn)
            elif self.reveal_timer > self.death_anim_duration + self.black_screen_duration:
                elapsed_in_phase3 = self.reveal_timer - (self.death_anim_duration + self.black_screen_duration)
                progress = elapsed_in_phase3 / self.respawn_anim_duration
                self.respawn_radius = self.max_radius * progress
            
            # End animation once complete
            if self.reveal_timer >= self.total_anim_duration:
                self.revealing = False
                self.is_dying = False
                self.reveal_timer = 0
        
        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / CAMERA_SPEED
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() * 0.65 - self.scroll[1]) / CAMERA_SPEED
        
        self.clouds.update()
        
        # Only process movement if not dying
        if not self.is_dying:
            movement_x = 0
            if movement[0]:  
                movement_x -= 1
            if movement[1]: 
                movement_x += 1
                
            self.player.update(self.tilemap, (movement_x, 0))
            if self.tilemap.spike_check(self.player.rect()):
                self.trigger_death()
        
        for particle in self.particles.copy():
            kill = particle.update()
            if kill:
                self.particles.remove(particle)
                
        self.handle_finish()
        
        return (int(self.scroll[0]), int(self.scroll[1]))
    
    def trigger_death(self):
        if not self.is_dying:
            self.is_dying = True
            
            self.death_pos = self.player.rect().center
            
            for _ in range(20):
                self.particles.append(
                    Particle(self.game, 'particle', 
                            self.death_pos, 
                            velocity=[random.uniform(-2, 2), random.uniform(-2, 2)], 
                            frame=random.randint(0, 7))
                )
            
            self.player.pos = self.default_pos.copy()  
            self.start_reveal_animation()
            self.reset()
    
    def start_reveal_animation(self):
        self.revealing = True
        self.reveal_timer = 0
        self.death_radius = self.max_radius
        self.respawn_radius = self.min_radius
    
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
        
        if self.revealing:
            if self.reveal_timer <= self.death_anim_duration and self.death_pos:
                death_screen_pos = (
                    self.death_pos[0] - render_scroll[0],
                    self.death_pos[1] - render_scroll[1]
                )
                self.draw_reveal(display, death_screen_pos, self.death_radius, 'shrink')
            
            elif self.reveal_timer <= self.death_anim_duration + self.black_screen_duration:
                self.draw_reveal(display, (0, 0), 0, 'black')
            
            else:
                spawn_screen_pos = (
                    self.default_pos[0] - render_scroll[0],
                    self.default_pos[1] - render_scroll[1]
                )
                self.draw_reveal(display, spawn_screen_pos, self.respawn_radius, 'expand')

    def draw_reveal(self, display, center_pos, radius, mode):
        """Draw the reveal effect"""
        width, height = display.get_size()
        transition_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if mode == 'black':
            # Full black screen
            transition_surf.fill((0, 0, 0, 255))
        else:
            # Start with black
            transition_surf.fill((0, 0, 0, 255))
            
            # Draw a transparent hole (circle)
            if radius > 0:
                pygame.draw.circle(transition_surf, (0, 0, 0, 0), center_pos, radius)
        
        display.blit(transition_surf, (0, 0))

    def handle_finish(self):
        if self.tilemap.finishline_check(self.player.rect()):
            pass  # You can implement finish line logic here
    
    def reset(self):
        self.player.pos = self.default_pos.copy()
        self.player.reset()
        self.particles.clear()
        self.scroll = [10, 10]
        self.is_dying = False
        self.start_reveal_animation()
        
    def create_particle(self, particle_type, pos, velocity=None, frame=0):
        if velocity is None:
            velocity = [0, 0]
        self.particles.append(
            Particle(self.game, particle_type, pos, velocity=velocity, frame=frame)
        )