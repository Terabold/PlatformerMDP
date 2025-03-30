import pygame, sys
from scripts.utils import Button
from screenstate import state_control
from Constants import SCREEN_WIDTH, FONT, RECT, MENUBG, WHITE, FONT2, MENUTXTCOLOR

def font_scale(size, Font=FONT):
    return pygame.font.Font(Font, size)

def create_shadowed_text(text, font, color, shadow_color=(0,0,0), offset=4):
    shadow = font.render(text, True, shadow_color)
    main_text = font.render(text, True, color)
    
    combined = pygame.Surface((shadow.get_width() + offset, shadow.get_height() + offset), pygame.SRCALPHA)
    combined.blit(shadow, (offset, offset))
    combined.blit(main_text, (0, 0))
    return combined
                  
class Menu():
    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.image.load(MENUBG)
    def run(self):
        self.screen.blit(self.background, (0,0))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        font = font_scale(85, FONT)
        MENU_TEXT = create_shadowed_text("Temu Celeste", font, color=WHITE)
        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH//2, 100))

        PLAY_BUTTON = Button(image=pygame.image.load(RECT), pos=(SCREEN_WIDTH//2, 250), 
                            text_input="PLAY", font=font_scale(50), base_color=MENUTXTCOLOR, hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load(RECT), pos=(SCREEN_WIDTH//2, 400), 
                            text_input="Train AI", font=font_scale(42), base_color=MENUTXTCOLOR, hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load(RECT), pos=(SCREEN_WIDTH//2, 550), 
                            text_input="QUIT", font=font_scale(50), base_color=MENUTXTCOLOR, hovering_color="White")

        self.screen.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(self.screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    state_control.setState('game')
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()