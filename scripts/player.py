import math
import random
from Constants import *
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
        
        # Player-specific attributes
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.sliding = 0
        self.slide_cooldown = 0
        self.slide_wall_stun = 0
        self.dash_count = 2  # Track available dashes
        self.dash_directions = set()
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
    
    def update(self, tilemap, movement=(0, 0)):
        # Reset collisions
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        # Store pre-update position for slide wall detection
        pre_pos = self.pos.copy()
        
        # Adjust movement if slide_wall_stun is active
        modified_movement = list(movement)
        if self.slide_wall_stun > 0:
            modified_movement[0] = 0  # Prevent horizontal movement during wall stun
            self.slide_wall_stun -= 1
        
        # Physics movement calculation
        frame_movement = (modified_movement[0] + self.velocity[0], modified_movement[1] + self.velocity[1])
        
        # Horizontal movement and collision
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
        
        # Vertical movement and collision
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
        
        # Update facing direction
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        self.last_movement = movement
        
        # Gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        # Stop vertical movement on collision
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        # Player-specific update logic
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
        
        # Handle sliding cooldown
        if self.slide_cooldown > 0:
            self.slide_cooldown -= 1
        
        # Handle sliding state
        if self.sliding > 0:
            self.sliding -= 1
            # During slide, maintain horizontal momentum in slide direction
            if self.flip:
                self.velocity[0] = -PLAYER_SLIDE_SPEED  # Slide left
            else:
                self.velocity[0] = PLAYER_SLIDE_SPEED   # Slide right
            
            # Push player down during slide
            if not self.collisions['down']:
                self.velocity[1] = 2.0  # Push player downward during slide
            
            # Create particle effects during slide
            if self.sliding % 3 == 0:
                pvelocity = [-0.5 if self.flip else 0.5, 0]
                self.game.particles.append(Particle(self.game, 'particle', 
                                            [self.rect().centerx, self.rect().bottom - 2], 
                                            velocity=pvelocity, frame=random.randint(0, 7)))
        
        # Check if we hit a wall during slide
        if self.sliding > 0 and (self.collisions['right'] or self.collisions['left']):
            # Calculate how far we moved before hitting the wall
            movement_before_wall = abs(self.pos[0] - pre_pos[0])
            
            # If we didn't move much, we likely hit a wall
            if movement_before_wall < 1.0:  # Threshold for "direct" wall hit
                self.slide_wall_stun = PLAYER_SLIDE_WALL_STUN
                self.sliding = 0  # End the slide immediately
                self.velocity[0] = 0  # Stop horizontal movement
                self.velocity[1] = 0.5  # Small upward counter to prevent immediate falling
                
                # Add impact particle effect
                impact_direction = 1 if self.collisions['left'] else -1
                for i in range(PARTICLE_COUNT_SLIDE_IMPACT):
                    pvelocity = [impact_direction * random.random() * 1.5, 
                                (random.random() - 0.5) * 2]
                    self.game.particles.append(Particle(self.game, 'particle', 
                                            [self.rect().centerx, self.rect().centery], 
                                            velocity=pvelocity, frame=random.randint(0, 7)))
        
        # Wall sliding logic
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > PLAYER_AIR_TIME_THRESHOLD and self.slide_wall_stun <= 0:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        # Animation state logic
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
        
        if self.collisions['down']:
            self.dash_count = 2
            self.dash_directions.clear()
        
        # Handle dash mechanics
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        
        # Apply dash movement if currently dashing
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            if hasattr(self, 'dash_direction'):
                direction_x, direction_y = self.dash_direction
                
                # Calculate dash speeds with consistent velocity
                dash_power = PLAYER_DASH_SPEED * 1.2  # Slightly stronger dash
                if direction_x != 0 and direction_y != 0:
                    # Normalize diagonal movement to maintain speed
                    dash_power *= 0.7071  # 1/sqrt(2)
                
                self.velocity[0] = direction_x * dash_power
                self.velocity[1] = direction_y * dash_power
                
                # Apply slowdown at the end of dash
                if abs(self.dashing) == PLAYER_DASH_DURATION - 9:
                    self.velocity[0] *= PLAYER_DASH_SLOWDOWN
                    self.velocity[1] *= PLAYER_DASH_SLOWDOWN
            
            # Create trail particles during dash
            if self.dashing % 2 == 0:  # More frequent particles
                if hasattr(self, 'dash_direction'):
                    direction_x, direction_y = self.dash_direction
                    # More dramatic particle effects
                    pvelocity = [
                        -direction_x * random.random() * 3, 
                        -direction_y * random.random() * 3
                    ]
                    self.game.particles.append(
                        Particle(self.game, 'particle', 
                                self.rect().center, 
                                velocity=pvelocity, 
                                frame=random.randint(0, 7))
                    )
        
        # Apply friction when not dashing
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            if self.velocity[0] > 0:
                self.velocity[0] = max(self.velocity[0] - FRICTION, 0)
            else:
                self.velocity[0] = min(self.velocity[0] + FRICTION, 0)
        
        # Update animation
        self.animation.update()
    
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
    
    def dash(self):
        # Don't allow dash during slide wall stun or if no dashes left
        if self.slide_wall_stun > 0 or self.dash_count <= 0:
            return False
            
        # Get the current keyboard state
        keys = pygame.key.get_pressed()
        
        # Determine dash direction based on key combinations
        dash_direction = [0, 0]
        
        # Horizontal direction
        if keys[KEY_LEFT]:
            dash_direction[0] = -1
        elif keys[KEY_RIGHT]:
            dash_direction[0] = 1
        
        # Vertical direction
        if keys[KEY_UP]:
            dash_direction[1] = -1
        elif keys[KEY_DOWN]:
            dash_direction[1] = 1
        
        # If no direction is pressed, dash in facing direction
        if dash_direction == [0, 0]:
            dash_direction[0] = -1 if self.flip else 1
        
        # Convert to tuple for hashability
        dash_direction_tuple = tuple(dash_direction)
        
        # Only allow same direction once per airtime (encourages varied dashes)
        if dash_direction_tuple in self.dash_directions and len(self.dash_directions) > 1:
            return False
        
        # Store dash direction
        self.dash_direction = dash_direction_tuple
        self.dash_directions.add(dash_direction_tuple)
        
        # Set dashing state
        if dash_direction[0] < 0:
            self.dashing = -PLAYER_DASH_DURATION
            self.flip = True
        elif dash_direction[0] > 0:
            self.dashing = PLAYER_DASH_DURATION
            self.flip = False
        else:
            # For pure vertical dashes, maintain current facing
            self.dashing = PLAYER_DASH_DURATION if not self.flip else -PLAYER_DASH_DURATION
        
        # Consume a dash
        self.dash_count -= 1
        
        for i in range(PARTICLE_COUNT_DASH): 
            angle = random.random() * math.pi * 2
            speed = random.random() * (PARTICLE_SPEED_MAX * 1.5 - PARTICLE_SPEED_MIN) + PARTICLE_SPEED_MIN
            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            offset = [
                dash_direction[0] * 5 if dash_direction[0] != 0 else 0,
                dash_direction[1] * 5 if dash_direction[1] != 0 else 0
            ]
            self.game.particles.append(
                Particle(self.game, 'particle', 
                        [self.rect().centerx + offset[0], self.rect().centery + offset[1]], 
                        velocity=pvelocity, 
                        frame=random.randint(0, 7))
            )
        return True