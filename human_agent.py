import pygame

class BaseHumanAgent:
    def __init__(self):
        self.action = 0
        self.controls = {
            'jump': None,  # Changed from 'forward' to 'jump'
            'backward': None,
            'left': None,
            'right': None
        }
        self.state = {
            'normal': None,
            'dash': None,
            'grab': None,
        }
        # Added movement tracking
        self.movement = [0, 0]  # [horizontal, vertical]

    def get_state(self):
        keys = pygame.key.get_pressed()
        
        action_state = 0
        
        if(self.state['jump'] is not None and keys[self.state['jump']]):
            action_state = 1
        if self.state['dash'] is not None and keys[self.state['dash']]:
            action_state = 2
        elif self.state['grab'] is not None and keys[self.state['grab']]:
            action_state = 3
            
        return action_state
    
    def get_action(self):
        keys = pygame.key.get_pressed()
        
        self.movement = [0, 0]
        
        forward = keys[self.controls['up']]
        down = keys[self.controls['down']]
        left = keys[self.controls['left']]
        right = keys[self.controls['right']]
        
        if forward and left:
            self.action = 5 
        elif forward and right:
            self.action = 6 
        elif down and left:
            self.action = 7 
        elif down and right:
            self.action = 8  
        elif forward:
            self.action = 1  
        elif down:
            self.action = 2 
        elif left:
            self.action = 3  
        elif right:
            self.action = 4  
        else:
            self.action = 0  
            
        return self.action

class HumanAgentWASD(BaseHumanAgent):
    def __init__(self):
        super().__init__()
        self.controls = {
            'up': pygame.K_w,  
            'down': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d
        }

        self.state = {
            'normal': None,
            'jump': pygame.K_SPACE,
            'dash': pygame.K_LSHIFT,
            'grab': pygame.K_v,
        }

class HumanAgentArrows(BaseHumanAgent):
    def __init__(self):
        super().__init__()
        self.controls = {
            'forward': pygame.K_UP, 
            'backward': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT
        }

        self.state = {
            'normal': None,
            'jump': pygame.K_k,
            'dash': pygame.K_RSHIFT,
            'grab': pygame.K_RCTRL,
        }