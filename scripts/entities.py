import math
import random
from Constants import *
import pygame

from scripts.particle import Particle

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
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
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.sliding = 0
        self.slide_cooldown = 0
        self.slide_wall_stun = 0
        self.dash_direction = (0, 0)
    
    def update(self, tilemap, movement=(0, 0)):
        # Store pre-update position for slide wall detection
        pre_pos = self.pos.copy()
        
        # Adjust movement if slide_wall_stun is active
        modified_movement = list(movement)
        if self.slide_wall_stun > 0:
            modified_movement[0] = 0  # Prevent horizontal movement during wall stun
            self.slide_wall_stun -= 1
        
        super().update(tilemap, movement=tuple(modified_movement))
        
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
            
        # Wall sliding logic - don't allow wall slide immediately after hitting wall during slide
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > PLAYER_AIR_TIME_THRESHOLD and self.slide_wall_stun <= 0:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        # Animation state logic - add stunned state
        if self.slide_wall_stun > 0:
            # Could have a specific stunned animation if you create one
            self.set_action('idle')  # Or use 'slide' animation to show the stun
        elif not self.wall_slide:
            if self.sliding > 0:
                self.set_action('slide')
            elif self.air_time > PLAYER_AIR_TIME_THRESHOLD:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        # Handle dash mechanics
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
            
        # Apply dash movement if currently dashing
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            if hasattr(self, 'dash_direction'):
                # Apply velocity based on the stored dash direction
                direction_x, direction_y = self.dash_direction
                
                # Calculate dash speeds
                dash_speed_x = PLAYER_DASH_SPEED if direction_x != 0 else 0
                dash_speed_y = PLAYER_DASH_SPEED if direction_y != 0 else 0
                
                # Normalize diagonal movement to maintain consistent speed
                if direction_x != 0 and direction_y != 0:
                    # Pythagoras to the rescue (1/sqrt(2) ≈ 0.7071)
                    dash_speed_x *= 0.7071
                    dash_speed_y *= 0.7071
                
                # Apply the directional speeds
                self.velocity[0] = direction_x * dash_speed_x
                self.velocity[1] = direction_y * dash_speed_y
                
                # Apply slowdown at the end of dash
                if abs(self.dashing) == PLAYER_DASH_DURATION - 9:
                    self.velocity[0] *= PLAYER_DASH_SLOWDOWN
                    self.velocity[1] *= PLAYER_DASH_SLOWDOWN
            
            # Create trail particles during dash
            if self.dashing % 3 == 0:
                # Adjust particle direction based on dash direction
                if hasattr(self, 'dash_direction'):
                    direction_x, direction_y = self.dash_direction
                    pvelocity = [-direction_x * random.random() * 2, -direction_y * random.random() * 2]
                    self.game.particles.append(Particle(self.game, 'particle', 
                                                    self.rect().center, 
                                                    velocity=pvelocity, 
                                                    frame=random.randint(0, 7)))
                
        # Apply friction when not dashing
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            if self.velocity[0] > 0:
                self.velocity[0] = max(self.velocity[0] - FRICTION, 0)
            else:
                self.velocity[0] = min(self.velocity[0] + FRICTION, 0)
    
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            super().render(surf, offset=offset)
            
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
        # Don't allow dash during slide wall stun
        if self.slide_wall_stun > 0 or self.dashing:
            return False
            
        # Get the current keyboard state
        keys = pygame.key.get_pressed()
        
        # Determine dash direction based on key combinations
        dash_direction = None
        
        # Check for up direction (diagonal up-left, straight up, or diagonal up-right)
        if keys[KEY_UP]:
            if keys[KEY_LEFT]:
                # Diagonal up-left
                dash_direction = (-1, -1)
            elif keys[KEY_RIGHT]:
                # Diagonal up-right
                dash_direction = (1, -1)
            else:
                # Straight up
                dash_direction = (0, -1)
        
        # If no valid direction is pressed, don't dash
        if dash_direction is None:
            return False
        
        # Set dashing state based on horizontal direction
        if dash_direction[0] < 0:
            self.dashing = -PLAYER_DASH_DURATION
            self.flip = True
        elif dash_direction[0] > 0:
            self.dashing = PLAYER_DASH_DURATION
            self.flip = False
        else:
            # For straight up, use current facing direction
            self.dashing = PLAYER_DASH_DURATION if not self.flip else -PLAYER_DASH_DURATION
        
        # Store the selected dash direction for use in the update method
        self.dash_direction = dash_direction
        
        # Create initial dash effect
        for i in range(PARTICLE_COUNT_DASH):
            angle = random.random() * math.pi * 2
            speed = random.random() * (PARTICLE_SPEED_MAX - PARTICLE_SPEED_MIN) + PARTICLE_SPEED_MIN
            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, 
                                            velocity=pvelocity, frame=random.randint(0, 7)))
        
        return True
