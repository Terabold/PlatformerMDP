import pygame
from Constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, FONT
from game import Game
from Menu import Menu
from screenstate import state_control
from scripts.utils import Text

class Engine:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Celeste Temu')
        
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.game = Game(self.display)
        self.menu = Menu(self.display)

        self.state = {'game': self.game, 'menu': self.menu}

    def run(self):
        while True:
            self.state[state_control.getState()].run()

            # Correct way to create a font and render the FPS
            font = pygame.font.SysFont(FONT, 50)  # You can choose another font
            fps = str(int(self.clock.get_fps()))
            fps_t = font.render(fps, True, pygame.Color("RED"))

            self.display.blit(fps_t, (0, 0))
            pygame.display.update() 
            self.clock.tick(FPS)


if __name__ == '__main__':
    Engine().run()
