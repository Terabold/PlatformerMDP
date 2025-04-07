import pygame
from Constants import *

class HumanAgent:
    def __init__(self):
        self.movement = [0, 0]  
        
        self.actions = {
            'jump': False,
            'dash': False,
            'grab': False
        }
        
        self.controls = {
            'left': KEY_LEFT,
            'right': KEY_RIGHT,
            'up': KEY_UP,
            'down': KEY_DOWN,
            'jump': KEY_JUMP,
            'dash': KEY_DASH,
            'grab': KEY_GRAB  # Assuming slide is the grab action
        }
        
        self.key_pressed = {action: False for action in self.actions}
        self.key_released = {action: False for action in self.actions}

    def process_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.controls['left']:
                self.movement[0] = -1
            if event.key == self.controls['right']:
                self.movement[0] = 1
            if event.key == self.controls['up']:
                self.movement[1] = -1
            if event.key == self.controls['down']:
                self.movement[1] = 1
                
            if event.key == self.controls['jump']:
                self.actions['jump'] = True
                self.key_pressed['jump'] = True
            if event.key == self.controls['dash']:
                self.actions['dash'] = True
                self.key_pressed['dash'] = True
            if event.key == self.controls['grab']:
                self.actions['grab'] = True
                self.key_pressed['grab'] = True
                
        elif event.type == pygame.KEYUP:
            if event.key == self.controls['left'] and self.movement[0] == -1:
                self.movement[0] = 0
            if event.key == self.controls['right'] and self.movement[0] == 1:
                self.movement[0] = 0
            if event.key == self.controls['up'] and self.movement[1] == -1:
                self.movement[1] = 0
            if event.key == self.controls['down'] and self.movement[1] == 1:
                self.movement[1] = 0
                
            if event.key == self.controls['jump']:
                self.actions['jump'] = False
                self.key_released['jump'] = True
            if event.key == self.controls['dash']:
                self.actions['dash'] = False
                self.key_released['dash'] = True
            if event.key == self.controls['grab']:
                self.actions['grab'] = False
                self.key_released['grab'] = True

    def update(self):
        keys = pygame.key.get_pressed()
        
        self.movement[0] = 0
        if keys[self.controls['left']]:
            self.movement[0] = -1
        if keys[self.controls['right']]:
            self.movement[0] = 1
            
        self.movement[1] = 0
        if keys[self.controls['up']]:
            self.movement[1] = -1
        if keys[self.controls['down']]:
            self.movement[1] = 1
            
        self.actions['jump'] = keys[self.controls['jump']]
        self.actions['dash'] = keys[self.controls['dash']]
        self.actions['grab'] = keys[self.controls['grab']]
    
    def get_movement(self):
        return self.movement
    
    def get_horizontal_movement(self):
        return [self.movement[0] == -1, self.movement[0] == 1]
    
    def is_action_pressed(self, action):
        result = self.key_pressed[action]
        self.key_pressed[action] = False 
        return result
    
    def is_action_released(self, action):
        result = self.key_released[action]
        self.key_released[action] = False  
        return result
    
    def is_action_held(self, action):
        return self.actions[action]
    
    def reset_frame_data(self):
        for action in self.actions:
            self.key_pressed[action] = False
            self.key_released[action] = False