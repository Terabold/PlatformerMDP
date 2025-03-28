import math
import random
from scripts.Constants import *
import pygame

from scripts.particle import Particle

class Player:
    def __init__(self, game, pos, size):
        self.game = game
        self.type = 'player'
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.sliding = 0
        self.slide_cooldown = 0
        self.slide_wall_stun = 0
        self.dash_direction = (0, 0)
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def dash(self):
        if self.slide_wall_stun > 0:
            return False
            
        if not self.dashing:
            if self.flip:
                self.dashing = -PLAYER_DASH_DURATION
                self.dash_direction = (-1, 0)  # Dash to the left
            else:
                self.dashing = PLAYER_DASH_DURATION
                self.dash_direction = (1, 0)  # Dash to the right
            return True
        
        return False

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            
        if self.slide_cooldown > 0:
            self.slide_cooldown -= 1
            
        if self.sliding > 0:
            self.sliding -= 1
            if self.flip:
                self.velocity[0] = -PLAYER_SLIDE_SPEED
            else:
                self.velocity[0] = PLAYER_SLIDE_SPEED
                
            if not self.collisions['down']:
                self.velocity[1] = 2.0
                
            if self.sliding % 3 == 0:
                pvelocity = [-0.5 if self.flip else 0.5, 0]
                self.game.particles.append(Particle(self.game, 'particle', 
                                                [self.rect().centerx, self.rect().bottom - 2], 
                                                velocity=pvelocity, frame=random.randint(0, 7)))
            
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > PLAYER_AIR_TIME_THRESHOLD and self.slide_wall_stun <= 0:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        if self.slide_wall_stun > 0:
            self.set_action('idle')
        elif not self.wall_slide:
            if self.sliding > 0:
                self.set_action('slide')
            elif self.air_time > PLAYER_AIR_TIME_THRESHOLD:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        # Dash state handling
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
            
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            if hasattr(self, 'dash_direction'):
                direction_x, direction_y = self.dash_direction
                dash_speed_x = PLAYER_DASH_SPEED if direction_x != 0 else 0
                dash_speed_y = PLAYER_DASH_SPEED if direction_y != 0 else 0
                
                if direction_x != 0 and direction_y != 0:
                    dash_speed_x *= 0.7071
                    dash_speed_y *= 0.7071
                
                self.velocity[0] = direction_x * dash_speed_x
                self.velocity[1] = direction_y * dash_speed_y
            
            if self.dashing % 3 == 0:
                if hasattr(self, 'dash_direction'):
                    direction_x, direction_y = self.dash_direction
                    pvelocity = [-direction_x * random.random() * 2, -direction_y * random.random() * 2]
                    self.game.particles.append(Particle(self.game, 'particle', 
                                                    self.rect().center, 
                                                    velocity=pvelocity, 
                                                    frame=random.randint(0, 7)))
                
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            if self.velocity[0] > 0:
                self.velocity[0] = max(self.velocity[0] - FRICTION, 0)
            else:
                self.velocity[0] = min(self.velocity[0] + FRICTION, 0)

    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), 
                      (self.pos[0] - offset[0] + self.anim_offset[0], 
                       self.pos[1] - offset[1] + self.anim_offset[1]))

    def jump(self):        
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = PLAYER_WALL_JUMP_HORIZONTAL
                self.velocity[1] = -PLAYER_WALL_JUMP_VERTICAL
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -PLAYER_WALL_JUMP_HORIZONTAL
                self.velocity[1] = -PLAYER_WALL_JUMP_VERTICAL
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jumps = max(0, self.jumps - 1)
                return True
                
        elif self.jumps:
            self.velocity[1] = -PLAYER_JUMP_POWER
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = -1
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = 1
            self.jumps -= 1
            self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
            return True
