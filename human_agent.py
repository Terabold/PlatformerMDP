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
        
        # Initialize state to normal (0) by default
        action_state = 0
        
        # Check for dash and grab keys, ignoring normal since it's None
        if self.state['dash'] is not None and keys[self.state['dash']]:
            action_state = 1
        elif self.state['grab'] is not None and keys[self.state['grab']]:
            action_state = 2
            
        return action_state
    
    def get_action(self):
        keys = pygame.key.get_pressed()
        
        # Reset movement tracking
        self.movement = [0, 0]
        
        # Get keys status
        jump = keys[self.controls['jump']]
        backward = keys[self.controls['backward']]
        left = keys[self.controls['left']]
        right = keys[self.controls['right']]
        
        # Update movement tracking
        if left:
            self.movement[0] = -1
        elif right:
            self.movement[0] = 1
            
        if jump:
            self.movement[1] = -1  # Up
        elif backward:
            self.movement[1] = 1   # Down
        
        # Determine action based on key combinations
        if jump and left:
            self.action = 5  # Jump + Left
        elif jump and right:
            self.action = 6  # Jump + Right
        elif backward and left:
            self.action = 7  # Down + Left
        elif backward and right:
            self.action = 8  # Down + Right
        elif jump:
            self.action = 1  # Jump
        elif backward:
            self.action = 2  # Down
        elif left:
            self.action = 3  # Left
        elif right:
            self.action = 4  # Right
        else:
            self.action = 0  # No action
            
        return self.action

class HumanAgentWASD(BaseHumanAgent):
    def __init__(self):
        super().__init__()
        self.controls = {
            'jump': pygame.K_SPACE,  # Jump with space
            'backward': pygame.K_s,
            'left': pygame.K_a,
            'right': pygame.K_d
        }

        self.state = {
            'normal': None,
            'dash': pygame.K_LSHIFT,
            'grab': pygame.K_v,
        }

class HumanAgentArrows(BaseHumanAgent):
    def __init__(self):
        super().__init__()
        self.controls = {
            'jump': pygame.K_UP,  # Jump with up arrow
            'backward': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT
        }

        self.state = {
            'normal': None,
            'dash': pygame.K_RSHIFT,
            'grab': pygame.K_RCTRL,
        }