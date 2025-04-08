import sys
import pygame
from scripts.utils import load_image, load_images, Animation
from environment import Environment
from Constants import *
from human_agent import HumanAgentWASD  

class Game:
    def __init__(self, screen=None):
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        
        self.screen = screen 
        self.display = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = pygame.time.Clock()
        
        self.agent = HumanAgentWASD()
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'spikes': load_images('tiles/spikes'),
            'checkpoint': load_images('tiles/Checkpoint'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=IDLE_ANIMATION_DURATION),
            'player/run': Animation(load_images('entities/player/run'), img_dur=RUN_ANIMATION_DURATION),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=PARTICLE_ANIMATION_DURATION, loop=False),
        }
        
        self.music = pygame.mixer.Sound(MUSIC)
        self.music.set_volume(0.05)
        
        self.environment = Environment(self, self.display)
        
    def run(self):
        self.music.play(-1)
        
        while True:            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
            
            action = self.agent.get_action()
            state = self.agent.get_state()

            self.environment.move(action, state)
            
            self.environment.update(self.agent)
            
            self.environment.render(self.display, debug=True)
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)