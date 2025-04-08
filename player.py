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
        
        # Animation properties
        self.action = ''
        self.anim_offset = PLAYER_ANIMATION_OFFSET
        self.flip = False
        self.set_action('idle')
        
        # Movement mechanics
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.dash_count = 2
        self.dash_directions = set()
        self.dash_direction = (1, 0)  # Default dash direction
        
        # Jump variables
        self.jump_held = False
        self.jump_timer = 0
        self.max_jump_time = 20
        self.jump_strength_multiplier = 1.0
        
        # Stamina for abilities
        self.stamina = 110
        
        # Input movement state
        self.moving_left = False
        self.moving_right = False
        self.is_jumping = False
        self.is_dashing = False
        self.is_grabbing = False
    
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
        
        # Create reset particles
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
    
    def update(self, tilemap, movement_input=(0, 0)):
        # Reset collisions
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        # Calculate horizontal movement based on input flags
        movement_x = 0
        if self.moving_right:
            movement_x += 1
        if self.moving_left:
            movement_x -= 1
            
        # Apply movement speed if not dashing
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            if movement_x != 0:
                self.velocity[0] = movement_x * PLAYER_SPEED
            else:
                # Apply friction
                if self.velocity[0] > 0:
                    self.velocity[0] = max(self.velocity[0] - FRICTION, 0)
                elif self.velocity[0] < 0:
                    self.velocity[0] = min(self.velocity[0] + FRICTION, 0)
        
        # Calculate movement for this frame
        frame_movement = [self.velocity[0], self.velocity[1]]
        
        # Handle horizontal movement and collision
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
        
        # Handle vertical movement and collision
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
        
        # Update facing direction based on movement
        if movement_x > 0:
            self.flip = False
        elif movement_x < 0:
            self.flip = True
        
        # Apply gravity
        self.velocity[1] = min(MAX_FALL_SPEED, self.velocity[1] + 0.1)
        
        # Stop vertical movement on collision
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        # Air time tracking
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            self.jump_timer = 0
            self.jump_strength_multiplier = 1.0
        
        # Stamina management
        if self.air_time < PLAYER_AIR_TIME_THRESHOLD:
            self.stamina = 110
        else:
            self.stamina -= 1/6  
        
        # Wall slide handling
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > PLAYER_AIR_TIME_THRESHOLD:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            
            self.set_action('wall_slide')
        
        # Animation state logic
        if not self.wall_slide:
            if self.air_time > PLAYER_AIR_TIME_THRESHOLD:
                self.set_action('jump')
            elif movement_x != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        # Reset dash count when touching ground
        if self.collisions['down']:
            self.dash_count = 2
            self.dash_directions.clear()
        
        # Update jump mechanics
        if self.is_jumping and self.jump_held and self.jump_timer < self.max_jump_time:
            self.jump_timer += 1
            self.jump_strength_multiplier = max(0.5, 1.0 - (self.jump_timer / (self.max_jump_time * 2)))
        
        # Handle dash mechanics
        self._update_dash()
        
        # Update animation
        self.animation.update()
    
    def _update_dash(self):
        # Update dash timer
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        
        # Apply dash movement if currently dashing
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            direction_x, direction_y = self.dash_direction
            
            # Calculate dash speeds with consistent velocity
            dash_power = PLAYER_DASH_SPEED * 1.2
            if direction_x != 0 and direction_y != 0:
                # Normalize diagonal movement
                dash_power *= 0.7071  # 1/sqrt(2)
            
            self.velocity[0] = direction_x * dash_power
            self.velocity[1] = direction_y * dash_power
            
            # Stop at end of dash
            if abs(self.dashing) == PLAYER_DASH_DURATION - 9:
                self.velocity[0] = 0
                self.velocity[1] = 0
            
            # Create trail particles during dash
            if self.dashing % 2 == 0:
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
        # Select animation frame
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            img = self.game.assets['player/slide'].img()
        else:
            img = self.animation.img()
        
        # Render the player with proper flip
        surf.blit(pygame.transform.flip(img, self.flip, False), 
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                self.pos[1] - offset[1] + self.anim_offset[1]))
    
    # Movement API methods
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
        if active and self.dash_count > 0:
            self.dash()
            
    def start_grab(self, active=True):
        self.is_grabbing = active
        # Grab mechanics to be implemented
            
    def stop_movement(self):
        self.moving_left = False
        self.moving_right = False
        self.is_jumping = False
        self.is_dashing = False
        self.is_grabbing = False
        self.end_jump()
    
    def jump(self):        
        if self.wall_slide and self.stamina > 0:
            wall_jump_horizontal = PLAYER_WALL_JUMP_HORIZONTAL * 0.6
            wall_jump_vertical = -PLAYER_WALL_JUMP_VERTICAL
            
            # Consume stamina
            self.stamina -= 30
            
            # Force player to jump away from wall
            if self.collisions['left']:  # Left wall - jump right
                self.velocity[0] = wall_jump_horizontal
                self.velocity[1] = wall_jump_vertical
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jumps = max(0, self.jumps - 1)
                self.jump_held = True
                return True
                
            elif self.collisions['right']:  # Right wall - jump left
                self.velocity[0] = -wall_jump_horizontal
                self.velocity[1] = wall_jump_vertical
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jumps = max(0, self.jumps - 1)
                self.jump_held = True
                return True
                
        # Regular jump
        elif self.jumps:
            # Base jump power
            jump_power = -PLAYER_JUMP_POWER
            
            # Set jump velocity
            self.velocity[1] = jump_power
            
            # Add horizontal velocity if moving
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
        # Reset jump variables
        self.jump_held = False
        self.jump_timer = 0
        self.jump_strength_multiplier = 1.0
    
    def dash(self):
        if self.dash_count <= 0:
            return False
        
        # Get dash direction from current input flags
        dash_direction = [0, 0]
        
        # Initialize direction based on movement flags
        if self.moving_left:
            dash_direction[0] = -1
        elif self.moving_right:
            dash_direction[0] = 1
        
        # Check for vertical input from keyboard
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            dash_direction[1] = -1.6  # Upward dash
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dash_direction[1] = 1  # Downward dash
        
        # Default to facing direction if no specific direction
        if dash_direction == [0, 0]:
            dash_direction[0] = -1 if self.flip else 1
        
        dash_direction_tuple = tuple(dash_direction)
        
        # Prevent dashing in the same direction twice
        if dash_direction_tuple in self.dash_directions and len(self.dash_directions) > 1:
            return False
        
        self.dash_direction = dash_direction_tuple
        self.dash_directions.add(dash_direction_tuple)
        
        # Set dashing state and direction
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
        
        # Create dash particles
        self._create_dash_particles(dash_direction)
        
        return True
        
    def _create_dash_particles(self, dash_direction):
        environment = self.game.environment
        if not environment:
            return
            
        # Create dash trail particles
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