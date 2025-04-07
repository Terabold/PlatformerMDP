import math
import random
from Constants import *
import pygame

from scripts.particle import Particle

class Player:
    def __init__(self, game, pos, size=PLAYER_SIZE):
        self.game = game
        self.type = 'player'
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = PLAYER_ANIMATION_OFFSET
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
        
        # Player-specific attributes
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
        self.dash_count = 2  # Track available dashes
        self.dash_directions = set()
        
        # Initialize dash_direction with a default value
        self.dash_direction = (1, 0)
        
        # Jump variables
        self.jump_held = False
        self.jump_timer = 0
        self.max_jump_time = 20  # Maximum time jump can be held
        self.jump_strength_multiplier = 1.0
        
        # Add wall jump cooldown to prevent repeated wall jumps
        self.last_wall_side = None  # 'left' or 'right'

        self.stamina = 110
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
    
    def update(self, tilemap, movement=(0, 0)):
        # Reset collisions
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        # Physics movement calculation
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
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
        self.velocity[1] = min(MAX_FALL_SPEED, self.velocity[1] + 0.1)
        
        # Stop vertical movement on collision
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        # Player-specific update logic
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            self.jump_timer = 0
            self.jump_strength_multiplier = 1.0
            self.last_wall_side = None   # Reset last wall side when landing
        
        if self.air_time < PLAYER_AIR_TIME_THRESHOLD:
            self.stamina = 110
        else: self.stamina -= 1/6

        # Wall sliding logic
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > PLAYER_AIR_TIME_THRESHOLD:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], PLAYER_WALL_SLIDE_SPEED)
            if self.collisions['right']:
                self.flip = False
                current_wall = 'right'
            else:
                self.flip = True
                current_wall = 'left'
            
            # Update last wall side when in contact with a wall
            if self.last_wall_side != current_wall:
                self.last_wall_side = current_wall
            
            self.set_action('wall_slide')

        
        # Animation state logic
        if not self.wall_slide:
            if self.air_time > PLAYER_AIR_TIME_THRESHOLD:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        if self.collisions['down']:
            self.dash_count = 2
            self.dash_directions.clear()
        
        # Handle jump timer and strength
        if self.jump_held and self.jump_timer < self.max_jump_time:
            self.jump_timer += 1
            # Gradually reduce jump strength as time progresses
            self.jump_strength_multiplier = max(0.5, 1.0 - (self.jump_timer / (self.max_jump_time * 2)))
        
        # Handle dash mechanics
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        
        # Apply dash movement if currently dashing
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            direction_x, direction_y = self.dash_direction
            
            # Calculate dash speeds with consistent velocity
            dash_power = PLAYER_DASH_SPEED * 1.2  # Slightly stronger dash
            if direction_x != 0 and direction_y != 0:
                # Normalize diagonal movement to maintain speed
                dash_power *= 0.7071  # 1/sqrt(2)
            
            self.velocity[0] = direction_x * dash_power
            self.velocity[1] = direction_y * dash_power
            
            # MODIFIED: Instead of applying slowdown, completely stop at the end of dash
            if abs(self.dashing) == PLAYER_DASH_DURATION - 9:
                # Set velocity to zero immediately when dash ends
                self.velocity[0] = 0
                self.velocity[1] = 0
            
            # Create trail particles during dash
            if self.dashing % 2 == 0:  # More frequent particles
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
        
        # Apply friction when not dashing - can also be removed if desired
        # as we're now stopping momentum completely at the end of the dash
        if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
            if self.velocity[0] > 0:
                self.velocity[0] = max(self.velocity[0] - FRICTION, 0)
            else:
                self.velocity[0] = min(self.velocity[0] + FRICTION, 0)
        
        # Update animation
        self.animation.update()
    
    def render(self, surf, offset=(0, 0)):
        # Remove the condition that prevents rendering during dash
        # Original: if abs(self.dashing) <= PLAYER_DASH_DURATION - 10:
        
        # Display jump animation during dash
        if abs(self.dashing) > PLAYER_DASH_DURATION - 10:
            # Use jump animation during dash
            img = self.game.assets['player/slide'].img()
        else:
            # Use normal animation otherwise
            img = self.animation.img()
        
        # Render the player with proper flip
        surf.blit(pygame.transform.flip(img, self.flip, False), 
                (self.pos[0] - offset[0] + self.anim_offset[0], 
                self.pos[1] - offset[1] + self.anim_offset[1]))
    
    def jump(self):        
        # Check for wall jump - COMPLETELY REWORKED
        if self.wall_slide and self.stamina > 0:
            # Significantly reduced horizontal and vertical wall jump speed
            wall_jump_horizontal = PLAYER_WALL_JUMP_HORIZONTAL * 0.4  # Reduced by 60%
            wall_jump_vertical = -PLAYER_WALL_JUMP_VERTICAL     # Reduced by 40%
            
            # Set wall jump cooldown to prevent repeated wall jumps
            self.stamina -= 30
            
            # Force player to jump AWAY from the wall
            if self.collisions['left']:  # Left wall - must jump RIGHT
                self.velocity[0] = wall_jump_horizontal  # Positive = right
                self.velocity[1] = wall_jump_vertical
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jumps = max(0, self.jumps - 1)
                self.jump_held = True
                return True
            elif self.collisions['right']:  # Right wall - must jump LEFT
                self.velocity[0] = -wall_jump_horizontal  # Negative = left
                self.velocity[1] = wall_jump_vertical
                self.air_time = PLAYER_AIR_TIME_THRESHOLD + 1
                self.jumps = max(0, self.jumps - 1)
                self.jump_held = True
                return True
                
        # Regular jump
        elif self.jumps:
            keys = pygame.key.get_pressed()
            
            # Base jump power
            jump_power = -PLAYER_JUMP_POWER
            
            # Adjust jump based on up key
            if keys[KEY_UP]:
                jump_power *= 1.2  # Higher initial jump
            
            # Set initial jump velocity
            self.velocity[1] = jump_power
            
            # Add slight horizontal movement during jump
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = -1
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = 1
            
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
        # Don't allow dash if no dashes left
        if self.dash_count <= 0:
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
            dash_direction[1] = -1.6
        elif keys[KEY_DOWN]:
            dash_direction[1] = 1
        
        if dash_direction == [0, 0]:
            dash_direction[0] = -1 if self.flip else 1
        
        dash_direction_tuple = tuple(dash_direction)
        
        if dash_direction_tuple in self.dash_directions and len(self.dash_directions) > 1:
            return False
        
        self.dash_direction = dash_direction_tuple
        self.dash_directions.add(dash_direction_tuple)
        
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
        

        impact_offset = [0, 0]
    
        # Determine offset based on dash direction
        if dash_direction[0] < 0:  # Dashing left
            impact_offset[0] = self.size[0]  # Appear on right side
        elif dash_direction[0] > 0:  # Dashing right
            impact_offset[0] = -self.size[0]  # Appear on left side
            
        if dash_direction[1] < 0:  # Dashing up
            impact_offset[1] = self.size[1]  # Appear below
        elif dash_direction[1] > 0:  # Dashing down
            impact_offset[1] = -self.size[1]  # Appear above
        
        # If no vertical component, adjust offset to center vertically
        if dash_direction[1] == 0:
            impact_offset[1] = 0
        
        # Create a burst of particles for the impact effect
        impact_count = 12  # Number of particles in the impact
        
        for i in range(impact_count):
            # Calculate particle angle based on impact direction
            if dash_direction[0] != 0:
                # For horizontal dash, create a semicircle of particles in the opposite direction
                angle_min = math.pi * 0.75 if dash_direction[0] > 0 else -math.pi * 0.25
                angle_max = -math.pi * 0.75 if dash_direction[0] > 0 else math.pi * 0.25
                angle = angle_min + (angle_max - angle_min) * (i / impact_count)
            elif dash_direction[1] != 0:
                # For vertical dash, create a semicircle of particles in the opposite direction
                angle_min = 0 if dash_direction[1] > 0 else math.pi
                angle_max = math.pi if dash_direction[1] > 0 else math.pi * 2
                angle = angle_min + (angle_max - angle_min) * (i / impact_count)
            else:
                # Fallback for any edge cases
                angle = random.random() * math.pi * 2
            
            # Calculate particle speed and velocity
            speed = random.uniform(2.0, 3.5)  # Faster particles for impact effect
            pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            
            # Calculate spawn position with offset
            spawn_pos = [
                self.rect().centerx + impact_offset[0],
                self.rect().centery + impact_offset[1]
            ]
            
            # Add a small random offset to create a more natural effect
            spawn_pos[0] += random.uniform(-5, 5)
            spawn_pos[1] += random.uniform(-5, 5)
            
            # Create the particle with a different frame for the impact effect
            self.game.particles.append(
                Particle(self.game, 'particle', 
                        spawn_pos, 
                        velocity=pvelocity, 
                        frame=random.randint(0, 7))
            )
        
        return True