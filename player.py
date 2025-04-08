import math
import random
from Constants import *
import pygame

class Player:
    def __init__(self, game, pos, size=PLAYER_SIZE):
        self.game = game
        self.type = 'player'
        self.originalpos = list(pos)
        self.pos = self.originalpos.copy()
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = PLAYER_ANIMATION_OFFSET
        self.flip = False
        self.set_action('idle')
        
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.dash_count = 2
        self.dash_directions = set()
        self.dash_direction = (1, 0)  
        
        self.jump_held = False
        self.jump_timer = 0
        self.max_jump_time = 20
        self.jump_strength_multiplier = 1.0
        
        self.stamina = 110
        self.wall_jump_count = 0  
        self.max_wall_jumps = 1   

        self.moving_left = False
        self.moving_right = False
        self.is_jumping = False
        self.is_dashing = False
        self.is_grabbing = False
        
        self.last_movement = [0, 0]
        self.last_dash_time = 0

    def reset(self):
        self.action = ''
        self.set_action('idle')
        self.pos = self.originalpos.copy()
        self.velocity = [0, 0]
        self.stamina = 110
        self.air_time = 0
        self.jumps = 1
        self.dashing = 0
        self.dash_count = 2
        self.dash_directions.clear()
        self.wall_slide = False
        self.moving_left = False
        self.moving_right = False
        self.is_jumping = False
        self.is_dashing = False
        self.is_grabbing = False
        self.wall_jump_count = 0
        self.last_dash_time = 0
        
        self.create_reset_particles()
    
    def create_reset_particles(self):
        # Create particles for death/reset effect
        environment = self.game.environment
        if environment:
            for _ in range(15):
                angle = random.random() * math.pi * 2
                speed = random.uniform(0.5, 2)
                velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                
                environment.create_particle(
                    'particle', 
                    [self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2], 
                    velocity=velocity, 
                    frame=random.randint(0, 7)
                )

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
    
    def handle_movement(self, tilemap):
        self.update(tilemap)
    
    def update(self, tilemap):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        movement_x = 0
        if self.moving_right:
            movement_x += 1
        if self.moving_left:
            movement_x -= 1
            
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            if movement_x != 0:
                target_speed = movement_x * PLAYER_SPEED
                
                if abs(self.velocity[0]) < abs(target_speed):
                    self.velocity[0] += movement_x * 0.8
                    self.velocity[0] = max(min(self.velocity[0], PLAYER_SPEED), -PLAYER_SPEED)
                else:
                    self.velocity[0] = target_speed
            else:
                if self.velocity[0] > 0:
                    self.velocity[0] = max(self.velocity[0] - FRICTION * 1.5, 0)
                elif self.velocity[0] < 0:
                    self.velocity[0] = min(self.velocity[0] + FRICTION * 1.5, 0)
        
        self.velocity[1] = min(MAX_FALL_SPEED, self.velocity[1] + 0.1)
        
        frame_movement = [self.velocity[0], self.velocity[1]]
        
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
        
        if movement_x > 0:
            self.flip = False
        elif movement_x < 0:
            self.flip = True
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        self.air_time += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            self.jump_timer = 0
            self.jump_strength_multiplier = 1.0
            self.dash_count = 2  
            self.dash_directions.clear()
            self.wall_jump_count = 0 
            self.last_dash_time = 0
        
        if self.collisions['down']:
            self.stamina = min(110, self.stamina + 1)
        elif self.wall_slide:
            self.stamina = max(0, self.stamina - 0.1)
        elif self.air_time > PLAYER_AIR_TIME_THRESHOLD:
            self.stamina = max(0, self.stamina - 0.15)
        
        if ((self.collisions['right'] or self.collisions['left']) and 
            self.air_time > PLAYER_AIR_TIME_THRESHOLD and 
            self.velocity[1] > 0 and 
            self.stamina > 0):
            
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)
            
            if self.collisions['right']:
                self.flip = False
            elif self.collisions['left']:
                self.flip = True
                
            self.set_action('wall_slide')
        else:
            self.wall_slide = False
        
        if not self.wall_slide:
            if self.air_time > PLAYER_AIR_TIME_THRESHOLD:
                self.set_action('jump')
            elif abs(self.velocity[0]) > 0.5: 
                self.set_action('run')
            else:
                self.set_action('idle')
        
        if self.is_jumping and self.jump_held and self.jump_timer < self.max_jump_time:
            self.jump_timer += 1
            jump_boost = -0.3 * self.jump_strength_multiplier
            self.velocity[1] += jump_boost
            
            self.jump_strength_multiplier = max(0.5, 1.0 - (self.jump_timer / (self.max_jump_time * 2)))
        
        self._update_dash()
        
        self.animation.update()
    
    def _update_dash(self):
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            direction_x, direction_y = self.dash_direction
            
            dash_power = PLAYER_DASH_SPEED * 1.2
            if direction_x != 0 and direction_y != 0:
                dash_power *= 0.7071 
            
            self.velocity[0] = direction_x * dash_power
            self.velocity[1] = direction_y * dash_power
            
            if abs(self.dashing) % 2 == 0:
                pvelocity = [
                    -direction_x * random.random() * 3, 
                    -direction_y * random.random() * 3
                ]
                environment = self.game.environment
                if environment:
                    environment.create_particle(
                        'particle', 
                        self.rect().center, 
                        velocity=pvelocity, 
                        frame=random.randint(0, 7)
                    )
    
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            img = self.game.assets['player/slide'].img()
        else:
            img = self.animation.img()
        
        surf.blit(pygame.transform.flip(img, self.flip, False), 
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                self.pos[1] - offset[1] + self.anim_offset[1]))
    
    def move_left(self, active=True):
        self.moving_left = active
        if active:
            self.flip = True
            
    def move_right(self, active=True):
        self.moving_right = active
        if active:
            self.flip = False
            
    def start_jump(self, active=True):
        self.is_jumping = active
        if active:
            self.jump()
        else:
            self.end_jump()
            
    def start_dash(self, active=True):
        self.is_dashing = active
        if active:
            self.dash()
            
    def start_grab(self, active=True):
        self.is_grabbing = active
            
    def stop_movement(self):
        self.moving_left = False
        self.moving_right = False
        self.is_jumping = False
        self.is_dashing = False
        self.is_grabbing = False
        self.end_jump()
    
    def jump(self):        
        if self.wall_slide and self.stamina > 20 and self.wall_jump_count < self.max_wall_jumps:
            wall_jump_horizontal = PLAYER_WALL_JUMP_HORIZONTAL * 0.8
            wall_jump_vertical = -PLAYER_WALL_JUMP_VERTICAL
            
            self.stamina -= 20
            
            self.wall_jump_count += 1
            
            if self.collisions['left']: 
                self.velocity[0] = wall_jump_horizontal
                self.velocity[1] = wall_jump_vertical
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jump_held = True
                return True
                
            elif self.collisions['right']: 
                self.velocity[0] = -wall_jump_horizontal
                self.velocity[1] = wall_jump_vertical
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jump_held = True
                return True
                
        elif self.jumps > 0:
            jump_power = -PLAYER_JUMP_POWER
            
            self.velocity[1] = jump_power
            
            if self.moving_left:
                self.velocity[0] = -PLAYER_SPEED * 1.1
            elif self.moving_right:
                self.velocity[0] = PLAYER_SPEED * 1.1
            
            self.jumps -= 1
            self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
            self.jump_held = True
            return True
        
        return False
    
    def end_jump(self):
        self.jump_held = False
        self.jump_timer = 0
        self.jump_strength_multiplier = 1.0
    
    def dash(self):
        if self.dash_count <= 0:
            return False
        
        dash_direction = [0, 0]
        
        if self.moving_left:
            dash_direction[0] = -1
        elif self.moving_right:
            dash_direction[0] = 1
        
        if self.is_jumping:
            dash_direction[1] = -1  
        elif self.is_grabbing: 
            dash_direction[1] = 1  
        
        if dash_direction == [0, 0]:
            dash_direction[0] = -1 if self.flip else 1
        
        dash_direction_tuple = tuple(dash_direction)
        
        self.dash_directions.add(dash_direction_tuple)
        self.dash_direction = dash_direction_tuple
        
        if dash_direction[0] < 0:
            self.dashing = -PLAYER_DASH_DURATION
            self.flip = True
        elif dash_direction[0] > 0:
            self.dashing = PLAYER_DASH_DURATION
            self.flip = False
        else:
            self.dashing = PLAYER_DASH_DURATION if not self.flip else -PLAYER_DASH_DURATION
        
        self.dash_count -= 1
        self.last_dash_time = pygame.time.get_ticks()
        
        self._create_dash_particles(dash_direction)
        
        return True
        
    def _create_dash_particles(self, dash_direction):
        environment = self.game.environment
        if not environment:
            return
            
        for _ in range(PARTICLE_COUNT_DASH): 
            angle = random.random() * math.pi * 2
            speed = random.random() * (PARTICLE_SPEED_MAX * 1.5 - PARTICLE_SPEED_MIN) + PARTICLE_SPEED_MIN
            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            offset = [
                dash_direction[0] * 5 if dash_direction[0] != 0 else 0,
                dash_direction[1] * 5 if dash_direction[1] != 0 else 0
            ]
            environment.create_particle(
                'particle', 
                [self.rect().centerx + offset[0], self.rect().centery + offset[1]], 
                velocity=pvelocity, 
                frame=random.randint(0, 7)
            )