import pygame
from Constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from game import Game
from Menu import Menu
from screenstate import state_control
from scripts.utils import Text

DISPLAY_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
class Engine:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Celeste Temu')
        self.display = pygame.display.set_mode(DISPLAY_SIZE)
        self.clock = pygame.time.Clock()
        self.game = Game(self.display)
        self.menu = Menu(self.display)

        self.state = {'game': self.game, 'menu': self.menu}

    def run(self):
        while True:
            self.state[state_control.getState()].run()

            pygame.display.update() 
            self.clock.tick(FPS)


if __name__ == '__main__':
    Engine().run()