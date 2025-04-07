
import pygame

def death(display):
    transition_surf = pygame.Surface(display.get_size(), pygame.SRCALPHA)
    transition_surf.fill((0, 0, 0, 0))  
    
    pygame.draw.circle(transition_surf, (0, 0, 0, 200), 
                    (display.get_width() // 2, display.get_height() // 2), 
                    max(0, display.get_height() - 10))
    
    display.blit(transition_surf, (0, 0))