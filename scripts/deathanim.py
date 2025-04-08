# death_animation.py
import pygame

class DeathAnimation:
    def __init__(self, game):
        self.game = game
        
        # Animation settings
        self.death_anim_duration = 10
        self.black_screen_duration = 20  
        self.respawn_anim_duration = 50  
        self.total_anim_duration = self.death_anim_duration + self.black_screen_duration + self.respawn_anim_duration
        
        self.timer = 0
        self.death_pos = None  
        self.max_radius = 300  
        self.min_radius = 0   
        self.death_radius = self.max_radius  
        self.respawn_radius = self.min_radius  
        self.active = False
        self.is_dying = False
        
    def start(self, death_pos=None):
        self.active = True
        self.is_dying = True
        self.timer = 0
        self.death_pos = death_pos
        self.death_radius = self.max_radius
        self.respawn_radius = self.min_radius
        
    def update(self):
        if not self.active:
            return False
            
        self.timer += 1
        
        # Phase 1: Shrinking circle at death position
        if self.timer <= self.death_anim_duration:
            progress = self.timer / self.death_anim_duration
            self.death_radius = self.max_radius * (1 - progress)
            
        # Phase 2: Reset player position during black screen
        elif self.timer == self.death_anim_duration + 1:
            return True  # Signal to reset player
            
        # Phase 3: Growing circle at respawn position
        elif self.timer > self.death_anim_duration + self.black_screen_duration:
            elapsed_in_phase3 = self.timer - (self.death_anim_duration + self.black_screen_duration)
            progress = elapsed_in_phase3 / self.respawn_anim_duration
            self.respawn_radius = self.max_radius * progress
        
        # Animation complete
        if self.timer >= self.total_anim_duration:
            self.active = False
            self.is_dying = False
            self.timer = 0
            return False
            
        return None
        
    def render(self, display, scroll):
        if not self.active:
            return
            
        render_scroll = (int(scroll[0]), int(scroll[1]))
        width, height = display.get_size()
        transition_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if self.timer <= self.death_anim_duration and self.death_pos:
            transition_surf.fill((0, 0, 0, 255))
            death_screen_pos = (
                self.death_pos[0] - render_scroll[0],
                self.death_pos[1] - render_scroll[1]
            )
            if self.death_radius > 0:
                pygame.draw.circle(transition_surf, (0, 0, 0, 0), death_screen_pos, self.death_radius)
                
        elif self.timer <= self.death_anim_duration + self.black_screen_duration:
            transition_surf.fill((0, 0, 0, 255))
            
        else:
            transition_surf.fill((0, 0, 0, 255))
            spawn_screen_pos = (
                self.game.environment.default_pos[0] - render_scroll[0],
                self.game.environment.default_pos[1] - render_scroll[1]
            )
            if self.respawn_radius > 0:
                pygame.draw.circle(transition_surf, (0, 0, 0, 0), spawn_screen_pos, self.respawn_radius)
        
        display.blit(transition_surf, (0, 0))